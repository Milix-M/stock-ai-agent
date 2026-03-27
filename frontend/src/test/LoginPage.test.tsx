import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import LoginPage from '../pages/LoginPage'

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useNavigate: () => vi.fn(),
}))

describe('LoginPage', () => {
  it('ログインフォームが表示される', () => {
    render(<LoginPage />)
    expect(screen.getByText('ログイン')).toBeInTheDocument()
    expect(screen.getByLabelText(/メール/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/パスワード/i)).toBeInTheDocument()
  })

  it('パスワードリセットリンクがある', () => {
    render(<LoginPage />)
    expect(screen.getByText(/パスワードをお忘れ/i)).toBeInTheDocument()
  })
})
