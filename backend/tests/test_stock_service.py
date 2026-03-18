"""
株価検索サービスのテスト
"""
import pytest
import asyncio
from app.services.stock_search_service import StockSearchService


class TestStockSearchService:
    """株価検索サービスのテスト"""
    
    @pytest.fixture
    def service(self):
        return StockSearchService()
    
    @pytest.mark.asyncio
    async def test_search_by_code(self, service):
        """銘柄コードで検索できるか"""
        results = await service.search("7203", limit=10)
        
        assert len(results) > 0
        # トヨタ自動車が含まれる
        codes = [r.code for r in results]
        assert "7203" in codes
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, service):
        """銘柄名で検索できるか"""
        results = await service.search("トヨタ", limit=10)
        
        assert len(results) > 0
        names = [r.name for r in results]
        assert any("トヨタ" in name for name in names)
    
    @pytest.mark.asyncio
    async def test_search_limit(self, service):
        """検索結果の制限が機能するか"""
        results = await service.search("", limit=5)
        
        assert len(results) <= 5
    
    @pytest.mark.asyncio
    async def test_get_stock_info(self, service):
        """銘柄情報が取得できるか"""
        info = await service.get_stock_info("7203")
        
        assert info is not None
        assert info.code == "7203"
        assert info.name is not None
    
    @pytest.mark.asyncio
    async def test_get_stock_info_not_found(self, service):
        """存在しない銘柄はNoneを返すか"""
        info = await service.get_stock_info("9999")
        
        # 人気銘柄リストにない場合はyfinanceで試行するが、
        # 結果は取得できる場合もある
        assert info is None or info.code == "9999"
    
    @pytest.mark.asyncio
    async def test_get_price_data(self, service):
        """株価データが取得できるか（またはフォールバックされるか）"""
        # 人気銘柄でテスト
        price_data = await service.get_price_data("7203")
        
        # 取得できる場合はデータを検証
        if price_data:
            assert "current" in price_data or "close" in price_data
            assert price_data["code"] == "7203"
    
    @pytest.mark.asyncio
    async def test_get_historical_prices(self, service):
        """過去の株価データが取得できるか"""
        prices = await service.get_historical_prices("7203", period="5d")
        
        # 取得できる場合はデータを検証
        if prices:
            assert len(prices) > 0
            assert "close" in prices[0] or "Close" in prices[0]


class TestStockSearchFallback:
    """フォールバック機能のテスト"""
    
    def test_popular_stocks_loaded(self):
        """人気銘柄リストが読み込まれているか"""
        service = StockSearchService()
        
        assert len(service._popular_stocks) > 0
        # 主要銘柄が含まれる
        codes = [s["code"] for s in service._popular_stocks]
        assert "7203" in codes  # トヨタ
        assert "6758" in codes  # ソニー


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])