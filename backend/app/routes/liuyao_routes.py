# -*- coding: utf-8 -*-
"""六爻（纳甲筮法）路由

设计要点
--------
1. **无状态**：摇卦不依赖服务端会话。前端连调 6 次 `/liuyao/toss` 收集六爻，
   再一次性提交 `/liuyao/paipan` 装卦。这样无需会话管理，也不会出现并发错配。
2. **随机由服务端产生**：每次 `/toss` 的结果由服务端决定，前端只负责把动画
   演到这个结果上。避免「先有动画再随机」——那样结果可被前端预测。
3. **时间语义**：`moment` 视为**当地时间**（用户所在时区的墙上时间），四柱按
   此刻推算。真太阳时校正属后续增强，目前不做。
4. **暂不落库**：解读规则引擎（用神旺衰）尚未完成，现在写库只会存下半截记录
   （有卦无断），留下需要回填的历史数据。待解读层完成后统一落库。
"""

import traceback
from datetime import datetime

from flask import request, jsonify

from app.routes import liuyao_bp
from app.services.liuyao import (
    HEXAGRAMS, PALACE_ORDER, YAO_POSITION_NAMES, YAO_LABELS, YAO_NAMES,
    TOPIC_YONGSHEN, TOPIC_LABELS,
    toss_coins, toss_six, paipan_at, si_zhu, kong_wang, analyze,
    solar_term_datetime, solar_terms_of_year,
)
from app.services.liuyao.constants import TRIGRAMS

# 合法爻值直接取自爻名单一来源，避免两处各写一份而失同步
_VALID_YAO_VALUES = tuple(sorted(YAO_NAMES))


def _parse_moment(raw):
    """把请求中的时刻解析为「naive 当地时间」。

    兼容三种输入：
    - 缺省 / 空 → 服务器当前时间
    - 朴素 ISO 串（如 2026-10-08T14:52）→ 直接采用为当地时间
    - 带时区的 ISO 串（如 ...Z 或 +08:00）→ 转成本地时间后去掉时区
    """
    if raw in (None, ''):
        return datetime.now()

    if isinstance(raw, datetime):
        dt = raw
    else:
        text = str(raw).strip()
        if text.endswith(('Z', 'z')):
            text = text[:-1] + '+00:00'
        dt = datetime.fromisoformat(text)

    if dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)
    return dt


def _ok(data):
    return jsonify({
        'status': 'success',
        'data': data,
        'timestamp': datetime.utcnow().isoformat(),
    }), 200


def _fail(message, code):
    return jsonify({'error': message}), code


def _tag_position(yao, index):
    """给一爻补上爻位信息（1 = 初爻）"""
    yao['position'] = index + 1
    yao['position_name'] = YAO_POSITION_NAMES[index]
    return yao


# ---------------------------------------------------------------------------
# 摇卦
# ---------------------------------------------------------------------------
@liuyao_bp.route('/liuyao/toss', methods=['POST'])
def liuyao_toss():
    """摇一爻：投掷三枚铜钱，返回正反与所得爻。

    请求体（可选）：{"position": 1}   position 为 1–6，用于标注是第几爻。
    """
    try:
        data = request.get_json(silent=True) or {}
        raw_position = data.get('position', 1)
        try:
            position = int(raw_position)
        except (TypeError, ValueError):
            return _fail('position 必须是 1–6 的整数', 400)
        if not 1 <= position <= 6:
            return _fail('position 必须在 1–6 之间', 400)

        return _ok(_tag_position(toss_coins(), position - 1))
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


@liuyao_bp.route('/liuyao/toss-six', methods=['POST'])
def liuyao_toss_six():
    """一次摇满六爻（自初爻至上爻）。

    供「跳过动画」的快速模式使用：前端不必连调 6 次。
    """
    try:
        yaos = [_tag_position(y, i) for i, y in enumerate(toss_six())]
        return _ok({
            'yaos': yaos,
            'yao_values': [y['value'] for y in yaos],
        })
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


# ---------------------------------------------------------------------------
# 装卦
# ---------------------------------------------------------------------------
@liuyao_bp.route('/liuyao/paipan', methods=['POST'])
def liuyao_paipan():
    """由六爻结果装卦，返回完整卦盘。

    请求体：
        yao_values : [6,7,8,9] × 6，自初爻至上爻（必填）
        moment     : 起卦时刻（可选，默认当前时间）
        question   : 心中所问（可选，仅回显）
        topic      : 问事类别（可选，默认 general），决定用神
        gender     : 男/女（可选，仅感情类用神依此取）
    """
    try:
        data = request.get_json(silent=True) or {}

        values = data.get('yao_values')
        if not isinstance(values, (list, tuple)) or len(values) != 6:
            return _fail('yao_values 必须是长度 6 的数组（自初爻至上爻）', 400)
        try:
            values = [int(v) for v in values]
        except (TypeError, ValueError):
            return _fail('yao_values 只能包含整数 6/7/8/9', 400)
        bad = [v for v in values if v not in _VALID_YAO_VALUES]
        if bad:
            return _fail('爻值必须是 6/7/8/9，收到 {0}'.format(bad), 400)

        try:
            moment = _parse_moment(data.get('moment'))
        except ValueError:
            return _fail('moment 不是合法的 ISO 时间字符串', 400)

        topic = data.get('topic') or 'general'
        if topic not in TOPIC_YONGSHEN:
            return _fail('未知的问事类别: {0}'.format(topic), 400)
        gender = data.get('gender') or '男'
        if gender not in ('男', '女'):
            return _fail('gender 只能是 男 或 女', 400)

        pan = paipan_at(values, moment, late_zi_next_day=bool(
            data.get('late_zi_next_day', True)))

        # 用神选取与旺衰分析。topic 变了只需重算这一步，不必重新起卦。
        pan['analysis'] = analyze(pan, topic, gender)

        # datetime 不能直接 JSON 序列化
        pan['moment'] = moment.isoformat()
        pan['si_zhu']['effective_day'] = pan['si_zhu']['effective_day'].isoformat()
        pan['yao_values'] = values
        pan['question'] = (data.get('question') or '').strip()[:200]
        pan['topic'] = topic
        pan['gender'] = gender

        return _ok(pan)
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


