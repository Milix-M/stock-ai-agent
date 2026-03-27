import RecommendationList from '../components/RecommendationList'
import MarketOverview from '../components/MarketOverview'

export default function DashboardPage() {
  return (
    <div>
      <h1 className="text-xl font-bold text-slate-800 mb-6">ダッシュボード</h1>
      {/* 市場概要 */}
      <div className="mb-6">
        <MarketOverview />
      </div>
      {/* レコメンド */}
      <div className="lg:max-w-4xl">
        <RecommendationList />
      </div>
    </div>
  )
}
