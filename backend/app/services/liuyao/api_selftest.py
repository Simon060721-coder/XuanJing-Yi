# -*- coding: utf-8 -*-
"""六爻接口层自检

用 Flask 自带的测试客户端打真实路由，而不是直接调函数——这样蓝图注册、
前缀、参数校验、JSON 序列化都在测试范围内。

数据库使用项目自带的 `TestingConfig`（内存 SQLite），因此**不写任何磁盘文件**，
在受限环境下也能运行。

附加一项统计检验：三枚铜钱应是三次独立投掷（二项分布 B(3, 1/2)），
即 0/3 背各约 1/8、1/2 背各约 3/8。这检验的是"铜钱模型"本身对不对，
而不只是"代码没报错"。
"""

from datetime import datetime, timezone

from .casting import toss_coins, BACK
from .judgment import BASE_SCORE

API = '/api/v1'


def run(check, check_true, note):
    try:
        from app import create_app
        from app.config import TestingConfig
    except ImportError as exc:                     # pragma: no cover
        note('接口层自检已跳过（无法导入 Flask 应用：{0}）'.format(exc))
        return

    app = create_app(TestingConfig)
    client = app.test_client()

    def post(url, payload=None):
        return client.post(url, json=payload if payload is not None else {})

    # ── 0. 既有接口未受影响 ─────────────────────────────────────────
    check('既有 /health 仍正常', client.get(API + '/health').status_code, 200)
    check('既有 /hexagrams 仍正常', client.get(API + '/hexagrams').status_code, 200)
    check('六爻蓝图已注册',
          client.get(API + '/liuyao/hexagrams').status_code, 200)

    # ── 1. 六十四卦清单 ─────────────────────────────────────────────
    resp = client.get(API + '/liuyao/hexagrams')
    body = resp.get_json()
    check('卦清单 status', body.get('status'), 'success')
    check('卦清单总数', body['data']['total'], 64)
    table = {h['name']: h for h in body['data']['hexagrams']}
    check('卦清单含乾为天', '乾为天' in table, True)
    check('乾为天所属宫', table['乾为天']['palace'], '乾')
    check('乾为天宫五行', table['乾为天']['palace_element'], '金')
    check('乾为天世应', (table['乾为天']['shi'], table['乾为天']['ying']), (6, 3))
    check('乾为天卦符', table['乾为天']['symbols'], '☰☰')
    check('卦清单含八宫', body['data']['palaces'],
          ['乾', '坎', '艮', '震', '巽', '离', '坤', '兑'])

    # ── 2. 摇一爻 ───────────────────────────────────────────────────
    resp = post(API + '/liuyao/toss')
    check('摇爻 HTTP', resp.status_code, 200)
    yao = resp.get_json()['data']
    check('摇爻返回三枚铜钱', len(yao['coins']), 3)
    check_true('摇爻铜钱只有背/字',
               all(c in ('背', '字') for c in yao['coins']),
               '实际 {0}'.format(yao['coins']))
    check_true('摇爻爻值在 6–9', yao['value'] in (6, 7, 8, 9),
               '实际 {0}'.format(yao['value']))
    check('摇爻背数与铜钱一致', yao['backs'], yao['coins'].count(BACK))
    check('摇爻默认位置为初爻', yao['position'], 1)
    check('摇爻初爻名称', yao['position_name'], '初')
    check_true('摇爻阴阳与爻值自洽',
               (yao['value'] % 2 == 1) == (yao['yin_yang'] == '阳'))
    check_true('摇爻动爻与爻值自洽',
               yao['moving'] == (yao['value'] in (6, 9)))

    yao6 = post(API + '/liuyao/toss', {'position': 6}).get_json()['data']
    check('摇爻第六爻名称', yao6['position_name'], '上')
    check('摇爻第六爻位置', yao6['position'], 6)

    # 参数校验
    for bad in (0, 7, -1, 'x', None):
        check('position={0!r} 应被拒'.format(bad),
              post(API + '/liuyao/toss', {'position': bad}).status_code, 400)

    # ── 3. 一次摇满六爻 ─────────────────────────────────────────────
    body = post(API + '/liuyao/toss-six').get_json()
    six = body['data']['yaos']
    check('摇六爻数量', len(six), 6)
    check('摇六爻爻值数量', len(body['data']['yao_values']), 6)
    check('摇六爻位置序列', [y['position'] for y in six], [1, 2, 3, 4, 5, 6])
    check('摇六爻名称序列', [y['position_name'] for y in six],
          ['初', '二', '三', '四', '五', '上'])
    check_true('摇六爻爻值均合法',
               all(y['value'] in (6, 7, 8, 9) for y in six),
               '实际 {0}'.format([y['value'] for y in six]))
    check('摇六爻回显爻值一致',
          body['data']['yao_values'], [y['value'] for y in six])

    # ── 4. 装卦 ─────────────────────────────────────────────────────
    resp = post(API + '/liuyao/paipan',
                {'yao_values': [7, 7, 7, 7, 7, 7],
                 'moment': '2000-01-01T12:00:00',
                 'question': '近期事业如何'})
    check('装卦 HTTP', resp.status_code, 200)
    pan = resp.get_json()['data']
    check('装卦本卦', pan['ben']['name'], '乾为天')
    check('装卦静卦标记', pan['is_jing'], True)
    check('装卦四柱年', pan['si_zhu']['year']['gan_zhi'], '己卯')
    check('装卦四柱月', pan['si_zhu']['month']['gan_zhi'], '丙子')
    check('装卦四柱日', pan['si_zhu']['day']['gan_zhi'], '戊午')
    check('装卦四柱时', pan['si_zhu']['hour']['gan_zhi'], '戊午')
    check('装卦月建', pan['month_branch'], '子')
    check('装卦日建', pan['day_branch'], '午')
    check('装卦旬空', pan['kong_wang'], ['子', '丑'])
    check('装卦六爻数', len(pan['yaos']), 6)
    check('装卦首爻六神', pan['yaos'][0]['god'], '勾陈')
    check('装卦伏神（乾为天六亲齐全）', pan['fu_shen'], [])
    check('装卦回显问题', pan['question'], '近期事业如何')
    check('装卦回显爻值', pan['yao_values'], [7, 7, 7, 7, 7, 7])
    check_true('装卦返回的 moment 可解析',
               datetime.fromisoformat(pan['moment']) is not None)

    # 动卦 + 伏神
    pan2 = post(API + '/liuyao/paipan',
                {'yao_values': [9, 7, 7, 7, 7, 7],
                 'moment': '2000-01-01T12:00:00'}).get_json()['data']
    check('装卦动卦变卦', pan2['bian']['name'], '天风姤')
    check('装卦动爻位置', pan2['moving_lines'], [1])
    check('装卦动爻带变爻', pan2['yaos'][0]['bian'] is not None, True)

    pan3 = post(API + '/liuyao/paipan',
                {'yao_values': [8, 7, 7, 7, 7, 7],
                 'moment': '2000-01-01T12:00:00'}).get_json()['data']
    check('装卦天风姤', pan3['ben']['name'], '天风姤')
    check('装卦天风姤伏神数量', len(pan3['fu_shen']), 1)
    check('装卦天风姤伏神六亲', pan3['fu_shen'][0]['relative'], '妻财')
    check('装卦天风姤伏神纳甲', pan3['fu_shen'][0]['na_jia'], '甲寅')

    # 参数校验
    for bad_payload in (
        {},
        {'yao_values': [7, 7, 7]},
        {'yao_values': [7, 7, 7, 7, 7, 7, 7]},
        {'yao_values': [5, 7, 7, 7, 7, 7]},
        {'yao_values': [0, 7, 7, 7, 7, 7]},
        {'yao_values': ['a', 'b', 'c', 'd', 'e', 'f']},
        {'yao_values': '123456'},
        {'yao_values': [7, 7, 7, 7, 7, 7], 'moment': '不是时间'},
    ):
        check('装卦非法输入应被拒: {0}'.format(str(bad_payload)[:44]),
              post(API + '/liuyao/paipan', bad_payload).status_code, 400)

    # 带时区的时刻：换算成本地时间后结果应与朴素本地时间一致
    aware_resp = post(API + '/liuyao/paipan',
                      {'yao_values': [7] * 6, 'moment': '2000-01-01T04:00:00Z'})
    check('装卦接受带时区的时刻', aware_resp.status_code, 200)
    local_dt = (datetime(2000, 1, 1, 4, 0, tzinfo=timezone.utc)
                .astimezone().replace(tzinfo=None))
    naive_resp = post(API + '/liuyao/paipan',
                      {'yao_values': [7] * 6, 'moment': local_dt.isoformat()})
    check('时区换算与朴素本地时间一致',
          aware_resp.get_json()['data']['si_zhu']['day']['gan_zhi'],
          naive_resp.get_json()['data']['si_zhu']['day']['gan_zhi'])

    # ── 5. 四柱接口 ─────────────────────────────────────────────────
    resp = client.get(API + '/liuyao/sizhu?moment=2000-01-01T12:00:00')
    check('四柱 HTTP', resp.status_code, 200)
    sz = resp.get_json()['data']
    check('四柱年', sz['year']['gan_zhi'], '己卯')
    check('四柱月', sz['month']['gan_zhi'], '丙子')
    check('四柱日', sz['day']['gan_zhi'], '戊午')
    check('四柱旬空', sz['kong_wang'], ['子', '丑'])
    check('四柱月建', sz['month_branch'], '子')
    check('四柱非法时刻应被拒',
          client.get(API + '/liuyao/sizhu?moment=乱码').status_code, 400)

    # ── 6. 节气接口 ─────────────────────────────────────────────────
    resp = client.get(API + '/liuyao/solar-terms?year=2025')
    check('节气 HTTP', resp.status_code, 200)
    terms = resp.get_json()['data']['terms']
    check('节气数量', len(terms), 24)
    check('节气按时间排序', [t['moment'] for t in terms],
          sorted(t['moment'] for t in terms))
    check('节气非法年份应被拒',
          client.get(API + '/liuyao/solar-terms?year=1800').status_code, 400)
    check('节气非数字年份应被拒',
          client.get(API + '/liuyao/solar-terms?year=abc').status_code, 400)

    # ── 7. 铜钱模型的统计检验 ───────────────────────────────────────
    # 三枚铜钱各自独立，应为二项分布 B(3, 1/2)：
    # 背数 0/1/2/3 的概率分别约 1/8、3/8、3/8、1/8
    rounds = 4000
    counts = [0, 0, 0, 0]
    for _ in range(rounds):
        counts[toss_coins()['backs']] += 1
    observed = [c / float(rounds) for c in counts]
    expected = [0.125, 0.375, 0.375, 0.125]
    note('铜钱分布实测（{0} 次）：0背 {1:.3f}　1背 {2:.3f}　2背 {3:.3f}　3背 {4:.3f}'.format(
        rounds, observed[0], observed[1], observed[2], observed[3]))
    note('理论值（B(3,1/2)）：0背 0.125　1背 0.375　2背 0.375　3背 0.125')
    for backs in range(4):
        check_true('背数 {0} 的频率接近理论值'.format(backs),
                   abs(observed[backs] - expected[backs]) < 0.03,
                   '实测 {0:.3f}，理论 {1:.3f}'.format(
                       observed[backs], expected[backs]))
    check_true('四种爻值均出现过',
               all(c > 0 for c in counts), '实际计数 {0}'.format(counts))

    # ── 8. 用神选取与旺衰分析 ───────────────────────────────────────
    resp = client.get(API + '/liuyao/topics')
    check('问事类别 HTTP', resp.status_code, 200)
    topics = {t['key']: t for t in resp.get_json()['data']['topics']}
    check('问事类别数量', len(topics), 10)
    check('事业类用神为官鬼', topics['career']['yong_shen'], '官鬼')
    check('财运类用神为妻财', topics['wealth']['yong_shen'], '妻财')
    check('感情类用神依性别', topics['relationship']['yong_shen'],
          '依性别取（男占妻财、女占官鬼）')

    base = {'yao_values': [7, 7, 7, 7, 7, 7], 'moment': '2000-01-01T12:00:00'}
    body = post(API + '/liuyao/paipan', dict(base, topic='career')).get_json()['data']
    check('装卦结果含 analysis', 'analysis' in body, True)
    a = body['analysis']
    check('分析问事类别', a['topic'], 'career')
    check('分析问事标签', a['topic_label'], '事业功名')
    check('事业用神为官鬼', a['yong_shen']['relative'], '官鬼')
    check('事业用神纳甲', a['yong_shen']['na_jia'], '壬午')
    check_true('分析含因子清单', len(a['factors']) > 0)
    check_true('每条因子都有说明文字', all(f['text'] for f in a['factors']))
    check_true('每条因子的符号与权重一致',
               all((f['sign'] == '+' and f['weight'] >= 0)
                   or (f['sign'] == '-' and f['weight'] <= 0)
                   or (f['sign'] == '0' and f['weight'] == 0)
                   for f in a['factors']))
    check('分数等于基础分加因子权重之和', a['score'],
          max(0, min(100, BASE_SCORE + sum(f['weight'] for f in a['factors']))))
    check_true('摘要非空', bool(a['summary']))
    check_true('建议 1–4 条', 1 <= len(a['advice']) <= 4)
    check_true('关键词非空', len(a['keywords']) > 0)
    check('回显 topic', body['topic'], 'career')
    check('回显 gender', body['gender'], '男')

    # 换问事类别只需重算分析，不必重新起卦
    a_wealth = post(API + '/liuyao/paipan',
                    dict(base, topic='wealth')).get_json()['data']['analysis']
    check('换类别后用神变为妻财', a_wealth['yong_shen']['relative'], '妻财')
    check_true('换类别后分数随之改变', a_wealth['score'] != a['score'])

    # 感情类依性别取用神
    a_male = post(API + '/liuyao/paipan',
                  dict(base, topic='relationship', gender='男')).get_json()['data']['analysis']
    a_female = post(API + '/liuyao/paipan',
                    dict(base, topic='relationship', gender='女')).get_json()['data']['analysis']
    check('男占感情用妻财', a_male['yong_shen']['relative'], '妻财')
    check('女占感情用官鬼', a_female['yong_shen']['relative'], '官鬼')
    check('非感情类不记录性别',
          a['gender'], None)

    # 默认与校验
    check('不传 topic 默认 general',
          post(API + '/liuyao/paipan', base).get_json()['data']['analysis']['topic'],
          'general')
    check('未知问事类别应被拒',
          post(API + '/liuyao/paipan', dict(base, topic='不存在')).status_code, 400)
    check('非法性别应被拒',
          post(API + '/liuyao/paipan', dict(base, gender='其他')).status_code, 400)

    # 用神伏藏的情形（天风姤缺妻财）
    fu_body = post(API + '/liuyao/paipan',
                   {'yao_values': [8, 7, 7, 7, 7, 7],
                    'moment': '2000-01-01T12:00:00',
                    'topic': 'wealth'}).get_json()['data']['analysis']
    check('伏藏用神来源', fu_body['yong_shen']['source'], 'fu_shen')
    check('伏藏用神纳甲', fu_body['yong_shen']['na_jia'], '甲寅')
    check_true('标记用神伏藏', '用神伏藏' in fu_body['flags'])
    note('接口示例（乾为天·问事业）：' + a['summary'])

    # ── 梅花易数接口 ────────────────────────────────────────────────
    # 这里有条**回归测试**：前端发的是带时区的 ISO 串（toISOString() 以 Z 结尾），
    # 曾经把它直接交给按 naive 当地时间处理的引擎，于是抛
    # 「can't compare offset-naive and offset-aware datetimes」。
    # 此前的验证用手写的**无时区**串，恰好绕过了这个 bug —— 所以必须测 Z 串。
    # 教训：接口层要按前端真实发出的形状去测，不能按自己方便的写法测。
    resp = post(API + '/divination/query',
                {'query_type': '梅花易数', 'input_method': '时间',
                 'timestamp': '2026-06-27T14:30:00.000Z'})
    check('时间起卦（带 Z 的 ISO 串）HTTP', resp.status_code, 200)
    hx = resp.get_json()['data']['hexagram_layer']
    check('时间起卦返回六爻画卦数据', len(hx['yaos']), 6)
    check('上卦为干净的独立字段', sorted(hx['upper'].keys()),
          ['direction', 'element', 'name', 'symbol'])
    check_true('六爻自初爻起且阴阳/动爻齐备',
               all({'is_yang', 'moving', 'changed_is_yang'} <= set(y) for y in hx['yaos']))

    # 无时区的朴素串同样要能工作（两种形状都得吃）
    resp = post(API + '/divination/query',
                {'query_type': '梅花易数', 'input_method': '时间',
                 'timestamp': '2000-01-01T12:00:00'})
    check('时间起卦（无时区串）HTTP', resp.status_code, 200)
    check('无时区串 2000-01-01 12:00 得水风井',
          resp.get_json()['data']['hexagram_layer']['primary_hexagram'], '水风井（☵☴）')

    # 数字起卦已知答案：26/6/27 → 火天大有，动爻五
    d = post(API + '/divination/query',
             {'query_type': '梅花易数', 'input_method': '数字',
              'num1': 26, 'num2': 6, 'num3': 27}).get_json()['data']
    check('数字起卦主卦', d['hexagram_layer']['primary_hexagram'], '火天大有（☲☰）')
    check('数字起卦动爻', d['hexagram_layer']['changing_lines'], [5])
    check('数字起卦回传起卦所用之数', d['calculation']['num1'], 26)
    check_true('多维评分已移除', 'aspects_layer' not in d)
    check_true('体用元素齐备',
               set(d['hexagram_layer']['elements']) == {'体', '用'},
               '实际 {0}'.format(d['hexagram_layer']['elements']))

    # ── 清空历史（只在测试库上做，绝不碰开发库）────────────────────
    # 上面几次起卦已写入若干记录（TestingConfig 用内存 SQLite，不落盘）
    before = client.get(API + '/divination/history').get_json()['data']
    check_true('清空前确有记录', before['total'] >= 1,
               '实际 {0} 条'.format(before['total']))

    resp = client.delete(API + '/divination/history')
    check('清空历史 HTTP', resp.status_code, 200)
    check('清空返回实际删除条数', resp.get_json()['data']['deleted'], before['total'])
    check('清空后总数为 0',
          client.get(API + '/divination/history').get_json()['data']['total'], 0)

    # 清空是幂等的：再清一次不报错，且删除 0 条
    resp = client.delete(API + '/divination/history')
    check('重复清空仍成功', resp.status_code, 200)
    check('重复清空删除 0 条', resp.get_json()['data']['deleted'], 0)

    # 单条删除的路径不能被清空路由抢走（方法同为 DELETE，路由不能串）
    fresh = post(API + '/divination/query',
                 {'query_type': '梅花易数', 'input_method': '数字',
                  'num1': 26, 'num2': 6, 'num3': 27}).get_json()['data']
    one_id = fresh['record_id']
    check('重新起卦后又有 1 条',
          client.get(API + '/divination/history').get_json()['data']['total'], 1)
    check('按 id 删除单条 HTTP',
          client.delete(API + '/divination/history/{0}'.format(one_id)).status_code, 200)
    check('按 id 删除只删那一条',
          client.get(API + '/divination/history').get_json()['data']['total'], 0)
