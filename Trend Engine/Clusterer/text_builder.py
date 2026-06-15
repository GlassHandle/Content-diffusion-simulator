"""Text preparation and keyword filtering."""

from typing import Dict, Optional, Set, Tuple
from .config import MIN_KEYWORD_SCORE, MAX_KEYWORDS_PER_ITEM, EXCLUDED_SOURCES


def filter_keywords(
    keywords_dict: Dict[str, float],
    min_score: float = MIN_KEYWORD_SCORE,
    max_terms: Optional[int] = MAX_KEYWORDS_PER_ITEM,
    blocklist: Optional[Set[str]] = None,
) -> Dict[str, float]:
    if not keywords_dict:
        return {}
    blocklist = blocklist or set()
    strong = {
        k: v for k, v in keywords_dict.items()
        if v >= min_score and k.lower() not in blocklist
    }
    if not strong:
        strong = dict(sorted(keywords_dict.items(), key=lambda x: x[1], reverse=True)[:3])
        strong = {k: v for k, v in strong.items() if k.lower() not in blocklist}
        if not strong:
            return {}
    if max_terms and len(strong) > max_terms:
        strong = dict(sorted(strong.items(), key=lambda x: x[1], reverse=True)[:max_terms])
    return strong

def build_texts(
    item: Dict,
    blocklist: Optional[Set[str]] = None,
    excluded_sources: Optional[Set[str]] = None,
) -> Tuple[str, str]:
    blocklist = blocklist or set()
    excluded_sources = excluded_sources or EXCLUDED_SOURCES
    kws = filter_keywords(
        item.get("keywords", {}),
        min_score=MIN_KEYWORD_SCORE,
        max_terms=MAX_KEYWORDS_PER_ITEM,
        blocklist=blocklist,
    )
    # Extract concepts
    if item.get("source") in excluded_sources:
        concs = []
    else:
        concs = [
            c.lower() for c in item.get("concepts", {}).keys()
            if c.lower() not in blocklist
        ]
        concs = list(set(concs))

    tags = list(set(
        t.lower() for t in item.get("tags", [])
        if t.lower() not in blocklist
    ))

    # Format for SentenceTransformer: natural language is better than comma-separated
    concs_str = ", ".join(concs) if concs else "various entities"
    kws_str = ", ".join(kws.keys()) if kws else "general topics"
    tags_str = ", ".join(tags) if tags else "uncategorized domains"

    embedding_text = (
        f"This content relates to the categories of {tags_str}. "
        f"It involves entities like {concs_str}, with a specific focus on {kws_str}."
    )

    # Legacy label text (for TF-IDF fallback if needed)
    label_parts = []
    label_parts.extend([k.replace(" ", "_") for k in kws])
    label_parts.extend([c.replace(" ", "_") for c in concs])
    label_text = " ".join(label_parts)

    return embedding_text, label_text
