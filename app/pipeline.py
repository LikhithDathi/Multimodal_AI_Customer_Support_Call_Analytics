import whisper
from app.models import CallAnalysis 
import ollama
import json
import json5

OLLAMA_MODEL = "phi3"

# Load Whisper once
whisper_model = whisper.load_model("base")


# -----------------------------
# Audio Transcription
# -----------------------------
def transcribe_audio(audio_path: str) -> str:
    try:
        result = whisper_model.transcribe(audio_path)
        return result.get("text", "").strip()
    except Exception:
        return ""


# -----------------------------
# LLM Analysis (Improved)
# -----------------------------
def analyze_transcript(transcript: str) -> dict:
    """
    Analyze transcript using LLM with few-shot examples and semantic hints.
    Returns a dict compatible with CallAnalysis model.
    """
    # Few-shot prompt for both sentiment and issue_category
    prompt = f"""
You are a system that outputs structured JSON. ONLY return JSON, no explanations.

Rules:
- sentiment: positive, neutral, negative
    - positive: happy, thankful, satisfied, polite
    - neutral: factual, routine, no strong emotion
    - negative: frustrated, angry, dissatisfied
- issue_category: billing, delivery, refund, technical, other
- urgency: low, medium, high
- agent_behavior: polite, neutral, rude
- call_outcome: resolved, unresolved

Choose the category that best matches the transcript. Use 'other' ONLY if it does not fit any other category.

Examples:

Transcript: "Thank you for helping me, I really appreciate it!"
JSON: {{
  "sentiment": "positive",
  "issue_category": "other",
  "urgency": "low",
  "agent_behavior": "polite",
  "call_outcome": "resolved"
}}

Transcript: "I was charged twice for my order."
JSON: {{
  "sentiment": "negative",
  "issue_category": "billing",
  "urgency": "high",
  "agent_behavior": "neutral",
  "call_outcome": "unresolved"
}}

Transcript: "My package hasn't arrived yet."
JSON: {{
  "sentiment": "negative",
  "issue_category": "delivery",
  "urgency": "high",
  "agent_behavior": "neutral",
  "call_outcome": "unresolved"
}}

Transcript: "I want a refund for the defective product."
JSON: {{
  "sentiment": "negative",
  "issue_category": "refund",
  "urgency": "high",
  "agent_behavior": "neutral",
  "call_outcome": "unresolved"
}}

Transcript: "The app crashes when I log in."
JSON: {{
  "sentiment": "negative",
  "issue_category": "technical",
  "urgency": "high",
  "agent_behavior": "neutral",
  "call_outcome": "unresolved"
}}

Transcript: "I want to transfer money between my accounts."
JSON: {{
  "sentiment": "neutral",
  "issue_category": "other",
  "urgency": "low",
  "agent_behavior": "polite",
  "call_outcome": "resolved"
}}

Now analyze the following transcript and produce ONLY valid JSON:

Transcript:
\"\"\"{transcript}\"\"\"
"""

    raw = _call_llm(prompt)
    parsed = _extract_json(raw)

    # Retry fallback if parsing fails
    fallback = {
        "sentiment": "neutral",
        "issue_category": "other",
        "urgency": "low",
        "agent_behavior": "neutral",
        "call_outcome": "unresolved",
    }

    if not parsed:
        retry_prompt = f"""
ONLY return valid JSON. No explanations.
Use fallback values if uncertain:
{json.dumps(fallback)}

Transcript:
\"\"\"{transcript}\"\"\"
"""
        retry_raw = _call_llm(retry_prompt)
        parsed = _extract_json(retry_raw)

    # Ensure it matches CallAnalysis model
    try:
        return CallAnalysis(**(parsed or fallback)).dict()
    except Exception:
        return fallback


# -----------------------------
# Helpers
# -----------------------------
def _call_llm(prompt: str) -> str:
    """
    Call Ollama LLM with no unsupported kwargs.
    """
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        # Remove temperature, Ollama SDK doesn't support this directly
    )
    return response["message"]["content"]



def _extract_json(text: str) -> dict | None:
    """
    Safely extract JSON object from LLM output.
    Handles extra text or minor formatting issues.
    """
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}") + 1

    if start == -1 or end == -1:
        return None

    candidate = text[start:end]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        try:
            return json5.loads(candidate)
        except Exception:
            return None
