import { api } from './api'

export interface MarketIndex {
  name: string
  code: string
  current: number
  change: number
  change_percent: number
  open?: number
  high?: number
  low?: number
  volume?: number
}

export interface MarketOverview {
  indices: {
    nikkei_225: MarketIndex | null
    nikkei_futures: MarketIndex | null
  }
  updated_at?: string
  data_source?: string
}

export const marketApi = {
  getMarketOverview: async (): Promise<MarketOverview> => {
    const response = await api.get('/market/overview')
    return response.data
  },

  getNikkei: async (): Promise<MarketIndex> => {
    const response = await api.get('/market/nikkei')
    return response.data
  },
}
