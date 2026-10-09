import YaoBars from './YaoBars'
import type { TossResult } from '../../types/liuyao'
import { useLanguage } from '../../i18n'

interface YaoStackProps {
  /** 已摇出的爻，自初爻起累积 */
  yaos: TossResult[]
  /** 当前正在摇的爻位（1–6），null 表示未在进行 */
  activePosition: number | null
  /** 卦盘是否已装成。六爻已足但解读尚未返回时显示「正在装卦…」 */
  panReady?: boolean
}

const POSITION_NAMES = ['初', '二', '三', '四', '五', '上']

/** 六爻堆叠：自上爻至初爻自上而下排列，随摇卦逐爻亮起 */
export default function YaoStack({ yaos, activePosition, panReady }: YaoStackProps) {
  const { t } = useLanguage()
  const byPosition = new Map(yaos.map((y) => [y.position, y]))
  const newest = yaos.length > 0 ? yaos[yaos.length - 1].position : null

  return (
    <div>
      {[6, 5, 4, 3, 2, 1].map((position) => {
        const yao = byPosition.get(position)
        const isNewest = yao != null && position === newest
        const bar = (
          <YaoBars
            isYang={yao ? yao.is_yang : false}
            pending={!yao}
            movingMark={yao ? (yao.value === 9 ? '○' : yao.value === 6 ? '×' : null) : null}
            active={activePosition === position}
            className={isNewest ? 'yao-row-new' : ''}
          />
        )

        return (
          <div key={position} className="flex items-center gap-3">
            <span className="w-6 flex-none text-center font-heading text-sm text-xuanjing-paper-faint">
              {POSITION_NAMES[position - 1]}
            </span>
            {bar}
            <span className="w-16 flex-none text-xs text-xuanjing-paper-dim">
              {yao ? `${t(yao.label)}${yao.moving ? t('·动') : ''}` : '—'}
            </span>
          </div>
        )
      })}

      <div className="mt-4 border-t border-xuanjing-line pt-3 text-xs text-xuanjing-paper-faint">
        {yaos.length < 6 ? (
          <>
            {t('已摇')} <span className="font-semibold text-xuanjing-gold">{yaos.length}</span> / 6 {t('爻')}
            <span className="ml-2">{t('自初爻向上依次装卦')}</span>
          </>
        ) : panReady ? (
          <span className="text-xuanjing-gold">{t('六爻已足 · 卦已装成')}</span>
        ) : (
          <span className="text-xuanjing-gold">{t('六爻已足，正在装卦…')}</span>
        )}
      </div>
    </div>
  )
}
