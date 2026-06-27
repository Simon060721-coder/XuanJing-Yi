"""占卜相关路由"""
from flask import request, jsonify
from datetime import datetime
from app.routes import divination_bp
from app.services.divination_engine import DivinationEngine
from app.services.mapping_service import MappingService
from app.models.hexagram import DivinationQuery
from app import db

engine = DivinationEngine()
mapping_service = MappingService()

@divination_bp.route('/divination/query', methods=['POST'])
def query_divination():
    """占卜查询API"""
    try:
        data = request.get_json()

        # 验证输入
        query_type = data.get('query_type', '梅花易数')
        input_method = data.get('input_method')

        if not input_method:
            return jsonify({'error': '输入方法不能为Null'}), 400

        # 根据输入方法起卦
        if input_method == '时间':
            timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
            hexagram_data = engine.query_by_timestamp(timestamp)
        elif input_method == '数字':
            num1 = int(data.get('num1', 0))
            num2 = int(data.get('num2', 0))
            num3 = int(data.get('num3', 0))
            hexagram_data = engine.query_by_numbers(num1, num2, num3)
        else:
            return jsonify({'error': '不支持的输入方法'}), 400

        # 提取卦象信息
        primary_hex = hexagram_data['primary_hexagram']
        secondary_hex = hexagram_data['secondary_hexagram']
        changing_lines = hexagram_data['changing_lines']

        # 获取卦象编号并分析五行
        primary_hex_num = next(
            (num for num, value in engine.HEXAGRAMS.items() if value['name'] == primary_hex['name']),
            None
        )
        secondary_hex_num = next(
            (num for num, value in engine.HEXAGRAMS.items() if value['name'] == secondary_hex['name']),
            None
        )
        if primary_hex_num is None or secondary_hex_num is None:
            return jsonify({'error': '无法识别卦象编号'}), 500

        element_analysis = engine.analyze_elements([primary_hex_num, secondary_hex_num])

        # 计算吉凶评分
        fortune_analysis = engine.calculate_fortune_score(
            primary_hex_num,
            secondary_hex_num,
            element_analysis['balance_score'],
            changing_lines[0]
        )

        # 获取卦象体用解读（64组全覆盖）
        hexagram_meaning = mapping_service.get_hexagram_meaning(primary_hex['name'], secondary_hex['name'])

        # 获取所有维度的分析结果（5维度全覆盖）
        all_aspects = mapping_service.get_all_aspects(primary_hex['name'], secondary_hex['name'])

        # 获取吉凶中文名
        fortune_label = mapping_service.get_fortune_label(hexagram_meaning.get('fortune', 'moderate'))

        # 构建完整响应
        result = {
            'status': 'success',
            'data': {
                'hexagram_layer': {
                    'primary_hexagram': f"{primary_hex['name']}（{primary_hex['symbol']}）",
                    'secondary_hexagram': f"{secondary_hex['name']}（{secondary_hex['symbol']}）",
                    'changing_lines': changing_lines,
                    'elements': element_analysis['elements']
                },
                'analysis_layer': {
                    'fortune_score': fortune_analysis['fortune_score'],
                    'fortune_level': fortune_analysis['fortune_level'],
                    'fortune_label': fortune_label,
                    'element_balance': element_analysis['balance_level'],
                    'balance_score': element_analysis['balance_score']
                },
                'advice_layer': {
                    'main_interpretation': hexagram_meaning['meaning'],
                    'fortune_type': hexagram_meaning.get('fortune', 'moderate'),
                    'fortune_label': fortune_label,
                    'keywords': hexagram_meaning.get('keywords', [])
                },
                'aspects_layer': all_aspects
            },
            'timestamp': datetime.utcnow().isoformat()
        }

        # 保存查询记录（可选）
        record = DivinationQuery(
            query_type=query_type,
            input_method=input_method,
            input_value=str(data),
            primary_hexagram=primary_hex['name'],
            secondary_hexagram=secondary_hex['name'],
            changing_lines=str(changing_lines),
            fortune_score=fortune_analysis['fortune_score'],
            fortune_level=fortune_analysis['fortune_level'],
            analysis_result=result['data'],
            query_timestamp=datetime.utcnow()
        )
        db.session.add(record)
        db.session.commit()

        return jsonify(result), 200

    except Exception as e:
        # 打印完整异常堆栈到控制台，便于调试
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@divination_bp.route('/hexagrams', methods=['GET'])
def get_hexagrams():
    """获取所有卦象列表"""
    hexagrams = []
    for num, hex_info in DivinationEngine.HEXAGRAMS.items():
        hexagrams.append({
            'number': num,
            'name': hex_info['name'],
            'symbol': hex_info['symbol'],
            'element': hex_info['element'],
            'direction': hex_info['direction']
        })
    return jsonify({'status': 'success', 'data': hexagrams}), 200

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
