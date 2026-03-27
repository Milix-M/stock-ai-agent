from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, users, stocks, patterns, watchlist, notifications, recommendations, admin, market
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.middleware.security import SecurityHeadersMiddleware
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.config import get_settings
from app.db.session import engine
from app.models.base import Base
# Import models to register them with SQLAlchemy
from app.models import User, InvestmentPattern, Stock, StockPrice, Watchlist, PushSubscription, Notification

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフスパン管理"""
    # 起動時
    async with engine.begin() as conn:
        # 開発環境のみ: テーブル作成
        if settings.APP_ENV == "development":
            await conn.run_sync(Base.metadata.create_all)
    yield
    # 終了時
    await engine.dispose()


app = FastAPI(
    title="PICKS API",
    description="株AIエージェントバックエンドAPI",
    version="0.1.0",
    lifespan=lifespan,
)

# Security Headers
app.add_middleware(SecurityHeadersMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ヘルスチェック
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}


# APIルーター
# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# APIルーター
app.include_router(auth.router, prefix="/api/v1/auth", tags=["認証"])
app.include_router(users.router, prefix="/api/v1/users", tags=["ユーザー"])
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["銘柄"])
app.include_router(patterns.router, prefix="/api/v1/patterns", tags=["パターン"])
app.include_router(watchlist.router, prefix="/api/v1/watchlist", tags=["ウォッチリスト"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["通知"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["レコメンド"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["管理"])
app.include_router(market.router, prefix="/api/v1/market", tags=["マーケット"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)
