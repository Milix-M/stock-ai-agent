export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* ヘッダー */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold">Stock AI Agent</h1>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">ユーザー名</span>
            <button className="text-sm text-gray-500 hover:text-gray-700">
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* レコメンド */}
          <div className="md:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">本日のレコメンド</h2>
              <p className="text-gray-500">レコメンド機能は実装中です...</p>
            </div>
          </div>

          {/* サイドバー */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-md font-semibold mb-4">マーケット概況</h3>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">日経平均</span>
                  <span className="font-medium">-（実装中）</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">TOPIX</span>
                  <span className="font-medium">-（実装中）</span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-md font-semibold mb-4">ウォッチリスト</h3>
              <p className="text-gray-500 text-sm">銘柄を追加してください</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
