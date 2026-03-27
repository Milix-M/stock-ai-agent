import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../services/auth'

export default function PasswordResetRequestPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [resetToken, setResetToken] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')
    
    try {
      const result = await authApi.requestPasswordReset(email)
      if (result.reset_token) {
        setResetToken(result.reset_token)
      }
    } catch {
      setError('エラーが発生しました。しばらく待ってから再度お試しください。')
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

  if (resetToken) {
    return (
      <CardWrapper>
        <h2 className="text-xl font-bold text-slate-800 text-center mb-4">リセットトークン発行完了</h2>
        <p className="text-sm text-slate-500 mb-4 text-center">開発モード：以下のトークンをコピーしてパスワードリセット確認画面で使用してください。</p>
        <div className="bg-slate-50 border border-slate-200 p-3 rounded-lg mb-4 break-all text-xs font-mono text-slate-700">
          {resetToken}
        </div>
        <button
          onClick={() => navigate(`/password-reset/confirm?token=${encodeURIComponent(resetToken)}`)}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition text-sm"
        >
          パスワードをリセットする
        </button>
        <p className="mt-4 text-center text-sm text-slate-500">
          <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">ログインに戻る</a>
        </p>
      </CardWrapper>
    )
  }

  return (
    <CardWrapper>
      <h2 className="text-xl font-bold text-slate-800 text-center mb-6">パスワードリセット</h2>
      
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
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            placeholder="you@example.com"
            required
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
        >
          {isLoading ? '送信中...' : 'リセットメールを送信'}
        </button>
      </form>
      
      <p className="mt-4 text-center text-sm text-slate-500">
        <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium">ログインに戻る</a>
      </p>
    </CardWrapper>
  )
}
