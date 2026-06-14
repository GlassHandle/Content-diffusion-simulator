import re

def valid_keyword(keyword):
    keyword = keyword.lower().strip()
    if len(keyword) < 3:
        return False
    if keyword.isdigit():
        return False
    if not re.search(r"[a-zA-Z]", keyword):
        return False
    if "http://" in keyword or "https://" in keyword:
        return False
    return True


def get_keywords(text, kw_model, top_n=10):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=top_n * 3,
        use_mmr=True,
        diversity=0.7
    )

    candidates = []
    seen = set()

    for keyword, score in keywords:
        keyword = keyword.lower().strip()
        if not valid_keyword(keyword):
            continue
        if keyword in seen:
            continue
        seen.add(keyword)
        candidates.append((keyword,round(float(score),4)))

    candidates.sort(key=lambda x: len(x[0].split()),reverse=True)

    results = {}
    covered_words = set()

    for keyword, score in candidates:
        words = set(keyword.split())
        overlap=len(words & covered_words)
        if overlap>=2:
            continue
        results[keyword] = score
        covered_words.update(words)
        if len(results) >= top_n:
            break

    return results