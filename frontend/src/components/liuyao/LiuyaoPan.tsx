import YaoBars from './YaoBars'
import type { LiuyaoPan } from '../../types/liuyao'
import { useLanguage } from '../../i18n'

interface LiuyaoPanProps {
  pan: LiuyaoPan
}

const POSITION_NAMES = ['初', '二', '三', '四', '五', '上']

/** 完整卦盘：四柱、卦名、世应、伏神，以及逐爻的六神／六亲／纳甲／变爻 */
export default function LiuyaoPanView({ pan }: LiuyaoPanProps) {
  const { t } = useLanguage()
  const rows = [...pan.yaos].reverse()          // 自上爻至初爻
  const fuByPosition = new Map(pan.fu_shen.map((f) => [f.position, f]))

  return (
    <div className="space-y-5">
      {/* 四柱与月建日建：六爻断卦的时间基准 */}
      <div className="glass-card rounded-3xl border border-xuanjing-line p-5">
        <h3 className="mb-3 font-heading text-lg font-semibold text-xuanjing-gold">{t('四柱')}</h3>
        <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm">
          <span className="text-xuanjing-paper">
            {t(pan.si_zhu.year.gan_zhi)}年　{t(pan.si_zhu.month.gan_zhi)}月　
            {t(pan.si_zhu.day.gan_zhi)}日　{t(pan.si_zhu.hour.gan_zhi)}时
          </span>
          <span className="text-xuanjing-paper-dim">
            {t('月建')} <span className="text-xuanjing-gold">{t(pan.month_branch)}</span>
          </span>
          <span className="text-xuanjing-paper-dim">
            {t('日建')} <span className="text-xuanjing-gold">{t(pan.day_branch)}</span>
          </span>
          <span className="text-xuanjing-paper-dim">
            {t('旬空')} <span className="text-xuanjing-cinnabar-text">{t(pan.kong_wang.join(''))}</span>
          </span>
        </div>
        {pan.question && (
          <p className="mt-3 text-xs text-xuanjing-paper-faint">{t('所问')}：{t(pan.question)}</p>
        )}
      </div>

      {/* 卦名与世应 */}
      <div className="glass-card rounded-3xl border border-xuanjing-line p-5">
        <div className="flex flex-wrap items-baseline gap-x-6 gap-y-3">
          <div>
            <span className="mr-3 text-xs text-xuanjing-paper-faint">{t('本卦')}</span>
            <span className="font-heading text-2xl text-xuanjing-paper">{t(pan.ben.name)}</span>
            <span className="ml-3 font-heading text-xl text-xuanjing-gold">{pan.ben.symbols}</span>
          </div>
          {!pan.is_jing && (
            <div>
              <span className="mr-3 text-xs text-xuanjing-paper-faint">{t('变卦')}</span>
              <span className="font-heading text-2xl text-xuanjing-paper">{t(pan.bian.name)}</span>
              <span className="ml-3 font-heading text-xl text-xuanjing-gold">{pan.bian.symbols}</span>
            </div>
          )}
        </div>

        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-xuanjing-paper-dim">
          <span>
            {t(pan.ben.palace)}{t('宫')}{t(pan.ben.stage)}（{t(pan.ben.palace_element)}）
          </span>
          <span>
            {t('世在')}<span className="text-xuanjing-gold">{t(pan.ben.shi)}</span>{t('爻')}　
            {t('应在')}<span className="text-xuanjing-gold">{t(pan.ben.ying)}</span>{t('爻')}
          </span>
          <span>
            {pan.is_jing
              ? t('静卦（六爻不动）')
              : t(`动爻 ${pan.moving_lines.map((n) => POSITION_NAMES[n - 1]).join('、')}`)}
          </span>
        </div>

        {/* 伏神 */}
        <div className="mt-4 border-t border-xuanjing-line pt-3 text-xs">
          <span className="text-xuanjing-paper-faint">{t('伏神')}：</span>
          {pan.fu_shen.length === 0 ? (
            <span className="text-xuanjing-paper-dim">{t('无（六亲齐全）')}</span>
          ) : (
            <span className="text-xuanjing-gold">
              {t(
                pan.fu_shen
                  .map(
                    (f) =>
                      `${f.na_jia}${f.relative}（伏于第 ${f.position} 爻，飞神 ${f.fei_shen.na_jia}${f.fei_shen.relative}）`,
                  )
                  .join('；'),
              )}
            </span>
          )}
        </div>
      </div>

      {/* 卦盘表 */}
      <div className="glass-card overflow-x-auto rounded-3xl border border-xuanjing-line p-5">
        <div className="pan-grid">
          <div className="pan-head">{t('六神')}</div>
          <div className="pan-head">{t('六亲')}</div>
          <div className="pan-head">{t('纳甲')}</div>
          <div className="pan-head">{t('五行')}</div>
          <div className="pan-head">{t('世应')}</div>
          <div className="pan-head">{t('卦画')}</div>
          <div className="pan-head">{t('变卦')}</div>

          {rows.map((yao) => {
            const fu = fuByPosition.get(yao.position)
            const marks = [yao.is_shi ? t('世') : '', yao.is_ying ? t('应') : '', yao.is_kong ? t('空') : '']
              .filter(Boolean)
              .join('')

            return (
              <div key={yao.position} className="contents">
                <div className="pan-cell pan-cell-dim">{t(yao.god)}</div>

                <div className="pan-cell">
                  <div>{t(yao.relative)}</div>
                  {fu && (
                    <div className="text-[11px] text-xuanjing-gold-deep">
                      {t(fu.na_jia)}
                      {t(fu.relative)}
                    </div>
                  )}
                </div>

                <div className="pan-cell">
                  <span className="font-heading">{t(yao.na_jia)}</span>
                  <span className="ml-1 text-[11px] text-xuanjing-paper-faint">
                    {POSITION_NAMES[yao.position - 1]}
                    {yao.is_yang ? '九' : '六'}
                  </span>
                </div>

                <div className="pan-cell pan-cell-dim">{t(yao.element)}</div>

                <div
                  className={`pan-cell ${marks.includes(t('空')) ? 'text-xuanjing-cinnabar-text' : 'text-xuanjing-gold'}`}
                >
                  {marks || '　'}
                </div>

                <YaoBars isYang={yao.is_yang} movingMark={null} className="!gap-0" />

                <div className="pan-cell">
                  {yao.bian ? (
                    <span className="text-xuanjing-paper-dim">
                      <span className="font-heading text-xuanjing-gold-deep">{t(yao.bian.na_jia)}</span>{' '}
                      {t(yao.bian.relative)}
                      <span className="ml-1 text-[11px]">{t(yao.bian.element)}</span>
                    </span>
                  ) : (
                    <span className="text-xuanjing-paper-faint">{t('静')}</span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
