import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../i18n'
import type { Language } from '../i18n'

// 六爻与梅花易数**不进导航**——它们从首页的两个入口进（首页主/次按钮）。
// 导航只保留"容器级"的页面：首页、历史、关于。
const NAV_ITEMS = [
  { to: '/', label: '首页' },
  { to: '/history', label: '历史' },
  { to: '/about', label: '关于' },
]

const LANGS: { value: Language; label: string }[] = [
  { value: 'zh-CN', label: '简' },
  { value: 'zh-TW', label: '繁' },
]

/** 语言切换：贴合古风的两个小圆钮，当前语言高亮 */
function LangSwitch({ className }: { className?: string }) {
  const { lang, setLang, t } = useLanguage()
  return (
    <div
      className={`flex items-center gap-0.5 rounded-full border border-xuanjing-line bg-xuanjing-ink/60 p-0.5 text-xs ${className ?? ''}`}
      role="group"
      aria-label={t('语言切换')}
    >
      {LANGS.map((item) => (
        <button
          key={item.value}
          type="button"
          onClick={() => setLang(item.value)}
          aria-pressed={lang === item.value}
          className={`rounded-full px-2 py-0.5 transition-colors duration-200 ${
            lang === item.value
              ? 'bg-xuanjing-gold/20 text-xuanjing-gold'
              : 'text-xuanjing-paper-dim hover:text-xuanjing-paper'
          }`}
        >
          {item.label}
        </button>
      ))}
    </div>
  )
}

function Header() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const { t } = useLanguage()

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  /** 导航项配色统一由令牌决定，当前项用强调金 */
  const navItemClass = (to: string) =>
    `transition-colors duration-300 hover:text-xuanjing-gold ${
      location.pathname === to ? 'text-xuanjing-gold' : 'text-xuanjing-paper'
    }`

  return (
    <header className="sticky top-0 z-50 border-b border-xuanjing-line bg-xuanjing-ink-2/85 py-6 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-baseline gap-2">
          <h1 className="font-heading text-4xl font-bold text-xuanjing-paper">玄镜易</h1>
          <span className="text-sm font-light text-xuanjing-gold-deep">/ XuanJing Yi</span>
        </Link>

        {/* 桌面端导航 */}
        <nav className="hidden items-center gap-7 md:flex">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`text-sm ${navItemClass(item.to)}`}
            >
              {t(item.label)}
            </Link>
          ))}
          <LangSwitch />
        </nav>

        {/* 移动端汉堡按钮 */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="flex flex-col gap-1.5 p-2 md:hidden"
          aria-label={t('菜单')}
          aria-expanded={mobileOpen}
        >
          <motion.span
            className="block h-0.5 w-6 bg-xuanjing-paper"
            animate={mobileOpen ? { rotate: 45, y: 8 } : { rotate: 0, y: 0 }}
          />
          <motion.span
            className="block h-0.5 w-6 bg-xuanjing-paper"
            animate={mobileOpen ? { opacity: 0 } : { opacity: 1 }}
          />
          <motion.span
            className="block h-0.5 w-6 bg-xuanjing-paper"
            animate={mobileOpen ? { rotate: -45, y: -8 } : { rotate: 0, y: 0 }}
          />
        </button>
      </div>

      {/* 移动端菜单 */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.nav
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden border-t border-xuanjing-line md:hidden"
          >
            <div className="flex flex-col gap-3 px-6 py-4">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`py-2 ${navItemClass(item.to)}`}
                >
                  {t(item.label)}
                </Link>
              ))}
              <LangSwitch className="self-start" />
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}

export default Header
