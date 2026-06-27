import React from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'

interface DivinationResultProps {
  data: any
  onReset?: () => void
}

/** 维度中文名映射 */
const ASPECT_LABELS: Record<string, string> = {
  career: '事业',
  wealth: '财运',
  relationship: '感情',
  health: '健康',
  study: '学业',
}

/** 维度图标映射 */
const ASPECT_ICONS: Record<string, string> = {
  career: '💼',
  wealth: '💰',
  relationship: '❤️',
  health: '🏥',
  study: '📚',
}

/** 根据分数返回颜色类名 */
function getScoreColor(score: number): string {
  if (score >= 85) return 'text-emerald-400'
  if (score >= 70) return 'text-emerald-300'
  if (score >= 55) return 'text-xuanjing-accent'
  if (score >= 40) return 'text-amber-400'
  return 'text-xuanjing-red'
}

/** 根据趋势返回颜色 */
function getTrendColor(trend: string): string {
  if (trend === '↑') return 'text-emerald-400'
  if (trend === '↓') return 'text-xuanjing-red'
  return 'text-xuanjing-accent'
}

/** 根据吉凶标签返回颜色 */
function getFortuneColor(level: string): string {
  if (level === '大吉') return 'text-emerald-300'
  if (level === '吉') return 'text-emerald-400'
  if (level === '平吉') return 'text-emerald-400/70'
  if (level === '平') return 'text-xuanjing-accent'
  if (level === '凶') return 'text-amber-400'
  return 'text-xuanjing-red'
}

