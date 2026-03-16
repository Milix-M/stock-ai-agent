export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Stock AI Agent
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          AIが株価を監視し、あなたの投資パターンに合った銘柄を提案
        </p>
        <div className="space-x-4">
          <a
            href="/login"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            ログイン
          </a>
          <a
            href="/dashboard"
            className="inline-block bg-gray-200 text-gray-800 px-6 py-3 rounded-lg font-medium hover:bg-gray-300 transition"
          >
            ダッシュボード（仮）
          </a>
        </div>
      </div>
    </div>
  )
}
