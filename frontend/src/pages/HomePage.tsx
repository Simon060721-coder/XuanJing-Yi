import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'

import PageShell from '../components/PageShell'
import { BTN_PRIMARY, BTN_BRONZE, CARD } from '../styles/ui'
import { useLanguage } from '../i18n'

function HomePage() {
  const { t } = useLanguage()

  const FEATURES = [
    { title: t('正统六爻'), desc: t('纳甲、六亲、世应、伏神，依月建日建断卦') },
    { title: t('古风美学'), desc: t('极简而沉浸的视觉语言') },
    { title: t('摇卦入卦'), desc: t('龟壳摇钱，六次成卦，如临其境') },
  ]

  const container = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { staggerChildren: 0.15, delayChildren: 0.15 } },
  }

  const item = {
    hidden: { opacity: 0, y: 18 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: 'easeOut' } },
  }

  return (
    <PageShell
      title={t('玄镜易')}
      kicker={t('一扇通往东方古智的数字之门')}
      subtitle={t('将千年易学转化为精确的算法，为你诠释天地运行的奥秘')}
      size="lg"
    >
      <motion.div variants={container} initial="hidden" animate="visible" className="text-center">
        <motion.div variants={item} className="mt-10 flex flex-wrap justify-center gap-4">
          <Link to="/liuyao" className={BTN_PRIMARY}>
            {t('六爻摇卦')}
          </Link>
          <Link to="/divination" className={BTN_BRONZE}>
            {t('梅花易数')}
          </Link>
        </motion.div>

        <motion.div
          variants={item}
          className="mt-14 grid grid-cols-1 gap-6 text-left md:grid-cols-3"
        >
          {FEATURES.map((feature) => (
            <div key={feature.title} className={CARD}>
              <h3 className="mb-2 font-heading text-lg font-semibold text-xuanjing-gold">
                {feature.title}
              </h3>
              <p className="text-sm leading-relaxed text-xuanjing-paper-dim">{feature.desc}</p>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </PageShell>
  )
}

export default HomePage
