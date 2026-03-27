import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import React from 'react'
import StocksPage from '../pages/StocksPage'

// モック: stockApi
vi.mock('../services/stock', () => ({
  stockApi: {
    searchStocks: vi.fn(),
  },
}))

// 型定義
const mockStockApi = await import('../services/stock')

describe('StocksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  const renderWithRouter = (component: React.ReactElement) => {
    return render(
      <BrowserRouter>
        {component}
      </BrowserRouter>
    )
  }

  it('検索入力が表示される', () => {
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    expect(input).toBeInTheDocument()
  })

  it('検索ボタンがクリックできる', async () => {
    const user = userEvent.setup()
    renderWithRouter(<StocksPage />)
    
    const searchButton = screen.getByRole('button', { name: '検索' })
    expect(searchButton).toBeEnabled()
    
    await user.click(searchButton)
    // 空のクエリでは検索が実行されないことを確認
    expect(mockStockApi.stockApi.searchStocks).not.toHaveBeenCalled()
  })

  it('検索クエリ入力後、Enterキーで検索できる', async () => {
    const user = userEvent.setup()
    vi.mocked(mockStockApi.stockApi.searchStocks).mockResolvedValue([] as any)
    
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    await user.type(input, 'トヨタ')
    await user.keyboard('{Enter}')
    
    // APIが呼ばれたことを確認
    expect(mockStockApi.stockApi.searchStocks).toHaveBeenCalledWith('トヨタ')
  })

  it('検索ボタンクリックで検索できる', async () => {
    const user = userEvent.setup()
    vi.mocked(mockStockApi.stockApi.searchStocks).mockResolvedValue([] as any)
    
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    await user.type(input, '7203')
    
    const searchButton = screen.getByRole('button', { name: '検索' })
    await user.click(searchButton)
    
    expect(mockStockApi.stockApi.searchStocks).toHaveBeenCalledWith('7203')
  })

  it('検索結果が表示される', async () => {
    const user = userEvent.setup()
    const mockResults = [
      { code: '7203', name: 'トヨタ自動車', market: '東証プライム', sector: '輸送用機器' },
      { code: '6758', name: 'ソニーグループ', market: '東証プライム', sector: '電気機器' },
    ]
    vi.mocked(mockStockApi.stockApi.searchStocks).mockResolvedValue(mockResults as any)
    
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    await user.type(input, 'トヨタ')
    
    const searchButton = screen.getByRole('button', { name: '検索' })
    await user.click(searchButton)
    
    await waitFor(() => {
      expect(screen.getByText('7203')).toBeInTheDocument()
      expect(screen.getByText('トヨタ自動車')).toBeInTheDocument()
      expect(screen.getByText('6758')).toBeInTheDocument()
      expect(screen.getByText('ソニーグループ')).toBeInTheDocument()
    })
  })

  it('検索結果なしのメッセージが表示される', async () => {
    const user = userEvent.setup()
    vi.mocked(mockStockApi.stockApi.searchStocks).mockResolvedValue([] as any)
    
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    await user.type(input, 'NOTFOUND')
    
    const searchButton = screen.getByRole('button', { name: '検索' })
    await user.click(searchButton)
    
    await waitFor(() => {
      expect(screen.getByText('検索結果がありません')).toBeInTheDocument()
    })
  })

  it('検索中はローディング表示になる', async () => {
    const user = userEvent.setup()
    let resolveSearch: any
    const searchPromise = new Promise((resolve) => {
      resolveSearch = resolve
    })
    vi.mocked(mockStockApi.stockApi.searchStocks).mockReturnValue(searchPromise)
    
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    await user.type(input, 'テスト')
    
    const searchButton = screen.getByRole('button', { name: '検索' })
    await user.click(searchButton)
    
    expect(await screen.findByText('検索中...')).toBeInTheDocument()
    
    resolveSearch([])
    await waitFor(() => {
      expect(screen.queryByText('検索中...')).not.toBeInTheDocument()
    })
  })

  it('検索エラー時にエラーメッセージが表示される', async () => {
    const user = userEvent.setup()
    vi.mocked(mockStockApi.stockApi.searchStocks).mockRejectedValue(new Error('API Error'))
    
    renderWithRouter(<StocksPage />)
    
    const input = screen.getByPlaceholderText('銘柄コードまたは銘柄名')
    await user.type(input, 'テスト')
    
    const searchButton = screen.getByRole('button', { name: '検索' })
    await user.click(searchButton)
    
    await waitFor(() => {
      expect(screen.getByText('検索に失敗しました')).toBeInTheDocument()
    })
  })
})
