import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import type { HistoryCall } from "../types/analysis"
import { formatHistoryDate, parseFilterDate } from "../utils/date"
import "./History.css"

// Helper function to truncate at word boundaries
function truncateAtWord(text: string, limit: number): string {
  if (text.length <= limit) return text
  const slice = text.slice(0, limit)
  const lastSpace = slice.lastIndexOf(" ")
  return lastSpace > 0 ? slice.slice(0, lastSpace) : slice
}

export default function History() {
  const [calls, setCalls] = useState<HistoryCall[]>([])
  const [params, setParams] = useSearchParams()
  const [sortOrder, setSortOrder] = useState<"newest" | "oldest">("newest")
  const [expandedCardId, setExpandedCardId] = useState<number | null>(null)

  useEffect(() => {
    async function loadCalls() {
      try {
        const res = await fetch("http://localhost:8000/calls")
        const data: unknown = await res.json()

        if (Array.isArray(data)) {
          setCalls(data as HistoryCall[])
        } else {
          throw new Error("Invalid response format")
        }
      } catch (err) {
        console.error("Failed to load calls", err)
      }
    }

    loadCalls()
  }, [])

  const splitCategories = (categoryString: string): string[] => {
    if (!categoryString) return []
    return categoryString.split(',').map(cat => cat.trim()).filter(cat => cat.length > 0)
  }

  const filtered = calls.filter(call => {
    const status = params.get("status")
    const urgency = params.get("urgency")
    const sentiment = params.get("sentiment")
    const category = params.get("category")
    const from = params.get("from")
    const to = params.get("to")

    if (status && call.call_outcome !== status) return false
    if (urgency && call.urgency !== urgency) return false
    if (sentiment && call.sentiment !== sentiment) return false
    if (category && !call.issue_category.toLowerCase().includes(category.toLowerCase())) return false

    // Use UTC dates for filtering
    const callDate = new Date(call.created_at).getTime()
    if (from) {
      const fromDate = parseFilterDate(from).getTime()
      if (callDate < fromDate) return false
    }
    if (to) {
      const toDate = parseFilterDate(to).getTime()
      // Add 24 hours to include the entire end day
      const toDateEnd = toDate + (24 * 60 * 60 * 1000 - 1)
      if (callDate > toDateEnd) return false
    }

    return true
  })

  const sortedCalls = [...filtered].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime()
    const dateB = new Date(b.created_at).getTime()
    
    return sortOrder === "newest" 
      ? dateB - dateA
      : dateA - dateB
  })

  function updateParam(key: string, value: string) {
    const next = new URLSearchParams(params)
    if (value) {
      next.set(key, value)
    } else {
      next.delete(key)
    }
    setParams(next)
  }

  function removeParam(key: string) {
    const next = new URLSearchParams(params)
    next.delete(key)
    setParams(next)
  }

  function resetFilters() {
    setParams({})
  }

  function toggleSortOrder() {
    setSortOrder(prev => prev === "newest" ? "oldest" : "newest")
  }

  function toggleTranscript(callId: number) {
    setExpandedCardId(prev => prev === callId ? null : callId)
  }

  return (
    <div className="history-page">
      <div className="page-header">
        <h1>Call History</h1>
        <div className="sort-control">
          <button 
            className={`sort-btn ${sortOrder === "newest" ? "active" : ""}`}
            onClick={toggleSortOrder}
          >
            <span className="sort-icon">
              {sortOrder === "newest" ? "↓" : "↑"}
            </span>
            {sortOrder === "newest" ? "Newest First" : "Oldest First"}
          </button>
          <span className="results-count">
            {sortedCalls.length} {sortedCalls.length === 1 ? 'call' : 'calls'}
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <label>Status</label>
          <select 
            value={params.get("status") ?? ""} 
            onChange={e => updateParam("status", e.target.value)}
          >
            <option value="">All Status</option>
            <option value="unresolved">Unresolved</option>
            <option value="resolved">Resolved</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Urgency</label>
          <select 
            value={params.get("urgency") ?? ""} 
            onChange={e => updateParam("urgency", e.target.value)}
          >
            <option value="">All Urgency</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Sentiment</label>
          <select 
            value={params.get("sentiment") ?? ""} 
            onChange={e => updateParam("sentiment", e.target.value)}
          >
            <option value="">All Sentiment</option>
            <option value="negative">Negative</option>
            <option value="neutral">Neutral</option>
            <option value="positive">Positive</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Category</label>
          <select 
            value={params.get("category") ?? ""} 
            onChange={e => updateParam("category", e.target.value)}
          >
            <option value="">All Categories</option>
            <option value="billing">Billing</option>
            <option value="delivery">Delivery</option>
            <option value="refund">Refund</option>
            <option value="technical">Technical</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="filter-group date-group">
          <label>From Date</label>
          <input 
            type="date" 
            value={params.get("from") ?? ""} 
            onChange={e => updateParam("from", e.target.value)} 
          />
        </div>

        <div className="filter-group date-group">
          <label>To Date</label>
          <input 
            type="date" 
            value={params.get("to") ?? ""} 
            onChange={e => updateParam("to", e.target.value)} 
          />
        </div>

        <div className="filter-actions">
          <button className="reset-btn" onClick={resetFilters}>
            Clear All Filters
          </button>
        </div>
      </div>

      {/* Active filters */}
      {params.size > 0 && (
        <div className="active-filters">
          {[...params.entries()].map(([key, value]) => (
            <span key={key} className="filter-chip" onClick={() => removeParam(key)}>
              <span className="filter-chip-key">{key}:</span>
              <span className="filter-chip-value">{value}</span>
              <span className="filter-chip-remove">×</span>
            </span>
          ))}
          <button className="clear-all-btn" onClick={resetFilters}>
            Clear All
          </button>
        </div>
      )}

      {/* Results */}
      <div className="history-list">
        {sortedCalls.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📞</div>
            <h3>No calls found</h3>
            <p>No calls match the selected filters. Try adjusting your search criteria.</p>
            {params.size > 0 && (
              <button className="empty-reset-btn" onClick={resetFilters}>
                Clear All Filters
              </button>
            )}
          </div>
        )}

        {sortedCalls.map(call => {
          const isExpanded = expandedCardId === call.id
          const shouldTruncate = call.transcript && call.transcript.length > 200
          
          const displayText = call.transcript 
            ? (isExpanded 
                ? call.transcript 
                : (shouldTruncate 
                    ? truncateAtWord(call.transcript, 200) + "..." 
                    : call.transcript))
            : "No transcript available"
          
          const categories = splitCategories(call.issue_category)
          
          return (
            <div 
              key={call.id} 
              className={`call-card ${isExpanded ? 'expanded' : ''}`}
            >
              <div className="card-header">
                <div className="call-id">
                  <span className="call-icon">📞</span>
                  <div className="call-info">
                    <div className="call-number">Call #{call.id}</div>
                    <div className="call-date">
                      {/* FIXED: Using UTC-based formatter */}
                      {formatHistoryDate(call.created_at)}
                    </div>
                  </div>
                </div>
                <div className={`status-badge ${call.call_outcome}`}>
                  <span className="status-dot"></span>
                  {call.call_outcome.charAt(0).toUpperCase() + call.call_outcome.slice(1)}
                </div>
              </div>

              <div className="card-metadata">
                <div className="metadata-item">
                  <span className="metadata-label">Category</span>
                  <div className="category-tags">
                    {categories.length > 0 ? (
                      categories.map((cat, index) => (
                        <span key={index} className="category-tag">
                          {cat}
                        </span>
                      ))
                    ) : (
                      <span className="category-tag">Unknown</span>
                    )}
                  </div>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Sentiment</span>
                  <span className={`metadata-value sentiment-tag sentiment-${call.sentiment}`}>
                    {call.sentiment}
                  </span>
                </div>
                <div className="metadata-item">
                  <span className="metadata-label">Urgency</span>
                  <span className={`metadata-value urgency-tag urgency-${call.urgency}`}>
                    {call.urgency}
                  </span>
                </div>
              </div>

              {/* Transcript section */}
              {call.transcript && (
                <div className="transcript-section">
                  <div className="transcript-header">
                    <span className="transcript-label">Transcript</span>
                    {shouldTruncate && (
                      <button 
                        className="transcript-toggle"
                        onClick={() => toggleTranscript(call.id)}
                      >
                        {isExpanded ? "Show Less" : "Read More"}
                        <span className="toggle-icon">{isExpanded ? "↑" : "↓"}</span>
                      </button>
                    )}
                  </div>
                  <div className="transcript-content">
                    {displayText}
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}