# -*- coding: utf-8 -*-
"""用神选取与旺衰规则引擎

定位与边界（务必先读）
----------------------
**装卦是规范可校验的**（纳甲、六亲、世应、旬空、伏神都有确定的传统规则），
**但"旺衰打分"没有经典依据**。古籍给的是定性判断——月破为凶、回头生为吉、
用神旬空主落空……从未给出数值权重。

因此本模块的做法是：

1. 每一条判断都产出一个**带理由的因子**（`factors`），说明依据的规则；
2. 所有**权重集中在本文件的 `WEIGHTS` 表**，可整体调整，不在逻辑里散落魔数；
3. `score` 只是这些因子的线性叠加，用于排序与分档；**它不是"准确率"**，
   换一套权重就会得到不同数值，而因子清单不变。

换句话说：**能追溯到规则的判断是可靠的，分数只是它的摘要**。界面上应优先
展示因子清单，分数只作辅助。

覆盖的规则
----------
用神选取、月建旺衰、月破、日建旺衰、日破（含"动而逢冲为冲起"）、旬空（含填实）、
用神发动、变爻回头生克、他爻动来生克、伏神（飞神生克与透出）、进神退神、
六冲卦六合卦、原神忌神仇神。
"""

from .constants import ZHI_ORDER, ZHI_ELEMENT, GENERATION, RESTRICTION
from .paipan import relative

# ---------------------------------------------------------------------------
# 地支刑冲合
# ---------------------------------------------------------------------------
ZHI_CHONG = {
    '子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
    '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳',
}

ZHI_HE = {
    '子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯',
    '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午',
}

# 三合局（地支三合成局）
SAN_HE = {
    frozenset(('申', '子', '辰')): '水',
    frozenset(('亥', '卯', '未')): '木',
    frozenset(('寅', '午', '戌')): '火',
    frozenset(('巳', '酉', '丑')): '金',
}

# 进神／退神：动爻与变爻同五行而地支递进或递退
JIN_SHEN = {
    ('亥', '子'), ('寅', '卯'), ('巳', '午'), ('申', '酉'),
    ('丑', '辰'), ('辰', '未'), ('未', '戌'), ('戌', '丑'),
}
TUI_SHEN = set((b, a) for a, b in JIN_SHEN)

# 六冲卦（八纯卦 + 天雷无妄 + 雷天大壮）
LIU_CHONG_GUA = {
    '乾为天', '坤为地', '震为雷', '巽为风', '坎为水', '离为火', '艮为山', '兑为泽',
    '天雷无妄', '雷天大壮',
}

# 六合卦
LIU_HE_GUA = {
    '天地否', '地天泰', '地雷复', '雷地豫',
    '水泽节', '泽水困', '火山旅', '山火贲',
}

# ---------------------------------------------------------------------------
# 用神选取：按所问之事
# ---------------------------------------------------------------------------
# 传统取用：「用神」即所问之事的代表六亲。
#   求财／妻子（男占）→ 妻财
#   求官／事业／丈夫（女占）→ 官鬼
#   父母／长辈／文书／房屋／学业 → 父母
#   子女／晚辈／医药解忧 → 子孙
#   兄弟／朋友／竞争者 → 兄弟
#   泛问自身 → 世爻
TOPIC_YONGSHEN = {
    'career': '官鬼',        # 事业、功名、工作
    'wealth': '妻财',        # 财运、求财、生意
    'study': '父母',         # 学业、考试、文书
    'family': '父母',        # 长辈、房屋、车
    'children': '子孙',      # 子女、晚辈、下属
    'friends': '兄弟',       # 朋友、同事、竞争
    'health': '官鬼',        # 疾病（官鬼为病，子孙为药）
    'travel': '父母',        # 出行（父母为行李车马）
    'relationship': None,    # 感情：依性别取（男占妻财、女占官鬼）
    'general': '世爻',       # 泛问，取世爻为自身
}

