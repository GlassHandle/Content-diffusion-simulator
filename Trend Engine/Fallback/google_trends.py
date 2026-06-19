import json
from pathlib import Path
from datetime import datetime, UTC
import shutil

import feedparser

class GoogleTrendsCollector:
    def __init__(self, region="IN"):
        self.region = region

    def _collect_daily(self):
        url = f"https://trends.google.com/trending/rss?geo={self.region}"

        feed = feedparser.parse(url)

        results = []

        for entry in feed.entries:
            results.append({
                "id": "",
                "title": entry.title,
                "articles": [],
                "image": "",
                "created_utc": "",
                "traffic": "",
            })

        return results

    def collect(self):
        extraction_time = datetime.now(UTC).strftime("%Y-%m-%d_%H.%M.%S")

        posts = []

        for item in self._collect_daily():
            item.update({
                "source": "google_trends",
                "region": self.region,
                "feed": "daily",
                "extracted_utc": extraction_time,
            })

            posts.append(item)

        return posts

    def save(self, data):
        raw_dir = (self.base_dir.parent.parent/ "data"/ "raw")
        raw_dir.mkdir(parents=True,exist_ok=True)
        latest_file = (raw_dir / "google-trends-latest.json")
        last_file = (raw_dir / "google-trends-last.json")

        if latest_file.exists():
            shutil.copy2(latest_file,last_file)

        with open(latest_file,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)


if __name__ == "__main__":
    collector = GoogleTrendsCollector(region="IN")
    posts = collector.collect()
    collector.save(posts)