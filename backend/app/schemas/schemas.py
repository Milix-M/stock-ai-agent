from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ==================== User Schemas ====================

class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserBase):
    id: UUID
    password_hash: str
    created_at: datetime
    updated_at: datetime


# ==================== Auth Schemas ====================

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ==================== Pattern Schemas ====================

class PatternBase(BaseModel):
    name: str
    description: Optional[str] = None
    raw_input: str
    parsed_filters: dict
    is_active: bool = True


class PatternCreate(PatternBase):
    pass


class PatternResponse(PatternBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PatternParseRequest(BaseModel):
    input: str


class PatternParseResponse(BaseModel):
    raw_input: str
    parsed: dict


# ==================== Stock Schemas ====================

class StockBase(BaseModel):
    code: str
    name: str
    market: Optional[str] = None
    sector: Optional[str] = None
    per: Optional[float] = None
    pbr: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[int] = None


class StockCreate(StockBase):
    pass


class StockResponse(StockBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StockPriceData(BaseModel):
    date: datetime
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: float
    volume: Optional[int] = None
    adjusted_close: Optional[float] = None


class StockSearchResponse(StockBase):
    """yfinance検索結果用のレスポンス（IDなし）"""
    pass


class StockDetailResponse(StockResponse):
    prices: dict  # daily, weekly, monthly


# ==================== Watchlist Schemas ====================

class WatchlistBase(BaseModel):
    stock_id: UUID
    alert_threshold: Optional[float] = None


class WatchlistCreate(WatchlistBase):
    pass


class WatchlistResponse(WatchlistBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    stock: StockResponse
    
    class Config:
        from_attributes = True


# ==================== Notification Schemas ====================

class NotificationBase(BaseModel):
    type: str
    title: str
    body: str
    data: Optional[dict] = None


class NotificationCreate(NotificationBase):
    pass


class NotificationResponse(NotificationBase):
    id: UUID
    user_id: UUID
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class PushSubscriptionCreate(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


# ==================== Recommendation Schemas ====================

class RecommendationResponse(BaseModel):
    stock: StockResponse
    match_score: float
    reason: str
    matched_filters: dict
    alerts: list


class RecommendationListResponse(BaseModel):
    recommendations: list[RecommendationResponse]
    generated_at: datetime
