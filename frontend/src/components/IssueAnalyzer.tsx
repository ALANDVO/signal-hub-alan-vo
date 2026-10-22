// Issue Analyzer component
import { useState } from 'react'
import { api } from '../api/client'
import './IssueAnalyzer.css'

interface IssueAnalysisRequest {
  title: string
  body: string
  php_version?: string
  os?: string
}

interface IssueAnalysisResponse {
  issue_type: string
  confidence: number
  reproduction_hints: string[]
  related_issues: number[]
}

const ISSUE_TYPES = {
  jit_segfault: { label: 'JIT Segfault', color: '#ef4444', description: 'Segmentation fault in JIT-compiled code' },
  gc_threshold: { label: 'GC Threshold', color: '#f59e0b', description: 'Performance regression from GC threshold changes' },
  fork_safety: { label: 'Fork Safety (macOS)', color: '#8b5cf6', description: 'Child process crash after fork on macOS' },
  array_unique: { label: 'array_unique Bug', color: '#06b6d4', description: 'Non-transitive comparison in SORT_REGULAR' },
  ldap_cleanup: { label: 'LDAP Cleanup', color: '#84cc16', description: 'Segfault during OpenSSL engine cleanup' },
  unknown: { label: 'Unknown', color: '#6b7280', description: 'No matching pattern found' },
}

export default function IssueAnalyzer() {
  const [request, setRequest] = useState<IssueAnalysisRequest>({
    title: '',
    body: '',
    php_version: '',
    os: '',
  })
  const [response, setResponse] = useState<IssueAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResponse(null)
    
    try {
      const data = await api.post<IssueAnalysisResponse>('/issues/analyze', request)
      setResponse(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (field: keyof IssueAnalysisRequest, value: string) => {
    setRequest(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="issue-analyzer">
      <div className="analyzer-header">
        <h1>Issue Analyzer</h1>
        <p>Paste a PHP issue report to classify the failure type and get reproduction hints.</p>
      </div>

      <form onSubmit={handleSubmit} className="analyzer-form">
        <div className="form-grid">
          <div className="form-field full-width">
            <label htmlFor="title">Issue Title</label>
            <input
              id="title"
              type="text"
              value={request.title}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="e.g., JIT segmentation fault in PHP 8.1"
              required
            />
          </div>
          <div className="form-field full-width">
            <label htmlFor="body">Issue Body / Description</label>
            <textarea
              id="body"
              value={request.body}
              onChange={(e) => handleChange('body', e.target.value)}
              placeholder="Paste the issue description, stack trace, or error messages..."
              rows={8}
              required
            />
          </div>
          <div className="form-field">
            <label htmlFor="php_version">PHP Version (optional)</label>
            <input
              id="php_version"
              type="text"
              value={request.php_version}
              onChange={(e) => handleChange('php_version', e.target.value)}
              placeholder="e.g., 8.1.0"
            />
          </div>
          <div className="form-field">
            <label htmlFor="os">Operating System (optional)</label>
            <input
              id="os"
              type="text"
              value={request.os}
              onChange={(e) => handleChange('os', e.target.value)}
              placeholder="e.g., CentOS 7, macOS 13.5"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Analyzing...' : 'Analyze Issue'}
          </button>
          <button type="button" onClick={() => { setResponse(null); setError(null); }} className="btn btn-secondary">
            Clear
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
      </form>

      {response && (
        <div className="analysis-result">
          <h2>Analysis Result</h2>
          <div className="result-card">
            <div className="result-type">
              <span 
                className="type-badge" 
                style={{ backgroundColor: ISSUE_TYPES[response.issue_type as keyof typeof ISSUE_TYPES]?.color || '#6b7280' }}
              >
                {ISSUE_TYPES[response.issue_type as keyof typeof ISSUE_TYPES]?.label || 'Unknown'}
              </span>
              <div className="confidence">
                Confidence: {(response.confidence * 100).toFixed(0)}%
              </div>
            </div>
            <p className="type-description">
              {ISSUE_TYPES[response.issue_type as keyof typeof ISSUE_TYPES]?.description || 'No description available'}
            </p>

            {response.reproduction_hints.length > 0 && (
              <div className="hints-section">
                <h3>Reproduction Hints</h3>
                <ul>
                  {response.reproduction_hints.map((hint, i) => (
                    <li key={i}>{hint}</li>
                  ))}
                </ul>
              </div>
            )}

            {response.related_issues.length > 0 && (
              <div className="related-section">
                <h3>Related PHP Issues</h3>
                <ul>
                  {response.related_issues.map((issueNum) => (
                    <li key={issueNum}>
                      <a href={`https://github.com/php/php-src/issues/${issueNum}`} target="_blank" rel="noopener noreferrer">
                        php/php-src#{issueNum}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}