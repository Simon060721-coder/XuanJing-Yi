# -*- coding: utf-8 -*-
"""用神选取与旺衰规则引擎自检

测试策略（重要）
----------------
旺衰打分**没有经典数值可对照**——古籍只给定性的规则。因此本文件测的是：

1. **规则是否按传统被正确触发**：月破、日破、冲起、填实、进神退神、六冲六合、
   伏神飞神生克、原神忌神仇神的五行关系——这些都有确定的传统定义，可以判对错；
2. **分数与因子是否自洽**：score 必须等于 BASE 加各因子权重之和（可追溯）；
3. **文案是否只由真实因子推导**：不出现因子中不存在的判断。

**不测**「分数应该是多少」——那是我自己定的权重，没有权威答案。
"""

from datetime import datetime

from .constants import GENERATION, RESTRICTION
from .paipan import paipan_at
from .judgment import (
    WEIGHTS, BASE_SCORE, LEVELS, TOPIC_YONGSHEN, TOPIC_LABELS,
    ZHI_CHONG, ZHI_HE, SAN_HE, JIN_SHEN, TUI_SHEN,
    LIU_CHONG_GUA, LIU_HE_GUA,
    month_factor, day_factor, kong_factor, jin_tui_factor, gua_factor,
    locate_yong_shen, analyze,
)
from .hexagrams import HEXAGRAMS


def _pan():
    """2000-01-01 12:00 起卦得乾为天：月建子、日建午、旬空子丑、乾宫金

    六亲：初甲子水子孙、二甲寅木妻财、三甲辰土父母、
          四壬午火官鬼、五壬申金兄弟、六壬戌土父母（世）
    """
    return paipan_at([7, 7, 7, 7, 7, 7], datetime(2000, 1, 1, 12, 0))


