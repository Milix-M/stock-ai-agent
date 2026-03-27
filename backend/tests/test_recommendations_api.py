"""
レコメンドAPIテスト (GET list, POST generate)
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestRecommendationsAPI:
    @pytest.mark.asyncio
    async def test_get_recommendations_no_patterns(self, client, auth_headers):
        """有効なパターンがない場合のレスポンス"""
        response = await client.get(
            "/api/v1/recommendations/", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["recommendations"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_recommendations_with_patterns(self, client, auth_headers, db_session):
        """有効パターンがある場合のレコメンド生成"""
        from app.models.models import InvestmentPattern, User
        from sqlalchemy import select
        stmt = select(User).limit(1)
        result = await db_session.execute(stmt)
        user = result.scalar_one()

        # パターン作成
        pattern = InvestmentPattern(
            user_id=user.id,
            name="Rec Test",
            description="test",
            raw_input="test",
            parsed_filters={"strategy": "test", "filters": {}, "sectors": []},
            is_active=True,
        )
        db_session.add(pattern)
        await db_session.commit()

        mock_result = {
            "status": "success",
            "recommendations": [
                {"symbol": "7203.T", "name": "トヨタ自動車", "score": 0.9}
            ],
            "total_patterns": 1,
        }

        with patch("app.api.v1.recommendations.generate_all_recommendations", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_result
            response = await client.get(
                "/api/v1/recommendations/", headers=auth_headers
            )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["patterns_used"] == 1

    @pytest.mark.asyncio
    async def test_get_recommendations_unauthorized(self, client):
        response = await client.get("/api/v1/recommendations/")
        assert response.status_code == 401
