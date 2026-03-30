import {
  useColorThemeStore,
  RISE_PRESETS,
  FALL_PRESETS,
} from '../stores/colorThemeStore'

function ColorSwatch({
  presets,
  selectedId,
  onSelect,
}: {
  presets: typeof RISE_PRESETS
  selectedId: string
  onSelect: (id: string) => void
}) {
  return (
    <div className="flex gap-2 flex-wrap">
      {presets.map((preset) => (
        <button
          key={preset.id}
          onClick={() => onSelect(preset.id)}
          title={preset.label}
          className={`w-8 h-8 rounded-full border-2 transition-all duration-150 hover:scale-110 ${
            selectedId === preset.id
              ? 'border-slate-800 ring-2 ring-offset-1 ring-slate-400'
              : 'border-transparent'
          }`}
          style={{ backgroundColor: preset.preview }}
        />
      ))}
    </div>
  )
}

export default function ColorThemeSettings() {
  const { riseColorId, fallColorId, setRiseColor, setFallColor } = useColorThemeStore()
  const rise = RISE_PRESETS.find(p => p.id === riseColorId)
  const fall = FALL_PRESETS.find(p => p.id === fallColorId)

  return (
    <div className="mt-6">
      <h3 className="text-sm font-bold text-slate-800 mb-3">表示設定</h3>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-sm text-slate-700">上昇の色</p>
            <p className="text-xs text-slate-400 mt-0.5">{rise?.label || 'エメラルドグリーン'}</p>
          </div>
          <ColorSwatch presets={RISE_PRESETS} selectedId={riseColorId} onSelect={setRiseColor} />
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="font-medium text-sm text-slate-700">下落の色</p>
            <p className="text-xs text-slate-400 mt-0.5">{fall?.label || 'レッド'}</p>
          </div>
          <ColorSwatch presets={FALL_PRESETS} selectedId={fallColorId} onSelect={setFallColor} />
        </div>
      </div>
      <p className="text-xs text-slate-400 mt-2">
        ※ 設定はブラウザに保存されます
      </p>
    </div>
  )
}
