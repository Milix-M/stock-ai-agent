"""
投資パターンサービスのテスト
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.services.pattern_service import PatternService


class TestPatternService:
    """パターンサービスのテスト"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        return MagicMock()
    
    @pytest.fixture
    def service(self, mock_db):
        return PatternService(mock_db)
    
    def test_init(self, service, mock_db):
        """サービスが正しく初期化されるか"""
        assert service.db == mock_db


class TestLLMService:
    """LLMサービスのテスト"""
    
    def test_fallback_parse_per(self):
        """PER抽出のフォールバックが機能するか"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        result = service._fallback_parse("PER=15倍以下の高配当株")
        
        assert result["strategy"] == "dividend_focus"
        assert "filters" in result
        # PERが抽出される
        assert result["filters"].get("per_max") == 15
    
    def test_fallback_parse_dividend(self):
        """配当利回り抽出のフォールバックが機能するか"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        result = service._fallback_parse("配当利回り3%以上")
        
        assert result["strategy"] == "dividend_focus"
        assert result["filters"].get("dividend_yield_min") == 3
    
    def test_fallback_parse_growth(self):
        """成長戦略の判定が機能するか"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        result = service._fallback_parse("成長株")
        
        assert result["strategy"] == "growth"
    
    def test_fallback_parse_value(self):
        """バリュー戦略の判定が機能するか"""
        from app.services.llm_service import LLMService
        
        service = LLMService()
        result = service._fallback_parse("割安なバリュー株")
        
        assert result["strategy"] == "value"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])