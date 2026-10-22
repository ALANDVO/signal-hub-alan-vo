// Frontend tests
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import IssueAnalyzer from './IssueAnalyzer'
import * as apiModule from '../api/client'

interface IssueAnalysisResponse {
  issue_type: string
  confidence: number
  reproduction_hints: string[]
  related_issues: number[]
}

// Mock the module
vi.mock('../api/client', () => {
  const mockPost = vi.fn()
  return {
    api: {
      get: vi.fn(),
      post: mockPost,
      put: vi.fn(),
      delete: vi.fn(),
    },
    issuesApi: {
      analyze: mockPost,
      listTypes: vi.fn(),
    },
    healthApi: {
      check: vi.fn(),
      checkDb: vi.fn(),
    },
  }
})

const renderWithRouter = (component: React.ReactNode) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('IssueAnalyzer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the analyzer form', () => {
    renderWithRouter(<IssueAnalyzer />)
    
    expect(screen.getByText('Issue Analyzer')).toBeInTheDocument()
    expect(screen.getByLabelText('Issue Title')).toBeInTheDocument()
    expect(screen.getByLabelText('Issue Body / Description')).toBeInTheDocument()
    expect(screen.getByLabelText('PHP Version (optional)')).toBeInTheDocument()
    expect(screen.getByLabelText('Operating System (optional)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Analyze Issue' })).toBeInTheDocument()
  })

  it('shows error when title is empty on submit', async () => {
    renderWithRouter(<IssueAnalyzer />)
    
    fireEvent.click(screen.getByRole('button', { name: 'Analyze Issue' }))
    
    // HTML5 validation prevents submit, so button click doesn't trigger API
    await waitFor(() => {
      expect(apiModule.api.post).not.toHaveBeenCalled()
    })
  })

  it('calls API and displays result for JIT segfault', async () => {
    const mockResponse: IssueAnalysisResponse = {
      issue_type: 'jit_segfault',
      confidence: 0.85,
      reproduction_hints: [
        'Enable JIT: opcache.jit=tracing',
        'Test with PHP 8.1.x',
      ],
      related_issues: [7817],
    }
    
    vi.mocked(apiModule.api.post).mockResolvedValue(mockResponse)
    
    renderWithRouter(<IssueAnalyzer />)
    
    fireEvent.change(screen.getByLabelText('Issue Title'), { target: { value: 'JIT segfault in PHP 8.1' } })
    fireEvent.change(screen.getByLabelText('Issue Body / Description'), { target: { value: 'Segmentation fault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analyze Issue' }))
    
    await waitFor(() => {
      expect(screen.getByText('JIT Segfault')).toBeInTheDocument()
    })
    
    expect(screen.getByText('Confidence: 85%')).toBeInTheDocument()
    expect(screen.getByText('Enable JIT: opcache.jit=tracing')).toBeInTheDocument()
    expect(screen.getByText('php/php-src#7817')).toBeInTheDocument()
  })

  it('displays loading state during analysis', async () => {
    let resolvePromise: (value: IssueAnalysisResponse) => void
    const promise = new Promise<IssueAnalysisResponse>((resolve) => {
      resolvePromise = resolve
    })
    vi.mocked(apiModule.api.post).mockReturnValue(promise)
    
    renderWithRouter(<IssueAnalyzer />)
    
    fireEvent.change(screen.getByLabelText('Issue Title'), { target: { value: 'Test issue' } })
    fireEvent.change(screen.getByLabelText('Issue Body / Description'), { target: { value: 'Test body' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analyze Issue' }))
    
    expect(screen.getByRole('button', { name: 'Analyzing...' })).toBeDisabled()
    
    resolvePromise!({
      issue_type: 'unknown',
      confidence: 0,
      reproduction_hints: [],
      related_issues: [],
    })
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Analyze Issue' })).not.toBeDisabled()
    })
  })

  it('displays error message on API failure', async () => {
    vi.mocked(apiModule.api.post).mockRejectedValue(new Error('Network error'))
    
    renderWithRouter(<IssueAnalyzer />)
    
    fireEvent.change(screen.getByLabelText('Issue Title'), { target: { value: 'Test issue' } })
    fireEvent.change(screen.getByLabelText('Issue Body / Description'), { target: { value: 'Test body' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analyze Issue' }))
    
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })

  it('clears result when clear button clicked', async () => {
    const mockResponse: IssueAnalysisResponse = {
      issue_type: 'jit_segfault',
      confidence: 0.85,
      reproduction_hints: ['Hint 1'],
      related_issues: [7817],
    }
    
    vi.mocked(apiModule.api.post).mockResolvedValue(mockResponse)
    
    renderWithRouter(<IssueAnalyzer />)
    
    fireEvent.change(screen.getByLabelText('Issue Title'), { target: { value: 'JIT segfault' } })
    fireEvent.change(screen.getByLabelText('Issue Body / Description'), { target: { value: 'Stack trace' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analyze Issue' }))
    
    await waitFor(() => {
      expect(screen.getByText('JIT Segfault')).toBeInTheDocument()
    })
    
    fireEvent.click(screen.getByRole('button', { name: 'Clear' }))
    
    expect(screen.queryByText('JIT Segfault')).not.toBeInTheDocument()
  })
})