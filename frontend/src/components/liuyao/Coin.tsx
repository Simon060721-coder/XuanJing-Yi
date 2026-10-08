import type { CSSProperties } from 'react'

import type { CoinFace } from '../../types/liuyao'

/** 三枚铜钱的落点（相对中点，单位 px） */
export const COIN_SLOT_X = [-104, 0, 104]

/** 停定前转满的整圈数——圈数越多，停定前的减速越明显 */
const SPINS = 3

interface CoinProps {
  /** 0/1/2，决定落点与动画错峰 */
  index: number
  /** 服务端定下的正反面；未定则按背面朝向显示 */
  face: CoinFace | null
  /** 是否播出「弹出 → 排开 → 旋转 → 停定」这段动画 */
  flying: boolean
}

/**
 * 一枚方孔铜钱。
 *
 * 结构上刻意分两层：
 *   .coin       定位、透明度、落下与排开的位移
 *   .coin-spin  只做 rotateY，并持有 preserve-3d
 *
 * 不能把 3D 与 opacity 动画放在同一个元素上：`opacity` 动画或
 * `will-change: opacity` 会让 `transform-style: preserve-3d` 退化为 `flat`，
 * 于是两个面塌到同一平面，"字"面因 backface-visibility 永远被判为背面而隐藏
 * ——实际就踩过这个坑（三枚钱全部只显示背面）。
 *
 * 停定角度必须是 360 的整数倍（背）或整数倍加 180（字），否则会停在半路。
 */
export default function Coin({ index, face, flying }: CoinProps) {
  const endRot = SPINS * 360 + (face === '字' ? 180 : 0)

  const style = {
    '--slot-x': `${COIN_SLOT_X[index]}px`,
    '--end-rot': `${endRot}deg`,
    '--coin-i': String(index),
  } as unknown as CSSProperties

  return (
    <div className={`coin ${flying ? 'coin-flying' : ''}`} style={style}>
      <div className={`coin-spin ${flying ? 'coin-spin-flying' : ''}`}>
        {/* 背面：素面 + 近边缘的阳线 */}
        <div className="coin-face">
          <div className="coin-back-ring" />
          <div className="coin-hole" />
        </div>

        {/* 字面：绕 Y 轴 180°，与背面同处一个 3D 空间。读序 上右下左 = 玄镜通宝
            四字须贴边放：方孔占中央 27%，字距过小会被孔压住 */}
        <div className="coin-face coin-face-front">
          <span className="coin-char font-heading" style={{ top: '4%', left: '50%', transform: 'translateX(-50%)' }}>
            玄
          </span>
          <span className="coin-char font-heading" style={{ right: '5%', top: '50%', transform: 'translateY(-50%)' }}>
            镜
          </span>
          <span className="coin-char font-heading" style={{ bottom: '4%', left: '50%', transform: 'translateX(-50%)' }}>
            通
          </span>
          <span className="coin-char font-heading" style={{ left: '5%', top: '50%', transform: 'translateY(-50%)' }}>
            宝
          </span>
          <div className="coin-hole" />
        </div>
      </div>
    </div>
  )
}
