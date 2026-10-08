# -*- coding: utf-8 -*-
"""六爻术数内核自检

设计原则：不用「程序没报错」当验证，而是拿传统术数中**结果已知**的卦去核对。
如果哪条规则写错了，这里会直接报出来。

运行（需在 backend 目录，或设置 PYTHONPATH 指向 backend）：
    py -c "from app.services.liuyao.selftest import main; raise SystemExit(main())"
"""

from datetime import datetime

from .constants import (
    TRIGRAMS, GAN_ORDER, ZHI_ORDER, ZHI_ELEMENT, SIX_GODS, SIX_RELATIVES, YAO_NAMES,
)
from .hexagrams import (
    HEXAGRAMS, by_lines, by_name, by_trigrams, palaces, expected_name_prefix,
)
from .casting import toss_coins, BACK, FRONT
from .paipan import (
    paipan, paipan_at, relative, kong_wang, six_gods, render, yao_title,
    fu_shen, _yao_relatives, _najia_for_line,
)
from .ganzhi_selftest import run as run_ganzhi
from .api_selftest import run as run_api
from .judgment_selftest import run as run_judgment
from app.services.meihua_selftest import run as run_meihua

_FAILURES = []
_CHECKS = 0


def check(label, actual, expected):
    global _CHECKS
    _CHECKS += 1
    if actual != expected:
        _FAILURES.append(
            '{0}\n        期望: {1}\n        实际: {2}'.format(label, expected, actual))
        return False
    return True


def check_true(label, condition, detail=''):
    global _CHECKS
    _CHECKS += 1
    if not condition:
        _FAILURES.append('{0}{1}'.format(label, ('  ' + detail) if detail else ''))
        return False
    return True


def _summary(pan):
    """把卦盘压成 (纳甲, 六亲, 六神) 三元组列表，便于与已知结果比对"""
    return [(y['na_jia'], y['relative'], y['god']) for y in pan['yaos']]


# ---------------------------------------------------------------------------
# 1. 八卦符号（防的是旧代码那三处错误）
# ---------------------------------------------------------------------------
def test_trigrams():
    expected = {
        '乾': '☰', '兑': '☱', '离': '☲', '震': '☳',
        '巽': '☴', '坎': '☵', '艮': '☶', '坤': '☷',
    }
    for name, sym in expected.items():
        check('八卦符号 {0}'.format(name), TRIGRAMS[name]['symbol'], sym)

    symbols = [t['symbol'] for t in TRIGRAMS.values()]
    check_true('八个卦符互不重复', len(set(symbols)) == 8,
               '实际: {0}'.format(sorted(symbols)))
    check_true('☱（兑）必须出现（旧代码缺失）', '☱' in symbols)
    check_true('☷（坤）不可被两卦共用', symbols.count('☷') == 1)

    elements = {n: t['element'] for n, t in TRIGRAMS.items()}
    check('八卦五行', elements, {
        '乾': '金', '兑': '金', '离': '火', '震': '木',
        '巽': '木', '坎': '水', '艮': '土', '坤': '土',
    })


# ---------------------------------------------------------------------------
# 2. 六十四卦：数量、唯一性、八宫卦序
# ---------------------------------------------------------------------------
TRADITIONAL_PALACES = {
    '乾': ['乾为天', '天风姤', '天山遁', '天地否', '风地观', '山地剥', '火地晋', '火天大有'],
    '坎': ['坎为水', '水泽节', '水雷屯', '水火既济', '泽火革', '雷火丰', '地火明夷', '地水师'],
    '艮': ['艮为山', '山火贲', '山天大畜', '山泽损', '火泽睽', '天泽履', '风泽中孚', '风山渐'],
    '震': ['震为雷', '雷地豫', '雷水解', '雷风恒', '地风升', '水风井', '泽风大过', '泽雷随'],
    '巽': ['巽为风', '风天小畜', '风火家人', '风雷益', '天雷无妄', '火雷噬嗑', '山雷颐', '山风蛊'],
    '离': ['离为火', '火山旅', '火风鼎', '火水未济', '山水蒙', '风水涣', '天水讼', '天火同人'],
    '坤': ['坤为地', '地雷复', '地泽临', '地天泰', '雷天大壮', '泽天夬', '水天需', '水地比'],
    '兑': ['兑为泽', '泽水困', '泽地萃', '泽山咸', '水山蹇', '地山谦', '雷山小过', '雷泽归妹'],
}


