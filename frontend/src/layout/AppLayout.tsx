import { Outlet } from "react-router-dom"
import NavBar from "../components/NavBar"
import "./AppLayout.css"

export default function AppLayout() {
  return (
    <div className="app-layout">
      <NavBar />
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  )
}