import json
from datetime import datetime,UTC
from scraper import scraper
from pathlib import Path
import shutil

class RedditFallback:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent

    def collect(self, soup):
        data=soup.find("shreddit-feed")
        output=[]
        extraction_time = datetime.now(UTC).strftime("%Y-%m-%d_%H.%M.%S") 
        if data:
            posts=data.find_all("shreddit-post")
            for post in posts:
                title=post.get("post-title") if post.has_attr("post-title") else ""
                id=post.get("id") if post.has_attr("id") else ""
                upvotes=post.get("score") if post.has_attr("score") else 0
                subreddit=post.get("subreddit-name") if post.has_attr("subreddit-name") else ""
                comments=post.get("comment-count") if post.has_attr("comment-count") else 0
                created_utc=post.get("created-timestamp") if post.has_attr("created-timestamp") else ""
                formatted = datetime.strptime(created_utc,"%Y-%m-%dT%H:%M:%S.%f%z").strftime("%Y-%m-%d_%H.%M.%S") if created_utc else ""

                if id and title:
                    output.append({
                    "id":id,
                    "title":title,
                    "source":"reddit",
                    "region":"IN",
                    "feed":"popular",
                    "subreddit":subreddit,
                    "created_utc":formatted,
                    "extracted_utc":extraction_time,
                    "upvotes":upvotes,
                    "comments":comments
                })
        return output

    def save(self, data ,source):
        raw_dir = (self.base_dir.parent.parent/ "data"/ "raw")
        raw_dir.mkdir(parents=True,exist_ok=True)
        latest_file = (raw_dir / f"{source}-latest.json")
        last_file = (raw_dir / f"{source}-last.json")

        if latest_file.exists():
            shutil.copy2(latest_file,last_file)

        with open(latest_file,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)

if __name__=="__main__":
    encoder = RedditFallback()
    data=scraper("https://www.reddit.com/r/popular/",encoder.collect)
    encoder.save(data,"reddit")