TOPIC_LABELS = {
    'career': '事业功名',
    'wealth': '财运求财',
    'study': '学业考试',
    'family': '长辈家宅',
    'children': '子女晚辈',
    'friends': '朋友同事',
    'health': '疾病健康',
    'travel': '出行',
    'relationship': '感情婚姻',
    'general': '泛问自身',
}

# 六冲在哪些问事上反为吉（忧患得解）
CHONG_IS_GOOD = {'health'}

# ---------------------------------------------------------------------------
# 权重表（唯一可调处）
# ---------------------------------------------------------------------------
# 说明：以下数值是工程选择，不是经典数据。调这一张表即可整体改变倾向，
# 因子清单（判断依据）不会变。
WEIGHTS = {
    'month_same': 18,          # 用神临月建
    'month_generate': 12,      # 月建生用神
    'month_same_element': 8,   # 月建与用神同五行（比和）
    'month_drain': -6,         # 用神生月建（泄气）
    'month_restrict': -4,      # 用神克月建（耗力）
    'month_attack': -14,       # 月建克用神
    'month_break': -20,        # 月破
    'day_same': 14,            # 用神临日建
    'day_generate': 9,         # 日建生用神
    'day_same_element': 6,     # 日建与用神同五行
    'day_drain': -4,
    'day_restrict': -3,
    'day_attack': -10,         # 日建克用神
    'day_break': -12,          # 日破
    'day_chong_moving': 6,     # 动而逢日冲（冲起）
    'kong': -12,               # 旬空
    'kong_moving': -6,         # 旬空发动（出空可用）
    'yong_moving': 6,          # 用神发动
    'bian_back_generate': 6,   # 变爻回头生
    'bian_back_restrict': -10,  # 变爻回头克
    'other_moving_generate': 6,  # 他爻动来生用神
    'other_moving_attack': -8,   # 他爻动来克用神
    'other_bian_generate': 4,    # 他爻变爻生用神
    'other_bian_attack': -6,     # 他爻变爻克用神
    'fu_hidden': -10,          # 用神不上卦（伏藏）
    'fu_fei_generate': 6,      # 飞神生伏神
    'fu_fei_attack': -8,       # 飞神克伏神
    'fu_decent': 6,            # 伏神得日月生扶
    'jin_shen': 8,             # 进神
    'tui_shen': -8,            # 退神
    'gua_liu_chong': -8,       # 六冲卦
    'gua_liu_he': 8,           # 六合卦
    'yong_on_shi': 4,          # 用神临世
}

BASE_SCORE = 50

# 分档阈值（同样为工程选择）
LEVELS = (
    (82, '大吉'),
    (68, '吉'),
    (54, '平吉'),
    (40, '平'),
    (26, '凶'),
    (0, '大凶'),
)


def _factor(kind, sign, weight, text, advice=''):
    return {
        'kind': kind,
        'sign': sign,
        'weight': weight,
        'text': text,
        'advice': advice,
    }


# ---------------------------------------------------------------------------
# 单项规则：月建
# ---------------------------------------------------------------------------
def month_factor(zhi, element, month_zhi):
    """用神与月建的关系。月建为一卦之提纲，权重最高。"""
    if ZHI_CHONG.get(zhi) == month_zhi:
        return _factor('month', '-', WEIGHTS['month_break'],
                       '用神{zhi}与月建{month}相冲，是为月破，根基受损'.format(zhi=zhi, month=month_zhi),
                       '月破之事难以成立，宜静待出月再图，不宜强行推进')
    if zhi == month_zhi:
        return _factor('month', '+', WEIGHTS['month_same'],
                       '用神{zhi}临月建，当令得势'.format(zhi=zhi),
                       '正逢其时，可顺势而为')
    month_el = ZHI_ELEMENT[month_zhi]
    if GENERATION[month_el] == element:
        return _factor('month', '+', WEIGHTS['month_generate'],
                       '月建{month}（{me}）生用神{el}，得月令之助'.format(month=month_zhi, me=month_el, el=element),
                       '外有助力，可借势推进')
    if month_el == element:
        return _factor('month', '+', WEIGHTS['month_same_element'],
                       '月建{month}与用神同为{el}，比和有助'.format(month=month_zhi, el=element))
    if GENERATION[element] == month_el:
        return _factor('month', '-', WEIGHTS['month_drain'],
                       '用神{el}泄气于月建{month}（{me}）'.format(el=element, month=month_zhi, me=month_el),
                       '当令不在自己这边，付出多而收效少')
    if RESTRICTION[element] == month_el:
        return _factor('month', '-', WEIGHTS['month_restrict'],
                       '用神{el}克月建{month}（{me}），虽能制之而自耗'.format(el=element, month=month_zhi, me=month_el))
    return _factor('month', '-', WEIGHTS['month_attack'],
                   '月建{month}（{me}）克用神{el}，受制于月令'.format(month=month_zhi, me=month_el, el=element),
                   '时令不利，宜守不宜攻')


