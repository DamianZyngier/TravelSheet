import { render, screen, waitFor, act } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import App from './App'

// Mock fetch
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

describe('App Smoke Test', () => {
  beforeEach(() => {
    mockFetch.mockClear()
    // Reset location
    const url = new URL('http://localhost/')
    Object.defineProperty(window, 'location', {
      value: url,
      writable: true,
      configurable: true
    })
  })

  it('renders loading state initially', () => {
    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => ({})
    })
    
    render(<App />)
    expect(screen.getByText(/Ładowanie danych podróżniczych/i)).toBeInTheDocument()
  })

  it('renders country grid when data is loaded', async () => {
    const mockData = {
      "PL": {
        "name": "Poland",
        "name_pl": "Polska",
        "iso2": "PL",
        "continent": "Europe",
        "flag_url": "https://flag.url",
        "safety": { "risk_level": "low" },
        "currency": { "code": "PLN" },
        "practical": { "plug_types": "C, E" },
        "languages": [],
        "religions": [],
        "unesco_count": 0,
        "wiki_summary": "Summary"
      }
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData
    })

    render(<App />)
    
    const polskaElement = await screen.findByText(/Polska/i)
    expect(polskaElement).toBeInTheDocument()
  })

  it('synchronizes state with URL on browser navigation (popstate)', async () => {
    const mockData = {
      "PL": {
        "name": "Poland",
        "name_pl": "Polska",
        "iso2": "PL",
        "continent": "Europe",
        "flag_url": "https://flag.url",
        "safety": { "risk_level": "low" },
        "currency": { "code": "PLN" },
        "practical": { "plug_types": "C, E" },
        "languages": [],
        "religions": [],
        "unesco_count": 0,
        "wiki_summary": "Summary"
      }
    }

    mockFetch.mockResolvedValue({
      ok: true,
      json: async () => mockData
    })

    render(<App />)
    
    // 1. Initial state (list)
    await screen.findByText(/Polska/i)

    // 2. Simulate URL change to ?kraj=PL
    const urlWithParam = new URL('http://localhost/?kraj=PL')
    Object.defineProperty(window, 'location', {
      value: urlWithParam,
      writable: true,
      configurable: true
    })

    // Trigger popstate within act
    await act(async () => {
      window.dispatchEvent(new PopStateEvent('popstate'))
    })

    // 3. Should now show detail view
    await waitFor(() => {
      expect(screen.getByText(/Poland \(PL\)/i)).toBeInTheDocument()
    }, { timeout: 2000 })

    // 4. Mock URL change back to home
    const homeUrl = new URL('http://localhost/')
    Object.defineProperty(window, 'location', {
      value: homeUrl,
      writable: true,
      configurable: true
    })
    
    await act(async () => {
      window.dispatchEvent(new PopStateEvent('popstate'))
    })

    // 5. Should show list again
    await waitFor(() => {
      expect(screen.getByText(/Twoje centrum bezpiecznych podróży/i)).toBeInTheDocument()
    })
  })
})
