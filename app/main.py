import os
import uuid
import shutil
import json
import re
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import AI pipeline + DB functions
from app.pipeline import transcribe_audio, analyze_transcript
from app.database import init_db, insert_call, fetch_all_calls, fetch_summary

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
UPLOAD_DIR = os.path.join("data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# Startup DB
# -----------------------------
@app.on_event("startup")
def startup_event():
    init_db()


# -----------------------------
# Health check
# -----------------------------
@app.get("/")
def root():
    return {"message": "Customer Support Call Analytics API is running"}


# -----------------------------
# Analyze Audio Endpoint
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

        # Run pipeline in a thread
        transcript, insights = await asyncio.to_thread(run_pipeline_safe, file_path)

        # Save results to DB
        insert_call(
            audio_path=file_path,
            transcript=transcript,
            insights=insights
        )

        return {
            "transcript": transcript,
            "insights": insights
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
            "created_at": row[8]
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
    """Run transcription + LLM analysis safely"""
    transcript = transcribe_audio(file_path)
    insights = analyze_transcript(transcript)  # this returns dict already
    return transcript, insights



def analyze_transcript_safe(transcript: str):
    """
    Calls your LLM/AI analysis and safely parses JSON, even if extra text is returned.
    """
    raw_output = analyze_transcript(transcript)  # Your existing LLM function

    # Try to extract first JSON object
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if not match:
        # Fallback to defaults
        return {
            "sentiment": "neutral",
            "issue_category": "other",
            "urgency": "low",
            "agent_behavior": "neutral",
            "call_outcome": "unresolved"
        }

    candidate = match.group(0)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        try:
            import json5
            return json5.loads(candidate)
        except Exception:
            # Absolute fallback
            return {
                "sentiment": "neutral",
                "issue_category": "other",
                "urgency": "low",
                "agent_behavior": "neutral",
                "call_outcome": "unresolved"
            }
