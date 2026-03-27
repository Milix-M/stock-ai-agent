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
      <h1 className="text-xl font-bold text-slate-800 mb-6">銘柄検索</h1>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-6">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <svg className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
            </svg>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="銘柄コードまたは銘柄名を入力"
              className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium text-sm transition-colors"
          >
            {isLoading ? '検索中...' : '検索'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">{error}</div>
      )}

      {searched && results.length === 0 && !isLoading && (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 text-center py-16">
          <p className="text-slate-400 text-sm">検索結果がありません</p>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">銘柄コード</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">銘柄名</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">市場</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">セクター</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {results.map((stock) => (
              <tr key={stock.code} className="hover:bg-slate-50 transition-colors">
                <td className="px-6 py-3">
                  <Link to={`/stocks/${stock.code}`} className="text-blue-600 hover:text-blue-700 font-semibold text-sm">
                    {stock.code}
                  </Link>
                </td>
                <td className="px-6 py-3">
                  <Link to={`/stocks/${stock.code}`} className="text-slate-700 hover:text-slate-900 text-sm">
                    {stock.name}
                  </Link>
                </td>
                <td className="px-6 py-3 text-sm text-slate-500 hidden sm:table-cell">{stock.market}</td>
                <td className="px-6 py-3 text-sm text-slate-500 hidden md:table-cell">{stock.sector}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
