import { useCallback, useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'

import RitualStage, { type RitualPhase } from '../components/liuyao/RitualStage'
import YaoStack from '../components/liuyao/YaoStack'
import HexagramProgress from '../components/liuyao/HexagramProgress'
import LiuyaoPanView from '../components/liuyao/LiuyaoPan'
import ReadingPanel from '../components/liuyao/ReadingPanel'
import PageShell from '../components/PageShell'
import {
  BTN_PRIMARY, BTN_SECONDARY, BTN_GHOST, CHIP, CHIP_ON, CHIP_OFF, FIELD,
} from '../styles/ui'
import { liuyaoApi, nowIso } from '../services/liuyaoApi'
import type {
  LiuyaoPan, SiZhu, TopicInfo, TossResult, Trigram, YaoValue,
} from '../types/liuyao'
import '../styles/liuyao.css'
import { useLanguage } from '../i18n'

/* 与 styles/liuyao.css 中 coin-journey / shell-shake 的时长对应，改一处要同步另一处 */
const SHAKE_MS = 720      // 龟壳摇晃
const FLY_MS = 2160       // 铜钱弹出 → 排开 → 旋转停定（含三枚错峰）
/* 停定后记入六爻堆叠前的极短停顿，只为让"铜钱落定"与"该爻入列"两个动作分开。
   注意：铜钱与正反标记**不会**在此之后消失，而是留在桌面上直到点下一爻，
   所以这里不需要留阅读时间（早先留 460ms 就清空，根本看不清）。 */
const HOLD_MS = 300

const sleep = (ms: number) => new Promise<void>((resolve) => setTimeout(resolve, ms))

type Gender = '男' | '女'

export default function LiuyaoPage() {
  const { t } = useLanguage()
  const [sizhu, setSizhu] = useState<SiZhu | null>(null)
  const [topics, setTopics] = useState<TopicInfo[]>([])
  /** 八卦表，由后端提供；「卦象成形」据此把三爻阴阳位映射成卦名 */
  const [trigrams, setTrigrams] = useState<Trigram[]>([])
  const [topic, setTopic] = useState('general')
  const [gender, setGender] = useState<Gender>('男')

  const [yaos, setYaos] = useState<TossResult[]>([])
  const [phase, setPhase] = useState<RitualPhase>('idle')
  /** 当前这一爻的结果。落定后**保持不清空**，供慢慢核对三枚正反 */
  const [current, setCurrent] = useState<TossResult | null>(null)
  const [roundKey, setRoundKey] = useState(0)
  const [pan, setPan] = useState<LiuyaoPan | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [question, setQuestion] = useState('')

  /** 起卦时刻在第一爻落下时锁定，六爻共用同一时刻排四柱 */
  const momentRef = useRef<string | null>(null)
  /** 已摇出的爻值，供换问事类别时只重算解读、不必重新起卦 */
  const yaoValuesRef = useRef<YaoValue[] | null>(null)

  const lockMoment = () => {
    if (!momentRef.current) momentRef.current = nowIso()
    return momentRef.current
  }

  const loadSizhu = useCallback(async () => {
    try {
      setSizhu(await liuyaoApi.sizhu())
    } catch {
      setSizhu(null)      // 四柱只是辅助信息，取不到不阻断摇卦
    }
  }, [])

  const loadTopics = useCallback(async () => {
    try {
      const data = await liuyaoApi.topics()
      setTopics(data.topics)
    } catch {
      setTopics([])
    }
  }, [])

  const loadTrigrams = useCallback(async () => {
    try {
      const data = await liuyaoApi.trigrams()
      setTrigrams(data.trigrams)
    } catch {
      setTrigrams([])      // 取不到就只显示阴阳位、不显示卦名，不阻断摇卦
    }
  }, [])

  useEffect(() => {
    loadSizhu()
    loadTopics()
    loadTrigrams()
  }, [loadSizhu, loadTopics, loadTrigrams])

  const submit = async (values: YaoValue[], moment: string, nextTopic = topic, nextGender = gender) => {
    yaoValuesRef.current = values
    setPan(await liuyaoApi.paipan(values, moment, question, nextTopic, nextGender))
  }

  const handleToss = async () => {
    if (busy || yaos.length >= 6) return
    const position = yaos.length + 1
    const moment = lockMoment()

    setBusy(true)
    setError(null)
    try {
      // 先取服务端定下的结果，再把动画演到这个结果上
      const result = await liuyaoApi.toss(position)
      setCurrent(result)
      setRoundKey((k) => k + 1)

      setPhase('shaking')
      await sleep(SHAKE_MS)
      setPhase('flying')
      await sleep(FLY_MS)
      setPhase('settled')
      await sleep(HOLD_MS)

      // 记入六爻堆叠。**不重置 phase 与 current**：铜钱和三枚正反要留在桌面上，
      // 等你看清之后再点下一爻；下一爻开始时新一轮动画会把它们替换掉。
      const next = [...yaos, result]
      setYaos(next)

      if (next.length === 6) {
        await submit(next.map((y) => y.value) as YaoValue[], moment)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t('摇卦失败，请稍后重试。'))
      setPhase('idle')
      setCurrent(null)
    } finally {
      setBusy(false)
    }
  }

  const handleSkip = async () => {
    if (busy) return
    const moment = lockMoment()
    setBusy(true)
    setError(null)
    setPan(null)
    try {
      const six = await liuyaoApi.tossSix()
      setYaos(six.yaos)
      setPhase('idle')
      setCurrent(null)
      await submit(six.yao_values, moment)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('起卦失败，请稍后重试。'))
    } finally {
      setBusy(false)
    }
  }

  /** 换问事类别／性别：卦已定，只重算用神与旺衰 */
  const reanalyze = async (nextTopic: string, nextGender: Gender) => {
    setTopic(nextTopic)
    setGender(nextGender)
    const values = yaoValuesRef.current
    if (!pan || !values || !momentRef.current) return
    setBusy(true)
    setError(null)
    try {
      setPan(await liuyaoApi.paipan(values, momentRef.current, question, nextTopic, nextGender))
    } catch (err) {
      setError(err instanceof Error ? err.message : t('重新解读失败。'))
    } finally {
      setBusy(false)
    }
  }

  const handleReset = () => {
    setYaos([])
    setPan(null)
    setCurrent(null)
    setPhase('idle')
    setError(null)
    momentRef.current = null
    yaoValuesRef.current = null
    loadSizhu()
  }

  const done = yaos.length >= 6
  const activePosition = busy && phase !== 'idle' ? yaos.length + 1 : null
  const kongWang = (sizhu?.kong_wang ?? []).join('')
  const currentTopic = topics.find((item) => item.key === topic)

  return (
    <PageShell title={t('六爻摇卦')} subtitle={t('三枚铜钱，六次摇掷，自初爻而上装卦')}>
      {/* 四柱条 */}
      <div className="mb-8">
        <div className="glass-panel flex flex-wrap items-center justify-center gap-x-6 gap-y-2 border border-xuanjing-line px-5 py-3 text-xs">
          {sizhu ? (
            <>
              <span className="text-xuanjing-paper">
                {sizhu.year.gan_zhi}年　{sizhu.month.gan_zhi}月　{sizhu.day.gan_zhi}日　
                {sizhu.hour.gan_zhi}时
              </span>
              <span className="text-xuanjing-paper-dim">
                {t('月建')} <span className="text-xuanjing-gold">{sizhu.month_branch}</span>
              </span>
              <span className="text-xuanjing-paper-dim">
                {t('日建')} <span className="text-xuanjing-gold">{sizhu.day_branch}</span>
              </span>
              <span className="text-xuanjing-paper-dim">
                {t('旬空')} <span className="text-xuanjing-cinnabar-text">{kongWang}</span>
              </span>
            </>
          ) : (
            <span className="text-xuanjing-paper-faint">{t('正在取当前四柱…')}</span>
          )}
        </div>
      </div>

      <div>
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_360px]">
          {/* 仪式区 */}
          <div className="glass-card rounded-3xl border border-xuanjing-line p-6">
            <RitualStage
              phase={phase}
              faces={current ? current.coins : null}
              roundKey={roundKey}
              showFaces={phase === 'settled'}
            />

            <div className="mt-2 min-h-[3.5rem] text-center text-sm">
              {phase === 'idle' && !done && (
                <span className="text-xuanjing-paper-dim">
                  {t(`按下方按钮摇出第 ${yaos.length + 1} 爻`)}
                </span>
              )}
              {phase === 'shaking' && (
                <span className="ritual-hint text-xuanjing-gold">{t('龟壳摇动中…')}</span>
              )}
              {phase === 'flying' && (
                <span className="ritual-hint text-xuanjing-gold">{t('铜钱旋转，将依次停定…')}</span>
              )}
              {phase === 'settled' && current && (
                <div>
                  <div className="font-heading text-lg text-xuanjing-gold">
                    {t(current.position_name)}爻　{t(current.label)}
                    {current.moving && (
                      <span className="ml-2 text-xuanjing-cinnabar-text">
                        {current.value === 9 ? '○' : '×'} {t('动爻')}
                      </span>
                    )}
                  </div>
                  <div className="mt-1 text-xs text-xuanjing-paper-faint">
                    {t(`${current.coins.join('　')}　→　${current.name}`)}
                    {!done && `　·　${t('看清后点下方按钮摇下一爻')}`}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-6 space-y-5">
              {/* 问事类别：决定用神 */}
              {topics.length > 0 && (
                <div>
                  <div className="mb-2 text-xs text-xuanjing-paper-faint">{t('所问何事（决定用神）')}</div>
                  <div className="flex flex-wrap gap-2">
                    {topics.map((item) => (
                      <button
                        key={item.key}
                        type="button"
                        onClick={() => reanalyze(item.key, gender)}
                        disabled={busy}
                        title={t(`用神：${item.yong_shen}`)}
                        className={`${CHIP} ${topic === item.key ? CHIP_ON : CHIP_OFF}`}
                      >
                        {t(item.label)}
                      </button>
                    ))}
                  </div>
                  {currentTopic && (
                    <p className="mt-2 text-[11px] text-xuanjing-paper-faint">
                      {t('用神')}：{t(currentTopic.yong_shen)}
                      {pan ? `　${t('（换类别会立即重新解读，不必重新起卦）')}` : ''}
                    </p>
                  )}
                </div>
              )}

              {/* 感情类依性别取用神 */}
              {topic === 'relationship' && (
                <div className="flex flex-wrap items-center gap-3 text-xs">
                  <span className="text-xuanjing-paper-faint">{t('占者')}</span>
                  {(['男', '女'] as Gender[]).map((g) => (
                    <button
                      key={g}
                      type="button"
                      onClick={() => reanalyze(topic, g)}
                      disabled={busy}
                      className={`${CHIP} ${gender === g ? CHIP_ON : CHIP_OFF}`}
                    >
                      {g}
                    </button>
                  ))}
                  <span className="text-xuanjing-paper-faint">{t('男占妻财、女占官鬼')}</span>
                </div>
              )}

              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                maxLength={50}
                disabled={yaos.length > 0 || busy}
                placeholder={t('心中所问（选填），如：近期事业运势如何？')}
                className={FIELD}
              />

              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={handleToss}
                  disabled={busy || done}
                  className={`min-w-[180px] flex-1 ${BTN_PRIMARY}`}
                >
                  {busy ? t('摇卦中…') : done ? t('六爻已足') : t(`摇第 ${yaos.length + 1} 爻`)}
                </button>
                <button
                  type="button"
                  onClick={handleSkip}
                  disabled={busy || done}
                  className={BTN_SECONDARY}
                >
                  {t('跳过动画，直接起卦')}
                </button>
                {(yaos.length > 0 || pan) && (
                  <button
                    type="button"
                    onClick={handleReset}
                    disabled={busy}
                    className={BTN_GHOST}
                  >
                    {t('重新起卦')}
                  </button>
                )}
              </div>

              {error && (
                <p className="text-center text-sm text-xuanjing-cinnabar-text">{error}</p>
              )}
            </div>
          </div>

          {/* 右栏：六爻堆叠 + 卦象成形 */}
          <div className="space-y-5">
            <div className="glass-card h-fit rounded-3xl border border-xuanjing-line p-6">
              <h2 className="mb-4 font-heading text-lg font-semibold text-xuanjing-gold">{t('六爻')}</h2>
              <YaoStack yaos={yaos} activePosition={activePosition} panReady={pan != null} />
            </div>
            <HexagramProgress yaos={yaos} trigrams={trigrams} pan={pan} />
          </div>
        </div>

        {pan && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mt-10 space-y-5"
          >
            {pan.analysis && <ReadingPanel analysis={pan.analysis} />}
            <LiuyaoPanView pan={pan} />
          </motion.div>
        )}
      </div>
    </PageShell>
  )
}
