import requests
from time import sleep

from .cache import EntityCache

SEARCH_URL = "https://www.wikidata.org/w/api.php"
HEADERS = {"User-Agent": "TrendEngine/1.0 (research project)"}

cache = EntityCache()


def search_entity(entity, limit=3, retries=3):
    params = {
        "action": "wbsearchentities",
        "search": entity,
        "language": "en",
        "limit": limit,
        "format": "json"
    }

    for attempt in range(retries):
        try:
            response = requests.get(SEARCH_URL,params=params,headers=HEADERS,timeout=10)
            if response.status_code == 429:
                wait = 2**(attempt + 1)
                print(f"Rate limited for '{entity}', retrying in {wait}s...")
                sleep(wait)
                continue

            response.raise_for_status()
            results = response.json().get("search", [])
            return [
                {
                    "id": result["id"],
                    "label": result["label"],
                    "description": result.get("description", "")
                }
                for result in results
            ]

        except requests.RequestException as e:
            if attempt == retries - 1:
                raise e
            wait = 2**(attempt + 1)
            print(f"Request failed for '{entity}', retrying in {wait}s...")
            sleep(wait)

    return []


def resolve_entities(entities):
    resolved = {}
    missing = []

    for entity in entities:
        cached = cache.get(entity)
        if cached is not None:
            resolved[entity] = cached
        else:
            missing.append(entity)

    for entity in missing:
        try:
            results = search_entity(entity)
            resolved[entity] = results
            cache.set(entity,results)
            sleep(0.5)

        except Exception as e:
            print(f"Failed: {entity} -> {e}")
            resolved[entity] = []
            cache.set(entity,[])

    cache.save()
    return resolved