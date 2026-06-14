from .concepts import extract_concepts,filter_concepts
from .wikidata import resolve_entities
from .keyword_extractor import get_keywords
from .entity_resolver import EntityResolver
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from .config import (MODEL_NAME,TOP_N_KEYWORDS,TOP_N_TAGS)
from .tagger import Tagger

class TrendProcessor:
    def __init__(self):
        self.model=SentenceTransformer(MODEL_NAME)
        self.tagger=Tagger()
        self.entity_resolver = EntityResolver()
        self.kw_model = KeyBERT(self.model)

    def process(self, item, text,initial_concepts=None):
        concepts = extract_concepts(text,initial_concepts=initial_concepts)
        keywords = get_keywords(text,self.kw_model,TOP_N_KEYWORDS)
        concepts = filter_concepts(concepts,keywords)
        wikidata_results = resolve_entities(concepts)
        resolved_entities = self.entity_resolver.resolve_all(
            concepts,
            wikidata_results,
            text
        )

        tag_scores = {}
        for entity_data in resolved_entities.values():
            if not entity_data:
                continue
            description = entity_data.get("description","")
            if not description:
                continue
            entity_tags = self.tagger.get_tags(description)

            for tag, score in entity_tags.items():
                tag_scores[tag] = (tag_scores.get(tag,0)+score)
        
        sorted_tags = sorted(tag_scores.items(),key=lambda x: x[1],reverse=True)
        item["tags"] = [tag for tag, _ in sorted_tags[:TOP_N_TAGS]]
        item["concepts"] = concepts
        item["keywords"] = keywords

        return item

    def process_all(self,source,data, text_builder):
        processed = []

        for item in data:
            text = text_builder(item)
            if source=="reddit":
                processed.append(self.process(item,text,[item.get("subreddit")]))
            else:
                processed.append(self.process(item,text))
        return processed