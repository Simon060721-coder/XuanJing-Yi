import PageShell from '../components/PageShell'
import { CARD } from '../styles/ui'
import { useLanguage } from '../i18n'

const SECTION = `${CARD} mb-6`

function AboutPage() {
  const { t } = useLanguage()
  return (
    <PageShell title={t('关于玄镜易')} kicker="XuanJing Yi">
      <section className={SECTION}>
        <h2 className="mb-4 font-heading text-2xl font-semibold text-xuanjing-gold">{t('何为玄镜易')}</h2>
        <p className="mb-3 text-sm leading-relaxed text-xuanjing-paper">
          {t('玄镜易是一扇通往东方古智的数字之门。我们将千年易学的核心智慧，转化为精确而克制的算法，为你诠释天地运行的奥秘。')}
        </p>
        <p className="text-sm leading-relaxed text-xuanjing-paper-dim">
          {t('玄镜者，洞见之镜也；易者，变化之道也。我们希望以现代技术为镜，照见古老易学中蕴含的时序、节律与人生智慧。')}
        </p>
      </section>

      <section className={SECTION}>
        <h2 className="mb-4 font-heading text-2xl font-semibold text-xuanjing-gold">{t('起卦方法')}</h2>
        <div className="space-y-5 text-sm text-xuanjing-paper">
          <div>
            <h3 className="mb-2 font-semibold text-xuanjing-gold">{t('六爻（纳甲筮法）')}</h3>
            <p className="leading-relaxed text-xuanjing-paper-dim">
              {t('三枚铜钱摇掷六次，自初爻而上依次装卦。以背为阳，三背为老阳、三字为老阴，老阳老阴为动爻。本卦由六爻阴阳定，翻转动爻得出变卦。')}
            </p>
          </div>
          <div>
            <h3 className="mb-2 font-semibold text-xuanjing-gold">{t('梅花易数 · 按时间起卦')}</h3>
            <p className="leading-relaxed text-xuanjing-paper-dim">
              {t('上卦为（年＋月＋日）除八取余，下卦为（年＋月＋日＋时）除八取余，动爻为（年＋月＋日＋时）除六取余。余数为零时取八（或六）。年取年支序数、时取时支序数，二者由四柱干支推得。此法是**取此刻**之数。')}
            </p>
            <p className="mt-2 text-xs leading-relaxed text-xuanjing-paper-faint">
              {t('说明：古法时间起卦用农历月日取数，本版暂用公历月日（年支、时支已为干支准确值），此偏差如实标注，待农历换算补齐后修正。')}
            </p>
          </div>
          <div>
            <h3 className="mb-2 font-semibold text-xuanjing-gold">{t('梅花易数 · 按数字起卦')}</h3>
            <p className="leading-relaxed text-xuanjing-paper-dim">
              {t('上卦为三数之和除八取余，下卦为后两数之和除八取余，动爻为三数之和除六取余。数可由**点盘三下**而定——取点击那一刻的时间碎片，你决定"何时"，不决定"是几"；也可以自己报数，用眼前看到的数字（车牌、日期皆可）。')}
            </p>
          </div>
          <div>
            <h3 className="mb-2 font-semibold text-xuanjing-gold">{t('体用与吉凶')}</h3>
            <p className="leading-relaxed text-xuanjing-paper-dim">
              {t('动爻所在之卦为「用」，另一卦为「体」。以体用五行生克断吉凶：用生体为得助、体克用为费力有成、体生用为耗泄、用克体为受制。主卦由上下卦合成六十四卦，变卦由翻转动爻得出。')}
            </p>
          </div>
        </div>
      </section>

      <section className={SECTION}>
        <h2 className="mb-4 font-heading text-2xl font-semibold text-xuanjing-gold">{t('解读如何构成')}</h2>
        <div className="space-y-4 text-sm">
          <div>
            <h3 className="mb-2 font-semibold text-xuanjing-gold">{t('六爻')}</h3>
            <p className="leading-relaxed text-xuanjing-paper-dim">
              {t('先按所问之事选取用神，再看月建、日建、旬空、伏神、进神退神、六冲六合等传统依据，逐条列出判断与权重，汇总为吉凶分档。')}
            </p>
            <p className="mt-2 text-xs leading-relaxed text-xuanjing-paper-faint">
              {t('如实说明：其中少数数值为工程设定的权重，不是经典数据——它用于排序与分档，换一套权重数值就会变化，而依据清单不变。界面上亦一并标注，请以依据为准。')}
            </p>
          </div>
          <div>
            <h3 className="mb-2 font-semibold text-xuanjing-gold">{t('梅花易数')}</h3>
            <p className="leading-relaxed text-xuanjing-paper-dim">
              {t('以体用五行生克定吉凶：用生体（得助）、体克用（费力有成）、体用比和（平稳）、体生用（耗泄）、用克体（受制）。主卦与变卦按上下卦合成，动爻所在之卦即用卦。')}
            </p>
          </div>
        </div>
      </section>

      <section className={SECTION}>
        <h2 className="mb-4 font-heading text-2xl font-semibold text-xuanjing-gold">{t('使用提示')}</h2>
        <ul className="space-y-2 text-sm leading-relaxed text-xuanjing-paper-dim">
          <li>· {t('起卦是观心的镜子，结果在于参考而不在于执念')}</li>
          <li>· {t('心中所问越清晰，所感越敏锐，解读也越贴近实情')}</li>
          <li>· {t('同一问题不宜反复起卦，时移事易，卦象随之而变')}</li>
          <li>· {t('重大决策仍需理性判断，卦象提示吉凶倾向，不替代行动')}</li>
        </ul>
      </section>

      <section className={SECTION}>
        <h2 className="mb-4 font-heading text-2xl font-semibold text-xuanjing-gold">{t('用途声明')}</h2>
        <p className="text-sm leading-relaxed text-xuanjing-paper-dim">
          {t('本项目为易学文化研究与算法演示而开发。排盘与断卦结果源自传统规则的推演，仅供参考与学习，不构成任何现实决策建议，亦不提供商业占卜服务。')}
        </p>
      </section>

      <p className="mt-10 text-center text-xs text-xuanjing-paper-dim">
        {t('愿这一面玄镜，照见你心中的明路')}
      </p>
    </PageShell>
  )
}

export default AboutPage
