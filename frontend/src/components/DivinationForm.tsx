import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface DivinationFormProps {
  onSubmit: (data: any) => void
  loading: boolean
}

function DivinationForm({ onSubmit, loading }: DivinationFormProps) {
  const [method, setMethod] = useState<'time' | 'numbers'>('time')
  const [timestamp, setTimestamp] = useState(new Date().toISOString().slice(0, 16))
  const [num1, setNum1] = useState('')
  const [num2, setNum2] = useState('')
  const [num3, setNum3] = useState('')
  const [question, setQuestion] = useState('')
  const [validationError, setValidationError] = useState<string | null>(null)

  const validate = (): boolean => {
    setValidationError(null)

    if (method === 'numbers') {
      const n1 = parseInt(num1)
      const n2 = parseInt(num2)
      const n3 = parseInt(num3)

      if (!num1 || !num2 || !num3) {
        setValidationError('请填写全部三个数字')
        return false
      }
      if (isNaN(n1) || isNaN(n2) || isNaN(n3)) {
        setValidationError('请输入有效的数字')
        return false
      }
      if (n1 < 1 || n1 > 99 || n2 < 1 || n2 > 99 || n3 < 1 || n3 > 99) {
        setValidationError('每个数字需在 1-99 之间')
        return false
      }
    }

    return true
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    if (method === 'time') {
      onSubmit({
        query_type: '梅花易数',
        input_method: '时间',
        timestamp: new Date(timestamp).toISOString(),
        question: question.trim(),
      })
    } else {
      onSubmit({
        query_type: '梅花易数',
        input_method: '数字',
        num1: parseInt(num1),
        num2: parseInt(num2),
        num3: parseInt(num3),
        question: question.trim(),
      })
    }
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="glass-card border border-xuanjing-wood/30 rounded-3xl p-8"
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
    >
      <h2 className="text-2xl font-heading font-semibold text-xuanjing-cream mb-6">选择起卦方式</h2>

      {/* 方式选择 */}
      <div className="mb-8 flex gap-6">
        <label className="flex items-center gap-3 cursor-pointer group">
          <input
            type="radio"
            name="method"
            value="time"
            checked={method === 'time'}
            onChange={(e) => setMethod(e.target.value as 'time')}
            className="w-4 h-4 accent-xuanjing-accent"
          />
          <span className="text-xuanjing-cream group-hover:text-xuanjing-accent transition-colors duration-200">按时间</span>
        </label>
        <label className="flex items-center gap-3 cursor-pointer group">
          <input
            type="radio"
            name="method"
            value="numbers"
            checked={method === 'numbers'}
            onChange={(e) => setMethod(e.target.value as 'numbers')}
            className="w-4 h-4 accent-xuanjing-accent"
          />
          <span className="text-xuanjing-cream group-hover:text-xuanjing-accent transition-colors duration-200">按数字</span>
        </label>
      </div>

      {/* 占卜问题（可选） */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mb-6"
      >
        <label className="block text-xuanjing-cream mb-2 text-sm">心中所问（选填）</label>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          maxLength={50}
          className="w-full bg-white/10 text-xuanjing-cream px-4 py-2.5 border border-xuanjing-wood/30 rounded-2xl backdrop-blur-sm placeholder-xuanjing-gray-light/50 focus:border-xuanjing-accent/50 focus:outline-none transition-colors duration-200"
          placeholder="默想你想问的事，如：近期事业运势如何？"
        />
      </motion.div>

      {/* 时间输入 */}
      {method === 'time' && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-6"
        >
          <label className="block text-xuanjing-cream mb-2 text-sm">选择日期和时间</label>
          <input
            type="datetime-local"
            value={timestamp}
            onChange={(e) => setTimestamp(e.target.value)}
            className="w-full bg-white/10 text-xuanjing-cream px-4 py-2.5 border border-xuanjing-wood/30 rounded-2xl backdrop-blur-sm focus:border-xuanjing-accent/50 focus:outline-none transition-colors duration-200"
          />
          <p className="mt-2 text-xs text-xuanjing-gray-light leading-relaxed">
            选择你想占卜的时刻。系统将根据年、月、日、时推算卦象。
            也可以不选，默认使用当前时间。
          </p>
        </motion.div>
      )}

      {/* 数字输入 */}
      {method === 'numbers' && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="mb-6 space-y-4"
        >
            {/* 引导提示 */}
            <div
              className="rounded-2xl p-4 mb-2"
              style={{
                backgroundColor: 'rgba(147, 97, 66, 0.15)',
                border: '1px solid rgba(147, 97, 66, 0.35)',
              }}
            >
              <p className="text-sm font-semibold mb-1.5" style={{ color: '#936142' }}>如何选择数字？</p>
              <ul className="text-xs space-y-1 leading-relaxed" style={{ color: '#B7A08A' }}>
                <li>- 心中默想所问之事，随口说出或脑海中浮现的数字即可</li>
                <li>- 也可以用年月日拆分，如 2026 年 6 月 27 日输入 26、6、27</li>
                <li>- 看到的号码、车牌、门牌号等皆可使用，如 328 输入 3、2、8</li>
              </ul>
            </div>

            <div>
              <label className="block text-xuanjing-cream mb-2 text-sm">第一个数字 <span className="text-xuanjing-gray-light">（1-99，对应天）</span></label>
              <input
                type="number"
                min="1"
                max="99"
                value={num1}
                onChange={(e) => { setNum1(e.target.value); setValidationError(null) }}
                className="w-full bg-white/10 text-xuanjing-cream px-4 py-2.5 border border-xuanjing-wood/30 rounded-2xl backdrop-blur-sm placeholder-xuanjing-gray-light/50 focus:border-xuanjing-accent/50 focus:outline-none transition-colors duration-200"
                placeholder="如：26"
              />
            </div>
            <div>
              <label className="block text-xuanjing-cream mb-2 text-sm">第二个数字 <span className="text-xuanjing-gray-light">（1-99，对应地）</span></label>
              <input
                type="number"
                min="1"
                max="99"
                value={num2}
                onChange={(e) => { setNum2(e.target.value); setValidationError(null) }}
                className="w-full bg-white/10 text-xuanjing-cream px-4 py-2.5 border border-xuanjing-wood/30 rounded-2xl backdrop-blur-sm placeholder-xuanjing-gray-light/50 focus:border-xuanjing-accent/50 focus:outline-none transition-colors duration-200"
                placeholder="如：6"
              />
            </div>
            <div>
              <label className="block text-xuanjing-cream mb-2 text-sm">第三个数字 <span className="text-xuanjing-gray-light">（1-99，对应人）</span></label>
              <input
                type="number"
                min="1"
                max="99"
                value={num3}
                onChange={(e) => { setNum3(e.target.value); setValidationError(null) }}
                className="w-full bg-white/10 text-xuanjing-cream px-4 py-2.5 border border-xuanjing-wood/30 rounded-2xl backdrop-blur-sm placeholder-xuanjing-gray-light/50 focus:border-xuanjing-accent/50 focus:outline-none transition-colors duration-200"
                placeholder="如：27"
              />
            </div>
          </motion.div>
      )}

      {/* 验证错误提示 */}
      <AnimatePresence>
        {validationError && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="mb-4 text-amber-400 text-sm text-center"
          >
            {validationError}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 提交按钮 */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-xuanjing-accent text-xuanjing-cream font-semibold py-3 rounded-2xl border border-xuanjing-cream/20 hover:bg-xuanjing-red transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? '卦象生成中...' : '开始占卜'}
      </button>
    </motion.form>
  )
}

export default DivinationForm
