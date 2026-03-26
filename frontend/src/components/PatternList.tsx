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
    // パターンリストを更新
    await fetchPatterns()
    // レコメンドを更新（少し遅延させてバックエンドの処理完了を待つ）
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

    // PER条件
    if (filters.per_min !== null && filters.per_min !== undefined && filters.per_max !== null && filters.per_max !== undefined) {
      items.push(`PER: ${filters.per_min}〜${filters.per_max}倍`)
    } else if (filters.per_min !== null && filters.per_min !== undefined) {
      items.push(`PER: ${filters.per_min}倍以上`)
    } else if (filters.per_max !== null && filters.per_max !== undefined) {
      items.push(`PER: ${filters.per_max}倍以下`)
    }

    // PBR条件
    if (filters.pbr_min !== null && filters.pbr_min !== undefined && filters.pbr_max !== null && filters.pbr_max !== undefined) {
      items.push(`PBR: ${filters.pbr_min}〜${filters.pbr_max}倍`)
    } else if (filters.pbr_min !== null && filters.pbr_min !== undefined) {
      items.push(`PBR: ${filters.pbr_min}倍以上`)
    } else if (filters.pbr_max !== null && filters.pbr_max !== undefined) {
      items.push(`PBR: ${filters.pbr_max}倍以下`)
    }

    // 配当利回り条件
    if (filters.dividend_yield_min !== null && filters.dividend_yield_min !== undefined && filters.dividend_yield_max !== null && filters.dividend_yield_max !== undefined) {
      items.push(`配当: ${filters.dividend_yield_min}〜${filters.dividend_yield_max}%`)
    } else if (filters.dividend_yield_min !== null && filters.dividend_yield_min !== undefined) {
      items.push(`配当: ${filters.dividend_yield_min}%以上`)
    } else if (filters.dividend_yield_max !== null && filters.dividend_yield_max !== undefined) {
      items.push(`配当: ${filters.dividend_yield_max}%以下`)
    }

    // 時価総額条件
    if (filters.market_cap_min !== null && filters.market_cap_min !== undefined && filters.market_cap_max !== null && filters.market_cap_max !== undefined) {
      items.push(`時価総額: ${formatMarketCap(filters.market_cap_min)}〜${formatMarketCap(filters.market_cap_max)}`)
    } else if (filters.market_cap_min !== null && filters.market_cap_min !== undefined) {
      items.push(`時価総額: ${formatMarketCap(filters.market_cap_min)}以上`)
    } else if (filters.market_cap_max !== null && filters.market_cap_max !== undefined) {
      items.push(`時価総額: ${formatMarketCap(filters.market_cap_max)}以下`)
    }

    // 株価変動率条件
    if (filters.price_change_min !== null && filters.price_change_min !== undefined && filters.price_change_max !== null && filters.price_change_max !== undefined) {
      items.push(`変動率: ${filters.price_change_min}〜${filters.price_change_max}%`)
    } else if (filters.price_change_min !== null && filters.price_change_min !== undefined) {
      items.push(`変動率: ${filters.price_change_min}%以上`)
    } else if (filters.price_change_max !== null && filters.price_change_max !== undefined) {
      items.push(`変動率: ${filters.price_change_max}%以下`)
    }

    return items.length > 0 ? items.join(' · ') : '条件なし'
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
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">投資パターン</h3>
          <button
            onClick={() => setIsModalOpen(true)}
            className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
          >
            ＋ 新規作成
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
            <button onClick={clearError} className="ml-2 text-sm underline">閉じる</button>
          </div>
        )}

        {isLoading && patterns.length === 0 ? (
          <div className="text-center py-4">読み込み中...</div>
        ) : patterns.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">パターンがありません</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="text-blue-600 hover:text-blue-800 underline"
            >
              パターンを作成する
            </button>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {patterns.map((pattern) => (
              <li key={pattern.id} className="py-4">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{pattern.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        pattern.is_active 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        {pattern.is_active ? '有効' : '無効'}
                      </span>
                    </div>
                    
                    {pattern.description && (
                      <p className="text-sm text-gray-500 mt-1">{pattern.description}</p>
                    )}
                    
                    <div className="flex items-center gap-2 mt-2 text-sm text-gray-600">
                      <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">
                        {getStrategyLabel(pattern.parsed_filters?.strategy)}
                      </span>
                      <span>{renderFilters(pattern.parsed_filters?.filters)}</span>
                      {pattern.parsed_filters?.sectors && pattern.parsed_filters.sectors.length > 0 && (
                        <span className="px-2 py-0.5 bg-purple-50 text-purple-700 rounded text-xs">
                          {pattern.parsed_filters.sectors.join(' · ')}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => togglePattern(pattern.id)}
                      className={`text-sm px-3 py-1 rounded ${
                        pattern.is_active
                          ? 'text-gray-600 hover:bg-gray-100'
                          : 'text-green-600 hover:bg-green-50'
                      }`}
                    >
                      {pattern.is_active ? '無効化' : '有効化'}
                    </button>
                    
                    <button
                      onClick={() => handleDelete(pattern.id)}
                      disabled={deletingId === pattern.id}
                      className="text-red-500 hover:text-red-700 text-sm px-3 py-1"
                    >
                      {deletingId === pattern.id ? '削除中...' : '削除'}
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
