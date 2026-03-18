import { api } from './api'

export interface Pattern {
  id: string
  name: string
  description?: string
  raw_input: string
  parsed_filters: {
    strategy?: string
    filters?: {
      per_min?: number
      per_max?: number
      pbr_min?: number
      pbr_max?: number
      dividend_yield_min?: number
      dividend_yield_max?: number
      market_cap_min?: number
      market_cap_max?: number
    }
    sort_by?: string
    sort_order?: string
    keywords?: string[]
  }
  is_active: boolean
  created_at: string
}

export interface PatternCreateRequest {
  name: string
  description?: string
  raw_input: string
  parsed_filters: Pattern['parsed_filters']
}

export interface PatternParseRequest {
  input: string
}

export interface PatternParseResponse {
  raw_input: string
  parsed: Pattern['parsed_filters']
}

export const patternApi = {
  getPatterns: async (): Promise<Pattern[]> => {
    const response = await api.get('/patterns/')
    return response.data
  },

  parsePattern: async (input: string): Promise<PatternParseResponse> => {
    const response = await api.post('/patterns/parse', { input })
    return response.data
  },

  createPattern: async (data: PatternCreateRequest): Promise<Pattern> => {
    const response = await api.post('/patterns/', data)
    return response.data
  },

  deletePattern: async (patternId: string): Promise<void> => {
    await api.delete(`/patterns/${patternId}`)
  },

  togglePattern: async (patternId: string): Promise<{ is_active: boolean }> => {
    const response = await api.patch(`/patterns/${patternId}/toggle`)
    return response.data
  },
}
