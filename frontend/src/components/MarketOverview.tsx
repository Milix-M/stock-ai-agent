import { useEffect, useState } from 'react'
import { marketApi, MarketIndex } from '../services/market'
import { useColorThemeStore, RISE_PRESETS, FALL_PRESETS } from '../stores/colorThemeStore'

export default function MarketOverview() {
  const [indices, setIndices] = useState<{
    nikkei_225: MarketIndex | null
    nikkei_futures: MarketIndex | null
  }>({
    nikkei_225: null,
    nikkei_futures: null,
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isFallback, setIsFallback] = useState(false)

  useEffect(() => {
    fetchMarketData()
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

  const renderIndex = (data: MarketIndex | null, label: string) => {
    const { riseColorId, fallColorId } = useColorThemeStore.getState()
    const riseText = RISE_PRESETS.find(p => p.id === riseColorId)?.textClass || 'text-emerald-600'
    const fallText = FALL_PRESETS.find(p => p.id === fallColorId)?.textClass || 'text-red-600'

    if (!data) {
      return (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
          <p className="text-sm text-slate-500 mb-2">{label}</p>
          <div className="h-5 bg-slate-100 rounded animate-pulse w-24 mb-1" />
          <div className="h-4 bg-slate-100 rounded animate-pulse w-16" />
        </div>
      )
    }

    const isPositive = data.change >= 0

    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
        <p className="text-sm text-slate-500 mb-2">{label}</p>
        <p className="text-xl font-bold text-slate-800">
          {formatNumber(data.current)}
        </p>
        <div className="flex items-center gap-1 mt-1">
          <svg className={`w-4 h-4 ${isPositive ? riseText : fallText}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            {isPositive ? (
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 4.5l15 15m0 0V8.25m0 11.25H8.25" />
            )}
          </svg>
          <span className={`text-sm font-semibold ${isPositive ? riseText : fallText}`}>
            {isPositive ? '+' : ''}{data.change.toFixed(2)}
            <span className="ml-0.5 text-xs font-medium">
              ({isPositive ? '+' : ''}{data.change_percent.toFixed(2)}%)
            </span>
          </span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-sm font-bold text-slate-800 mb-4">マーケット概況</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="h-24 bg-slate-50 rounded-lg animate-pulse" />
          <div className="h-24 bg-slate-50 rounded-lg animate-pulse" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-sm font-bold text-slate-800">マーケット概況</h3>
        <button
          onClick={fetchMarketData}
          className="text-xs text-slate-400 hover:text-slate-600 transition-colors"
          disabled={isLoading}
        >
          更新
        </button>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {renderIndex(indices.nikkei_225, '日経平均')}
        {renderIndex(indices.nikkei_futures, '日経平均先物ミニ')}
      </div>
      
      <p className="text-xs text-slate-400 mt-3">
        ※ 30秒ごとに自動更新
        {isFallback && <span className="ml-1 text-amber-600">(デモデータ)</span>}
      </p>
    </div>
  )
}
