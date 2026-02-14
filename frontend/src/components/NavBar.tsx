import { NavLink } from "react-router-dom"
import "./Navbar.css"

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span className="brand-icon">🎧</span>
        <div className="brand-text-wrapper">
          <span className="brand-text">CallSense</span>
          <span className="brand-badge">Analytics</span>
        </div>
      </div>

      <div className="navbar-links">
        <NavLink 
          to="/analyze" 
          className={({ isActive }) => 
            isActive ? "nav-link active" : "nav-link"
          }
        >
          <span className="nav-icon">🔍</span>
          <span className="nav-label">Analyze</span>
          <span className="active-indicator-wrapper">
            <span className="active-indicator" />
          </span>
        </NavLink>

        <NavLink 
          to="/analytics" 
          className={({ isActive }) => 
            isActive ? "nav-link active" : "nav-link"
          }
        >
          <span className="nav-icon">📊</span>
          <span className="nav-label">Analytics</span>
        </NavLink>

        <NavLink 
          to="/history" 
          className={({ isActive }) => 
            isActive ? "nav-link active" : "nav-link"
          }
        >
          <span className="nav-icon">📋</span>
          <span className="nav-label">History</span>
          <span className="active-indicator-wrapper">
            <span className="active-indicator" />
          </span>
        </NavLink>
      </div>

      <div className="navbar-profile">
        <div className="profile-avatar">
          <span className="avatar-icon">👤</span>
        </div>
        <div className="profile-info">
          <span className="profile-name">Admin</span>
          <span className="profile-role">Support Lead</span>
        </div>
      </div>
    </nav>
  )
}