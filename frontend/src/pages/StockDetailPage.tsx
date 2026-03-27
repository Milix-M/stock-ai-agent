import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { stockApi } from '../services/stock'
import { watchlistApi } from '../services/watchlist'

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
      // エラーハンドリング
    } finally {
      setWatchlistLoading(false)
    }
  }

  if (isLoading) return <div className="text-center py-8">読み込み中...</div>
  if (error) return <div className="text-center py-8 text-red-600">{error}</div>
  if (!stock) return <div className="text-center py-8">銘柄が見つかりません</div>

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
      <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
        <Link to="/stocks" className="hover:text-blue-600">銘柄検索</Link>
        <span>/</span>
        <span>{stock.code}</span>
      </div>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{stock.name}</h1>
          <p className="text-gray-500">{stock.code} ・ {stock.market || '-'} ・ {stock.sector || '-'}</p>
        </div>
        <button
          onClick={handleToggleWatchlist}
          disabled={watchlistLoading}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            inWatchlist
              ? 'bg-red-100 text-red-700 hover:bg-red-200'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
        >
          {inWatchlist ? 'ウォッチリストから削除' : 'ウォッチリストに追加'}
        </button>
      </div>

      {stock.current_price != null && (
        <div className="mb-6">
          <span className="text-3xl font-bold">¥{formatNumber(stock.current_price)}</span>
          {stock.change != null && (
            <span className={`ml-2 text-lg ${(stock.change ?? 0) >= 0 ? 'text-red-600' : 'text-blue-600'}`}>
              {(stock.change ?? 0) >= 0 ? '+' : ''}{formatNumber(stock.change)}
              ({(stock.change_percent ?? 0) >= 0 ? '+' : ''}{stock.change_percent?.toFixed(2)}%)
            </span>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-semibold mt-1">{value}</p>
    </div>
  )
}