def test_hexagrams():
    check('六十四卦总数', len(HEXAGRAMS), 64)

    table = palaces()
    for palace, names in TRADITIONAL_PALACES.items():
        actual = [h['name'] for h in table[palace]]
        check('{0}宫八卦卦序'.format(palace), actual, names)

    # 同卦不同宫的情况必须不存在（每卦只属一宫）
    total = sum(len(v) for v in table.values())
    check('八宫合计 64 卦', total, 64)

    # 上下卦组合应覆盖全部 8x8
    pairs = {(h['upper'], h['lower']) for h in HEXAGRAMS.values()}
    check('上下卦组合覆盖 8x8', len(pairs), 64)

    # ★ 关键校验：由**算法生成**的上下卦，去反推卦名应有的取象前缀，
    #   必须与**传统卦名**一致。这是验证变爻算法是否正确的独立手段。
    for name, h in HEXAGRAMS.items():
        prefix = expected_name_prefix(h)
        check_true(
            '{0} 卦名与上下卦取象一致'.format(name),
            name.startswith(prefix),
            '上卦 {0}({1}) 下卦 {2}({3}) → 应为「{4}」开头'.format(
                h['upper'], TRIGRAMS[h['upper']]['nature'],
                h['lower'], TRIGRAMS[h['lower']]['nature'], prefix))


def test_shi_ying():
    cases = {
        '乾为天': (6, 3), '天风姤': (1, 4), '天山遁': (2, 5), '天地否': (3, 6),
        '风地观': (4, 1), '山地剥': (5, 2), '火地晋': (4, 1), '火天大有': (3, 6),
        '水火既济': (3, 6), '地水师': (3, 6), '水泽节': (1, 4),
    }
    for name, (shi, ying) in cases.items():
        h = by_name(name)
        check('{0} 世应'.format(name), (h['shi'], h['ying']), (shi, ying))


def test_lookup():
    check('由六爻取乾为天', by_lines((1, 1, 1, 1, 1, 1))['name'], '乾为天')
    check('由六爻取坤为地', by_lines((0, 0, 0, 0, 0, 0))['name'], '坤为地')
    check('由六爻取水火既济', by_lines((1, 0, 1, 0, 1, 0))['name'], '水火既济')
    check('由六爻取天风姤', by_lines((0, 1, 1, 1, 1, 1))['name'], '天风姤')
    check('由上卦下卦取卦', by_trigrams('坎', '离')['name'], '水火既济')
    check('由上卦下卦取卦2', by_trigrams('乾', '巽')['name'], '天风姤')


# ---------------------------------------------------------------------------
# 3. 六亲取用
# ---------------------------------------------------------------------------
def test_relatives():
    # 以金为「我」：土生金=父母、金=兄弟、金生水=子孙、金克木=妻财、火克金=官鬼
    metal = {'土': '父母', '金': '兄弟', '水': '子孙', '木': '妻财', '火': '官鬼'}
    for other, expected in metal.items():
        check('六亲 金 vs {0}'.format(other), relative('金', other), expected)

    # 每种「我」都应恰好产生五种六亲，不重不漏
    for me in ('金', '木', '水', '火', '土'):
        got = {relative(me, o) for o in ('金', '木', '水', '火', '土')}
        check('五行 {0} 的六亲覆盖'.format(me), got,
              {'父母', '兄弟', '子孙', '妻财', '官鬼'})


# ---------------------------------------------------------------------------
# 4. 旬空
# ---------------------------------------------------------------------------
def test_kong_wang():
    cases = {
        ('甲', '子'): ('戌', '亥'), ('癸', '酉'): ('戌', '亥'),
        ('甲', '戌'): ('申', '酉'), ('甲', '申'): ('午', '未'),
        ('甲', '午'): ('辰', '巳'), ('甲', '辰'): ('寅', '卯'),
        ('甲', '寅'): ('子', '丑'),
    }
    for (gan, zhi), expected in cases.items():
        check('旬空 {0}{1}'.format(gan, zhi), kong_wang(gan, zhi), expected)


