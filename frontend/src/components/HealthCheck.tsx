// Health Check component
import { useState, useEffect } from 'react'
import { healthApi } from '../api/client'
import './HealthCheck.css'

interface HealthStatus {
  status: string
  service: string
  version: string
}

interface DbHealthStatus {
  status: string
  database: string
  error?: string
}

export default function HealthCheck() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [dbHealth, setDbHealth] = useState<DbHealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const checkHealth = async () => {
    setLoading(true)
    setError(null)
    try {
      const [healthRes, dbHealthRes] = await Promise.all([
        healthApi.check(),
        healthApi.checkDb(),
      ])
      setHealth(healthRes)
      setDbHealth(dbHealthRes)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Health check failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkHealth()
  }, [])

  if (loading && !health) {
    return (
      <div className="health-check loading">
        <div className="spinner"></div>
        <p>Checking system health...</p>
      </div>
    )
  }

  return (
    <div className="health-check">
      <div className="health-header">
        <h1>System Health</h1>
        <button onClick={checkHealth} disabled={loading} className="btn btn-secondary">
          {loading ? 'Checking...' : 'Refresh'}
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="health-grid">
        <div className={`health-card ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
          <div className="health-card-header">
            <svg className="health-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <h2>API Service</h2>
          </div>
          <div className={`health-status ${health?.status}`}>
            {health?.status === 'healthy' ? '✓ Healthy' : '✗ Unhealthy'}
          </div>
          <div className="health-details">
            {health && (
              <>
                <div><strong>Service:</strong> {health.service}</div>
                <div><strong>Version:</strong> {health.version}</div>
              </>
            )}
          </div>
        </div>

        <div className={`health-card ${dbHealth?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
          <div className="health-card-header">
            <svg className="health-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <ellipse cx="12" cy="5" rx="9" ry="3" />
              <path d="M3 5v14a9 3 0 0 0 18 0V5" />
            </svg>
            <h2>Database</h2>
          </div>
          <div className={`health-status ${dbHealth?.status}`}>
            {dbHealth?.status === 'healthy' ? '✓ Connected' : '✗ Disconnected'}
          </div>
          <div className="health-details">
            {dbHealth && (
              <>
                <div><strong>Status:</strong> {dbHealth.database}</div>
                {dbHealth.error && <div className="error"><strong>Error:</strong> {dbHealth.error}</div>}
              </>
            )}
          </div>
        </div>
      </div>

      <div className="health-info">
        <h3>Endpoints</h3>
        <ul>
          <li><code>GET /api/v1/health</code> — Basic service health</li>
          <li><code>GET /api/v1/health/db</code> — Database connectivity</li>
          <li><code>POST /api/v1/issues/analyze</code> — Issue classification</li>
          <li><code>GET /api/v1/issues/types</code> — List issue types</li>
        </ul>
      </div>
    </div>
  )
}