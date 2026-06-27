"""映射矩阵服务 - 卦象组合解读与多维度分析"""
from typing import Dict, Tuple
from itertools import product


# 八经卦基本信息
TRIGRAMS = ['乾', '坤', '震', '巽', '兑', '坎', '艮', '离']

# 五行属性
ELEMENTS = {
    '乾': '金', '兑': '金',
    '震': '木', '巽': '木',
    '坎': '水',
    '离': '火',
    '坤': '土', '艮': '土',
}

# 五行生克
ELEMENT_GENERATION = {'金': '水', '水': '木', '木': '火', '火': '土', '土': '金'}
ELEMENT_RESTRICTION = {'金': '木', '木': '土', '土': '水', '水': '火', '火': '金'}


def _element_relation(p: str, s: str) -> str:
    """判断两卦的五行关系"""
    if p == s:
        return 'same'
    pe, se = ELEMENTS[p], ELEMENTS[s]
    if ELEMENT_GENERATION[pe] == se:
        return 'generate'  # 体生用，耗泄
    if ELEMENT_GENERATION[se] == pe:
        return 'support'  # 用生体，得助
    if ELEMENT_RESTRICTION[pe] == se:
        return 'restrict'  # 体克用，费力
    if ELEMENT_RESTRICTION[se] == pe:
        return 'attack'  # 用克体，受克
    return 'neutral'


def _build_meaning(p: str, s: str) -> Dict:
    """根据主卦和变卦构建解读"""
    relation = _element_relation(p, s)
    same = (p == s)

    if same:
        if p == '乾':
            meaning = '乾为纯阳之卦，刚健中正。时运亨通，事业可成，唯需防过刚易折，谦逊待人方能持久。'
            fortune, keywords = 'very_good', ['阳刚', '奋进', '主导']
        elif p == '坤':
            meaning = '坤为纯阴之卦，柔顺包容。以宽厚承载万物，厚德载物，宜静守待时，不宜急进。'
            fortune, keywords = 'good', ['柔顺', '包容', '守成']
        else:
            meaning = f'{p}卦自化{p}卦，本卦本气独发，{ELEMENTS[p]}气纯粹专一。事态专一而稳定，宜守不宜攻。'
            fortune, keywords = 'moderate', ['专一', '守成', '稳定']
    else:
        meaning_map = {
            'support': f'{p}化{s}，用生体，得外界之助力，{ELEMENTS[s]}来滋{ELEMENTS[p]}。运势上扬，宜主动进取，借势而上。',
            'generate': f'{p}化{s}，体生用，自家能量外泄，{ELEMENTS[p]}去生{ELEMENTS[s]}。虽有所耗，但利于奉献与教化之事。',
            'restrict': f'{p}化{s}，体克用，需费力克制{ELEMENTS[s]}之事。辛苦有成，可得实权，但需防操劳过度。',
            'attack': f'{p}化{s}，用克体，受{ELEMENTS[s]}之克。运势受压，宜守不宜攻，谨慎规避风险。',
            'neutral': f'{p}化{s}，{ELEMENTS[p]}与{ELEMENTS[s]}比和。平稳过渡，无大起大落，宜按部就班推进。',
        }
        fortune_map = {
            'support': 'good',
            'restrict': 'good',
            'neutral': 'moderate',
            'generate': 'balanced',
            'attack': 'challenging',
        }
        keyword_map = {
            'support': ['得助', '顺势', '进取'],
            'restrict': ['掌控', '费力', '务实'],
            'neutral': ['平稳', '守正', '渐进'],
            'generate': ['付出', '奉献', '教化'],
            'attack': ['受压', '慎行', '守成'],
        }
        meaning = meaning_map[relation]
        fortune = fortune_map[relation]
        keywords = keyword_map[relation]

    return {
        'meaning': meaning,
        'fortune': fortune,
        'keywords': keywords,
    }


