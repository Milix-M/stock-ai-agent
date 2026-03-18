"""
ウォッチリストサービスのテスト
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

from app.services.watchlist_service import WatchlistService


class TestWatchlistService:
    """ウォッチリストサービスのテスト"""
    
    @pytest.fixture
    def mock_db(self):
        """モックデータベースセッション"""
        db = MagicMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        return WatchlistService(mock_db)
    
    @pytest.mark.asyncio
    async def test_add_to_watchlist(self, service, mock_db):
        """ウォッチリストに追加できるか"""
        # 既存チェックでNoneを返す（新規追加）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await service.add_to_watchlist("user-123", "7203")
        
        assert result is not None
        assert result.stock_code == "7203"
        assert result.user_id == "user-123"
    
    @pytest.mark.asyncio
    async def test_add_duplicate_raises_error(self, service, mock_db):
        """重複追加でエラーが発生するか"""
        # 既存チェックで既存データを返す
        mock_existing = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_existing
        mock_db.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="already in watchlist"):
            await service.add_to_watchlist("user-123", "7203")
    
    @pytest.mark.asyncio
    async def test_remove_from_watchlist(self, service, mock_db):
        """ウォッチリストから削除できるか"""
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_db.execute.return_value = mock_result
        
        result = await service.remove_from_watchlist("user-123", "7203")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_remove_not_found(self, service, mock_db):
        """存在しない銘柄の削除はFalseを返すか"""
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_db.execute.return_value = mock_result
        
        result = await service.remove_from_watchlist("user-123", "9999")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_is_in_watchlist_true(self, service, mock_db):
        """ウォッチリストに含まれる場合Trueを返すか"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_result
        
        result = await service.is_in_watchlist("user-123", "7203")
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_in_watchlist_false(self, service, mock_db):
        """ウォッチリストに含まれない場合Falseを返すか"""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await service.is_in_watchlist("user-123", "9999")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_watchlist_codes(self, service, mock_db):
        """ウォッチリストのコード一覧が取得できるか"""
        mock_result = MagicMock()
        mock_result.all.return_value = [("7203",), ("6758",), ("9984",)]
        mock_db.execute.return_value = mock_result
        
        codes = await service.get_watchlist_codes("user-123")
        
        assert len(codes) == 3
        assert "7203" in codes
        assert "6758" in codes
        assert "9984" in codes


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])