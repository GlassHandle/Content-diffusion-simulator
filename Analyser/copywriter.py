from __future__ import annotations
from pydantic import BaseModel, Field
import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.3
P90_TAIL_MIN_PCT = 4.0

SYSTEM_PROMPT = (
    "You are the optimization desk of Reech, a tool that simulates how a social post "
    "will spread before it's posted. You write short, sharp, creator-to-creator advice. "
    "Voice: confident, concrete, encouraging — never fluffy, never salesy, no emojis. "
    "Each suggestion must be specific to the lever and reference its simulated lift "
    "naturally. You are given levers already ranked by how much they moved the forecast; "
    "keep them in the SAME ORDER and write exactly one {title, detail} per lever."
)

# Response schema for gemini
def _schema():
    class _Item(BaseModel):
        title: str = Field(..., description="imperative headline, ~4-8 words, no trailing period")
        detail: str = Field(..., description="1-2 sentences of concrete why, references the simulated lift")

    class _Items(BaseModel):
        items: list[_Item]

    return _Items

# convert ranked levers from rank_and_select() to json input for Gemini
def _lever_brief(levers: list[dict]) -> str:
    rows = []
    for i, r in enumerate(levers, 1):
        cur = f"{r['current']:.1f}/10" if isinstance(r.get("current"), (int, float)) else "n/a"
        row = {
            "n": i,
            "subject": r["subject"],
            "current_score": cur,
            "suggested_action": r["action"],
            "entity": r.get("entity"),
            "sim_reach_lift_pct": round(r["delta_reach_pct"], 1),
            "sim_viral_lift_points": round(r["delta_viral_pts"], 1),
            "impact": r["impact"],
        }
        p90_delta = r.get("delta_p90_pct")
        if isinstance(p90_delta, (int, float)) and p90_delta >= P90_TAIL_MIN_PCT:
            row["sim_p90_lift_pct"] = round(p90_delta, 1)
            
        if r.get("reasoning"):
            row["why_it_scored"] = r["reasoning"]
        rows.append(row)
    return json.dumps(rows, indent=2)


def _gemini_copy(levers: list[dict], forecast: dict) -> list[dict]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    schema = _schema()
    prompt = (
        "Forecast for this post (Monte Carlo simulation):\n"
        f"  expected reach: {round(forecast.get('expected_reach', 0)):,}\n"
        f"  viral probability: {round(forecast.get('viral_probability', 0) * 100)}%\n"
        f"  confidence: {round(forecast.get('confidence', 0) * 100)}%\n\n"
        "Levers, already ranked by simulated reach lift (keep this order):\n"
        f"{_lever_brief(levers)}\n\n"
        "Write one suggestion per lever. Ground every quantitative claim ONLY in the "
        "numbers given for THAT lever — its sim_reach_lift_pct and sim_viral_lift_points "
        "(e.g. 'lifted simulated reach ~12%', 'added ~3 pts to its viral odds'). Some "
        "levers ALSO include sim_p90_lift_pct: for those you MAY say it widens the upside "
        "tail / raises the 'if it pops' ceiling by ~that %. If a lever has NO "
        "sim_p90_lift_pct, never mention any tail/p90/ceiling. Never cite p10/p50, "
        "confidence, or any metric not listed for the lever. Frame lifts as SIMULATED "
        "estimates, not promises. Only item 1 may be called the strongest lever. For a "
        "'soften' lever, be clear it's about dialing something DOWN. If a lever has an "
        "'entity', name it in the copy.\n"
        "why_it_scored (when a lever includes it) describes the CURRENT post and explains "
        "why it received its current dimension score. It does NOT explain the simulated lift "
        "and is not evidence that the suggested intervention will work. suggested_action "
        "describes the counterfactual edit that was re-simulated. Keep those roles distinct. "
        "Do not invent post details that are absent from why_it_scored. You may propose a "
        "concrete edit consistent with suggested_action, but clearly frame it as a "
        "recommendation, not as something already present in the post. "
        f"Return exactly {len(levers)} items in order."
    )
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=schema,
            temperature=TEMPERATURE,
            # copywriting needs no reasoning tokens — thinking ~5x's latency for no gain
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    parsed = resp.parsed or schema.model_validate_json(resp.text)
    items = parsed.items
    if len(items) != len(levers):
        raise ValueError(f"Gemini returned {len(items)} items for {len(levers)} levers")
    return [
        {"title": it.title.strip(), "detail": it.detail.strip(), "impact": r["impact"]}
        for it, r in zip(items, levers)
    ]

# If gemini is unavailable then fallback for lever entities
def _template_suggestion(r: dict) -> dict:
    pct = round(r["delta_reach_pct"])
    if r["label"] == "trend" and r.get("entity"):
        return {
            "title": f"Ride “{r['entity']}” while it trends",
            "detail": (f"{r['entity']} is peaking right now, and aligning with it lifted "
                       f"simulated reach ~{pct}%. Post while the wave is live."),
            "impact": r["impact"],
        }
    cur = r.get("current")
    curtxt = f" (currently {cur:.1f}/10)" if isinstance(cur, (int, float)) else ""
    return {
        "title": r["title"],
        "detail": (f"Your {r['subject']}{curtxt} is a high-leverage lever here — "
                   f"{r['action']} lifted simulated reach ~{pct}% across the re-runs."),
        "impact": r["impact"],
    }


def _maxed_out() -> dict:
    return {
        "title": "You're near this post's ceiling",
        "detail": ("No single edit moved the forecast much in simulation — the creative is "
                   "already well-tuned. Your biggest lever now is timing and consistency: "
                   "post when your audience is most active."),
        "impact": "low",
    }

# frontend ready suggestions
def write_suggestions(levers: list[dict], forecast: dict) -> list[dict]:
    if not levers:
        return [_maxed_out()]
    try:
        return _gemini_copy(levers, forecast)
    except Exception as e: 
        logger.warning("Analyse copywriter: Gemini unavailable, using templates — %s", e)
        return [_template_suggestion(r) for r in levers]
