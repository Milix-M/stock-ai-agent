import { useEffect, useState } from 'react'
import {
  requestNotificationPermission,
  subscribeToPushNotifications,
  unsubscribeFromPushNotifications,
  getNotificationSettings,
  updateNotificationSettings,
  type NotificationSettings,
} from '../services/notification'
import ColorThemeSettings from './ColorThemeSettings'

const defaultSettings: NotificationSettings = {
  recommend_enabled: true,
  recommend_min_score: 0.7,
  price_alert_enabled: true,
  price_alert_threshold: 5.0,
  volume_surge_enabled: true,
  volume_surge_multiplier: 2.0,
  daily_report_enabled: true,
}

function Toggle({ checked, onChange, disabled }: { checked: boolean; onChange: (v: boolean) => void; disabled?: boolean }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 ${
        checked ? 'bg-emerald-500' : 'bg-slate-300'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white shadow-sm transition-transform duration-200 ${
          checked ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  )
}

function Slider({ value, min, max, step, onChange, label }: {
  value: number; min: number; max: number; step: number
  onChange: (v: number) => void; label: string
}) {
  return (
    <div className="flex items-center gap-3">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1 accent-emerald-500"
      />
      <span className="text-sm text-slate-500 w-24 text-right font-medium">{label}</span>
    </div>
  )
}

export default function NotificationSettings() {
  const [isSupported, setIsSupported] = useState(false)
  const [permission, setPermission] = useState<NotificationPermission | null>(null)
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [isPushLoading, setIsPushLoading] = useState(false)
  const [settings, setSettings] = useState<NotificationSettings>(defaultSettings)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [saveMessage, setSaveMessage] = useState<string | null>(null)

  useEffect(() => {
    fetchSettings()
    checkSupport()
  }, [])

  const fetchSettings = async () => {
    try {
      const s = await getNotificationSettings()
      setSettings({ ...defaultSettings, ...s })
    } catch {
    } finally {
      setIsLoading(false)
    }
  }

  const checkSupport = () => {
    if (!('Notification' in window)) {
      setIsSupported(false)
      return
    }
    setIsSupported(true)
    setPermission(Notification.permission)
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

  const handleSave = async () => {
    setIsSaving(true)
    setSaveMessage(null)
    try {
      await updateNotificationSettings(settings)
      setSaveMessage('設定を保存しました')
      setTimeout(() => setSaveMessage(null), 3000)
    } catch {
      setSaveMessage('保存に失敗しました')
    } finally {
      setIsSaving(false)
    }
  }

  const handleEnable = async () => {
    setIsPushLoading(true)
    try {
      const granted = await requestNotificationPermission()
      if (!granted) {
        alert('通知の許可が必要です')
        return
      }
      setPermission('granted')
      const subscribed = await subscribeToPushNotifications()
      if (subscribed) setIsSubscribed(true)
    } catch {
      alert('設定に失敗しました')
    } finally {
      setIsPushLoading(false)
    }
  }

  const handleDisable = async () => {
    setIsPushLoading(true)
    try {
      const success = await unsubscribeFromPushNotifications()
      if (success) setIsSubscribed(false)
    } catch {
      alert('解除に失敗しました')
    } finally {
      setIsPushLoading(false)
    }
  }

  const update = <K extends keyof NotificationSettings>(key: K, value: NotificationSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  if (isLoading) {
    return <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6"><p className="text-center py-4 text-slate-400 text-sm">読み込み中...</p></div>
  }

  return (
    <div className="space-y-6">
      {/* プッシュ通知 */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-base font-bold text-slate-800 mb-4">プッシュ通知</h3>
        {isSupported ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm text-slate-700">ブラウザプッシュ通知</p>
                <p className="text-xs text-slate-400 mt-0.5">
                  {isSubscribed ? '通知が有効です' : '株価変動やレコメンドをブラウザで受け取れます'}
                </p>
              </div>
              {isSubscribed ? (
                <button
                  onClick={handleDisable}
                  disabled={isPushLoading}
                  className="px-4 py-1.5 text-red-600 border border-red-200 rounded-lg hover:bg-red-50 disabled:opacity-50 text-sm font-medium transition-colors"
                >
                  {isPushLoading ? '処理中...' : '無効にする'}
                </button>
              ) : (
                <button
                  onClick={handleEnable}
                  disabled={isPushLoading || permission === 'denied'}
                  className="px-4 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium transition-colors"
                >
                  {isPushLoading ? '処理中...' : '有効にする'}
                </button>
              )}
            </div>
            {!import.meta.env.VITE_VAPID_PUBLIC_KEY && (
              <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 p-3 rounded-lg">
                VAPID公開鍵が設定されていません。<code className="text-xs">frontend/.env</code> に <code className="text-xs">VITE_VAPID_PUBLIC_KEY</code> を設定してください。
              </p>
            )}
            {permission === 'denied' && (
              <p className="text-xs text-red-600">ブラウザの設定から通知を許可してください</p>
            )}
          </div>
        ) : (
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 p-3 rounded-lg">お使いのブラウザはプッシュ通知に対応していません。</p>
        )}
      </div>

      {/* 通知内容の設定 */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-base font-bold text-slate-800 mb-4">通知内容の設定</h3>
        <div className="space-y-5">
          {/* レコメンド通知 */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-medium text-sm text-slate-700">レコメンド通知</p>
                <p className="text-xs text-slate-400 mt-0.5">AIおすすめ銘柄の通知</p>
              </div>
              <Toggle
                checked={settings.recommend_enabled}
                onChange={(v) => update('recommend_enabled', v)}
                disabled={!settings.recommend_enabled && !isSubscribed}
              />
            </div>
            {settings.recommend_enabled && (
              <Slider
                value={settings.recommend_min_score}
                min={0.1}
                max={1.0}
                step={0.05}
                onChange={(v) => update('recommend_min_score', v)}
                label={`最低スコア: ${settings.recommend_min_score}`}
              />
            )}
          </div>

          {/* 価格変動通知 */}
          <div className="border-t border-slate-100 pt-5">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="font-medium text-sm text-slate-700">価格変動アラート</p>
                <p className="text-xs text-slate-400 mt-0.5">指定%以上の変動時に通知</p>
              </div>
              <Toggle
                checked={settings.price_alert_enabled}
                onChange={(v) => update('price_alert_enabled', v)}
              />
            </div>
            {settings.price_alert_enabled && (
              <Slider
                value={settings.price_alert_threshold}
                min={1}
                max={20}
                step={0.5}
                onChange={(v) => update('price_alert_threshold', v)}
                label={`閾値: ${settings.price_alert_threshold}%`}
              />
            )}
          </div>

          {/* 出来高急増通知 */}
          <div className="border-t border-slate-100 pt-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm text-slate-700">出来高急増通知</p>
                <p className="text-xs text-slate-400 mt-0.5">通常の指定倍以上の出来高時に通知</p>
              </div>
              <Toggle
                checked={settings.volume_surge_enabled}
                onChange={(v) => update('volume_surge_enabled', v)}
              />
            </div>
            {settings.volume_surge_enabled && (
              <Slider
                value={settings.volume_surge_multiplier}
                min={1.5}
                max={10}
                step={0.5}
                onChange={(v) => update('volume_surge_multiplier', v)}
                label={`倍率: ${settings.volume_surge_multiplier}x`}
              />
            )}
          </div>

          {/* 日次レポート */}
          <div className="border-t border-slate-100 pt-5">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-sm text-slate-700">日次レポート</p>
                <p className="text-xs text-slate-400 mt-0.5">毎日の市場サマリーを通知</p>
              </div>
              <Toggle
                checked={settings.daily_report_enabled}
                onChange={(v) => update('daily_report_enabled', v)}
              />
            </div>
          </div>

          <ColorThemeSettings />

        </div>

        {/* 保存ボタン */}
        <div className="mt-6 pt-5 border-t border-slate-100 flex items-center gap-4">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 text-sm font-medium transition-colors"
          >
            {isSaving ? '保存中...' : '設定を保存'}
          </button>
          {saveMessage && (
            <span className={`text-sm font-medium ${saveMessage.includes('失敗') ? 'text-red-600' : 'text-emerald-600'}`}>
              {saveMessage}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
