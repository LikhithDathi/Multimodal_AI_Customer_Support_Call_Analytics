import { useEffect, useState } from "react"
import { getOperationalRisk, fetchCalls } from "../api/calls"
import type { HistoryCall } from "../types/analysis"
import type { OperationalRisk } from "../api/calls"
import { 
  PieChart, Pie, Cell,
  Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Line, ComposedChart, Legend
} from 'recharts'
import "./Dashboard.css"

// Professional color palette
const COLORS = {
  success: '#34d399',
  warning: '#fbbf24',
  danger: '#f87171',
  neutral: '#94a3b8',
  primary: '#a78bfa'
}

export default function Analytics() {
  const [riskData, setRiskData] = useState<OperationalRisk | null>(null)
  const [calls, setCalls] = useState<HistoryCall[]>([])
  const [loading, setLoading] = useState(true)
  const [timeframe, setTimeframe] = useState<'7d' | '30d' | 'all'>('7d')

  useEffect(() => {
    async function loadAnalytics() {
      setLoading(true)
      try {
        const [risk, callsData] = await Promise.all([
          getOperationalRisk(),
          fetchCalls()
        ])
        setRiskData(risk)
        setCalls(callsData)
      } catch (error) {
        console.error("Failed to load analytics", error)
      } finally {
        setLoading(false)
      }
    }
    
    loadAnalytics()
  }, [])

  // ========== FILTER CALLS BY TIMEFRAME ==========
  
  const getFilteredCalls = () => {
    if (timeframe === 'all') return calls
    
    const now = new Date()
    const cutoff = new Date()
    
    if (timeframe === '7d') {
      cutoff.setDate(now.getDate() - 7)
    } else if (timeframe === '30d') {
      cutoff.setDate(now.getDate() - 30)
    }
    
    return calls.filter(call => new Date(call.created_at) >= cutoff)
  }

  const filteredCalls = getFilteredCalls()
  const totalFilteredCalls = filteredCalls.length

  // ========== METRICS BASED ON FILTERED CALLS ==========
  
  const resolvedCalls = filteredCalls.filter(c => c.call_outcome === 'resolved').length
  const resolutionRate = totalFilteredCalls ? Math.round((resolvedCalls / totalFilteredCalls) * 100) : 0
  
  const highUrgencyCount = filteredCalls.filter(c => c.urgency === 'high').length
  const mediumUrgencyCount = filteredCalls.filter(c => c.urgency === 'medium').length
  const lowUrgencyCount = filteredCalls.filter(c => c.urgency === 'low').length
  
  const negativeSentimentCount = filteredCalls.filter(c => c.sentiment === 'negative').length
  const neutralSentimentCount = filteredCalls.filter(c => c.sentiment === 'neutral').length
  const positiveSentimentCount = filteredCalls.filter(c => c.sentiment === 'positive').length

  // ========== CATEGORY DATA BASED ON FILTERED CALLS ==========
  
  const categoryMap = new Map<string, { count: number; resolved: number }>()
  
  filteredCalls.forEach(call => {
    const categories = call.issue_category.split(',').map(c => c.trim())
    categories.forEach(cat => {
      if (!cat) return
      const existing = categoryMap.get(cat) || { count: 0, resolved: 0 }
      existing.count += 1
      if (call.call_outcome === 'resolved') {
        existing.resolved += 1
      }
      categoryMap.set(cat, existing)
    })
  })

  const categoryData = Array.from(categoryMap.entries())
    .map(([name, data]) => ({
      name: name.charAt(0).toUpperCase() + name.slice(1),
      count: data.count,
      resolved: data.resolved,
      color: getCategoryColor(name)
    }))
    .sort((a, b) => b.count - a.count)

  // ========== WEEK-OVER-WEEK TRENDS (still based on all calls for comparison) ==========
  
  const lastWeekCalls = calls.filter(c => {
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return new Date(c.created_at) >= weekAgo
  }).length

  const previousWeekCalls = calls.filter(c => {
    const twoWeeksAgo = new Date()
    twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14)
    const oneWeekAgo = new Date()
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
    const callDate = new Date(c.created_at)
    return callDate >= twoWeeksAgo && callDate < oneWeekAgo
  }).length

  const volumeTrend = previousWeekCalls 
    ? Math.round(((lastWeekCalls - previousWeekCalls) / previousWeekCalls) * 100) 
    : 0

  // ========== TREND DATA BASED ON TIMEFRAME ==========
  
  const getDateRange = () => {
    const endDate = new Date()
    const startDate = new Date()
    
    if (timeframe === '7d') {
      startDate.setDate(startDate.getDate() - 7)
    } else if (timeframe === '30d') {
      startDate.setDate(startDate.getDate() - 30)
    } else { // 'all'
      if (calls.length > 0) {
        const dates = calls.map(c => new Date(c.created_at).getTime())
        startDate.setTime(Math.min(...dates))
      } else {
        startDate.setDate(startDate.getDate() - 30)
      }
    }
    
    return { startDate, endDate }
  }

  const generateTrendData = () => {
    const { startDate, endDate } = getDateRange()
    
    const dates: Date[] = []
    const currentDate = new Date(startDate)
    
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate))
      currentDate.setDate(currentDate.getDate() + 1)
    }
    
    let displayDates = dates
    if (timeframe === 'all' && dates.length > 30) {
      const step = Math.ceil(dates.length / 30)
      displayDates = dates.filter((_, i) => i % step === 0)
    }
    
    return displayDates.map(date => {
      const dayCalls = filteredCalls.filter(call => {
        const callDate = new Date(call.created_at)
        return callDate.toDateString() === date.toDateString()
      })
      
      return {
        day: timeframe === 'all' 
          ? date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
          : date.toLocaleDateString('en-US', { weekday: 'short' }),
        resolved: dayCalls.filter(c => c.call_outcome === 'resolved').length,
        unresolved: dayCalls.filter(c => c.call_outcome === 'unresolved').length,
        volume: dayCalls.length
      }
    })
  }

  const trendData = generateTrendData()

  // ========== DYNAMIC TITLES ==========
  
  const getTrendTitle = () => {
    switch(timeframe) {
      case '7d': return 'Call Volume & Resolution Trend (Last 7 Days)'
      case '30d': return 'Call Volume & Resolution Trend (Last 30 Days)'
      case 'all': return 'Call Volume & Resolution Trend (All Time)'
      default: return 'Call Volume & Resolution Trend'
    }
  }

  const getKPISubtext = () => {
    switch(timeframe) {
      case '7d': return 'Last 7 days'
      case '30d': return 'Last 30 days'
      case 'all': return 'All time'
      default: return ''
    }
  }

  // ========== DONUT DATA FOR URGENCY (FILTERED) ==========
  
  const urgencyDonutData = [
    { name: 'High', value: highUrgencyCount, color: COLORS.danger },
    { name: 'Medium', value: mediumUrgencyCount, color: COLORS.warning },
    { name: 'Low', value: lowUrgencyCount, color: COLORS.success }
  ].filter(item => item.value > 0)

  // ========== BAR DATA FOR SENTIMENT (FILTERED) ==========
  
  const sentimentBarData = [
    { name: 'Positive', value: positiveSentimentCount, color: COLORS.success },
    { name: 'Neutral', value: neutralSentimentCount, color: COLORS.neutral },
    { name: 'Negative', value: negativeSentimentCount, color: COLORS.danger }
  ]

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-container">
          <div className="loading-skeleton">
            <div className="skeleton-header"></div>
            <div className="skeleton-grid">
              <div className="skeleton-card"></div>
              <div className="skeleton-card"></div>
              <div className="skeleton-card"></div>
              <div className="skeleton-card"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="analytics-page">
      <div className="analytics-container">
        
        {/* Header */}
        <div className="analytics-header">
          <div>
            <h1>Operational Intelligence</h1>
            <p className="header-subtitle">
              {totalFilteredCalls} calls • {getKPISubtext()} • Last updated {new Date().toLocaleTimeString()}
            </p>
          </div>
          <div className="timeframe-selector">
            <button 
              className={`timeframe-btn ${timeframe === '7d' ? 'active' : ''}`}
              onClick={() => setTimeframe('7d')}
            >
              7D
            </button>
            <button 
              className={`timeframe-btn ${timeframe === '30d' ? 'active' : ''}`}
              onClick={() => setTimeframe('30d')}
            >
              30D
            </button>
            <button 
              className={`timeframe-btn ${timeframe === 'all' ? 'active' : ''}`}
              onClick={() => setTimeframe('all')}
            >
              All
            </button>
          </div>
        </div>

        {/* KPI Row - Now shows filtered data */}
        <div className="kpi-grid">
          {/* ML Risk Score Card - Still shows overall risk (ML model needs all data) */}
          {riskData && (
            <div className={`kpi-card risk-${riskData.level.toLowerCase()}`}>
              <div className="kpi-header">
                <span className="kpi-icon">🧠</span>
                <span className="kpi-label">ML Risk Score</span>
              </div>
              <div className="kpi-value">{riskData.risk_score}%</div>
              <div className="kpi-footer">
                <span className={`risk-badge ${riskData.level.toLowerCase()}`}>
                  {riskData.level} Risk
                </span>
                <span className="kpi-trend">
                  Based on {riskData.total_calls_used} calls
                </span>
              </div>
              {riskData.top_factor && (
                <div className="risk-factor">
                  <span className="factor-label">Top factor:</span>
                  <span className="factor-value">
                    {riskData.top_factor.name} {riskData.top_factor.impact}
                  </span>
                </div>
              )}
            </div>
          )}

          {/* Resolution Rate Card - Filtered */}
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">✅</span>
              <span className="kpi-label">Resolution Rate</span>
            </div>
            <div className="kpi-value">{resolutionRate}%</div>
            <div className="kpi-footer">
              <span className="kpi-subtext">{resolvedCalls} of {totalFilteredCalls} calls</span>
              <span className="kpi-trend positive">
                {resolutionRate > 70 ? '↑ Good' : '↓ Needs attention'}
              </span>
            </div>
          </div>

          {/* High Urgency Card - Filtered */}
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">⚠️</span>
              <span className="kpi-label">High Urgency</span>
            </div>
            <div className="kpi-value">{highUrgencyCount}</div>
            <div className="kpi-footer">
              <span className="kpi-subtext">
                {totalFilteredCalls ? Math.round((highUrgencyCount / totalFilteredCalls) * 100) : 0}% of {getKPISubtext()}
              </span>
              <span className={`kpi-trend ${highUrgencyCount > 5 ? 'negative' : 'positive'}`}>
                {highUrgencyCount > 5 ? '↑ High' : '↓ Normal'}
              </span>
            </div>
          </div>

          {/* Volume Card - Filtered */}
          <div className="kpi-card">
            <div className="kpi-header">
              <span className="kpi-icon">📞</span>
              <span className="kpi-label">Call Volume</span>
            </div>
            <div className="kpi-value">{totalFilteredCalls}</div>
            <div className="kpi-footer">
              <span className="kpi-subtext">{getKPISubtext()}</span>
              <span className={`kpi-trend ${volumeTrend > 0 ? 'negative' : 'positive'}`}>
                vs previous period
              </span>
            </div>
          </div>
        </div>

        {/* Volume & Resolution Trend Chart - Filtered */}
        <div className="chart-card">
          <div className="chart-header">
            <h3>{getTrendTitle()}</h3>
            <div className="chart-legend">
              <span className="legend-item">
                <span className="legend-dot resolved"></span> Resolved
              </span>
              <span className="legend-item">
                <span className="legend-dot unresolved"></span> Unresolved
              </span>
              <span className="legend-item">
                <span className="legend-dot volume"></span> Volume
              </span>
            </div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis 
                  dataKey="day" 
                  stroke="#64748b" 
                  angle={timeframe === 'all' ? -45 : 0}
                  textAnchor={timeframe === 'all' ? 'end' : 'middle'}
                  height={timeframe === 'all' ? 60 : 30}
                />
                <YAxis yAxisId="left" stroke="#64748b" />
                <YAxis yAxisId="right" orientation="right" stroke="#64748b" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }} 
                />
                <Legend />
                <Bar yAxisId="left" dataKey="volume" fill="#a78bfa" opacity={0.3} name="Volume" />
                <Line yAxisId="right" type="monotone" dataKey="resolved" stroke="#34d399" strokeWidth={3} name="Resolved" />
                <Line yAxisId="right" type="monotone" dataKey="unresolved" stroke="#f87171" strokeWidth={3} name="Unresolved" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Charts Row - Mixed Styles - All Filtered */}
        <div className="charts-mixed-row">
          {/* Urgency Donut Chart - Filtered */}
          <div className="chart-card half-width">
            <h3>Urgency Distribution {timeframe !== 'all' && `(${getKPISubtext()})`}</h3>
            <div className="donut-container">
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={urgencyDonutData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                    labelLine={false}
                  >
                    {urgencyDonutData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="donut-center">
                <span className="donut-value">{totalFilteredCalls}</span>
                <span className="donut-label">Total Calls</span>
              </div>
            </div>
            <div className="donut-legend">
              {urgencyDonutData.map((item, index) => (
                <div key={index} className="legend-item-horizontal">
                  <span className="legend-color" style={{ backgroundColor: item.color }}></span>
                  <span className="legend-name">{item.name}</span>
                  <span className="legend-value">{item.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Sentiment Bar Chart - Filtered */}
          <div className="chart-card half-width">
            <h3>Sentiment Distribution {timeframe !== 'all' && `(${getKPISubtext()})`}</h3>
            <div className="compact-bar-chart">
              {sentimentBarData.map((item, index) => (
                <div key={index} className="compact-bar-item">
                  <div className="compact-bar-header">
                    <span className="compact-bar-label">{item.name}</span>
                    <span className="compact-bar-value">{item.value}</span>
                  </div>
                  <div className="compact-bar-container">
                    <div 
                      className="compact-bar-fill"
                      style={{ 
                        width: `${totalFilteredCalls ? (item.value / totalFilteredCalls) * 100 : 0}%`,
                        backgroundColor: item.color
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
            <div className="compact-total">
              <span className="total-label">Total</span>
              <span className="total-value">{totalFilteredCalls}</span>
            </div>
          </div>
        </div>

        {/* Category Performance - Filtered */}
        {categoryData.length > 0 && (
          <div className="chart-card">
            <h3>Category Performance {timeframe !== 'all' && `(${getKPISubtext()})`}</h3>
            <div className="category-list">
              {categoryData.slice(0, 5).map((cat, index) => (
                <div key={index} className="category-item">
                  <div className="category-header">
                    <div className="category-title">
                      <span className="category-dot" style={{ backgroundColor: cat.color }}></span>
                      <span className="category-name">{cat.name}</span>
                    </div>
                    <span className="category-count">{cat.count} calls</span>
                  </div>
                  <div className="category-bars">
                    <div className="resolution-bar">
                      <div 
                        className="resolution-fill"
                        style={{ 
                          width: `${(cat.resolved / cat.count) * 100}%`,
                          backgroundColor: cat.color
                        }}
                      />
                    </div>
                    <div className="category-stats">
                      <span className="resolved-count">✅ {cat.resolved} resolved</span>
                      <span className="resolution-rate">
                        {Math.round((cat.resolved / cat.count) * 100)}% resolution
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No data message */}
        {totalFilteredCalls === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📊</div>
            <h3>No data available for this period</h3>
            <p>Try selecting a different timeframe or upload more calls.</p>
          </div>
        )}

      </div>
    </div>
  )
}

// Helper function for category colors
function getCategoryColor(category: string): string {
  const colorMap: Record<string, string> = {
    'billing': '#a78bfa',
    'refund': '#fbbf24',
    'technical': '#34d399',
    'delivery': '#60a5fa',
    'other': '#94a3b8'
  }
  return colorMap[category.toLowerCase()] || '#94a3b8'
}