import pytest
from datetime import datetime, timedelta

from app.core.security import create_access_token, create_refresh_token


# ==========================================
# POST /auth/register
# ==========================================

def test_register_success(test_client):
    """正常なユーザー登録"""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "NewPassword123",
            "display_name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(test_client, test_user):
    """メールアドレス重複エラー"""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "password": "Password123",
        }
    )
    
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]


def test_register_short_password(test_client):
    """パスワードが短すぎるエラー"""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser2@example.com",
            "password": "short",
        }
    )
    
    # バリデーションエラー（422）または409（DB制約）
    assert response.status_code in [409, 422]


def test_register_invalid_email(test_client):
    """無効なメールアドレス"""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Password123",
        }
    )
    
    assert response.status_code == 422


# ==========================================
# POST /auth/login
# ==========================================

def test_login_success(test_client, test_user):
    """正常ログイン"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_json_success(test_client, test_user):
    """JSON形式での正常ログイン"""
    response = test_client.post(
        "/api/v1/auth/login/json",
        json={
            "email": test_user.email,
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_email(test_client):
    """存在しないメールアドレス"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "TestPassword123"
        }
    )
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_wrong_password(test_client, test_user):
    """パスワード不一致"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "WrongPassword123"
        }
    )
    
    assert response.status_code == 401


def test_login_missing_fields(test_client):
    """必須フィールド欠落"""
    response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
        }
    )
    
    assert response.status_code == 422


# ==========================================
# POST /auth/refresh
# ==========================================

def test_refresh_token_success(test_client, test_user):
    """トークンリフレッシュ成功"""
    # まずログインしてリフレッシュトークンを取得
    login_response = test_client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user.email,
            "password": "TestPassword123"
        }
    )
    refresh_token = login_response.json()["refresh_token"]
    
    # リフレッシュ
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid(test_client):
    """無効なリフレッシュトークン"""
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"}
    )
    
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]


def test_refresh_token_wrong_type(test_client, test_user):
    """アクセストークンをリフレッシュトークンとして使用"""
    access_token = create_access_token(data={"sub": str(test_user.id)})
    
    response = test_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token}
    )
    
    assert response.status_code == 401
    assert "Invalid refresh token" in response.json()["detail"]


# ==========================================
# POST /auth/password-reset/request
# ==========================================

def test_password_reset_request_success(test_client, test_user):
    """パスワードリセット要求成功"""
    response = test_client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": test_user.email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "dev_mode" in data
    # 開発モードではトークンが返る
    assert "reset_token" in data


def test_password_reset_request_nonexistent_email(test_client):
    """存在しないメールアドレスでも同じレスポンス（セキュリティ）"""
    response = test_client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "nonexistent@example.com"}
    )
    
    # 成功と同じレスポンス（メールアドレス存在有無を暴露しない）
    assert response.status_code == 200
    assert "reset_token" not in response.json() or response.json()["reset_token"] is None


# ==========================================
# POST /auth/password-reset/confirm
# ==========================================

def test_password_reset_confirm_success(test_client, valid_reset_token):
    """パスワードリセット確認成功"""
    response = test_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": valid_reset_token.token,
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 200
    assert "updated" in response.json()["message"].lower()


def test_password_reset_confirm_short_password(test_client, valid_reset_token):
    """新しいパスワードが短すぎる"""
    response = test_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": valid_reset_token.token,
            "new_password": "short"
        }
    )
    
    assert response.status_code == 400
    assert "8文字以上" in response.json()["detail"]


def test_password_reset_confirm_invalid_token(test_client):
    """無効なトークン"""
    response = test_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": "invalid_token",
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 400
    assert "無効" in response.json()["detail"]


def test_password_reset_confirm_expired_token(test_client, expired_reset_token):
    """期限切れトークン"""
    response = test_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": expired_reset_token.token,
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 400
    assert "有効期限" in response.json()["detail"]


def test_password_reset_confirm_used_token(test_client, used_reset_token):
    """使用済みトークン"""
    response = test_client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "token": used_reset_token.token,
            "new_password": "NewPassword456"
        }
    )
    
    assert response.status_code == 400
    assert "無効" in response.json()["detail"]


# ==========================================
# GET /api/v1/users/me
# ==========================================

def test_get_current_user_info(test_client, test_user):
    """現在のユーザー情報取得"""
    token = create_access_token(data={"sub": str(test_user.id)})
    
    response = test_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["display_name"] == test_user.display_name
    assert str(data["id"]) == str(test_user.id)


def test_get_current_user_unauthorized(test_client):
    """認証なしでユーザー情報取得"""
    response = test_client.get("/api/v1/users/me")
    
    assert response.status_code == 401


def test_get_current_user_invalid_token(test_client):
    """無効なトークンでユーザー情報取得"""
    response = test_client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
