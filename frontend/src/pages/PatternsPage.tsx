import { useNavigate } from 'react-router-dom'
import PatternList from '../components/PatternList'

export default function PatternsPage() {
  const navigate = useNavigate()

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">パターン管理</h1>
        <button
          onClick={() => navigate('/patterns/new')}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
        >
          + 新規作成
        </button>
      </div>
      <PatternList />
    </div>
  )
}
