"""
テスト用共通フィクスチャ
インメモリSQLite + FastAPI TestClient + モック
"""
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models import User, InvestmentPattern, Stock, StockPrice, Watchlist, PushSubscription, Notification
from app.db.session import get_db
from app.main import app
from app.core.security import get_password_hash

# インメモリSQLite
TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """テスト用DBセッション"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """テスト用非同期HTTPクライアント（モックDB注入）"""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    """テスト用ユーザーを作成して返す"""
    user = User(
        email="test@example.com",
        password_hash=get_password_hash("password123"),
        display_name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(client, test_user):
    """テスト用ユーザーの認証ヘッダーを返す"""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


# yfinance と LLM系サービスのモックを自動適用
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """yfinance, LLMサービス, redis等の外部依存をモック"""
    # yfinance
    monkeypatch.setattr("yfinance.Ticker", lambda x: type("Ticker", (), {
        "info": {"symbol": x, "shortName": x, "sector": "Tech", "marketCap": 1e12,
                 "trailingPE": 15, "forwardPE": 14, "dividendYield": 0.02,
                 "priceToBook": 2.0, "roe": 0.15, "revenueGrowth": 0.1,
                 "regularMarketPrice": 100.0, "previousClose": 99.0,
                 "fiftyTwoWeekHigh": 120.0, "fiftyTwoWeekLow": 80.0,
                 "volume": 1000000, "averageVolume": 800000},
        "history": lambda period="1mo": type("Hist", (), {
            "empty": False,
            "index": [],
            "to_dict": lambda: [],
            "Close": type("S", (), {"iloc": type("I", (), {"__getitem__": lambda s, k: 100.0})()})(),
            "Volume": type("S", (), {"iloc": type("I", (), {"__getitem__": lambda s, k: 1000000})()})(),
        })(),
        "financials": type("F", (), {"to_dict": lambda: {}})(),
        "balance_sheet": type("B", (), {"to_dict": lambda: {}})(),
    })())

    # redis
    import unittest.mock
    mock_redis = unittest.mock.AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.exists.return_value = False
    monkeypatch.setattr("redis.asyncio.from_url", lambda *a, **kw: mock_redis)
    monkeypatch.setattr("redis.asyncio.Redis", lambda *a, **kw: mock_redis)
