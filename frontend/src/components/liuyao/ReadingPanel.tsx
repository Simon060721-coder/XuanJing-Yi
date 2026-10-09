import type { LiuyaoAnalysis, ShenInfo } from '../../types/liuyao'
import { useLanguage } from '../../i18n'

interface ReadingPanelProps {
  analysis: LiuyaoAnalysis
}

function levelClass(level: string): string {
  if (level === '大吉') return 'bg-xuanjing-jade/20 text-xuanjing-jade-bright'
  if (level === '吉') return 'bg-xuanjing-jade/15 text-xuanjing-jade'
  if (level === '平吉') return 'bg-xuanjing-gold/15 text-xuanjing-gold'
  if (level === '平') return 'bg-xuanjing-paper/10 text-xuanjing-paper-dim'
  return 'bg-xuanjing-cinnabar/20 text-xuanjing-cinnabar-text'
}

function signClass(sign: '+' | '-' | '0'): string {
  if (sign === '+') return 'text-xuanjing-jade'
  if (sign === '-') return 'text-xuanjing-cinnabar-text'
  return 'text-xuanjing-paper-faint'
}

function signGlyph(sign: '+' | '-' | '0'): string {
  return sign === '+' ? '＋' : sign === '-' ? '－' : '○'
}

function ShenCell({ label, info }: { label: string; info: ShenInfo }) {
  const { t } = useLanguage()
  return (
    <div className="rounded-2xl border border-xuanjing-line bg-xuanjing-paper/5 p-3">
      <div className="text-xs text-xuanjing-paper-faint">{t(label)}</div>
      <div className="mt-1 text-sm text-xuanjing-paper">
        {t(info.relative)}
        <span className="ml-1 text-xs text-xuanjing-paper-dim">{t(info.element)}</span>
      </div>
      <div className="mt-1 text-[11px] text-xuanjing-paper-faint">
        {info.present
          ? t(`现于第 ${info.positions.join('、')} 爻`)
          : t('不上卦')}
      </div>
    </div>
  )
}

