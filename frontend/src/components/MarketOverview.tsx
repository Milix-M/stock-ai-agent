import { useEffect, useState } from 'react'
import { marketApi, MarketIndex } from '../services/market'

export default function MarketOverview() {
  const [indices, setIndices] = useState<{
    nikkei_225: MarketIndex | null
    dow_jones: MarketIndex | null
  }>({
    nikkei_225: null,
    dow_jones: null,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isFallback, setIsFallback] = useState(false)

  useEffect(() => {
    fetchMarketData()
    // 30秒ごとに更新
    const interval = setInterval(fetchMarketData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchMarketData = async () => {
    try {
      const data = await marketApi.getMarketOverview()
      setIndices(data.indices)
      setIsFallback(data.data_source === 'yahoo_fallback')
    } catch (error) {
      console.error('Failed to fetch market data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatNumber = (num: number) => {
    return num.toLocaleString('ja-JP')
  }

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-red-600'
    if (change < 0) return 'text-green-600'
    return 'text-gray-600'
  }

  const getChangeBg = (change: number) => {
    if (change > 0) return 'bg-red-50'
    if (change < 0) return 'bg-green-50'
    return 'bg-gray-50'
  }

  const renderIndex = (data: MarketIndex | null, label: string) => {
    if (!data) {
      return (
        <div className="py-2">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">{label}</span>
            <span className="text-gray-400">取得中...</span>
          </div>
        </div>
      )
    }

    const isPositive = data.change >= 0

    return (
      <div className={`py-2 px-3 rounded-lg ${getChangeBg(data.change)}`}>
        <div className="flex justify-between items-center">
          <div>
            <span className="font-medium text-gray-800">{data.name}</span>
          </div>
          <div className="text-right">
            <div className="font-bold text-gray-900">
              {formatNumber(data.current)}
            </div>
            <div className={`text-sm ${getChangeColor(data.change)}`}>
              {isPositive ? '+' : ''}{data.change.toFixed(2)} (
              {isPositive ? '+' : ''}{data.change_percent.toFixed(2)}%)
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-md font-semibold mb-4">マーケット概況</h3>
        <div className="space-y-3">
          <div className="h-12 bg-gray-100 rounded animate-pulse"></div>
          <div className="h-12 bg-gray-100 rounded animate-pulse"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-md font-semibold">マーケット概況</h3>
        <button
          onClick={fetchMarketData}
          className="text-xs text-gray-500 hover:text-gray-700"
          disabled={isLoading}
        >
          更新
        </button>
      </div>
      
      <div className="space-y-2">
        {renderIndex(indices.nikkei_225, '日経平均')}
        {renderIndex(indices.dow_jones, 'NYダウ')}
      </div>
      
      <p className="text-xs text-gray-400 mt-3">
        ※ 30秒ごとに自動更新
        {isFallback && <span className="ml-1 text-yellow-600">(デモデータ)</span>}
      </p>
    </div>
  )
}
