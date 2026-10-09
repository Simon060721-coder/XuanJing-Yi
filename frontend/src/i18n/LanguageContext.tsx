import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { toTraditional } from './zhConverter'

export type Language = 'zh-CN' | 'zh-TW'

const STORAGE_KEY = 'xuanjing-lang'

interface LanguageContextValue {
  lang: Language
  setLang: (lang: Language) => void
  /** 按当前语言转换简体文案：繁体时输出繁体，简体时原样返回 */
  t: (text: string) => string
}

const LanguageContext = createContext<LanguageContextValue | null>(null)

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Language>(() => {
    try {
      return window.localStorage.getItem(STORAGE_KEY) === 'zh-TW' ? 'zh-TW' : 'zh-CN'
    } catch {
      return 'zh-CN'
    }
  })

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, lang)
    } catch {
      // 忽略存储失败（如隐私模式）
    }
    document.documentElement.lang = lang
  }, [lang])

  const value = useMemo<LanguageContextValue>(
    () => ({
      lang,
      setLang: setLangState,
      t: (text: string) => (lang === 'zh-TW' ? toTraditional(text) : text),
    }),
    [lang],
  )

  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage 必须在 LanguageProvider 内使用')
  return ctx
}
