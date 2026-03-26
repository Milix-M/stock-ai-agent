import { useState } from 'react'
import { usePatternStore } from '../stores/patternStore'

interface PatternCreateModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function PatternCreateModal({ isOpen, onClose, onSuccess }: PatternCreateModalProps) {
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
    clearParseResult
  } = usePatternStore()

  const handleParse = async () => {
    if (!input.trim()) return
    clearError()
    
    const result = await parsePattern(input)
    if (result) {
      // 自動的に名前を生成
      if (!name) {
        const autoName = generatePatternName(result.parsed)
        setName(autoName)
      }
      setStep(2)
    }
  }

  const generatePatternName = (parsed: any): string => {
    const filters = parsed.filters || {}
    const sectors = parsed.sectors || []
    const strategy = parsed.strategy || 'hybrid'

    const parts: string[] = []

    // 戦略に基づく接頭辞
    const strategyLabels: Record<string, string> = {
      dividend_focus: '高配当',
      growth: '成長',
      value: '割安',
      technical: 'テクニカル',
      hybrid: '複合'
    }

    if (strategyLabels[strategy]) {
      parts.push(strategyLabels[strategy])
    }

    // セクター情報
    if (sectors.length > 0) {
      parts.push(sectors[0])
    }

    // 主要な条件を追加（nullチェック付き）
    if (typeof filters.per_max === 'number' && !isNaN(filters.per_max) && filters.per_max <= 20) {
      parts.push(`PER${filters.per_max}倍以下`)
    }
    if (typeof filters.dividend_yield_min === 'number' && !isNaN(filters.dividend_yield_min) && filters.dividend_yield_min >= 2) {
      parts.push(`配当${filters.dividend_yield_min}%以上`)
    }
    if (typeof filters.pbr_max === 'number' && !isNaN(filters.pbr_max) && filters.pbr_max <= 2) {
      parts.push(`PBR${filters.pbr_max}倍以下`)
    }

    // 名前が空の場合はデフォルト
    if (parts.length === 0) {
      return 'カスタムパターン'
    }

    return parts.join('・') + 'パターン'
  }

  const handleCreate = async () => {
    if (!name.trim() || !parseResult) return
    
    try {
      await createPattern(name, description, input, parseResult.parsed)
      onSuccess()
      handleClose()
    } catch {
      // エラーはストアで処理
    }
  }

  const handleClose = () => {
    setInput('')
    setName('')
    setDescription('')
    setStep(1)
    clearParseResult()
    clearError()
    onClose()
  }

  const renderFilters = () => {
    if (!parseResult?.parsed?.filters) return null

    const filters = parseResult.parsed.filters
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
      items.push(`配当利回り: ${filters.dividend_yield_min}〜${filters.dividend_yield_max}%`)
    } else if (filters.dividend_yield_min !== null && filters.dividend_yield_min !== undefined) {
      items.push(`配当利回り: ${filters.dividend_yield_min}%以上`)
    } else if (filters.dividend_yield_max !== null && filters.dividend_yield_max !== undefined) {
      items.push(`配当利回り: ${filters.dividend_yield_max}%以下`)
    }

    // 時価総額条件
    if (filters.market_cap_min !== null && filters.market_cap_min !== undefined && filters.market_cap_max !== null && filters.market_cap_max !== undefined) {
      items.push(`時価総額: ${filters.market_cap_min}〜${filters.market_cap_max}`)
    } else if (filters.market_cap_min !== null && filters.market_cap_min !== undefined) {
      items.push(`時価総額: ${filters.market_cap_min}以上`)
    } else if (filters.market_cap_max !== null && filters.market_cap_max !== undefined) {
      items.push(`時価総額: ${filters.market_cap_max}以下`)
    }

    return items
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-lg w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">
            {step === 1 ? '投資パターンを作成' : 'パターンを確認'}
          </h2>
          <button onClick={handleClose} className="text-gray-500 hover:text-gray-700 text-2xl">
            ×
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

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
                onClick={handleClose}
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
        ) : (
          <>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                パターン名
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                説明（任意）
              </label>
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
              
              {parseResult?.parsed?.strategy && (
                <p className="text-sm text-gray-600 mb-2">
                  戦略: {parseResult.parsed.strategy}
                </p>
              )}
              
              {renderFilters().length > 0 && (
                <div className="space-y-1">
                  {renderFilters().map((filter, idx) => (
                    <p key={idx} className="text-sm text-gray-600">• {filter}</p>
                  ))}
                </div>
              )}
              
              {parseResult?.parsed?.keywords && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {parseResult.parsed.keywords?.map((keyword, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setStep(1)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
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
        )}
      </div>
    </div>
  )
}