# ---------------------------------------------------------------------------
# 问事类别（界面据此选用神）
# ---------------------------------------------------------------------------
@liuyao_bp.route('/liuyao/topics', methods=['GET'])
def liuyao_topics():
    """问事类别清单。每一类对应一个用神，'relationship' 依性别取用神。"""
    try:
        items = []
        for key, label in TOPIC_LABELS.items():
            yong = TOPIC_YONGSHEN.get(key)
            items.append({
                'key': key,
                'label': label,
                'yong_shen': yong or '依性别取（男占妻财、女占官鬼）',
            })
        return _ok({'topics': items, 'total': len(items)})
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


# ---------------------------------------------------------------------------
# 四柱（起卦前预览用）
# ---------------------------------------------------------------------------
@liuyao_bp.route('/liuyao/sizhu', methods=['GET', 'POST'])
def liuyao_sizhu():
    """取某时刻的四柱、月建、日建、旬空。

    供界面在起卦前显示「当前：某年某月某日某时」，也便于排查时间问题。
    """
    try:
        late_zi = True
        if request.method == 'POST':
            data = request.get_json(silent=True) or {}
            raw = data.get('moment')
            late_zi = bool(data.get('late_zi_next_day', True))
        else:
            raw = request.args.get('moment')

        try:
            moment = _parse_moment(raw)
        except ValueError:
            return _fail('moment 不是合法的 ISO 时间字符串', 400)

        sz = si_zhu(moment, late_zi_next_day=late_zi)
        sz['effective_day'] = sz['effective_day'].isoformat()
        sz['moment'] = moment.isoformat()
        sz['kong_wang'] = list(kong_wang(sz['day']['gan'], sz['day']['zhi']))

        return _ok(sz)
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


# ---------------------------------------------------------------------------
# 参考资料
# ---------------------------------------------------------------------------
@liuyao_bp.route('/liuyao/hexagrams', methods=['GET'])
def liuyao_hexagrams():
    """六十四卦清单（按八宫卦序），含宫、世应、上下卦与卦符。"""
    try:
        items = []
        for name, h in HEXAGRAMS.items():
            items.append({
                'name': name,
                'symbols': h['symbols'],
                'upper': h['upper'],
                'lower': h['lower'],
                'palace': h['palace'],
                'palace_element': h['palace_element'],
                'stage': h['stage'],
                'shi': h['shi'],
                'ying': h['ying'],
            })
        return _ok({
            'hexagrams': items,
            'palaces': list(PALACE_ORDER),
            'yao_labels': YAO_LABELS,
            'total': len(items),
        })
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


@liuyao_bp.route('/liuyao/trigrams', methods=['GET'])
def liuyao_trigrams():
    """八卦表（含三爻阴阳位）。

    给前端的「卦象成形」用：初二三爻定内卦、四五六爻定外卦，每摇一爻即可
    即时反馈。**前端据此把三爻的阴阳位映射成卦名**，不必在前端另抄一份八卦表；
    bits 自下而上，(1,1,0) 即兑。
    """
    try:
        return _ok({
            'trigrams': [
                {
                    'name': name,
                    'symbol': t['symbol'],
                    'bits': list(t['bits']),
                    'element': t['element'],
                    'nature': t['nature'],
                }
                for name, t in TRIGRAMS.items()
            ],
        })
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)


@liuyao_bp.route('/liuyao/solar-terms', methods=['GET'])
def liuyao_solar_terms():
    """某年二十四节气时刻（北京时间），用于说明月建换月时点。

    Query: year（默认今年）
    """
    try:
        raw_year = request.args.get('year', datetime.now().year)
        try:
            year = int(raw_year)
        except (TypeError, ValueError):
            return _fail('year 必须是整数', 400)
        if not 1900 <= year <= 2100:
            return _fail('year 需在 1900–2100 之间', 400)

        terms = [{'name': name, 'moment': dt.isoformat()}
                 for name, dt in solar_terms_of_year(year)]

        return _ok({
            'year': year,
            'terms': terms,
            'lichun': solar_term_datetime(year, '立春').isoformat(),
        })
    except Exception as exc:                       # pragma: no cover
        traceback.print_exc()
        return _fail(str(exc), 500)
