import os
import uuid
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import AI pipeline + DB functions
from app.pipeline import (
    transcribe_audio,
    analyze_transcript,
    analyze_input,
)
from app.database import (
    init_db,
    insert_call,
    fetch_all_calls,
    fetch_summary,
)

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="Customer Support Call Analytics API")

# Allow CORS for all origins (use "*" in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Upload Folder
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# Startup DB
# -----------------------------
@app.on_event("startup")
def startup_event():
    init_db()

# -----------------------------
# Request Schema
# -----------------------------
class AnalyzeRequest(BaseModel):
    input_type: str  # "call" or "message"
    content: str     # audio file path OR message text

# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def root():
    return {"message": "Customer Support Call Analytics API is running"}

# -----------------------------
# Analyze Audio Upload (CALL)
# -----------------------------
@app.post("/analyze-call")
async def analyze_call(file: UploadFile = File(...)):
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{safe_filename}")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Run pipeline in background thread
        transcript, insights = await asyncio.to_thread(
            run_pipeline_safe,
            file_path
        )

        # Save results to DB
        insert_call(
            audio_path=file_path,
            transcript=transcript,
            insights=insights,
        )

        return {
            "transcript": transcript,
            "insights": insights,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------
# Analyze Call OR Message (Unified)
# -----------------------------
@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    """
    Handles:
    - Calls (audio file path)
    - Messages (plain text)
    """
    return analyze_input(
        payload.content,
        input_type=payload.input_type,
    )

# -----------------------------
# Get All Calls
# -----------------------------
@app.get("/calls")
def get_all_calls():
    rows = fetch_all_calls()
    return [
        {
            "id": row[0],
            "audio_path": row[1],
            "transcript": row[2],
            "sentiment": row[3],
            "issue_category": row[4],
            "urgency": row[5],
            "agent_behavior": row[6],
            "call_outcome": row[7],
            "created_at": row[8],
        }
        for row in rows
    ]

# -----------------------------
# Get Summary
# -----------------------------
@app.get("/calls/summary")
def get_summary():
    return fetch_summary()

# -----------------------------
# Helpers
# -----------------------------
def run_pipeline_safe(file_path: str):
    """
    Run transcription + LLM analysis safely.
    """
    transcript = transcribe_audio(file_path)
    insights = analyze_transcript(transcript)
    return transcript, insights
