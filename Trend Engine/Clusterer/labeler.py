"""Cluster labeling and naming logic."""

from typing import Dict, List, Optional, Set
from collections import Counter
from .config import MIN_KEYWORD_SCORE, MAX_KEYWORDS_PER_ITEM, TOP_TERMS_FOR_LABEL, EXCLUDED_SOURCES
from .text_builder import filter_keywords


def merge_sub_terms(terms: List[str]) -> List[str]:
    """
    Remove subterms that are contained in other terms.

    Example: if "machine learning" and "learning" are both present,
    remove "learning" since it's a sub-term.
    """
    if len(terms) <= 1:
        return terms

    sorted_terms = sorted(terms, key=lambda t: -len(t))
    kept = []

    for term in sorted_terms:
        if any(term in other and term != other for other in kept):
            continue
        kept.append(term)

    return [t for t in terms if t in kept]


def weighted_label_for_cluster(
    cluster_items: List[Dict],
    top_n: int = TOP_TERMS_FOR_LABEL,
    blocklist: Optional[Set[str]] = None,
    excluded_sources: Optional[Set[str]] = None,
) -> str:
    """
    Generate a weighted label for a cluster based on its items..
    """
    blocklist = blocklist or set()
    excluded_sources = excluded_sources or EXCLUDED_SOURCES
    term_weight = Counter()

    # Aggregate weighted keywords and concepts
    for item in cluster_items:
        kws = filter_keywords(
            item.get("keywords", {}),
            min_score=MIN_KEYWORD_SCORE,
            max_terms=MAX_KEYWORDS_PER_ITEM,
            blocklist=blocklist,
        )
        for term, score in kws.items():
            term_weight[term.lower()] += score

        if item.get("source") not in excluded_sources:
            for conc in item.get("concepts", {}):
                if conc.lower() not in blocklist:
                    term_weight[conc.lower()] += 1.0

    # Fallback: if no weighted terms, use raw keyword frequency
    if not term_weight:
        raw = Counter()
        for item in cluster_items:
            for kw in item.get("keywords", {}):
                if kw.lower() not in blocklist:
                    raw[kw.lower()] += 1
        term_weight = Counter({k: float(v) for k, v in raw.most_common(top_n)})

    # Get top candidates and merge sub-terms
    candidates = [
        term.replace("_", " ").title()
        for term, _ in term_weight.most_common(top_n * 2)
    ]
    merged = merge_sub_terms(candidates)[:top_n]

    return " / ".join(merged) if merged else "Misc/Low-Signal"
