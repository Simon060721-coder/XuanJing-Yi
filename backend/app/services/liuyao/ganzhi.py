# -*- coding: utf-8 -*-
"""四柱干支与二十四节气

这是六爻的**时间基础**。六爻吉凶极大程度取决于月建与日建，而它们不是公历
也不是农历：

- **月建按「节」换月**：立春起寅月、惊蛰起卯月……所以月柱必须按节气分界，
  而不是按农历初一，也不是按公历 1 号。
- **年柱按立春分界**：立春之前仍算上一年（例如 2000-01-01 属己卯年）。
- **日柱**是连续六十甲子循环。
- **时柱**按日干以五鼠遁推。

时区约定
--------
本模块所有 `datetime` 一律为**北京时间（UTC+8，naive）**，与农历/干支历的
通行做法一致。

精度说明（重要，不要误读为「精确到秒」）
------------------------------------
太阳视黄经采用 Meeus《Astronomical Algorithms》第 25 章的低精度公式，理论误差
约 0.01°（折合时间约 15 分钟）；ΔT 采用 Espenak–Meeus 多项式，1900–2100 年区间
内误差远小于 1 分钟。

**实测偏差**（对照历书 25 个节气样本，其中 2025 年全年 22 个样本跨越四季）：
- 最小约 3.5 分钟，最大 13.3 分钟；
- 因此**节气时刻的误差在十几分钟以内**，与理论界相符。

用于确定月建、年柱在绝大多数情况下完全足够；只有当起卦时刻恰好落在节气前后
约十五分钟内时，月建才可能差一柱。`ganzhi_selftest.py` 会打印每次对照的实测
偏差，不做隐瞒。
"""

import math
from datetime import datetime, timedelta

from .constants import GAN_ORDER, ZHI_ORDER

# ---------------------------------------------------------------------------
# 六十甲子
# ---------------------------------------------------------------------------
JIAZI = tuple(
    GAN_ORDER[i % 10] + ZHI_ORDER[i % 12] for i in range(60)
)

# ---------------------------------------------------------------------------
# 二十四节气与太阳黄经
# ---------------------------------------------------------------------------
# 春分为黄经 0°，每气相差 15°
SOLAR_TERM_LONGITUDES = {
    '春分': 0, '清明': 15, '谷雨': 30, '立夏': 45,
    '小满': 60, '芒种': 75, '夏至': 90, '小暑': 105,
    '大暑': 120, '立秋': 135, '处暑': 150, '白露': 165,
    '秋分': 180, '寒露': 195, '霜降': 210, '立冬': 225,
    '小雪': 240, '大雪': 255, '冬至': 270, '小寒': 285,
    '大寒': 300, '立春': 315, '雨水': 330, '惊蛰': 345,
}

# 十二「节」（每月之首），决定月建换月
JIE_TO_MONTH_BRANCH = {
    '立春': '寅', '惊蛰': '卯', '清明': '辰', '立夏': '巳',
    '芒种': '午', '小暑': '未', '立秋': '申', '白露': '酉',
    '寒露': '戌', '立冬': '亥', '大雪': '子', '小寒': '丑',
}

# 立春黄经，用于年柱分界
LICHUN_LONGITUDE = 315

_MEAN_DAILY_MOTION = 0.98564736      # 太阳黄经平均日变化（度/日）


# ---------------------------------------------------------------------------
# 儒略日换算
# ---------------------------------------------------------------------------
def datetime_to_jd(dt):
    """北京时间 datetime → 儒略日（UT 意义上的 JD）"""
    ut = dt - timedelta(hours=8)          # 北京时 → UT
    y, m = ut.year, ut.month
    d = ut.day + (ut.hour + ut.minute / 60.0 + ut.second / 3600.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return (int(365.25 * (y + 4716)) + int(30.6001 * (m + 1))
            + d + b - 1524.5)


def jd_to_datetime(jd):
    """儒略日 → 北京时间 datetime（Meeus 第 7 章）"""
    jd = jd + 0.5
    z = int(jd)
    f = jd - z
    if z < 2299161:
        a = z
    else:
        alpha = int((z - 1867216.25) / 36524.25)
        a = z + 1 + alpha - alpha // 4
    b = a + 1524
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6001)
    day = b - d - int(30.6001 * e) + f
    month = e - 1 if e < 14 else e - 13
    year = c - 4716 if month > 2 else c - 4715

    day_int = int(day)
    frac = day - day_int
    total_seconds = int(round(frac * 86400.0))
    base = datetime(year, month, day_int)
    # 北京时 = UT + 8 小时
    return base + timedelta(seconds=total_seconds, hours=8)


