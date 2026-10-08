# -*- coding: utf-8 -*-
"""装卦：由六爻结果排出完整卦盘

包含：本卦、变卦、纳甲（天干地支）、六亲、六神、世应、旬空、动爻。

关键规则说明
------------
1. **六亲以本卦之宫的五行为「我」**。变爻的六亲同样以本卦宫为准，
   而不是变卦的宫（此为《增删卜易》一系主流做法）。
2. **变卦的纳甲**取变卦自身的上下卦，但六亲仍按本卦宫定。
3. **旬空**由日干支所在旬推出。
4. **六神**按日干起于初爻，依次顺排。
"""

from .constants import (
    TRIGRAMS, ZHI_ORDER, ZHI_ELEMENT, GAN_ORDER, NAJIA,
    SIX_GODS, SIX_GODS_START, SIX_RELATIVES, GENERATION, RESTRICTION,
    MOVING_VALUES, YAO_NAMES, YAO_POSITION_NAMES,
)
from .hexagrams import by_lines, HEXAGRAMS
from .ganzhi import si_zhu

_SHENG = GENERATION          # 我生
_KE = RESTRICTION            # 我克


def relative(me, other):
    """以「我」的五行定六亲。

    me / other 均为五行（金木水火土）。
    """
    if me == other:
        return '兄弟'
    if GENERATION[other] == me:
        return '父母'        # 生我者
    if GENERATION[me] == other:
        return '子孙'        # 我生者
    if RESTRICTION[me] == other:
        return '妻财'        # 我克者
    return '官鬼'            # 克我者（五行中剩余的唯一关系）


def kong_wang(day_gan, day_zhi):
    """旬空：由日干支所在旬推出空亡的两个地支。"""
    if day_gan not in GAN_ORDER:
        raise ValueError('无效日干: {0}'.format(day_gan))
    if day_zhi not in ZHI_ORDER:
        raise ValueError('无效日支: {0}'.format(day_zhi))

    gan_index = GAN_ORDER.index(day_gan)
    zhi_index = ZHI_ORDER.index(day_zhi)
    # 旬首地支：日支回退「日干在一旬内的序号」位
    xun_head = (zhi_index - gan_index) % 12
    return (ZHI_ORDER[(xun_head - 2) % 12], ZHI_ORDER[(xun_head - 1) % 12])


def six_gods(day_gan):
    """六神：按日干决定初爻所起之神，自初爻至上爻顺排。"""
    if day_gan not in SIX_GODS_START:
        raise ValueError('无效日干: {0}'.format(day_gan))
    start = SIX_GODS_START[day_gan]
    return [SIX_GODS[(start + i) % 6] for i in range(6)]


def _najia_for_line(hexagram, index):
    """取某卦第 index 爻（0 = 初爻）的纳甲（天干, 地支）。

    下卦（初二三）用内卦纳甲，上卦（四五六）用外卦纳甲。
    """
    if index < 3:
        trigram = hexagram['lower']
        gan, zhis, _, _ = NAJIA[trigram]
        return gan, zhis[index]
    trigram = hexagram['upper']
    _, _, gan, zhis = NAJIA[trigram]
    return gan, zhis[index - 3]


def _yao_relatives(hexagram, me_element):
    """某卦六爻的（天干, 地支, 五行, 六亲），六亲以 me_element 为「我」"""
    rows = []
    for i in range(6):
        gan, zhi = _najia_for_line(hexagram, i)
        element = ZHI_ELEMENT[zhi]
        rows.append((gan, zhi, element, relative(me_element, element)))
    return rows


def fu_shen(hexagram):
    """伏神：本卦若缺某个六亲，则从**本宫纯卦**取该六亲之爻为伏神。

    规则：用神不上卦时，到本宫首卦（八纯卦）中去找该六亲，那一爻即为伏神；
    伏神所伏的、本卦同位之爻称为飞神。伏神与飞神的生克是断卦的重要依据。

    卦中六亲齐全时返回空列表（无伏神）。

    经典例子：天风姤（乾宫）六亲只有父母、子孙、兄弟、官鬼，**缺妻财**，
    于是从乾为天取二爻甲寅木为伏神，伏于本卦二爻辛亥水（飞神）之下。
    """
    me = hexagram['palace_element']
    present = set(row[3] for row in _yao_relatives(hexagram, me))
    missing = [r for r in SIX_RELATIVES if r not in present]
    if not missing:
        return []

    pure_name = '{0}为{1}'.format(hexagram['palace'],
                                 TRIGRAMS[hexagram['palace']]['nature'])
    pure = HEXAGRAMS[pure_name]
    pure_rows = _yao_relatives(pure, me)
    fei_rows = _yao_relatives(hexagram, me)

    result = []
    for target in missing:
        for index, (gan, zhi, element, rel) in enumerate(pure_rows):
            if rel != target:
                continue
            f_gan, f_zhi, f_element, f_rel = fei_rows[index]
            result.append({
                'relative': target,
                'position': index + 1,
                'position_name': YAO_POSITION_NAMES[index],
                'gan': gan, 'zhi': zhi, 'element': element,
                'na_jia': gan + zhi,
                'fei_shen': {
                    'na_jia': f_gan + f_zhi,
                    'zhi': f_zhi,
                    'element': f_element,
                    'relative': f_rel,
                },
            })
            break
    return result


