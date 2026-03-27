"""
パターンAPIルーティングテスト (POST/GET/DELETE/toggle)
"""
import pytest
from unittest.mock import AsyncMock, patch


class TestPatternAPI:
    @pytest.mark.asyncio
    async def test_list_patterns_empty(self, client, auth_headers):
        response = await client.get("/api/v1/patterns/", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.asyncio
    async def test_list_patterns_unauthorized(self, client):
        response = await client.get("/api/v1/patterns/")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_pattern_success(self, client, auth_headers, db_session):
        pattern_data = {
            "name": "Test Pattern",
            "description": "テストパターン",
            "raw_input": "高配当株でPER15倍以下",
            "parsed_filters": {
                "strategy": "dividend_focus",
                "filters": {"per_max": 15},
                "sectors": [],
            },
        }

        # バックグラウンドタスクをモック
        with patch("app.api.v1.patterns.asyncio") as mock_asyncio:
            mock_asyncio.create_task.return_value = None
            response = await client.post(
                "/api/v1/patterns/", json=pattern_data, headers=auth_headers
            )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Pattern"

    @pytest.mark.asyncio
    async def test_delete_pattern_success(self, client, auth_headers, db_session):
        # まずパターンを作成
        pattern_data = {
            "name": "To Delete",
            "description": "削除用",
            "raw_input": "テスト",
            "parsed_filters": {"strategy": "test", "filters": {}, "sectors": []},
        }
        with patch("app.api.v1.patterns.asyncio") as mock_asyncio:
            mock_asyncio.create_task.return_value = None
            create_resp = await client.post(
                "/api/v1/patterns/", json=pattern_data, headers=auth_headers
            )
        pattern_id = create_resp.json()["id"]

        # 削除
        del_resp = await client.delete(
            f"/api/v1/patterns/{pattern_id}", headers=auth_headers
        )
        assert del_resp.status_code == 200

        # 削除確認
        list_resp = await client.get("/api/v1/patterns/", headers=auth_headers)
        assert all(p["id"] != pattern_id for p in list_resp.json())

    @pytest.mark.asyncio
    async def test_delete_pattern_not_found(self, client, auth_headers):
        response = await client.delete(
            "/api/v1/patterns/nonexistent-id", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_toggle_pattern(self, client, auth_headers, db_session):
        pattern_data = {
            "name": "Toggle Pattern",
            "description": "トグル用",
            "raw_input": "テスト",
            "parsed_filters": {"strategy": "test", "filters": {}, "sectors": []},
        }
        with patch("app.api.v1.patterns.asyncio") as mock_asyncio:
            mock_asyncio.create_task.return_value = None
            create_resp = await client.post(
                "/api/v1/patterns/", json=pattern_data, headers=auth_headers
            )
        pattern_id = create_resp.json()["id"]

        # トグル (有効→無効)
        toggle_resp = await client.patch(
            f"/api/v1/patterns/{pattern_id}/toggle", headers=auth_headers
        )
        assert toggle_resp.status_code == 200
        assert toggle_resp.json()["is_active"] is False

        # もう一度トグル (無効→有効)
        toggle_resp2 = await client.patch(
            f"/api/v1/patterns/{pattern_id}/toggle", headers=auth_headers
        )
        assert toggle_resp2.json()["is_active"] is True

    @pytest.mark.asyncio
    async def test_parse_pattern(self, client, auth_headers):
        mock_parsed = {
            "strategy": "dividend_focus",
            "filters": {"per_max": 15, "dividend_yield_min": 0.03},
            "sectors": ["Financial"],
        }

        with patch("app.api.v1.patterns.LLMService") as MockLLM:
            mock_instance = AsyncMock()
            mock_instance.parse_pattern.return_value = mock_parsed
            MockLLM.return_value = mock_instance

            response = await client.post(
                "/api/v1/patterns/parse",
                json={"input": "高配当株でPER15倍以下"},
                headers=auth_headers,
            )
        assert response.status_code == 200
        assert "parsed" in response.json()
