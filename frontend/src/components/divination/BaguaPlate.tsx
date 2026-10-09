import type { CSSProperties } from 'react'
import { useLanguage } from '../../i18n'

interface BaguaPlateProps {
  /** 待命时缓慢自转 */
  spinning: boolean
  /** 起卦中：减速停 + 微暗 */
  casting: boolean
  /** 成卦前那一下全暗 */
  dimmed: boolean
  /** 点亮的卦名（上下卦），在盘缘高亮 */
  lit: string[]
}

/** 先天八卦方位：乾上坤下、离左坎右（上南下北）。
 *  角度按屏幕坐标（0°=右，顺时针增大，-90°=顶）。 */
const TRIGRAM_RING: Array<{ name: string; symbol: string; number: number; angle: number }> = [
  { name: '乾', symbol: '☰', number: 1, angle: -90 },
  { name: '巽', symbol: '☴', number: 5, angle: -45 },
  { name: '坎', symbol: '☵', number: 6, angle: 0 },
  { name: '艮', symbol: '☶', number: 7, angle: 45 },
  { name: '坤', symbol: '☷', number: 8, angle: 90 },
  { name: '震', symbol: '☳', number: 4, angle: 135 },
  { name: '离', symbol: '☲', number: 3, angle: 180 },
  { name: '兑', symbol: '☱', number: 2, angle: -135 },
]

const CX = 200
const CY = 200
const R = 178
const RIM_R = 150
const PIT_R = 20

/**
 * 青铜八卦盘：与六爻青铜龟甲同材质（暗青铜 + 绿锈 + 左上来光），
 * 八卦为**刻线**（暗槽 + 亮缘），先天方位排列。中间是太极。
 *
 * 待命时缓慢自转（60s 一圈，几乎看不出在动，只看得出"活着"）。
 */
export default function BaguaPlate({ spinning, casting, dimmed, lit }: BaguaPlateProps) {
  const { t } = useLanguage()
  return (
    <div
      className={`bagua-wrap ${spinning && !casting ? 'bagua-spin' : ''} ${casting ? 'bagua-settle' : ''} ${dimmed ? 'bagua-dim' : ''}`}
      style={{ '--lit-count': String(lit.length) } as unknown as CSSProperties}
    >
      <svg viewBox="0 0 400 400" className="h-auto w-full" role="img" aria-label={t('八卦盘')}>
        <defs>
          {/* 盘面比龟甲更暗：大面积平滑金属若用得亮，会读成镜子而不是法器 */}
          <radialGradient id="xjPlateGrad" cx="34%" cy="24%" r="84%">
            <stop offset="0%" className="plate-stop-honey" />
            <stop offset="26%" className="plate-stop-warm" />
            <stop offset="60%" className="plate-stop-mid" />
            <stop offset="88%" className="plate-stop-dark" />
            <stop offset="100%" className="plate-stop-deep" />
          </radialGradient>
          <radialGradient id="xjPlateSheen" cx="30%" cy="22%" r="60%">
            <stop offset="0%" className="plate-stop-gloss" />
            <stop offset="100%" className="plate-stop-gloss-out" />
          </radialGradient>
          <filter id="xjPlateSoft" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="6" />
          </filter>
          <filter id="xjPlateGrain" x="0" y="0" width="100%" height="100%">
            <feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch" />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          {/* 噪点必须裁进圆内：不裁的话方框边缘会在深底上显出一道矩形暗带 */}
          <clipPath id="xjPlateClip">
            <circle cx={CX} cy={CY} r={R} />
          </clipPath>
        </defs>

        {/* 盘体 */}
        <circle cx={CX} cy={CY} r={R} className="bagua-disc" />
        <circle cx={CX} cy={CY} r={R} fill="url(#xjPlateSheen)" />

        {/* 绿锈斑 */}
        <g className="bagua-patina">
          <ellipse cx={118} cy={120} rx={62} ry={46} />
          <ellipse cx={294} cy={272} rx={70} ry={52} />
          <ellipse cx={288} cy={112} rx={40} ry={30} />
          <ellipse cx={112} cy={286} rx={36} ry={26} />
        </g>

        {/* 刻线：外缘双圈 */}
        <circle cx={CX} cy={CY} r={R - 8} className="bagua-rim" />
        <circle cx={CX} cy={CY} r={RIM_R} className="bagua-rim" />

        {/* 八卦刻位 */}
        {TRIGRAM_RING.map((t) => {
          const a = (t.angle * Math.PI) / 180
          const x = CX + RIM_R * Math.cos(a)
          const y = CY + RIM_R * Math.sin(a)
          const on = lit.includes(t.name)
          return (
            <g key={t.name} transform={`translate(${x} ${y})`} className={on ? 'bagua-lit' : ''}>
              <text
                className="bagua-symbol"
                textAnchor="middle"
                dominantBaseline="central"
              >
                {t.symbol}
              </text>
              {/* 先天数沿**半径方向**向内偏一点，不能用固定 dy——
                  刻符是绕圆布置的，固定向下偏移会把数字推出盘外。 */}
              <text
                className="bagua-number"
                textAnchor="middle"
                dominantBaseline="central"
                x={(-Math.cos(a) * 34).toFixed(1)}
                y={(-Math.sin(a) * 34).toFixed(1)}
              >
                {t.number}
              </text>
            </g>
          )
        })}

        {/* 太极（中心） */}
        <g className="bagua-taiji" opacity="0.9">
          <circle cx={CX} cy={CY} r={PIT_R + 46} className="bagua-taiji-ring" />
          <circle cx={CX} cy={CY} r={PIT_R + 34} fill="none" className="bagua-rim" />
          {/* 阴阳双鱼：两段半圆 + 两段小鱼眼弧 */}
          <path
            d={`M ${CX} ${CY - PIT_R} A ${PIT_R} ${PIT_R} 0 0 1 ${CX} ${CY + PIT_R} `
              + `A ${PIT_R / 2} ${PIT_R / 2} 0 0 1 ${CX} ${CY} `
              + `A ${PIT_R / 2} ${PIT_R / 2} 0 0 0 ${CX} ${CY - PIT_R} Z`}
            className="bagua-yin"
          />
          <circle cx={CX} cy={CY - PIT_R / 2} r={PIT_R / 6} className="bagua-yang-dot" />
          <circle cx={CX} cy={CY + PIT_R / 2} r={PIT_R / 6} className="bagua-yin-dot" />
        </g>

        {/* 高光 + 噪点 */}
        <ellipse cx={128} cy={96} rx={96} ry={40} className="bagua-gloss" transform="rotate(-16 128 96)" />
        <g clipPath="url(#xjPlateClip)">
          <rect x="0" y="0" width="400" height="400" filter="url(#xjPlateGrain)" className="bagua-grain" />
        </g>
      </svg>
    </div>
  )
}
