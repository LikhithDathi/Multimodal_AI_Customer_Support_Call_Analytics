from pydantic import BaseModel
from typing import Literal


class CallAnalysis(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    issue_category: Literal["billing", "delivery", "refund", "technical", "other"]
    urgency: Literal["low", "medium", "high"]
    agent_behavior: Literal["polite", "neutral", "rude"]
    call_outcome: Literal["resolved", "unresolved"]
