import pytest
import uuid


# ==========================================
# GET /patterns/
# ==========================================

@pytest.mark.asyncio
async def test_list_patterns_empty(async_http_client, auth_headers, test_user):
    """パターン一覧取得（空）"""
    response = await async_http_client.get(
        "/api/v1/patterns/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_patterns_success(async_http_client, auth_headers, test_pattern, inactive_pattern):
    """パターン一覧取得成功"""
    response = await async_http_client.get(
        "/api/v1/patterns/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    
    # 名前で確認
    pattern_names = [p["name"] for p in data]
    assert "高配当株パターン" in pattern_names
    assert "成長株パターン" in pattern_names


@pytest.mark.asyncio
async def test_list_patterns_unauthorized(async_http_client):
    """認証なしで一覧取得"""
    response = await async_http_client.get("/api/v1/patterns/")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_patterns_only_own(async_http_client, auth_headers, test_pattern, test_user2, async_test_session):
    """自分のパターンのみ取得"""
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
    
    # test_userとして取得
    response = await async_http_client.get(
        "/api/v1/patterns/",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    pattern_names = [p["name"] for p in data]
    assert "他人のパターン" not in pattern_names


# ==========================================
# POST /patterns/parse
# ==========================================

@pytest.mark.asyncio
async def test_parse_pattern_success(async_http_client, auth_headers, mock_llm_service):
    """パターン解析成功"""
    # モック設定
    mock_llm_service.parse_pattern.return_value = {
        "strategy": "dividend_focus",
        "filters": {
            "per_max": 15,
            "dividend_yield_min": 3.0
        },
        "keywords": ["配当", "高配当"]
    }
    
    response = await async_http_client.post(
        "/api/v1/patterns/parse",
        json={"input": "高配当株でPER15倍以下、配当利回り3%以上"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["raw_input"] == "高配当株でPER15倍以下、配当利回り3%以上"
    assert "parsed" in data
    assert data["parsed"]["strategy"] == "dividend_focus"
    
    # モックが呼ばれたことを確認
    mock_llm_service.parse_pattern.assert_called_once()


@pytest.mark.asyncio
async def test_parse_pattern_unauthorized(async_http_client, mock_llm_service):
    """認証なしで解析"""
    response = await async_http_client.post(
        "/api/v1/patterns/parse",
        json={"input": "高配当株"}
    )
    
    assert response.status_code == 401
    mock_llm_service.parse_pattern.assert_not_called()


@pytest.mark.asyncio
async def test_parse_pattern_missing_input(async_http_client, auth_headers):
    """入力なし"""
    response = await async_http_client.post(
        "/api/v1/patterns/parse",
        json={},
        headers=auth_headers
    )
    
    assert response.status_code == 422


# ==========================================
# POST /patterns/ (Create)
# ==========================================

@pytest.mark.asyncio
async def test_create_pattern_success(async_http_client, auth_headers, mock_recommendation_tasks):
    """パターン作成成功"""
    response = await async_http_client.post(
        "/api/v1/patterns/",
        json={
            "name": "テストパターン",
            "description": "テスト用パターン",
            "raw_input": "テスト入力",
            "parsed_filters": {
                "strategy": "growth",
                "per_max": 20
            }
        },
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "テストパターン"
    assert data["description"] == "テスト用パターン"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    
    # 非同期タスクが呼ばれたことを確認
    mock_recommendation_tasks.assert_called_once()


@pytest.mark.asyncio
async def test_create_pattern_unauthorized(async_http_client, mock_recommendation_tasks):
    """認証なしで作成"""
    response = await async_http_client.post(
        "/api/v1/patterns/",
        json={
            "name": "テストパターン",
            "raw_input": "テスト",
            "parsed_filters": {}
        }
    )
    
    assert response.status_code == 401
    mock_recommendation_tasks.assert_not_called()


@pytest.mark.asyncio
async def test_create_pattern_missing_required_fields(async_http_client, auth_headers):
    """必須フィールド欠落"""
    response = await async_http_client.post(
        "/api/v1/patterns/",
        json={
            "name": "テストパターン",
            # raw_input と parsed_filters がない
        },
        headers=auth_headers
    )
    
    assert response.status_code == 422


# ==========================================
# DELETE /patterns/{pattern_id}
# ==========================================

@pytest.mark.asyncio
async def test_delete_pattern_success(async_http_client, auth_headers, test_pattern):
    """パターン削除成功"""
    response = await async_http_client.delete(
        f"/api/v1/patterns/{test_pattern.id}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "deleted" in response.json()["message"].lower()


@pytest.mark.asyncio
async def test_delete_pattern_not_found(async_http_client, auth_headers):
    """存在しないパターンを削除"""
    fake_id = uuid.uuid4()
    response = await async_http_client.delete(
        f"/api/v1/patterns/{fake_id}",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_pattern_unauthorized(async_http_client, test_pattern):
    """認証なしで削除"""
    response = await async_http_client.delete(f"/api/v1/patterns/{test_pattern.id}")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_pattern_other_user(async_http_client, test_pattern, test_user2):
    """他人のパターンを削除"""
    # 別ユーザーのトークンで作成
    from app.core.security import create_access_token
    other_token = create_access_token(data={"sub": str(test_user2.id)})
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    response = await async_http_client.delete(
        f"/api/v1/patterns/{test_pattern.id}",
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


# ==========================================
# PATCH /patterns/{pattern_id}/toggle
# ==========================================

@pytest.mark.asyncio
async def test_toggle_pattern_activate(async_http_client, auth_headers, inactive_pattern):
    """パターンを有効化"""
    response = await async_http_client.patch(
        f"/api/v1/patterns/{inactive_pattern.id}/toggle",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "activated" in data["message"].lower()
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_toggle_pattern_deactivate(async_http_client, auth_headers, test_pattern):
    """パターンを無効化"""
    response = await async_http_client.patch(
        f"/api/v1/patterns/{test_pattern.id}/toggle",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "deactivated" in data["message"].lower()
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_toggle_pattern_not_found(async_http_client, auth_headers):
    """存在しないパターンをトグル"""
    fake_id = uuid.uuid4()
    response = await async_http_client.patch(
        f"/api/v1/patterns/{fake_id}/toggle",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_toggle_pattern_unauthorized(async_http_client, test_pattern):
    """認証なしでトグル"""
    response = await async_http_client.patch(f"/api/v1/patterns/{test_pattern.id}/toggle")
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_toggle_pattern_other_user(async_http_client, test_pattern, test_user2):
    """他人のパターンをトグル"""
    from app.core.security import create_access_token
    other_token = create_access_token(data={"sub": str(test_user2.id)})
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    response = await async_http_client.patch(
        f"/api/v1/patterns/{test_pattern.id}/toggle",
        headers=other_headers
    )
    
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]
