import os
import json
from pathlib import Path
from dotenv import load_dotenv
import praw
import shutil
from datetime import datetime,UTC

load_dotenv()

reddit=praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

class RedditCollector:
    def collect(self,limit=500):
        posts=[]
        feeds=[
            ("rising",reddit.subreddit("all").rising(limit=limit)),
            ("hot",reddit.subreddit("all").hot(limit=limit)),
            ("top_day",reddit.subreddit("all").top(time_filter="day",limit=limit))
        ]

        extraction_time = datetime.now(UTC).strftime("%Y-%m-%d_%H.%M.%S")

        for feed_name,feed in feeds:
            for post in feed:
                sub=post.subreddit
                posts.append({
                    "id": post.id,
                    "post_description": post.selftext or "",
                    "title": post.title,
                    "source": "reddit",
                    "region": "global",
                    "feed": feed_name,
                    "subreddit":sub.display_name,
                    "subreddit_description":sub.public_description or "",
                    "created_utc": datetime.fromtimestamp(post.created_utc,UTC).strftime("%Y-%m-%d_%H.%M.%S"),
                    "extracted_utc": extraction_time,
                    "upvotes": post.score,
                    "comments": post.num_comments
                })
        return posts
    
    def save(self, data):
        raw_dir = (self.base_dir.parent.parent/ "data"/ "raw")
        raw_dir.mkdir(parents=True,exist_ok=True)
        latest_file = (raw_dir / "reddit-latest.json")
        last_file = (raw_dir / "reddit-last.json")

        if latest_file.exists():
            shutil.copy2(latest_file,last_file)

        with open(latest_file,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=4,ensure_ascii=False)


if __name__=="__main__":
    collector=RedditCollector()
    posts=collector.collect(limit=30)
    collector.save(posts)
    
