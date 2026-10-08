import type { ReactNode } from 'react'

interface PageShellProps {
  title: string
  /** 标题下的一行说明 */
  subtitle?: string
  /** 副标题上方的小字（如英文名），可选 */
  kicker?: string
  /** 标题字号：入口页可用 lg */
  size?: 'md' | 'lg'
  /** 标题下的金色短分隔线，默认显示 */
  divider?: boolean
  children: ReactNode
}

/**
 * 全站统一的页面骨架。
 *
 * 统一这四件事（此前每页各写各的，翻页时左右边缘与节奏会跳动）：
 *   · 水平内边距 px-6 —— 与页头/页脚一致；此前页面用 px-2，比页头宽出 16px
 *   · 内容宽度 max-w-6xl —— 与页头/页脚对齐；此前 3xl/4xl/6xl 混用
 *   · 竖向节奏 py-10 —— 此前 8/10/12 三种
 *   · 页头规格 —— 标题字号、副标题间距、分隔线统一
 *
 * 注意：骨架只管"外框"。仪式页（六爻的龟壳、梅花的八卦盘）的内部气质各自保留，
 * 统一的是它们周围的边距与节奏，不是它们的表现语言。
 */
export default function PageShell({
  title,
  subtitle,
  kicker,
  size = 'md',
  divider = true,
  children,
}: PageShellProps) {
  const titleClass =
    size === 'lg'
      ? 'font-heading text-6xl font-bold text-xuanjing-paper md:text-7xl'
      : 'font-heading text-5xl font-bold text-xuanjing-paper'

  return (
    <div className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-6xl">
        <header className="mb-10 text-center">
          <h1 className={titleClass}>{title}</h1>
          {kicker && (
            <p className="mt-3 text-lg font-light tracking-wide text-xuanjing-gold">{kicker}</p>
          )}
          {subtitle && (
            <p className={`text-sm tracking-wide text-xuanjing-paper-dim ${kicker ? 'mt-1' : 'mt-3'}`}>
              {subtitle}
            </p>
          )}
          {divider && (
            <div className="mx-auto mt-6 h-0.5 w-20 rounded-full bg-xuanjing-gold/40" />
          )}
        </header>

        {children}
      </div>
    </div>
  )
}
