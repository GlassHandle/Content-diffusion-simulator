import os
import json
from pathlib import Path
import shutil
from datetime import datetime,UTC
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

youtube=build(
    serviceName="youtube",
    version="v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)

class YoutubeCollector:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        
    def collect(self,region="IN",limit=50):
        request=youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode=region,
            maxResults=limit
        )
        response = request.execute()
        videos=[]

        extraction_time = datetime.now(UTC).strftime("%Y-%m-%d_%H.%M.%S")

        for item in response["items"]:
            snippet=item["snippet"]
            stats=item["statistics"]
            videos.append({
                "id":item['id'],
                "title":snippet["title"],
                "description":snippet["description"],
                "channel":snippet["channelTitle"],
                "category_id":snippet["categoryId"],
                "published_at":snippet["publishedAt"],
                "region":region,
                "source":"youtube",
                "views":stats.get("viewCount",0),
                "likes":stats.get("likeCount",0),
                "comments":stats.get("commentCount",0),
                "extracted_utc":extraction_time
            })
        return videos
    
    def save(self, data):
        raw_dir = (self.base_dir.parent.parent/ "data"/ "raw")
        raw_dir.mkdir(parents=True,exist_ok=True)
        latest_file = (raw_dir / "youtube-latest.json")
        last_file = (raw_dir / "youtube-last.json")

        if latest_file.exists():
            shutil.copy2(latest_file,last_file)

        with open(latest_file,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)

if __name__=="__main__":
    collector=YoutubeCollector()
    videos=collector.collect(region="US",limit=50)
    collector.save(videos)
