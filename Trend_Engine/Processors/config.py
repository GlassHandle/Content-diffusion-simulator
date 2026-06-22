STOP_CONCEPTS = {"edit","update","tldr","source","everyone","someone","anyone","thing","things","way"}
TYPE_WEIGHTS = {
    "person": 5,
    "organization": 4,
    "event": 4,
    "product": 3,
    "location": 2,
    "keyword": 2,
    "group": 1,
    "initial": 0
}
IGNORE_ENTITY_TYPES = {"DATE","TIME","CARDINAL","ORDINAL","MONEY","PERCENT","QUANTITY"}
TYPE_MAP = {
    "PERSON": "person",
    "ORG": "organization",
    "GPE": "location",
    "LOC": "location",
    "PRODUCT": "product",
    "EVENT": "event",
    "WORK_OF_ART": "media",
}

TYPE_HINTS = {
    "person": ["person", "player", "athlete", "cricketer", "footballer", "actor", "actress", "singer", "politician", "scientist", "author"],
    "organization": ["organization", "company", "corporation", "developer", "team", "club", "university", "agency", "institution"],
    "location": ["country", "city", "state", "district", "province", "region", "location"],
    "product": ["product", "video game", "software", "phone", "application", "service", "model"],
    "event": ["event", "tournament", "league", "championship", "cup", "competition", "festival"],
    "media": ["movie", "film", "song", "album", "television", "series", "book", "novel"]
}

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_N_TAGS = 5
TOP_N_KEYWORDS = 7
TOP_N_CONCEPTS = 10
TOP_N_TAGS_FOREACH=8
TAGS_WEIGHTS = {
    "reddit":{
        "concepts":3,
        "entities":2.5,
        "keywords":1.5,
        "text":0.5
    },
    "youtube":{
        "concepts":3,
        "entities":2.5,
        "keywords":1.5,
        "text":0.5
    },
    "google-trends":{
        "concepts":0,
        "entities":1,
        "keywords":0,
        "text":0
    }
}