# ---------------------------------------------------------------------------
# 单项规则：日建
# ---------------------------------------------------------------------------
def day_factor(zhi, element, day_zhi, moving=False):
    """用神与日建的关系。日建为一卦之主宰。"""
    if ZHI_CHONG.get(zhi) == day_zhi:
        if moving:
            return _factor('day', '+', WEIGHTS['day_chong_moving'],
                           '用神发动而逢日冲{zhi}，是为冲起，反有动力'.format(zhi=zhi),
                           '受激而动，反可成事')
        return _factor('day', '-', WEIGHTS['day_break'],
                       '用神{zhi}与日建{day}相冲，是为日破，受冲受损'.format(zhi=zhi, day=day_zhi),
                       '当日之事受挫，宜暂缓')
    if zhi == day_zhi:
        return _factor('day', '+', WEIGHTS['day_same'],
                       '用神{zhi}临日建，得日辰之力'.format(zhi=zhi),
                       '当下正得其力，宜及时行动')
    day_el = ZHI_ELEMENT[day_zhi]
    if GENERATION[day_el] == element:
        return _factor('day', '+', WEIGHTS['day_generate'],
                       '日建{day}（{de}）生用神{el}'.format(day=day_zhi, de=day_el, el=element),
                       '眼下有助力，可着手')
    if day_el == element:
        return _factor('day', '+', WEIGHTS['day_same_element'],
                       '日建{day}与用神同为{el}，比和'.format(day=day_zhi, el=element))
    if GENERATION[element] == day_el:
        return _factor('day', '-', WEIGHTS['day_drain'],
                       '用神{el}泄气于日建{day}（{de}）'.format(el=element, day=day_zhi, de=day_el))
    if RESTRICTION[element] == day_el:
        return _factor('day', '-', WEIGHTS['day_restrict'],
                       '用神{el}克日建{day}（{de}），耗力'.format(el=element, day=day_zhi, de=day_el))
    return _factor('day', '-', WEIGHTS['day_attack'],
                   '日建{day}（{de}）克用神{el}，当下受制'.format(day=day_zhi, de=day_el, el=element),
                   '眼下不宜强行，避其锋芒')


# ---------------------------------------------------------------------------
# 单项规则：旬空
# ---------------------------------------------------------------------------
def kong_factor(zhi, is_kong, month_zhi, day_zhi, moving=False):
    """旬空。逢月建／日建填实则不作空论；发动者出空可用。"""
    if not is_kong:
        return None
    if zhi == month_zhi or zhi == day_zhi:
        return _factor('kong', '0', 0,
                       '用神{zhi}虽在旬空，然临月建／日建，谓之填实，不作空论'.format(zhi=zhi))
    if moving:
        return _factor('kong', '-', WEIGHTS['kong_moving'],
                       '用神{zhi}旬空而发动，出空可用，力量打折'.format(zhi=zhi),
                       '时机未到，须待出空之日方见分晓')
    return _factor('kong', '-', WEIGHTS['kong'],
                   '用神{zhi}落旬空，主事多落空、暂不得力'.format(zhi=zhi),
                   '眼下虚而不实，宜待出旬再议')


