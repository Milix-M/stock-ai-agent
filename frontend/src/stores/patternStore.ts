import { create } from 'zustand'
import { patternApi, Pattern, PatternParseResponse } from '../services/pattern'

interface PatternState {
  patterns: Pattern[]
  isLoading: boolean
  isParsing: boolean
  error: string | null
  parseResult: PatternParseResponse | null
  
  // Actions
  fetchPatterns: () => Promise<void>
  parsePattern: (input: string) => Promise<PatternParseResponse | null>
  createPattern: (name: string, description: string, rawInput: string, parsedFilters: any) => Promise<void>
  deletePattern: (patternId: string) => Promise<void>
  togglePattern: (patternId: string) => Promise<void>
  clearError: () => void
  clearParseResult: () => void
}

export const usePatternStore = create<PatternState>()((set, get) => ({
  patterns: [],
  isLoading: false,
  isParsing: false,
  error: null,
  parseResult: null,

  fetchPatterns: async () => {
    set({ isLoading: true, error: null })
    try {
      const patterns = await patternApi.getPatterns()
      set({ patterns, isLoading: false })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'パターンの取得に失敗しました',
        isLoading: false,
      })
    }
  },

  parsePattern: async (input) => {
    set({ isParsing: true, error: null })
    try {
      const result = await patternApi.parsePattern(input)
      set({ parseResult: result, isParsing: false })
      return result
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'パターンの解析に失敗しました',
        isParsing: false,
      })
      return null
    }
  },

  createPattern: async (name, description, rawInput, parsedFilters) => {
    set({ isLoading: true, error: null })
    try {
      const newPattern = await patternApi.createPattern({
        name,
        description,
        raw_input: rawInput,
        parsed_filters: parsedFilters,
      })
      set({
        patterns: [newPattern, ...get().patterns],
        isLoading: false,
        parseResult: null,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'パターンの作成に失敗しました',
        isLoading: false,
      })
      throw error
    }
  },

  deletePattern: async (patternId) => {
    set({ isLoading: true, error: null })
    try {
      await patternApi.deletePattern(patternId)
      set({
        patterns: get().patterns.filter((p) => p.id !== patternId),
        isLoading: false,
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'パターンの削除に失敗しました',
        isLoading: false,
      })
      throw error
    }
  },

  togglePattern: async (patternId) => {
    try {
      const result = await patternApi.togglePattern(patternId)
      set({
        patterns: get().patterns.map((p) =>
          p.id === patternId ? { ...p, is_active: result.is_active } : p
        ),
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || '状態の変更に失敗しました',
      })
    }
  },

  clearError: () => set({ error: null }),
  clearParseResult: () => set({ parseResult: null }),
}))