def paipan(yao_values, day_gan, day_zhi):
    """排出完整卦盘。

    参数
    ----
    yao_values : 长度 6 的序列，值为 6/7/8/9，顺序为初爻 → 上爻
    day_gan    : 日干，如 '甲'
    day_zhi    : 日支，如 '子'
    """
    values = list(yao_values)
    if len(values) != 6:
        raise ValueError('需要 6 个爻值，收到 {0} 个'.format(len(values)))
    for v in values:
        if v not in YAO_NAMES:
            raise ValueError('爻值必须是 6/7/8/9，收到 {0}'.format(v))

    # 本卦六爻阴阳：7、9 为阳
    ben_lines = tuple(1 if v in (7, 9) else 0 for v in values)
    moving_indexes = [i for i, v in enumerate(values) if v in MOVING_VALUES]

    # 变卦：动爻阴阳翻转
    bian_lines = list(ben_lines)
    for i in moving_indexes:
        bian_lines[i] ^= 1
    bian_lines = tuple(bian_lines)

    ben = by_lines(ben_lines)
    bian = by_lines(bian_lines)
    palace_element = ben['palace_element']

    gods = six_gods(day_gan)
    kong = kong_wang(day_gan, day_zhi)

    yaos = []
    for i in range(6):
        value = values[i]
        gan, zhi = _najia_for_line(ben, i)
        element = ZHI_ELEMENT[zhi]

        yao = {
            'position': i + 1,
            'position_name': YAO_POSITION_NAMES[i],
            'value': value,
            'name': YAO_NAMES[value],
            'is_yang': value % 2 == 1,
            'moving': value in MOVING_VALUES,
            'gan': gan,
            'zhi': zhi,
            'element': element,
            'relative': relative(palace_element, element),
            'god': gods[i],
            'is_shi': (i + 1) == ben['shi'],
            'is_ying': (i + 1) == ben['ying'],
            'is_kong': zhi in kong,
            'na_jia': '{0}{1}'.format(gan, zhi),
        }

        # 变爻：变卦同位置的纳甲
        if i in moving_indexes:
            bgan, bzhi = _najia_for_line(bian, i)
            belement = ZHI_ELEMENT[bzhi]
            yao['bian'] = {
                'gan': bgan,
                'zhi': bzhi,
                'element': belement,
                'na_jia': '{0}{1}'.format(bgan, bzhi),
                # 变爻六亲仍以本卦宫为我
                'relative': relative(palace_element, belement),
            }
        else:
            yao['bian'] = None

        yaos.append(yao)

    return {
        'ben': _hexagram_brief(ben),
        'bian': _hexagram_brief(bian),
        'is_jing': len(moving_indexes) == 0,      # 静卦（无动爻）
        'moving_lines': [i + 1 for i in moving_indexes],
        'yaos': yaos,
        'day': {'gan': day_gan, 'zhi': day_zhi, 'gan_zhi': day_gan + day_zhi},
        'kong_wang': list(kong),
        'fu_shen': fu_shen(ben),            # 本卦伏神（六亲不全时才有）
        'bian_fu_shen': fu_shen(bian),      # 变卦伏神
    }


def _hexagram_brief(hexagram):
    """卦的摘要信息（不含逐爻）"""
    return {
        'name': hexagram['name'],
        'upper': hexagram['upper'],
        'lower': hexagram['lower'],
        'symbols': hexagram['symbols'],
        'palace': hexagram['palace'],
        'palace_element': hexagram['palace_element'],
        'stage': hexagram['stage'],
        'shi': hexagram['shi'],
        'ying': hexagram['ying'],
    }


