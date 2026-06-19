from .concepts import extract_concepts,filter_concepts
from .wikidata import resolve_entities
from .keyword_extractor import get_keywords
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from .config import (MODEL_NAME,TOP_N_KEYWORDS)

class TrendProcessor:
    def __init__(self):
        self.model=SentenceTransformer(MODEL_NAME)
        self.kw_model = KeyBERT(self.model)

    def process(self,source,item,text,initial_concepts=None):
        concepts = extract_concepts(source,text,initial_concepts=initial_concepts)
        keywords = get_keywords(text,self.kw_model,TOP_N_KEYWORDS)
        
        if not concepts and not keywords:
            item["concepts"] = {}
            item["keywords"] = {}
            return item
            
        concepts = filter_concepts(concepts,keywords)
        wikidata_results = resolve_entities(concepts)
        item["concepts"] = {
            concept: candidates
            for concept, candidates in wikidata_results.items()
            if candidates
        }

        return item

    def process_all(self,source,data, text_builder):
        processed = []

        for item in data:
            text = text_builder(item)
            if source=="reddit":
                processed.append(self.process(source,item,text,[item.get("subreddit")]))
            else:
                processed.append(self.process(source,item,text))
        return processed