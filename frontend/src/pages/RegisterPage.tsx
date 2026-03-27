import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { register, error, clearError, isLoading } = useAuthStore()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    displayName: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    
    try {
      await register(formData.email, formData.password, formData.displayName)
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
          <h2 className="text-xl font-bold text-slate-800 text-center mb-6">新規登録</h2>
          
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
                placeholder="8文字以上"
                required
                minLength={8}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                表示名（任意）
              </label>
              <input
                type="text"
                value={formData.displayName}
                onChange={(e) => setFormData({ ...formData, displayName: e.target.value })}
                className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                placeholder="ユーザー名"
              />
            </div>
            
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {isLoading ? '登録中...' : '登録'}
            </button>
          </form>
          
          <p className="mt-5 text-center text-sm text-slate-500">
            すでにアカウントをお持ちの方は
            <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium ml-1">ログイン</a>
          </p>
        </div>
      </div>
    </div>
  )
}
