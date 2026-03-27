import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import PatternCreatePage from '../pages/PatternCreatePage'

vi.mock('../stores/authStore', () => ({
  useAuthStore: () => ({ isAuthenticated: true, user: { email: 'test@test.com' } })
}))

vi.mock('../stores/patternStore', () => ({
  usePatternStore: () => ({
    parsePattern: vi.fn(),
    createPattern: vi.fn(),
    isParsing: false,
    isLoading: false,
    error: null,
    parseResult: null,
    clearError: vi.fn(),
    clearParseResult: vi.fn(),
  })
}))

describe('PatternCreatePage', () => {
  it('入力フォームが表示される', () => {
    render(<PatternCreatePage />, { wrapper: MemoryRouter })
    expect(screen.getByPlaceholderText(/投資条件/i)).toBeInTheDocument()
  })
})
