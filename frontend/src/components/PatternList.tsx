import { useEffect, useState } from 'react'
import { usePatternStore } from '../stores/patternStore'
import { useRecommendationStore } from '../stores/recommendationStore'
import PatternCreateModal from './PatternCreateModal'

export default function PatternList() {
  const { patterns, isLoading, error, fetchPatterns, deletePattern, togglePattern, clearError } = usePatternStore()
  const { fetchRecommendations } = useRecommendationStore()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  useEffect(() => {
    fetchPatterns()
  }, [fetchPatterns])

  const handleDelete = async (patternId: string) => {
    if (!confirm('このパターンを削除しますか？')) return
    
    setDeletingId(patternId)
    try {
      await deletePattern(patternId)
    } finally {
      setDeletingId(null)
    }
  }

  const handleCreateSuccess = async () => {
    await fetchPatterns()
    setTimeout(() => {
      fetchRecommendations()
    }, 1000)
  }

  const getStrategyLabel = (strategy?: string) => {
    const labels: Record<string, string> = {
      dividend_focus: '高配当',
      growth: '成長株',
      value: 'バリュー',
      technical: 'テクニカル',
      hybrid: '複合',
    }
    return labels[strategy || ''] || 'カスタム'
  }

  const renderFilters = (filters?: any) => {
    if (!filters) return null

    const items = []

    if (filters.per_min !== null && filters.per_min !== undefined && filters.per_max !== null && filters.per_max !== undefined) {
      items.push(`PER: ${filters.per_min}〜${filters.per_max}倍`)
    } else if (filters.per_min !== null && filters.per_min !== undefined) {
      items.push(`PER: ${filters.per_min}倍以上`)
    } else if (filters.per_max !== null && filters.per_max !== undefined) {
      items.push(`PER: ${filters.per_max}倍以下`)
    }

    if (filters.pbr_min !== null && filters.pbr_min !== undefined && filters.pbr_max !== null && filters.pbr_max !== undefined) {
      items.push(`PBR: ${filters.pbr_min}〜${filters.pbr_max}倍`)
    } else if (filters.pbr_min !== null && filters.pbr_min !== undefined) {
      items.push(`PBR: ${filters.pbr_min}倍以上`)
    } else if (filters.pbr_max !== null && filters.pbr_max !== undefined) {
      items.push(`PBR: ${filters.pbr_max}倍以下`)
    }

    if (filters.dividend_yield_min !== null && filters.dividend_yield_min !== undefined && filters.dividend_yield_max !== null && filters.dividend_yield_max !== undefined) {
      items.push(`配当: ${filters.dividend_yield_min}〜${filters.dividend_yield_max}%`)
    } else if (filters.dividend_yield_min !== null && filters.dividend_yield_min !== undefined) {
      items.push(`配当: ${filters.dividend_yield_min}%以上`)
    } else if (filters.dividend_yield_max !== null && filters.dividend_yield_max !== undefined) {
      items.push(`配当: ${filters.dividend_yield_max}%以下`)
    }

    if (filters.market_cap_min !== null && filters.market_cap_min !== undefined && filters.market_cap_max !== null && filters.market_cap_max !== undefined) {
      items.push(`時価総額: ${formatMarketCap(filters.market_cap_min)}〜${formatMarketCap(filters.market_cap_max)}`)
    } else if (filters.market_cap_min !== null && filters.market_cap_min !== undefined) {
      items.push(`時価総額: ${formatMarketCap(filters.market_cap_min)}以上`)
    } else if (filters.market_cap_max !== null && filters.market_cap_max !== undefined) {
      items.push(`時価総額: ${formatMarketCap(filters.market_cap_max)}以下`)
    }

    if (filters.price_change_min !== null && filters.price_change_min !== undefined && filters.price_change_max !== null && filters.price_change_max !== undefined) {
      items.push(`変動率: ${filters.price_change_min}〜${filters.price_change_max}%`)
    } else if (filters.price_change_min !== null && filters.price_change_min !== undefined) {
      items.push(`変動率: ${filters.price_change_min}%以上`)
    } else if (filters.price_change_max !== null && filters.price_change_max !== undefined) {
      items.push(`変動率: ${filters.price_change_max}%以下`)
    }

    return items
  }

  const renderEventInfo = (parsed: any): string | null => {
    const parts: string[] = []
    if (parsed.event_keywords?.length > 0) {
      parts.push(`イベント: ${parsed.event_keywords.join('、')}`)
    }
    if (parsed.affected_sectors?.length > 0) {
      parts.push(`影響セクター: ${parsed.affected_sectors.join('、')}`)
    }
    if (parsed.price_trend) {
      const trendLabels: Record<string, string> = { declining: '下落', rising: '上昇', volatile: 'ボラティリティ高' }
      const periodLabels: Record<string, string> = { '1mo': '1ヶ月', '3mo': '3ヶ月', '6mo': '半年', '1y': '1年' }
      const trendText = trendLabels[parsed.price_trend] || parsed.price_trend
      const periodText = parsed.trend_period ? `（${periodLabels[parsed.trend_period] || parsed.trend_period}）` : ''
      parts.push(`トレンド: ${trendText}${periodText}`)
    }
    return parts.length > 0 ? parts.join(' · ') : null
  }

  const formatMarketCap = (value: number): string => {
    if (value >= 1_000_000_000_000) {
      return `${(value / 1_000_000_000_000).toFixed(1)}兆円`
    } else if (value >= 100_000_000) {
      return `${(value / 100_000_000).toFixed(0)}億円`
    }
    return `${value}円`
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div className="flex justify-between items-center mb-5">
          <h3 className="text-lg font-bold text-slate-800">投資パターン</h3>
          <button
            onClick={() => setIsModalOpen(true)}
            className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            ＋ 新規作成
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
            {error}
            <button onClick={clearError} className="ml-2 text-sm underline">閉じる</button>
          </div>
        )}

        {isLoading && patterns.length === 0 ? (
          <div className="text-center py-12 text-slate-400">読み込み中...</div>
        ) : patterns.length === 0 ? (
          <div className="text-center py-12">
            <svg className="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.431.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.28c-.09.543-.56.941-1.11.941h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <p className="text-slate-500 text-sm mb-3">パターンがありません</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              パターンを作成する
            </button>
          </div>
        ) : (
          <ul className="space-y-3">
            {patterns.map((pattern) => (
              <li key={pattern.id} className="border border-slate-200 rounded-lg p-4 hover:border-slate-300 hover:shadow-sm transition-all">
                <div className="flex justify-between items-start">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-800">{pattern.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        pattern.is_active 
                          ? 'bg-emerald-100 text-emerald-700' 
                          : 'bg-slate-100 text-slate-500'
                      }`}>
                        {pattern.is_active ? '有効' : '無効'}
                      </span>
                    </div>
                    
                    {pattern.description && (
                      <p className="text-sm text-slate-500 mt-1">{pattern.description}</p>
                    )}
                    
                    <div className="flex items-center gap-2 mt-2 flex-wrap">
                      <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded font-medium">
                        {getStrategyLabel(pattern.parsed_filters?.strategy)}
                      </span>
                      <span className="text-xs text-slate-500">
                        {renderFilters(pattern.parsed_filters?.filters) || '条件なし'}{renderEventInfo(pattern.parsed_filters) ? ` · ${renderEventInfo(pattern.parsed_filters)}` : ''}
                      </span>
                      {pattern.parsed_filters?.sectors && pattern.parsed_filters.sectors.length > 0 && (
                        <span className="text-xs px-2 py-0.5 bg-violet-50 text-violet-700 rounded font-medium">
                          {pattern.parsed_filters.sectors.join(' · ')}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4 flex-shrink-0">
                    {/* トグルスイッチ */}
                    <button
                      onClick={() => togglePattern(pattern.id)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors flex-shrink-0 ${
                        pattern.is_active ? 'bg-emerald-500' : 'bg-slate-300'
                      }`}
                    >
                      <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
                        pattern.is_active ? 'translate-x-6' : 'translate-x-1'
                      }`} />
                    </button>

                    <button
                      onClick={() => handleDelete(pattern.id)}
                      disabled={deletingId === pattern.id}
                      className="text-red-400 hover:text-red-600 text-sm p-1 rounded hover:bg-red-50 transition-colors disabled:opacity-50"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                      </svg>
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <PatternCreateModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSuccess={handleCreateSuccess}
      />
    </>
  )
}
