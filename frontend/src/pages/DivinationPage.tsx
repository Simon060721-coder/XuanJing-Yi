import { useState } from 'react'

import BaguaPlate from '../components/divination/BaguaPlate'
import HexagramFigure from '../components/divination/HexagramFigure'
import PageShell from '../components/PageShell'
import { BTN_PRIMARY, BTN_OUTLINE, BTN_GHOST, FIELD, FIELD_COMPACT } from '../styles/ui'
import '../styles/divination.css'
import { useLanguage } from '../i18n'

/* ── 时序 ────────────────────────────────────────────────────────────────
   定调是「起卦静、成卦强」，所以两段的节奏刻意不同：
   静段以停顿为主（盘停、取数逐项浮现），强段是连续的动作（全暗→亮起→翻转→剥离）。
   这些常量与 styles/divination.css 里的动效时长对应，改一处要同步另一处。 */
const STOP_MS = 1200       // 盘减速停
const NUMBER_MS = 420      // 每个取数浮现的停留
const LIT_MS = 520         // 上下卦在盘上亮起
const DARK_MS = 350        // 成卦前那一下全暗
const LINES_MS = 400       // 六爻亮起
const LINE_STAGGER = 70    // 六爻逐根错峰
const FLIP_MS = 560        // 动爻翻转
const SEP_MS = 620         // 变卦剥离

type Phase = 'idle' | 'casting' | 'revealing' | 'done'
type Method = 'time' | 'numbers'

const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms))

/** 体用五行关系 → 生克方向。前四项有向，比和与同卦无向。 */
const RELATION_FLOW: Record<string, string> = {
  support: '用 生 体',
  restrict: '体 克 用',
  generate: '体 生 用',
  attack: '用 克 体',
  neutral: '体 用 比 和',
  same: '体 用 同 卦',
}

