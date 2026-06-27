"""占卜引擎核心模块"""
from datetime import datetime
from typing import Tuple, List, Dict, Optional
import math

class DivinationEngine:
    """占卜引擎主类"""
    
    HEXAGRAMS = {
        1: {"name": "乾", "symbol": "☰", "element": "金", "direction": "西北"},
        2: {"name": "坤", "symbol": "☷", "element": "土", "direction": "西南"},
        3: {"name": "震", "symbol": "☳", "element": "木", "direction": "东"},
        4: {"name": "巽", "symbol": "☴", "element": "木", "direction": "东南"},
        5: {"name": "兑", "symbol": "☵", "element": "金", "direction": "西"},
        6: {"name": "坎", "symbol": "☶", "element": "水", "direction": "北"},
        7: {"name": "艮", "symbol": "☷", "element": "土", "direction": "东北"},
        8: {"name": "离", "symbol": "☲", "element": "火", "direction": "南"},
    }
    
    ELEMENT_GENERATION = {
        "金": "水",
        "水": "木",
        "木": "火",
        "火": "土",
        "土": "金"
    }
    
    ELEMENT_RESTRICTION = {
        "金": "木",
        "木": "土",
        "土": "水",
        "水": "火",
        "火": "金"
    }
    
    def __init__(self):
        """初始化占卜引擎"""
        pass
    
    def query_by_timestamp(self, timestamp: datetime) -> Dict:
        """通过时间戳起卦
        
        Args:
            timestamp: 查询时间
            
        Returns:
            卦象信息字典
        """
        year_num = sum(int(d) for d in str(timestamp.year))
        month_num = timestamp.month
        day_num = timestamp.day
        hour_num = timestamp.hour
        
        total = year_num + month_num + day_num + hour_num
        
        primary_hex_num = (total % 8) or 8
        secondary_hex_num = ((day_num + hour_num) % 8) or 8
        changing_line = (total % 6) or 6
        
        return {
            "primary_hexagram": self.HEXAGRAMS[primary_hex_num],
            "secondary_hexagram": self.HEXAGRAMS[secondary_hex_num],
            "changing_lines": [changing_line],
            "calculation": {
                "year": year_num,
                "month": month_num,
                "day": day_num,
                "hour": hour_num,
                "total": total
            }
        }
    
    def query_by_numbers(self, num1: int, num2: int, num3: int) -> Dict:
        """通过数字起卦
        
        Args:
            num1, num2, num3: 三个数字
            
        Returns:
            卦象信息字典
        """
        total = num1 + num2 + num3
        
        primary_hex_num = (total % 8) or 8
        secondary_hex_num = ((num2 + num3) % 8) or 8
        changing_line = (total % 6) or 6
        
        return {
            "primary_hexagram": self.HEXAGRAMS[primary_hex_num],
            "secondary_hexagram": self.HEXAGRAMS[secondary_hex_num],
            "changing_lines": [changing_line],
            "calculation": {
                "num1": num1,
                "num2": num2,
                "num3": num3,
                "total": total
            }
        }
    
    def analyze_elements(self, hexagram_nums: List[int]) -> Dict:
        """分析五行平衡度
        
        Args:
            hexagram_nums: 卦象编号列表
            
        Returns:
            五行统计和平衡度
        """
        elements = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
        
        for hex_num in hexagram_nums:
            element = self.HEXAGRAMS[hex_num]["element"]
            elements[element] += 1
        
        values = list(elements.values())
        max_val = max(values)
        min_val = min(values)
        total = sum(values)
        
        balance_score = (max_val - min_val) / total if total > 0 else 0
        
        if balance_score < 0.2:
            balance_level = "完全平衡"
        elif balance_score < 0.4:
            balance_level = "基本平衡"
        elif balance_score < 0.6:
            balance_level = "需要调和"
        else:
            balance_level = "严重失衡"
        
        return {
            "elements": elements,
            "balance_score": round(balance_score, 3),
            "balance_level": balance_level
        }
    
    def calculate_fortune_score(self, 
                              primary_hex_num: int,
                              secondary_hex_num: int,
                              balance_score: float,
                              changing_line: int) -> Dict:
        """计算综合吉凶评分
        
        Args:
            primary_hex_num: 主卦编号
            secondary_hex_num: 变卦编号
            balance_score: 五行平衡分数
            changing_line: 动爻位置
            
        Returns:
            吉凶评分和等级
        """
        base_score = 60
        
        if primary_hex_num in [1, 2, 6]:
            base_score += 20
        elif primary_hex_num in [8, 3]:
            base_score += 15
        else:
            base_score += 10
        
        if primary_hex_num == secondary_hex_num:
            base_score += 10
        else:
            primary_element = self.HEXAGRAMS[primary_hex_num]["element"]
            secondary_element = self.HEXAGRAMS[secondary_hex_num]["element"]
            
            if self.ELEMENT_GENERATION.get(primary_element) == secondary_element:
                base_score += 15
            elif self.ELEMENT_RESTRICTION.get(primary_element) == secondary_element:
                base_score -= 15
        
        if balance_score < 0.2:
            base_score += 10
        elif balance_score < 0.4:
            base_score += 5
        elif balance_score > 0.6:
            base_score -= 15
        
        if changing_line <= 2:
            base_score -= 5
        elif changing_line >= 5:
            base_score += 5
        
        final_score = max(0, min(100, base_score))
        
        if final_score >= 85:
            fortune_level = "吉"
        elif final_score >= 70:
            fortune_level = "平吉"
        elif final_score >= 50:
            fortune_level = "平"
        elif final_score >= 30:
            fortune_level = "平凶"
        else:
            fortune_level = "凶"
        
        return {
            "fortune_score": round(final_score, 1),
            "fortune_level": fortune_level
        }
