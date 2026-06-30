from Graph.config import MAX_AGE_DAYS
from pathlib import Path

TOPICS = [
    "comedy", "gaming", "tech", "fitness", "food_cooking", "beauty_fashion", "travel", "music",
    "sports", "education_howto", "news_politics", "finance_business", "art_design", "science",
    "lifestyle_vlog", "parenting_family", "pets_animals", "automotive", "diy_crafts",
    "motivation_selfhelp", "relationships", "nature_outdoors", "film_tv", "health_wellness",
]

ROOT_MAP = {
    "Ad Safety Risk": None, "Adult Products and Services": None, "Alcohol": None,
    "Attractions": "travel", "Automotive": "automotive", "Books and Literature": "art_design",
    "Business and Finance": "finance_business", "Business and Industrial": "finance_business",
    "Cannabis": None, "Careers": "education_howto", "Clothing and Accessories": "beauty_fashion",
    "Collectables and Antiques": "diy_crafts", "Communication": "tech", "Computer Software": "tech",
    "Consumer Electronics": "tech", "Consumer Packaged Goods": None, "Cosmetic Services": "beauty_fashion",
    "Crime": "news_politics", "Culture and Fine Arts": "art_design", "Dating": "relationships",
    "Debated Sensitive Social Issue": "news_politics", "Dieting and Weightloss": "health_wellness",
    "Disasters": "news_politics", "Durable Goods": None, "Education": "education_howto",
    "Education and Careers": "education_howto", "Entertainment": "film_tv", "Events": None,
    "Events and Performances": None, "Family and Parenting": "parenting_family",
    "Family and Relationships": "relationships", "Finance and Insurance": "finance_business",
    "Fine Art": "art_design", "Fitness Activities": "fitness", "Food & Drink": "food_cooking",
    "Food and Beverage Services": "food_cooking", "Gambling": None, "Genres": "film_tv",
    "Gifts and Holiday Items": None, "Green/Eco": "nature_outdoors",
    "Health and Medical Services": "health_wellness", "Healthy Living": "health_wellness",
    "Hobbies & Interests": "diy_crafts", "Holidays": None, "Home & Garden": "diy_crafts",
    "Home and Garden Services": "diy_crafts", "Law": "news_politics", "Legal Services": "news_politics",
    "Media": "film_tv", "Medical Health": "health_wellness", "Metals": "finance_business",
    "Non-Fiat Currency": "finance_business", "Non-Profits": None,
    "Personal Celebrations & Life Events": None, "Personal Finance": "finance_business",
    "Personal/Consumer Telecom": "tech", "Pet Ownership": "pets_animals", "Pets": "pets_animals",
    "Pharmaceuticals": "health_wellness", "Politics": "news_politics", "Pop Culture": "film_tv",
    "Real Estate": "finance_business", "Religion & Spirituality": None, "Religion and Spirituality": None,
    "Retail": None, "Science": "science", "Sensitive Topics": "news_politics",
    "Sexual Health": "health_wellness", "Shopping": None, "Sporting Goods": "sports", "Sports": "sports",
    "Style & Fashion": "beauty_fashion", "Technology & Computing": "tech", "Tobacco": None,
    "Travel": "travel", "Travel and Tourism": "travel", "Vehicles": "automotive",
    "Video Gaming": "gaming", "War and Conflicts": "news_politics", "Weapons and Ammunition": "news_politics",
}

OVERRIDES = {
    "Music": "music", "Music Video": "music", "Musical": "music", "Musical Instruments": "music",
    "Music and Video Streaming Services": "music", "Movies": "film_tv", "Television": "film_tv",
    "Comedy": "comedy", "Humor and Satire": "comedy", "Fitness and Exercise": "fitness",
    "Core Gaming": "gaming", "Casual Games": "gaming", "Games and Puzzles": "gaming",
    "News and Analysis": "news_politics", "Arts and Crafts": "art_design",
    "Nature": "nature_outdoors", "Birdwatching": "nature_outdoors", "Environment": "nature_outdoors",
}

RETENTION_WINDOW_DAYS = MAX_AGE_DAYS
HALF_LIFE_DAYS = RETENTION_WINDOW_DAYS / 4.0

REPO = Path(__file__).resolve().parent.parent.parent
GRAPH_PATH = REPO / "data" / "graph" / "trend_graph.pkl"
OUT_PATH = REPO / "data" / "trends" / "trend_snapshot.json"



