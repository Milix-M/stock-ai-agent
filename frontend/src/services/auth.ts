import { api } from './api'

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  display_name?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  display_name?: string
  created_at: string
}

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    // OAuth2形式で送信
    const formData = new URLSearchParams()
    formData.append('username', data.email)
    formData.append('password', data.password)
    
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/users/me')
    return response.data
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },

  requestPasswordReset: async (email: string): Promise<{ message: string; reset_token: string | null; dev_mode: boolean }> => {
    const response = await api.post('/auth/password-reset/request', { email })
    return response.data
  },

  confirmPasswordReset: async (token: string, newPassword: string): Promise<{ message: string }> => {
    const response = await api.post('/auth/password-reset/confirm', { token, new_password: newPassword })
    return response.data
  },
}
