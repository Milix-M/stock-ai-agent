import { create } from 'zustand'
import { watchlistApi, WatchlistItem } from '../services/watchlist'

interface WatchlistState {
  items: WatchlistItem[]
  isLoading: boolean
  error: string | null
  
  // Actions
  fetchWatchlist: () => Promise<void>
  addToWatchlist: (stockCode: string, alertThreshold?: number) => Promise<void>
  removeFromWatchlist: (stockCode: string) => Promise<void>
  clearError: () => void
}

export const useWatchlistStore = create<WatchlistState>()((set, get) => ({
  items: [],
  isLoading: false,
  error: null,

  fetchWatchlist: async () => {
    set({ isLoading: true, error: null })
    try {
      const items = await watchlistApi.getWatchlist()
      set({ items, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'ウォッチリストの取得に失敗しました',
        isLoading: false,
      })
    }
  },

  addToWatchlist: async (stockCode, alertThreshold) => {
    set({ isLoading: true, error: null })
    try {
      const newItem = await watchlistApi.addToWatchlist(stockCode, alertThreshold)
      set({
        items: [newItem, ...get().items],
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'ウォッチリストへの追加に失敗しました',
        isLoading: false,
      })
      throw error
    }
  },

  removeFromWatchlist: async (stockCode) => {
    set({ isLoading: true, error: null })
    try {
      await watchlistApi.removeFromWatchlist(stockCode)
      set({
        items: get().items.filter(item => item.stock_code !== stockCode),
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'ウォッチリストからの削除に失敗しました',
        isLoading: false,
      })
      throw error
    }
  },

  clearError: () => set({ error: null }),
}))
