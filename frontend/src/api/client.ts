// Typed API client derived from backend routes
const API_BASE = '/api/v1'

interface RequestOptions extends RequestInit {
  params?: Record<string, string>
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { params, headers, ...fetchOptions } = options
  
  const url = new URL(`${API_BASE}${endpoint}`, window.location.origin)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value)
    })
  }

  const response = await fetch(url.toString(), {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    credentials: 'include', // For cookie-based auth
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

export const api = {
  get: <T>(endpoint: string, params?: Record<string, string>) => 
    request<T>(endpoint, { method: 'GET', params }),

  post: <T>(endpoint: string, body: unknown) => 
    request<T>(endpoint, { method: 'POST', body: JSON.stringify(body) }),

  put: <T>(endpoint: string, body: unknown) => 
    request<T>(endpoint, { method: 'PUT', body: JSON.stringify(body) }),

  delete: <T>(endpoint: string) => 
    request<T>(endpoint, { method: 'DELETE' }),
}

// Health API
export const healthApi = {
  check: () => api.get<{ status: string; service: string; version: string }>('/health'),
  checkDb: () => api.get<{ status: string; database: string; error?: string }>('/health/db'),
}

// Issues API
export interface IssueAnalysisRequest {
  title: string
  body: string
  php_version?: string
  os?: string
}

export interface IssueAnalysisResponse {
  issue_type: string
  confidence: number
  reproduction_hints: string[]
  related_issues: number[]
}

export type IssueType = 
  | 'jit_segfault'
  | 'gc_threshold'
  | 'fork_safety'
  | 'array_unique'
  | 'ldap_cleanup'
  | 'unknown'

export const issuesApi = {
  analyze: (request: IssueAnalysisRequest) => 
    api.post<IssueAnalysisResponse>('/issues/analyze', request),
  
  listTypes: () => api.get<IssueType[]>('/issues/types'),
}