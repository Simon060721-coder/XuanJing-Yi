import React, { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

import PageShell from '../components/PageShell'
import { BTN_PRIMARY, BTN_OUTLINE, BTN_DANGER } from '../styles/ui'
import { useLanguage } from '../i18n'

interface HistoryItem {
  id: number
  query_type: string
  input_method: string
  primary_hexagram: string
  secondary_hexagram: string
  changing_lines: string
  fortune_score: number
  fortune_level: string
  fortune_label: string
  main_interpretation: string
  keywords: string[]
  primary_display: string
  secondary_display: string
  query_timestamp: string
}

/** 吉凶标签 → 令牌色 */
function fortuneTone(level: string): { text: string; bg: string } {
  if (level === '大吉') return { text: 'text-xuanjing-jade-bright', bg: 'bg-xuanjing-jade/15' }
  if (level === '吉') return { text: 'text-xuanjing-jade', bg: 'bg-xuanjing-jade/15' }
  if (level === '平吉') return { text: 'text-xuanjing-jade/80', bg: 'bg-xuanjing-jade/10' }
  if (level === '平') return { text: 'text-xuanjing-gold', bg: 'bg-xuanjing-gold/15' }
  return { text: 'text-xuanjing-cinnabar-text', bg: 'bg-xuanjing-cinnabar/15' }
}

function HistoryPage() {
  const { t } = useLanguage()
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [offset, setOffset] = useState(0)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [detail, setDetail] = useState<any>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [clearing, setClearing] = useState(false)

  const limit = 10

  const fetchHistory = useCallback(async (reset = true) => {
    try {
      setLoading(true)
      setError(null)
      const currentOffset = reset ? 0 : offset
      const response = await fetch(`/api/v1/divination/history?limit=${limit}&offset=${currentOffset}`)
      const data = await response.json()

      if (!response.ok) {
        setError(data?.error || t('加载历史记录失败'))
        return
      }

      const newItems = data.data.items || []
      if (reset) {
        setItems(newItems)
        setOffset(newItems.length)
      } else {
        setItems((prev) => [...prev, ...newItems])
        setOffset((prev) => prev + newItems.length)
      }
      setTotal(data.data.total)
      setHasMore(data.data.has_more)
    } catch (err) {
      console.error(err)
      setError(t('网络请求失败，请检查后端服务是否已启动'))
    } finally {
      setLoading(false)
    }
  }, [offset])

  useEffect(() => {
    fetchHistory(true)
  }, [])

  const fetchDetail = async (id: number) => {
    if (expandedId === id) {
      setExpandedId(null)
      setDetail(null)
      return
    }
    setExpandedId(id)
    setDetail(null)
    setDetailLoading(true)
    try {
      const response = await fetch(`/api/v1/divination/history/${id}`)
      const data = await response.json()
      if (response.ok) {
        setDetail(data.data)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setDetailLoading(false)
    }
  }

  const deleteRecord = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!window.confirm(t('确定删除这条起卦记录？'))) return
    try {
      const response = await fetch(`/api/v1/divination/history/${id}`, { method: 'DELETE' })
      if (response.ok) {
        setItems((prev) => prev.filter((it) => it.id !== id))
        setTotal((prev) => prev - 1)
        if (expandedId === id) {
          setExpandedId(null)
          setDetail(null)
        }
      }
    } catch (err) {
      console.error(err)
    }
  }

  /**
   * 清空全部历史。不可恢复，所以确认框里带上条数，避免误点。
   * 删除范围是**全部**记录，不受当前分页影响（后端按整表删）。
   */
  const clearHistory = async () => {
    if (!window.confirm(t(`确定删除全部 ${total} 条起卦记录？\n\n此操作不可恢复。`))) return

    setClearing(true)
    try {
      const response = await fetch('/api/v1/divination/history', { method: 'DELETE' })
      const data = await response.json().catch(() => null)
      if (!response.ok) {
        setError(data?.error || t('清空历史失败'))
        return
      }
      setItems([])
      setTotal(0)
      setHasMore(false)
      setOffset(0)
      setExpandedId(null)
      setDetail(null)
      setError(null)
    } catch (err) {
      console.error(err)
      setError(t('网络请求失败，请检查后端服务是否已启动'))
    } finally {
      setClearing(false)
    }
  }

  const formatTime = (iso: string) => {
    if (!iso) return ''
    const d = new Date(iso)
    const now = new Date()
    const diff = now.getTime() - d.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return t('刚刚')
    if (minutes < 60) return t(`${minutes} 分钟前`)
    if (hours < 24) return t(`${hours} 小时前`)
    if (days < 7) return t(`${days} 天前`)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }

  return (
    <PageShell title={t('起卦历史')} subtitle={t('回顾往昔卦象，审视心路历程')}>
      {/* 统计信息 */}
      <div className="mb-8">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex flex-wrap items-center justify-between gap-3"
        >
          <div className="text-sm text-xuanjing-paper-dim">
            {t('共')} <span className="font-bold text-xuanjing-gold">{total}</span> {t('条起卦记录')}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/divination"
              className={BTN_PRIMARY}
            >
              {t('+ 再起一卦')}
            </Link>
            {total > 0 && (
              <button
                type="button"
                onClick={clearHistory}
                disabled={clearing}
                className={BTN_DANGER}
              >
                {clearing ? t('清空中…') : t('清空历史')}
              </button>
            )}
          </div>
        </motion.div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="mb-6">
          <div className="rounded-2xl border border-xuanjing-cinnabar/30 bg-xuanjing-cinnabar/15 p-4 text-center">
            <p className="text-xuanjing-cinnabar-text">{error}</p>
            <button
              onClick={() => fetchHistory(true)}
              className="mt-3 text-sm text-xuanjing-cinnabar-text underline"
            >
              {t('重试')}
            </button>
          </div>
        </div>
      )}

      {/* 历史记录列表 */}
      <div className="space-y-4">
        {loading && items.length === 0 ? (
          <div className="py-20 text-center text-xuanjing-paper-dim">
            {t('加载中...')}
          </div>
        ) : items.length === 0 && !error ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="py-20 text-center"
          >
            <div className="mb-4 font-heading text-6xl text-xuanjing-gold/25">卦</div>
            <p className="mb-6 text-xuanjing-paper-dim">{t('尚无起卦记录')}</p>
            <Link
              to="/divination"
              className={`inline-block ${BTN_PRIMARY}`}
            >
              {t('开始第一次起卦')}
            </Link>
          </motion.div>
        ) : (
          <>
            {items.map((item, idx) => {
              const tone = fortuneTone(item.fortune_label || item.fortune_level || '平')
              const isExpanded = expandedId === item.id

              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  className="cursor-pointer overflow-hidden rounded-2xl border border-xuanjing-line bg-xuanjing-paper/5"
                  onClick={() => fetchDetail(item.id)}
                >
                  {/* 卡片头部 */}
                  <div className="p-5">
                    <div className="mb-3 flex items-center justify-between">
                      <div className="flex flex-wrap items-center gap-3">
                        <div className="font-heading text-2xl font-bold text-xuanjing-paper">
                          {t(item.primary_display || item.primary_hexagram)}
                        </div>
                        <span className="text-xuanjing-gold">→</span>
                        <div className="font-heading text-2xl font-bold text-xuanjing-paper">
                          {t(item.secondary_display || item.secondary_hexagram)}
                        </div>
                      </div>
                      <div className={`rounded-full px-3 py-1 text-xs font-semibold ${tone.text} ${tone.bg}`}>
                        {t(item.fortune_label || item.fortune_level)} · {item.fortune_score}
                      </div>
                    </div>

                    <p className="mb-3 line-clamp-2 text-sm leading-relaxed text-xuanjing-paper-dim">
                      {t(item.main_interpretation)}
                    </p>

                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="text-xs text-xuanjing-paper-dim">
                        {item.input_method === '时间'
                          ? t('按时间')
                          : item.input_method === '数字'
                            ? t('按数字')
                            : t('铜钱摇卦')} · {formatTime(item.query_timestamp)}
                      </div>
                      <button
                        onClick={(e) => deleteRecord(item.id, e)}
                        className="text-xs text-xuanjing-paper-dim transition-colors duration-200 hover:text-xuanjing-cinnabar-text"
                      >
                        {t('删除')}
                      </button>
                    </div>
                  </div>

                  {/* 展开详情 */}
                  <AnimatePresence>
                    {isExpanded && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="overflow-hidden border-t border-xuanjing-line"
                      >
                        <div className="p-5">
                          {detailLoading ? (
                            <div className="py-4 text-center text-sm text-xuanjing-paper-dim">
                              {t('加载详情中...')}
                            </div>
                          ) : detail ? (
                            <div className="space-y-4">
                              {item.keywords && item.keywords.length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                  {item.keywords.map((kw, i) => (
                                    <span
                                      key={i}
                                      className="rounded-full bg-xuanjing-gold/15 px-3 py-1 text-xs text-xuanjing-paper"
                                    >
                                      {t(kw)}
                                    </span>
                                  ))}
                                </div>
                              )}

                              <div className="pt-2 text-center text-xs text-xuanjing-paper-dim">
                                {t('点击卡片收起详情')}
                              </div>
                            </div>
                          ) : null}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )
            })}

            {/* 加载更多 */}
            {hasMore && (
              <div className="pt-4 text-center">
                <button
                  onClick={() => fetchHistory(false)}
                  disabled={loading}
                  className={BTN_OUTLINE}
                >
                  {loading ? t('加载中...') : t('加载更多')}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </PageShell>
  )
}

export default HistoryPage
