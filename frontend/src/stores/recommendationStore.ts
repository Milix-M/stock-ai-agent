import { create } from 'zustand'
import { recommendationApi, RecommendationsResponse } from '../services/recommendation'

interface RecommendationState {
  recommendations: RecommendationsResponse['recommendations']
  total: number
  patternsUsed: number
  isLoading: boolean
  error: string | null
  
  // Actions
  fetchRecommendations: () => Promise<void>
  clearError: () => void
}

export const useRecommendationStore = create<RecommendationState>()((set) => ({
  recommendations: [],
  total: 0,
  patternsUsed: 0,
  isLoading: false,
  error: null,

  fetchRecommendations: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await recommendationApi.getRecommendations()
      set({
        recommendations: response.recommendations,
        total: response.total,
        patternsUsed: response.patterns_used,
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'レコメンドの取得に失敗しました',
        isLoading: false,
      })
    }
  },

  clearError: () => set({ error: null }),
}))
