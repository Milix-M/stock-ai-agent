import { api } from './api'

export interface Recommendation {
  stock_code: string
  stock_name: string
  pattern_name: string
  match_score: number
  matched_criteria: string[]
  reason: string
}

export interface RecommendationsResponse {
  recommendations: Recommendation[]
  total: number
  patterns_used: number
  message?: string
}

export const recommendationApi = {
  getRecommendations: async (): Promise<RecommendationsResponse> => {
    const response = await api.get('/recommendations/')
    return response.data
  },
}
