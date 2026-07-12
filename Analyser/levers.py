from __future__ import annotations
import re

DELTA = 2.0
MIN_LIFT_PCT = 1.5
MAX_SUGGESTIONS = 4
BOOST_GATE = 3.5            
CONTROVERSY_DOWN_GATE = 5.0  

GENERAL_DIMS = ["curiosity", "novelty", "relatability", "emotional_intensity"]
GATED_DIMS = ["humor", "educational", "practical_value"]

HINTS: dict[str, tuple[str, str, str]] = {
    "dim:humor":               ("humor", "Sharpen the humor",
                                "land a harder punchline or funnier framing"),
    "dim:curiosity":           ("curiosity", "Open a stronger curiosity gap",
                                "tease the payoff up front without giving it away"),
    "dim:educational":         ("educational value", "Teach one concrete thing",
                                "make the takeaway sharper and more useful"),
    "dim:novelty":             ("novelty", "Make it feel fresher",
                                "a format, angle, or detail viewers haven't seen"),
    "dim:controversy_up":      ("point of view", "Take a clearer stance",
                                "a claim people can push back on drives comments"),
    "dim:controversy_down":    ("divisiveness", "Soften the divisive edge",
                                "the friction is costing you reach on this one"),
    "dim:emotional_intensity": ("emotional punch", "Raise the emotional stakes",
                                "a stronger high-arousal beat — awe, joy, tension"),
    "dim:relatability":        ("relatability", "Make it more 'that's so me'",
                                "a detail a wide audience instantly recognizes"),
    "dim:practical_value":     ("practical value", "Add something actionable",
                                "a tip or takeaway worth acting on"),
    "composite:shareability":  ("shareability", "Give them a reason to share",
                                "a hook or moment viewers want to send to a friend"),
    "composite:saveability":   ("saveability", "Add a save-worthy takeaway",
                                "a tip, list, or reference worth bookmarking"),
    "trend":                   ("trend alignment", "Ride a trend that's peaking",
                                "align with a topic the algorithm is boosting right now"),
}

# normalise text and break into unique words
def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))

# get the tokens (words) from topics, entities, tags
def _content_theme_tokens(content: dict) -> set[str]:
    toks: set[str] = set()
    for topic, val in (content.get("topics") or {}).items():
        if isinstance(val, (int, float)) and val > 0:
            toks |= _tokens(topic)
    for ent in content.get("entities") or []:
        if isinstance(ent, str):
            toks |= _tokens(ent)
    for tag in content.get("tags") or []:
        if isinstance(tag, str):
            toks |= _tokens(tag)
    return toks

# find the best entity from Layer 1 output that is relevant to the content but is not present in its tokens 
def _trend_lever(content: dict, trend: dict | None) -> dict | None:
    if not trend:
        return None
    theme = _content_theme_tokens(content)
    if not theme:
        return None
    have = {e.lower() for e in (content.get("entities") or []) if isinstance(e, str)}

    best = None
    for e in trend.get("trending_entities") or []:
        if not isinstance(e, dict):
            continue
        label = e.get("label")
        if not label or label.lower() in have:
            continue
        ent_tokens = _tokens(label) | _tokens(" ".join(e.get("tags") or []))
        if not (theme & ent_tokens):      
            continue
        weight = e.get("weight", 0) or 0
        if best is None or weight > best[1]:
            best = (label, weight)

    if best is None:
        return None
    label = best[0]
    return {
        "scenario": {"label": "trend", "ops": [{"add_entity": label}]},
        "meta": {"entity": label},
    }

# generate general scenarios
def _general_scenarios() -> list[dict]:
    scen = [{"label": f"dim:{d}", "ops": [{"dim": d, "delta": DELTA}]} for d in GENERAL_DIMS]
    scen.append({"label": "composite:shareability", "ops": [{"composite": "shareability", "delta": DELTA}]})
    return scen

