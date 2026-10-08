# -*- coding: utf-8 -*-
"""梅花易数引擎自检

用已知答案核对重写后的引擎，重点验证本轮修掉的四处问题：

1. 先天八卦数编号（旧实现的编号取卦会整体错位）
2. 时间起卦的上卦公式（旧实现从未计算上卦）
3. 主卦＝上下卦合成六十四卦、变卦＝翻转动爻（旧实现返回两个独立八卦）
4. 体用按动爻所在卦判定（旧实现与动爻无关）

另有一项**一致性不变量**：吉凶评分与解读评级必须来自同一个五行关系，
不允许出现"分数高却评凶"这类矛盾。
"""

from datetime import datetime

from .divination_engine import DivinationEngine
from .mapping_service import element_relation, MappingService
from .liuyao.hexagrams import HEXAGRAMS as ALL_HEXAGRAMS

# 关系 → 允许的评级（分数分档必须落在评级指向的区间内，不可矛盾）
FORTUNE_BANDS = {
    'support': {'吉', '平吉'},
    'restrict': {'吉', '平吉'},
    'neutral': {'平'},
    'generate': {'平吉', '平'},
    'attack': {'凶', '平凶'},
    'same': {'吉', '平吉', '平'},
}


def run(check, check_true, note):
    engine = DivinationEngine()
    mapping = MappingService()

    # ── 1. 先天八卦数 ───────────────────────────────────────────────
    expected_numbers = {'乾': 1, '兑': 2, '离': 3, '震': 4,
                        '巽': 5, '坎': 6, '艮': 7, '坤': 8}
    for name, num in expected_numbers.items():
        check('先天八卦数 {0}'.format(name),
              engine.TRIGRAM_INFO[name]['number'], num)
        check('先天数 {0} 反查为 {1}'.format(num, name),
              engine.NUMBER_TO_NAME[num], name)
    check('八卦数目为八', len(engine.TRIGRAM_INFO), 8)

    # 卦符仍然正确（别在重写时把上一轮修好的符号弄坏）
    symbols = {n: engine.TRIGRAM_INFO[n]['symbol'] for n in expected_numbers}
    check('八卦符号', symbols, {
        '乾': '☰', '兑': '☱', '离': '☲', '震': '☳',
        '巽': '☴', '坎': '☵', '艮': '☶', '坤': '☷',
    })
    check_true('八卦符号互不重复',
               len(set(symbols.values())) == 8)

    # ── 2. 数字起卦：已知答案 ───────────────────────────────────────
    # 26、6、27 → 上卦 (26+6+27)=59, 59%8=3 → 离；下卦 (6+27)=33, 33%8=1 → 乾
    #             动爻 59%6=5
    # 上离下乾 = 火天大有；五爻动 → 变乾为天
    cast = engine.query_by_numbers(26, 6, 27)
    check('数字起卦 上卦数', cast['calculation']['upper_number'], 3)
    check('数字起卦 下卦数', cast['calculation']['lower_number'], 1)
    check('数字起卦 上卦', cast['upper']['name'], '离')
    check('数字起卦 下卦', cast['lower']['name'], '乾')
    check('数字起卦 动爻', cast['changing_line'], 5)
    check('数字起卦 主卦', cast['primary_hexagram']['name'], '火天大有')
    check('数字起卦 主卦卦符', cast['primary_hexagram']['symbols'], '☲☰')
    check('数字起卦 变卦', cast['changed_hexagram']['name'], '乾为天')
    # 动爻在上卦 → 上卦为用、下卦为体
    check('数字起卦 体卦', cast['body'], '乾')
    check('数字起卦 用卦', cast['use'], '离')
    # 乾金 与 离火：火克金 → 用克体
    check('数字起卦 体用关系',
          element_relation(cast['body'], cast['use']), 'attack')

    # 六爻画卦数据：火天大有（上离下乾）＝ 下三爻全阳 + 上三爻阳阴阳，
    # 动爻 5（索引 4）翻转 → 乾为天（六爻皆阳）
    check('数字起卦 本卦六爻阴阳', [y['is_yang'] for y in cast['yaos']],
          [True, True, True, True, False, True])
    check('数字起卦 动爻标记', [y['moving'] for y in cast['yaos']],
          [False, False, False, False, True, False])
    check('数字起卦 变卦六爻阴阳', [y['changed_is_yang'] for y in cast['yaos']],
          [True, True, True, True, True, True])
    check('数字起卦 爻位名', [y['position_name'] for y in cast['yaos']],
          ['初', '二', '三', '四', '五', '上'])

    # 旧实现同一输入返回「震（☳）→ 乾（☰）」，即两个独立八卦，且编号错位。
    note('数字起卦 26/6/27：旧实现返回 震☳ → 乾☰（两个独立八卦、编号错位）；'
         '现返回 火天大有 → 乾为天（六十四卦）')

    # ── 3. 数字起卦的文档一致性 ─────────────────────────────────────
    # About 页文档：上卦＝三者之和取余八、下卦＝后两者之和取余八、动爻＝三者之和取余六
    for nums in ((1, 1, 1), (8, 8, 8), (99, 99, 99), (1, 2, 3), (7, 14, 21)):
        c = engine.query_by_numbers(*nums)
        total = sum(nums)
        lower_total = nums[1] + nums[2]
        check('{0} 上卦数符合文档'.format(nums), c['calculation']['upper_number'],
              (total % 8) or 8)
        check('{0} 下卦数符合文档'.format(nums), c['calculation']['lower_number'],
              (lower_total % 8) or 8)
        check('{0} 动爻符合文档'.format(nums), c['changing_line'],
              (total % 6) or 6)

    # ── 4. 时间起卦：已知答案 ───────────────────────────────────────
    # 2000-01-01 12:00 → 己卯年（年支卯=4）、戊午时（时支午=7）
    # 上卦 (4+1+1)=6 → 坎；下卦 (6+7)=13, 13%8=5 → 巽；动爻 13%6=1
    # 上坎下巽 = 水风井；初爻动 → 变水天需
    cast = engine.query_by_timestamp(datetime(2000, 1, 1, 12, 0))
    check('时间起卦 年支序数', cast['calculation']['year'], 4)
    check('时间起卦 时支序数', cast['calculation']['hour'], 7)
    check('时间起卦 上卦', cast['upper']['name'], '坎')
    check('时间起卦 下卦', cast['lower']['name'], '巽')
    check('时间起卦 动爻', cast['changing_line'], 1)
    check('时间起卦 主卦', cast['primary_hexagram']['name'], '水风井')
    check('时间起卦 变卦', cast['changed_hexagram']['name'], '水天需')
    # 动爻在下卦 → 下卦为用、上卦为体
    check('时间起卦 体卦', cast['body'], '坎')
    check('时间起卦 用卦', cast['use'], '巽')
    # 坎水 生 巽木 → 体生用
    check('时间起卦 体用关系',
          element_relation(cast['body'], cast['use']), 'generate')
    check_true('时间起卦注明历法偏差',
               '公历' in cast['calculation']['calendar'])

    # ── 5. 体用判定：随动爻所在卦而变 ───────────────────────────────
    for line in (1, 2, 3):
        check('动爻 {0}（在下卦）体为上卦'.format(line),
              engine.body_and_use('乾', '坤', line), ('乾', '坤'))
    for line in (4, 5, 6):
        check('动爻 {0}（在上卦）体为下卦'.format(line),
              engine.body_and_use('乾', '坤', line), ('坤', '乾'))

    # ── 6. 上下卦组合覆盖全部六十四卦 ───────────────────────────────
    names = set()
    for upper_num in range(1, 9):
        for lower_num in range(1, 9):
            upper = engine.NUMBER_TO_NAME[upper_num]
            lower = engine.NUMBER_TO_NAME[lower_num]
            cast = engine._build(upper, lower, 1, '测试', {})
            names.add(cast['primary_hexagram']['name'])
    check('8×8 组合得到 64 个不同卦名', len(names), 64)
    check_true('全部为上卦下卦合成的真实卦名',
               names == set(ALL_HEXAGRAMS.keys()),
               '差异：{0}'.format(sorted(names ^ set(ALL_HEXAGRAMS.keys()))[:5]))

    # ── 7. 变卦必与主卦相差一个爻，且仍是六十四卦 ───────────────────
    for upper_name in ('乾', '坤', '震', '巽'):
        for lower_name in ('坎', '离', '艮', '兑'):
            for line in range(1, 7):
                cast = engine._build(upper_name, lower_name, line, '测试', {})
                primary = ALL_HEXAGRAMS[cast['primary_hexagram']['name']]
                changed = ALL_HEXAGRAMS[cast['changed_hexagram']['name']]
                diff = sum(1 for a, b in zip(primary['lines'], changed['lines']) if a != b)
                check('{0} 动{1}爻：变卦恰好差一爻'.format(
                    cast['primary_hexagram']['name'], line), diff, 1)

    # ── 8. 分数与关系同源、排序一致 ─────────────────────────────────
    base = DivinationEngine.RELATION_SCORE
    check_true('用生体优于比和', base['support'] > base['neutral'])
    check_true('体克用优于比和', base['restrict'] > base['neutral'])
    check_true('比和优于体生用', base['neutral'] > base['generate'])
    check_true('体生用优于用克体', base['generate'] > base['attack'])
    check_true('八纯卦中乾为最高',
               DivinationEngine.SAME_SCORE['乾'] > DivinationEngine.SAME_SCORE['坤'])

    # 分数只能小幅浮动，不足以把关系顺序颠倒超过并列程度
    for line in range(1, 7):
        f = engine.calculate_fortune_score('attack', line, '坎', '离')
        check_true('动爻 {0} 的调整不超过 ±3'.format(line), abs(f['adjust']) <= 3)

    # ── 9. 关键不变量：分数分档与解读评级方向一致 ───────────────────
    trigram_names = list(engine.TRIGRAM_INFO.keys())
    mismatches = []
    labels_seen = {}
    for body in trigram_names:
        for use in trigram_names:
            relation = element_relation(body, use)
            fortune = engine.calculate_fortune_score(relation, 3, body, use)
            label = mapping.get_fortune_label(
                mapping.get_hexagram_meaning(body, use).get('fortune', 'moderate'))
            labels_seen.setdefault(relation, set()).add(label)
            if fortune['fortune_level'] not in FORTUNE_BANDS[relation]:
                mismatches.append('{0}/{1} 关系{2} 评级{3} 分数档{4}'.format(
                    body, use, relation, label, fortune['fortune_level']))
    check_true('分数分档与吉凶评级不矛盾', not mismatches,
               '矛盾：{0}'.format(mismatches[:3]))

    # 体用同卦时评级**依卦而分**（乾大吉、坤吉、其余平），并非一关系一评级。
    # 这一点必须与 SAME_SCORE 的分档对应，否则分数与评级会不一致。
    same_labels = {}
    for name in trigram_names:
        check('{0} 与自身的关系为 same'.format(name),
              element_relation(name, name), 'same')
        same_labels[name] = mapping.get_fortune_label(
            mapping.get_hexagram_meaning(name, name).get('fortune', 'moderate'))
    check('乾体用同卦评大吉', same_labels['乾'], '大吉')
    check('坤体用同卦评吉', same_labels['坤'], '吉')
    for name in trigram_names:
        if name not in ('乾', '坤'):
            check('{0} 体用同卦评平'.format(name), same_labels[name], '平')
    check_true('同卦分数与评级同序：乾 > 坤 > 其余',
               DivinationEngine.SAME_SCORE['乾']
               > DivinationEngine.SAME_SCORE['坤']
               > DivinationEngine.SAME_SCORE_DEFAULT)

    # 除 same 之外，每种关系应对应唯一评级（说明两处映射同源）
    for relation, labels in labels_seen.items():
        if relation == 'same':
            continue
        check('关系 {0} 对应唯一评级'.format(relation), len(labels), 1)
    note('体用关系 → 评级：' + '　'.join(
        '{0}={1}'.format(r, sorted(v)[0]) for r, v in sorted(labels_seen.items())))

    # ── 10. 余数为零时取八（坤）────────────────────────────────────
    # 三数之和为 8 的倍数时，上卦应取 8（坤）而非 0
    cast = engine.query_by_numbers(8, 8, 8)
    check('和为 24（8 的倍数）时上卦取坤', cast['upper']['name'], '坤')
    check('和为 24（6 的倍数）时动爻取上爻', cast['changing_line'], 6)

    # ── 11. 梅花易数恒有动爻，故变卦必不同于主卦 ────────────────────
    for nums in ((1, 2, 3), (8, 8, 8), (26, 6, 27), (99, 1, 50)):
        cast = engine.query_by_numbers(*nums)
        check_true('{0} 的主卦与变卦不同'.format(nums),
                   cast['primary_hexagram']['name'] != cast['changed_hexagram']['name'])

    # ── 12. 卦名与宫属信息完整 ─────────────────────────────────────
    cast = engine.query_by_numbers(26, 6, 27)
    for key in ('palace', 'palace_element', 'stage', 'shi', 'ying'):
        check_true('主卦含 {0}'.format(key), key in cast['primary_hexagram'])
    check('火天大有属乾宫', cast['primary_hexagram']['palace'], '乾')
    check('火天大有阶段为归魂', cast['primary_hexagram']['stage'], '归魂')
