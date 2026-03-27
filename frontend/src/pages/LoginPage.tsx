import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, error, clearError, isLoading } = useAuthStore()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    
    try {
      await login(formData.email, formData.password)
      navigate('/dashboard')
    } catch {
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-navy-700 via-navy-700 to-navy-500">
      <div className="max-w-md w-full">
        {/* ロゴ */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <svg className="w-8 h-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
            </svg>
            <span className="text-2xl font-bold text-white tracking-wide">PICKS</span>
          </div>
          <p className="text-sm text-white/60">AIがあなたの投資をサポート</p>
        </div>

        <div className="bg-white rounded-xl shadow-xl p-8">
          <h2 className="text-xl font-bold text-slate-800 text-center mb-6">ログイン</h2>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
              {error}
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                メールアドレス
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                placeholder="you@example.com"
                required
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                パスワード
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                placeholder="••••••••"
                required
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {isLoading ? 'ログイン中...' : 'ログイン'}
            </button>
          </form>
          
          <p className="mt-5 text-center text-sm text-slate-500">
            アカウントをお持ちでない方は
            <a href="/register" className="text-blue-600 hover:text-blue-700 font-medium ml-1">新規登録</a>
          </p>
          
          <p className="mt-2 text-center text-sm text-slate-500">
            <a href="/password-reset" className="text-blue-600 hover:text-blue-700 font-medium">パスワードをお忘れですか？</a>
          </p>
        </div>
      </div>
    </div>
  )
}
