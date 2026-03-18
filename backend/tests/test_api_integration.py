"""
APIエンドポイントのテスト
"""
import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8000/api/v1"


@pytest.fixture
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client


class TestAuthAPI:
    """認証APIのテスト"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """ヘルスチェックエンドポイント"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json()["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_register_new_user(self):
        """新規ユーザー登録"""
        import uuid
        unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": unique_email,
                    "password": "TestPass123!",
                    "display_name": "Test User"
                }
            )
            print(f"Register response: {response.status_code} - {response.text}")
            assert response.status_code == 201
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        """重複メールアドレス登録"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            # まず登録
            response1 = await client.post(
                "/auth/register",
                json={
                    "email": "duplicate_test@example.com",
                    "password": "TestPass123!",
                    "display_name": "Test User"
                }
            )
            assert response1.status_code == 201
            
            # 同じメールで再登録
            response2 = await client.post(
                "/auth/register",
                json={
                    "email": "duplicate_test@example.com",
                    "password": "TestPass123!",
                    "display_name": "Test User"
                }
            )
            print(f"Duplicate register response: {response2.status_code} - {response2.text}")
            assert response2.status_code == 409
            assert "already registered" in response2.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_with_form_data(self):
        """OAuth2形式でのログイン"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/auth/login",
                data={
                    "username": "test@example.com",
                    "password": "password123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"Login response: {response.status_code} - {response.text[:200]}")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_login_with_json(self):
        """JSON形式でのログイン"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/auth/login/json",
                json={
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
            print(f"Login JSON response: {response.status_code} - {response.text[:200]}")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """不正な認証情報でのログイン"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/auth/login/json",
                json={
                    "email": "wrong@example.com",
                    "password": "wrongpass"
                }
            )
            print(f"Invalid login response: {response.status_code} - {response.text}")
            assert response.status_code == 401


class TestPatternAPI:
    """パターンAPIのテスト"""
    
    @pytest.fixture
    async def auth_token(self):
        """テスト用認証トークン"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/auth/login/json",
                json={
                    "email": "test@example.com",
                    "password": "password123"
                }
            )
            return response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_parse_pattern(self, auth_token):
        """パターンパースAPI"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/patterns/parse",
                json={"input": "高配当株でPER15倍以下"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            print(f"Parse pattern response: {response.status_code} - {response.text[:500]}")
            assert response.status_code == 200
            data = response.json()
            assert "parsed" in data
            assert "strategy" in data["parsed"]
    
    @pytest.mark.asyncio
    async def test_create_pattern(self, auth_token):
        """パターン作成API"""
        import uuid
        unique_name = f"Test Pattern {uuid.uuid4().hex[:8]}"
        
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.post(
                "/patterns/",
                json={
                    "name": unique_name,
                    "description": "Test description",
                    "raw_input": "高配当株でPER15倍以下",
                    "parsed_filters": {
                        "strategy": "dividend_focus",
                        "filters": {"per_max": 15},
                        "sectors": []
                    }
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            print(f"Create pattern response: {response.status_code} - {response.text[:500]}")
            assert response.status_code == 201
            data = response.json()
            assert data["name"] == unique_name
    
    @pytest.mark.asyncio
    async def test_list_patterns(self, auth_token):
        """パターン一覧取得API"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.get(
                "/patterns/",
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            print(f"List patterns response: {response.status_code} - {response.text[:500]}")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)


class TestCORS:
    """CORS設定のテスト"""
    
    @pytest.mark.asyncio
    async def test_cors_preflight(self):
        """CORSプリフライトリクエスト"""
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            response = await client.options(
                "/auth/register",
                headers={
                    "Origin": "http://localhost:5173",
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "Content-Type"
                }
            )
            print(f"CORS preflight response: {response.status_code}")
            print(f"Access-Control-Allow-Origin: {response.headers.get('access-control-allow-origin')}")
            assert response.status_code == 200
            assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
