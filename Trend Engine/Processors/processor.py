from keybert import KeyBERT
from sentence_transformers import SentenceTransformer

from .config import (
    MODEL_NAME,
    TAGS,
    TOP_N_TAGS,
    TOP_N_KEYWORDS
)

from .tagger import get_tags
from .keyword_extractor import get_keywords
class Processor:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.kw_model = KeyBERT(self.model)
        self.tag_embeddings = self.model.encode(TAGS,show_progress_bar=False)
    def process(self,data,primary_field,secondary_field=None,description_field=None):
        for item in data:
            primary_text = item.get(
                primary_field,
                ""
            )
            secondary_text = ""
            if secondary_field:
                secondary_text = item.get(
                    secondary_field,
                    ""
                )
            item["tags"] = get_tags(
                primary_text,
                secondary_text,
                self.model,
                self.tag_embeddings,
                TAGS,
                TOP_N_TAGS
            )
            keyword_text = primary_text
            if (description_field and item.get(description_field)):
                keyword_text += (" " +item[description_field])
            item["keywords"] = get_keywords(
                keyword_text,
                self.kw_model,
                TOP_N_KEYWORDS
            )
        return data