# ---------------------------------------------------------------------------
# 太阳视黄经（Meeus 第 25 章低精度算法）
# ---------------------------------------------------------------------------
def sun_apparent_longitude(jde):
    """给定儒略日（力学时 TT），返回太阳视黄经（度，0–360）"""
    t = (jde - 2451545.0) / 36525.0

    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    mr = math.radians(m % 360.0)

    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(mr)
         + (0.019993 - 0.000101 * t) * math.sin(2 * mr)
         + 0.000289 * math.sin(3 * mr))

    true_long = l0 + c
    omega = 125.04 - 1934.136 * t
    apparent = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    return apparent % 360.0


def delta_t_seconds(year):
    """ΔT = TT − UT（秒），Espenak–Meeus 多项式，覆盖 1900–2150"""
    if year < 1920:
        t = year - 1900
        return (-2.79 + 1.494119 * t - 0.0598939 * t ** 2
                + 0.0061966 * t ** 3 - 0.000197 * t ** 4)
    if year < 1941:
        t = year - 1920
        return 21.20 + 0.84493 * t - 0.076100 * t ** 2 + 0.0020936 * t ** 3
    if year < 1961:
        t = year - 1950
        return 29.07 + 0.407 * t - t ** 2 / 233.0 + t ** 3 / 2547.0
    if year < 1986:
        t = year - 1975
        return 45.45 + 1.067 * t - t ** 2 / 260.0 - t ** 3 / 718.0
    if year < 2005:
        t = year - 2000
        return (63.86 + 0.3345 * t - 0.060374 * t ** 2 + 0.0017275 * t ** 3
                + 0.000651814 * t ** 4 + 0.00002373599 * t ** 5)
    if year < 2050:
        t = year - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t ** 2
    if year < 2150:
        u = (year - 1820) / 100.0
        return -20 + 32 * u * u - 0.5628 * (2150 - year)
    u = (year - 1820) / 100.0
    return -20 + 32 * u * u


def _solve_term_jde(jde_guess, target_lon):
    """牛顿迭代求太阳视黄经等于 target_lon 的儒略日（TT）"""
    jde = jde_guess
    for _ in range(30):
        lon = sun_apparent_longitude(jde)
        diff = (lon - target_lon + 180.0) % 360.0 - 180.0
        if abs(diff) < 1e-8:
            break
        jde -= diff / _MEAN_DAILY_MOTION
    return jde


def solar_term_datetime(year, term_name):
    """返回某年某节气的北京时间 datetime。

    year 为公历年份；节气取该公历年内发生的那个（例如 2024 年立春在 2 月 4 日）。
    """
    if term_name not in SOLAR_TERM_LONGITUDES:
        raise ValueError('未知节气: {0}'.format(term_name))
    target = SOLAR_TERM_LONGITUDES[term_name]

    # 以该年 1 月 1 日为起点，用平均日运动估初值
    jd_start = datetime_to_jd(datetime(year, 1, 1, 0, 0, 0))
    lon_start = sun_apparent_longitude(jd_start)
    guess = jd_start + ((target - lon_start) % 360.0) / _MEAN_DAILY_MOTION

    jde = _solve_term_jde(guess, target)
    jd_ut = jde - delta_t_seconds(year) / 86400.0
    dt = jd_to_datetime(jd_ut)

    # 目标节气若落在相邻年份（极少数边界情形），做一次校正
    if dt.year < year:
        jde = _solve_term_jde(guess + 365.2422, target)
        jd_ut = jde - delta_t_seconds(year) / 86400.0
        dt = jd_to_datetime(jd_ut)
    elif dt.year > year:
        jde = _solve_term_jde(guess - 365.2422, target)
        jd_ut = jde - delta_t_seconds(year) / 86400.0
        dt = jd_to_datetime(jd_ut)
    return dt


def solar_terms_of_year(year):
    """返回该公历年内全部 24 个节气，按时间先后排序 [(名称, datetime), ...]"""
    items = [(name, solar_term_datetime(year, name))
             for name in SOLAR_TERM_LONGITUDES]
    return sorted(items, key=lambda x: x[1])


def lichun(year):
    """某年立春的北京时间"""
    return solar_term_datetime(year, '立春')


