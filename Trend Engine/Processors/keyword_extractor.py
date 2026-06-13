def get_keywords(text,kw_model,top_n=10):
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=top_n,
        use_mmr=True,
        diversity=0.7
    )
    return [keyword for keyword, score in keywords]