/** 解读面板：结论、用神四神、逐条判断依据、建议 */
export default function ReadingPanel({ analysis }: ReadingPanelProps) {
  const { t } = useLanguage()
  const yong = analysis.yong_shen

  return (
    <div className="space-y-5">
      {/* 结论 */}
      <div className="glass-card rounded-3xl border border-xuanjing-line p-6">
        <div className="mb-4 flex flex-wrap items-center gap-3">
          <h3 className="font-heading text-lg font-semibold text-xuanjing-gold">{t('解读')}</h3>
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${levelClass(analysis.level)}`}>
            {t(analysis.level)}
          </span>
          <span className="text-xs text-xuanjing-paper-faint">
            {t('问事')}：{t(analysis.topic_label)}
            {analysis.gender ? `（${t(analysis.gender)}占）` : ''}
          </span>
        </div>

        <p className="text-sm leading-relaxed text-xuanjing-paper">{t(analysis.summary)}</p>

        {analysis.keywords.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {analysis.keywords.map((kw, i) => (
              <span
                key={i}
                className="rounded-full bg-xuanjing-gold/15 px-3 py-1 text-xs text-xuanjing-paper"
              >
                {t(kw)}
              </span>
            ))}
          </div>
        )}

        {analysis.flags.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {analysis.flags.map((flag, i) => (
              <span
                key={i}
                className="rounded-full border border-xuanjing-cinnabar/30 px-3 py-1 text-xs text-xuanjing-cinnabar-text"
              >
                {t(flag)}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* 用神与四神 */}
      <div className="glass-card rounded-3xl border border-xuanjing-line p-6">
        <h3 className="mb-4 font-heading text-lg font-semibold text-xuanjing-gold">{t('用神')}</h3>

        {yong && (
          <div className="mb-4 flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
            <span className="text-xuanjing-paper">
              {t('用神')} <span className="font-heading text-xuanjing-gold">{t(yong.relative)}</span>
            </span>
            <span className="text-xuanjing-paper-dim">
              {t('纳甲')} <span className="font-heading text-xuanjing-paper">{t(yong.na_jia)}</span>
              （{t(yong.element)}）
            </span>
            <span className="text-xuanjing-paper-dim">
              {yong.source === 'fu_shen' ? t('伏藏') : t(`第 ${yong.position} 爻`)}
            </span>
            {yong.multiple && (
              <span className="text-xuanjing-paper-faint">
                {t(`多现于第 ${yong.all_positions.join('、')} 爻`)}
              </span>
            )}
            {yong.moving && <span className="text-xuanjing-gold">{t('发动')}</span>}
            {yong.is_kong && <span className="text-xuanjing-cinnabar-text">{t('旬空')}</span>}
            {yong.is_shi && <span className="text-xuanjing-gold">{t('临世')}</span>}
          </div>
        )}

        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <ShenCell label="原神（生用神）" info={analysis.yuan_shen} />
          <ShenCell label="忌神（克用神）" info={analysis.ji_shen} />
          <ShenCell label="仇神（克原神）" info={analysis.chou_shen} />
          <div className="rounded-2xl border border-xuanjing-line bg-xuanjing-paper/5 p-3">
            <div className="text-xs text-xuanjing-paper-faint">{t('世爻（自身）')}</div>
            {analysis.shi_yao ? (
              <>
                <div className="mt-1 text-sm text-xuanjing-paper">
                  {t(analysis.shi_yao.relative)}
                  <span className="ml-1 font-heading text-xs text-xuanjing-gold">
                    {t(analysis.shi_yao.na_jia)}
                  </span>
                </div>
                <div className="mt-1 text-[11px] text-xuanjing-paper-faint">
                  {t(`第 ${analysis.shi_yao.position} 爻`)}
                  {analysis.shi_yao.moving ? ` · ${t('发动')}` : ''}
                  {analysis.shi_yao.is_kong ? ` · ${t('旬空')}` : ''}
                </div>
              </>
            ) : (
              <div className="mt-1 text-sm text-xuanjing-paper-faint">—</div>
            )}
          </div>
        </div>
      </div>

      {/* 判断依据 */}
      <div className="glass-card rounded-3xl border border-xuanjing-line p-6">
        <h3 className="mb-4 font-heading text-lg font-semibold text-xuanjing-gold">{t('判断依据')}</h3>
        <ul className="space-y-2">
          {analysis.factors.map((f, i) => (
            <li key={i} className="flex items-start gap-3 text-sm">
              <span className={`w-4 flex-none text-center ${signClass(f.sign)}`}>
                {signGlyph(f.sign)}
              </span>
              <span className="w-9 flex-none text-right text-xs tabular-nums text-xuanjing-paper-faint">
                {f.weight === 0 ? '' : f.weight > 0 ? `+${f.weight}` : f.weight}
              </span>
              <span className="text-xuanjing-paper-dim">{t(f.text)}</span>
            </li>
          ))}
        </ul>

        <p className="mt-5 border-t border-xuanjing-line pt-3 text-[11px] leading-relaxed text-xuanjing-paper-faint">
          {t('上列每一条都对应传统规则（月破、冲起、旬空填实、进神退神、飞伏生克等），可逐条核对。')}
          <strong className="text-xuanjing-paper-dim">{t('右侧分值仅为工程设定的权重之和，不是经典数据')}</strong>
          {t('——它用于排序与分档，换一套权重数值就会变化，而依据清单不变。请以依据为准。')}
        </p>
      </div>

      {/* 建议 */}
      <div className="glass-card rounded-3xl border border-xuanjing-line p-6">
        <h3 className="mb-4 font-heading text-lg font-semibold text-xuanjing-gold">{t('建议')}</h3>
        <ul className="space-y-2 text-sm leading-relaxed text-xuanjing-paper">
          {analysis.advice.map((adv, i) => (
            <li key={i} className="flex items-start gap-3">
              <span className="mt-[7px] h-1.5 w-1.5 flex-none rounded-full bg-xuanjing-gold" />
              <span>{t(adv)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
