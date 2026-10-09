import { useEffect } from 'react'

import type { LiuyaoPan, TossResult, Trigram } from '../../types/liuyao'
import { useLanguage } from '../../i18n'

interface HexagramProgressProps {
  /** 已摇出的爻，自初爻起 */
  yaos: TossResult[]
  /** 八卦表，由后端 `/liuyao/trigrams` 提供，不在前端另抄一份 */
  trigrams: Trigram[]
  /** 六爻齐后的卦盘 */
  pan: LiuyaoPan | null
}

/** 老阳(9)与少阳(7)为阳，老阴(6)与少阴(8)为阴 */
const isYang = (value: number) => value === 7 || value === 9

/** 三爻取卦：bits 自下而上，(1,1,0) 即兑 */
function trigramOf(slice: TossResult[], trigrams: Trigram[]): Trigram | null {
  if (slice.length < 3) return null
  const bits = slice.map((y) => (isYang(y.value) ? 1 : 0))
  return trigrams.find((t) => t.bits.every((b, i) => b === bits[i])) ?? null
}

/** 自下而上画三爻；未摇到的位置以极淡的横线占位 */
function TrigramLines({ yaos }: { yaos: TossResult[] }) {
  return (
    <div className="flex flex-col-reverse gap-1.5 pt-0.5">
      {[0, 1, 2].map((i) => {
        const yao = yaos[i]
        const yang = yao ? isYang(yao.value) : null
        return (
          <span key={i} className="flex items-center gap-1.5">
            <span
              className="yao-bars"
              style={{ width: 64, opacity: yang === null ? 0.18 : 1 }}
            >
              {yang === false ? (
                <>
                  <span className="yao-bar yao-bar-yin" />
                  <span className="yao-bar yao-bar-yin" />
                </>
              ) : (
                <span className="yao-bar yao-bar-full" />
              )}
            </span>
            <span className="w-3 text-center text-[11px] leading-none text-xuanjing-cinnabar-text">
              {yao?.moving ? (yao.value === 9 ? '○' : '×') : ''}
            </span>
          </span>
        )
      })}
    </div>
  )
}

interface TrigramRowProps {
  label: string
  hint: string
  slice: TossResult[]
  trigram: Trigram | null
}

function TrigramRow({ label, hint, slice, trigram }: TrigramRowProps) {
  const { t } = useLanguage()
  return (
    <div className="flex items-start gap-4">
      <TrigramLines yaos={slice} />
      <div className="min-w-0 flex-1">
        <div className="text-xs text-xuanjing-paper-faint">
          {t(label)}（{t(hint)}）
        </div>
        {trigram ? (
          <div className="mt-1.5 font-heading text-lg text-xuanjing-gold">
            {t(trigram.name)}
            <span className="ml-1.5 text-base">{trigram.symbol}</span>
            <span className="ml-2 font-body text-xs text-xuanjing-paper-dim">
              {t(trigram.nature)}·{t(trigram.element)}
            </span>
          </div>
        ) : (
          <div className="mt-2 text-xs text-xuanjing-paper-faint">
            {t(`还差 ${3 - slice.length} 爻`)}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * 卦象成形进度。
 *
 * 六爻成卦的过程原本是个黑箱——摇满六次才知道结果。这张卡把中间过程显性化：
 * 初二三爻定**内卦**、四五六爻定**外卦**，所以每摇一爻都能给出即时反馈。
 *
 * 取卦只用三爻的阴阳位，与后端 `constants.TRIGRAMS` 的 bits 对齐；
 * 六爻齐后再与后端装卦结果比对一次，不一致会打印告警（正常时沉默）。
 */
export default function HexagramProgress({ yaos, trigrams, pan }: HexagramProgressProps) {
  const { t } = useLanguage()
  const inner = trigramOf(yaos.slice(0, 3), trigrams)
  const outer = trigramOf(yaos.slice(3, 6), trigrams)
  const innerName = inner?.name ?? null
  const outerName = outer?.name ?? null

  // 自检：前端自算的内外卦应与后端装卦结果一致。不一致说明三爻取卦
  // 的位数约定或八卦表有偏差——这类偏差不会报错，只会静静显示错的卦。
  useEffect(() => {
    if (!pan) return
    if (innerName && innerName !== pan.ben.lower) {
      console.warn(`[玄镜易] 内卦自算「${innerName}」与后端「${pan.ben.lower}」不一致`)
    }
    if (outerName && outerName !== pan.ben.upper) {
      console.warn(`[玄镜易] 外卦自算「${outerName}」与后端「${pan.ben.upper}」不一致`)
    }
  }, [pan, innerName, outerName])

  return (
    <div className="glass-card h-fit rounded-3xl border border-xuanjing-line p-6">
      <div className="flex items-baseline justify-between">
        <h2 className="font-heading text-lg font-semibold text-xuanjing-gold">{t('卦象成形')}</h2>
        <span className="text-xs text-xuanjing-paper-faint">
          {t('已摇')} <span className="text-xuanjing-gold">{yaos.length}</span> / 6 {t('爻')}
        </span>
      </div>
      <p className="mb-5 mt-1 text-[11px] leading-relaxed text-xuanjing-paper-faint">
        {t('初二三爻定内卦，四五六爻定外卦')}
      </p>

      <div className="space-y-5">
        <TrigramRow label="内卦" hint="初二三" slice={yaos.slice(0, 3)} trigram={inner} />
        <TrigramRow label="外卦" hint="四五六" slice={yaos.slice(3, 6)} trigram={outer} />
      </div>

      {pan && (
        <div className="mt-6 space-y-2.5 border-t border-xuanjing-line pt-5">
          <div className="flex items-baseline justify-between">
            <span className="text-xs text-xuanjing-paper-faint">{t('本卦')}</span>
            <span className="font-heading text-base text-xuanjing-gold">
              {t(pan.ben.name)}
              <span className="ml-2 text-sm text-xuanjing-paper-dim">{pan.ben.symbols}</span>
            </span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-xs text-xuanjing-paper-faint">
              {pan.is_jing ? t('六爻皆静') : t(`动爻 ${pan.moving_lines.join('、')}`)}
            </span>
            {pan.is_jing ? (
              <span className="text-sm text-xuanjing-paper-dim">{t('无变卦')}</span>
            ) : (
              <span className="font-heading text-base text-xuanjing-gold">
                {t(pan.bian.name)}
                <span className="ml-2 text-sm text-xuanjing-paper-dim">{pan.bian.symbols}</span>
              </span>
            )}
          </div>
          <div className="flex items-baseline justify-between pt-1 text-[11px] text-xuanjing-paper-dim">
            <span>
              {t(pan.ben.palace)}{t('宫')} · {t(pan.ben.palace_element)}
            </span>
            <span>
              {t(pan.ben.stage)}　{t('世')}{pan.ben.shi} {t('应')}{pan.ben.ying}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
