import json
from pathlib import Path

from Processors.pipeline import TrendProcessor

BASE_DIR = Path(__file__).resolve().parent

processor = TrendProcessor()

SOURCES = {
    "reddit": lambda item: (item.get("title", "") + " . "+ item.get("post_description", "")),
    "youtube": lambda item: (item.get("title", "") + " . " + item.get("description", "")),
    "google-trends": lambda item: (item.get("Trend", "") + " . " + item.get("Trend breakdown", ""))
}

temp_dir = BASE_DIR.parent / "data" / "temp"
temp_dir.mkdir(parents=True, exist_ok=True)

for source, text_builder in SOURCES.items():
    with open(BASE_DIR.parent / "data" / "raw" / f"{source}.json","r",encoding="utf-8") as f:
        data = json.load(f)

    results = processor.process_all(
        source,
        data,
        text_builder
    )

    with open(temp_dir / f"{source}.json","w",encoding="utf-8") as f:
        json.dump(results,f,indent=4,ensure_ascii=False)

    print(f"Processed {source}")