"""
レコメンドサービスのテスト
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.services.recommendation_service import PatternMatcher


class TestPatternMatcherExistence:
    """PatternMatcherのメソッド存在確認テスト"""
    
    def test_matcher_has_required_methods(self):
        """必要なメソッドが存在するか"""
        from app.services.recommendation_service import PatternMatcher
        
        # 存在するメソッドを確認
        assert hasattr(PatternMatcher, 'match_pattern')
        assert hasattr(PatternMatcher, '_evaluate_stock')
        assert hasattr(PatternMatcher, '_check_range')
        assert hasattr(PatternMatcher, '_format_market_cap')


class TestMarketCapFormatting:
    """時価総額フォーマットのテスト"""
    
    @pytest.fixture
    def matcher(self):
        from app.services.recommendation_service import PatternMatcher
        return PatternMatcher(None)
    
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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])