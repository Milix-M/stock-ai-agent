import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getNotifications, markNotificationAsRead, NotificationItem } from '../services/notification'

const typeConfig: Record<string, { icon: string; label: string; path: string }> = {
  recommendation: { icon: '💡', label: 'おすすめ銘柄', path: '/dashboard' },
  price_alert: { icon: '📉', label: '価格アラート', path: '/watchlist' },
  volume_surge: { icon: '🔥', label: '出来高急増', path: '/stocks' },
  test: { icon: '🧪', label: 'テスト', path: '/dashboard' },
}

function getTypeConfig(type: string) {
  return typeConfig[type] || { icon: '🔔', label: type, path: '/dashboard' }
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
        <h1 className="text-2xl font-bold text-gray-900">通知履歴</h1>
        {unreadCount > 0 && (
          <span className="text-sm text-gray-500">{unreadCount}件の未読</span>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-20">
          <span className="text-5xl mb-4 block">🔕</span>
          <p className="text-gray-500">通知はまだありません</p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((notification) => {
            const config = getTypeConfig(notification.type)
            return (
              <button
                key={notification.id}
                onClick={() => handleClick(notification)}
                className={`w-full text-left p-4 rounded-lg border transition-colors
                  ${notification.is_read
                    ? 'bg-white border-gray-100 hover:bg-gray-50'
                    : 'bg-blue-50 border-blue-100 hover:bg-blue-100'
                  }`}
              >
                <div className="flex items-start gap-3">
                  <span className="text-xl flex-shrink-0 mt-0.5">{config.icon}</span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-gray-400 font-medium">{config.label}</span>
                      {!notification.is_read && (
                        <span className="w-2 h-2 rounded-full bg-blue-500 flex-shrink-0" />
                      )}
                    </div>
                    <p className={`mt-1 text-sm ${notification.is_read ? 'text-gray-600' : 'text-gray-900 font-medium'}`}>
                      {notification.title}
                    </p>
                    {notification.body && (
                      <p className="mt-0.5 text-xs text-gray-400 truncate">{notification.body}</p>
                    )}
                    <p className="mt-1 text-xs text-gray-400">{formatTime(notification.created_at)}</p>
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
