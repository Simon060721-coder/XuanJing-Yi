# -*- coding: utf-8 -*-
"""摇卦：三枚铜钱 → 一爻

每次投掷三枚铜钱，按「以背为阳」计值（背 = 3、字 = 2），三枚相加：

    三枚全字（0 背）= 6  老阴，动爻
    一背二字（1 背）= 7  少阳，静爻
    二背一字（2 背）= 8  少阴，静爻
    三枚全背（3 背）= 9  老阳，动爻

这个 6/7/8/9 的取值与古法揲蓍一致，也自然满足「奇为阳、偶为阴」：
7、9 为阳，6、8 为阴。

随机源使用 `random.SystemRandom`，避免可预测的伪随机序列——
占卜工具的结果可预测是致命的。
"""

import random

from .constants import YAO_NAMES, YAO_LABELS, MOVING_VALUES

BACK = '背'    # 阳面
FRONT = '字'   # 阴面

_sysrand = random.SystemRandom()


def toss_coins(rng=None):
    """摇一次三枚铜钱，返回本次结果（即一爻）。"""
    pick = rng or _sysrand.choice
    coins = [pick((BACK, FRONT)) for _ in range(3)]

    backs = coins.count(BACK)
    value = 6 + backs
    moving = value in MOVING_VALUES

    return {
        'coins': coins,                              # 三枚的正反，顺序即排列顺序
        'backs': backs,
        'value': value,                              # 6/7/8/9
        'name': YAO_NAMES[value],                    # 交/单/拆/重
        'label': YAO_LABELS[value],                  # 老阴/少阳/少阴/老阳
        'yin_yang': '阳' if value % 2 == 1 else '阴',
        'moving': moving,
        'is_yang': value % 2 == 1,
    }


def toss_six(rng=None):
    """连摇六次，返回自初爻至上爻的六爻结果。"""
    return [toss_coins(rng) for _ in range(6)]


def describe(yao):
    """把一爻转成便于阅读的一行文字，如「背、字、背 → 拆（少阴，阴）」"""
    faces = '、'.join(yao['coins'])
    tail = '，动爻' if yao['moving'] else ''
    return '{0} → {1}（{2}，{3}{4}）'.format(
        faces, yao['name'], YAO_LABELS[yao['value']], yao['yin_yang'], tail)