# ---------------------------------------------------------------------------
# 单项规则：伏神
# ---------------------------------------------------------------------------
def fu_factor(fu, month_zhi, day_zhi):
    """用神不上卦，须借伏神论。看飞神生克与能否透出。"""
    factors = [_factor('fu', '-', WEIGHTS['fu_hidden'],
                       '用神不上卦，伏于第 {n} 爻{fei}之下，伏藏难出'.format(
                           n=fu['position'], fei=fu['fei_shen']['na_jia'] + fu['fei_shen']['relative']),
                       '此事目前不显，须待时机引动')]

    fei_el = fu['fei_shen']['element']
    if GENERATION[fei_el] == fu['element']:
        factors.append(_factor('fu', '+', WEIGHTS['fu_fei_generate'],
                               '飞神{fe}生伏神{fu}，伏而可出'.format(
                                   fe=fu['fei_shen']['na_jia'], fu=fu['na_jia']),
                               '有外力提携，静待即可显'))
    elif RESTRICTION[fei_el] == fu['element']:
        factors.append(_factor('fu', '-', WEIGHTS['fu_fei_attack'],
                               '飞神{fe}克伏神{fu}，伏而难出'.format(
                                   fe=fu['fei_shen']['na_jia'], fu=fu['na_jia']),
                               '受压制，须先解开阻滞'))

    if fu['zhi'] == month_zhi or fu['zhi'] == day_zhi:
        factors.append(_factor('fu', '+', WEIGHTS['fu_decent'],
                               '伏神{zhi}临月建／日建，得扶可以透出'.format(zhi=fu['zhi']),
                               '时机一到自会显形'))
    return factors


# ---------------------------------------------------------------------------
# 单项规则：进神退神
# ---------------------------------------------------------------------------
def jin_tui_factor(yong_zhi, bian_zhi):
    """动爻与变爻同五行而地支递进为进神，递退为退神。"""
    if yong_zhi == bian_zhi:
        return None
    if (yong_zhi, bian_zhi) in JIN_SHEN:
        return _factor('jin', '+', WEIGHTS['jin_shen'],
                       '用神{z}化{b}，同气递进，是为进神，力增'.format(z=yong_zhi, b=bian_zhi),
                       '势头渐强，可乘势而进')
    if (yong_zhi, bian_zhi) in TUI_SHEN:
        return _factor('tui', '-', WEIGHTS['tui_shen'],
                       '用神{z}化{b}，同气递退，是为退神，力减'.format(z=yong_zhi, b=bian_zhi),
                       '势头渐弱，宜见好即收')
    return None


# ---------------------------------------------------------------------------
# 单项规则：卦体六冲六合
# ---------------------------------------------------------------------------
def gua_factor(gua_name, topic):
    """六冲卦主散，六合卦主成。占病逢冲反为吉（病气得散）。

    注意：占病时六冲的**符号与权重都要翻转**，否则会出现"标着 + 却扣分"。
    """
    if gua_name in LIU_CHONG_GUA:
        good = topic in CHONG_IS_GOOD
        magnitude = abs(WEIGHTS['gua_liu_chong'])
        weight = magnitude if good else -magnitude
        return _factor('gua', '+' if good else '-', weight,
                       '{gua}为六冲卦，主散'.format(gua=gua_name),
                       '忧患者得冲而解，可望消散' if good else '事多散而不聚，难以久持')
    if gua_name in LIU_HE_GUA:
        magnitude = abs(WEIGHTS['gua_liu_he'])
        return _factor('gua', '+', magnitude,
                       '{gua}为六合卦，主成'.format(gua=gua_name),
                       '事有和合之象，宜促成不宜拖延')
    return None


