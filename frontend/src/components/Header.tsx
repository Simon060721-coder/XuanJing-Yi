import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

const NAV_ITEMS = [
  { to: '/', label: '首页' },
  { to: '/divination', label: '占卜' },
  { to: '/history', label: '历史' },
  { to: '/about', label: '关于' },
]

function Header() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  return (
    <header className="bg-xuanjing-black/80 border-b border-xuanjing-wood/30 py-6 sticky top-0 z-50 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <h1 className="text-4xl font-heading font-bold text-xuanjing-cream">玄镜易</h1>
          <span className="text-xuanjing-accent text-sm font-light">/ XuanJing Yi</span>
        </Link>

        {/* 桌面端导航 */}
        <nav className="hidden md:flex gap-8">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="transition-colors duration-300 hover:text-xuanjing-accent"
              style={{
                color: location.pathname === item.to ? '#936142' : '#F5E7D0',
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* 移动端汉堡按钮 */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden flex flex-col gap-1.5 p-2"
          aria-label="菜单"
        >
          <motion.span
            className="block w-6 h-0.5 bg-xuanjing-cream"
            animate={mobileOpen ? { rotate: 45, y: 8 } : { rotate: 0, y: 0 }}
          />
          <motion.span
            className="block w-6 h-0.5 bg-xuanjing-cream"
            animate={mobileOpen ? { opacity: 0 } : { opacity: 1 }}
          />
          <motion.span
            className="block w-6 h-0.5 bg-xuanjing-cream"
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
            className="md:hidden overflow-hidden"
            style={{ borderTop: '1px solid rgba(122, 82, 60, 0.2)' }}
          >
            <div className="px-6 py-4 flex flex-col gap-3">
              {NAV_ITEMS.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className="py-2 transition-colors duration-300"
                  style={{
                    color: location.pathname === item.to ? '#936142' : '#F5E7D0',
                  }}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  )
}

export default Header
