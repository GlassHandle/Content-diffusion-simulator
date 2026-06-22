import json
import shutil
from datetime import datetime, UTC
from pathlib import Path

import feedparser


class GoogleTrendsFallback:
    def __init__(self, region="IN"):
        self.region = region
        self.base_dir = Path(__file__).resolve().parent
    
    @staticmethod
    def parse_search_volume(value):
        if not value:
            return 0
        value = str(value).strip().upper().replace("+", "")
        multipliers = {
            "K": 1_000,
            "M": 1_000_000,
            "B": 1_000_000_000,
        }
        suffix = value[-1]

        if suffix in multipliers:
            try:
                return int(float(value[:-1]) * multipliers[suffix])
            except ValueError:
                return value
        try:
            return int(value)
        except ValueError:
            return value

    def collect(self):
        url = (f"https://trends.google.com/trending/rss"f"?geo={self.region}")
        feed = feedparser.parse(url)
        results = []
        extraction_time = datetime.now(UTC).strftime("%Y-%m-%d_%H.%M.%S")
        for entry in feed.entries:
            value=entry.get("ht_approx_traffic","")
            value=self.parse_search_volume(value=value)
            results.append({
                "id": "",
                "Trends": entry.title,
                "Search volume": value,
                "Started": entry.get("published",""),
                "Ended": "",
                "Trend breakdown": entry.get("ht_news_item_title",""),
                "Explore link": entry.link,
                "region": self.region,
                "source": "google_trends",
                "extraction_utc": extraction_time
            })

        return results

    def save(self, data):
        raw_dir = (self.base_dir.parent.parent/ "data"/ "raw")
        raw_dir.mkdir(parents=True,exist_ok=True)
        latest_file = (raw_dir / "google-trends-latest.json")
        last_file = (raw_dir / "google-trends-last.json")
        if latest_file.exists():shutil.copy2(latest_file,last_file)

        with open(latest_file,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)
