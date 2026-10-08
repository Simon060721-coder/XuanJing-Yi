/**
 * 龟壳素材配置 —— 换素材的**唯一入口**，不必改组件代码
 * =====================================================================
 *
 * 用法（三选一）
 * --------------
 * 1. 用内置矢量版（默认）：
 *      把 TURTLE_ASSET 设为 null
 *
 * 2. 用你自己出图的 PNG（推荐，最省事）：
 *      a. 把图放到   frontend/public/assets/turtle-shell.png
 *      b. 本文件保持默认即可 —— src 已指向该路径
 *      文件一旦存在即自动启用；不存在则回退到内置矢量版，不会报错。
 *
 * 3. 用 3D 模型（.glb）：
 *      需要额外引入 three.js / react-three-fiber（约 +600KB 依赖与一块
 *      WebGL 画布），目前**未接入**。若确定走这条路，告知后我再接。
 *
 * 素材规格见 docs/ASSET_SPEC.md
 */

export interface TurtleAsset {
  /** 图片地址。放在 frontend/public 下的文件即以 / 开头引用 */
  src: string
  /** 素材显示宽度（px）。默认 336，与内置矢量版一致 */
  width?: number
  /**
   * 出钱口在**舞台中的纵坐标**（px，自舞台顶部算）——铜钱由此落下。
   * 内置矢量版为 176。换成自己的图后，若开口位置不同，调这个值即可对齐，
   * 不必改 CSS。调法：先跑一次摇卦，看铜钱是从开口上方还是下方冒出来的。
   */
  mouthTopPx?: number
  /** 是否给素材加落地投影（素材本身请不要画投影） */
  shadow?: boolean
}

export const TURTLE_ASSET: TurtleAsset | null = {
  // WebP 带 alpha，同画质下体积约为 PNG 的 1/5；桌面端与主流浏览器均支持
  src: '/assets/turtle-shell.webp',
  width: 300,
  mouthTopPx: 180,
  shadow: true,
}
