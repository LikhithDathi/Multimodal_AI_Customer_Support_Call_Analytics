// =======================
// Domain enums / unions
// =======================

export type CallSentiment = "positive" | "neutral" | "negative"
export type CallUrgency = "low" | "medium" | "high"
export type CallOutcome = "resolved" | "unresolved"
export type AgentBehavior = "polite" | "neutral" | "rude" | "unknown"

// =======================
// History (DB record)
// =======================

/**
 * Represents a single call record
 * as returned from GET /calls
 */
export type HistoryCall = {
  id: number
  transcript: string
  sentiment: CallSentiment
  issue_category: string        // comma-separated string from DB
  urgency: CallUrgency
  agent_behavior: AgentBehavior
  call_outcome: CallOutcome
  created_at: string            // ISO timestamp (SQLite)
}

// =======================
// API responses
// =======================

/**
 * GET /calls
 */
export type FetchCallsResponse = HistoryCall[]

/**
 * DELETE /calls/:id
 */
export type DeleteCallResponse = {
  status: "deleted"
  id: number
}

