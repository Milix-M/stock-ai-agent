import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { authApi } from '../services/auth'

export default function PasswordResetConfirmPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState(searchParams.get('token') || '')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (newPassword.length < 8) {
      setError('パスワードは8文字以上必要です')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('パスワードが一致しません')
      return
    }

    if (!token) {
      setError('リセットトークンを入力してください')
      return
    }

    setIsLoading(true)

    try {
      await authApi.confirmPasswordReset(token, newPassword)
      setSuccess(true)
    } catch (err: unknown) {
      const msg = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : undefined
      setError(msg || 'エラーが発生しました')
    } finally {
      setIsLoading(false)
    }
  }

  const CardWrapper = ({ children }: { children: React.ReactNode }) => (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-navy-700 via-navy-700 to-navy-500">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <svg className="w-8 h-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941" />
            </svg>
            <span className="text-2xl font-bold text-white tracking-wide">PICKS</span>
          </div>
        </div>
        <div className="bg-white rounded-xl shadow-xl p-8">
          {children}
        </div>
      </div>
    </div>
  )

  if (success) {
    return (
      <CardWrapper>
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto text-emerald-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-xl font-bold text-slate-800 mb-2">パスワード更新完了</h2>
          <p className="text-sm text-slate-500 mb-6">パスワードが正常に更新されました。</p>
          <button
            onClick={() => navigate('/login')}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition text-sm"
          >
            ログインする
          </button>
        </div>
      </CardWrapper>
    )
  }

  return (
    <CardWrapper>
      <h2 className="text-xl font-bold text-slate-800 text-center mb-6">新しいパスワードを設定</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            リセットトークン
          </label>
          <input
            type="text"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-xs"
            placeholder="リセットトークンを入力"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            新しいパスワード
          </label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="8文字以上"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            パスワード（確認用）
          </label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="もう一度入力"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
        >
          {isLoading ? '更新中...' : 'パスワードを更新'}
        </button>
      </form>
      
      <p className="mt-4 text-center text-sm text-slate-500">
        <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">ログインに戻る</a>
      </p>
    </CardWrapper>
  )
}