# ---------------------------------------------------------------------------
# 用神定位
# ---------------------------------------------------------------------------
def locate_yong_shen(pan, relative_name):
    """定位用神。

    卦中现出者优先。多爻现出时依传统：取**发动**之爻；若皆不动，取**临世**
    者；再取临应者；仍不明则取位次最低者（初爻）。
    """
    hits = [y for y in pan['yaos'] if y['relative'] == relative_name]
    if hits:
        moving = [y for y in hits if y['moving']]
        if len(moving) == 1:
            chosen = moving[0]
        else:
            pool = moving or hits
            on_shi = [y for y in pool if y['is_shi']]
            on_ying = [y for y in pool if y['is_ying']]
            chosen = (on_shi or on_ying or sorted(pool, key=lambda y: y['position']))[0]
        return {
            'source': 'yao',
            'relative': relative_name,
            'all_positions': [y['position'] for y in hits],
            'position': chosen['position'],
            'zhi': chosen['zhi'],
            'element': chosen['element'],
            'na_jia': chosen['na_jia'],
            'moving': chosen['moving'],
            'is_kong': chosen['is_kong'],
            'is_shi': chosen['is_shi'],
            'is_ying': chosen['is_ying'],
            'bian': chosen['bian'],
            'multiple': len(hits) > 1,
            'yao': chosen,
        }

    fu = [f for f in pan['fu_shen'] if f['relative'] == relative_name]
    if fu:
        f = fu[0]
        return {
            'source': 'fu_shen',
            'relative': relative_name,
            'all_positions': [f['position']],
            'position': f['position'],
            'zhi': f['zhi'],
            'element': f['element'],
            'na_jia': f['na_jia'],
            'moving': False,
            'is_kong': f['zhi'] in pan['kong_wang'],
            'is_shi': False,
            'is_ying': False,
            'bian': None,
            'multiple': len(fu) > 1,
            'fu': f,
        }
    return None


def _locate_shi(pan):
    for y in pan['yaos']:
        if y['is_shi']:
            return y
    return None


def _shen_for_element(palace_element, element):
    """某五行在本宫之中对应哪一个六亲"""
    return relative(palace_element, element)


