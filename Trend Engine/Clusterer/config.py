"""Configuration and tunable parameters for clustering."""

# I/O files
INPUT_FILE = "Normalized_data.json"
OUTPUT_FILE = "clustered.json"

# Data filtering
EXCLUDED_SOURCES = []

KEYWORD_BLOCKLIST = {
    # Platform & social media noise
    "youtube", "letra", "video", "channel", "watch", "subscribe",
    "www", "com", "https", "http", "twitter", "instagram",
    "official", "lyrics", "music", "song", "audio", "ft", "feat",
    # Purely temporal/generic
    "today", "latest", "update", "big", "news", "new",
    "time", "day", "live"
}

# Text builder parameters
MIN_KEYWORD_SCORE = 0.3
MAX_KEYWORDS_PER_ITEM = 10

# UMAP parameters
UMAP_N_COMPONENTS = 8
UMAP_N_NEIGHBORS = 15
UMAP_MIN_DIST = 0.0
UMAP_METRIC = "cosine"
UMAP_RANDOM_STATE = 42

# HDBSCAN parameters
HDBSCAN_MIN_CLUSTER_SIZE = 5
HDBSCAN_MIN_SAMPLES = 2
HDBSCAN_METRIC = "euclidean"
HDBSCAN_CLUSTER_SELECTION_METHOD = "eom"
HDBSCAN_CLUSTER_SELECTION_EPSILON = 0.0

# Clustering quality thresholds
MIN_CONFIDENCE_PROB = 0.25

# Labeling parameters
TOP_TERMS_FOR_LABEL = 3

# SentenceTransformer model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
