import { useEffect } from 'react'
import { useRecommendationStore } from '../stores/recommendationStore'

export default function RecommendationList() {
  const { recommendations, isLoading, error, fetchRecommendations } = useRecommendationStore()

  useEffect(() => {
    fetchRecommendations()
  }, [fetchRecommendations])

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-100'
    if (score >= 0.75) return 'text-blue-600 bg-blue-100'
    return 'text-gray-600 bg-gray-100'
  }

  // null/undefined対策
  const safeRecommendations = recommendations || []

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">本日のレコメンド</h2>
        <button
          onClick={() => fetchRecommendations()}
          className="text-sm text-blue-600 hover:text-blue-800"
          disabled={isLoading}
        >
          更新
        </button>
      </div>

      {isLoading && safeRecommendations.length === 0 ? (
        <div className="text-center py-8">読み込み中...</div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">{error}</div>
      ) : safeRecommendations.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">
            レコメンドがありません。
          </p>
          <p className="text-sm text-gray-400 mt-2">
            投資パターンを作成すると、条件に合った銘柄が表示されます。
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {safeRecommendations.map((rec, idx) => (
            <div
              key={`${rec.stock_code}-${idx}`}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-lg">{rec.stock_name}</span>
                    <span className="text-gray-500">({rec.stock_code})</span>
                  </div>
                  
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded ${getScoreColor(rec.match_score)}`}>
                      マッチ度: {Math.round(rec.match_score * 100)}%
                    </span>
                    <span className="text-xs text-gray-500 px-2 py-0.5 bg-gray-100 rounded">
                      {rec.pattern_name}
                    </span>
                  </div>
                </div>
              </div>

              <p className="text-sm text-gray-600 mt-3">{rec.reason}</p>

              {rec.matched_criteria.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1">
                  {rec.matched_criteria.slice(0, 3).map((criteria, cidx) => (
                    <span
                      key={cidx}
                      className="text-xs px-2 py-1 bg-green-50 text-green-700 rounded"
                    >
                      ✓ {criteria}
                    </span>
                  ))}
                </div>
              )}

              {rec.pattern_input && (
                <div className="mt-2 text-xs text-gray-400 italic">
                  検索条件: 「{rec.pattern_input}」
                </div>
              )}

              {rec.event_keywords && rec.event_keywords.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {rec.event_keywords.map((kw, kidx) => (
                    <span
                      key={kidx}
                      className="text-xs px-2 py-1 bg-orange-50 text-orange-600 rounded"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              )}

              {rec.trend_info && (
                <div className="mt-2 text-xs text-blue-600">
                  📈 {rec.trend_info}
                </div>
              )}

              <div className="mt-3 flex gap-2">
                <button className="text-sm text-blue-600 hover:text-blue-800">
                  詳細を見る →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
