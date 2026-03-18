import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import WatchlistComponent from '../components/WatchlistComponent'
import PatternList from '../components/PatternList'
import RecommendationList from '../components/RecommendationList'
import { adminApi } from '../services/admin'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()
  const [isSeeding, setIsSeeding] = useState(false)
  const [seedResult, setSeedResult] = useState<string | null>(null)
  const [isSeeded, setIsSeeded] = useState<boolean | null>(null)
  const [stockCount, setStockCount] = useState(0)

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  // セットアップ状態を確認
  useEffect(() => {
    checkSetupStatus()
  }, [])

  const checkSetupStatus = async () => {
    try {
      const status = await adminApi.getSetupStatus()
      setIsSeeded(status.is_seeded)
      setStockCount(status.stock_count)
    } catch {
      setIsSeeded(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleSeed = async () => {
    if (!confirm('データベースに銘柄データを追加しますか？')) return
    
    setIsSeeding(true)
    setSeedResult(null)
    try {
      const result = await adminApi.seedDatabase()
      setSeedResult(`✅ ${result.created}件の銘柄を追加しました`)
      setIsSeeded(true)
      setStockCount(result.created)
      // 3秒後にリロード
      setTimeout(() => window.location.reload(), 2000)
    } catch (error: any) {
      const message = error.response?.data?.detail || '失敗しました'
      setSeedResult(`❌ ${message}`)
      if (error.response?.status === 400) {
        setIsSeeded(true)
      }
    } finally {
      setIsSeeding(false)
    }
  }

  if (!user) {
    return <div className="min-h-screen flex items-center justify-center">読み込み中...</div>
  }

  // まだ状態確認中
  if (isSeeded === null) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p>セットアップ状態を確認中...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Stock AI Agent</h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user.display_name || user.email}</span>
            <button onClick={handleLogout} className="text-sm text-gray-500 hover:text-gray-700">
              ログアウト
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* 初回セットアップ - 未完了時のみ表示 */}
        {!isSeeded && (
          <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800 mb-2">
              🔧 初回セットアップ: 銘柄データをデータベースに追加してください
            </p>
            <button
              onClick={handleSeed}
              disabled={isSeeding}
              className="text-sm bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isSeeding ? '追加中...' : '銘柄データを追加'}
            </button>
            {seedResult && <p className="mt-2 text-sm">{seedResult}</p>}
          </div>
        )}

        {/* セットアップ完了メッセージ */}
        {isSeeded && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-sm text-green-800">
              ✅ セットアップ完了: {stockCount}件の銘柄データが登録されています
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <RecommendationList />

            <PatternList />
          </div>

          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-md font-semibold mb-4">マーケット概況</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">日経平均</span>
                  <span className="font-medium">-（実装中）</span>
                </div>
              </div>
            </div>

            <WatchlistComponent />
          </div>
        </div>
      </main>
    </div>
  )
}