# content-derived scenarios
def content_levers(content: dict) -> list[dict]:
    dims = content.get("dims") or {}
    comp = content.get("composites") or {}

    def cur(name: str, src: dict) -> float:
        v = src.get(name, 0)
        return float(v) if isinstance(v, (int, float)) else 0.0

    scen: list[dict] = []
    for d in GATED_DIMS:
        if cur(d, dims) >= BOOST_GATE:
            scen.append({"label": f"dim:{d}", "ops": [{"dim": d, "delta": DELTA}]})

    controversy = cur("controversy", dims)
    if controversy >= BOOST_GATE:            
        scen.append({"label": "dim:controversy_up", "ops": [{"dim": "controversy", "delta": DELTA}]})
    if controversy >= CONTROVERSY_DOWN_GATE:  
        scen.append({"label": "dim:controversy_down", "ops": [{"dim": "controversy", "delta": -DELTA}]})

    if cur("saveability", comp) >= BOOST_GATE: 
        scen.append({"label": "composite:saveability", "ops": [{"composite": "saveability", "delta": DELTA}]})

    return scen


# __control__ is the actual scenario
def build_scenarios(content: dict, trend: dict | None) -> tuple[list[dict], dict]:
    scen: list[dict] = [{"label": "__control__", "ops": []}]
    scen += _general_scenarios()
    scen += content_levers(content)
    meta: dict[str, dict] = {}

    trend_lever = _trend_lever(content, trend)
    if trend_lever:
        scen.append(trend_lever["scenario"])
        meta["trend"] = trend_lever["meta"]

    return scen, meta

# return the current value of the tested dim or composite with the changed lever
def current_value(label: str, content: dict) -> float | None:
    dims = content.get("dims") or {}
    comp = content.get("composites") or {}
    if label.startswith("dim:"):
        name = label[4:].replace("_up", "").replace("_down", "")
        v = dims.get(name)
        return float(v) if isinstance(v, (int, float)) else None
    if label == "composite:shareability":
        v = comp.get("shareability")
        return float(v) if isinstance(v, (int, float)) else None
    if label == "composite:saveability":
        v = comp.get("saveability")
        return float(v) if isinstance(v, (int, float)) else None
    return None

# Get the reasoning for dims' from L3 output for Gemini response
def _dim_reasoning(label: str, content: dict) -> str | None:
    if not label.startswith("dim:"):
        return None
    name = label[4:].replace("_up", "").replace("_down", "")
    scores = ((content.get("analysis") or {}).get("engagement") or {}).get("scores") or {}
    entry = scores.get(name)
    if isinstance(entry, dict):
        r = entry.get("reasoning")
        if isinstance(r, str) and r.strip():
            return r.strip()
    return None


def _impact(pct: float) -> str:
    if pct >= 15.0:
        return "high"
    if pct >= 5.0:
        return "medium"
    return "low"

# filter and return the best 4 scenarios that improved the react
def rank_and_select(scenarios: list[dict], content: dict, meta: dict) -> list[dict]:
    by_label = {s["label"]: s for s in scenarios}
    control = by_label.get("__control__")
    if not control or control.get("expected_reach", 0) <= 0:
        return []
    base_reach = control["expected_reach"]
    base_viral = control.get("viral_probability", 0.0)
    base_p90 = control.get("reach_p90", 0.0)

    ranked: list[dict] = []
    for s in scenarios:
        if s["label"] == "__control__":
            continue
        subject, title, action = HINTS.get(s["label"], (s["label"], s["label"], ""))
        scenario_p90 = s.get("reach_p90")
        delta_p90_pct = ((scenario_p90-base_p90)/base_p90*100 if isinstance(scenario_p90,(int,float)) and base_p90>0 else None)
        ranked.append({
            "label": s["label"],
            "subject": subject,
            "title": title,
            "action": action,
            "current": current_value(s["label"], content),
            "entity": meta.get(s["label"], {}).get("entity"),
            "delta_reach_pct": (s["expected_reach"] - base_reach) / base_reach * 100.0,
            "delta_viral_pts": (s.get("viral_probability", 0.0) - base_viral) * 100.0,
            "delta_p90_pct": delta_p90_pct,
            "reasoning": _dim_reasoning(s["label"], content),
        })

    ranked.sort(key=lambda r: r["delta_reach_pct"], reverse=True)

    chosen = [r for r in ranked if r["delta_reach_pct"] >= MIN_LIFT_PCT][:MAX_SUGGESTIONS]

    if not chosen and ranked and ranked[0]["delta_reach_pct"] > 0:
        chosen = [ranked[0]]  
    for r in chosen:
        r["impact"] = _impact(r["delta_reach_pct"])
    return chosen
