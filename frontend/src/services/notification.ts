import { api } from './api'

export interface NotificationSubscription {
  endpoint: string
  p256dh: string
  auth: string
}

export interface NotificationItem {
  id: string
  type: string
  title: string
  body: string
  data?: any
  is_read: boolean
  created_at: string
}

// VAPID公開鍵を取得
const getVapidPublicKey = (): string => {
  return import.meta.env.VITE_VAPID_PUBLIC_KEY || ''
}

// Service Workerを登録
export const registerServiceWorker = async (): Promise<ServiceWorkerRegistration | null> => {
  if (!('serviceWorker' in navigator)) {
    console.log('Service Worker not supported')
    return null
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js')
    console.log('Service Worker registered:', registration)
    return registration
  } catch (error) {
    console.error('Service Worker registration failed:', error)
    return null
  }
}

// プッシュ通知の許可をリクエスト
export const requestNotificationPermission = async (): Promise<boolean> => {
  if (!('Notification' in window)) {
    console.log('Notifications not supported')
    return false
  }

  const permission = await Notification.requestPermission()
  return permission === 'granted'
}

// プッシュ通知を購読
export const subscribeToPushNotifications = async (): Promise<boolean> => {
  try {
    const registration = await registerServiceWorker()
    if (!registration) return false

    // 既存の購読を確認
    let subscription = await registration.pushManager.getSubscription()
    
    if (subscription) {
      console.log('Already subscribed')
      return true
    }

    // 新規購読
    const vapidPublicKey = getVapidPublicKey()
    if (!vapidPublicKey) {
      console.error('VAPID public key not configured')
      return false
    }

    const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey)

    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: convertedVapidKey
    })

    // サーバーに購読情報を送信
    const subscriptionData = {
      endpoint: subscription.endpoint,
      p256dh: arrayBufferToBase64(subscription.getKey('p256dh')!),
      auth: arrayBufferToBase64(subscription.getKey('auth')!)
    }

    await api.post('/notifications/subscribe', subscriptionData)
    console.log('Push notification subscription successful')
    return true

  } catch (error) {
    console.error('Failed to subscribe to push notifications:', error)
    return false
  }
}

// プッシュ通知を解除
export const unsubscribeFromPushNotifications = async (): Promise<boolean> => {
  try {
    const registration = await navigator.serviceWorker.ready
    const subscription = await registration.pushManager.getSubscription()

    if (!subscription) {
      return true
    }

    // サーバーから削除
    await api.post('/notifications/unsubscribe', {
      endpoint: subscription.endpoint
    })

    // ブラウザの購読を解除
    await subscription.unsubscribe()
    console.log('Push notification unsubscription successful')
    return true

  } catch (error) {
    console.error('Failed to unsubscribe:', error)
    return false
  }
}

// 通知履歴を取得
export const getNotifications = async (limit: number = 50): Promise<NotificationItem[]> => {
  const response = await api.get(`/notifications?limit=${limit}`)
  return response.data
}

// 通知を既読にする
export const markNotificationAsRead = async (notificationId: string): Promise<void> => {
  await api.post(`/notifications/${notificationId}/read`)
}

// --- 通知設定 ---

export interface NotificationSettings {
  recommend_enabled: boolean
  recommend_min_score: number
  price_alert_enabled: boolean
  price_alert_threshold: number
  volume_surge_enabled: boolean
  volume_surge_multiplier: number
  daily_report_enabled: boolean
}

export const getNotificationSettings = async (): Promise<NotificationSettings> => {
  const response = await api.get('/notifications/settings')
  return response.data
}

export const updateNotificationSettings = async (settings: Partial<NotificationSettings>): Promise<void> => {
  await api.put('/notifications/settings', settings)
}

// --- Push購読（settingsベース） ---

export const subscribePush = async (subscription: { endpoint: string; p256dh: string; auth: string }): Promise<void> => {
  await api.post('/notifications/subscribe', subscription)
}

export const unsubscribePush = async (endpoint: string): Promise<void> => {
  await api.post('/notifications/unsubscribe', { endpoint })
}

// Base64変換ユーティリティ
function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = '='.repeat((4 - base64String.length % 4) % 4)
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/')

  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

function arrayBufferToBase64(buffer: ArrayBuffer | null): string {
  if (!buffer) return ''
  
  const bytes = new Uint8Array(buffer)
  let binary = ''
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i])
  }
  return window.btoa(binary)
}