async function postQuery(payload: Record<string, unknown>) {
  const res = await fetch('/api/v1/divination/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const body = await res.json().catch(() => null)
  if (!res.ok) throw new Error(body?.error || `起卦失败（HTTP ${res.status}）`)
  if (!body) throw new Error('后端返回了无法解析的内容。')
  return body
}

interface TiyongRowProps {
  bodyName: string
  bodyElement: string
  useName: string
  useElement: string
  relation: string
  relationLabel: string
}

/** 体用两卦 + 生克方向。分色：体暖金（主）、用青色（客） */
function TiyongRow({
  bodyName, bodyElement, useName, useElement, relation, relationLabel,
}: TiyongRowProps) {
  const { t } = useLanguage()
  const tag = (which: string, name: string, element: string, isBody: boolean) => (
    <div className="text-center">
      <div className="text-[11px] tracking-widest text-xuanjing-paper-faint">{t(which)}卦</div>
      <div
        className={`mt-1 font-heading text-xl ${
          isBody ? 'text-xuanjing-gold' : 'text-xuanjing-jade-bright'
        }`}
      >
        {t(name)}
        <span className="ml-1 text-sm opacity-80">{t(element)}</span>
      </div>
    </div>
  )

  return (
    <div className="mt-9">
      <div className="flex items-center justify-center gap-5">
        {tag('体', bodyName, bodyElement, true)}
        <div className="tiyong-arrow min-w-[116px] text-center text-sm text-xuanjing-gold">
          {t(RELATION_FLOW[relation] ?? '体 用 相 参')}
        </div>
        {tag('用', useName, useElement, false)}
      </div>
      <p className="mt-4 text-center text-xs tracking-wide text-xuanjing-paper-dim">
        {t(relationLabel)}
      </p>
    </div>
  )
}

/**
 * 梅花易数 · 起卦仪式
 *
 * 与六爻的区别在**性格**：六爻是「摇六次」的重仪式，梅花易数是「心动则数生」的轻感应。
 * 所以这里不照搬摇卦，而是：
 *   · 静——盘自转、取数逐项浮现、上下卦亮起，全程几乎不动
 *   · 强——成卦那一下：全暗 → 六爻亮起 → 动爻翻转 → 变卦剥离 → 体用分色
 *
 * 时间起卦用**此刻**（正统即如此），故不再给时刻选择器——顺带消掉了原来
 * 「UTC 填进本地解析控件」的 8 小时偏差。
 */
export default function DivinationPage() {
  const { t } = useLanguage()
  const [phase, setPhase] = useState<Phase>('idle')
  const [method, setMethod] = useState<Method | null>(null)
  const [result, setResult] = useState<any>(null)
  const [numbers, setNumbers] = useState<Array<{ label: string; value: number }>>([])
  const [lit, setLit] = useState<string[]>([])
  const [dimmed, setDimmed] = useState(false)
  const [revealStep, setRevealStep] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [question, setQuestion] = useState('')
  const [showManual, setShowManual] = useState(false)
  const [manual, setManual] = useState<[string, string, string]>(['', '', ''])
  const [shaking, setShaking] = useState(false)

  const hl = result?.data?.hexagram_layer ?? null
  const advice = result?.data?.advice_layer ?? null
  const analysis = result?.data?.analysis_layer ?? null

  const bigPlate = phase === 'idle' || phase === 'casting'
  const tapActive = phase === 'casting' && method === 'numbers' && numbers.length < 3

  /** 成卦：静（取向）→ 强（显现），两种起卦方式共用这一段 */
  const runReveal = async (body: any, m: Method) => {
    const h = body.data.hexagram_layer
    const c = body.data.calculation || {}

    // 静 · 取数：时间起卦的年月日时逐项浮现（数字起卦是用户点出来的，已经显示过）
    if (m === 'time') {
      const items = [
        { label: '年', value: c.year },
        { label: '月', value: c.month },
        { label: '日', value: c.day },
        { label: '时', value: c.hour },
      ].filter((it) => typeof it.value === 'number')
      for (const it of items) {
        setNumbers((prev) => [...prev, it])
        await sleep(NUMBER_MS)
      }
    }

    // 静 · 上下卦在盘上亮起
    setLit([h.upper.name, h.lower.name])
    await sleep(LIT_MS)

    // 强 · 呼吸一下再显现
    setDimmed(true)
    await sleep(DARK_MS)
    setPhase('revealing')
    setDimmed(false)
    setRevealStep(1)
    await sleep(LINES_MS + 6 * LINE_STAGGER)
    setRevealStep(2)
    await sleep(FLIP_MS)
    setRevealStep(3)
    await sleep(SEP_MS)
    setRevealStep(4)
    await sleep(420)
    setPhase('done')
  }

  const fail = (e: unknown) => {
    setError(e instanceof Error ? e.message : t('起卦失败，请稍后重试。'))
    setPhase('idle')
    setDimmed(false)
  }

  /** 以时起卦：取此刻，不问用户 */
  const castTime = async () => {
    setMethod('time')
    setPhase('casting')
    setError(null)
    setResult(null)
    setNumbers([])
    setLit([])
    setRevealStep(0)
    try {
      const [body] = await Promise.all([
        postQuery({
          query_type: '梅花易数',
          input_method: '时间',
          timestamp: new Date().toISOString(),
          question: question.trim(),
        }),
        sleep(STOP_MS),
      ])
      setResult(body)
      await runReveal(body, 'time')
    } catch (e) {
      fail(e)
    }
  }

  /** 以数起卦：先停盘，再让用户点盘报数 */
  const startNumbers = async () => {
    setMethod('numbers')
    setPhase('casting')
    setError(null)
    setResult(null)
    setNumbers([])
    setLit([])
    setRevealStep(0)
    await sleep(STOP_MS)
  }

  /** 点盘：数取自**点击那一瞬**的毫秒。用户决定"何时"，不决定"是几" */
  const tapPlate = async () => {
    if (!tapActive) return
    const value = (Date.now() % 99) + 1
    const label = ['一', '二', '三'][numbers.length]
    const next = [...numbers, { label, value }]
    setNumbers(next)
    setShaking(true)
    window.setTimeout(() => setShaking(false), 240)

    if (next.length < 3) return

    try {
      const body = await postQuery({
        query_type: '梅花易数',
        input_method: '数字',
        num1: next[0].value,
        num2: next[1].value,
        num3: next[2].value,
        question: question.trim(),
      })
      setResult(body)
      await runReveal(body, 'numbers')
    } catch (e) {
      fail(e)
    }
  }

  /** 自己报数：保留"看到什么数就用什么数"这条路 */
  const castManual = async () => {
    const nums = manual.map((v) => parseInt(v, 10))
    if (nums.some((n) => !Number.isFinite(n) || n < 1 || n > 99)) {
      setError(t('三个数字均需在 1-99 之间'))
      return
    }
    setMethod('numbers')
    setPhase('casting')
    setError(null)
    setResult(null)
    setLit([])
    setRevealStep(0)
    setNumbers([
      { label: '一', value: nums[0] },
      { label: '二', value: nums[1] },
      { label: '三', value: nums[2] },
    ])
    try {
      const [body] = await Promise.all([
        postQuery({
          query_type: '梅花易数',
          input_method: '数字',
          num1: nums[0],
          num2: nums[1],
          num3: nums[2],
          question: question.trim(),
        }),
        sleep(STOP_MS),
      ])
      setResult(body)
      await runReveal(body, 'numbers')
    } catch (e) {
      fail(e)
    }
  }

  const reset = () => {
    setPhase('idle')
    setMethod(null)
    setResult(null)
    setNumbers([])
    setLit([])
    setDimmed(false)
    setRevealStep(0)
    setError(null)
    setShowManual(false)
  }

  return (
    <PageShell title={t('梅花易数')} subtitle={t('以数起卦 · 观其体用')}>
      <div>
        {/* ── 盘 ───────────────────────────────────────────────────── */}
        <div
          className={`mx-auto transition-[width] duration-700 ease-out ${shaking ? 'plate-shake' : ''}`}
          style={{ width: bigPlate ? 'min(78vw, 380px)' : 'min(46vw, 186px)' }}
        >
          <div
            onClick={tapActive ? tapPlate : undefined}
            className={tapActive ? 'cursor-pointer' : undefined}
            role={tapActive ? 'button' : undefined}
          >
            <BaguaPlate
              spinning={phase === 'idle'}
              casting={phase === 'casting'}
              dimmed={dimmed}
              lit={lit}
            />
          </div>
        </div>

        {/* ── 状态与取数 ───────────────────────────────────────────── */}
        <div className="mx-auto mt-8 min-h-[4rem] max-w-xl text-center">
          {phase === 'idle' && numbers.length === 0 && (
            <p className="quiet-hint font-heading text-base">{t('心中默想所问之事')}</p>
          )}
          {phase === 'casting' && method === 'time' && numbers.length === 0 && (
            <p className="quiet-hint font-heading text-base">{t('取此刻之数…')}</p>
          )}
          {phase === 'casting' && method === 'numbers' && numbers.length < 3 && (
            <p className="quiet-hint font-heading text-base">{t('点盘三下，数自此刻而生')}</p>
          )}

          {numbers.length > 0 && (
            <div className="flex items-start justify-center gap-7">
              {numbers.map((n, i) => (
                <div
                  key={`${n.label}-${i}`}
                  className="cast-number text-center"
                  style={{ animationDelay: `${i * 40}ms` }}
                >
                  <div className="font-heading text-3xl text-xuanjing-gold">{n.value}</div>
                  <div className="mt-1 text-[11px] tracking-widest text-xuanjing-paper-faint">
                    {n.label}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && (
          <p className="mt-2 text-center text-sm text-xuanjing-cinnabar-text">{error}</p>
        )}

        {/* ── 强：成卦显现 ─────────────────────────────────────────── */}
        {(phase === 'revealing' || phase === 'done') && hl && (
          <div className="mt-10">
            <div className="flex items-start justify-center gap-8 sm:gap-14">
              <div>
                <div className="mb-3 text-center text-[11px] tracking-widest text-xuanjing-paper-faint">
                  {t('本卦')}
                </div>
                <HexagramFigure
                  yaos={hl.yaos}
                  variant="primary"
                  bodyTrigram={hl.body_hexagram}
                  upperTrigram={hl.upper.name}
                  lowerTrigram={hl.lower.name}
                  animate={revealStep >= 1}
                  flipping={revealStep === 2}
                  tiyong={revealStep >= 4}
                />
                <div className="mt-4 text-center font-heading text-lg text-xuanjing-paper">
                  {t(hl.primary_hexagram)}
                </div>
              </div>

              {revealStep >= 3 && (
                <div className="hex-separate">
                  <div className="mb-3 text-center text-[11px] tracking-widest text-xuanjing-paper-faint">
                    {t('变卦')}
                  </div>
                  <HexagramFigure
                    yaos={hl.yaos}
                    variant="changed"
                    bodyTrigram={hl.body_hexagram}
                    upperTrigram={hl.upper.name}
                    lowerTrigram={hl.lower.name}
                  />
                  <div className="mt-4 text-center font-heading text-lg text-xuanjing-paper-dim">
                    {t(hl.secondary_hexagram)}
                  </div>
                </div>
              )}
            </div>

            {revealStep >= 4 && analysis && (
              <TiyongRow
                bodyName={hl.body_hexagram}
                bodyElement={hl.elements.体}
                useName={hl.use_hexagram}
                useElement={hl.elements.用}
                relation={analysis.relation}
                relationLabel={analysis.element_balance}
              />
            )}
          </div>
        )}

        {/* ── 解读：最后淡入，且比卦象暗 ───────────────────────────── */}
        {phase === 'done' && advice && (
          <div className="reveal-in mx-auto mt-12 max-w-xl text-center">
            <div className="font-heading text-2xl tracking-widest text-xuanjing-gold">
              {t(analysis?.fortune_label)}
            </div>
            <p className="mt-5 text-sm leading-loose text-xuanjing-paper-dim">
              {t(advice.main_interpretation)}
            </p>
            {Array.isArray(advice.keywords) && advice.keywords.length > 0 && (
              <div className="mt-6 flex flex-wrap justify-center gap-2">
                {advice.keywords.map((k: string, i: number) => (
                  <span
                    key={i}
                    className="rounded-full border border-xuanjing-line px-3 py-1 text-xs text-xuanjing-paper-faint"
                  >
                    {t(k)}
                  </span>
                ))}
              </div>
            )}
            <button type="button" onClick={reset} className={`mt-10 ${BTN_GHOST}`}>
              {t('再起一卦')}
            </button>
          </div>
        )}

        {/* ── 静：起卦前的唯一一屏控件 ─────────────────────────────── */}
        {phase === 'idle' && (
          <div className="mx-auto mt-10 max-w-md text-center">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              maxLength={50}
              placeholder={t('默想所问之事（选填）')}
              className={`${FIELD} text-center font-heading`}
            />

            <div className="mt-9 flex flex-wrap items-center justify-center gap-4">
              <button type="button" onClick={castTime} className={BTN_OUTLINE}>
                {t('以时起卦')}
              </button>
              <button
                type="button"
                onClick={startNumbers}
                className={BTN_OUTLINE}
              >
                {t('以数起卦')}
              </button>
            </div>

            <button
              type="button"
              onClick={() => setShowManual((v) => !v)}
              className="mt-7 text-xs text-xuanjing-paper-faint transition-colors duration-200 hover:text-xuanjing-paper-dim"
            >
              {t('或自己报数')}
            </button>

            {showManual && (
              <div className="mt-5 flex flex-wrap items-center justify-center gap-3">
                {[0, 1, 2].map((i) => (
                  <input
                    key={i}
                    type="number"
                    min={1}
                    max={99}
                    value={manual[i]}
                    onChange={(e) => {
                      const next = [...manual] as [string, string, string]
                      next[i] = e.target.value
                      setManual(next)
                      setError(null)
                    }}
                    placeholder="1-99"
                    className={`${FIELD_COMPACT} w-20 font-heading text-lg`}
                  />
                ))}
                <button type="button" onClick={castManual} className={BTN_PRIMARY}>
                  {t('起卦')}
                </button>
              </div>
            )}

            <p className="mt-9 text-[11px] leading-relaxed text-xuanjing-paper-faint">
              {t('以时起卦取此刻之数；以数起卦可点盘三下由天定数，或自己报数')}
            </p>
          </div>
        )}
      </div>
    </PageShell>
  )
}
