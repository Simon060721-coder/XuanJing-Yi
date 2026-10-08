interface YaoBarsProps {
  isYang: boolean
  /** 尚未摇出的爻位 */
  pending?: boolean
  /** 动爻：老阳画○，老阴画× */
  movingMark?: '○' | '×' | null
  /** 是否高亮（当前正在摇的一爻） */
  active?: boolean
  className?: string
}

/** 爻的卦画。阳爻一整条，阴爻两段中间留缺口。 */
export default function YaoBars({
  isYang,
  pending = false,
  movingMark = null,
  active = false,
  className = '',
}: YaoBarsProps) {
  const rowClass = [
    'yao-row',
    pending ? 'yao-row-pending' : '',
    active ? 'yao-row-active' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <div className={rowClass}>
      <div className="yao-bars">
        {isYang ? (
          <span className="yao-bar yao-bar-full" />
        ) : (
          <>
            <span className="yao-bar yao-bar-yin" />
            <span className="yao-bar yao-bar-yin" />
          </>
        )}
      </div>
      <span className="w-5 text-center text-sm text-xuanjing-cinnabar-text">
        {movingMark ?? ''}
      </span>
    </div>
  )
}
