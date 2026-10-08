# -*- coding: utf-8 -*-
"""六十四卦数据

数据来源分两路，**互相校验**，避免手工录入出错：

1. **卦名**：传统六十四卦名，按京房八宫次序排列（`PALACE_HEXAGRAM_NAMES`）。
   卦名无法由上下卦推导——「天风」只是取象前缀，第三字（姤、遁、否…）是
   传统定名，必须查表。
2. **上下卦**：由京房八宫卦序**程序化生成**：

   本宫卦  下卦 = 上卦 = 宫卦
   一世卦  自本宫变初爻
   二世卦  再变二爻
   三世卦  再变三爻
   四世卦  再变四爻
   五世卦  再变五爻
   游魂卦  自五世卦再变四爻
   归魂卦  下卦恢复为宫卦的下卦

两路数据必须自洽：非纯卦的卦名，其前两字应当等于「上卦取象 + 下卦取象」
（如「天风姤」= 上乾(天) 下巽(风)）。`selftest.py` 会逐卦核对这一点——
这正是验证变爻算法是否正确的手段。
"""

from .constants import (
    TRIGRAMS, BITS_TO_TRIGRAM, PALACE_ORDER, PALACE_STAGES, SHI_YING,
)

# ---------------------------------------------------------------------------
# 传统六十四卦名，按京房八宫次序：本宫、一世、二世、三世、四世、五世、游魂、归魂
# ---------------------------------------------------------------------------
PALACE_HEXAGRAM_NAMES = {
    '乾': ('乾为天', '天风姤', '天山遁', '天地否', '风地观', '山地剥', '火地晋', '火天大有'),
    '坎': ('坎为水', '水泽节', '水雷屯', '水火既济', '泽火革', '雷火丰', '地火明夷', '地水师'),
    '艮': ('艮为山', '山火贲', '山天大畜', '山泽损', '火泽睽', '天泽履', '风泽中孚', '风山渐'),
    '震': ('震为雷', '雷地豫', '雷水解', '雷风恒', '地风升', '水风井', '泽风大过', '泽雷随'),
    '巽': ('巽为风', '风天小畜', '风火家人', '风雷益', '天雷无妄', '火雷噬嗑', '山雷颐', '山风蛊'),
    '离': ('离为火', '火山旅', '火风鼎', '火水未济', '山水蒙', '风水涣', '天水讼', '天火同人'),
    '坤': ('坤为地', '地雷复', '地泽临', '地天泰', '雷天大壮', '泽天夬', '水天需', '水地比'),
    '兑': ('兑为泽', '泽水困', '泽地萃', '泽山咸', '水山蹇', '地山谦', '雷山小过', '雷泽归妹'),
}


def _build():
    """由八宫卦序生成六十四卦表"""
    table = {}
    for palace in PALACE_ORDER:
        base = TRIGRAMS[palace]['bits']
        lines = list(base) + list(base)          # 本宫卦：下卦与上卦皆宫卦
        names = PALACE_HEXAGRAM_NAMES[palace]

        for stage in range(8):
            if stage == 1:
                lines[0] ^= 1
            elif stage == 2:
                lines[1] ^= 1
            elif stage == 3:
                lines[2] ^= 1
            elif stage == 4:
                lines[3] ^= 1
            elif stage == 5:
                lines[4] ^= 1
            elif stage == 6:
                lines[3] ^= 1                    # 游魂：五世卦再变四爻
            elif stage == 7:
                lines[0], lines[1], lines[2] = base   # 归魂：下卦恢复为宫卦

            lower = BITS_TO_TRIGRAM[tuple(lines[0:3])]
            upper = BITS_TO_TRIGRAM[tuple(lines[3:6])]
            name = names[stage]
            shi, ying = SHI_YING[stage]

            table[name] = {
                'name': name,
                'upper': upper,
                'lower': lower,
                'palace': palace,
                'palace_element': TRIGRAMS[palace]['element'],
                'stage': PALACE_STAGES[stage],
                'stage_index': stage,
                'shi': shi,
                'ying': ying,
                'lines': tuple(lines),           # 索引 0 = 初爻
                'symbols': TRIGRAMS[upper]['symbol'] + TRIGRAMS[lower]['symbol'],
            }
    return table


HEXAGRAMS = _build()

# 由六爻阴阳反查卦（键为六位元组，索引 0 = 初爻）
LINES_TO_HEXAGRAM = {v['lines']: v for v in HEXAGRAMS.values()}

# 由上卦、下卦名反查卦
TRIGRAM_PAIR_TO_HEXAGRAM = {(v['upper'], v['lower']): v for v in HEXAGRAMS.values()}


def expected_name_prefix(hexagram):
    """按上下卦取象推出卦名应有的前两字（纯卦返回「宫为取象」）。"""
    if hexagram['stage_index'] == 0:
        return '{0}为{1}'.format(hexagram['palace'],
                                 TRIGRAMS[hexagram['palace']]['nature'])
    return TRIGRAMS[hexagram['upper']]['nature'] + TRIGRAMS[hexagram['lower']]['nature']


def by_lines(lines):
    """由六爻阴阳取卦。lines 为长度 6 的可迭代对象，索引 0 = 初爻。"""
    key = tuple(1 if x else 0 for x in lines)
    if len(key) != 6:
        raise ValueError('需要 6 个爻，收到 {0} 个'.format(len(key)))
    return LINES_TO_HEXAGRAM[key]


def by_name(name):
    """由卦名取卦"""
    return HEXAGRAMS.get(name)


def by_trigrams(upper, lower):
    """由上卦、下卦名取卦"""
    return TRIGRAM_PAIR_TO_HEXAGRAM.get((upper, lower))


def palaces():
    """按八宫返回卦，每宫 8 卦（本宫 → 归魂）"""
    result = {}
    for palace in PALACE_ORDER:
        result[palace] = sorted(
            (h for h in HEXAGRAMS.values() if h['palace'] == palace),
            key=lambda h: h['stage_index'],
        )
    return result
