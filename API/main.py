import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .Routers import user_engine, context_engine, simulator, analyse
from .Routers.context_engine import warmup as warmup_context_engine
from . import db

logging.basicConfig(level=logging.INFO, format="%(name)s | %(levelname)s | %(message)s")
logger = logging.getLogger("API")

db.init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    warmup_context_engine()
    logger.info("Content Understanding + tagger models loaded; API ready.")
    yield

app = FastAPI(title="Content Diffusion Simulator API", lifespan=lifespan)
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(user_engine)
app.include_router(context_engine)
app.include_router(simulator)
app.include_router(analyse)

@app.get("/")
def root():
    return {
        "service": "Content Diffusion Simulator API",
        "layers": [
            "Layer 2 - User Engine",
            "Layer 3 - Context Engine",
            "Layer 4 - Simulator",
            "Layer 5 - Analyse",
        ],
    }
