"""占卜相关路由"""
from flask import request, jsonify
from datetime import datetime
from app.routes import divination_bp
from app.services.divination_engine import DivinationEngine
from app.services.mapping_service import MappingService, element_relation
from app.models.hexagram import DivinationQuery
from app import db

engine = DivinationEngine()
mapping_service = MappingService()

@divination_bp.route('/divination/query', methods=['POST'])
def query_divination():
    """占卜查询API（梅花易数）

    返回的是**真正的六十四卦**（主卦／变卦），而不是两个独立的八卦。
    体卦、用卦按动爻所在卦判定。
    """
    try:
        data = request.get_json() or {}

        # 验证输入
        query_type = data.get('query_type', '梅花易数')
        input_method = data.get('input_method')

        if not input_method:
            return jsonify({'error': '输入方法不能为Null'}), 400

        # 根据输入方法起卦
        if input_method == '时间':
            try:
                raw = data.get('timestamp') or datetime.now().isoformat()
                text = str(raw).strip()
                if text.endswith(('Z', 'z')):
                    text = text[:-1] + '+00:00'
                timestamp = datetime.fromisoformat(text)
                # 前端发的是**带时区**的 ISO 串（`toISOString()` 以 Z 结尾），
                # 而引擎按 naive 当地时间推四柱。必须先转成本地时间再去掉时区，
                # 否则会在干支换算里抛「can't compare offset-naive and offset-aware」。
                # 这与六爻路由 _parse_moment 的约定一致。
                if timestamp.tzinfo is not None:
                    timestamp = timestamp.astimezone().replace(tzinfo=None)
            except ValueError:
                return jsonify({'error': 'timestamp 不是合法的 ISO 时间'}), 400
            cast = engine.query_by_timestamp(timestamp)
        elif input_method == '数字':
            try:
                num1 = int(data.get('num1', 0))
                num2 = int(data.get('num2', 0))
                num3 = int(data.get('num3', 0))
            except (TypeError, ValueError):
                return jsonify({'error': '数字起卦需要三个整数'}), 400
            if not all(1 <= n <= 99 for n in (num1, num2, num3)):
                return jsonify({'error': '三个数字均需在 1-99 之间'}), 400
            cast = engine.query_by_numbers(num1, num2, num3)
        else:
            return jsonify({'error': '不支持的输入方法'}), 400

        primary = cast['primary_hexagram']
        changed = cast['changed_hexagram']
        changing_line = cast['changing_line']
        body = cast['body']
        use = cast['use']

        # 体用五行关系——**吉凶评分与解读文案共用同一来源**，故两者不会矛盾
        relation = element_relation(body, use)
        fortune = engine.calculate_fortune_score(relation, changing_line, body, use)

        # 解读文案以（体, 用）为键；多维评分（aspects）已弃用——那五个数是同一
        # 基准分加固定偏移，维度差异与卦象、所问皆无关，故不再计算也不返回
        hexagram_meaning = mapping_service.get_hexagram_meaning(body, use)
        fortune_label = mapping_service.get_fortune_label(
            hexagram_meaning.get('fortune', 'moderate'))

        result = {
            'status': 'success',
            'data': {
                'hexagram_layer': {
                    'primary_hexagram': '{0}（{1}）'.format(primary['name'], primary['symbols']),
                    'secondary_hexagram': '{0}（{1}）'.format(changed['name'], changed['symbols']),
                    'changing_lines': [changing_line],
                    # 六爻（自初爻起），画卦直接用；upper/lower 为干净的上下卦信息
                    'yaos': cast['yaos'],
                    'upper': {
                        'name': cast['upper']['name'],
                        'symbol': cast['upper']['symbol'],
                        'element': cast['upper']['element'],
                        'direction': cast['upper']['direction'],
                    },
                    'lower': {
                        'name': cast['lower']['name'],
                        'symbol': cast['lower']['symbol'],
                        'element': cast['lower']['element'],
                        'direction': cast['lower']['direction'],
                    },
                    'upper_hexagram': '{0}（{1}）'.format(
                        cast['upper']['name'], cast['upper']['symbol']),
                    'lower_hexagram': '{0}（{1}）'.format(
                        cast['lower']['name'], cast['lower']['symbol']),
                    'body_hexagram': body,
                    'use_hexagram': use,
                    'elements': {
                        '体': engine.TRIGRAM_INFO[body]['element'],
                        '用': engine.TRIGRAM_INFO[use]['element'],
                    },
                },
                'analysis_layer': {
                    'fortune_score': fortune['fortune_score'],
                    'fortune_level': fortune['fortune_level'],
                    'fortune_label': fortune_label,
                    'element_balance': engine.RELATION_LABELS[relation],
                    'relation': relation,
                },
                'advice_layer': {
                    'main_interpretation': hexagram_meaning['meaning'],
                    'fortune_type': hexagram_meaning.get('fortune', 'moderate'),
                    'fortune_label': fortune_label,
                    'keywords': hexagram_meaning.get('keywords', []),
                },
                # 起卦所用的数（时间起卦为年/月/日/时数，数字起卦为三数），
                # 前端"取数"动效据此逐项展示，不必再算一遍
                'calculation': cast['calculation'],
            },
            'timestamp': datetime.utcnow().isoformat(),
        }

        # 保存查询记录
        record = DivinationQuery(
            query_type=query_type,
            input_method=input_method,
            input_value=str(data),
            primary_hexagram=primary['name'],
            secondary_hexagram=changed['name'],
            changing_lines=str([changing_line]),
            fortune_score=fortune['fortune_score'],
            fortune_level=fortune['fortune_level'],
            analysis_result=result['data'],
            query_timestamp=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()

        result['data']['record_id'] = record.id
        return jsonify(result), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@divination_bp.route('/hexagrams', methods=['GET'])
def get_hexagrams():
    """获取六十四卦列表（含所属宫、世应、上下卦）。

    旧实现返回的是八个**八卦**，与端点名不符；现返回真正的六十四卦，
    八卦信息另置于 `trigrams` 字段。
    """
    from app.services.liuyao.hexagrams import HEXAGRAMS as LIUYAO_HEXAGRAMS

    hexagrams = [{
        'name': h['name'],
        'symbols': h['symbols'],
        'upper': h['upper'],
        'lower': h['lower'],
        'palace': h['palace'],
        'palace_element': h['palace_element'],
        'stage': h['stage'],
        'shi': h['shi'],
        'ying': h['ying'],
    } for h in LIUYAO_HEXAGRAMS.values()]

    trigrams = [{
        'number': num,
        'name': info['name'],
        'symbol': info['symbol'],
        'element': info['element'],
        'direction': info['direction'],
    } for num, info in sorted(DivinationEngine.HEXAGRAMS.items())]

    return jsonify({
        'status': 'success',
        'data': hexagrams,
        'trigrams': trigrams,
        'total': len(hexagrams),
    }), 200

@divination_bp.route('/health', methods=['GET'])
def health_check():
    """数报检查"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200

@divination_bp.route('/divination/history', methods=['GET'])
def get_divination_history():
    """获取占卜历史记录

    Query Params:
        limit: 返回记录数量（默认 20，最大 100）
        offset: 偏移量（默认 0）
        user_id: 可选的用户标识

    Returns:
        历史记录列表（按时间倒序）+ 总数
    """
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
        offset = int(request.args.get('offset', 0))
        user_id = request.args.get('user_id')

        query = DivinationQuery.query
        if user_id:
            query = query.filter(DivinationQuery.user_id == user_id)

        total = query.count()
        records = query.order_by(DivinationQuery.query_timestamp.desc()) \
                       .offset(offset) \
                       .limit(limit) \
                       .all()

        items = []
        for r in records:
            data = r.analysis_result or {}
            hexagram_layer = data.get('hexagram_layer', {})
            advice_layer = data.get('advice_layer', {})

            items.append({
                'id': r.id,
                'query_type': r.query_type,
                'input_method': r.input_method,
                'input_value': r.input_value,
                'primary_hexagram': r.primary_hexagram,
                'secondary_hexagram': r.secondary_hexagram,
                'changing_lines': r.changing_lines,
                'fortune_score': r.fortune_score,
                'fortune_level': r.fortune_level,
                'fortune_label': advice_layer.get('fortune_label'),
                'main_interpretation': advice_layer.get('main_interpretation'),
                'keywords': advice_layer.get('keywords', []),
                'primary_display': hexagram_layer.get('primary_hexagram'),
                'secondary_display': hexagram_layer.get('secondary_hexagram'),
                'query_timestamp': r.query_timestamp.isoformat() if r.query_timestamp else None,
            })

        return jsonify({
            'status': 'success',
            'data': {
                'items': items,
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': offset + len(items) < total,
            }
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@divination_bp.route('/divination/history/<int:record_id>', methods=['GET'])
def get_divination_detail(record_id):
    """获取单条占卜记录的完整解读详情"""
    try:
        record = DivinationQuery.query.get(record_id)
        if not record:
            return jsonify({'error': '记录不存在'}), 404

        return jsonify({
            'status': 'success',
            'data': {
                'id': record.id,
                'query_type': record.query_type,
                'input_method': record.input_method,
                'input_value': record.input_value,
                'primary_hexagram': record.primary_hexagram,
                'secondary_hexagram': record.secondary_hexagram,
                'changing_lines': record.changing_lines,
                'fortune_score': record.fortune_score,
                'fortune_level': record.fortune_level,
                'analysis_result': record.analysis_result,
                'query_timestamp': record.query_timestamp.isoformat() if record.query_timestamp else None,
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@divination_bp.route('/divination/history/<int:record_id>', methods=['DELETE'])
def delete_divination_record(record_id):
    """删除单条占卜记录"""
    try:
        record = DivinationQuery.query.get(record_id)
        if not record:
            return jsonify({'error': '记录不存在'}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({'status': 'success', 'message': '记录已删除'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@divination_bp.route('/divination/history', methods=['DELETE'])
def clear_divination_history():
    """清空**全部**占卜记录（历史页的「清空历史」）。

    与单条删除同一个资源路径，靠 HTTP 方法 + 有无 id 区分：
    DELETE /divination/history        → 清空全部
    DELETE /divination/history/<id>   → 删一条

    返回实际删除条数，供前端核对与提示。分页只影响展示，不影响删除范围。
    """
    try:
        deleted = DivinationQuery.query.delete()
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': '历史已清空',
            'data': {'deleted': deleted},
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
