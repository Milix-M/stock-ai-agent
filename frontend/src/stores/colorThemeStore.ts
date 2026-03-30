import { create } from 'zustand'

export interface ColorPreset {
  id: string
  label: string
  preview: string // hex color for display
  textClass: string    // tailwind text-{color}-600
  bgTextClass: string  // tailwind bg-{color}-100 text-{color}-700
  bgClass: string      // tailwind bg-{color}-50
  borderClass: string  // tailwind border-{color}-200
}

export const RISE_PRESETS: ColorPreset[] = [
  {
    id: 'emerald',
    label: 'エメラルドグリーン',
    preview: '#059669',
    textClass: 'text-emerald-600',
    bgTextClass: 'bg-emerald-100 text-emerald-700',
    bgClass: 'bg-emerald-50',
    borderClass: 'border-emerald-200',
  },
  {
    id: 'sky',
    label: 'スカイブルー',
    preview: '#0284c7',
    textClass: 'text-sky-600',
    bgTextClass: 'bg-sky-100 text-sky-700',
    bgClass: 'bg-sky-50',
    borderClass: 'border-sky-200',
  },
  {
    id: 'violet',
    label: 'バイオレット',
    preview: '#7c3aed',
    textClass: 'text-violet-600',
    bgTextClass: 'bg-violet-100 text-violet-700',
    bgClass: 'bg-violet-50',
    borderClass: 'border-violet-200',
  },
]

export const FALL_PRESETS: ColorPreset[] = [
  {
    id: 'red',
    label: 'レッド',
    preview: '#dc2626',
    textClass: 'text-red-600',
    bgTextClass: 'bg-red-100 text-red-700',
    bgClass: 'bg-red-50',
    borderClass: 'border-red-200',
  },
  {
    id: 'orange',
    label: 'オレンジ',
    preview: '#ea580c',
    textClass: 'text-orange-600',
    bgTextClass: 'bg-orange-100 text-orange-700',
    bgClass: 'bg-orange-50',
    borderClass: 'border-orange-200',
  },
  {
    id: 'pink',
    label: 'ピンク',
    preview: '#db2777',
    textClass: 'text-pink-600',
    bgTextClass: 'bg-pink-100 text-pink-700',
    bgClass: 'bg-pink-50',
    borderClass: 'border-pink-200',
  },
]

interface ColorThemeState {
  riseColorId: string
  fallColorId: string
  setRiseColor: (id: string) => void
  setFallColor: (id: string) => void
}

function loadFromStorage(key: string, fallback: string): string {
  try {
    return localStorage.getItem(key) || fallback
  } catch {
    return fallback
  }
}

function saveToStorage(key: string, value: string) {
  try {
    localStorage.setItem(key, value)
  } catch {
    // ignore
  }
}

export const useColorThemeStore = create<ColorThemeState>((set) => ({
  riseColorId: loadFromStorage('color-rise', 'emerald'),
  fallColorId: loadFromStorage('color-fall', 'red'),
  setRiseColor: (id) => {
    saveToStorage('color-rise', id)
    set({ riseColorId: id })
  },
  setFallColor: (id) => {
    saveToStorage('color-fall', id)
    set({ fallColorId: id })
  },
}))

/** Get current rise/fall ColorPreset objects */
export function useColorTheme() {
  const { riseColorId, fallColorId } = useColorThemeStore()
  const rise = RISE_PRESETS.find(p => p.id === riseColorId) || RISE_PRESETS[0]
  const fall = FALL_PRESETS.find(p => p.id === fallColorId) || FALL_PRESETS[0]
  return { rise, fall }
}
