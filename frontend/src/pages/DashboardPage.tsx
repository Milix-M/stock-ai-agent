import RecommendationList from '../components/RecommendationList'
import MarketOverview from '../components/MarketOverview'

export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">ダッシュボード</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <RecommendationList />
        </div>
        <div>
          <MarketOverview />
        </div>
      </div>
    </div>
  )
}
