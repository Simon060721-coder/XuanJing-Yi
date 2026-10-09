# -*- coding: utf-8 -*-
"""梅花易数起卦引擎

以**先天八卦数**起卦：乾一、兑二、离三、震四、巽五、坎六、艮七、坤八。

相对旧实现的重要修正
--------------------
1. **八卦编号改为先天八卦数**。旧实现用的是「1乾 2坤 3震 4巽 5兑 6坎 7艮 8离」，
   既非先天数也非后天数，于是「余数取卦」整体错位——同一个余数取到的卦是错的。
2. **时间起卦补上上卦**。正统为：

       上卦 = (年 + 月 + 日) % 8
       下卦 = (年 + 月 + 日 + 时) % 8
       动爻 = (年 + 月 + 日 + 时) % 6

   旧实现把 `(日 + 时) % 8` 当作「第二卦」，**上卦从未被计算**。
3. **主卦由上下卦合成六十四卦，变卦由翻转动爻得出**。旧实现把上下卦当成
   「主卦/变卦」两个独立八卦返回，既不符合梅花易数，也从来给不出六十四卦名。
4. **体用按动爻所在卦判定**：动爻所在之卦为「用」，另一卦为「体」。
   旧实现径以第一卦为体、第二卦为用，与动爻无关，是错的。
5. 吉凶评分改为**由体用五行关系推出**，与解读文案共用同一套 relation，
   不再出现「分数 80 却评凶」这种自相矛盾。

已知偏差（不隐瞒）
------------------
正统时间起卦以**农历**取数：年支序数 + 农历月 + 农历日 + 时辰序数。
本实现取 **年支序数 + 公历月 + 公历日 + 时支序数**——年支、时支由四柱干支
得出（准确），但月、日暂用公历，因项目尚无农历换算。
该偏差会写入 `calculation['calendar']` 并由接口一并返回。

数字起卦的公式与本项目 About 页文档一致（上卦＝三数之和取余八、
下卦＝后两数之和取余八、动爻＝三数之和取余六），无偏差。
"""

from datetime import datetime

from app.services.liuyao.ganzhi import si_zhu
from app.services.liuyao.hexagrams import by_trigrams, by_lines
from app.services.liuyao.constants import YAO_POSITION_NAMES, ZHI_ORDER


