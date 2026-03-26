import { api } from './api'

export interface WatchlistItem {
  id: string
  stock_id: string
  alert_threshold?: number
  created_at: string
  stock: {
    id: string
    code: string
    name: string
    market?: string
    sector?: string
    per?: number
    pbr?: number
    dividend_yield?: number
  }
}

export interface WatchlistCreateRequest {
  stock_code: string
  alert_threshold?: number
}

export const watchlistApi = {
  getWatchlist: async (): Promise<WatchlistItem[]> => {
    const response = await api.get('/watchlist/')
    return response.data
  },

  addToWatchlist: async (stockCode: string, alertThreshold?: number): Promise<WatchlistItem> => {
    const response = await api.post('/watchlist/', {
      stock_code: stockCode,
      alert_threshold: alertThreshold,
    })
    return response.data
  },

  removeFromWatchlist: async (stockCode: string): Promise<void> => {
    await api.delete(`/watchlist/${stockCode}`)
  },

  checkWatchlist: async (stockCode: string): Promise<{ in_watchlist: boolean }> => {
    const response = await api.get(`/watchlist/${stockCode}/check`)
    return response.data
  },
}