# ---------------------------------------------------------------------------
# 主分析
# ---------------------------------------------------------------------------
def analyze(pan, topic='general', gender='男'):
    """对已排好的卦盘做用神选取与旺衰分析。

    参数
    ----
    pan    : `paipan_at()` 的返回（必须含 month_branch / day_branch）
    topic  : 所问之事的类别，见 TOPIC_YONGSHEN
    gender : 感情类用神依性别取（男占妻财、女占官鬼）

    返回
    ----
    含 factors（带理由的因子清单）、score、level、用神/原神/忌神/仇神定位、
    以及由因子推导的 summary / advice / keywords。
    """
    if topic not in TOPIC_YONGSHEN:
        raise ValueError('未知的问事类别: {0}'.format(topic))
    if 'month_branch' not in pan:
        raise ValueError('卦盘缺少 month_branch，请改用 paipan_at() 排盘')

    month_zhi = pan['month_branch']
    day_zhi = pan['day_branch']
    palace_element = pan['ben']['palace_element']

    # ── 定用神 ───────────────────────────────────────────────────────
    relative_name = TOPIC_YONGSHEN[topic]
    if topic == 'relationship':
        relative_name = '妻财' if gender == '男' else '官鬼'

    yong = None
    if relative_name == '世爻':
        shi = _locate_shi(pan)
        if shi is not None:
            yong = {
                'source': 'yao',
                'relative': shi['relative'],
                'all_positions': [shi['position']],
                'position': shi['position'],
                'zhi': shi['zhi'],
                'element': shi['element'],
                'na_jia': shi['na_jia'],
                'moving': shi['moving'],
                'is_kong': shi['is_kong'],
                'is_shi': True,
                'is_ying': False,
                'bian': shi['bian'],
                'multiple': False,
                'yao': shi,
            }
    else:
        yong = locate_yong_shen(pan, relative_name)

    if yong is None:
        # 理论上不会发生：六亲必有一爻或缺而伏藏；此处兜底
        return {
            'topic': topic,
            'topic_label': TOPIC_LABELS.get(topic, topic),
            'yong_shen': None,
            'factors': [],
            'flags': ['用神未寻得'],
            'score': BASE_SCORE,
            'level': '平',
            'summary': '未能定出用神，请检查卦盘数据。',
            'advice': [],
            'keywords': [],
        }

    # ── 逐条规则 ─────────────────────────────────────────────────────
    factors = []
    flags = []

    factors.append(month_factor(yong['zhi'], yong['element'], month_zhi))
    factors.append(day_factor(yong['zhi'], yong['element'], day_zhi, yong['moving']))

    kf = kong_factor(yong['zhi'], yong['is_kong'], month_zhi, day_zhi, yong['moving'])
    if kf:
        factors.append(kf)
        if kf['weight'] < 0:
            flags.append('旬空')

    if yong['source'] == 'fu_shen':
        flags.append('用神伏藏')
        factors.extend(fu_factor(yong['fu'], month_zhi, day_zhi))

    if yong['moving']:
        factors.append(_factor('yong', '+', WEIGHTS['yong_moving'],
                               '用神{zhi}发动，事有变动'.format(zhi=yong['zhi']),
                               '事态正在变化，宜随时而应'))
        jt = jin_tui_factor(yong['zhi'], yong['bian']['zhi']) if yong['bian'] else None
        if jt:
            factors.append(jt)
        if yong['bian']:
            b_el = yong['bian']['element']
            if GENERATION[b_el] == yong['element']:
                factors.append(_factor('bian', '+', WEIGHTS['bian_back_generate'],
                                       '变爻{b}回头生用神，愈变愈强'.format(b=yong['bian']['na_jia']),
                                       '转机向好，变中得利'))
            elif RESTRICTION[b_el] == yong['element']:
                factors.append(_factor('bian', '-', WEIGHTS['bian_back_restrict'],
                                       '变爻{b}回头克用神，变而生忧'.format(b=yong['bian']['na_jia']),
                                       '变化反倒伤及根本，宜守旧'))

    # 他爻发动对用神的影响（他爻自身的回头生克计入其强弱，此处只看它对用神的作用）
    for yao in pan['yaos']:
        if yao['position'] == yong['position']:
            continue
        if not yao['moving']:
            continue
        if GENERATION[yao['element']] == yong['element']:
            factors.append(_factor('other_moving', '+', WEIGHTS['other_moving_generate'],
                                   '第 {n} 爻{gz}发动生用神'.format(n=yao['position'], gz=yao['na_jia']),
                                   '有外力相助，可借他方之力'))
        elif RESTRICTION[yao['element']] == yong['element']:
            factors.append(_factor('other_moving', '-', WEIGHTS['other_moving_attack'],
                                   '第 {n} 爻{gz}发动克用神'.format(n=yao['position'], gz=yao['na_jia']),
                                   '有外力相阻，须防他人干扰'))
        if yao['bian']:
            b_el = yao['bian']['element']
            if GENERATION[b_el] == yong['element']:
                factors.append(_factor('other_bian', '+', WEIGHTS['other_bian_generate'],
                                       '第 {n} 爻变出{b}生用神'.format(n=yao['position'], b=yao['bian']['na_jia'])))
            elif RESTRICTION[b_el] == yong['element']:
                factors.append(_factor('other_bian', '-', WEIGHTS['other_bian_attack'],
                                       '第 {n} 爻变出{b}克用神'.format(n=yao['position'], b=yao['bian']['na_jia'])))

    gf = gua_factor(pan['ben']['name'], topic)
    if gf:
        factors.append(gf)
        flags.append('六冲卦' if pan['ben']['name'] in LIU_CHONG_GUA else '六合卦')

    if yong['is_shi']:
        factors.append(_factor('shi', '+', WEIGHTS['yong_on_shi'],
                               '用神即世爻，事在己身'.format(),
                               '此事的主动权的确在自己手上'))

    # ── 汇总 ─────────────────────────────────────────────────────────
    score = max(0, min(100, BASE_SCORE + sum(f['weight'] for f in factors)))
    level = next(label for threshold, label in LEVELS if score >= threshold)

    # 原神／忌神／仇神
    yuan_el = next(el for el, gen in GENERATION.items() if gen == yong['element'])
    ji_el = next(el for el, res in RESTRICTION.items() if res == yong['element'])
    chou_el = next(el for el, res in RESTRICTION.items() if res == yuan_el)

    shen = {}
    for label, el in (('原神', yuan_el), ('忌神', ji_el), ('仇神', chou_el)):
        rel = _shen_for_element(palace_element, el)
        found = locate_yong_shen(pan, rel)
        shen[label] = {
            'element': el,
            'relative': rel,
            'present': found is not None,
            'source': found['source'] if found else None,
            'positions': found['all_positions'] if found else [],
        }

    shi_yao = _locate_shi(pan)
    analysis = {
        'topic': topic,
        'topic_label': TOPIC_LABELS.get(topic, topic),
        'gender': gender if topic == 'relationship' else None,
        'yong_shen': {
            'relative': yong['relative'],
            'source': yong['source'],
            'position': yong['position'],
            'all_positions': yong['all_positions'],
            'na_jia': yong['na_jia'],
            'zhi': yong['zhi'],
            'element': yong['element'],
            'moving': yong['moving'],
            'is_kong': yong['is_kong'],
            'is_shi': yong['is_shi'],
            'is_ying': yong['is_ying'],
            'multiple': yong['multiple'],
        },
        'yuan_shen': shen['原神'],
        'ji_shen': shen['忌神'],
        'chou_shen': shen['仇神'],
        'shi_yao': {
            'position': shi_yao['position'],
            'na_jia': shi_yao['na_jia'],
            'relative': shi_yao['relative'],
            'element': shi_yao['element'],
            'moving': shi_yao['moving'],
            'is_kong': shi_yao['is_kong'],
        } if shi_yao else None,
        'month_branch': month_zhi,
        'day_branch': day_zhi,
        'factors': factors,
        'flags': flags,
        'score': score,
        'level': level,
    }
    analysis.update(compose_text(analysis))
    return analysis


