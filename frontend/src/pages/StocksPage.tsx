import { useState } from 'react'
import { Link } from 'react-router-dom'
import { stockApi, Stock } from '../services/stock'

export default function StocksPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Stock[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) return
    setIsLoading(true)
    setError(null)
    setSearched(true)
    try {
      const stocks = await stockApi.searchStocks(query)
      setResults(stocks)
    } catch {
      setError('検索に失敗しました')
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">銘柄検索</h1>

      <div className="flex gap-2 mb-6">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="銘柄コードまたは銘柄名"
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleSearch}
          disabled={isLoading}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? '検索中...' : '検索'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">{error}</div>
      )}

      {searched && results.length === 0 && !isLoading && (
        <p className="text-gray-500 text-center py-8">検索結果がありません</p>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">銘柄コード</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">銘柄名</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 hidden sm:table-cell">市場</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 hidden md:table-cell">セクター</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {results.map((stock) => (
              <tr key={stock.code} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link to={`/stocks/${stock.code}`} className="text-blue-600 hover:text-blue-800 font-medium">
                    {stock.code}
                  </Link>
                </td>
                <td className="px-4 py-3">
                  <Link to={`/stocks/${stock.code}`} className="text-blue-600 hover:text-blue-800">
                    {stock.name}
                  </Link>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 hidden sm:table-cell">{stock.market}</td>
                <td className="px-4 py-3 text-sm text-gray-500 hidden md:table-cell">{stock.sector}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
