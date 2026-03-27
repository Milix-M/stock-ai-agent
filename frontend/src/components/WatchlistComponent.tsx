import { useEffect, useState } from 'react'
import { useWatchlistStore } from '../stores/watchlistStore'
import StockSearchModal from './StockSearchModal'

export default function WatchlistComponent() {
  const { items, isLoading, error, fetchWatchlist, removeFromWatchlist, clearError } = useWatchlistStore()
  const [removingId, setRemovingId] = useState<string | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    fetchWatchlist()
  }, [fetchWatchlist])

  const handleRemove = async (stockCode: string) => {
    setRemovingId(stockCode)
    try {
      await removeFromWatchlist(stockCode)
    } finally {
      setRemovingId(null)
    }
  }

  const handleAddSuccess = () => {
    fetchWatchlist()
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        <div className="flex justify-between items-center p-6 pb-4">
          <h3 className="text-lg font-bold text-slate-800">ウォッチリスト</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 font-medium transition-colors"
            >
              ＋ 追加
            </button>
            <button
              onClick={() => fetchWatchlist()}
              className="text-sm text-slate-500 hover:text-slate-700 font-medium transition-colors"
              disabled={isLoading}
            >
              更新
            </button>
          </div>
        </div>

        {error && (
          <div className="mx-6 mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
            <button onClick={clearError} className="ml-2 text-sm underline">閉じる</button>
          </div>
        )}

        {items.length === 0 ? (
          <div className="text-center py-12 px-6">
            <svg className="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p className="text-slate-500 text-sm mb-3">ウォッチリストは空です</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              銘柄を追加する
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-t border-b border-slate-200 bg-slate-50">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wider">銘柄</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider">株価</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:table-cell">変動率</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">PER</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-500 uppercase tracking-wider hidden md:table-cell">配当</th>
                  <th className="px-6 py-3 text-center text-xs font-semibold text-slate-500 uppercase tracking-wider w-20">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {items.map((item) => (
                  <tr key={item.stock_code} className="hover:bg-slate-50 transition-colors">
                    <td className="px-6 py-3.5">
                      <div className="font-semibold text-slate-800">{item.stock_name}</div>
                      <div className="text-xs text-slate-400">{item.stock_code} ・ {item.market}{item.sector ? ` / ${item.sector}` : ''}</div>
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <span className="font-semibold text-slate-800">
                        {item.current_price !== undefined ? `${item.current_price.toLocaleString()}円` : '-'}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-right hidden sm:table-cell">
                      {item.change_percent !== undefined ? (
                        <span className={`inline-flex items-center gap-0.5 text-sm font-semibold ${item.change_percent >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                          {item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
                        </span>
                      ) : '-'}
                    </td>
                    <td className="px-6 py-3.5 text-right text-sm text-slate-500 hidden md:table-cell">
                      {item.per !== undefined ? `${item.per.toFixed(1)}` : '-'}
                    </td>
                    <td className="px-6 py-3.5 text-right text-sm text-slate-500 hidden md:table-cell">
                      {item.dividend_yield !== undefined ? `${item.dividend_yield.toFixed(1)}%` : '-'}
                    </td>
                    <td className="px-6 py-3.5 text-center">
                      <button
                        onClick={() => handleRemove(item.stock_code)}
                        disabled={removingId === item.stock_code}
                        className="text-xs text-red-500 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition-colors disabled:opacity-50"
                      >
                        {removingId === item.stock_code ? '...' : '削除'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <StockSearchModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onAdd={handleAddSuccess}
      />
    </>
  )
}
