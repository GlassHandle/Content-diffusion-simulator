from .concepts import extract_concepts,filter_concepts
from .wikidata import resolve_entities
from .keyword_extractor import get_keywords
from .entity_resolver import EntityResolver
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from .config import (MODEL_NAME,TOP_N_KEYWORDS,TOP_N_TAGS,TOP_N_TAGS_FOREACH,TAGS_WEIGHTS)
from .tagger import Tagger

class TrendProcessor:
    def __init__(self):
        self.model=SentenceTransformer(MODEL_NAME)
        self.tagger=Tagger()
        self.entity_resolver = EntityResolver()
        self.kw_model = KeyBERT(self.model)

    def process(self,source,item,text,initial_concepts=None):
        concepts = extract_concepts(source,text,initial_concepts=initial_concepts)
        keywords = get_keywords(text,self.kw_model,TOP_N_KEYWORDS)
        
        if not concepts and not keywords:
            item["tags"] = []
            item["enitites"] = {}
            item["concepts"] = {}
            item["keywords"] = {}
            return item
            
        concepts = filter_concepts(concepts,keywords)
        wikidata_results = resolve_entities(concepts)
        resolved_entities = self.entity_resolver.resolve_all(
            wikidata_results,
            text
        )

        final_concepts = {}
        for i in resolved_entities:
            if resolved_entities[i]:
                final_concepts[i]=resolved_entities[i]['description']

        tag_scores = {}

        concept_text = " ".join(final_concepts.keys())
        concept_tags = self.tagger.get_tags(concept_text,TOP_N_TAGS_FOREACH) if concept_text else {}
        keyword_text = " ".join(keywords.keys())
        keyword_tags = self.tagger.get_tags(keyword_text,TOP_N_TAGS_FOREACH) if keyword_text else {}
        entity_text = " ".join(value for value in final_concepts.values())
        entity_tags=self.tagger.get_tags(entity_text,TOP_N_TAGS_FOREACH) if entity_text else {}
        base_tags = self.tagger.get_tags(text,TOP_N_TAGS_FOREACH)

        for tag, score in concept_tags.items():
            tag_scores[tag] = tag_scores.get(tag,0)+(score*TAGS_WEIGHTS[source]["concepts"])
        for tag, score in keyword_tags.items():
            tag_scores[tag] = tag_scores.get(tag,0)+(score*TAGS_WEIGHTS[source]["keywords"])
        for tag, score in entity_tags.items():
            tag_scores[tag] = tag_scores.get(tag,0)+(score*TAGS_WEIGHTS[source]["entities"])
        for tag, score in base_tags.items():
            tag_scores[tag] = tag_scores.get(tag,0)+(score*TAGS_WEIGHTS[source]["text"])
        
        sorted_tags = sorted(tag_scores.items(),key=lambda x: x[1],reverse=True)
        max_score = sorted_tags[0][1] if sorted_tags else 0

        filtered_tags = []
        seen_roots = set()

        for tag, score in sorted_tags:
            root = tag.split(">")[0].strip()
            if root in seen_roots:
                continue
            best_tag = tag
            curr_score=score
            best_depth = len(tag.split(">"))

            for other_tag, other_score in sorted_tags:
                if other_tag.split(">")[0].strip() != root:
                    continue

                depth=len(other_tag.split(">"))

                if depth > best_depth:
                    best_tag = other_tag
                    curr_score=other_score
                    best_depth = depth

            filtered_tags.append([best_tag,curr_score])
            seen_roots.add(root)

        item["tags"] = [tag for tag, score in filtered_tags if score >= max_score * 0.4][:TOP_N_TAGS]
        item["concepts"] = final_concepts
        item["keywords"] = keywords

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