# ---------------------------------------------------------------------------
# 模板文案
# ---------------------------------------------------------------------------
LEVEL_OPENING = {
    '大吉': '用神得势，诸缘相助，此事可成。',
    '吉': '用神有力，事有可为。',
    '平吉': '用神尚可，吉凶参半而偏于顺。',
    '平': '用神平平，事无大起大落。',
    '凶': '用神受制，此事多阻。',
    '大凶': '用神衰弱受克，此事难成。',
}

KIND_KEYWORDS = {
    'month': '月令',
    'day': '日辰',
    'kong': '旬空',
    'fu': '伏藏',
    'yong': '主动',
    'bian': '变爻',
    'jin': '进神',
    'tui': '退神',
    'other_moving': '他爻',
    'other_bian': '他变',
    'gua': '卦体',
    'shi': '在己',
}


def compose_text(analysis):
    """由因子清单推导文案。

    只使用真实触发的因子，不添加任何未在 factors 中出现的判断——
    这样文案与依据永远一致，不会出现"凭空断语"。
    """
    factors = analysis['factors']
    level = analysis['level']
    yong = analysis['yong_shen']

    strong = sorted(
        [f for f in factors if f['weight'] != 0],
        key=lambda f: abs(f['weight']),
        reverse=True,
    )

    opening = LEVEL_OPENING.get(level, '')

    # 摘要：开头一句 + 权重最大的两条依据
    top = [f for f in strong[:2]]
    parts = [opening]
    if top:
        parts.append('　'.join(f['text'] + '。' for f in top))
    summary = ''.join(parts)

    # 建议：取触发因子里自带建议的，按权重排序，去重，最多四条
    advice = []
    seen = set()
    for f in strong:
        if f['advice'] and f['advice'] not in seen:
            advice.append(f['advice'])
            seen.add(f['advice'])
        if len(advice) >= 4:
            break
    if len(advice) < 2:
        advice.append('卦象只提示倾向，重大决策仍须自己判断。')

    # 关键词：用神 + 状态 + 触发的因子类别
    keywords = [yong['relative'], level]
    for f in strong:
        kw = KIND_KEYWORDS.get(f['kind'])
        if kw and kw not in keywords:
            keywords.append(kw)
        if len(keywords) >= 6:
            break

    return {
        'summary': summary,
        'advice': advice,
        'keywords': keywords,
    }
