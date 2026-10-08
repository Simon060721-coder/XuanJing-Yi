# -*- coding: utf-8 -*-
"""六爻（纳甲筮法）术数内核

模块划分
--------
constants   八卦、五行、地支、纳甲、六神、八宫世应等固定规则
hexagrams   六十四卦数据（由京房八宫卦序生成）
casting     摇卦：三枚铜钱 → 一爻
paipan      装卦：排纳甲、六亲、六神、世应、旬空、变卦

尚未实现（后续阶段）
------------------
- 四柱干支与二十四节气（月建、日建）
- 伏神、用神选取、旺衰分析
"""

from .constants import (           # noqa: F401
    TRIGRAMS, GENERATION, RESTRICTION, ZHI_ORDER, ZHI_ELEMENT,
    NAJIA, SIX_GODS, SIX_GODS_START, SIX_RELATIVES,
    PALACE_ORDER, PALACE_STAGES, SHI_YING, YAO_NAMES, YAO_LABELS,
    YAO_POSITION_NAMES,
)
from .hexagrams import (           # noqa: F401
    HEXAGRAMS, LINES_TO_HEXAGRAM, by_lines, by_name, by_trigrams, palaces,
)
from .casting import toss_coins, toss_six, describe   # noqa: F401
from .paipan import (              # noqa: F401
    paipan, paipan_at, relative, kong_wang, six_gods, render, yao_title, fu_shen,
)
from .ganzhi import (              # noqa: F401
    si_zhu, day_ganzhi, year_ganzhi, month_ganzhi, hour_ganzhi,
    month_branch_at, solar_term_datetime, solar_terms_of_year, lichun,
)
from .judgment import (            # noqa: F401
    analyze, TOPIC_YONGSHEN, TOPIC_LABELS, WEIGHTS, BASE_SCORE,
    month_factor, day_factor, kong_factor, jin_tui_factor, gua_factor,
    locate_yong_shen,
)

__all__ = [
    'TRIGRAMS', 'HEXAGRAMS', 'palaces', 'by_lines', 'by_name', 'by_trigrams',
    'YAO_NAMES', 'YAO_LABELS', 'YAO_POSITION_NAMES', 'PALACE_ORDER',
    'toss_coins', 'toss_six', 'describe', 'paipan', 'paipan_at',
    'relative', 'kong_wang', 'six_gods', 'render', 'yao_title', 'fu_shen',
    'si_zhu', 'day_ganzhi', 'year_ganzhi', 'month_ganzhi', 'hour_ganzhi',
    'month_branch_at', 'solar_term_datetime', 'solar_terms_of_year', 'lichun',
    'analyze', 'TOPIC_YONGSHEN', 'TOPIC_LABELS',
]