class DivinationEngine:
    """梅花易数起卦引擎"""

    # 先天八卦数：乾一、兑二、离三、震四、巽五、坎六、艮七、坤八
    TRIGRAM_INFO = {
        '乾': {'number': 1, 'symbol': '☰', 'element': '金', 'direction': '西北'},
        '兑': {'number': 2, 'symbol': '☱', 'element': '金', 'direction': '西'},
        '离': {'number': 3, 'symbol': '☲', 'element': '火', 'direction': '南'},
        '震': {'number': 4, 'symbol': '☳', 'element': '木', 'direction': '东'},
        '巽': {'number': 5, 'symbol': '☴', 'element': '木', 'direction': '东南'},
        '坎': {'number': 6, 'symbol': '☵', 'element': '水', 'direction': '北'},
        '艮': {'number': 7, 'symbol': '☶', 'element': '土', 'direction': '东北'},
        '坤': {'number': 8, 'symbol': '☷', 'element': '土', 'direction': '西南'},
    }

    # 按先天数索引，保持旧接口 `engine.HEXAGRAMS[num]['name']` 可用
    HEXAGRAMS = {
        info['number']: {'name': name, **info}
        for name, info in TRIGRAM_INFO.items()
    }

    NUMBER_TO_NAME = {info['number']: name for name, info in TRIGRAM_INFO.items()}

    # 体用五行关系 → 分数。与 mapping_service 的 fortune 映射逐一对应，
    # 保证「分数」与「评级」由同一个 relation 推出，不会互相矛盾。
    RELATION_SCORE = {
        'support': 80,     # 用生体，得助
        'restrict': 72,    # 体克用，费力有成
        'neutral': 60,     # 比和
        'generate': 54,    # 体生用，耗泄
        'attack': 34,      # 用克体，受制
    }
    # 体用同卦（八纯卦）的分档，对应 mapping_service 的 very_good / good / moderate
    SAME_SCORE = {'乾': 88, '坤': 78}
    SAME_SCORE_DEFAULT = 62

    RELATION_LABELS = {
        'support': '用生体（得助）',
        'restrict': '体克用（费力有成）',
        'neutral': '体用比和（平稳）',
        'generate': '体生用（耗泄）',
        'attack': '用克体（受制）',
        'same': '体用同卦（专一）',
    }

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # 取卦
    # ------------------------------------------------------------------
    def _trigram(self, number):
        """先天数 → 八卦信息"""
        name = self.NUMBER_TO_NAME[(number % 8) or 8]
        return {'name': name, **self.TRIGRAM_INFO[name]}

    @staticmethod
    def body_and_use(upper_name, lower_name, changing_line):
        """定体用：动爻所在之卦为「用」，另一卦为「体」。"""
        if changing_line <= 3:
            # 动爻在下卦 → 下卦为用，上卦为体
            return upper_name, lower_name
        return lower_name, upper_name

    def _build(self, upper_name, lower_name, changing_line, method, calculation):
        """由上下卦与动爻组装完整结果"""
        primary = by_trigrams(upper_name, lower_name)
        if primary is None:
            raise ValueError('无法由 {0}/{1} 合成六十四卦'.format(upper_name, lower_name))

        lines = list(primary['lines'])
        lines[changing_line - 1] ^= 1
        changed = by_lines(lines)

        body, use = self.body_and_use(upper_name, lower_name, changing_line)
        upper = self.TRIGRAM_INFO[upper_name]
        lower = self.TRIGRAM_INFO[lower_name]

        return {
            'method': method,
            'upper': {'name': upper_name, **upper},
            'lower': {'name': lower_name, **lower},
            'primary_hexagram': self._brief(primary),
            'changed_hexagram': self._brief(changed),
            'changing_line': changing_line,
            'body': body,          # 体卦（不动之卦）
            'use': use,            # 用卦（动爻所在之卦）
            # 六爻（自初爻起）：给前端画卦用，含变卦后的阴阳，避免前端再算一遍
            'yaos': [
                {
                    'position': i + 1,
                    'position_name': YAO_POSITION_NAMES[i],
                    'is_yang': bool(primary['lines'][i]),
                    'moving': (i + 1) == changing_line,
                    'changed_is_yang': bool(lines[i]),
                }
                for i in range(6)
            ],
            'calculation': calculation,
        }

    @staticmethod
    def _brief(hexagram):
        return {
            'name': hexagram['name'],
            'symbols': hexagram['symbols'],
            'upper': hexagram['upper'],
            'lower': hexagram['lower'],
            'palace': hexagram['palace'],
            'palace_element': hexagram['palace_element'],
            'stage': hexagram['stage'],
            'shi': hexagram['shi'],
            'ying': hexagram['ying'],
        }

    # ------------------------------------------------------------------
    # 起卦方式
    # ------------------------------------------------------------------
    def query_by_timestamp(self, timestamp):
        """时间起卦。

        上卦 = (年 + 月 + 日) % 8
        下卦 = (年 + 月 + 日 + 时) % 8
        动爻 = (年 + 月 + 日 + 时) % 6

        年取**年支序数**（子1…亥12），时取**时支序数**（子1…亥12），
        二者由四柱干支得出；月、日暂用公历（见模块文档的偏差说明）。
        """
        sz = si_zhu(timestamp)
        year_num = ZHI_ORDER.index(sz['year']['zhi']) + 1
        hour_num = ZHI_ORDER.index(sz['hour']['zhi']) + 1
        month_num = timestamp.month
        day_num = timestamp.day

        upper_total = year_num + month_num + day_num
        total = upper_total + hour_num

        upper_number = upper_total % 8 or 8
        lower_number = total % 8 or 8
        changing_line = total % 6 or 6

        upper_name = self.NUMBER_TO_NAME[upper_number]
        lower_name = self.NUMBER_TO_NAME[lower_number]

        return self._build(
            upper_name, lower_name, changing_line, '时间',
            {
                'year_zhi': sz['year']['zhi'],
                'year': year_num,
                'month': month_num,
                'day': day_num,
                'hour_zhi': sz['hour']['zhi'],
                'hour': hour_num,
                'upper_total': upper_total,
                'total': total,
                'upper_number': upper_number,
                'lower_number': lower_number,
                'changing_line': changing_line,
                'calendar': '年支与时支由四柱干支得出；月、日暂用公历（正统用农历）',
            },
        )

    def query_by_numbers(self, num1, num2, num3):
        """数字起卦（与 About 页文档一致）。

        上卦 = 三数之和 % 8
        下卦 = 后两数之和 % 8
        动爻 = 三数之和 % 6
        """
        total = num1 + num2 + num3
        lower_total = num2 + num3

        upper_number = total % 8 or 8
        lower_number = lower_total % 8 or 8
        changing_line = total % 6 or 6

        upper_name = self.NUMBER_TO_NAME[upper_number]
        lower_name = self.NUMBER_TO_NAME[lower_number]

        return self._build(
            upper_name, lower_name, changing_line, '数字',
            {
                'num1': num1, 'num2': num2, 'num3': num3,
                'total': total,
                'lower_total': lower_total,
                'upper_number': upper_number,
                'lower_number': lower_number,
                'changing_line': changing_line,
                'calendar': '不涉及历法',
            },
        )

    # ------------------------------------------------------------------
    # 吉凶评分
    # ------------------------------------------------------------------
    def calculate_fortune_score(self, relation, changing_line, body, use):
        """由体用五行关系与动爻位置定吉凶分数。

        relation 必须与解读文案取自**同一个** element_relation 结果，
        这样分数与评级不会矛盾。
        """
        if relation == 'same':
            base = (self.SAME_SCORE.get(body, self.SAME_SCORE_DEFAULT)
                    if body == use else self.SAME_SCORE_DEFAULT)
        else:
            base = self.RELATION_SCORE[relation]

        # 动爻位置：初爻主事之始，上爻主事之终，居中之爻气最盛
        adjust = {1: -3, 2: 0, 3: 3, 4: 3, 5: 0, 6: -3}[changing_line]
        score = max(0, min(100, base + adjust))

        if score >= 85:
            level = '吉'
        elif score >= 70:
            level = '平吉'
        elif score >= 50:
            level = '平'
        elif score >= 30:
            level = '平凶'
        else:
            level = '凶'

        return {
            'fortune_score': round(score, 1),
            'fortune_level': level,
            'relation': relation,
            'base_score': base,
            'adjust': adjust,
        }

    # 兼容旧接口：由上下卦统计五行。新实现不再使用，保留以免外部调用报错。
    def analyze_elements(self, hexagram_nums):
        elements = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        for num in hexagram_nums:
            elements[self.HEXAGRAMS[num]['element']] += 1
        return {'elements': elements}
