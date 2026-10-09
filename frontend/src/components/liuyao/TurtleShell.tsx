import { useMemo, useState } from 'react'
import type { CSSProperties } from 'react'

import { TURTLE_ASSET } from '../../config/turtle'
import { useLanguage } from '../../i18n'

interface TurtleShellProps {
  /** 正在摇晃 */
  shaking: boolean
}

/* ── 侧视图几何 ────────────────────────────────────────────────────────
   侧视给出的是龟甲最有辨识度的轮廓：隆起的背弓、底缘外翻成锯齿的缘盾、
   可见的壳体厚度。

   曾试过"3/4 俯视 + 甲片网格"，结果是**退步**：做成了正交俯视的扁平椭圆
   加一层蜂窝网，没有透视收缩、没有穹顶体积，等于退回"画了花纹的盘子"。
   参考照片的 3/4 视是有强烈透视的，不是把图案贴在椭圆上就能得到。

   刻意做成**左右不对称**：峰顶偏后、前端陡起、后端平缓外翻。

   坐标按 viewBox 0 0 340 240。**改动底部开口 cy 会连带影响铜钱落点**，
   需同步 config/turtle.ts 的 mouthTopPx（现为 176，对应开口 cy≈172）。 */
const CX = 173
const X0 = 36
const X1 = 306
/** 底缘基准线：两端略高、中间略低 */
const rimBase = (x: number) => 162 + 5 * Math.sin((Math.PI * (x - X0)) / (X1 - X0))
/** 缘盾上界。环带留 40 高，才能形成外翻的"裙边" */
const rimTop = (x: number) => rimBase(x) - 40

const TABS = 11
const tabBulge = (i: number) => (i % 2 === 0 ? 15 : 8)
const tabX = (i: number) => X0 + (i / TABS) * (X1 - X0)

/** 底缘曲线（不带 M/Z 的纯线段串）。
 *  **甲壳路径必须用它拼接，不能直接拼 tabPath()**——tabPath 末尾有 Z，
 *  在 SVG 里 Z 之后再出现 L 会从子路径起点接着画，连出一堆斜线。 */
function rimSegments(): string {
  const parts: string[] = []
  for (let i = 0; i < TABS; i += 1) {
    const x0 = tabX(i)
    const x1 = tabX(i + 1)
    const y0 = rimBase(x0)
    const y1 = rimBase(x1)
    parts.push(
      `Q ${((x0 + x1) / 2).toFixed(1)} ${(Math.max(y0, y1) + tabBulge(i)).toFixed(1)} ${x1.toFixed(1)} ${y1.toFixed(1)}`,
    )
  }
  return parts.join(' ')
}

/** 单块缘盾：自环带上界包到锯齿底缘 */
function tabPath(i: number): string {
  const x0 = tabX(i)
  const x1 = tabX(i + 1)
  const y0 = rimBase(x0)
  const y1 = rimBase(x1)
  const cy = Math.max(y0, y1) + tabBulge(i)
  return `M ${x0.toFixed(1)} ${rimTop(x0).toFixed(1)} L ${x0.toFixed(1)} ${y0.toFixed(1)} `
    + `Q ${((x0 + x1) / 2).toFixed(1)} ${cy.toFixed(1)} ${x1.toFixed(1)} ${y1.toFixed(1)} `
    + `L ${x1.toFixed(1)} ${rimTop(x1).toFixed(1)} Z`
}

/** 底缘锯齿线（用于给缘盾尖端提亮） */
function rimEdgePath(): string {
  return `M ${X0.toFixed(1)} ${rimBase(X0).toFixed(1)} ${rimSegments()}`
}

/** 背弓（右→左，便于与底缘接成闭合路径）。峰顶偏后、前端更陡 */
const ARCH_BACK =
  'C 312 134 298 104 270 82 C 248 62 214 54 176 56 C 136 58 96 70 70 90 C 44 110 30 140 36 164'

/** 肋盾沟缝的落点（x 坐标）。间距刻意不等 */
const SUTURE_XS = [84, 136, 194, 246]

/**
 * 龟甲（侧视）。两种来源：
 *
 * 1. **外部素材**（`config/turtle.ts` 里配了 TURTLE_ASSET 且文件存在）
 *    —— 直接显示你出的图，摇晃动画照旧。
 * 2. **内置矢量版**（默认，或素材加载失败时自动回退）
 *
 * 材质照实拍青铜龟甲：本体暗青铜、沟缝是磨亮的黄铜凸线。让甲片"鼓起来"
 * 靠三层：① 沟缝 = 模糊暗影 + 错开的暗线 + 浅金线；② 每块甲片中央压一枚
 * 柔光；③ 缘盾逐块填充、交替压暗，尖端提亮。
 *
 * 注意 hooks 必须全部在分支之前调用，否则素材加载失败切换分支时会打乱 hook 顺序。
 */
