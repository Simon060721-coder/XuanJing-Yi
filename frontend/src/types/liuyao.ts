// 六爻接口的数据类型（与 backend/app/routes/liuyao_routes.py 一一对应）

export type CoinFace = '背' | '字'
export type YaoValue = 6 | 7 | 8 | 9

/** 一次摇卦的结果（三枚铜钱 → 一爻） */
export interface TossResult {
  coins: CoinFace[]
  backs: number
  value: YaoValue
  name: string          // 交 / 单 / 拆 / 重
  label: string         // 老阴 / 少阳 / 少阴 / 老阳
  yin_yang: '阴' | '阳'
  moving: boolean
  is_yang: boolean
  position: number
  position_name: string
}

export interface GanZhi {
  gan: string
  zhi: string
  gan_zhi: string
  index?: number
}

/** 四柱与月建日建 */
export interface SiZhu {
  year: GanZhi
  month: GanZhi
  day: GanZhi
  hour: GanZhi
  month_branch: string
  day_branch: string
  effective_day: string
  late_zi_adjusted: boolean
  moment: string
  kong_wang?: string[]
}

/** 卦的摘要（本卦 / 变卦） */
export interface HexagramBrief {
  name: string
  upper: string
  lower: string
  symbols: string
  palace: string
  palace_element: string
  stage: string
  shi: number
  ying: number
}

/** 变爻（动爻变出之爻） */
export interface BianYao {
  gan: string
  zhi: string
  element: string
  na_jia: string
  relative: string
}

/** 卦盘中的一爻 */
export interface PanYao {
  position: number
  position_name: string
  value: YaoValue
  name: string
  is_yang: boolean
  moving: boolean
  gan: string
  zhi: string
  element: string
  relative: string
  god: string
  is_shi: boolean
  is_ying: boolean
  is_kong: boolean
  na_jia: string
  bian: BianYao | null
}

/** 伏神（含其所伏之飞神） */
export interface FuShen {
  relative: string
  position: number
  position_name: string
  gan: string
  zhi: string
  element: string
  na_jia: string
  fei_shen: {
    na_jia: string
    zhi: string
    element: string
    relative: string
  }
}

/** 问事类别（决定用神） */
export interface TopicInfo {
  key: string
  label: string
  yong_shen: string
}

/** 八卦。bits 自下而上，(1,1,0) 即兑 —— 与后端 constants.TRIGRAMS 同源 */
export interface Trigram {
  name: string
  symbol: string
  bits: [number, number, number]
  element: string
  nature: string
}

/** 一条判断依据。每条都带传统规则说明，weight 为工程设定的权重。 */
export interface JudgmentFactor {
  kind: string
  sign: '+' | '-' | '0'
  weight: number
  text: string
  advice: string
}

/** 原神／忌神／仇神的定位 */
export interface ShenInfo {
  element: string
  relative: string
  present: boolean
  source: string | null
  positions: number[]
}

/** 用神选取与旺衰分析 */
export interface LiuyaoAnalysis {
  topic: string
  topic_label: string
  gender: string | null
  yong_shen: {
    relative: string
    source: 'yao' | 'fu_shen'
    position: number
    all_positions: number[]
    na_jia: string
    zhi: string
    element: string
    moving: boolean
    is_kong: boolean
    is_shi: boolean
    is_ying: boolean
    multiple: boolean
  } | null
  yuan_shen: ShenInfo
  ji_shen: ShenInfo
  chou_shen: ShenInfo
  shi_yao: {
    position: number
    na_jia: string
    relative: string
    element: string
    moving: boolean
    is_kong: boolean
  } | null
  month_branch: string
  day_branch: string
  factors: JudgmentFactor[]
  flags: string[]
  score: number
  level: string
  summary: string
  advice: string[]
  keywords: string[]
}

/** 完整卦盘 */
export interface LiuyaoPan {
  ben: HexagramBrief
  bian: HexagramBrief
  is_jing: boolean
  moving_lines: number[]
  yaos: PanYao[]
  day: GanZhi
  kong_wang: string[]
  fu_shen: FuShen[]
  bian_fu_shen: FuShen[]
  si_zhu: SiZhu
  month_branch: string
  day_branch: string
  moment: string
  yao_values: YaoValue[]
  question: string
  topic?: string
  gender?: string
  analysis?: LiuyaoAnalysis
}
