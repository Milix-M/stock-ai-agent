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

  if (resetToken) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-center mb-6">リセットトークン発行完了</h2>
          <p className="text-gray-600 mb-4 text-center">開発モード：以下のトークンをコピーしてパスワードリセット確認画面で使用してください。</p>
          <div className="bg-gray-100 p-3 rounded-lg mb-4 break-all text-sm font-mono">
            {resetToken}
          </div>
          <button
            onClick={() => navigate(`/password-reset/confirm?token=${encodeURIComponent(resetToken)}`)}
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            パスワードをリセットする
          </button>
          <p className="mt-4 text-center text-sm text-gray-600">
            <a href="/login" className="text-blue-600 hover:underline">ログインに戻る</a>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8">
        <h2 className="text-2xl font-bold text-center mb-6">パスワードリセット</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              メールアドレス
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="you@example.com"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? '送信中...' : 'リセットメールを送信'}
          </button>
        </form>
        
        <p className="mt-4 text-center text-sm text-gray-600">
          <a href="/login" className="text-blue-600 hover:underline">ログインに戻る</a>
        </p>
      </div>
    </div>
  )
}
