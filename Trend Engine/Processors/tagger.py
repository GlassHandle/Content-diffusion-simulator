from sklearn.metrics.pairwise import cosine_similarity

def get_tags(primary_text,secondary_text,model,tag_embeddings,tags,top_n=5):
    primary_scores = cosine_similarity(
        [model.encode(primary_text)],
        tag_embeddings
    )[0]
    if secondary_text:
        secondary_scores = cosine_similarity(
            [model.encode(secondary_text)],
            tag_embeddings
        )[0]
        text_len = len(primary_text.split())
        match text_len:
            case n if n < 4:
                primary_weight = 0.6
                secondary_weight = 0.4
            case n if n < 8:
                primary_weight = 0.75
                secondary_weight = 0.25
            case _:
                primary_weight = 0.9
                secondary_weight = 0.1
        scores = (
            primary_weight * primary_scores +
            secondary_weight * secondary_scores
        )
    else:
        scores = primary_scores
    return [tags[i] for i in scores.argsort()[-top_n:][::-1]]