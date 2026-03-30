import ColorThemeSettings from '../components/ColorThemeSettings'
import NotificationSettings from '../components/NotificationSettings'

export default function SettingsPage() {
  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-xl font-bold text-slate-800 mb-6">設定</h1>

      <div className="space-y-6">
        {/* 表示設定 */}
        <ColorThemeSettings />

        {/* 通知設定 */}
        <NotificationSettings />
      </div>
    </div>
  )
}
