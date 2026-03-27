import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getNotifications, markNotificationAsRead, NotificationItem } from '../services/notification'

const typeConfig: Record<string, { icon: string; label: string; path: string; color: string }> = {
  recommendation: { icon: 'recommendation', label: 'おすすめ銘柄', path: '/dashboard', color: 'text-blue-500' },
  price_alert: { icon: 'alert', label: '価格アラート', path: '/watchlist', color: 'text-red-500' },
  volume_surge: { icon: 'surge', label: '出来高急増', path: '/stocks', color: 'text-amber-500' },
  test: { icon: 'test', label: 'テスト', path: '/dashboard', color: 'text-slate-400' },
}

function TypeIcon({ type }: { type: string }) {
  const config = typeConfig[type] || { icon: 'default', color: 'text-slate-400' }
  const cls = `w-5 h-5 ${config.color}`
  switch (config.icon) {
    case 'recommendation':
      return <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" /></svg>
    case 'alert':
      return <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" /></svg>
    case 'surge':
      return <svg className={cls} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M15.362 5.214A8.252 8.252 0 0112 21 8.25 8.25 0 016.038 7.048 8.287 8.287 0 009 9.6a8.983 8.983 0 013.361-6.867 8.21 8.21 0 003 2.48z" /><path strokeLinecap="round" strokeLinejoin="round" d="M12 18a3.75 3.75 0 00.495-7.467 5.99 5.99 0 00-1.925 3.546 5.974 5.974 0 01-2.133-1A3.75 3.75 0 0012 18z" /></svg>
    default:
      return <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" /></svg>
  }
}

function getTypeConfig(type: string) {
  return typeConfig[type] || { icon: 'default', label: type, path: '/dashboard', color: 'text-slate-400' }
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return 'たった今'
  if (diffMin < 60) return `${diffMin}分前`
  if (diffHour < 24) return `${diffHour}時間前`
  if (diffDay < 7) return `${diffDay}日前`
  return date.toLocaleDateString('ja-JP')
}

export default function NotificationHistoryPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    fetchNotifications()
  }, [])

  const fetchNotifications = async () => {
    try {
      const data = await getNotifications()
      setNotifications(data)
    } catch (err) {
      console.error('通知の取得に失敗しました', err)
    } finally {
      setLoading(false)
    }
  }

  const handleClick = async (notification: NotificationItem) => {
    const config = getTypeConfig(notification.type)
    if (!notification.is_read) {
      try {
        await markNotificationAsRead(notification.id)
        setNotifications((prev) =>
          prev.map((n) => (n.id === notification.id ? { ...n, is_read: true } : n))
        )
      } catch (err) {
        console.error('既読化に失敗しました', err)
      }
    }
    navigate(config.path)
  }

  const unreadCount = notifications.filter((n) => !n.is_read).length

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">通知履歴</h1>
        {unreadCount > 0 && (
          <span className="text-sm text-slate-400">{unreadCount}件の未読</span>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 text-center py-20">
          <svg className="w-12 h-12 mx-auto text-slate-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" />
          </svg>
          <p className="text-slate-400 text-sm">通知はまだありません</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((notification) => {
            const config = getTypeConfig(notification.type)
            return (
              <button
                key={notification.id}
                onClick={() => handleClick(notification)}
                className={`w-full text-left rounded-lg border transition-all duration-150 flex
                  ${notification.is_read
                    ? 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
                    : 'bg-blue-50/50 border-blue-200 hover:bg-blue-50 hover:shadow-sm'
                  }`}
              >
                {/* 未読アクセントバー */}
                {!notification.is_read && (
                  <div className="w-1 bg-blue-500 rounded-l-lg flex-shrink-0" />
                )}
                <div className="p-4 flex-1">
                  <div className="flex items-start gap-3">
                    <div className="mt-0.5 flex-shrink-0">
                      <TypeIcon type={notification.type} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-400 font-medium">{config.label}</span>
                        {!notification.is_read && (
                          <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                        )}
                      </div>
                      <p className={`mt-1 text-sm ${notification.is_read ? 'text-slate-600' : 'text-slate-900 font-medium'}`}>
                        {notification.title}
                      </p>
                      {notification.body && (
                        <p className="mt-0.5 text-xs text-slate-400 truncate">{notification.body}</p>
                      )}
                      <p className="mt-1.5 text-xs text-slate-400">{formatTime(notification.created_at)}</p>
                    </div>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}
