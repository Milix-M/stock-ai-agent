import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Boolean, DateTime, Text, Numeric, BigInteger, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """ユーザーモデル"""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    patterns: Mapped[List["InvestmentPattern"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    watchlists: Mapped[List["Watchlist"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    push_subscriptions: Mapped[List["PushSubscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class InvestmentPattern(Base):
    """投資パターンモデル"""
    __tablename__ = "investment_patterns"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_input: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_filters: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    user: Mapped["User"] = relationship(back_populates="patterns")

    def __repr__(self) -> str:
        return f"<InvestmentPattern(id={self.id}, name={self.name})>"


class Stock(Base):
    """銘柄情報モデル"""
    __tablename__ = "stocks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    market: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    per: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    pbr: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    dividend_yield: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    market_cap: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # リレーションシップ
    prices: Mapped[List["StockPrice"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    watchlists: Mapped[List["Watchlist"]] = relationship(back_populates="stock", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Stock(code={self.code}, name={self.name})>"


class StockPrice(Base):
    """株価時系列データモデル（TimescaleDBハイパーテーブル）"""
    __tablename__ = "stock_prices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stock_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stocks.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    open: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    high: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    low: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    close: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    volume: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    adjusted_close: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)

    # リレーションシップ
    stock: Mapped["Stock"] = relationship(back_populates="prices")

    def __repr__(self) -> str:
        return f"<StockPrice(stock={self.stock_id}, date={self.date}, close={self.close})>"


class Watchlist(Base):
    """ウォッチリストモデル - 銘柄コードのみ保存"""
    __tablename__ = "watchlists"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    stock_code: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_threshold: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # ユニーク制約: ユーザー×銘柄コード
    __table_args__ = (
        UniqueConstraint('user_id', 'stock_code', name='uix_user_stock_code'),
    )

    # リレーションシップ
    user: Mapped["User"] = relationship(back_populates="watchlists")

    def __repr__(self) -> str:
        return f"<Watchlist(user={self.user_id}, stock_code={self.stock_code})>"


class PushSubscription(Base):
    """プッシュ通知購読モデル"""
    __tablename__ = "push_subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    p256dh: Mapped[str] = mapped_column(Text, nullable=False)
    auth: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    user: Mapped["User"] = relationship(back_populates="push_subscriptions")

    def __repr__(self) -> str:
        return f"<PushSubscription(user={self.user_id})>"


class Notification(Base):
    """通知履歴モデル"""
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # リレーションシップ
    user: Mapped["User"] = relationship(back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(user={self.user_id}, title={self.title})>"
