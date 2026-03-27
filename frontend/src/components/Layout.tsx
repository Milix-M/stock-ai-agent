import { useState, useEffect } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { getNotifications } from '../services/notification'

const navItems = [
  { to: '/dashboard', label: 'ダッシュボード', icon: '📊' },
  { to: '/stocks', label: '銘柄検索', icon: '🔍' },
  { to: '/patterns', label: 'パターン管理', icon: '📐' },
  { to: '/watchlist', label: 'ウォッチリスト', icon: '👁' },
  { to: '/notifications', label: '通知履歴', icon: '🔔' },
  { to: '/settings/notifications', label: '通知設定', icon: '⚙️' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  useEffect(() => {
    getNotifications().then((ns) => {
      setUnreadCount(ns.filter((n) => !n.is_read).length)
    }).catch(() => {})
  }, [])

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

      {/* サイドバー — デスクトップ: group + hoverで展開 / モバイル: toggle */}
      <aside
        className={`fixed top-0 left-0 h-full z-40 bg-white shadow-lg
          flex flex-col transition-all duration-200
          ${sidebarOpen ? 'w-56' : 'w-16'}
          group`}
      >
        {/* ロゴ */}
        <div className="flex items-center h-16 px-4 border-b overflow-hidden">
          <span className="text-xl flex-shrink-0">📈</span>
          <span className="ml-2 font-bold text-lg whitespace-nowrap overflow-hidden">
            PICKS
          </span>
        </div>

        {/* ナビ */}
        <nav className="mt-4 space-y-1 px-2 flex-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center px-3 py-3 rounded-lg transition-colors overflow-hidden
                ${isActive ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'}`
              }
            >
              <span className="text-xl flex-shrink-0">{item.icon}</span>
              <span className="ml-3 whitespace-nowrap text-sm overflow-hidden">
                {item.label}
              </span>
            </NavLink>
          ))}
        </nav>
      </aside>

      {/* メインエリア — サイドバー幅分オフセット */}
      <div className="transition-all duration-200" style={{ marginLeft: '4rem' }}>
        {/* ヘッダー */}
        <header className="bg-white shadow-sm sticky top-0 z-20">
          <div className="flex items-center justify-between px-4 py-3">
            {/* ハンバーガー（モバイルのみ） */}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-gray-600 hover:text-gray-900 mr-3"
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
              {/* 通知ベル */}
              <button
                onClick={() => navigate('/notifications')}
                className="relative text-gray-500 hover:text-gray-700"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>
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

      {/* CSS for group hover — inline style because Tailwind group hover needs parent class */}
      <style>{`
        @media (min-width: 1024px) {
          aside:not(:hover) span.ml-3 {
            display: none;
          }
          aside:hover {
            width: 14rem !important;
          }
          aside:hover ~ div {
            margin-left: 14rem !important;
          }
        }
        @media (max-width: 1023px) {
          aside {
            transform: translateX(${sidebarOpen ? '0' : '-100%'});
          }
          aside ~ div {
            margin-left: 0 !important;
          }
        }
      `}</style>
    </div>
  )
}
