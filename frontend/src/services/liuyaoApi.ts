// 六爻接口客户端。所有请求走同源 /api/v1，由 vite 在开发期代理到后端。
import type { LiuyaoPan, SiZhu, TopicInfo, TossResult, Trigram, YaoValue } from '../types/liuyao'

const BASE = '/api/v1/liuyao'

interface Envelope<T> {
  status: string
  data: T
  error?: string
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response
  try {
    res = await fetch(BASE + path, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    throw new Error('网络请求失败，请确认后端服务已启动。')
  }

  const body = (await res.json().catch(() => null)) as Envelope<T> | null
  if (!res.ok) {
    throw new Error(body?.error || `请求失败（HTTP ${res.status}）`)
  }
  if (!body) {
    throw new Error('后端返回了无法解析的内容。')
  }
  return body.data
}

/** 以 UTC ISO 发送时刻，由后端换算成本地时间排四柱，避免时区歧义 */
export function nowIso(): string {
  return new Date().toISOString()
}

export const liuyaoApi = {
  /** 取某时刻的四柱（默认当前） */
  sizhu: (moment?: string) =>
    request<SiZhu>(moment ? `/sizhu?moment=${encodeURIComponent(moment)}` : '/sizhu'),

  /** 摇一爻 */
  toss: (position: number) =>
    request<TossResult>('/toss', {
      method: 'POST',
      body: JSON.stringify({ position }),
    }),

  /** 一次摇满六爻（跳过动画时使用） */
  tossSix: () =>
    request<{ yaos: TossResult[]; yao_values: YaoValue[] }>('/toss-six', {
      method: 'POST',
      body: '{}',
    }),

  /** 由六爻结果装卦并解读；换问事类别只需重算，不必重新起卦 */
  paipan: (
    yaoValues: YaoValue[],
    moment: string,
    question?: string,
    topic?: string,
    gender?: string,
  ) =>
    request<LiuyaoPan>('/paipan', {
      method: 'POST',
      body: JSON.stringify({
        yao_values: yaoValues,
        moment,
        question: question || '',
        topic: topic || 'general',
        gender: gender || '男',
      }),
    }),

  /** 问事类别清单（决定用神），由后端作为单一来源 */
  topics: () => request<{ topics: TopicInfo[]; total: number }>('/topics'),

  /** 八卦表（含三爻阴阳位）。给「卦象成形」用，避免前端另抄一份八卦 */
  trigrams: () => request<{ trigrams: Trigram[] }>('/trigrams'),
}
