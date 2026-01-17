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
# Unified Input Analysis (Call / Message)
# -----------------------------
def analyze_input(content: str, input_type: str = "call"):
    """
    Analyze either a call (audio file path) or a text message.
    """
    if input_type == "call":
        transcript = transcribe_audio(content)
    else:
        transcript = content

    return analyze_transcript(transcript)


# -----------------------------
# NEW: Deterministic Outcome Logic (SMALL ADDITION)
# -----------------------------
def derive_call_outcome(data: dict) -> str:
    """
    Derive call outcome from evidence to avoid politeness bias.
    """
    if (
        data.get("resolution_action_taken") == "yes"
        and data.get("customer_confirmation") == "yes"
        and data.get("pending_followup") == "no"
    ):
        return "resolved"

    return "unresolved"


# -----------------------------
# LLM Analysis (Improved, CORE KEPT)
# -----------------------------
def analyze_transcript(transcript: str) -> dict:
    """
    Analyze transcript using LLM with few-shot examples and semantic hints.
    Returns a dict compatible with CallAnalysis model.
    """

    prompt = f"""
You are a system that outputs structured JSON. ONLY return JSON, no explanations.

Rules:
- sentiment: positive, neutral, negative
- issue_category: billing, delivery, refund, technical, other
- urgency: low, medium, high
- agent_behavior: polite, neutral, rude

Evidence fields:
- resolution_action_taken: yes, no, unclear
- customer_confirmation: yes, no, unclear
- pending_followup: yes, no

IMPORTANT:
- Do NOT infer resolution from politeness.
- Extract factual signals only.

Examples:

Transcript: "Thank you for helping me, I really appreciate it!"
JSON: {{
  "sentiment": "positive",
  "issue_category": "other",
  "urgency": "low",
  "agent_behavior": "polite",
  "resolution_action_taken": "unclear",
  "customer_confirmation": "unclear",
  "pending_followup": "no"
}}

Transcript: "I was charged twice for my order."
JSON: {{
  "sentiment": "negative",
  "issue_category": "billing",
  "urgency": "high",
  "agent_behavior": "neutral",
  "resolution_action_taken": "no",
  "customer_confirmation": "no",
  "pending_followup": "yes"
}}

Transcript: "The app crashes when I log in."
JSON: {{
  "sentiment": "negative",
  "issue_category": "technical",
  "urgency": "high",
  "agent_behavior": "neutral",
  "resolution_action_taken": "no",
  "customer_confirmation": "no",
  "pending_followup": "yes"
}}

Transcript: "I reset your account and it works now. Yes, it is fixed."
JSON: {{
  "sentiment": "positive",
  "issue_category": "technical",
  "urgency": "low",
  "agent_behavior": "polite",
  "resolution_action_taken": "yes",
  "customer_confirmation": "yes",
  "pending_followup": "no"
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
        "resolution_action_taken": "unclear",
        "customer_confirmation": "unclear",
        "pending_followup": "no",
    }

    if not parsed:
        retry_prompt = f"""
ONLY return valid JSON. No explanations.
If unsure, mark values as "unclear".
Do NOT infer resolution from politeness.

Fallback:
{json.dumps(fallback)}

Transcript:
\"\"\"{transcript}\"\"\"
"""
        retry_raw = _call_llm(retry_prompt)
        parsed = _extract_json(retry_raw)

    analysis = parsed or fallback

    # ✅ NEW: derive outcome instead of trusting LLM
    analysis["call_outcome"] = derive_call_outcome(analysis)

    # Ensure it matches CallAnalysis model
    try:
        return CallAnalysis(**analysis).dict()
    except Exception:
        analysis["call_outcome"] = "unresolved"
        return analysis


# -----------------------------
# Helpers (UNCHANGED)
# -----------------------------
def _call_llm(prompt: str) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"]


def _extract_json(text: str) -> dict | None:
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
