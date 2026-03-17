import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi, User } from '../services/auth'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  
  // Actions
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, displayName?: string) => Promise<void>
  logout: () => void
  clearError: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.login({ email, password })
          localStorage.setItem('access_token', response.access_token)
          localStorage.setItem('refresh_token', response.refresh_token)
          
          // ユーザー情報取得
          const user = await authApi.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'ログインに失敗しました',
            isLoading: false,
          })
          throw error
        }
      },

      register: async (email, password, displayName) => {
        set({ isLoading: true, error: null })
        try {
          const response = await authApi.register({ email, password, display_name: displayName })
          localStorage.setItem('access_token', response.access_token)
          localStorage.setItem('refresh_token', response.refresh_token)
          
          const user = await authApi.getCurrentUser()
          set({ user, isAuthenticated: true, isLoading: false })
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || '登録に失敗しました',
            isLoading: false,
          })
          throw error
        }
      },

      logout: () => {
        authApi.logout()
        set({ user: null, isAuthenticated: false, error: null })
      },

      clearError: () => set({ error: null }),
      
      setUser: (user) => set({ user, isAuthenticated: true }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
