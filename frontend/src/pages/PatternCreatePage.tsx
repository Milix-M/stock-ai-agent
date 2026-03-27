import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { usePatternStore } from '../stores/patternStore'

export default function PatternCreatePage() {
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [step, setStep] = useState<1 | 2>(1)

  const {
    parsePattern,
    createPattern,
    isParsing,
    isLoading,
    error,
    parseResult,
    clearError,
    clearParseResult,
  } = usePatternStore()

  const handleParse = async () => {
    if (!input.trim()) return
    clearError()
    const result = await parsePattern(input)
    if (result) {
      if (!name) setName(generatePatternName(result.parsed))
      setStep(2)
    }
  }

  const generatePatternName = (parsed: any): string => {
    const filters = parsed.filters || {}
    const sectors = parsed.sectors || []
    const strategy = parsed.strategy || 'hybrid'
    const parts: string[] = []
    const strategyLabels: Record<string, string> = {
      dividend_focus: '高配当', growth: '成長', value: '割安', technical: 'テクニカル', hybrid: '複合',
    }
    if (strategyLabels[strategy]) parts.push(strategyLabels[strategy])
    if (sectors.length > 0) parts.push(sectors[0])
    if (typeof filters.per_max === 'number' && filters.per_max <= 20) parts.push(`PER${filters.per_max}倍以下`)
    if (typeof filters.dividend_yield_min === 'number' && filters.dividend_yield_min >= 2) parts.push(`配当${filters.dividend_yield_min}%以上`)
    if (typeof filters.pbr_max === 'number' && filters.pbr_max <= 2) parts.push(`PBR${filters.pbr_max}倍以下`)
    return parts.length === 0 ? 'カスタムパターン' : parts.join('・') + 'パターン'
  }

  const handleCreate = async () => {
    if (!name.trim() || !parseResult) return
    try {
      await createPattern(name, description, input, parseResult.parsed)
      navigate('/patterns')
    } catch {
      // ストアでエラー処理
    }
  }

  const renderFilters = () => {
    if (!parseResult?.parsed?.filters) return null
    const filters = parseResult.parsed.filters
    const items: string[] = []
    const addRange = (key: string, unit: string) => {
      const min = filters[`${key}_min`]
      const max = filters[`${key}_max`]
      if (min != null && max != null) items.push(`${key.toUpperCase()}: ${min}〜${max}${unit}`)
      else if (min != null) items.push(`${key.toUpperCase()}: ${min}${unit}以上`)
      else if (max != null) items.push(`${key.toUpperCase()}: ${max}${unit}以下`)
    }
    addRange('per', '倍')
    addRange('pbr', '倍')
    addRange('dividend_yield', '%')
    const ek = parseResult.parsed.event_keywords
    if (ek?.length) items.push(`関連イベント: ${ek.join('、')}`)
    const trend = parseResult.parsed.price_trend
    if (trend) {
      const tl: Record<string, string> = { declining: '下落', rising: '上昇', volatile: 'ボラティリティ高' }
      items.push(`トレンド: ${tl[trend] || trend}`)
    }
    return items
  }

  return (
    <div className="max-w-lg">
      <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
        <button onClick={() => navigate('/patterns')} className="hover:text-blue-600">パターン管理</button>
        <span>/</span>
        <span>新規作成</span>
      </div>

      <h1 className="text-2xl font-bold mb-6">投資パターンを作成</h1>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">{error}</div>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        {step === 1 ? (
          <>
            <p className="text-gray-600 mb-4">
              自然言語であなたの投資基準を教えてください。
              <br />
              例：「高配当株でPER15倍以下、配当利回り3%以上」
            </p>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="高配当株でPER15倍以下、配当利回り3%以上..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 min-h-[100px]"
            />
            <div className="flex gap-2 mt-4">
              <button
                onClick={() => navigate('/patterns')}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                キャンセル
              </button>
              <button
                onClick={handleParse}
                disabled={!input.trim() || isParsing}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {isParsing ? '解析中...' : '次へ'}
              </button>
            </div>
          </>
        ) : parseResult ? (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">パターン名</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">説明（任意）</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="このパターンについてのメモ..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <h4 className="font-medium mb-2">解析結果</h4>
              {parseResult.parsed?.strategy && (
                <p className="text-sm text-gray-600 mb-2">戦略: {parseResult.parsed.strategy}</p>
              )}
              {renderFilters()?.map((f, i) => (
                <p key={i} className="text-sm text-gray-600">• {f}</p>
              ))}
              {parseResult.parsed?.keywords && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {parseResult.parsed.keywords?.map((kw, i) => (
                    <span key={i} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{kw}</span>
                  ))}
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <button onClick={() => setStep(1)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                戻る
              </button>
              <button
                onClick={handleCreate}
                disabled={!name.trim() || isLoading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
              >
                {isLoading ? '作成中...' : '作成'}
              </button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  )
}