def _build_aspect(p: str, s: str, aspect: str) -> Dict:
    """构建单个维度的解读"""
    relation = _element_relation(p, s)
    same = (p == s)

    # 基础分
    if same:
        base = 70
    else:
        base_map = {'support': 82, 'restrict': 70, 'neutral': 65, 'generate': 58, 'attack': 42}
        base = base_map[relation]

    # 维度调整
    aspect_modifier = {
        'career': {'乾': 8, '震': 6, '离': 5, '巽': 2, '兑': 0, '坎': -3, '艮': -1, '坤': -2},
        'wealth': {'乾': 8, '兑': 6, '离': 4, '巽': 3, '震': 0, '坎': -2, '坤': 1, '艮': 0},
        'relationship': {'兑': 8, '巽': 5, '离': 4, '坤': 3, '艮': 0, '震': -1, '乾': -2, '坎': -4},
        'health': {'乾': 5, '震': 4, '巽': 3, '坤': 2, '兑': 0, '艮': 0, '离': -2, '坎': -5},
        'study': {'乾': 6, '巽': 5, '离': 4, '震': 3, '兑': 1, '坤': 0, '艮': -1, '坎': -3},
    }

    score = base + aspect_modifier[aspect].get(p, 0)
    # 变卦影响
    if not same:
        score += aspect_modifier[aspect].get(s, 0) // 2
    score = max(20, min(95, score))

    # 趋势
    if score >= 80:
        trend = '↑'
    elif score <= 45:
        trend = '↓'
    else:
        trend = '→'

    # 建议
    aspect_templates = {
        'career': {
            'high': '事业运势上扬，宜把握机会主动出击，争取更高平台与重要项目。',
            'mid': '事业稳中有进，按既定规划扎实推进，注重积累人脉与专业能力。',
            'low': '事业阻力较大，宜守不宜攻，专注打磨内功，等待时机转换。',
        },
        'wealth': {
            'high': '财运亨通，正财偏财皆有利，但需量力而行，避免过度投资。',
            'mid': '财运平稳，宜稳健理财，开源节流，积少成多。',
            'low': '财运偏弱，不宜投机冒险，宜保守储蓄，待运势回稳。',
        },
        'relationship': {
            'high': '感情运势极佳，单身者有望遇良缘，情侣感情升温，宜主动表达。',
            'mid': '感情平稳，需多沟通理解，用心经营方能长久。',
            'low': '感情易生波折，宜冷静处理，避免冲动言行，给彼此空间。',
        },
        'health': {
            'high': '身心状态良好，精力充沛，适合开展运动与调养计划。',
            'mid': '健康尚可，注意作息规律，避免过度劳累，适度放松。',
            'low': '健康需多加关注，宜早睡早起，调节饮食，必要时及时就医。',
        },
        'study': {
            'high': '学业运势佳，理解力与记忆力俱佳，宜攻克难点与重要考试。',
            'mid': '学业平稳，需保持专注，循序渐进，不可急躁冒进。',
            'low': '学业受困，宜调整学习方法，寻找良师指点，切忌死记硬背。',
        },
    }
    bucket = 'high' if score >= 75 else ('mid' if score >= 55 else 'low')
    advice = aspect_templates[aspect][bucket]

    return {
        'score': score,
        'trend': trend,
        'advice': advice,
    }


class MappingService:
    """映射矩阵服务类"""

    ASPECT_TYPES = ['career', 'wealth', 'relationship', 'health', 'study']

    FORTUNE_LABELS = {
        'very_good': '大吉',
        'good': '吉',
        'balanced': '平吉',
        'moderate': '平',
        'challenging': '凶',
        'bad': '大凶',
    }

    # 预生成 8x8 = 64 组卦象解读
    HEXAGRAM_MEANINGS: Dict[Tuple[str, str], Dict] = {
        (p, s): _build_meaning(p, s)
        for p, s in product(TRIGRAMS, TRIGRAMS)
    }

    # 预生成 5 维度 × 64 组分析
    ASPECT_MAPPING: Dict[str, Dict[Tuple[str, str], Dict]] = {
        aspect: {
            (p, s): _build_aspect(p, s, aspect)
            for p, s in product(TRIGRAMS, TRIGRAMS)
        }
        for aspect in ASPECT_TYPES
    }

    def get_hexagram_meaning(self, primary_hex: str, secondary_hex: str) -> Dict:
        """获取卦象的体用解读

        Args:
            primary_hex: 主卦名称
            secondary_hex: 变卦名称

        Returns:
            解读字典，包含 meaning / fortune / keywords
        """
        key = (primary_hex, secondary_hex)
        if key in self.HEXAGRAM_MEANINGS:
            return self.HEXAGRAM_MEANINGS[key]
        return {
            'meaning': f'{primary_hex}转{secondary_hex}，需结合具体情境细细参详。',
            'fortune': 'moderate',
            'keywords': ['观察', '思考', '求稳'],
        }

    def get_aspect_analysis(self, aspect_type: str, primary_hex: str, secondary_hex: str) -> Dict:
        """获取特定维度的映射分析（保留旧接口）

        Args:
            aspect_type: 维度类型
            primary_hex: 主卦名称
            secondary_hex: 变卦名称

        Returns:
            单维度分析结果
        """
        if aspect_type not in self.ASPECT_MAPPING:
            return {'score': 60, 'trend': '→', 'advice': '此维度暂未覆盖，建议综合参考整体解读。'}

        key = (primary_hex, secondary_hex)
        aspect_map = self.ASPECT_MAPPING[aspect_type]
        if key in aspect_map:
            return aspect_map[key]
        return {'score': 60, 'trend': '→', 'advice': f'{aspect_type}方面建议继续观察。'}

    def get_all_aspects(self, primary_hex: str, secondary_hex: str) -> Dict:
        """一次性获取全部维度的分析结果

        Args:
            primary_hex: 主卦名称
            secondary_hex: 变卦名称

        Returns:
            {维度: {score, trend, advice}} 字典
        """
        result = {}
        for aspect in self.ASPECT_TYPES:
            result[aspect] = self.get_aspect_analysis(aspect, primary_hex, secondary_hex)
        return result

    def get_fortune_label(self, fortune_type: str) -> str:
        """根据吉凶类型返回中文标签

        Args:
            fortune_type: 吉凶类型（very_good/good/balanced/moderate/challenging/bad）

        Returns:
            中文标签
        """
        return self.FORTUNE_LABELS.get(fortune_type, '平')
