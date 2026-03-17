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
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">ウォッチリスト</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
            >
              ＋ 追加
            </button>
            <button
              onClick={() => fetchWatchlist()}
              className="text-sm text-blue-600 hover:text-blue-800"
              disabled={isLoading}
            >
              更新
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
            <button
              onClick={clearError}
              className="ml-2 text-sm underline"
            >
              閉じる
            </button>
          </div>
        )}

        {items.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">
              ウォッチリストは空です
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              銘柄を追加する
            </button>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {items.map((item) => (
              <li key={item.id} className="py-3 flex justify-between items-center">
                <div>
                  <div className="font-medium">
                    {item.stock.code} - {item.stock.name}
                  </div>
                  <div className="text-sm text-gray-500">
                    {item.stock.market}
                    {item.stock.sector && ` / ${item.stock.sector}`}
                  </div>
                  {item.alert_threshold && (
                    <div className="text-xs text-blue-600">
                      アラート: ±{item.alert_threshold}%
                    </div>
                  )}
                </div>
                <button
                  onClick={() => handleRemove(item.stock.code)}
                  disabled={removingId === item.stock.code}
                  className="text-red-500 hover:text-red-700 text-sm px-3 py-1 border border-red-300 rounded hover:bg-red-50 transition disabled:opacity-50"
                >
                  {removingId === item.stock.code ? '削除中...' : '削除'}
                </button>
              </li>
            ))}
          </ul>
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
