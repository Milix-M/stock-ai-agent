import os
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


def _generate_vapid_keys() -> tuple[str, str]:
    """VAPID鍵ペアを自動生成して.envに保存する（開発用）"""
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives import serialization
    import base64

    private_key = ec.generate_private_key(ec.SECP256R1())
    pub_bytes = private_key.public_key().public_bytes(
        serialization.Encoding.X962,
        serialization.PublicFormat.UncompressedPoint,
    )
    priv_bytes = private_key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    def b64url(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

    public_key = b64url(pub_bytes)
    private_key_b64 = b64url(priv_bytes)

    # .envに追記
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    content = env_path.read_text() if env_path.exists() else ''
    prefix = 'VAPID_'
    lines = content.splitlines(keepends=True)
    filtered = [l for l in lines if not l.startswith(prefix)]
    filtered.append(f'\nVAPID_PUBLIC_KEY={public_key}\n')
    filtered.append(f'VAPID_PRIVATE_KEY={private_key_b64}\n')
    env_path.write_text(''.join(filtered))

    return public_key, private_key_b64


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # アプリ設定
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    APP_HOST: str = "0.0.0.0"
    SECRET_KEY: str = "dev-secret-key"
    
    # データベース
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/stock_ai"
    DATABASE_POOL_SIZE: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24時間
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # LLM
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_HTTP_REFERER: str = ""
    
    # 株価API
    STOCK_API_PROVIDER: str = "yfinance"
    ALPHA_VANTAGE_API_KEY: str = ""
    
    # Web Push
    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_CLAIMS_SUB: str = ""
    
    # メール
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""
    
    # ログ
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def ensure_vapid_keys(self) -> None:
        """VAPID鍵が未設定の場合に自動生成（開発用）"""
        if not self.VAPID_PUBLIC_KEY or not self.VAPID_PRIVATE_KEY:
            pub, priv = _generate_vapid_keys()
            # 現在のインスタンスを更新
            object.__setattr__(self, 'VAPID_PUBLIC_KEY', pub)
            object.__setattr__(self, 'VAPID_PRIVATE_KEY', priv)
            print(f"[INFO] VAPID keys auto-generated and saved to .env")
            print(f"[INFO] Add VITE_VAPID_PUBLIC_KEY={pub} to frontend/.env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
