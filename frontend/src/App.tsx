// Main App component
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './components/Dashboard'
import IssueAnalyzer from './components/IssueAnalyzer'
import HealthCheck from './components/HealthCheck'

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze" element={<IssueAnalyzer />} />
        <Route path="/health" element={<HealthCheck />} />
      </Route>
    </Routes>
  )
}

export default App