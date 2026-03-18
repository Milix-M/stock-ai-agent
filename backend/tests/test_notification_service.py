"""
通知サービスのテスト
"""
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.notification_service import NotificationService, NotificationPayload


class TestNotificationPayload:
    """通知ペイロードのテスト"""
    
    def test_payload_creation(self):
        """ペイロードが正しく作成されるか"""
        payload = NotificationPayload(
            title="テスト通知",
            body="これはテストです",
            data={"key": "value"}
        )
        
        assert payload.title == "テスト通知"
        assert payload.body == "これはテストです"
        assert payload.data == {"key": "value"}
        assert payload.icon == "/icon-192.png"  # デフォルト値
    
    def test_payload_with_actions(self):
        """アクション付きペイロードが正しく作成されるか"""
        payload = NotificationPayload(
            title="テスト",
            body="本文",
            actions=[
                {"action": "view", "title": "詳細"},
                {"action": "dismiss", "title": "閉じる"}
            ]
        )
        
        assert len(payload.actions) == 2
        assert payload.actions[0]["action"] == "view"


class TestNotificationService:
    """通知サービスのテスト"""
    
    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = MagicMock()
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        # VAPIDキーをモック
        with patch("app.services.notification_service.settings") as mock_settings:
            mock_settings.VAPID_PRIVATE_KEY = "test-key"
            mock_settings.VAPID_CLAIMS_SUB = "mailto:test@example.com"
            return NotificationService(mock_db)
    
    @pytest.mark.asyncio
    async def test_get_user_subscriptions(self, service, mock_db):
        """ユーザーの購読情報が取得できるか"""
        mock_subscription = MagicMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_subscription]
        mock_db.execute.return_value = mock_result
        
        subscriptions = await service.get_user_subscriptions("user-123")
        
        assert len(subscriptions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])