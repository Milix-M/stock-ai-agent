import { useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function HomePage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-gradient-to-br from-navy-700 via-navy-700 to-navy-500">
      <div className="text-center">
        <div className="inline-flex items-center gap-3 mb-4">
          <svg className="w-10 h-10 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
          </svg>
          <h1 className="text-4xl font-bold text-white tracking-wide">
            PICKS
          </h1>
        </div>
        <p className="text-white/60 mb-8 text-sm">
          AIが株価を監視し、あなたの投資パターンに合った銘柄を提案
        </p>
        <div className="space-x-3">
          <Link
            to="/login"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition text-sm"
          >
            ログイン
          </Link>
          <Link
            to="/register"
            className="inline-block bg-white/10 text-white border border-white/20 px-6 py-3 rounded-lg font-medium hover:bg-white/20 transition text-sm backdrop-blur-sm"
          >
            新規登録
          </Link>
        </div>
      </div>
    </div>
  )
}
