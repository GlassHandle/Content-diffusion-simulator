from .concepts import isValid,normalize

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
        keyword = normalize(keyword)
        if not isValid(keyword):
            continue
        if keyword in seen:
            continue
        seen.add(keyword)
        candidates.append((keyword,round(float(score),4)))

    candidates.sort(key=lambda x: x[1],reverse=True)

    results = {}
    covered_words = set()

    for keyword, score in candidates:
        words = set(keyword.split())
        if len(words & covered_words)>=2:
            continue
        results[keyword] = score
        covered_words.update(words)
        if len(results) >= top_n:
            break

    return results