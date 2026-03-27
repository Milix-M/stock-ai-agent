import { useEffect } from 'react'
import { useRecommendationStore } from '../stores/recommendationStore'

export default function RecommendationList() {
  const { recommendations, isLoading, error, fetchRecommendations } = useRecommendationStore()

  useEffect(() => {
    fetchRecommendations()
  }, [fetchRecommendations])

  const getScoreColor = (score: number) => {
    if (score >= 0.9) return 'text-emerald-700 bg-emerald-100'
    if (score >= 0.75) return 'text-blue-700 bg-blue-100'
    return 'text-slate-600 bg-slate-100'
  }

  const safeRecommendations = recommendations || []

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-lg font-bold text-slate-800">本日のレコメンド</h2>
        <button
          onClick={() => fetchRecommendations()}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50"
          disabled={isLoading}
        >
          更新
        </button>
      </div>

      {isLoading && safeRecommendations.length === 0 ? (
        <div className="text-center py-12 text-slate-400">読み込み中...</div>
      ) : error ? (
        <div className="text-center py-8 text-red-600 text-sm">{error}</div>
      ) : safeRecommendations.length === 0 ? (
        <div className="text-center py-12">
          <svg className="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 8.511c.884.284 1.5 1.128 1.5 2.097v4.286c0 1.136-.847 2.1-1.98 2.193-.34.027-.68.052-1.02.072v3.091l-3-3c-1.354 0-2.694-.055-4.02-.163a2.115 2.115 0 01-.825-.242m9.345-8.334a2.126 2.126 0 00-.476-.095 48.64 48.64 0 00-8.048 0c-1.131.094-1.976 1.057-1.976 2.192v4.286c0 .837.46 1.58 1.155 1.951m9.345-8.334V6.637c0-1.621-1.152-3.026-2.76-3.235A48.455 48.455 0 0011.25 3c-2.115 0-4.198.137-6.24.402-1.608.209-2.76 1.614-2.76 3.235v6.226c0 1.621 1.152 3.026 2.76 3.235.577.075 1.157.14 1.74.194V21l4.155-4.155" />
          </svg>
          <p className="text-slate-500 text-sm">レコメンドがありません</p>
          <p className="text-xs text-slate-400 mt-1">投資パターンを作成すると、条件に合った銘柄が表示されます</p>
        </div>
      ) : (
        <div className="space-y-3">
          {safeRecommendations.map((rec, idx) => (
            <div
              key={`${rec.stock_code}-${idx}`}
              className="border border-slate-200 rounded-lg p-4 hover:shadow-md hover:border-slate-300 transition-all duration-150"
            >
              <div className="flex items-start gap-4">
                {/* スコア円形バッジ */}
                <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold ${getScoreColor(rec.match_score)}`}>
                  {Math.round(rec.match_score * 100)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-800">{rec.stock_name}</span>
                    <span className="text-xs text-slate-400">({rec.stock_code})</span>
                    <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-500 rounded font-medium">
                      {rec.pattern_name}
                    </span>
                  </div>

                  <p className="text-sm text-slate-500 mt-1 line-clamp-2">{rec.reason}</p>

                  {rec.matched_criteria.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {rec.matched_criteria.slice(0, 3).map((criteria, cidx) => (
                        <span
                          key={cidx}
                          className="text-xs px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded font-medium"
                        >
                          {criteria}
                        </span>
                      ))}
                    </div>
                  )}

                  {rec.event_keywords && rec.event_keywords.length > 0 && (
                    <div className="mt-1.5 flex flex-wrap gap-1">
                      {rec.event_keywords.map((kw, kidx) => (
                        <span
                          key={kidx}
                          className="text-xs px-2 py-0.5 bg-amber-50 text-amber-700 rounded"
                        >
                          {kw}
                        </span>
                      ))}
                    </div>
                  )}

                  {rec.trend_info && (
                    <div className="mt-1.5 text-xs text-blue-600 font-medium">
                      {rec.trend_info}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
