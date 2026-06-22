from .concepts import isValid,normalize
from keyphrase_vectorizers import KeyphraseCountVectorizer

def get_keywords(text, kw_model, top_n=10,threshold=0.20):
    vectorizer = KeyphraseCountVectorizer()
    try:
        keywords = kw_model.extract_keywords(
            text,
            vectorizer=vectorizer,
            top_n=top_n * 3,
            use_mmr=True,
            diversity=0.9
        )
    except ValueError:
        keywords = []

    candidates = []
    seen = set()

    for keyword, score in keywords:
        keyword = normalize(keyword)
        if not isValid(keyword):
            continue
        if keyword in seen:
            continue
        if score<threshold:
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