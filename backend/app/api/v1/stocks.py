from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.stock_service import StockService
from app.schemas import StockResponse, StockDetailResponse, StockPriceData

router = APIRouter()


@router.get("/", response_model=List[StockResponse])
async def list_stocks(
    q: str = Query(None, description="検索キーワード"),
    market: str = Query(None, description="市場フィルタ"),
    sector: str = Query(None, description="業種フィルタ"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """銘柄一覧を取得"""
    service = StockService(db)
    
    if q:
        stocks = await service.search_stocks(q, limit)
    else:
        stocks = await service.get_all_stocks()
    
    # 簡易的なページネーション
    start = (page - 1) * limit
    end = start + limit
    paginated_stocks = stocks[start:end]
    
    return paginated_stocks


@router.get("/{code}", response_model=StockDetailResponse)
async def get_stock(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """銘柄詳細を取得"""
    service = StockService(db)
    
    stock = await service.get_stock_by_code(code)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # 価格データ取得
    daily_prices = await service.get_stock_prices(stock.id, days=30)
    weekly_prices = await service.get_stock_prices(stock.id, days=90)
    monthly_prices = await service.get_stock_prices(stock.id, days=365)
    
    # 最新価格と前日比
    latest_price = await service.get_latest_price(stock.id)
    price_change = None
    if len(daily_prices) >= 2:
        price_change = service.calculate_price_change(
            daily_prices[0].close,
            daily_prices[1].close
        )
    
    return {
        "id": stock.id,
        "code": stock.code,
        "name": stock.name,
        "market": stock.market,
        "sector": stock.sector,
        "per": stock.per,
        "pbr": stock.pbr,
        "dividend_yield": stock.dividend_yield,
        "market_cap": stock.market_cap,
        "prices": {
            "current": float(latest_price.close) if latest_price else None,
            "open": float(latest_price.open) if latest_price else None,
            "high": float(latest_price.high) if latest_price else None,
            "low": float(latest_price.low) if latest_price else None,
            "previous_close": float(daily_prices[1].close) if len(daily_prices) > 1 else None,
            **(price_change if price_change else {"change": 0, "change_percent": 0}),
            "volume": latest_price.volume if latest_price else 0
        },
        "chart_data": {
            "daily": [StockPriceData(
                date=p.date,
                open=float(p.open) if p.open else None,
                high=float(p.high) if p.high else None,
                low=float(p.low) if p.low else None,
                close=float(p.close),
                volume=p.volume,
                adjusted_close=float(p.adjusted_close) if p.adjusted_close else None
            ) for p in daily_prices],
            "weekly": [StockPriceData(
                date=p.date,
                close=float(p.close)
            ) for p in weekly_prices[::5]],  # 週次は5日ごと
            "monthly": [StockPriceData(
                date=p.date,
                close=float(p.close)
            ) for p in monthly_prices[::20]]  # 月次は20日ごと
        }
    }


@router.post("/{code}/fetch")
async def fetch_stock_price(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """株価データを手動で取得・更新"""
    service = StockService(db)
    
    stock = await service.get_stock_by_code(code)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    price = await service.fetch_and_save_price(code)
    if not price:
        raise HTTPException(status_code=500, detail="Failed to fetch price")
    
    return {"message": "Price updated successfully", "stock_code": code}
