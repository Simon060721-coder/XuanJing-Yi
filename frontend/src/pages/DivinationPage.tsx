import React, { useState } from 'react'
import { motion } from 'framer-motion'
import DivinationForm from '../components/DivinationForm'
import DivinationResult from '../components/DivinationResult'

interface DivinationData {
  status: string
  data: any
  timestamp: string
}

function DivinationPage() {
  const [result, setResult] = useState<DivinationData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleDivination = async (formData: any) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/divination/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data?.error || '占卜接口返回异常，请稍后重试')
        return
      }

      setResult(data)
    } catch (fetchError) {
      console.error('占卜失败:', fetchError)
      setError('网络请求失败，请检查后端服务是否已启动。')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-5xl font-heading font-bold text-xuanjing-cream text-center mb-12">
          卜卦求签
        </h1>
      </motion.div>

      <div className="max-w-4xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div>
          <DivinationForm onSubmit={handleDivination} loading={loading} />
        </div>
        <div>
          {loading ? (
            <motion.div
              className="glass-card flex items-center justify-center h-96"
              animate={{ opacity: [0.75, 1, 0.75] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="text-xuanjing-accent text-lg">卦象生成中...</div>
            </motion.div>
          ) : error ? (
            <motion.div
              className="glass-card p-8 h-96 flex items-center justify-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="text-center">
                <p className="text-xuanjing-accent text-lg mb-4">占卜请求失败</p>
                <p className="text-xuanjing-gray-light">{error}</p>
              </div>
            </motion.div>
          ) : result ? (
            <DivinationResult data={result} onReset={() => { setResult(null); setError(null) }} />
          ) : (
            <motion.div
              className="glass-card flex items-center justify-center h-96"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              <p className="text-xuanjing-gray-light text-center px-6">
                选择方式开始占卜，卦象将在此显示
              </p>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DivinationPage
