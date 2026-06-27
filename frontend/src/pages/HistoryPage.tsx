import React, { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'

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

function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [total, setTotal] = useState(0)
  const [hasMore, setHasMore] = useState(false)
  const [offset, setOffset] = useState(0)
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [detail, setDetail] = useState<any>(null)
  const [detailLoading, setDetailLoading] = useState(false)

  const limit = 10

  const fetchHistory = useCallback(async (reset = true) => {
    try {
      setLoading(true)
      setError(null)
      const currentOffset = reset ? 0 : offset
      const response = await fetch(`/api/v1/divination/history?limit=${limit}&offset=${currentOffset}`)
      const data = await response.json()

      if (!response.ok) {
        setError(data?.error || '加载历史记录失败')
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
      setError('网络请求失败，请检查后端服务是否已启动')
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
    if (!window.confirm('确定删除这条占卜记录？')) return
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

  const formatTime = (iso: string) => {
    if (!iso) return ''
    const d = new Date(iso)
    const now = new Date()
    const diff = now.getTime() - d.getTime()
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 1) return '刚刚'
    if (minutes < 60) return `${minutes} 分钟前`
    if (hours < 24) return `${hours} 小时前`
    if (days < 7) return `${days} 天前`
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }

  const getFortuneColor = (level: string) => {
    if (level === '大吉') return { color: '#34d399', bg: 'rgba(52, 211, 153, 0.15)' }
    if (level === '吉') return { color: '#4ade80', bg: 'rgba(74, 222, 128, 0.12)' }
    if (level === '平吉') return { color: '#a3e635', bg: 'rgba(163, 230, 53, 0.12)' }
    if (level === '平') return { color: '#936142', bg: 'rgba(147, 97, 66, 0.18)' }
    if (level === '凶') return { color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.15)' }
    return { color: '#f87171', bg: 'rgba(248, 113, 113, 0.15)' }
  }

  return (
    <div className="min-h-screen pb-20">
      {/* 标题区 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center pt-12 pb-10 px-6"
      >
        <h1 className="text-5xl md:text-6xl font-heading font-bold text-xuanjing-cream mb-3">
          占卜历史
        </h1>
        <p className="text-lg text-xuanjing-accent font-light">
          回顾往昔卦象，审视心路历程
        </p>
        <div className="w-20 h-0.5 bg-xuanjing-accent/40 mx-auto mt-5 rounded-full" />
      </motion.div>

      {/* 统计信息 */}
      <div className="max-w-4xl mx-auto px-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center justify-between flex-wrap gap-3"
        >
          <div className="text-xuanjing-gray-light text-sm">
            共 <span style={{ color: '#936142' }} className="font-bold">{total}</span> 条占卜记录
          </div>
          <Link
            to="/divination"
            className="px-5 py-2 bg-xuanjing-accent text-xuanjing-cream text-sm font-semibold rounded-2xl border border-xuanjing-cream/20 hover:bg-xuanjing-red transition-colors duration-300"
          >
            + 再起一卦
          </Link>
        </motion.div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="max-w-4xl mx-auto px-6 mb-6">
          <div
            className="rounded-2xl p-4 text-center"
            style={{ backgroundColor: 'rgba(248, 113, 113, 0.12)', border: '1px solid rgba(248, 113, 113, 0.3)' }}
          >
            <p style={{ color: '#f87171' }}>{error}</p>
            <button
              onClick={() => fetchHistory(true)}
              className="mt-3 text-sm underline"
              style={{ color: '#f87171' }}
            >
              重试
            </button>
          </div>
        </div>
      )}

      {/* 历史记录列表 */}
      <div className="max-w-4xl mx-auto px-6 space-y-4">
        {loading && items.length === 0 ? (
          <div className="text-center py-20 text-xuanjing-gray-light">
            加载中...
          </div>
        ) : items.length === 0 && !error ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20"
          >
            <div className="text-6xl mb-4 opacity-30">卦</div>
            <p className="text-xuanjing-gray-light mb-6">尚无占卜记录</p>
            <Link
              to="/divination"
              className="inline-block px-6 py-2.5 bg-xuanjing-accent text-xuanjing-cream font-semibold rounded-2xl border border-xuanjing-cream/20 hover:bg-xuanjing-red transition-colors duration-300"
            >
              开始第一次占卜
            </Link>
          </motion.div>
        ) : (
          <>
            {items.map((item, idx) => {
              const fc = getFortuneColor(item.fortune_label || item.fortune_level || '平')
              const isExpanded = expandedId === item.id

              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  className="rounded-2xl overflow-hidden cursor-pointer"
                  style={{
                    backgroundColor: 'rgba(245, 231, 208, 0.06)',
                    border: '1px solid rgba(245, 231, 208, 0.1)',
                  }}
                  onClick={() => fetchDetail(item.id)}
                >
                  {/* 卡片头部 */}
                  <div className="p-5">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3 flex-wrap">
                        <div className="text-2xl font-heading font-bold text-xuanjing-cream">
                          {item.primary_display || item.primary_hexagram}
                        </div>
                        <span className="text-xuanjing-accent">→</span>
                        <div className="text-2xl font-heading font-bold text-xuanjing-cream">
                          {item.secondary_display || item.secondary_hexagram}
                        </div>
                      </div>
                      <div
                        className="text-xs font-semibold px-3 py-1 rounded-full"
                        style={{ color: fc.color, backgroundColor: fc.bg }}
                      >
                        {item.fortune_label || item.fortune_level} · {item.fortune_score}
                      </div>
                    </div>

                    <p className="text-xuanjing-gray-light text-sm leading-relaxed line-clamp-2 mb-3">
                      {item.main_interpretation}
                    </p>

                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="text-xs text-xuanjing-gray-light">
                        {item.input_method === '时间' ? '按时间' : '按数字'} · {formatTime(item.query_timestamp)}
                      </div>
                      <button
                        onClick={(e) => deleteRecord(item.id, e)}
                        className="text-xs text-xuanjing-gray-light hover:text-red-400 transition-colors duration-200"
                      >
                        删除
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
                        className="overflow-hidden"
                        style={{ borderTop: '1px solid rgba(245, 231, 208, 0.1)' }}
                      >
                        <div className="p-5">
                          {detailLoading ? (
                            <div className="text-center text-xuanjing-gray-light text-sm py-4">
                              加载详情中...
                            </div>
                          ) : detail ? (
                            <div className="space-y-4">
                              {item.keywords && item.keywords.length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                  {item.keywords.map((kw, i) => (
                                    <span
                                      key={i}
                                      className="text-xs px-3 py-1 rounded-full"
                                      style={{
                                        backgroundColor: 'rgba(147, 97, 66, 0.2)',
                                        color: '#F5E7D0',
                                      }}
                                    >
                                      {kw}
                                    </span>
                                  ))}
                                </div>
                              )}

                              {detail.analysis_result?.aspects_layer && (
                                <div>
                                  <h4 className="text-xuanjing-accent text-sm font-semibold mb-3">多维解读</h4>
                                  <div className="space-y-2">
                                    {Object.entries(detail.analysis_result.aspects_layer).map(([k, v]: [string, any]) => {
                                      const labelMap: Record<string, string> = {
                                        career: '事业', wealth: '财运', relationship: '感情',
                                        health: '健康', study: '学业'
                                      }
                                      const scoreColor = v.score >= 70 ? '#4ade80' : v.score >= 55 ? '#936142' : '#fbbf24'
                                      return (
                                        <div
                                          key={k}
                                          className="rounded-xl p-3"
                                          style={{ backgroundColor: 'rgba(245, 231, 208, 0.04)' }}
                                        >
                                          <div className="flex items-center justify-between mb-1.5">
                                            <span className="text-xuanjing-cream text-xs font-semibold">
                                              {labelMap[k] || k}
                                            </span>
                                            <span className="text-xs font-bold" style={{ color: scoreColor }}>
                                              {v.score} {v.trend}
                                            </span>
                                          </div>
                                          <p className="text-xs text-xuanjing-gray-light leading-relaxed">
                                            {v.advice}
                                          </p>
                                        </div>
                                      )
                                    })}
                                  </div>
                                </div>
                              )}

                              <div className="text-xs text-xuanjing-gray-light text-center pt-2">
                                点击卡片收起详情
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
              <div className="text-center pt-4">
                <button
                  onClick={() => fetchHistory(false)}
                  disabled={loading}
                  className="px-6 py-2.5 text-xuanjing-accent text-sm border border-xuanjing-accent/30 rounded-2xl hover:bg-xuanjing-accent/10 transition-colors duration-200 disabled:opacity-50"
                >
                  {loading ? '加载中...' : '加载更多'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default HistoryPage
