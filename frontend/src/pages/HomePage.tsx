import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

function HomePage() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: 'easeOut' },
    },
  }

  return (
    <motion.div
      className="min-h-screen flex flex-col items-center justify-center text-center"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-6xl md:text-7xl font-heading font-bold text-xuanjing-cream mb-6">
          玄镜易
        </h1>
      </motion.div>

      <motion.div variants={itemVariants} className="max-w-2xl">
        <p className="text-xl md:text-2xl text-xuanjing-accent mb-4 font-light leading-relaxed">
          一扇通往东方古智的数字之门
        </p>
        <p className="text-lg text-xuanjing-gray-light mb-8">
          将千年易学转化为精确的算法，为你诠释天地运行的奥秘
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="flex gap-6 mt-12">
        <Link
          to="/divination"
          className="px-8 py-3 bg-xuanjing-accent text-xuanjing-cream font-semibold rounded-2xl border border-xuanjing-cream/20 hover:bg-xuanjing-red transition-colors duration-300"
        >
          开始占卜
        </Link>
        <button className="px-8 py-3 bg-xuanjing-accent text-xuanjing-cream font-semibold rounded-2xl border border-xuanjing-cream/20 hover:bg-xuanjing-red transition-colors duration-300">
          了解更多
        </button>
      </motion.div>

      <motion.div
        variants={itemVariants}
        className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl w-full"
      >
        {[
          { title: '精确算法', desc: '基于传统易学精确计算' },
          { title: '古风美学', desc: '极简而沉浸的视觉语言' },
          { title: '诗意解读', desc: '深思且富有意蕴的文案' },
        ].map((item, idx) => (
          <div key={idx} className="glass-card border border-xuanjing-wood/20 p-6 rounded-3xl">
            <h3 className="text-xuanjing-accent text-lg font-semibold mb-2">{item.title}</h3>
            <p className="text-xuanjing-gray-light text-sm">{item.desc}</p>
          </div>
        ))}
      </motion.div>
    </motion.div>
  )
}

export default HomePage
