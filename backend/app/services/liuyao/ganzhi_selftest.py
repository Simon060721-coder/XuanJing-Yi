# -*- coding: utf-8 -*-
"""四柱干支与二十四节气自检

基准数据来源
------------
- 万年历 2000 年 1 月逐日表（每日列出年柱、月柱、日柱，并标注节气时刻）
  例：2000-01-01 己卯年 丙子月 戊午日；2000-01-06 丁丑月（小寒 09:00:42）
- 光明网 2024-02-04 报道：当年立春为 2 月 4 日 16 时 27 分

节气精度不做隐瞒：本模块用 Meeus 低精度太阳黄经公式，误差约十几分钟，
测试对节气时刻采用 20 分钟容差，并把实测偏差打印出来。
"""

from datetime import datetime, timedelta

from .ganzhi import (
    day_ganzhi, year_ganzhi, month_ganzhi, hour_ganzhi, si_zhu,
    solar_term_datetime, solar_terms_of_year, month_branch_at, lichun,
    sun_apparent_longitude, datetime_to_jd, delta_t_seconds,
)
from .constants import GAN_ORDER, ZHI_ORDER

# ---------------------------------------------------------------------------
# 权威参考数据
# ---------------------------------------------------------------------------
REF_DAY_GANZHI = {
    (2000, 1, 1): '戊午',
    (2000, 1, 6): '癸亥',
    (2000, 1, 7): '甲子',
    (2000, 1, 21): '戊寅',
    (2000, 1, 31): '戊子',
}

REF_YEAR_MONTH = [
    # (时刻, 期望年柱, 期望月柱)
    (datetime(2000, 1, 1, 12), '己卯', '丙子'),
    (datetime(2000, 1, 5, 12), '己卯', '丙子'),
    (datetime(2000, 1, 6, 10), '己卯', '丁丑'),   # 小寒 09:00:42 之后
    (datetime(2000, 1, 31, 12), '己卯', '丁丑'),
    (datetime(2000, 2, 10, 12), '庚辰', '戊寅'),  # 立春之后
]

REF_SOLAR_TERMS = [
    (2000, '小寒', datetime(2000, 1, 6, 9, 0, 42)),
    (2000, '大寒', datetime(2000, 1, 21, 2, 23, 3)),
    (2024, '立春', datetime(2024, 2, 4, 16, 27, 0)),
]

# 2025 年全年节气（北京时间）。样本跨越四季，用于检验算法在不同日地距离下
# （1 月初近日点、7 月初远日点）的误差分布，避免只用冬季样本得出片面结论。
# 来源：天气万年历《2025二十四节气时间对照表》
REF_SOLAR_TERMS_2025 = [
    ('立春', datetime(2025, 2, 3, 22, 10, 13)),
    ('雨水', datetime(2025, 2, 18, 18, 6, 18)),
    ('惊蛰', datetime(2025, 3, 5, 16, 7, 2)),
    ('春分', datetime(2025, 3, 20, 17, 1, 14)),
    ('清明', datetime(2025, 4, 4, 20, 48, 21)),
    ('谷雨', datetime(2025, 4, 20, 3, 55, 45)),
    ('立夏', datetime(2025, 5, 5, 13, 56, 57)),
    ('小满', datetime(2025, 5, 21, 2, 54, 23)),
    ('芒种', datetime(2025, 6, 5, 17, 56, 16)),
    ('夏至', datetime(2025, 6, 21, 10, 42, 0)),
    ('小暑', datetime(2025, 7, 7, 4, 4, 43)),
    ('大暑', datetime(2025, 7, 22, 21, 29, 11)),
    ('立秋', datetime(2025, 8, 7, 13, 51, 19)),
    ('处暑', datetime(2025, 8, 23, 4, 33, 35)),
    ('白露', datetime(2025, 9, 7, 16, 51, 41)),
    ('秋分', datetime(2025, 9, 23, 2, 19, 4)),
    ('寒露', datetime(2025, 10, 8, 8, 40, 57)),
    ('霜降', datetime(2025, 10, 23, 11, 50, 39)),
    ('立冬', datetime(2025, 11, 7, 12, 3, 48)),
    ('小雪', datetime(2025, 11, 22, 9, 35, 18)),
    ('大雪', datetime(2025, 12, 7, 5, 4, 20)),
    ('冬至', datetime(2025, 12, 21, 23, 2, 48)),
]

# 月建抽样（由节气区间推得）
REF_MONTH_BRANCH = [
    (datetime(2000, 1, 1, 12), '子'),    # 大雪后、小寒前
    (datetime(2000, 2, 10, 12), '寅'),   # 立春后
    (datetime(2000, 5, 1, 12), '辰'),    # 清明后、立夏前
    (datetime(2000, 5, 10, 12), '巳'),   # 立夏后
    (datetime(2000, 8, 1, 12), '未'),    # 小暑后、立秋前
    (datetime(2000, 12, 25, 12), '子'),  # 大雪后
]


