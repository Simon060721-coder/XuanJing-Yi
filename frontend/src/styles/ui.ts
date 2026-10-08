/**
 * 全站 UI 原语 —— **唯一来源**。
 *
 * 此前每个页面各写一份 class 串，于是同一类控件在五页里有五种 px/py/圆角/内距，
 * 翻页时按钮和卡片的尺寸会轻微跳动，看着"跳脱"。改这里即全站生效，
 * 不要再在页面里内联这些串。
 */

/** 玻璃卡：分组的容器。全站统一 p-6，不再有 p-8 的特例 */
export const CARD = 'glass-card rounded-3xl border border-xuanjing-line p-6'

/**
 * 按钮只分**主/次/三级/描边**四档，共用同一套几何：
 * `rounded-2xl` + `px-6 py-3` + `text-sm`。
 *
 * 主次**只靠颜色区分**，不靠尺寸——早先主按钮漏了 `text-sm`，于是并排时
 * 主按钮的字比次按钮大一号，看着不齐（实测 16px vs 14px）。
 */

/** 主操作：填充金 */
export const BTN_PRIMARY =
  'rounded-2xl border border-xuanjing-gold-bright/30 bg-xuanjing-gold px-6 py-3 text-sm font-semibold text-xuanjing-ink transition-colors duration-300 hover:bg-xuanjing-gold-bright disabled:cursor-not-allowed disabled:opacity-50'

/** 次操作：纸色浮层 */
export const BTN_SECONDARY =
  'rounded-2xl border border-xuanjing-paper/20 bg-xuanjing-paper/10 px-6 py-3 text-sm font-semibold text-xuanjing-paper transition-colors duration-300 hover:bg-xuanjing-paper/15 disabled:cursor-not-allowed disabled:opacity-50'

/** 三级操作：仅描边，用于"重新起卦"这类 */
export const BTN_GHOST =
  'rounded-2xl border border-xuanjing-line px-6 py-3 text-sm text-xuanjing-paper-dim transition-colors duration-300 hover:text-xuanjing-paper disabled:opacity-50'

/** 金色描边按钮：次级动作（加载更多、起卦方式） */
export const BTN_OUTLINE =
  'rounded-2xl border border-xuanjing-gold/30 px-6 py-3 text-sm text-xuanjing-gold transition-colors duration-200 hover:bg-xuanjing-gold/10 disabled:cursor-not-allowed disabled:opacity-40'

/**
 * 青铜按钮：与梅花易数的八卦盘同色（该色直接采样自盘体）。
 * 与主按钮同为"填充式"，靠**色相**而非尺寸区分，几何与其余按钮完全一致。
 */
export const BTN_BRONZE =
  'rounded-2xl border border-xuanjing-gold-deep/40 bg-xuanjing-bronze px-6 py-3 text-sm font-semibold text-xuanjing-paper transition-colors duration-300 hover:bg-xuanjing-bronze-light disabled:cursor-not-allowed disabled:opacity-50'

/** 危险操作：朱砂描边。用于不可恢复的删除（清空历史） */
export const BTN_DANGER =
  'rounded-2xl border border-xuanjing-cinnabar/40 px-6 py-3 text-sm text-xuanjing-cinnabar-text transition-colors duration-200 hover:bg-xuanjing-cinnabar/10 disabled:cursor-not-allowed disabled:opacity-40'

/** 紧凑输入：用于并排的三个小数字框 */
export const FIELD_COMPACT =
  'rounded-2xl border border-xuanjing-line bg-xuanjing-ink-3/60 py-2 text-center text-xuanjing-paper placeholder-xuanjing-paper-faint transition-colors duration-200 focus:border-xuanjing-gold/60 focus:outline-none focus:ring-2 focus:ring-xuanjing-gold/25'

/** 选项胶囊（问事类别、起卦方式都用它，含选中/未选两态） */
export const CHIP = 'rounded-full border px-3 py-1.5 text-xs transition-colors duration-200 disabled:opacity-50'
export const CHIP_ON = 'border-xuanjing-gold/50 bg-xuanjing-gold/20 text-xuanjing-gold'
export const CHIP_OFF = 'border-xuanjing-line text-xuanjing-paper-dim hover:text-xuanjing-paper'

/** 文本输入：全站统一圆角框，不再有下划线式的特例 */
export const FIELD =
  'w-full rounded-2xl border border-xuanjing-line bg-xuanjing-ink-3/60 px-4 py-2.5 text-xuanjing-paper placeholder-xuanjing-paper-faint transition-colors duration-200 focus:border-xuanjing-gold/60 focus:outline-none focus:ring-2 focus:ring-xuanjing-gold/25 disabled:opacity-50'