# ---------------------------------------------------------------------------
# 5. 六神起例
# ---------------------------------------------------------------------------
def test_six_gods():
    check('甲日六神', six_gods('甲'), ['青龙', '朱雀', '勾陈', '螣蛇', '白虎', '玄武'])
    check('己日六神', six_gods('己'), ['螣蛇', '白虎', '玄武', '青龙', '朱雀', '勾陈'])
    check('庚日六神', six_gods('庚'), ['白虎', '玄武', '青龙', '朱雀', '勾陈', '螣蛇'])
    for gan in GAN_ORDER:
        gods = six_gods(gan)
        check('{0}日六神为六神集合'.format(gan), set(gods), set(SIX_GODS))


# ---------------------------------------------------------------------------
# 6. 摇卦取值
# ---------------------------------------------------------------------------
class _FakeChoice(object):
    """固定的伪随机源，用于精确控制三枚铜钱的正反"""

    def __init__(self, faces):
        self.faces = list(faces)
        self.i = 0

    def __call__(self, options):
        face = self.faces[self.i % len(self.faces)]
        self.i += 1
        return face


def test_casting():
    cases = [
        ([FRONT, FRONT, FRONT], 6, '交', '阴', True),    # 三字 → 老阴
        ([BACK, FRONT, FRONT], 7, '单', '阳', False),    # 一背 → 少阳
        ([BACK, BACK, FRONT], 8, '拆', '阴', False),     # 二背 → 少阴
        ([BACK, BACK, BACK], 9, '重', '阳', True),       # 三背 → 老阳
    ]
    for faces, value, name, yy, moving in cases:
        r = toss_coins(_FakeChoice(faces))
        label = '摇卦 {0}'.format('、'.join(faces))
        check(label + ' 爻值', r['value'], value)
        check(label + ' 爻名', r['name'], name)
        check(label + ' 阴阳', r['yin_yang'], yy)
        check(label + ' 动爻', r['moving'], moving)
        check(label + ' 背数', r['backs'], faces.count(BACK))
    check('爻名表', YAO_NAMES, {6: '交', 7: '单', 8: '拆', 9: '重'})


# ---------------------------------------------------------------------------
# 7. 装卦：拿已知结果的卦核对
# ---------------------------------------------------------------------------
# 乾为天（乾宫本宫，全静）：子孙、妻财、父母、官鬼、兄弟、父母
QIAN_WEI_TIAN = [
    ('甲子', '子孙', '青龙'), ('甲寅', '妻财', '朱雀'), ('甲辰', '父母', '勾陈'),
    ('壬午', '官鬼', '螣蛇'), ('壬申', '兄弟', '白虎'), ('壬戌', '父母', '玄武'),
]
# 坤为地（坤宫本宫，全静）。注意三爻乙卯木：木克土为「克我」，故为官鬼。
KUN_WEI_DI = [
    ('乙未', '兄弟', '青龙'), ('乙巳', '父母', '朱雀'), ('乙卯', '官鬼', '勾陈'),
    ('癸丑', '兄弟', '螣蛇'), ('癸亥', '妻财', '白虎'), ('癸酉', '子孙', '玄武'),
]
# 水火既济（坎宫三世，全静）
JI_JI = [
    ('己卯', '子孙', '青龙'), ('己丑', '官鬼', '朱雀'), ('己亥', '兄弟', '勾陈'),
    ('戊申', '父母', '螣蛇'), ('戊戌', '官鬼', '白虎'), ('戊子', '兄弟', '玄武'),
]


def test_paipan_known():
    pan = paipan([7, 7, 7, 7, 7, 7], '甲', '子')
    check('乾为天之卦名', pan['ben']['name'], '乾为天')
    check('乾为天所属宫', pan['ben']['palace'], '乾')
    check('乾为天宫五行', pan['ben']['palace_element'], '金')
    check('乾为天阶段', pan['ben']['stage'], '本宫')
    check('乾为天装卦', _summary(pan), QIAN_WEI_TIAN)
    check('乾为天为静卦', pan['is_jing'], True)
    check('乾为天旬空', pan['kong_wang'], ['戌', '亥'])
    check('乾为天上爻旬空', pan['yaos'][5]['is_kong'], True)
    check('乾为天初爻非旬空', pan['yaos'][0]['is_kong'], False)
    check('乾为天世爻', [y['is_shi'] for y in pan['yaos']],
          [False, False, False, False, False, True])
    check('乾为天应爻', [y['is_ying'] for y in pan['yaos']],
          [False, False, True, False, False, False])

    pan = paipan([8, 8, 8, 8, 8, 8], '甲', '子')
    check('坤为地之卦名', pan['ben']['name'], '坤为地')
    check('坤为地装卦', _summary(pan), KUN_WEI_DI)
    check('坤为地宫五行', pan['ben']['palace_element'], '土')

    pan = paipan([7, 8, 7, 8, 7, 8], '甲', '子')
    check('水火既济之卦名', pan['ben']['name'], '水火既济')
    check('水火既济装卦', _summary(pan), JI_JI)
    check('水火既济阶段', pan['ben']['stage'], '三世')


