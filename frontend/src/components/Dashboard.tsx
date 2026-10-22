// Dashboard component
import { Link } from 'react-router-dom'
import './Dashboard.css'

interface StatCardProps {
  title: string
  value: string | number
  description: string
  icon: React.ReactNode
}

function StatCard({ title, value, description, icon }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-title">{title}</div>
      <div className="stat-description">{description}</div>
    </div>
  )
}

export default function Dashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>PHP Interpreter Issue Analysis</h1>
        <p className="subtitle">
          AI/ML-powered analysis of PHP core issues: JIT segfaults, GC regressions, fork safety, and more.
        </p>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Known Issue Types"
          value={5}
          description="Classified PHP bug patterns"
          icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>}
        />
        <StatCard
          title="Reference Issues"
          value={7}
          description="From php/php-src tracker"
          icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>}
        />
        <StatCard
          title="Analysis Engine"
          value="Deterministic"
          description="Offline pattern matching"
          icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><path d="M8 21h8"/><path d="M12 17v4"/></svg>}
        />
        <StatCard
          title="LLM Integration"
          value="Opt-in"
          description="Advisory explanations only"
          icon={<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/><path d="M21 12v7a2 2 0 0 1-2 2h-5"/></svg>}
        />
      </div>

      <div className="workflows">
        <h2>Core Workflows</h2>
        <div className="workflow-cards">
          <Link to="/analyze" className="workflow-card">
            <div className="workflow-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </div>
            <h3>Issue Analysis</h3>
            <p>Paste a PHP issue report to classify the failure type and get reproduction hints.</p>
            <span className="workflow-link">Try it →</span>
          </Link>
          <Link to="/health" className="workflow-card">
            <div className="workflow-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <h3>System Health</h3>
            <p>Check API and database connectivity status.</p>
            <span className="workflow-link">Check →</span>
          </Link>
          <div className="workflow-card coming-soon">
            <div className="workflow-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><path d="M8 21h8"/><path d="M12 17v4"/></svg>
            </div>
            <h3>Reproduction Runner</h3>
            <p>Submit PHP code snippets for isolated execution and segfault detection.</p>
            <span className="workflow-link disabled">Coming soon</span>
          </div>
          <div className="workflow-card coming-soon">
            <div className="workflow-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
            </div>
            <h3>Bisect Automation</h3>
            <p>Automated git bisect to find regression-introducing commits in php-src.</p>
            <span className="workflow-link disabled">Coming soon</span>
          </div>
        </div>
      </div>

      <div className="reference-issues">
        <h2>Reference PHP Issues</h2>
        <table>
          <thead>
            <tr>
              <th>Issue</th>
              <th>Title</th>
              <th>Type</th>
              <th>PHP Version</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><a href="https://github.com/php/php-src/issues/7817" target="_blank" rel="noopener noreferrer">#7817</a></td>
              <td>JIT segmentation fault in PHP 8.1</td>
              <td>JIT Segfault</td>
              <td>8.1.0-8.1.1</td>
            </tr>
            <tr>
              <td><a href="https://github.com/php/php-src/issues/9993" target="_blank" rel="noopener noreferrer">#9993</a></td>
              <td>Bad performance with hard-coded GC_THRESHOLD values</td>
              <td>GC Threshold</td>
              <td>8.1.10+</td>
            </tr>
            <tr>
              <td><a href="https://github.com/php/php-src/issues/11818" target="_blank" rel="noopener noreferrer">#11818</a></td>
              <td>macOS crashes fork() process</td>
              <td>Fork Safety</td>
              <td>8.2.8 / macOS 13.5</td>
            </tr>
            <tr>
              <td><a href="https://github.com/php/php-src/issues/20262" target="_blank" rel="noopener noreferrer">#20262</a></td>
              <td>array_unique() with SORT_REGULAR returns duplicates</td>
              <td>Array Unique</td>
              <td>8.4.13</td>
            </tr>
            <tr>
              <td><a href="https://github.com/php/php-src/issues/8620" target="_blank" rel="noopener noreferrer">#8620</a></td>
              <td>Segfault on exit with ldap_bind()</td>
              <td>LDAP Cleanup</td>
              <td>7.4.28, 8.0.16</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}