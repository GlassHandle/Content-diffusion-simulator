import spacy
import re
from .config import (STOP_CONCEPTS,IGNORE_ENTITY_TYPES,TYPE_MAP,TYPE_WEIGHTS,TOP_N_CONCEPTS)

nlp = spacy.load("en_core_web_sm")

def isValid(concept):
    if len(concept) < 3:
        return False
    if concept.isdigit():
        return False
    if not re.search(r"[a-zA-Z]", concept):
        return False
    if concept in STOP_CONCEPTS:
        return False
    if "http://" in concept or "https://" in concept:
        return False
    return True

def normalize_concept(text):
    text = text.lower().strip()
    text = text.replace("’", "'")
    text = text.replace("  "," ")
    text = re.sub(r"'s\b", "", text)
    return text

def extract_concepts(text,initial_concepts=None):
    doc = nlp(text)

    concepts = {}

    if initial_concepts:
        for concept in initial_concepts:
            value=normalize_concept(concept)
            if not isValid(value):
                continue
            concepts[value]="initial"

    for ent in doc.ents:
        if ent.label_ in IGNORE_ENTITY_TYPES:
            continue
        value=normalize_concept(ent.text)
        if(not isValid(value)):
            continue
        if ent.label_ in TYPE_MAP:
            concepts[value]=TYPE_MAP[ent.label_]

    return concepts

def filter_concepts(concepts,keywords,max_concepts=TOP_N_CONCEPTS):
    scores = {}

    for concept, concept_type in concepts.items():
        score = TYPE_WEIGHTS.get(concept_type,0)
        for keyword, keyword_score in keywords.items():
            keyword_words = set(keyword.split())
            if set(concept.split()).issubset(keyword_words):
                score += keyword_score
        scores[concept] = score

    ranked = sorted(scores.items(),key=lambda x: x[1],reverse=True)

    selected = {concept: concepts[concept] for concept, _ in ranked[:max_concepts]}
    return selected