def test_bian_gua():
    # 乾为天，初爻老阳发动 → 初爻变阴 → 下卦由乾变巽 → 天风姤
    pan = paipan([9, 7, 7, 7, 7, 7], '甲', '子')
    check('动爻变卦之卦名', pan['bian']['name'], '天风姤')
    check('动爻位置', pan['moving_lines'], [1])
    check('动爻标记', pan['yaos'][0]['moving'], True)
    check('非动爻无变爻', pan['yaos'][1]['bian'], None)
    check_true('动爻有变爻纳甲', pan['yaos'][0]['bian'] is not None)
    # 天风姤属乾宫，宫五行仍为金，故变爻六亲按金定
    check('变爻六亲按本卦宫定', pan['yaos'][0]['bian']['relative'],
          relative('金', pan['yaos'][0]['bian']['element']))

    # 乾为天，四爻老阳发动 → 上卦由乾变巽 → 风天小畜
    pan = paipan([7, 7, 7, 9, 7, 7], '甲', '子')
    check('四爻动之变卦', pan['bian']['name'], '风天小畜')
    check('四爻动位置', pan['moving_lines'], [4])

    # 老阴发动：坤为地初爻老阴 → 变阳 → 下卦由坤变震 → 地雷复
    pan = paipan([6, 8, 8, 8, 8, 8], '甲', '子')
    check('老阴发动之变卦', pan['bian']['name'], '地雷复')

    # 多爻发动：初爻与四爻
    pan = paipan([9, 7, 7, 9, 7, 7], '甲', '子')
    check('两爻发动位置', pan['moving_lines'], [1, 4])


# 八纯卦的装卦结果（纳甲 + 六亲），覆盖全部 8 个卦的内卦与外卦纳甲。
# 这是独立于实现的数据，等价于用传统卦书核对。
PURE_HEXAGRAM_EXPECTED = {
    '乾为天': [('甲子', '子孙'), ('甲寅', '妻财'), ('甲辰', '父母'),
             ('壬午', '官鬼'), ('壬申', '兄弟'), ('壬戌', '父母')],
    '坤为地': [('乙未', '兄弟'), ('乙巳', '父母'), ('乙卯', '官鬼'),
             ('癸丑', '兄弟'), ('癸亥', '妻财'), ('癸酉', '子孙')],
    '震为雷': [('庚子', '父母'), ('庚寅', '兄弟'), ('庚辰', '妻财'),
             ('庚午', '子孙'), ('庚申', '官鬼'), ('庚戌', '妻财')],
    '巽为风': [('辛丑', '妻财'), ('辛亥', '父母'), ('辛酉', '官鬼'),
             ('辛未', '妻财'), ('辛巳', '子孙'), ('辛卯', '兄弟')],
    '坎为水': [('戊寅', '子孙'), ('戊辰', '官鬼'), ('戊午', '妻财'),
             ('戊申', '父母'), ('戊戌', '官鬼'), ('戊子', '兄弟')],
    '离为火': [('己卯', '父母'), ('己丑', '子孙'), ('己亥', '官鬼'),
             ('己酉', '妻财'), ('己未', '子孙'), ('己巳', '兄弟')],
    '艮为山': [('丙辰', '兄弟'), ('丙午', '父母'), ('丙申', '子孙'),
             ('丙戌', '兄弟'), ('丙子', '妻财'), ('丙寅', '官鬼')],
    '兑为泽': [('丁巳', '官鬼'), ('丁卯', '妻财'), ('丁丑', '父母'),
             ('丁亥', '子孙'), ('丁酉', '兄弟'), ('丁未', '父母')],
}


