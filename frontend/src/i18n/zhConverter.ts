// 简繁转换器：基于 opencc-js，仅初始化一次。
// 只做「简体 → 繁体」，繁体状态下对界面文案与后端返回内容统一转换。
// 使用 cn2t 子路径，只打包简→繁词典，减小产物体积。
import OpenCC from 'opencc-js/cn2t'

let _toTraditional: ((text: string) => string) | null = null

export function toTraditional(text: string): string {
  if (!_toTraditional) {
    _toTraditional = OpenCC.Converter({ from: 'cn', to: 'tw' })
  }
  return _toTraditional(text)
}
