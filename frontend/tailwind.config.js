/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      /**
       * 所有色值均指向 src/index.css 中的 CSS 变量。
       * 这里不定义任何字面色值 —— 换配色只改 index.css。
       */
      colors: {
        xuanjing: {
          // 背景三级
          ink: 'rgb(var(--xj-ink) / <alpha-value>)',
          'ink-2': 'rgb(var(--xj-ink-2) / <alpha-value>)',
          'ink-3': 'rgb(var(--xj-ink-3) / <alpha-value>)',
          'ink-deep': 'rgb(var(--xj-ink-deep) / <alpha-value>)',

          // 强调：暗金
          gold: 'rgb(var(--xj-gold) / <alpha-value>)',
          'gold-bright': 'rgb(var(--xj-gold-bright) / <alpha-value>)',
          'gold-deep': 'rgb(var(--xj-gold-deep) / <alpha-value>)',

          // 青铜：采样自梅花易数八卦盘
          bronze: 'rgb(var(--xj-bronze) / <alpha-value>)',
          'bronze-light': 'rgb(var(--xj-bronze-light) / <alpha-value>)',

          // 朱砂：警示与「凶」
          cinnabar: 'rgb(var(--xj-cinnabar) / <alpha-value>)',
          'cinnabar-text': 'rgb(var(--xj-cinnabar-text) / <alpha-value>)',

          // 青玉：吉
          jade: 'rgb(var(--xj-jade) / <alpha-value>)',
          'jade-bright': 'rgb(var(--xj-jade-bright) / <alpha-value>)',

          // 文字三级
          paper: 'rgb(var(--xj-paper) / <alpha-value>)',
          'paper-dim': 'rgb(var(--xj-paper-dim) / <alpha-value>)',
          'paper-faint': 'rgb(var(--xj-paper-faint) / <alpha-value>)',

          // 描边
          line: 'rgb(var(--xj-line) / <alpha-value>)',
        },
      },
      /**
       * 纯系统字体栈：不依赖外网字体，离线可用。
       * 标题取楷体系（古籍手书气），正文取无衬线中文（长文易读）。
       * 回退链同时覆盖 Windows 与 macOS。
       */
      fontFamily: {
        heading: [
          '"STKaiti"', '"KaiTi"', '"华文楷体"', '"楷体"',
          '"Songti SC"', '"STSong"', '"STZhongsong"', '"华文中宋"',
          '"SimSun"', '"宋体"', 'serif',
        ],
        body: [
          '"PingFang SC"', '"Microsoft YaHei"', '"微软雅黑"',
          '"Hiragino Sans GB"', '"Heiti SC"', '"SimHei"', '"黑体"',
          'sans-serif',
        ],
        mono: ['"Fira Code"', '"Consolas"', '"Monaco"', 'monospace'],
      },
      boxShadow: {
        glass: '0 20px 60px rgba(0, 0, 0, 0.4)',
      },
      animation: {
        breathe: 'breathe 3s ease-in-out infinite',
        fadeInSlow: 'fadeIn 0.8s ease-out',
        slideInUp: 'slideInUp 0.6s ease-out',
      },
      keyframes: {
        breathe: {
          '0%, 100%': { opacity: '0.78' },
          '50%': { opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideInUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}
