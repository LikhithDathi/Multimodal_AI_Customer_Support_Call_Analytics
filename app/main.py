import os
import uuid
import asyncio
import hashlib
from app.config import Config
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import analyze_input
from app.database import (
    init_db,
    insert_call,
    fetch_all_calls,
    fetch_summary,
    call_exists,
    delete_call_by_id
)

# Import ONLY the one function that exists
from app.analytics import calculate_operational_risk

# -----------------------------
# App setup
# -----------------------------
app = FastAPI(title="Customer Support Call Analytics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # development
        "https://your-frontend.vercel.app",  # production - CHANGE THIS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, Config.UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = Config.MAX_FILE_SIZE

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac"}
ALLOWED_MIME_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/mp4",
    "audio/m4a", "audio/x-m4a", "audio/aac", "audio/ogg", "audio/flac", "audio/webm"
}

# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
def startup():
    init_db()

# -----------------------------
# Helpers
# -----------------------------
def compute_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

# -----------------------------
# Health
# -----------------------------
@app.get("/")
def root():
    return {"message": "Customer Support Call Analytics API is running"}

# -----------------------------
# Analyze Call (AUDIO)
# -----------------------------
@app.post("/analyze-call")
async def analyze_call(file: UploadFile = File(...)):
    file_path = None

    try:
        filename = file.filename.lower()
        ext = os.path.splitext(filename)[1]

        if ext not in ALLOWED_EXTENSIONS:
            return {
                "status": "failed",
                "reason": "invalid_file_type",
                "allowed_extensions": sorted(ALLOWED_EXTENSIONS),
            }

        file_bytes = await file.read()

        if not file_bytes:
            return {"status": "failed", "reason": "empty_file"}

        if len(file_bytes) > MAX_FILE_SIZE:
            return {
                "status": "failed",
                "reason": "file_too_large",
                "max_size_mb": 50,
            }

        file_hash = compute_file_hash(file_bytes)
        existing = call_exists(file_hash)

        if existing:
            return {
                "status": "duplicate",
                "message": "This call has already been analyzed",
                "existing_call_id": existing["id"],
            }

        safe_name = os.path.basename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{safe_name}")

        with open(file_path, "wb") as f:
            f.write(file_bytes)

        analysis = await asyncio.to_thread(analyze_input, file_path, "call")

        transcript = analysis.get("transcript", "")
        insights = analysis.get("insights", analysis)

        if not transcript.strip():
            return {
                "status": "failed",
                "reason": "transcription_failed"
            }

        issue_category = insights.get("issue_category", ["other"])
        if isinstance(issue_category, list):
            insights["issue_category"] = ",".join(issue_category)
        elif isinstance(issue_category, str):
            insights["issue_category"] = issue_category
        else:
            insights["issue_category"] = "other"

        insert_result = insert_call(
            file_hash=file_hash,
            transcript=transcript,
            insights=insights,
        )

        if insert_result.get("inserted"):
            return {
                "status": "success",
                "analysis": {
                    "transcript": transcript,
                    "insights": insights,
                },
            }

        if insert_result.get("reason") == "duplicate":
            return {
                "status": "duplicate",
                "message": "This call has already been analyzed",
                "existing_call_id": existing["id"] if existing else None,
            }

        return {
            "status": "failed",
            "reason": insert_result.get("reason"),
            "error": insert_result.get("error"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

# -----------------------------
# Unified Analyze (TEXT)
# -----------------------------
class AnalyzeRequest(BaseModel):
    input_type: str
    content: str

@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    return analyze_input(payload.content, payload.input_type)

# -----------------------------
# Fetch calls
# -----------------------------
@app.get("/calls")
def get_calls():
    return fetch_all_calls()

# -----------------------------
# Delete
# -----------------------------
@app.delete("/calls/{call_id}")
def delete_call(call_id: int):
    deleted = delete_call_by_id(call_id)

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Call not found")

    return {
        "status": "deleted",
        "id": call_id
    }

# -----------------------------
# Summary
# -----------------------------
@app.get("/calls/summary")
def get_summary():
    return fetch_summary()

# =======================
# Analytics Endpoints - SINGLE ML FEATURE
# =======================

@app.get("/analytics/operational-risk")
def operational_risk():
    """ML-powered operational risk score"""
    return calculate_operational_risk()