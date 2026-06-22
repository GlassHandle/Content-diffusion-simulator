from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .Routers import user_engine
from . import db

db.init_db()

app = FastAPI(title="Content Diffusion Simulator API")
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

@app.get("/")
def root():
    return {
        "service": "Content Diffusion Simulator API",
        "layers": ["Layer 2 - Creator Intelligence"],
    }