def test_pure_hexagrams():
    """八纯卦装卦：覆盖全部 8 卦的内外纳甲与 8 种宫五行"""
    for name, expected in PURE_HEXAGRAM_EXPECTED.items():
        h = by_name(name)
        check_true('{0} 存在'.format(name), h is not None)
        if h is None:
            continue
        values = [7 if b else 8 for b in h['lines']]
        pan = paipan(values, '甲', '子')
        check('八纯卦 {0} 取卦'.format(name), pan['ben']['name'], name)
        check('八纯卦 {0} 装卦'.format(name),
              [(y['na_jia'], y['relative']) for y in pan['yaos']], expected)
        check('八纯卦 {0} 阶段'.format(name), pan['ben']['stage'], '本宫')
        check('八纯卦 {0} 世应'.format(name),
              (pan['ben']['shi'], pan['ben']['ying']), (6, 3))


# 说明：曾试图断言「一卦六爻地支两两不同」，这是**错误**的假设。
# 内外卦纳甲地支本就会重复，例如天山遁 = 下艮(辰午申) + 上乾(午申戌)，
# 午、申各出现两次。故不设此断言。


def test_yao_title():
    """爻题格式：初爻与上爻「初／上」在前，中间四爻「九／六」在前"""
    cases = [
        (1, True, '初九'), (1, False, '初六'),
        (2, True, '九二'), (2, False, '六二'),
        (3, True, '九三'), (3, False, '六三'),
        (4, True, '九四'), (4, False, '六四'),
        (5, True, '九五'), (5, False, '六五'),
        (6, True, '上九'), (6, False, '上六'),
    ]
    for position, is_yang, expected in cases:
        check('爻题 第{0}爻{1}'.format(position, '阳' if is_yang else '阴'),
              yao_title(position, is_yang), expected)


def test_fu_shen():
    """伏神：六亲齐全则无，缺则从本宫纯卦取该六亲之爻"""
    # 乾为天六亲齐全（子孙、妻财、父母、官鬼、兄弟、父母）→ 无伏神
    check('乾为天无伏神', fu_shen(by_name('乾为天')), [])

    # 天风姤（乾宫）缺妻财，伏神应取乾为天二爻甲寅木，飞神为姤卦二爻辛亥水
    fu = fu_shen(by_name('天风姤'))
    check('天风姤伏神数量', len(fu), 1)
    if fu:
        check('天风姤伏神六亲', fu[0]['relative'], '妻财')
        check('天风姤伏神位置', fu[0]['position'], 2)
        check('天风姤伏神纳甲', fu[0]['na_jia'], '甲寅')
        check('天风姤伏神五行', fu[0]['element'], '木')
        check('天风姤飞神纳甲', fu[0]['fei_shen']['na_jia'], '辛亥')
        check('天风姤飞神六亲', fu[0]['fei_shen']['relative'], '子孙')

    # 坤为地六亲齐全 → 无伏神
    check('坤为地无伏神', fu_shen(by_name('坤为地')), [])

    # 全面检查：伏神的六亲集合必须正好等于本卦所缺的六亲；
    # 飞神必须与本卦同位之爻一致
    for name, h in HEXAGRAMS.items():
        me = h['palace_element']
        present = set(row[3] for row in _yao_relatives(h, me))
        expected_missing = set(r for r in SIX_RELATIVES if r not in present)
        fus = fu_shen(h)
        check('{0} 伏神六亲集合'.format(name),
              set(f['relative'] for f in fus), expected_missing)
        for f in fus:
            check_true('{0} 伏神位置在 1–6'.format(name),
                       1 <= f['position'] <= 6)
            gan, zhi = _najia_for_line(h, f['position'] - 1)
            check('{0} 伏神第{1}爻飞神'.format(name, f['position']),
                  f['fei_shen']['na_jia'], gan + zhi)

    # 伏神应带进装卦结果
    pan = paipan([8, 7, 7, 7, 7, 7], '甲', '子')      # 天风姤：下巽上乾
    check('装卦结果之卦名', pan['ben']['name'], '天风姤')
    check('装卦结果含伏神', len(pan['fu_shen']), 1)
    check('装卦结果伏神六亲', pan['fu_shen'][0]['relative'], '妻财')
    check_true('变卦伏神字段为列表', isinstance(pan['bian_fu_shen'], list))


