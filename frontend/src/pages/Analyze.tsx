import { useEffect, useState } from "react"
import { analyzeCall } from "../api/calls"
import api from "../api/api"
import { formatCallDate, getRelativeTimeString } from "../utils/date"
import type {
  AnalysisResultData,
  SummaryResponse,
} from "../types/analysis"
import "./Analyze.css"

const ALLOWED_EXTENSIONS = [
  ".wav",
  ".mp3",
  ".m4a",
  ".aac",
  ".ogg",
  ".flac",
]

export default function Analyze() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AnalysisResultData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [needsAttention, setNeedsAttention] = useState(false)

  // Fetch summary for risk indicator
  useEffect(() => {
    api.get<SummaryResponse>("/calls/summary")
      .then(res => {
        const summary = res.data
        const attention =
          (summary.urgency_distribution?.high ?? 0) > 0 ||
          (summary.call_outcome_distribution?.unresolved ?? 0) > 0
        setNeedsAttention(attention)
      })
      .catch(() => {})
  }, [result])

  const handleAnalyze = async () => {
    if (!file) return

    setLoading(true)
    setError(null)
    setResult(null)

    // Store the timestamp when analysis STARTS
    const startTime = new Date().toISOString()

    try {
      const response = await analyzeCall(file)

      if (response.status === "success") {
        // Use the timestamp from when analysis started
        // This is consistent and doesn't require fetching from DB
        setResult({
          transcript: response.analysis.transcript,
          insights: response.analysis.insights,
          created_at: startTime, // Use the start time, not current time
        })
      } else if (response.status === "duplicate") {
        setError("This call has already been analyzed. Please check history.")
      } else {
        setError("Analysis failed. Please try again.")
      }
    } catch (error) {
      console.error("Analysis error:", error)
      setError("Network or server error occurred. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="analyze-page">
      
      {/* SINGLE UNIFIED CONTAINER */}
      <div className="analyze-container">

        {/* TITLE */}
        <h1 className="analyze-title">
          Analyze Customer Support Call
        </h1>
        <p className="analyze-subtitle">
          Upload an audio file to extract transcript and insights.
        </p>

        {/* RISK INDICATOR WITH REVIEW BUTTON */}
        <div className={`risk-section ${needsAttention ? "warn" : "ok"}`}>
          <div className="risk-message">
            {needsAttention ? (
              <>⚠️ <strong>Some calls may still require follow-up.</strong></>
            ) : (
              <>✅ <strong>No pending follow-ups detected.</strong></>
            )}
          </div>
          {needsAttention && (
            <a href="/history?status=unresolved&urgency=high" className="risk-review-btn">
              Review Calls
            </a>
          )}
        </div>

        {/* UPLOAD SECTION */}
        <div className="upload-section">
          <div className="upload-row">
            <input
              type="file"
              accept={ALLOWED_EXTENSIONS.join(",")}
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              disabled={loading}
              placeholder="Choose audio file..."
            />
            <button
              className="analyze-btn"
              onClick={handleAnalyze}
              disabled={!file || loading}
            >
              {loading ? "⏳ Analyzing..." : "🔍 Analyze Call"}
            </button>
          </div>
          {file && !loading && (
            <div className="file-info">
              <span> Selected:</span> {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
            </div>
          )}
        </div>

        {/* INFO GRID - Hides when loading or result exists */}
        {!loading && !result && !error && (
          <>
            <div className="info-grid">
              <div className="info-column">
                <h4>Allowed file types (Max 50MB)</h4>
                <ul>
                  <li>WAV (recommended)</li>
                  <li>MP3 / M4A</li>
                  <li>AAC, OGG, FLAC</li>
                </ul>
              </div>
              <div className="info-column">
                <h4>Best results when</h4>
                <ul>
                  <li>Clear audio, minimal noise</li>
                  <li>Single customer-agent conversation</li>
                  <li>Natural conversation flow</li>
                </ul>
              </div>
              <div className="info-column">
                <h4>Important notes</h4>
                <ul>
                  <li>Fully automated analysis</li>
                  <li>Urgency & outcome are inferred</li>
                  <li>Manual review recommended</li>
                </ul>
              </div>
            </div>

            <div className="disclaimer">
              This system uses AI-based analysis and may occasionally produce incorrect or incomplete results. Always review critical calls manually.
            </div>
          </>
        )}

        {/* LOADING STATE */}
        {loading && (
          <div className="status-section loading">
            <div className="loading-content">
              <span className="loading-spinner">⏳</span>
              <div>
                <p className="status-title">Analyzing your call...</p>
                <p className="status-subtitle">This may take a few seconds. Please don't close the window.</p>
              </div>
            </div>
          </div>
        )}

        {/* ERROR STATE */}
        {error && (
          <div className="status-section error">
            <div className="error-content">
              <span className="error-icon">✕</span>
              <div>
                <p className="status-title">Analysis failed</p>
                <p className="status-subtitle">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* ANALYSIS RESULT - Using startTime timestamp */}
        {result && (
          <div className="result-section">
            
            {/* Tags Row */}
            <div className="result-tags">
              <span className={`tag urgency-${result.insights.urgency}`}>
                {result.insights.urgency.toUpperCase()} URGENCY
              </span>
              <span className={`tag sentiment-${result.insights.sentiment}`}>
                {result.insights.sentiment.toUpperCase()}
              </span>
              {result.insights.call_outcome === "unresolved" && (
                <span className="tag warn">
                  FOLLOW-UP NEEDED
                </span>
              )}
            </div>

            {/* Insights Cards Grid */}
            <div className="insights-grid">
              <div className="insight-card">
                <div className="insight-label">Issue Category</div>
                <div className="insight-value category">
                  {result.insights.issue_category || "General Inquiry"}
                </div>
              </div>
              
              <div className="insight-card">
                <div className="insight-label">Call Outcome</div>
                <div className="insight-value">
                  {result.insights.call_outcome === "resolved" 
                    ? "✅ Resolved" 
                    : "⚠️ Unresolved"}
                </div>
              </div>

              {result.insights.agent_behavior && result.insights.agent_behavior !== "unknown" && (
                <div className="insight-card">
                  <div className="insight-label">Agent Behavior</div>
                  <div className="insight-value">
                    {result.insights.agent_behavior.charAt(0).toUpperCase() + 
                     result.insights.agent_behavior.slice(1)}
                  </div>
                </div>
              )}

              <div className="insight-card">
                <div className="insight-label">Analysis Time</div>
                <div className="insight-value">
                  {formatCallDate(result.created_at)}
                </div>
              </div>
            </div>


            {/* Transcript Section */}
            <details className="transcript-details">
              <summary>
                <span> View Full Transcript</span>
                <span className="transcript-length">
                  {result.transcript.length.toLocaleString()} characters • {getRelativeTimeString(result.created_at)}
                </span>
              </summary>
              <div className="transcript-content">
                {result.transcript}
              </div>
            </details>
          </div>
        )}

      </div> {/* End analyze-container */}
    </div>
  )
}