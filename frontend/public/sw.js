// サービスワーカー（プッシュ通知用）

const CACHE_NAME = 'stock-ai-agent-v1'
const urlsToCache = [
  '/',
  '/index.html',
  '/icon-192.png',
  '/icon-512.png'
]

// インストール時：キャッシュ作成
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  )
  self.skipWaiting()
})

// フェッチ時：キャッシュ優先
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          return response
        }
        return fetch(event.request)
      })
  )
})

// プッシュ通知受信
self.addEventListener('push', (event) => {
  if (!event.data) return

  const data = event.data.json()
  
  const options = {
    body: data.body,
    icon: data.icon || '/icon-192.png',
    badge: data.badge || '/badge-72x72.png',
    data: data.data || {},
    requireInteraction: data.requireInteraction || false,
    actions: data.actions || []
  }

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  )
})

// 通知クリック時
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  const notificationData = event.notification.data
  const action = event.action

  if (action === 'view' || !action) {
    // アプリを開く
    const url = notificationData?.stock_code 
      ? `/stocks/${notificationData.stock_code}`
      : '/dashboard'

    event.waitUntil(
      clients.openWindow(url)
    )
  } else if (action === 'add_watchlist') {
    // ウォッチリストに追加（バックグラウンド処理）
    event.waitUntil(
      fetch('/api/v1/watchlist/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          stock_id: notificationData?.stock_code
        })
      }).then(() => {
        clients.openWindow('/dashboard')
      })
    )
  }
})
