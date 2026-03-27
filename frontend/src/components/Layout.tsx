import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

const navItems = [
  { to: '/dashboard', label: 'ダッシュボード', icon: '📊' },
  { to: '/stocks', label: '銘柄検索', icon: '🔍' },
  { to: '/patterns', label: 'パターン管理', icon: '📐' },
  { to: '/watchlist', label: 'ウォッチリスト', icon: '👁' },
  { to: '/settings/notifications', label: '通知設定', icon: '🔔' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* モバイルオーバーレイ */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* サイドバー */}
      <aside
        className={`fixed top-0 left-0 h-full z-40 bg-white shadow-lg transition-all duration-200
          ${sidebarOpen ? 'w-56' : 'w-16'} hover:w-56
          lg:w-16 lg:hover:w-56`}
      >
        <div className="flex items-center h-16 px-4 border-b">
          <span className="text-xl">📈</span>
          {sidebarOpen && (
            <span className="ml-2 font-bold text-lg whitespace-nowrap lg:hidden">Stock AI</span>
          )}
          <span className="ml-2 font-bold text-lg whitespace-nowrap hidden lg:group-hover:inline">
          </span>
        </div>

        <nav className="mt-4 space-y-1 px-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center px-3 py-3 rounded-lg transition-colors
                ${isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`
              }
            >
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              <span className="ml-3 whitespace-nowrap text-sm">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* メインエリア */}
      <div className="lg:pl-16">
        {/* ヘッダー */}
        <header className="bg-white shadow-sm sticky top-0 z-20">
          <div className="flex items-center justify-between px-4 py-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-gray-600 hover:text-gray-900"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {sidebarOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>

            <div className="flex-1" />

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 hidden sm:block">
                {user?.display_name || user?.email}
              </span>
              <button
                onClick={handleLogout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                ログアウト
              </button>
            </div>
          </div>
        </header>

        {/* コンテンツ */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
