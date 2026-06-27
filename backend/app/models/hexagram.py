"""卦象数据模型"""
from app import db
from datetime import datetime

class Hexagram(db.Model):
    """卦象模型"""
    __tablename__ = 'hexagrams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    symbol = db.Column(db.String(10), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    element = db.Column(db.String(10), nullable=False)
    direction = db.Column(db.String(10))
    season = db.Column(db.String(10))
    meaning = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'symbol': self.symbol,
            'number': self.number,
            'element': self.element
        }

class DivinationQuery(db.Model):
    """占卜查询记录"""
    __tablename__ = 'divination_queries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100))
    query_type = db.Column(db.String(50), nullable=False)
    input_method = db.Column(db.String(50), nullable=False)
    input_value = db.Column(db.String(500))
    
    primary_hexagram = db.Column(db.String(20), nullable=False)
    secondary_hexagram = db.Column(db.String(20))
    changing_lines = db.Column(db.String(50))
    
    fortune_score = db.Column(db.Float)
    fortune_level = db.Column(db.String(10))
    analysis_result = db.Column(db.JSON)
    
    query_timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'query_type': self.query_type,
            'primary_hexagram': self.primary_hexagram,
            'fortune_score': self.fortune_score,
            'fortune_level': self.fortune_level
        }
