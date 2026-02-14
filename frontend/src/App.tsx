import { Routes, Route } from "react-router-dom"
import Analyze from "./pages/Analyze"
import History from "./pages/History"
import Dashboard from "./pages/Dashboard"
import AppLayout from "./layout/AppLayout" // Use your AppLayout!

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route path="analyze" element={<Analyze />} />
        <Route path="analytics" element={<Dashboard />} />
        <Route path="history" element={<History />} />
      </Route>
    </Routes>
  )
}

export default App