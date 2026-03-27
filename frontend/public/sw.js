// サービスワーカー（プッシュ通知用）

const CACHE_NAME = 'picks-v1'
const urlsToCache = [
  '/',
  '/index.html',
  '/vite.svg'
]

// インストール時：キャッシュ作成
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  )
  self.skipWaiting()
})

// アクティベート時：古いキャッシュ削除
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  )
  self.clients.claim()
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
  const data = event.data ? event.data.json() : {}
  const title = data.title || 'PICKS'
  const options = {
    body: data.body || '新しい通知があります',
    icon: data.icon || '/vite.svg',
    badge: data.badge || '/vite.svg',
    data: data.data || {},
    vibrate: [100, 50, 100],
    requireInteraction: data.requireInteraction || false,
    actions: data.actions || [],
  }
  event.waitUntil(
    self.registration.showNotification(title, options)
  )
})

// 通知クリック時
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  const data = event.notification.data || {}
  const action = event.action
  let url = '/dashboard'

  // アクションボタン対応
  if (action === 'add_watchlist') {
    event.waitUntil(
      fetch('/api/v1/watchlist/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stock_code: data.stock_code }),
      }).then(() => clients.openWindow('/watchlist'))
    )
    return
  }

  // 通知タイプに応じて遷移先を変える
  if (data.type === 'recommendation') {
    url = '/dashboard'
  } else if (data.type === 'price_alert') {
    url = '/watchlist'
  } else if (data.type === 'volume_surge') {
    url = '/stocks'
  } else if (data.stock_code) {
    url = `/stocks/${data.stock_code}`
  }

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        // 既存のウィンドウがあればフォーカス
        for (const client of windowClients) {
          if (client.url.includes(self.location.origin) && 'focus' in client) {
            client.navigate(url)
            return client.focus()
          }
        }
        // なければ新規ウィンドウ
        return clients.openWindow(url)
      })
  )
})
