import { api } from './api'

export interface Stock {
  id: string
  code: string
  name: string
  market?: string
  sector?: string
  per?: number
  pbr?: number
  dividend_yield?: number
}

export const stockApi = {
  searchStocks: async (query: string): Promise<Stock[]> => {
    const response = await api.get(`/stocks?q=${encodeURIComponent(query)}&limit=20`)
    return response.data
  },

  getStockDetail: async (code: string): Promise<any> => {
    const response = await api.get(`/stocks/${code}`)
    return response.data
  },
}
