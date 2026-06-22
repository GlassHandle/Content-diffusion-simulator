import json
from pathlib import Path

class EntityCache:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.cache_path = (base_dir.parent / "data" / "cache" / "entity_cache.json")

        self.cache_path.parent.mkdir(parents=True,exist_ok=True)

        if self.cache_path.exists():
            with open(self.cache_path, "r", encoding="utf-8") as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def get(self, entity):
        return self.cache.get(entity.lower())

    def set(self, entity, data):
        self.cache[entity.lower()] = data
        self.save()

    def save(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=4)