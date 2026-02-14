// =======================
// Core domain enums
// =======================

export type CallSentiment = "positive" | "neutral" | "negative"
export type CallUrgency = "low" | "medium" | "high"
export type CallOutcome = "resolved" | "unresolved"
export type AgentBehavior = "polite" | "neutral" | "rude" | "unknown"

// =======================
// History / DB records
// =======================

export type HistoryCall = {
  id: number
  transcript: string
  sentiment: CallSentiment
  issue_category: string        // comma-separated string from DB
  urgency: CallUrgency
  agent_behavior: AgentBehavior
  call_outcome: CallOutcome
  created_at: string            // ISO timestamp (UTC)
}

export type FetchCallsResponse = HistoryCall[]

// =======================
// Analyze (LLM output)
// =======================

export type CallInsights = {
  sentiment: CallSentiment
  urgency: CallUrgency
  call_outcome: CallOutcome
  issue_category?: string
  agent_behavior?: AgentBehavior
}

export type AnalysisResultData = {
  transcript: string
  insights: CallInsights
  created_at: string  // Required - ISO timestamp (UTC)
  id?: number         // Optional - present if saved to DB
}

// =======================
// Analyze API responses
// =======================

export type AnalyzeApiSuccessResponse = {
  status: "success"
  analysis: {
    transcript: string
    insights: CallInsights
    created_at?: string
    id?: number
  }
}

export type AnalyzeApiErrorResponse = {
  status: "failed" | "duplicate"
  reason?: string
  message?: string
}

export type AnalyzeApiResponse =
  | AnalyzeApiSuccessResponse
  | AnalyzeApiErrorResponse

// =======================
// Summary (for indicators)
// =======================

export type SummaryResponse = {
  sentiment_distribution: Record<string, number>
  urgency_distribution: Record<string, number>
  call_outcome_distribution: Record<string, number>
}