def yao_title(position, is_yang):
    """爻题：初九、九二、九三、九四、九五、上九（阴爻作六）。

    格式不可想当然：**初爻与上爻把「初／上」放前面**（初九、上六），
    **中间四爻把「九／六」放前面**（九二、六五）。
    """
    num = '九' if is_yang else '六'
    if position == 1:
        return '初' + num
    if position == 6:
        return '上' + num
    return num + YAO_POSITION_NAMES[position - 1]


def paipan_at(yao_values, moment, late_zi_next_day=True):
    """按起卦时刻排盘：自动排四柱，取月建、日建入卦。

    这是给上层（接口层）用的入口——六爻的吉凶判断离不开月建与日建，
    所以排盘必须绑定起卦时刻，而不是任取一个日干支。

    参数
    ----
    yao_values : 长度 6 的爻值序列（6/7/8/9），初爻在前
    moment     : 起卦时刻（北京时间 datetime）
    """
    sz = si_zhu(moment, late_zi_next_day=late_zi_next_day)
    pan = paipan(yao_values, sz['day']['gan'], sz['day']['zhi'])
    pan['si_zhu'] = sz
    pan['month_branch'] = sz['month_branch']      # 月建
    pan['day_branch'] = sz['day_branch']          # 日建
    pan['moment'] = moment
    return pan


def render(pan):
    """把卦盘渲染成便于在终端阅读的多行文本（用于自检与调试）。"""
    ben, bian = pan['ben'], pan['bian']
    out = []
    if pan.get('si_zhu'):
        sz = pan['si_zhu']
        out.append('四柱：{0}年　{1}月　{2}日　{3}时'.format(
            sz['year']['gan_zhi'], sz['month']['gan_zhi'],
            sz['day']['gan_zhi'], sz['hour']['gan_zhi']))
        out.append('月建：{0}　日建：{1}　旬空：{2}{3}'.format(
            pan['month_branch'], pan['day_branch'],
            pan['kong_wang'][0], pan['kong_wang'][1]))
    else:
        out.append('日建：{0}　　旬空：{1}{2}'.format(
            pan['day']['gan_zhi'], pan['kong_wang'][0], pan['kong_wang'][1]))
    out.append('本卦：{0}（{1}宫{2}，{3}，{4}）　世{5}应{6}'.format(
        ben['name'], ben['palace'], ben['stage'], ben['symbols'],
        ben['palace_element'], ben['shi'], ben['ying']))
    if pan.get('fu_shen'):
        out.append('伏神：' + '；'.join(
            '{0}{1}（伏于第 {2} 爻，飞神 {3}{4}）'.format(
                f['na_jia'], f['relative'], f['position'],
                f['fei_shen']['na_jia'], f['fei_shen']['relative'])
            for f in pan['fu_shen']))
    else:
        out.append('伏神：无（六亲齐全）')
    if pan['is_jing']:
        out.append('变卦：无（静卦，六爻不动）')
    else:
        out.append('变卦：{0}（{1}宫{2}，{3}，{4}）　动爻：{5}'.format(
            bian['name'], bian['palace'], bian['stage'], bian['symbols'],
            bian['palace_element'],
            '、'.join('{0}爻'.format(n) for n in pan['moving_lines'])))
    out.append('')
    out.append('六神　爻题　六亲　纳甲　五行　世应　卦画　　动　（变卦）')
    for yao in reversed(pan['yaos']):                  # 自上而下显示
        marks = [m for m, ok in (('世', yao['is_shi']), ('应', yao['is_ying']),
                                 ('空', yao['is_kong'])) if ok]
        hex_line = '▬▬▬' if yao['is_yang'] else '▬ ▬'
        flag = '○动' if yao['value'] == 9 else ('×动' if yao['value'] == 6 else '')

        bian_txt = ''
        if yao['bian']:
            b = yao['bian']
            if GENERATION[b['element']] == yao['element']:
                note = '（回头生）'
            elif RESTRICTION[b['element']] == yao['element']:
                note = '（回头克）'
            else:
                note = ''
            bian_txt = '→ {0} {1} {2}{3}'.format(
                b['na_jia'], b['relative'], b['element'], note)

        out.append('{0}　{1}　{2}　{3}　{4}　{5}　{6}　{7}　{8}'.format(
            yao['god'], yao_title(yao['position'], yao['is_yang']),
            yao['relative'], yao['na_jia'], yao['element'],
            ''.join(marks) or '　', hex_line, flag, bian_txt))
    return '\n'.join(out)
