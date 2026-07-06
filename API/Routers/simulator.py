import json
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from .. import db

REPO_DIR = Path(__file__).resolve().parent.parent.parent
SIM_DIR = REPO_DIR / "Simulator"
EXE = SIM_DIR / "simulator.exe"
DATA_DIR = REPO_DIR / "data"

router = APIRouter(
    prefix="/simulate",
    tags=["Layer 4 - Simulator"]
)

@router.post("")
def simulate(
    content_id: str = Query(..., min_length=1, description="content_id returned by /context/analyze (also accepts a content file name or username)"),
    user_id: str = Query(..., min_length=1, description="creator user_id analyzed via /user/creator/analyze"),
    runs: int = Query(5000, ge=100, le=20000, description="Monte Carlo runs (>=2000 recommended)"),
    seed: int = Query(42, description="fixed seed -> reproducible forecast"),
):
    if not EXE.exists():
        raise HTTPException(status_code=503, detail="simulator.exe not built — run Simulator/build.bat")

    rec = db.get_content_file(content_id)
    content_arg = rec["path"] if rec and Path(rec["path"]).exists() else content_id

    crec = db.get_latest_creator_file(user_id)
    creator_arg = crec["path"] if crec and Path(crec["path"]).exists() else user_id

    cmd = [str(EXE),
           "--content", content_arg,
           "--creator", creator_arg,
           "--data", str(DATA_DIR),
           "--runs", str(runs),
           "--seed", str(seed)]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=SIM_DIR, timeout=120)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="simulation timed out")

    if proc.returncode != 0:
        lines = (proc.stderr or "").strip().splitlines()
        detail = lines[-1] if lines else "simulator failed"
        raise HTTPException(status_code=404 if "not found" in detail else 500, detail=detail)

    return json.loads(proc.stdout)
