import spacy
import re
from .config import (STOP_CONCEPTS,IGNORE_ENTITY_TYPES,TYPE_MAP,TYPE_WEIGHTS,TOP_N_CONCEPTS)

nlp = spacy.load("en_core_web_sm")

def isValid(concept):
    concept = concept.strip().lower()
    if len(concept) < 3:
        return False
    if concept.isdigit():
        return False
    if concept in STOP_CONCEPTS:
        return False
    if "http://" in concept or "https://" in concept:
        return False
    if not re.search(r"[a-zA-Z]", concept):
        return False
    if re.search(r"[\U0001F300-\U0001FAFF"r"\U00002700-\U000027BF"r"\U000024C2-\U0001F251]",concept):
        return False
    if re.search(r"^[ru]/", concept):
        return False
    if not re.fullmatch(r"[a-zA-Z0-9\s\-']+", concept):
        return False
    if (len(concept.split()) == 1 and re.search(r"\d", concept) and len(concept) > 8):
        return False
    return True

def normalize(text):
    text = text.lower().strip()
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = re.sub(r"'s\b", "", text)
    text = text.strip(".,;:!?()[]{}\"'")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*-\s*", "-", text)
    return text

def extract_concepts(source:str,text:str,initial_concepts=None):
    doc = nlp(text)
    concepts = []

    if initial_concepts:
        for concept in initial_concepts:
            value=normalize(concept)
            if isValid(value):
                concepts.append((value, "initial"))

    if source != "google-trends":
        for ent in doc.ents:
            if ent.label_ in IGNORE_ENTITY_TYPES:
                continue
            value=normalize(ent.text)
            if not isValid(value):
                continue
            if ent.label_ in TYPE_MAP:
                concepts.append((value, TYPE_MAP[ent.label_]))
    else:
        concepts = handle_trends(text)

    result = {}
    for key, value in concepts:
        result.setdefault(key, value)

    return result

def handle_trends(text:str):
    data = text.split(",")
    for i in range(len(data)):
        data[i]=normalize(data[i])
    filtered_data = [(val,"unknown") for val in data if isValid(val) and len(val.split())<=5]
    return filtered_data

def filter_concepts(concepts,keywords,max_concepts=TOP_N_CONCEPTS):
    scores = {}

    for concept, concept_type in concepts.items():
        score = TYPE_WEIGHTS.get(concept_type,0)
        c_words = set(concept.split())
        for keyword, keyword_score in keywords.items():
            k_words = set(keyword.split())
            overlap = len(c_words & k_words)
            if overlap > 0:
                score += (overlap / len(c_words | k_words)) * keyword_score
        scores[concept] = score

    ranked = sorted(scores.items(),key=lambda x: x[1],reverse=True)

    selected = {concept: concepts[concept] for concept, _ in ranked[:max_concepts]}
    for key in keywords:
        if key not in scores and len(key.split())>=2:
            selected[key]="Unknown"
    
    return selected
