/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        xuanjing: {
          black: '#2B1C16',
          cyan: '#9D7150',
          red: '#8B3D1A',
          cream: '#F5E7D0',
          gray: {
            light: '#B7A08A',
            dark: '#4B392F',
          },
          accent: '#936142',
          wood: '#7A523C',
          tea: '#8A6F57',
        }
      },
      fontFamily: {
        heading: ['Noto Serif SC', 'SimSun', 'serif'],
        body: ['Noto Sans SC', 'PingFang SC', 'sans-serif'],
        mono: ['Fira Code', 'Monaco', 'monospace']
      },
      boxShadow: {
        glass: '0 20px 60px rgba(29, 16, 10, 0.18)',
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
        }
      }
    },
  },
  plugins: [],
}
