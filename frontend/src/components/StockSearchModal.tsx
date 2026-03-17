import { useState } from 'react'
import { stockApi, Stock } from '../services/stock'
import { watchlistApi } from '../services/watchlist'

interface StockSearchModalProps {
  isOpen: boolean
  onClose: () => void
  onAdd: () => void
}

export default function StockSearchModal({ isOpen, onClose, onAdd }: StockSearchModalProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Stock[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [addingId, setAddingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async () => {
    if (!query.trim()) return
    
    setIsLoading(true)
    setError(null)
    try {
      const stocks = await stockApi.searchStocks(query)
      setResults(stocks)
    } catch (err: any) {
      setError('検索に失敗しました')
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleAdd = async (stockCode: string) => {
    setAddingId(stockCode)
    setError(null)
    try {
      await watchlistApi.addToWatchlist(stockCode)
      onAdd()
      onClose()
    } catch (err: any) {
      setError(err.response?.data?.detail || '追加に失敗しました')
    } finally {
      setAddingId(null)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-lg w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">銘柄を追加</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div className="flex gap-2 mb-4">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="銘柄コードまたは銘柄名"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? '検索中...' : '検索'}
          </button>
        </div>

        <div className="max-h-64 overflow-y-auto">
          {results.length === 0 ? (
            <p className="text-gray-500 text-center py-4">
              {isLoading ? '検索中...' : '検索結果がありません'}
            </p>
          ) : (
            <ul className="divide-y divide-gray-200">
              {results.map((stock) => (
                <li
                  key={stock.id}
                  className="py-3 flex justify-between items-center"
                >
                  <div>
                    <div className="font-medium">
                      {stock.code} - {stock.name}
                    </div>
                    <div className="text-sm text-gray-500">
                      {stock.market}
                      {stock.sector && ` / ${stock.sector}`}
                    </div>
                  </div>
                  <button
                    onClick={() => handleAdd(stock.code)}
                    disabled={addingId === stock.code}
                    className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50"
                  >
                    {addingId === stock.code ? '追加中...' : '追加'}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
