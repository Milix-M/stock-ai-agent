"""
レコメンドサービスのテスト
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.services.recommendation_service import PatternMatcher


class TestPatternMatcher:
    """パターンマッチングのテスト"""
    
    @pytest.fixture
    def mock_stock_service(self):
        service = MagicMock()
        return service
    
    @pytest.fixture
    def matcher(self, mock_stock_service):
        return PatternMatcher(mock_stock_service)
    
    def test_check_range_within(self, matcher):
        """範囲内の値が正しく判定されるか"""
        assert matcher._check_range(10, 5, 15) is True
        assert matcher._check_range(10, 10, 15) is True  # 境界値
        assert matcher._check_range(10, 5, 10) is True   # 境界値
    
    def test_check_range_outside(self, matcher):
        """範囲外の値が正しく判定されるか"""
        assert matcher._check_range(10, 15, 20) is False  # 小さすぎ
        assert matcher._check_range(10, 0, 5) is False    # 大きすぎ
    
    def test_check_range_no_bounds(self, matcher):
        """境界なしの場合は常にTrue"""
        assert matcher._check_range(10, None, None) is True
    
    def test_check_range_only_min(self, matcher):
        """最小値のみの場合"""
        assert matcher._check_range(10, 5, None) is True   # 範囲内
        assert matcher._check_range(3, 5, None) is False   # 範囲外
    
    def test_check_range_only_max(self, matcher):
        """最大値のみの場合"""
        assert matcher._check_range(10, None, 15) is True  # 範囲内
        assert matcher._check_range(20, None, 15) is False # 範囲外
    
    def test_check_range_none_value(self, matcher):
        """値がNoneの場合はFalse"""
        assert matcher._check_range(None, 5, 15) is False
    
    def test_format_market_cap_trillion(self, matcher):
        """兆円単位のフォーマット"""
        result = matcher._format_market_cap(1_500_000_000_000)
        assert "兆円" in result
    
    def test_format_market_cap_billion(self, matcher):
        """億円単位のフォーマット"""
        result = matcher._format_market_cap(500_000_000)
        assert "億円" in result
    
    def test_format_market_cap_unknown(self, matcher):
        """Noneの場合は不明"""
        result = matcher._format_market_cap(None)
        assert result == "不明"
    
    def test_determine_rating_buy(self, matcher):
        """買い評価が正しく判定されるか"""
        # 十分なポジティブスコア
        news = MagicMock()
        news.sentiment = "positive"
        financial = MagicMock()
        financial.revenue_trend = "growing"
        financial.profitability = "high"
        technical = MagicMock()
        technical.sma_5 = 110
        technical.sma_20 = 100
        
        rating = matcher._determine_rating(news, financial, technical)
        assert rating == "buy"
    
    def test_determine_rating_sell(self, matcher):
        """売り評価が正しく判定されるか"""
        news = MagicMock()
        news.sentiment = "negative"
        financial = MagicMock()
        financial.revenue_trend = "declining"
        financial.profitability = "low"
        technical = MagicMock()
        technical.sma_5 = 90
        technical.sma_20 = 100
        
        rating = matcher._determine_rating(news, financial, technical)
        assert rating == "sell"
    
    def test_determine_rating_hold(self, matcher):
        """ホールド評価が正しく判定されるか"""
        news = MagicMock()
        news.sentiment = "neutral"
        financial = MagicMock()
        financial.revenue_trend = "stable"
        financial.profitability = "medium"
        technical = MagicMock()
        technical.sma_5 = 100
        technical.sma_20 = 100
        
        rating = matcher._determine_rating(news, financial, technical)
        assert rating == "hold"


class TestConfidenceCalculation:
    """確信度計算のテスト"""
    
    @pytest.fixture
    def matcher(self):
        return PatternMatcher(MagicMock())
    
    def test_high_confidence(self, matcher):
        """高確信度が正しく計算されるか"""
        news = MagicMock()
        news.key_topics = ["topic1", "topic2"]
        financial = MagicMock()
        financial.key_metrics = {"eps": 100}
        technical = MagicMock()
        technical.rsi = 50
        
        confidence = matcher._calculate_confidence(news, financial, technical)
        assert confidence > 0.7
    
    def test_low_confidence(self, matcher):
        """低確信度が正しく計算されるか"""
        news = MagicMock()
        news.key_topics = []
        financial = MagicMock()
        financial.key_metrics = {}
        technical = MagicMock()
        technical.rsi = None
        
        confidence = matcher._calculate_confidence(news, financial, technical)
        assert confidence == 0.5  # デフォルト値


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])