function DivinationResult({ data, onReset }: DivinationResultProps) {
  const result = data?.data ?? null
  const hexagramLayer = result?.hexagram_layer
  const analysisLayer = result?.analysis_layer
  const adviceLayer = result?.advice_layer
  const aspectsLayer = result?.aspects_layer

  if (!result || !hexagramLayer || !analysisLayer || !adviceLayer) {
    return (
      <motion.div
        className="glass-card p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <p className="text-xuanjing-cream text-center">
          未能读取卦象结果，请稍后重试。
        </p>
      </motion.div>
    )
  }

  const activeLine = Array.isArray(hexagramLayer.changing_lines) && hexagramLayer.changing_lines.length > 0
    ? hexagramLayer.changing_lines[0]
    : null

  const fortuneLabel = adviceLayer.fortune_label || analysisLayer.fortune_level

  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* 卦象层 */}
      <motion.div
        className="glass-card border border-white/10 rounded-3xl p-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
      >
        <h3 className="text-xuanjing-accent font-heading font-semibold mb-4">卦象</h3>
        <div className="flex flex-col sm:flex-row justify-between gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-xuanjing-cream mb-2">
              {hexagramLayer.primary_hexagram}
            </div>
            <p className="text-xs text-xuanjing-gray-light">主卦</p>
          </div>
          <div className="text-2xl text-xuanjing-accent self-center">→</div>
          <div className="text-center">
            <div className="text-4xl font-bold text-xuanjing-cream mb-2">
              {hexagramLayer.secondary_hexagram}
            </div>
            <p className="text-xs text-xuanjing-gray-light">变卦</p>
          </div>
        </div>
        <p className="text-xs text-xuanjing-gray-light mt-4 text-center">
          动爻：{activeLine ? `第 ${activeLine} 爻` : '无动态爻'}
        </p>
      </motion.div>

      {/* 评分层 */}
      <motion.div
        className="glass-card border border-white/10 rounded-3xl p-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        <h3 className="text-xuanjing-accent font-heading font-semibold mb-4">评分</h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-xuanjing-cream">吉凶评分</span>
            <span className="text-2xl font-bold text-xuanjing-red">{analysisLayer.fortune_score}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xuanjing-cream">评级</span>
            <span className={`text-lg font-semibold ${getFortuneColor(fortuneLabel)}`}>
              {fortuneLabel}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xuanjing-cream">五行平衡</span>
            <span className="text-xuanjing-accent">{analysisLayer.element_balance}</span>
          </div>
        </div>
      </motion.div>

      {/* 总解读层 */}
      <motion.div
        className="glass-card border border-white/10 rounded-3xl p-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.3 }}
      >
        <h3 className="text-xuanjing-accent font-heading font-semibold mb-4">解读</h3>
        <p className="text-xuanjing-cream leading-relaxed text-sm">
          {adviceLayer.main_interpretation}
        </p>
        {adviceLayer.keywords && adviceLayer.keywords.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {adviceLayer.keywords.map((keyword: string, idx: number) => (
              <span key={idx} className="text-xs bg-xuanjing-cream/10 text-xuanjing-cream px-3 py-1 rounded-full">
                {keyword}
              </span>
            ))}
          </div>
        )}
      </motion.div>

      {/* 多维度分析层 */}
      {aspectsLayer && Object.keys(aspectsLayer).length > 0 && (
        <motion.div
          className="glass-card border border-white/10 rounded-3xl p-6"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <h3 className="text-xuanjing-accent font-heading font-semibold mb-5">多维解读</h3>
          <div className="space-y-4">
            {Object.entries(aspectsLayer).map(([aspectKey, aspectData]: [string, any], idx: number) => {
              const label = ASPECT_LABELS[aspectKey] || aspectKey
              const icon = ASPECT_ICONS[aspectKey] || '📊'
              const score = aspectData?.score ?? 65
              const trend = aspectData?.trend ?? '→'
              const advice = aspectData?.advice ?? ''

              return (
                <motion.div
                  key={aspectKey}
                  className="border border-xuanjing-wood/15 rounded-2xl p-4"
                  initial={{ opacity: 0, x: idx % 2 === 0 ? -10 : 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + idx * 0.08 }}
                >
                  {/* 维度头部 */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{icon}</span>
                      <span className="text-xuanjing-cream font-semibold text-sm">{label}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className={`text-sm font-bold ${getScoreColor(score)}`}>{score}</span>
                      <span className={`text-xs font-semibold ${getTrendColor(trend)}`}>{trend}</span>
                    </div>
                  </div>

                  {/* 进度条 */}
                  <div className="w-full h-1.5 bg-xuanjing-cream/10 rounded-full mb-3 overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{
                        backgroundColor: score >= 80
                          ? 'rgba(52, 211, 153, 0.7)'
                          : score >= 60
                            ? 'rgba(165, 125, 89, 0.7)'
                            : 'rgba(245, 158, 11, 0.7)',
                      }}
                      initial={{ width: 0 }}
                      animate={{ width: `${Math.min(score, 100)}%` }}
                      transition={{ delay: 0.6 + idx * 0.08, duration: 0.6, ease: 'easeOut' }}
                    />
                  </div>

                  {/* 建议 */}
                  <p className="text-xuanjing-gray-light text-xs leading-relaxed">{advice}</p>
                </motion.div>
              )
            })}
          </div>
        </motion.div>
      )}

      {/* 快捷操作 */}
      <motion.div
        className="flex gap-3 pt-2"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        {onReset ? (
          <button
            onClick={onReset}
            className="flex-1 py-2.5 rounded-2xl text-sm font-semibold transition-colors duration-300"
            style={{
              backgroundColor: '#936142',
              color: '#F5E7D0',
              border: '1px solid rgba(245, 231, 208, 0.2)',
            }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#8B3D1A')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#936142')}
          >
            再起一卦
          </button>
        ) : (
          <Link
            to="/divination"
            className="flex-1 py-2.5 rounded-2xl text-sm font-semibold text-center transition-colors duration-300"
            style={{
              backgroundColor: '#936142',
              color: '#F5E7D0',
              border: '1px solid rgba(245, 231, 208, 0.2)',
            }}
          >
            再起一卦
          </Link>
        )}
        <Link
          to="/history"
          className="flex-1 py-2.5 rounded-2xl text-sm font-semibold text-center transition-colors duration-300"
          style={{
            backgroundColor: 'rgba(245, 231, 208, 0.1)',
            color: '#F5E7D0',
            border: '1px solid rgba(245, 231, 208, 0.2)',
          }}
        >
          查看历史
        </Link>
      </motion.div>
    </motion.div>
  )
}

export default DivinationResult
