import ollama
import json
import re


prompt = """
You are a system that extracts structured data.
Return ONLY valid JSON.
Do NOT include explanations, comments, or markdown.
Do NOT wrap the output in ```.

The JSON must have exactly these fields:
- sentiment: one of ["positive", "neutral", "negative"]
- issue_type: one of ["billing", "delivery", "refund", "technical", "other"]
- problem_resolved: true or false

Transcript:
"I was charged twice for my order and the agent could not help me. This is very frustrating."
"""

response = ollama.chat(
    model="phi3",
    messages=[{"role": "user", "content": prompt}]
)

raw_output = response["message"]["content"]
print("Raw LLM Output:\n", raw_output)

# Remove markdown fences if present
cleaned = re.sub(r"```json|```", "", raw_output).strip()

print("\nCleaned Output:\n", cleaned)

try:
    parsed = json.loads(cleaned)
    print("\nValidated JSON:\n", parsed)
except json.JSONDecodeError as e:
    print("❌ Invalid JSON:", e)
