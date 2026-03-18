import { api } from './api'

export const adminApi = {
  seedDatabase: async (): Promise<{ message: string; created: number; skipped: number; total: number }> => {
    const response = await api.post('/admin/seed')
    return response.data
  },

  getSetupStatus: async (): Promise<{ is_seeded: boolean; stock_count: number }> => {
    const response = await api.get('/admin/status')
    return response.data
  },
}
