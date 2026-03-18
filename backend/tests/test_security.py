"""
認証サービスのテスト
"""
import pytest
import asyncio
from datetime import timedelta

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestPasswordSecurity:
    """パスワードセキュリティのテスト"""
    
    def test_password_hashing(self):
        """パスワードハッシュ化が正しく動作するか"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # ハッシュは平文と異なる
        assert hashed != password
        # ハッシュは文字列
        assert isinstance(hashed, str)
        # ハッシュは空でない
        assert len(hashed) > 0
    
    def test_password_verification(self):
        """パスワード検証が正しく動作するか"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # 正しいパスワードは検証成功
        assert verify_password(password, hashed) is True
        # 誤ったパスワードは検証失敗
        assert verify_password("wrongpassword", hashed) is False
    
    def test_password_verification_with_wrong_hash(self):
        """無効なハッシュでは検証が失敗するか"""
        assert verify_password("password", "invalid_hash") is False


class TestTokenSecurity:
    """トークンセキュリティのテスト"""
    
    def test_access_token_creation(self):
        """アクセストークンが正しく生成されるか"""
        data = {"sub": "user-123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # デコードして検証
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["type"] == "access"
        assert "exp" in decoded
    
    def test_refresh_token_creation(self):
        """リフレッシュトークンが正しく生成されるか"""
        data = {"sub": "user-123"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["type"] == "refresh"
    
    def test_token_expiration(self):
        """トークンの有効期限が設定されるか"""
        import time
        from datetime import datetime, timezone
        
        data = {"sub": "user-123"}
        token = create_access_token(data, expires_delta=timedelta(seconds=1))
        
        decoded = decode_token(token)
        exp_timestamp = decoded["exp"]
        
        # 有効期限は未来の時間
        now = datetime.now(timezone.utc).timestamp()
        assert exp_timestamp > now
    
    def test_invalid_token_decode(self):
        """無効なトークンはデコードできないか"""
        assert decode_token("invalid.token.here") is None
        assert decode_token("") is None
        assert decode_token("not.a.token") is None


class TestTokenDataIntegrity:
    """トークンデータの整合性テスト"""
    
    def test_token_payload_integrity(self):
        """トークンのペイロードが改ざんされていないか"""
        data = {
            "sub": "user-123",
            "email": "test@example.com",
            "type": "access"
        }
        token = create_access_token(data)
        decoded = decode_token(token)
        
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])