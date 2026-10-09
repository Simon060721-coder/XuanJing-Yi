import { useLanguage } from '../i18n'

function Footer() {
  const { t } = useLanguage()
  return (
    <footer className="mt-12 border-t border-xuanjing-line bg-xuanjing-ink-2/90 py-8 backdrop-blur-md">
      <div className="mx-auto max-w-6xl px-6 text-center text-sm text-xuanjing-paper-dim">
        <p>{t('玄镜易 © 2026 | 融合易学与数字化的传统文化应用')}</p>
        <p className="mt-2 text-xs text-xuanjing-paper-faint">Made with care and wisdom</p>
      </div>
    </footer>
  )
}

export default Footer
