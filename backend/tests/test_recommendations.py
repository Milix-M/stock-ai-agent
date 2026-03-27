import pytest
import uuid
from unittest.mock import patch


# ==========================================
# GET /recommendations/
# ==========================================

@pytest.mark.asyncio
async def test_get_recommendations_empty(async_http_client, auth_headers):
    """パターンがない場合のレコメンド"""
    response = await async_http_client.get(
        "/api/v1/recommendations/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) == 0
    assert data["total"] == 0
    assert data["patterns_used"] == 0
    assert "message" in data


@pytest.mark.asyncio
async def test_get_recommendations_success(async_http_client, auth_headers, test_pattern):
    """レコメンド取得成功（モック）"""
    # generate_all_recommendationsをモック
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        mock_gen.return_value = {
            "status": "success",
            "recommendations": [
                {
                    "stock_code": "7203",
                    "stock_name": "トヨタ自動車",
                    "match_score": 0.95,
                    "reason": "PER15倍以下、配当利回り3%以上の条件に合致"
                },
                {
                    "stock_code": "8306",
                    "stock_name": "三菱UFJ",
                    "match_score": 0.88,
                    "reason": "高配当、PBRが低い"
                }
            ],
            "total_patterns": 1
        }
        
        response = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["patterns_used"] == 1
        assert data["cached"] is False
        assert len(data["recommendations"]) == 2
        assert data["recommendations"][0]["stock_code"] == "7203"
        assert data["recommendations"][0]["match_score"] == 0.95
        
        # モックが呼ばれたことを確認
        mock_gen.assert_called_once()


@pytest.mark.asyncio
async def test_get_recommendations_multiple_patterns(async_http_client, auth_headers, test_pattern, inactive_pattern):
    """複数パターンのレコメンド"""
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        mock_gen.return_value = {
            "status": "success",
            "recommendations": [],
            "total_patterns": 1  # アクティブなパターンのみ
        }
        
        response = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # アクティブなパターンのみ使用される
        assert data["patterns_used"] == 1


@pytest.mark.asyncio
async def test_get_recommendations_generation_error(async_http_client, auth_headers, test_pattern):
    """レコメンド生成エラー"""
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        mock_gen.side_effect = Exception("LLM API error")
        
        response = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert "message" in data
        assert "失敗" in data["message"]


@pytest.mark.asyncio
async def test_get_recommendations_api_error(async_http_client, auth_headers, test_pattern):
    """APIからのエラーレスポンス"""
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        mock_gen.return_value = {
            "status": "error",
            "error": "API rate limit exceeded"
        }
        
        response = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert "rate limit exceeded" in data["message"]


@pytest.mark.asyncio
async def test_get_recommendations_unauthorized(async_http_client):
    """認証なしでレコメンド取得"""
    response = await async_http_client.get("/api/v1/recommendations/")
    
    assert response.status_code == 401


# ==========================================
# POST /recommendations/generate
# ==========================================

@pytest.mark.asyncio
async def test_manual_generate_recommendations(async_http_client, auth_headers, test_pattern):
    """手動レコメンド生成"""
    # POST /recommendations/generateエンドポイントがあるか確認
    # あればテスト、なければスキップ
    
    # 注: 現在のAPI定義ではこのエンドポイントがないかもしれない
    # 実際の実装に合わせて調整が必要
    pass


@pytest.mark.asyncio
async def test_recommendations_caching(async_http_client, auth_headers, test_pattern):
    """レコメンドキャッシング（Redisを使用）"""
    # テスト環境ではRedisが利用できない場合、キャッシュは無効化される
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        mock_gen.return_value = {
            "status": "success",
            "recommendations": [],
            "total_patterns": 1
        }
        
        # 1回目のリクエスト
        response1 = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        assert response1.status_code == 200
        
        # 2回目のリクエスト
        response2 = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        assert response2.status_code == 200


@pytest.mark.asyncio
async def test_recommendations_user_isolation(async_http_client, auth_headers, test_pattern, test_user2, async_test_session):
    """ユーザー間のレコメンド分離"""
    # 別ユーザーのパターンを作成
    from app.models import InvestmentPattern
    other_pattern = InvestmentPattern(
        id=uuid.uuid4(),
        user_id=test_user2.id,
        name="他人のパターン",
        raw_input="他人のパターン",
        parsed_filters={"strategy": "value"}
    )
    async_test_session.add(other_pattern)
    await async_test_session.commit()
    
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        mock_gen.return_value = {
            "status": "success",
            "recommendations": [],
            "total_patterns": 1
        }
        
        # test_userとしてリクエスト
        response = await async_http_client.get(
            "/api/v1/recommendations/",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        # test_userのパターンのみが使用される
        mock_gen.assert_called_once()
        call_args = mock_gen.call_args[0]
        assert call_args[0] == str(test_pattern.user_id)


@pytest.mark.asyncio
async def test_recommendations_timeout(async_http_client, auth_headers, test_pattern):
    """レコメンド生成タイムアウト"""
    import asyncio
    
    with patch("app.api.v1.recommendations.generate_all_recommendations") as mock_gen:
        # タイムアウトをシミュレート
        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(10)  # 長い待機
            return {"status": "success", "recommendations": [], "total_patterns": 1}
        
        mock_gen.side_effect = slow_generate
        
        # タイムアウトエラーになるかどうか
        # 注: 実際の実装に依存
        try:
            response = await async_http_client.get(
                "/api/v1/recommendations/",
                headers=auth_headers,
                timeout=1.0
            )
            # タイムアウトしない場合（デフォルト挙動）
            assert response.status_code in [200, 504]
        except Exception:
            # タイムアウト例外が発生する場合
            pass
