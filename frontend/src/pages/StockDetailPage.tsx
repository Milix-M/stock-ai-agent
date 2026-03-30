import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { stockApi } from '../services/stock'
import { watchlistApi } from '../services/watchlist'
import { useColorThemeStore, RISE_PRESETS, FALL_PRESETS } from '../stores/colorThemeStore'

interface StockDetail {
  code: string
  name: string
  market?: string
  sector?: string
  current_price?: number
  open?: number
  high?: number
  low?: number
  volume?: number
  change?: number
  change_percent?: number
  per?: number
  pbr?: number
  dividend_yield?: number
  market_cap?: number
}

export default function StockDetailPage() {
  const { code } = useParams<{ code: string }>()
  const [stock, setStock] = useState<StockDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [inWatchlist, setInWatchlist] = useState(false)
  const [watchlistLoading, setWatchlistLoading] = useState(false)

  useEffect(() => {
    if (!code) return
    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const detail = await stockApi.getStockDetail(code)
        setStock(detail)
      } catch {
        setError('銘柄情報の取得に失敗しました')
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [code])

  useEffect(() => {
    if (!code) return
    watchlistApi.checkWatchlist(code).then((res) => setInWatchlist(res.in_watchlist)).catch(() => {})
  }, [code])

  const handleToggleWatchlist = async () => {
    if (!code) return
    setWatchlistLoading(true)
    try {
      if (inWatchlist) {
        await watchlistApi.removeFromWatchlist(code)
        setInWatchlist(false)
      } else {
        await watchlistApi.addToWatchlist(code)
        setInWatchlist(true)
      }
    } catch {
    } finally {
      setWatchlistLoading(false)
    }
  }

  if (isLoading) return <div className="text-center py-16 text-slate-400">読み込み中...</div>
  if (error) return <div className="text-center py-16 text-red-600 text-sm">{error}</div>
  if (!stock) return <div className="text-center py-16 text-slate-400">銘柄が見つかりません</div>

  const formatNumber = (n: number | undefined) => n != null ? n.toLocaleString() : '-'
  const formatYield = (n: number | undefined) => n != null ? `${n.toFixed(2)}%` : '-'
  const formatCap = (n: number | undefined) => {
    if (n == null) return '-'
    if (n >= 1e12) return `${(n / 1e12).toFixed(1)}兆円`
    if (n >= 1e8) return `${(n / 1e8).toFixed(1)}億円`
    return `${(n / 1e6).toFixed(1)}百万円`
  }

  return (
    <div>
      <div className="flex items-center gap-2 text-sm text-slate-400 mb-6">
        <Link to="/stocks" className="hover:text-blue-600 transition-colors">銘柄検索</Link>
        <span>/</span>
        <span className="text-slate-600">{stock.code}</span>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">{stock.name}</h1>
            <p className="text-sm text-slate-500 mt-1">{stock.code} ・ {stock.market || '-'} ・ {stock.sector || '-'}</p>
            {stock.current_price != null && (
              <div className="mt-3 flex items-center gap-3">
                <span className="text-3xl font-bold text-slate-900">¥{formatNumber(stock.current_price)}</span>
                {stock.change_percent != null && (
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-sm font-semibold ${
                    stock.change_percent >= 0 ? (RISE_PRESETS.find(p => p.id === useColorThemeStore.getState().riseColorId)?.bgTextClass || 'bg-emerald-100 text-emerald-700') : (FALL_PRESETS.find(p => p.id === useColorThemeStore.getState().fallColorId)?.bgTextClass || 'bg-red-100 text-red-700')
                  }`}>
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                      {stock.change_percent >= 0 ? (
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                      ) : (
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 4.5l15 15m0 0V8.25m0 11.25H8.25" />
                      )}
                    </svg>
                    {stock.change_percent >= 0 ? '+' : ''}{stock.change_percent.toFixed(2)}%
                  </span>
                )}
              </div>
            )}
          </div>
          <button
            onClick={handleToggleWatchlist}
            disabled={watchlistLoading}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex-shrink-0 ${
              inWatchlist
                ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {inWatchlist ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        <InfoCard label="始値" value={`¥${formatNumber(stock.open)}`} />
        <InfoCard label="高値" value={`¥${formatNumber(stock.high)}`} />
        <InfoCard label="安値" value={`¥${formatNumber(stock.low)}`} />
        <InfoCard label="出来高" value={formatNumber(stock.volume)} />
        <InfoCard label="PER" value={stock.per != null ? `${stock.per.toFixed(2)}倍` : '-'} />
        <InfoCard label="PBR" value={stock.pbr != null ? `${stock.pbr.toFixed(2)}倍` : '-'} />
        <InfoCard label="配当利回り" value={formatYield(stock.dividend_yield)} />
        <InfoCard label="時価総額" value={formatCap(stock.market_cap)} />
      </div>
    </div>
  )
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-4">
      <p className="text-xs text-slate-400 font-medium">{label}</p>
      <p className="text-base font-semibold text-slate-800 mt-1">{value}</p>
    </div>
  )
}