def test_paipan_at():
    """按起卦时刻排盘：四柱、月建、日建应自动带入"""
    pan = paipan_at([7, 7, 7, 7, 7, 7], datetime(2000, 1, 1, 12, 0))
    check('按时刻排盘 卦名', pan['ben']['name'], '乾为天')
    check('按时刻排盘 四柱年', pan['si_zhu']['year']['gan_zhi'], '己卯')
    check('按时刻排盘 四柱月', pan['si_zhu']['month']['gan_zhi'], '丙子')
    check('按时刻排盘 四柱日', pan['si_zhu']['day']['gan_zhi'], '戊午')
    check('按时刻排盘 四柱时', pan['si_zhu']['hour']['gan_zhi'], '戊午')
    check('按时刻排盘 月建', pan['month_branch'], '子')
    check('按时刻排盘 日建', pan['day_branch'], '午')
    # 旬空与六神由日干日支决定，应与四柱自洽。
    # 注意：2000-01-01 是**戊午**日（不是甲子日）。戊午属甲寅旬，
    # 该旬含寅卯辰巳午未申酉戌亥，缺子丑，故旬空为子丑；
    # 六神按日干起，戊日初爻起勾陈（甲乙日才起青龙）。
    check('按时刻排盘 日柱', pan['day']['gan_zhi'], '戊午')
    check('按时刻排盘 旬空', pan['kong_wang'], ['子', '丑'])
    check('按时刻排盘 六神首爻', pan['yaos'][0]['god'], '勾陈')
    check('按时刻排盘 六神末爻', pan['yaos'][5]['god'], '朱雀')
    check('按时刻排盘 上爻旬空', pan['yaos'][5]['is_kong'], False)
    check('按时刻排盘 初爻旬空', pan['yaos'][0]['is_kong'], True)

    # 静卦与动卦都应可用
    pan2 = paipan_at([9, 7, 7, 7, 7, 7], datetime(2000, 1, 1, 12, 0))
    check('按时刻排盘 动卦变卦', pan2['bian']['name'], '天风姤')
    check('按时刻排盘 动卦四柱一致', pan2['si_zhu']['day']['gan_zhi'], '戊午')


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main():
    tests = [
        test_trigrams, test_hexagrams, test_shi_ying, test_lookup,
        test_relatives, test_kong_wang, test_six_gods, test_casting,
        test_pure_hexagrams, test_paipan_known, test_bian_gua, test_yao_title,
        test_fu_shen, test_paipan_at,
    ]
    notes = []
    for t in tests:
        t()
    run_ganzhi(check, check_true, notes.append)
    run_judgment(check, check_true, notes.append)
    run_meihua(check, check_true, notes.append)
    run_api(check, check_true, notes.append)

    print('=' * 64)
    print('玄镜易 · 术数内核自检（六爻纳甲 + 梅花易数）')
    print('=' * 64)
    print('检查项: {0}　失败: {1}'.format(_CHECKS, len(_FAILURES)))

    if _FAILURES:
        print('')
        for f in _FAILURES:
            print('  ✗ ' + f)

    if notes:
        print('')
        print('量化对照（精度不隐瞒）：')
        for n in notes:
            print('  ' + n)

    if _FAILURES:
        print('')
        print('结果: 未通过')
        return 1

    print('')
    print('结果: 全部通过')

    samples = [
        ('乾为天（静卦，六亲齐全）', [7, 7, 7, 7, 7, 7]),
        ('乾为天初爻老阳发动', [9, 7, 7, 7, 7, 7]),
        ('天风姤（静卦，缺妻财故有伏神）', [8, 7, 7, 7, 7, 7]),
    ]
    for title, values in samples:
        text = render(paipan_at(values, datetime(2000, 1, 1, 12, 0)))
        print('')
        print('抽样：{0}　起卦时刻 2000-01-01 12:00'.format(title))
        print('-' * 64)
        try:
            print(text)
        except UnicodeEncodeError:
            # Windows 控制台默认 GBK，无法编码 ▬ ☰ 等字符。
            # 这是终端限制，不影响自检结论。
            print('（当前终端编码无法显示卦盘样本；'
                  '设 PYTHONIOENCODING=utf-8 后即可正常显示）')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
