import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import LoginPage from '../pages/LoginPage'

// モック: authStore
const mockAuthStore = {
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  clearError: vi.fn(),
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
}

vi.mock('../stores/authStore', () => ({
  useAuthStore: () => mockAuthStore,
}))

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAuthStore.isLoading = false
    mockAuthStore.error = null
    mockAuthStore.isAuthenticated = false
  })

  const renderWithRouter = (component: React.ReactElement) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    )
  }

  it('ログインフォームが表示される', () => {
    renderWithRouter(<LoginPage />)
    
    expect(screen.getByText('ログイン')).toBeInTheDocument()
    expect(screen.getByLabelText('メールアドレス')).toBeInTheDocument()
    expect(screen.getByLabelText('パスワード')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'ログイン' })).toBeInTheDocument()
  })

  it('メールアドレス入力が表示される', () => {
    renderWithRouter(<LoginPage />)
    
    const emailInput = screen.getByLabelText('メールアドレス')
    expect(emailInput).toBeInTheDocument()
    expect(emailInput).toHaveAttribute('type', 'email')
    expect(emailInput).toHaveAttribute('placeholder', 'you@example.com')
  })

  it('パスワード入力が表示される', () => {
    renderWithRouter(<LoginPage />)
    
    const passwordInput = screen.getByLabelText('パスワード')
    expect(passwordInput).toBeInTheDocument()
    expect(passwordInput).toHaveAttribute('type', 'password')
  })

  it('ログインボタンがクリックできる', async () => {
    const user = userEvent.setup()
    renderWithRouter(<LoginPage />)
    
    const loginButton = screen.getByRole('button', { name: 'ログイン' })
    expect(loginButton).toBeEnabled()
    
    await user.click(loginButton)
    // 空のフォームなのでログインは実行されない
    expect(mockAuthStore.login).not.toHaveBeenCalled()
  })

  it('有効な情報でログインできる', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockResolvedValue(undefined)
    
    renderWithRouter(<LoginPage />)
    
    const emailInput = screen.getByLabelText('メールアドレス')
    const passwordInput = screen.getByLabelText('パスワード')
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    const loginButton = screen.getByRole('button', { name: 'ログイン' })
    await user.click(loginButton)
    
    expect(mockAuthStore.login).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('Enterキーでフォームを送信できる', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockResolvedValue(undefined)
    
    renderWithRouter(<LoginPage />)
    
    const emailInput = screen.getByLabelText('メールアドレス')
    const passwordInput = screen.getByLabelText('パスワード')
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    await user.keyboard('{Enter}')
    
    expect(mockAuthStore.login).toHaveBeenCalledWith('test@example.com', 'password123')
  })

  it('必須フィールドのバリデーション（空メール）', async () => {
    const user = userEvent.setup()
    renderWithRouter(<LoginPage />)
    
    const emailInput = screen.getByLabelText('メールアドレス')
    const passwordInput = screen.getByLabelText('パスワード')
    
    await user.type(passwordInput, 'password123')
    
    const loginButton = screen.getByRole('button', { name: 'ログイン' })
    await user.click(loginButton)
    
    // HTML5バリデーションでフォームが送信されない
    expect(mockAuthStore.login).not.toHaveBeenCalled()
  })

  it('必須フィールドのバリデーション（空パスワード）', async () => {
    const user = userEvent.setup()
    renderWithRouter(<LoginPage />)
    
    const emailInput = screen.getByLabelText('メールアドレス')
    
    await user.type(emailInput, 'test@example.com')
    
    const loginButton = screen.getByRole('button', { name: 'ログイン' })
    await user.click(loginButton)
    
    expect(mockAuthStore.login).not.toHaveBeenCalled()
  })

  it('ログイン中はボタンが無効', async () => {
    mockAuthStore.isLoading = true
    const user = userEvent.setup()
    
    renderWithRouter(<LoginPage />)
    
    const loginButton = screen.getByRole('button', { name: 'ログイン' })
    expect(loginButton).toBeDisabled()
    
    const emailInput = screen.getByLabelText('メールアドレス')
    const passwordInput = screen.getByLabelText('パスワード')
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    await user.click(loginButton)
    
    expect(mockAuthStore.login).not.toHaveBeenCalled()
  })

  it('エラーが表示される', () => {
    mockAuthStore.error = 'メールアドレスまたはパスワードが間違っています'
    
    renderWithRouter(<LoginPage />)
    
    expect(screen.getByText('メールアドレスまたはパスワードが間違っています')).toBeInTheDocument()
  })

  it('新規登録リンクが表示される', () => {
    renderWithRouter(<LoginPage />)
    
    const registerLink = screen.getByText('新規登録')
    expect(registerLink).toBeInTheDocument()
    expect(registerLink.closest('a')).toHaveAttribute('href', '/register')
  })

  it('パスワードリセットリンクが表示される', () => {
    renderWithRouter(<LoginPage />)
    
    const resetLink = screen.getByText('パスワードをお忘れですか？')
    expect(resetLink).toBeInTheDocument()
    expect(resetLink.closest('a')).toHaveAttribute('href', '/password-reset')
  })

  it('ログイン成功後、ダッシュボードにリダイレクトされる', async () => {
    const user = userEvent.setup()
    mockAuthStore.login.mockImplementation(async () => {
      mockAuthStore.isAuthenticated = true
      mockAuthStore.user = { id: '1', email: 'test@example.com' }
    })
    
    // 注: 実際のテストではルーティングのモックが必要
    // ここではlogin関数が呼ばれることだけを確認
    renderWithRouter(<LoginPage />)
    
    const emailInput = screen.getByLabelText('メールアドレス')
    const passwordInput = screen.getByLabelText('パスワード')
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    const loginButton = screen.getByRole('button', { name: 'ログイン' })
    await user.click(loginButton)
    
    expect(mockAuthStore.login).toHaveBeenCalledWith('test@example.com', 'password123')
  })
})
