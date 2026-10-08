import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    watch: {
      // Vite 在处理 CSS 时会于源文件旁创建 `.index.css.<hash>.tmpdir` 临时目录。
      // 该目录随即被删除，但文件监视器可能仍持有句柄，在 Windows 上抛出
      //   EBUSY: resource busy or locked, watch '...tmpdir\index.css.tmp'
      // 并让 dev server 直接退出（本项目已实际发生过一次）。
      // 把临时目录排除在监视范围之外即可，不影响对 .css 本身的改动监听。
      ignored: ['**/*.tmpdir/**', '**/.*.tmpdir/**'],
      // 本机的文件变更事件不可靠：实际出现过「源文件已改，dev server 仍持续
      // 提供旧模块」的情况，表现为改了半天样式却始终是旧渲染，极易误判。
      // 改为轮询，牺牲一点 CPU 换取「改了就一定生效」。
      usePolling: true,
      interval: 300,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})
