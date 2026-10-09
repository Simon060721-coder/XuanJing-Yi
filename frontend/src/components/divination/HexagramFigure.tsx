import { useLanguage } from '../../i18n'

interface HexYao {
  position: number
  position_name: string
  is_yang: boolean
  moving: boolean
  changed_is_yang: boolean
}

interface HexagramFigureProps {
  /** 六爻，自初爻起（索引 0 = 初爻） */
  yaos: HexYao[]
  /** primary 画本卦，changed 画变卦（动爻取翻面后的阴阳） */
  variant: 'primary' | 'changed'
  /** 体卦名（与 upper/lower 比较以决定哪些爻着暖金色） */
  bodyTrigram: string
  upperTrigram: string
  lowerTrigram: string
  /** 是否播放"逐根浮现"动效 */
  animate?: boolean
  /** 是否正在播放动爻翻转（本卦用） */
  flipping?: boolean
  /** 是否着色区分体用（成卦最后一步才亮出来） */
  tiyong?: boolean
}

/**
 * 卦画（六爻，自下而上）。
 *
 * 颜色即信息：**体卦暖金（主）、用卦青色（客）**，动爻另加朱砂标记。
 * 上卦为四五六爻、下卦为初二三爻，据此判断每一爻属于体还是用。
 */
export default function HexagramFigure({
  yaos,
  variant,
  bodyTrigram,
  upperTrigram,
  lowerTrigram,
  animate = false,
  flipping = false,
  tiyong = false,
}: HexagramFigureProps) {
  const { t } = useLanguage()
  const bodyIsUpper = bodyTrigram === upperTrigram
  const bodyIsLower = bodyTrigram === lowerTrigram

  return (
    <div className="flex flex-col-reverse gap-2">
      {yaos.map((y, i) => {
        const isUpperLine = y.position >= 4
        const isBody = (bodyIsUpper && isUpperLine) || (bodyIsLower && !isUpperLine)
        const yang = variant === 'primary' ? y.is_yang : y.changed_is_yang

        const cls = ['hex-line']
        if (variant === 'changed') cls.push('hex-line-changed')
        // 未到分体用那一步时一律暖金，避免提前泄露"哪一卦是体"
        else if (!tiyong || isBody) cls.push('hex-line-body')
        else cls.push('hex-line-use')
        if (animate) cls.push('hex-line-in')
        if (flipping && y.moving) cls.push('hex-flip')

        return (
          <div key={y.position} className="flex items-center gap-2.5">
            <span className="w-3 text-right text-[11px] leading-none text-xuanjing-paper-faint">
              {t(y.position_name)}
            </span>
            <span className="flex w-[86px] gap-2">
              {yang ? (
                <span
                  className={cls.join(' ')}
                  style={{ flex: 1, animationDelay: animate ? `${i * 70}ms` : undefined }}
                />
              ) : (
                <>
                  <span
                    className={cls.join(' ')}
                    style={{ flex: 1, animationDelay: animate ? `${i * 70}ms` : undefined }}
                  />
                  <span
                    className={cls.join(' ')}
                    style={{ flex: 1, animationDelay: animate ? `${i * 70}ms` : undefined }}
                  />
                </>
              )}
            </span>
            <span className="w-[34px] text-[11px] leading-none text-xuanjing-cinnabar-text">
              {variant === 'primary' && y.moving ? (y.is_yang ? t('○ 动') : t('× 动')) : ''}
            </span>
          </div>
        )
      })}
    </div>
  )
}
