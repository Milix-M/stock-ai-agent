import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import StocksPage from '../pages/StocksPage'

vi.mock('../stores/authStore', () => ({
  useAuthStore: () => ({ isAuthenticated: true, user: { email: 'test@test.com' } })
}))

describe('StocksPage', () => {
  it('検索フォームが表示される', () => {
    render(<StocksPage />, { wrapper: MemoryRouter })
    expect(screen.getByPlaceholderText(/銘柄/i)).toBeInTheDocument()
  })
})
