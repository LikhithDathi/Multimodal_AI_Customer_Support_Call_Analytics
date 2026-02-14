from pydantic import BaseModel
from typing import Literal, List


class CallAnalysis(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    issue_category: List[Literal["billing", "delivery", "refund", "technical", "other"]]
    urgency: Literal["low", "medium", "high"]
    agent_behavior: Literal["polite", "neutral", "rude", "unknown"]
    call_outcome: Literal["resolved", "unresolved"]
