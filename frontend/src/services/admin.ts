import { api } from './api'

export const adminApi = {
  seedDatabase: async (): Promise<{ message: string; created: number; skipped: number; total: number }> => {
    const response = await api.post('/admin/seed')
    return response.data
  },
}
