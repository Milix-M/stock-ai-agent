import { useEffect, useState } from 'react'
import { 
  requestNotificationPermission, 
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications 
} from '../services/notification'

export default function NotificationSettings() {
  const [isSupported, setIsSupported] = useState(false)
  const [permission, setPermission] = useState<NotificationPermission | null>(null)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    checkSupport()
  }, [])

  const checkSupport = () => {
    if (!('Notification' in window)) {
      setIsSupported(false)
      return
    }
    
    setIsSupported(true)
    setPermission(Notification.permission)
    
    // 既存の購読を確認
    checkExistingSubscription()
  }

  const checkExistingSubscription = async () => {
    try {
      const registration = await navigator.serviceWorker.ready
      const subscription = await registration.pushManager.getSubscription()
      setIsSubscribed(!!subscription)
    } catch {
      setIsSubscribed(false)
    }
  }

  const handleEnable = async () => {
    setIsLoading(true)
    try {
      // 許可をリクエスト
      const granted = await requestNotificationPermission()
      if (!granted) {
        alert('通知の許可が必要です')
        return
      }
      
      setPermission('granted')
      
      // プッシュ通知を購読
      const subscribed = await subscribeToPushNotifications()
      if (subscribed) {
        setIsSubscribed(true)
        alert('プッシュ通知を有効にしました！')
      }
    } catch (error) {
      alert('設定に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDisable = async () => {
    setIsLoading(true)
    try {
      const success = await unsubscribeFromPushNotifications()
      if (success) {
        setIsSubscribed(false)
        alert('プッシュ通知を無効にしました')
      }
    } catch (error) {
      alert('解除に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 p-4 rounded-lg">
        <p className="text-yellow-800">
          お使いのブラウザはプッシュ通知に対応していません。
        </p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">通知設定</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium">プッシュ通知</p>
            <p className="text-sm text-gray-500">
              {isSubscribed 
                ? '通知が有効です' 
                : '株価変動やレコメンドを受け取れます'}
            </p>
          </div>
          
          {isSubscribed ? (
            <button
              onClick={handleDisable}
              disabled={isLoading}
              className="px-4 py-2 text-red-600 border border-red-300 rounded hover:bg-red-50 disabled:opacity-50"
            >
              {isLoading ? '処理中...' : '無効にする'}
            </button>
          ) : (
            <button
              onClick={handleEnable}
              disabled={isLoading || permission === 'denied'}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? '処理中...' : '有効にする'}
            </button>
          )}
        </div>
        
        {permission === 'denied' && (
          <p className="text-sm text-red-600">
            ブラウザの設定から通知を許可してください
          </p>
        )}
        
        <div className="border-t pt-4 mt-4">
          <p className="text-sm text-gray-600 mb-2">通知内容：</p>
          <ul className="text-sm text-gray-500 list-disc list-inside space-y-1">
            <li>株価変動アラート</li>
            <li>おすすめ銘柄のレコメンド</li>
            <li>ウォッチリスト銘柄の更新</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