export default function TurtleShell({ shaking }: TurtleShellProps) {
  const { t } = useLanguage()
  const [assetFailed, setAssetFailed] = useState(false)

  const { dome, tabs, altTabs, rimEdge, costals, growth, plates, ridge } = useMemo(() => {
    const allTabs = Array.from({ length: TABS }, (_, i) => tabPath(i))
    const domePath = `M ${X0} ${rimBase(X0).toFixed(1)} ${rimSegments()} ${ARCH_BACK} Z`

    // 肋盾沟缝：像球面经线，自缘盾上界向上收拢
    const costalLines = SUTURE_XS.map((xb, i) => {
      const yb = rimTop(xb)
      const xt = CX + (xb - CX) * (i % 2 === 0 ? 0.46 : 0.36)
      const yt = 60 + Math.pow(Math.abs(xt - CX) / 130, 1.7) * 26
      const cx = (xb + xt) / 2 + (xb > CX ? 16 : -16)
      const cy = (yb + yt) / 2
      return `M ${xb.toFixed(1)} ${yb.toFixed(1)} Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${xt.toFixed(1)} ${yt.toFixed(1)}`
    })

    // 每块肋盾中央的柔光位置：取相邻两条沟缝的中线
    const bounds = [X0, ...SUTURE_XS, X1]
    const plateList = bounds.slice(0, -1).map((x0, i) => {
      const x1 = bounds[i + 1]
      const mid = (x0 + x1) / 2
      return {
        x: mid,
        y: 96 + Math.abs(mid - CX) * 0.06,
        rx: (x1 - x0) * 0.42,
        ry: 40 - Math.abs(mid - CX) * 0.1,
        rot: (mid - CX) * 0.13,
      }
    })

    // 生长纹：与底缘大致平行，间距不等
    const growthLines = [0.14, 0.3, 0.44, 0.6, 0.74].map((f, i) => {
      const half = (126 + i * 2) * Math.sqrt(Math.max(0.06, 1 - f * 0.72))
      const y = 134 - f * 78
      return `M ${(CX - half).toFixed(1)} ${(y + 10).toFixed(1)} Q ${CX} ${(y + 22).toFixed(1)} ${(CX + half).toFixed(1)} ${(y + 8).toFixed(1)}`
    })

    // 椎盾脊：顶部一条分节带
    const ridgeTicks = Array.from({ length: 6 }, (_, i) => {
      const t = 0.16 + (i / 5) * 0.68
      const x = X0 + t * (X1 - X0)
      const yTop = 56 + Math.pow(Math.abs(x - CX) / 140, 2) * 62
      return `M ${x.toFixed(1)} ${yTop.toFixed(1)} L ${x.toFixed(1)} ${(yTop + 15).toFixed(1)}`
    })

    return {
      dome: domePath,
      tabs: allTabs,
      altTabs: allTabs.filter((_, i) => i % 2 === 1),
      rimEdge: rimEdgePath(),
      costals: costalLines,
      growth: growthLines,
      plates: plateList,
      ridge: ridgeTicks,
    }
  }, [])

  const wrapperClass = `ritual-turtle ${shaking ? 'ritual-shell-shaking' : 'ritual-shell-idle'}`

  const asset = TURTLE_ASSET
  if (asset && !assetFailed) {
    const width = asset.width ?? 336
    return (
      <div
        className={wrapperClass}
        style={{ '--turtle-w': `${width}px` } as unknown as CSSProperties}
      >
        <img
          src={asset.src}
          alt={t('龟甲')}
          className={`ritual-asset${asset.shadow ? ' ritual-asset-shadow' : ''}`}
          onError={() => {
            console.info(
              `[玄镜易] 未找到龟甲素材 ${asset.src}，已回退到内置矢量版。` +
              '将图片放到 frontend/public/assets/ 下即可自动启用。',
            )
            setAssetFailed(true)
          }}
        />
      </div>
    )
  }

  return (
    <div className={wrapperClass}>
      <svg viewBox="0 0 340 240" className="h-auto w-full" role="img" aria-label={t('龟甲')}>
        <defs>
          <radialGradient id="xjGroundShadow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" className="shell-stop-shadow" />
            <stop offset="100%" className="shell-stop-shadow-out" />
          </radialGradient>
          {/* 背弓受光：左上亮、右下暗 */}
          <linearGradient id="xjDome" x1="0.14" y1="0.06" x2="0.68" y2="1">
            <stop offset="0%" className="shell-stop-light" />
            <stop offset="20%" className="shell-stop-honey" />
            <stop offset="50%" className="shell-stop-warm" />
            <stop offset="78%" className="shell-stop-mid" />
            <stop offset="100%" className="shell-stop-dark" />
          </linearGradient>
          <linearGradient id="xjBand" x1="0.1" y1="0" x2="0.35" y2="1">
            <stop offset="0%" className="shell-stop-warm" />
            <stop offset="55%" className="shell-stop-mid" />
            <stop offset="100%" className="shell-stop-dark" />
          </linearGradient>
          <radialGradient id="xjGlossGrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" className="shell-stop-gloss" />
            <stop offset="100%" className="shell-stop-gloss-out" />
          </radialGradient>
          <radialGradient id="xjPlate" cx="50%" cy="42%" r="62%">
            <stop offset="0%" className="shell-stop-plate" />
            <stop offset="100%" className="shell-stop-plate-out" />
          </radialGradient>
          <clipPath id="xjDomeClip">
            <path d={dome} />
          </clipPath>
          <filter id="xjSoft" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="6" />
          </filter>
          <filter id="xjSoft2" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="2.6" />
          </filter>
          {/* 噪点：矢量图最缺表面颗粒，加一层破掉塑料感 */}
          <filter id="xjGrain" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
        </defs>

        <ellipse cx={CX + 4} cy={196} rx={148} ry={18} className="shell-shadow" />

        <path d={dome} className="shell-dome" />

        <g clipPath="url(#xjDomeClip)">
          {/* 甲片柔光：先铺，让每块甲片有凸面感 */}
          {plates.map((p, i) => (
            <ellipse
              key={`p${i}`}
              cx={p.x}
              cy={p.y}
              rx={Math.max(8, p.rx)}
              ry={Math.max(10, p.ry)}
              transform={`rotate(${p.rot.toFixed(1)} ${p.x.toFixed(1)} ${p.y.toFixed(1)})`}
              className="shell-plate"
            />
          ))}

          <g className="shell-growth">
            {growth.map((d, i) => (
              <path key={`g${i}`} d={d} />
            ))}
          </g>

          {/* 肋盾沟缝：模糊暗影 → 错开的暗线 → 浅金线，三层叠出深沟与凸起 */}
          <g>
            {costals.map((d, i) => (
              <path key={`cs${i}`} d={d} className="shell-groove-soft" />
            ))}
            {costals.map((d, i) => (
              <path key={`cd${i}`} d={d} className="shell-suture-dark" />
            ))}
            {costals.map((d, i) => (
              <path key={`cl${i}`} d={d} className="shell-suture-light" />
            ))}
          </g>

          {/* 椎盾脊 */}
          <g className="shell-ridge">
            {ridge.map((d, i) => (
              <path key={`v${i}`} d={d} />
            ))}
          </g>

          {/* 背弓受光带：收窄压低，太亮会像抛光塑料 */}
          <ellipse cx={142} cy={84} rx={82} ry={17} className="shell-gloss" transform="rotate(-7 142 84)" />
          <ellipse cx={122} cy={74} rx={30} ry={7} className="shell-gloss" transform="rotate(-9 122 74)" />

          {/* 下缘向内收暗 */}
          <ellipse cx={CX} cy={176} rx={150} ry={28} className="shell-under" />

          <rect x="0" y="0" width="340" height="240" filter="url(#xjGrain)" className="shell-grain" />
        </g>

        {/* 缘盾：逐块填充，奇数块压暗一档，尖端提亮 */}
        <g>
          {tabs.map((d, i) => (
            <path key={`t${i}`} d={d} className="shell-band" />
          ))}
          {altTabs.map((d, i) => (
            <path key={`a${i}`} d={d} className="shell-band-alt" />
          ))}
        </g>
        <path d={rimEdge} className="shell-rim-tip" fill="none" />

        {/* 背弓轮廓与上缘反光 */}
        <path d={dome} className="shell-outline" fill="none" />
        <path
          d="M 40 160 C 34 138 48 110 72 91 C 97 71 137 59 177 57 C 215 55 249 63 271 83 C 297 105 311 135 305 157"
          className="shell-rimlight"
          fill="none"
        />

        {/* 出钱口：铜钱由此落下（cy 与 config 的 mouthTopPx 对应） */}
        <ellipse cx={CX} cy={172} rx={50} ry={10} className="shell-mouth" />
        <ellipse cx={CX} cy={170} rx={38} ry={5.5} className="shell-mouth-inner" />
      </svg>
    </div>
  )
}