# ---------------------------------------------------------------------------
# 月建：直接由太阳黄经判定
# ---------------------------------------------------------------------------
def month_branch_at(dt):
    """由太阳视黄经判定月建地支。

    黄经 315°（立春）起寅月，每 30° 进一个月支。
    直接算黄经而不去比较节气时刻，避免引入求根误差。
    """
    jde = datetime_to_jd(dt) + delta_t_seconds(dt.year) / 86400.0
    lon = sun_apparent_longitude(jde)
    offset = (lon - LICHUN_LONGITUDE) % 360.0
    index = int(offset // 30.0)
    # 寅 = ZHI_ORDER 中的索引 2
    return ZHI_ORDER[(2 + index) % 12]


# ---------------------------------------------------------------------------
# 四柱
# ---------------------------------------------------------------------------
def day_ganzhi(dt):
    """日柱：连续六十甲子。按北京时间的日历日计算。"""
    jd_noon = datetime_to_jd(datetime(dt.year, dt.month, dt.day, 12, 0, 0))
    jdn = int(math.floor(jd_noon + 0.5))
    index = (jdn + 49) % 60
    return GAN_ORDER[index % 10], ZHI_ORDER[index % 12], index


def year_ganzhi(dt):
    """年柱：以立春为界，立春之前仍属上一年。"""
    year = dt.year if dt >= lichun(dt.year) else dt.year - 1
    index = (year - 4) % 60          # 公元 4 年为甲子年
    return GAN_ORDER[index % 10], ZHI_ORDER[index % 12], index


def month_ganzhi(dt, year_gan=None):
    """月柱：月支由节气定，月干由年干以「五虎遁」推。

    五虎遁：甲己之年丙作首、乙庚之岁戊为头、丙辛必定寻庚起、
            丁壬壬位顺行流、戊癸之年甲寅求。
    """
    if year_gan is None:
        year_gan, _, _ = year_ganzhi(dt)

    branch = month_branch_at(dt)
    branch_index = ZHI_ORDER.index(branch)

    # 寅月天干序号 = (年干序号 * 2 + 2) % 10
    yin_gan_index = (GAN_ORDER.index(year_gan) * 2 + 2) % 10
    # 从寅月数到目标月支（寅=0 起算）
    steps = (branch_index - 2) % 12
    gan = GAN_ORDER[(yin_gan_index + steps) % 10]
    return gan, branch


def hour_ganzhi(hour, day_gan):
    """时柱：时支按小时定，时干由日干以「五鼠遁」推。

    五鼠遁：甲己还加甲、乙庚丙作初、丙辛从戊起、丁壬庚子居、戊癸壬子求。
    时支：23:00–00:59 为子，其后每两小时进一支。
    """
    branch_index = ((hour + 1) // 2) % 12
    branch = ZHI_ORDER[branch_index]

    # 子时天干序号 = (日干序号 * 2) % 10
    zi_gan_index = (GAN_ORDER.index(day_gan) * 2) % 10
    gan = GAN_ORDER[(zi_gan_index + branch_index) % 10]
    return gan, branch


def si_zhu(dt, late_zi_next_day=True):
    """排四柱。

    参数
    ----
    dt : 北京时间 datetime
    late_zi_next_day : 23:00 之后是否算次日日柱。
        主流做法（也是本函数默认）是「晚子时归次日」；若设为 False，
        则 23:00–24:00 仍用当日日柱。

    返回
    ----
    字典：year/month/day/hour 四柱（含干支与序号）、月建、日建、当日节气信息。
    """
    effective = dt + timedelta(days=1) if (late_zi_next_day and dt.hour >= 23) else dt

    y_gan, y_zhi, y_idx = year_ganzhi(dt)
    m_gan, m_zhi = month_ganzhi(dt, y_gan)
    d_gan, d_zhi, d_idx = day_ganzhi(effective)
    h_gan, h_zhi = hour_ganzhi(dt.hour, d_gan)

    return {
        'year': {'gan': y_gan, 'zhi': y_zhi, 'gan_zhi': y_gan + y_zhi, 'index': y_idx},
        'month': {'gan': m_gan, 'zhi': m_zhi, 'gan_zhi': m_gan + m_zhi},
        'day': {'gan': d_gan, 'zhi': d_zhi, 'gan_zhi': d_gan + d_zhi, 'index': d_idx},
        'hour': {'gan': h_gan, 'zhi': h_zhi, 'gan_zhi': h_gan + h_zhi},
        'month_branch': m_zhi,        # 月建
        'day_branch': d_zhi,          # 日建
        'effective_day': effective,
        'late_zi_adjusted': effective is not dt,
    }