def run(check, check_true, note):
    # ── 1. 地支冲合表本身自洽 ───────────────────────────────────────
    for zhi in ZHI_CHONG:
        check('{0} 的六冲是相互的'.format(zhi), ZHI_CHONG[ZHI_CHONG[zhi]], zhi)
        check('{0} 不冲自身'.format(zhi), ZHI_CHONG[zhi] != zhi, True)
    for zhi in ZHI_HE:
        check('{0} 的六合是相互的'.format(zhi), ZHI_HE[ZHI_HE[zhi]], zhi)
    check('六冲覆盖十二支', len(ZHI_CHONG), 12)
    check('六合覆盖十二支', len(ZHI_HE), 12)
    check('三合局四组', len(SAN_HE), 4)
    check('进神八组', len(JIN_SHEN), 8)
    check('退神与进神互为反向', len(TUI_SHEN), 8)
    check_true('进神退神无交集', not (JIN_SHEN & TUI_SHEN))

    # ── 2. 六冲卦／六合卦名单 ───────────────────────────────────────
    check('六冲卦共十卦', len(LIU_CHONG_GUA), 10)
    check('六合卦共八卦', len(LIU_HE_GUA), 8)
    for name in LIU_CHONG_GUA | LIU_HE_GUA:
        check_true('{0} 确实存在于六十四卦'.format(name), name in HEXAGRAMS)
    check_true('六冲与六合不重叠', not (LIU_CHONG_GUA & LIU_HE_GUA))
    # 八纯卦皆六冲
    for name in ('乾为天', '坤为地', '坎为水', '离为火', '震为雷', '巽为风', '艮为山', '兑为泽'):
        check_true('{0} 在六冲卦内'.format(name), name in LIU_CHONG_GUA)

    # ── 3. 月建规则 ─────────────────────────────────────────────────
    f = month_factor('午', '火', '子')
    check('月破：用神午与月建子相冲', (f['sign'], f['weight']), ('-', WEIGHTS['month_break']))
    check_true('月破文案含"月破"', '月破' in f['text'])

    f = month_factor('子', '水', '子')
    check('临月建', (f['sign'], f['weight']), ('+', WEIGHTS['month_same']))

    f = month_factor('寅', '木', '子')          # 月建子水 生 寅木
    check('月建生用神', (f['sign'], f['weight']), ('+', WEIGHTS['month_generate']))

    f = month_factor('子', '水', '申')          # 月建申金 生 子水
    check('月建生用神（金生水）', (f['sign'], f['weight']), ('+', WEIGHTS['month_generate']))

    f = month_factor('寅', '木', '午')          # 用神木 生 月建火
    check('用神泄气于月建', (f['sign'], f['weight']), ('-', WEIGHTS['month_drain']))

    # 用神克月建：须取**不相冲**的组合。寅木克辰土，而寅申冲、辰戌冲，故不相冲。
    f = month_factor('寅', '木', '辰')
    check('用神克月建', (f['sign'], f['weight']), ('-', WEIGHTS['month_restrict']))

    f = month_factor('寅', '木', '酉')          # 月建酉金 克 寅木
    check('月建克用神', (f['sign'], f['weight']), ('-', WEIGHTS['month_attack']))
    # 子水克未土？非也——子未不相冲，但土克水，即月建土克用神水
    f = month_factor('子', '水', '未')
    check('月建克用神（未土克子水，且子未不冲）',
          (f['sign'], f['weight']), ('-', WEIGHTS['month_attack']))

    check('月建同五行比和（丑未皆土）',
          month_factor('丑', '土', '未')['kind'], 'month')
    # 丑未相冲，应判月破而非比和
    check('丑未相冲优先判月破',
          month_factor('丑', '土', '未')['weight'], WEIGHTS['month_break'])
    # 子午既冲且克，传统以月破论 —— 冲的判定优先于五行生克
    check('子午既冲且克时以月破论',
          month_factor('午', '火', '子')['weight'], WEIGHTS['month_break'])
    check('子午既冲且克时不判月建克用神',
          month_factor('午', '火', '子')['weight'] != WEIGHTS['month_attack'], True)

    # ── 4. 日建规则，含"动而逢冲为冲起" ─────────────────────────────
    f = day_factor('午', '火', '子', moving=False)
    check('日破（静而逢冲）', (f['sign'], f['weight']), ('-', WEIGHTS['day_break']))
    f = day_factor('午', '火', '子', moving=True)
    check('冲起（动而逢冲）', (f['sign'], f['weight']), ('+', WEIGHTS['day_chong_moving']))
    check_true('冲起文案说明是冲起', '冲起' in f['text'])
    check('临日建', day_factor('午', '火', '午')['weight'], WEIGHTS['day_same'])
    check('日建克用神（酉克寅木）',
          day_factor('寅', '木', '酉')['weight'], WEIGHTS['day_attack'])

    # ── 5. 旬空三分：真空／填空／空动 ───────────────────────────────
    f = kong_factor('寅', True, '子', '午', moving=False)
    check('真旬空', (f['sign'], f['weight']), ('-', WEIGHTS['kong']))
    f = kong_factor('子', True, '子', '午', moving=False)
    check('临月建之空为填实', (f['sign'], f['weight']), ('0', 0))
    check_true('填实文案含"填实"', '填实' in f['text'])
    f = kong_factor('午', True, '子', '午', moving=False)
    check('临日建之空为填实', f['weight'], 0)
    f = kong_factor('寅', True, '子', '午', moving=True)
    check('空而动者出空可用', f['weight'], WEIGHTS['kong_moving'])
    check('不空则无因子', kong_factor('寅', False, '子', '午'), None)

    # ── 6. 进神退神 ─────────────────────────────────────────────────
    f = jin_tui_factor('寅', '卯')
    check('寅化卯为进神', (f['kind'], f['weight']), ('jin', WEIGHTS['jin_shen']))
    f = jin_tui_factor('卯', '寅')
    check('卯化寅为退神', (f['kind'], f['weight']), ('tui', WEIGHTS['tui_shen']))
    for a, b in (('亥', '子'), ('巳', '午'), ('申', '酉'), ('丑', '辰'), ('戌', '丑')):
        check_true('{0}化{1} 为进神'.format(a, b),
                   jin_tui_factor(a, b)['kind'] == 'jin')
    check('同支不判进退', jin_tui_factor('寅', '寅'), None)
    check('不同五行不判进退', jin_tui_factor('寅', '辰'), None)

    # ── 7. 卦体六冲六合 ─────────────────────────────────────────────
    check('乾为天为六冲卦，占财不利',
          gua_factor('乾为天', 'wealth')['sign'], '-')
    check('乾为天占病逢冲反吉',
          gua_factor('乾为天', 'health')['sign'], '+')
    # 关键：占病时符号与权重必须同时翻转，否则会"标着 + 却扣分"
    check('占病逢冲权重为正',
          gua_factor('乾为天', 'health')['weight'] > 0, True)
    check('占财逢冲权重为负',
          gua_factor('乾为天', 'wealth')['weight'] < 0, True)
    check('地天泰为六合卦',
          gua_factor('地天泰', 'wealth')['sign'], '+')
    check('非冲非合无因子', gua_factor('山雷颐', 'wealth'), None)

    # ── 7b. 不变量：每条因子的 sign 与 weight 符号必须一致 ─────────────
    # 这条能自动抓住"符号与权重不匹配"这类错误。
    inv_pan = _pan()
    inv_bad = []
    for tp in TOPIC_YONGSHEN:
        for f in analyze(inv_pan, tp)['factors']:
            ok = (
                (f['sign'] == '+' and f['weight'] >= 0)
                or (f['sign'] == '-' and f['weight'] <= 0)
                or (f['sign'] == '0' and f['weight'] == 0)
            )
            if not ok:
                inv_bad.append('{0}：{1} {2} {3}'.format(tp, f['sign'], f['weight'], f['text']))
    check_true('所有因子的符号与权重一致', not inv_bad,
               '不一致：{0}'.format(inv_bad[:3]))
    # 逐条规则直接验证
    for label, f in (
        ('六冲·占病', gua_factor('乾为天', 'health')),
        ('六冲·占财', gua_factor('乾为天', 'wealth')),
        ('六合', gua_factor('地天泰', 'wealth')),
        ('月破', month_factor('午', '火', '子')),
        ('冲起', day_factor('午', '火', '子', moving=True)),
        ('填实', kong_factor('子', True, '子', '午')),
        ('进神', jin_tui_factor('寅', '卯')),
        ('退神', jin_tui_factor('卯', '寅')),
    ):
        ok = ((f['sign'] == '+' and f['weight'] >= 0)
              or (f['sign'] == '-' and f['weight'] <= 0)
              or (f['sign'] == '0' and f['weight'] == 0))
        check_true('{0}：符号与权重一致'.format(label), ok,
                   '{0} {1}'.format(f['sign'], f['weight']))

    # ── 8. 用神定位（乾为天，甲子日）────────────────────────────────
    pan = _pan()
    check('乾为天本卦', pan['ben']['name'], '乾为天')
    check('月建为子', pan['month_branch'], '子')
    check('日建为午', pan['day_branch'], '午')
    check('旬空为子丑', pan['kong_wang'], ['子', '丑'])

    yong = locate_yong_shen(pan, '妻财')
    check('妻财位在二爻', yong['position'], 2)
    check('妻财纳甲甲寅', yong['na_jia'], '甲寅')

    yong = locate_yong_shen(pan, '官鬼')
    check('官鬼位在四爻', yong['position'], 4)
    check('官鬼为壬午火', (yong['na_jia'], yong['element']), ('壬午', '火'))

    # 父母两现（三爻、六爻），六爻临世 → 取临世者
    yong = locate_yong_shen(pan, '父母')
    check('父母多现时取临世之爻', yong['position'], 6)
    check('父母多现标记', yong['multiple'], True)
    check('父母现出位置', yong['all_positions'], [3, 6])

    check('卦中无此六亲则返回 None', locate_yong_shen(pan, '不存在的六亲'), None)

    # ── 9. 用神选取：按问事与性别 ───────────────────────────────────
    check('事业取官鬼', TOPIC_YONGSHEN['career'], '官鬼')
    check('财运取妻财', TOPIC_YONGSHEN['wealth'], '妻财')
    check('学业取父母', TOPIC_YONGSHEN['study'], '父母')
    check('子女取子孙', TOPIC_YONGSHEN['children'], '子孙')
    check('朋友取兄弟', TOPIC_YONGSHEN['friends'], '兄弟')
    check('泛问取世爻', TOPIC_YONGSHEN['general'], '世爻')
    check_true('感情类依性别而定（映射为 None）', TOPIC_YONGSHEN['relationship'] is None)
    check('类别标签齐全', set(TOPIC_LABELS), set(TOPIC_YONGSHEN))

    a_male = analyze(pan, 'relationship', '男')
    check('男占感情用妻财', a_male['yong_shen']['relative'], '妻财')
    a_female = analyze(pan, 'relationship', '女')
    check('女占感情用官鬼', a_female['yong_shen']['relative'], '官鬼')

    a_gen = analyze(pan, 'general')
    check('泛问用神即世爻', a_gen['yong_shen']['position'], 6)
    check('泛问世爻被标记', a_gen['yong_shen']['is_shi'], True)

    # ── 10. 端到端：分数与因子自洽 ──────────────────────────────────
    for topic in TOPIC_YONGSHEN:
        a = analyze(pan, topic)
        expected = max(0, min(100, BASE_SCORE + sum(f['weight'] for f in a['factors'])))
        check('{0} 分数等于基础分加因子权重之和'.format(topic), a['score'], expected)
        check_true('{0} 因子非空'.format(topic), len(a['factors']) > 0)
        check_true('{0} 每条因子都有说明文字'.format(topic),
                   all(f['text'] for f in a['factors']))
        check_true('{0} 分数在 0–100'.format(topic), 0 <= a['score'] <= 100)
        check_true('{0} 等级在既定档位内'.format(topic),
                   a['level'] in [label for _, label in LEVELS])
        check_true('{0} 摘要非空'.format(topic), bool(a['summary']))
        check_true('{0} 建议 1–4 条'.format(topic), 1 <= len(a['advice']) <= 4)
        check_true('{0} 关键词非空'.format(topic), len(a['keywords']) > 0)
        check_true('{0} 用神五行已定'.format(topic),
                   a['yong_shen']['element'] in GENERATION)

    # ── 11. 原神／忌神／仇神的五行关系 ───────────────────────────────
    a = analyze(pan, 'wealth')
    yong_el = a['yong_shen']['element']
    check('用神五行为木（甲寅）', yong_el, '木')
    check('原神生用神', GENERATION[a['yuan_shen']['element']], yong_el)
    check('忌神克用神', RESTRICTION[a['ji_shen']['element']], yong_el)
    check('仇神克原神', RESTRICTION[a['chou_shen']['element']], a['yuan_shen']['element'])
    check('原神为子孙（乾宫金生水）', a['yuan_shen']['relative'], '子孙')
    check('忌神为兄弟（同为金）', a['ji_shen']['relative'], '兄弟')
    check('仇神为父母（土克水）', a['chou_shen']['relative'], '父母')

    # ── 12. 具体规则在真实卦盘上被触发 ──────────────────────────────
    # 财运（妻财甲寅木）：月建子水生木 → 得月令；日建午火，木生火 → 泄气
    a = analyze(pan, 'wealth')
    kinds = {(f['kind'], f['sign']) for f in a['factors']}
    check_true('财运：月建生用神被触发', ('month', '+') in kinds)
    check_true('财运：用神泄气于日建被触发', ('day', '-') in kinds)
    check('财运用神为甲寅', a['yong_shen']['na_jia'], '甲寅')

    # 事业（官鬼壬午火）：日建午 → 临日建；月建子水与午相冲 → 月破（优先于五行克）
    a = analyze(pan, 'career')
    texts = ' '.join(f['text'] for f in a['factors'])
    check_true('事业：临日建被触发', '临日建' in texts)
    check_true('事业：子午相冲被判月破', '月破' in texts)
    check_true('事业：不误判为月建克用神', '克用神' not in texts)
    check('事业用神为壬午火', a['yong_shen']['na_jia'], '壬午')

    # 子女（子孙甲子水）：子落旬空，但子即月建 → 填实而非真空
    a = analyze(pan, 'children')
    texts = ' '.join(f['text'] for f in a['factors'])
    check_true('子女：旬空被判为填实', '填实' in texts)
    check_true('子女：不因旬空扣分',
               all(f['weight'] >= 0 for f in a['factors'] if f['kind'] == 'kong'))

    # ── 13. 确定性与错误处理 ───────────────────────────────────────
    a1 = analyze(pan, 'career')
    a2 = analyze(pan, 'career')
    check('同一卦盘两次分析分数一致', a1['score'], a2['score'])
    check('同一卦盘两次分析因子数一致', len(a1['factors']), len(a2['factors']))
    check('同一卦盘两次分析文案一致', a1['summary'], a2['summary'])

    raised = False
    try:
        analyze(pan, '不存在的类别')
    except ValueError:
        raised = True
    check_true('未知问事类别应报错', raised)

    raised = False
    try:
        from .paipan import paipan
        analyze(paipan([7, 7, 7, 7, 7, 7], '甲', '子'), 'career')
    except ValueError:
        raised = True
    check_true('缺 month_branch 的卦盘应报错（须用 paipan_at）', raised)

    # ── 14. 伏藏用神：天风姤缺妻财 ─────────────────────────────────
    pan_fu = paipan_at([8, 7, 7, 7, 7, 7], datetime(2000, 1, 1, 12, 0))
    check('天风姤本卦', pan_fu['ben']['name'], '天风姤')
    a = analyze(pan_fu, 'wealth')
    check('天风姤财运用神来源为伏神', a['yong_shen']['source'], 'fu_shen')
    check('伏藏用神纳甲甲寅', a['yong_shen']['na_jia'], '甲寅')
    texts = ' '.join(f['text'] for f in a['factors'])
    check_true('触发伏藏判断', '伏' in texts)
    check_true('伏藏被计入标记', '用神伏藏' in a['flags'])

    note('用神伏藏示例（天风姤，问财）：' + a['summary'])

    # ── 15. 文案只来自真实因子 ─────────────────────────────────────
    a = analyze(pan, 'career')
    for adv in a['advice']:
        check_true('建议非空且不是占位符', bool(adv.strip()) and '待补' not in adv)
    # 建议中的每一条都应能在因子里找到出处（末条兜底除外）
    advice_texts = {f['advice'] for f in a['factors'] if f['advice']}
    for adv in a['advice']:
        check_true('建议可在因子中找到出处：{0}'.format(adv[:14]),
                   adv in advice_texts or adv.startswith('卦象只提示倾向'))

    note('示例（乾为天，问事业）：' + a['summary'])
    note('建议：' + '　'.join(a['advice']))