def run(check, check_true, note):
    """把四柱节气相关的检查挂到主自检上"""

    # ── 1. 日柱：与历书逐日核对 ──────────────────────────────────────
    for (y, m, d), expected in REF_DAY_GANZHI.items():
        gan, zhi, idx = day_ganzhi(datetime(y, m, d, 12))
        check('日柱 {0:04d}-{1:02d}-{2:02d}'.format(y, m, d), gan + zhi, expected)

    # ── 2. 年柱与月柱：含立春/小寒分界 ───────────────────────────────
    for dt, exp_year, exp_month in REF_YEAR_MONTH:
        y_gan, y_zhi, _ = year_ganzhi(dt)
        m_gan, m_zhi = month_ganzhi(dt, y_gan)
        label = '年柱月柱 {0}'.format(dt.strftime('%Y-%m-%d %H:%M'))
        check(label + ' 年柱', y_gan + y_zhi, exp_year)
        check(label + ' 月柱', m_gan + m_zhi, exp_month)

    # ── 3. 月建由节气判定 ────────────────────────────────────────────
    for dt, expected in REF_MONTH_BRANCH:
        check('月建 {0}'.format(dt.strftime('%Y-%m-%d')),
              month_branch_at(dt), expected)

    # ── 4. 节气时刻：容差 20 分钟，并记录实测偏差 ─────────────────────
    for year, name, expected in REF_SOLAR_TERMS:
        got = solar_term_datetime(year, name)
        delta = abs((got - expected).total_seconds())
        note('节气 {0} {1}：历书 {2}　本模块 {3}　偏差 {4:.0f} 秒'.format(
            year, name, expected.strftime('%Y-%m-%d %H:%M:%S'),
            got.strftime('%Y-%m-%d %H:%M:%S'), delta))
        check_true('{0} 年 {1} 时刻误差在 20 分钟内'.format(year, name),
                   delta <= 1200, '实际偏差 {0:.0f} 秒'.format(delta))

    # ── 5. 月建换月的时刻（应由节气决定，而非午夜）────────────────────
    # 扫描 2000-01-06 全天，找出月支由「子」变「丑」的时刻
    transition = None
    probe = datetime(2000, 1, 6, 0, 0)
    prev = month_branch_at(probe)
    for minutes in range(1, 24 * 60):
        cur_dt = probe + timedelta(minutes=minutes)
        cur = month_branch_at(cur_dt)
        if cur != prev:
            transition = cur_dt
            break
        prev = cur
    note('2000 年小寒换月：历书 09:00:42　本模块检测到 {0}'.format(
        transition.strftime('%H:%M') if transition else '未检出'))
    ref_transition = datetime(2000, 1, 6, 9, 0, 42)
    transition_delta = (abs((transition - ref_transition).total_seconds())
                        if transition else None)
    check_true('能检测到小寒换月',
               transition is not None)
    check_true('换月时刻与历书相差在 20 分钟内',
               transition_delta is not None and transition_delta <= 1200,
               '实际相差 {0} 秒'.format(transition_delta))
    check_true('换月不是由午夜（00:00）触发——月建按节气切换，不按日期',
               transition is not None
               and not (transition.hour == 0 and transition.minute == 0),
               '检出时刻 {0}'.format(transition.strftime('%H:%M')))

    # ── 5b. 2025 全年 22 个节气：检验全年误差分布 ────────────────────
    worst = 0.0
    for name, expected in REF_SOLAR_TERMS_2025:
        got = solar_term_datetime(2025, name)
        delta = abs((got - expected).total_seconds())
        worst = max(worst, delta)
        check_true('2025 年 {0} 与历书相差在 20 分钟内'.format(name),
                   delta <= 1200,
                   '历书 {0}　本模块 {1}　偏差 {2:.0f} 秒'.format(
                       expected.strftime('%m-%d %H:%M:%S'),
                       got.strftime('%m-%d %H:%M:%S'), delta))
    note('2025 年全年 22 个节气最大偏差：{0:.0f} 秒（{1:.1f} 分钟）'.format(
        worst, worst / 60.0))

    # ── 6. 时柱：五鼠遁 ─────────────────────────────────────────────
    # 甲己还加甲、乙庚丙作初、丙辛从戊起、丁壬庚子居、戊癸壬子求
    zi_cases = [('甲', '甲子'), ('乙', '丙子'), ('丙', '戊子'),
                ('丁', '庚子'), ('戊', '壬子'), ('己', '甲子'),
                ('庚', '丙子'), ('辛', '戊子'), ('壬', '庚子'), ('癸', '壬子')]
    for day_gan, expected in zi_cases:
        g, z = hour_ganzhi(0, day_gan)
        check('{0}日子时'.format(day_gan), g + z, expected)

    # 时支边界：23 点与 0 点同属子时，21–22 点为亥时
    for hour, expected_zhi in [(23, '子'), (0, '子'), (1, '丑'), (2, '丑'),
                               (3, '寅'), (11, '午'), (12, '午'),
                               (21, '亥'), (22, '亥')]:
        g, z = hour_ganzhi(hour, '甲')
        check('{0} 时的时支'.format(hour), z, expected_zhi)

    # 甲日午时为庚午（子甲、丑乙、寅丙、卯丁、辰戊、巳己、午庚）
    g, z = hour_ganzhi(12, '甲')
    check('甲日午时', g + z, '庚午')

    # ── 7. 四柱整体：2000-01-01 12:00 ───────────────────────────────
    sz = si_zhu(datetime(2000, 1, 1, 12, 0))
    check('四柱 2000-01-01 12:00 年', sz['year']['gan_zhi'], '己卯')
    check('四柱 2000-01-01 12:00 月', sz['month']['gan_zhi'], '丙子')
    check('四柱 2000-01-01 12:00 日', sz['day']['gan_zhi'], '戊午')
    check('四柱 2000-01-01 12:00 时', sz['hour']['gan_zhi'], '戊午')
    check('四柱月建', sz['month_branch'], '子')
    check('四柱日建', sz['day_branch'], '午')

    # 戊日午时：戊癸壬子求 → 子时壬子，丑癸、寅甲、卯乙、辰丙、巳丁、午戊 → 戊午 ✓
    check('戊日午时', sz['hour']['gan_zhi'], '戊午')

    # ── 8. 晚子时归次日 ─────────────────────────────────────────────
    late = si_zhu(datetime(2000, 1, 1, 23, 30))
    early = si_zhu(datetime(2000, 1, 1, 22, 30))
    check('23:30 日柱进为次日', late['day']['gan_zhi'], '己未')
    check('22:30 日柱仍为当日', early['day']['gan_zhi'], '戊午')
    check('晚子时标记', late['late_zi_adjusted'], True)
    check('非晚子时标记', early['late_zi_adjusted'], False)
    # 时支仍为子
    check('23:30 时支', late['hour']['zhi'], '子')
    # 若关闭晚子时规则，则应保持当日
    no_adj = si_zhu(datetime(2000, 1, 1, 23, 30), late_zi_next_day=False)
    check('关闭晚子时规则后日柱', no_adj['day']['gan_zhi'], '戊午')

    # ── 9. 全年节气表的结构 ─────────────────────────────────────────
    terms = solar_terms_of_year(2025)
    check('2025 年节气数量', len(terms), 24)
    check('节气名称集合', set(n for n, _ in terms), set(
        ['春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至', '小暑',
         '大暑', '立秋', '处暑', '白露', '秋分', '寒露', '霜降', '立冬',
         '小雪', '大雪', '冬至', '小寒', '大寒', '立春', '雨水', '惊蛰']))
    check('节气按时间排序', [d for _, d in terms], sorted(d for _, d in terms))
    check('全部落在 2025 年', set(d.year for _, d in terms), {2025})

    gaps = [(terms[i + 1][1] - terms[i][1]).total_seconds() / 86400.0
            for i in range(len(terms) - 1)]
    check_true('相邻节气间隔均在 14–16 天',
               all(14.0 <= g <= 16.0 for g in gaps),
               '实际区间 {0:.2f}–{1:.2f} 天'.format(min(gaps), max(gaps)))
    note('2025 年节气间隔：{0:.2f} – {1:.2f} 天（地球近日点附近间隔最短）'.format(
        min(gaps), max(gaps)))

    # ── 10. 太阳黄经的单调性与范围 ─────────────────────────────────
    lons = [sun_apparent_longitude(datetime_to_jd(datetime(2025, 1, 1, 12))
                                   + i * 10) for i in range(0, 37)]
    check_true('太阳黄经始终在 0–360',
               all(0.0 <= x < 360.0 for x in lons))
    diffs = [(lons[i + 1] - lons[i] + 180) % 360 - 180 for i in range(len(lons) - 1)]
    check_true('太阳黄经持续推进（每 10 日约 9.8°）',
               all(8.0 < d < 11.0 for d in diffs),
               '实际 {0:.3f}–{1:.3f}'.format(min(diffs), max(diffs)))

    # ── 11. 立春时刻合理 ───────────────────────────────────────────
    for year in (1950, 2000, 2025, 2050):
        lc = lichun(year)
        check_true('{0} 年立春在 2 月 3–5 日'.format(year),
                   lc.month == 2 and 3 <= lc.day <= 5,
                   '实际 {0}'.format(lc.strftime('%Y-%m-%d %H:%M')))
    note('立春抽样：1950 {0}　2000 {1}　2025 {2}　2050 {3}'.format(
        *(lichun(y).strftime('%m-%d %H:%M') for y in (1950, 2000, 2025, 2050))))
