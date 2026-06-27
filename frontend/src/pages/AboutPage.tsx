import React from 'react'
import { motion } from 'framer-motion'

function AboutPage() {
  return (
    <div className="min-h-screen py-12 px-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-3xl mx-auto"
      >
        <h1 className="text-5xl font-heading font-bold text-xuanjing-cream text-center mb-3">
          关于玄镜易
        </h1>
        <p className="text-lg text-xuanjing-accent font-light text-center mb-2">
          XuanJing Yi
        </p>
        <div className="w-20 h-0.5 bg-xuanjing-accent/40 mx-auto mb-12 rounded-full" />

        <motion.section
          className="glass-card border border-xuanjing-wood/20 rounded-3xl p-8 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <h2 className="text-2xl font-heading font-semibold text-xuanjing-accent mb-4">
            何为玄镜易
          </h2>
          <p className="text-xuanjing-cream leading-relaxed text-sm mb-3">
            玄镜易是一扇通往东方古智的数字之门。我们将千年易学的核心智慧，转化为精确而克制的算法，
            为你诠释天地运行的奥秘。
          </p>
          <p className="text-xuanjing-gray-light leading-relaxed text-sm">
            玄镜者，洞见之镜也；易者，变化之道也。我们希望以现代技术为镜，照见古老易学中蕴含的
            时序、节律与人生智慧。
          </p>
        </motion.section>

        <motion.section
          className="glass-card border border-xuanjing-wood/20 rounded-3xl p-8 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <h2 className="text-2xl font-heading font-semibold text-xuanjing-accent mb-4">
            起卦方法
          </h2>
          <div className="space-y-4 text-sm text-xuanjing-cream">
            <div>
              <h3 className="text-xuanjing-accent font-semibold mb-2">按时间起卦（梅花易数）</h3>
              <p className="text-xuanjing-gray-light leading-relaxed">
                以年、月、日、时为参数，通过数字之和取余数得到主卦、变卦与动爻。
                古法以体用关系推演吉凶，五行生克判断运势起伏。
              </p>
            </div>
            <div>
              <h3 className="text-xuanjing-accent font-semibold mb-2">按数字起卦</h3>
              <p className="text-xuanjing-gray-light leading-relaxed">
                心中默想所问之事，随机取三个 1-99 的数字。上卦为三者之和取余八，
                下卦为后两者之和取余八，动爻为三者之和取余六。
              </p>
            </div>
          </div>
        </motion.section>

        <motion.section
          className="glass-card border border-xuanjing-wood/20 rounded-3xl p-8 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h2 className="text-2xl font-heading font-semibold text-xuanjing-accent mb-4">
            多维解读
          </h2>
          <p className="text-xuanjing-gray-light leading-relaxed text-sm mb-4">
            每一卦的解读从五个维度展开：
          </p>
          <ul className="text-xuanjing-cream text-sm space-y-2">
            <li className="flex items-start gap-3">
              <span className="text-xuanjing-accent">💼</span>
              <div><span className="font-semibold">事业</span> · 职场发展、领导关系、项目成败</div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xuanjing-accent">💰</span>
              <div><span className="font-semibold">财运</span> · 正财偏财、投资理财、收支平衡</div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xuanjing-accent">❤️</span>
              <div><span className="font-semibold">感情</span> · 婚恋缘分、情感沟通、关系维护</div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xuanjing-accent">🏥</span>
              <div><span className="font-semibold">健康</span> · 身心状态、作息调养、潜在隐忧</div>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-xuanjing-accent">📚</span>
              <div><span className="font-semibold">学业</span> · 考试运、领悟力、师长助力</div>
            </li>
          </ul>
        </motion.section>

        <motion.section
          className="glass-card border border-xuanjing-wood/20 rounded-3xl p-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <h2 className="text-2xl font-heading font-semibold text-xuanjing-accent mb-4">
            使用提示
          </h2>
          <ul className="text-xuanjing-gray-light text-sm space-y-2 leading-relaxed">
            <li>· 占卜是观心的镜子，结果在于参考而不在于执念</li>
            <li>· 心中所问越清晰，所感越敏锐，解读也越贴近实情</li>
            <li>· 同一问题不宜反复占卜，时移事易，卦象随之而变</li>
            <li>· 重大决策仍需理性判断，卦象提示吉凶倾向，不替代行动</li>
          </ul>
        </motion.section>

        <p className="text-center text-xuanjing-gray-light text-xs mt-12 mb-6">
          愿这一面玄镜，照见你心中的明路
        </p>
      </motion.div>
    </div>
  )
}

export default AboutPage
