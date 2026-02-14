from faster_whisper import WhisperModel
import ollama
import json
import json5
from app.models import CallAnalysis

OLLAMA_MODEL = "phi3"

# Load Whisper once
whisper_model = WhisperModel("base", device="cpu", compute_type="float32")


# -----------------------------
# Audio Transcription
# -----------------------------
def transcribe_audio(audio_path: str) -> dict:
    """
    Returns transcription result with status metadata.
    """
    try:
        segments, info = whisper_model.transcribe(audio_path)

        text = " ".join(seg.text for seg in segments).strip()

        if not text:
            return {
                "success": False,
                "text": "",
                "error": "empty_transcript",
                "language": info.language if info else None
            }

        return {
            "success": True,
            "text": text,
            "error": None,
            "language": info.language if info else None
        }

    except Exception as e:
        return {
            "success": False,
            "text": "",
            "error": f"transcription_exception: {str(e)}",
            "language": None
        }



# -----------------------------
# Unified Input Analysis
# -----------------------------
def analyze_input(content: str, input_type: str = "call") -> dict:
    if input_type == "call":
        tx = transcribe_audio(content)

        if not tx["success"]:
            return {
                "status": "failed",
                "stage": "transcription",
                "reason": tx["error"],
                "transcript": "",
                "insights": {}
            }

        transcript = tx["text"]

    else:
        transcript = content.strip()
        if len(transcript) < 5:
            return {
                "status": "failed",
                "stage": "input",
                "reason": "empty_or_invalid_text",
                "transcript": "",
                "insights": {}
            }

    analysis = analyze_transcript(transcript)

    return {
        "status": "success",
        "transcript": transcript,
        "insights": analysis
    }


# -----------------------------
# Deterministic Outcome Logic
# -----------------------------
def derive_call_outcome(data: dict) -> str:
    if (
        data.get("resolution_action_taken") == "yes"
        and data.get("customer_confirmation") == "yes"
        and data.get("pending_followup") == "no"
    ):
        return "resolved"
    return "unresolved"


# -----------------------------
# STRICT LLM ANALYSIS
# -----------------------------
def analyze_transcript(transcript: str) -> dict:
    # 🚨 HARD GUARD: empty or meaningless transcript
    if not transcript or len(transcript.strip()) < 5:
        return {
            "sentiment": "neutral",
            "issue_category": ["other"],
            "urgency": "low",
            "agent_behavior": "unknown",
            "call_outcome": "unresolved",
        }

    prompt = f"""
You are a STRICT classification engine for customer support calls.
You are NOT an assistant.
You do NOT explain.
You ONLY output JSON.

====================
ALLOWED VALUES ONLY
====================

sentiment:
- positive | neutral | negative

issue_category: ARRAY of one or more values
- Allowed values: billing, delivery, refund, technical, other
- Choose ALL categories that apply
- If unsure, use ["other"]

urgency:
- low | medium | high

agent_behavior:
- polite | neutral | rude | unknown

Evidence fields:
- resolution_action_taken: yes | no | unclear
- customer_confirmation: yes | no | unclear
- pending_followup: yes | no

====================
CRITICAL RULES
====================

- Gratitude ≠ resolution
- Apologies ≠ resolution
- Polite language ≠ resolution
- Promises ≠ resolution
- Only mark "yes" if explicitly stated AND confirmed
- If unsure, mark "unclear"
- If a refund is requested, processed, confirmed, discussed, or mentioned at ANY point,
  you MUST include "refund" in issue_category.
- NEVER infer missing facts
- If transcript lacks sufficient information, default safely
- Output INVALID values = FAILURE

====================
FEW-SHOT EXAMPLES
====================

Transcript:
"Thank you for calling, we will look into this and get back to you."
JSON:
{{
  "sentiment": "neutral",
  "issue_category": ["other"],
  "urgency": "medium",
  "agent_behavior": "polite",
  "resolution_action_taken": "no",
  "customer_confirmation": "no",
  "pending_followup": "yes"
}}

Transcript:
"I was charged twice yesterday. You have confirmed the refund to my card."
JSON:
{{
  "sentiment": "neutral",
  "issue_category": ["billing", "refund"],
  "urgency": "medium",
  "agent_behavior": "polite",
  "resolution_action_taken": "yes",
  "customer_confirmation": "yes",
  "pending_followup": "no"
}}


Transcript:
"My package arrived late and I was charged extra."
JSON:
{{
  "sentiment": "negative",
  "issue_category": ["delivery", "billing"],
  "urgency": "medium",
  "agent_behavior": "neutral",
  "resolution_action_taken": "no",
  "customer_confirmation": "no",
  "pending_followup": "yes"
}}

Transcript:
"I'm still facing the issue. You said it would be fixed yesterday."
JSON:
{{
  "sentiment": "negative",
  "issue_category": ["technical"],
  "urgency": "high",
  "agent_behavior": "neutral",
  "resolution_action_taken": "no",
  "customer_confirmation": "no",
  "pending_followup": "yes"
}}

Transcript:
"Yes, it is working now. Thanks for fixing it."
JSON:
{{
  "sentiment": "positive",
  "issue_category": ["technical"],
  "urgency": "low",
  "agent_behavior": "polite",
  "resolution_action_taken": "yes",
  "customer_confirmation": "yes",
  "pending_followup": "no"
}}

Transcript:
"I understand the issue, but I cannot resolve this right now."
JSON:
{{
  "sentiment": "neutral",
  "issue_category": ["other"],
  "urgency": "medium",
  "agent_behavior": "neutral",
  "resolution_action_taken": "no",
  "customer_confirmation": "no",
  "pending_followup": "yes"
}}

====================
TASK
====================

Analyze the following transcript.
Return ONLY valid JSON.
No markdown. No explanation.

Transcript:
\"\"\"{transcript}\"\"\"
"""

    raw = _call_llm(prompt)
    parsed = _extract_json(raw)

    fallback = {
        "sentiment": "neutral",
        "issue_category": ["other"],
        "urgency": "low",
        "agent_behavior": "unknown",
        "resolution_action_taken": "unclear",
        "customer_confirmation": "unclear",
        "pending_followup": "no",
    }

    if not parsed:
        parsed = fallback

    parsed["call_outcome"] = derive_call_outcome(parsed)

    try:
        validated = CallAnalysis(**parsed).dict()
        validated["_llm_status"] = "ok"
        return validated

    except Exception:
        return {
            "sentiment": "neutral",
            "issue_category": ["other"],
            "urgency": "low",
            "agent_behavior": "unknown",
            "call_outcome": "unresolved",
            "_llm_status": "validation_failed"
        }



# -----------------------------
# Helpers
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
