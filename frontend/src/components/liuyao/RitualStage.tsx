import type { CSSProperties } from 'react'

import Coin, { COIN_SLOT_X } from './Coin'
import TurtleShell from './TurtleShell'
import { TURTLE_ASSET } from '../../config/turtle'
import type { CoinFace } from '../../types/liuyao'

/** 一轮摇卦的阶段 */
export type RitualPhase =
  | 'idle'      // 待摇
  | 'shaking'   // 龟壳摇晃
  | 'flying'    // 铜钱弹出、排开、旋转
  | 'settled'   // 铜钱停定

interface RitualStageProps {
  phase: RitualPhase
  /** 本轮三枚铜钱的正反面（由服务端定下） */
  faces: CoinFace[] | null
  /** 每轮自增，用作 key 以重播动画 */
  roundKey: number
  /** 停定后是否在铜钱下方标出正反 */
  showFaces: boolean
}

export default function RitualStage({ phase, faces, roundKey, showFaces }: RitualStageProps) {
  const flying = phase === 'flying' || phase === 'settled'

  // 出钱口的纵坐标由素材配置决定：换成自己的图后只需调 config，不必改 CSS
  const mouthTop = TURTLE_ASSET?.mouthTopPx ?? 176
  const stageStyle = { '--mouth-top': `${mouthTop}px` } as unknown as CSSProperties

  return (
    <div className="ritual-stage" style={stageStyle}>
      <div className="ritual-coin-layer">
        {/* 只在飞出阶段挂载铜钱：动画随挂载即刻开始。
            若先挂载、之后再补上动画类，动画会从"中途开始"起算，
            在虚拟时钟（无头截图）下会停在起始帧而完全看不见。 */}
        {flying &&
          [0, 1, 2].map((i) => (
            <Coin
              key={`${roundKey}-${i}`}
              index={i}
              face={faces ? faces[i] : null}
              flying={flying}
            />
          ))}
      </div>

      <TurtleShell shaking={phase === 'shaking'} />

      {/* 停定后标出三枚的正反：铜钱图形在小尺寸下不够一目了然。
          位置在 CSS 里由 --mouth-top 推导，换素材时会跟着出钱口一起移动。 */}
      {showFaces && faces && (
        <div className="ritual-face-layer">
          {faces.map((face, i) => (
            <span
              key={i}
              className={`absolute w-[78px] -translate-x-1/2 text-center font-heading text-lg ${
                face === '背' ? 'text-xuanjing-gold-bright' : 'text-xuanjing-paper-dim'
              }`}
              style={{ left: `${COIN_SLOT_X[i]}px` }}
            >
              {face}
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
