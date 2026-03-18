import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import WatchlistComponent from '../components/WatchlistComponent'
import PatternList from '../components/PatternList'
import RecommendationList from '../components/RecommendationList'
import MarketOverview from '../components/MarketOverview'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login')
    }
  }, [isAuthenticated, navigate])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (!user) {
    return <div className="min-h-screen flex items-center justify-center">読み込み中...</div>
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <RecommendationList />

            <PatternList />
          </div>

          <div className="space-y-6">
            <MarketOverview />

            <WatchlistComponent />
          </div>
        </div>
      </main>
    </div>
  )
}
