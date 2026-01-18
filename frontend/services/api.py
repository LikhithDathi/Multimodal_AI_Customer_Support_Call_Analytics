import requests
from config import API_BASE

def analyze_call(file):
    return requests.post(
        f"{API_BASE}/analyze-call",
        files={"file": file}
    )

def get_calls():
    return requests.get(f"{API_BASE}/calls")


