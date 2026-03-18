from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.stock_search_service import StockSearchService
from app.schemas import StockResponse

router = APIRouter()
stock_search_service = StockSearchService()


@router.get("/", response_model=List[StockResponse])
async def search_stocks(
    q: str = Query(..., description="検索キーワード（銘柄コードまたは銘柄名）"),
    limit: int = Query(20, ge=1, le=50),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """銘柄を検索（yfinance経由）"""
    results = await stock_search_service.search(q, limit)
    
    return [
        StockResponse(
            id=result.code,  # コードをID代わりに使用
            code=result.code,
            name=result.name,
            market=result.market,
            sector=result.sector,
            per=None,
            pbr=None,
            dividend_yield=None,
            market_cap=None,
            created_at="",
            updated_at=""
        )
        for result in results
    ]


@router.get("/{code}/price")
async def get_stock_price(
    code: str,
    current_user = Depends(get_current_user)
):
    """リアルタイム株価を取得（yfinance経由）"""
    price_data = await stock_search_service.get_price_data(code)
    
    if not price_data:
        raise HTTPException(status_code=404, detail="Stock price data not available")
    
    return price_data


@router.get("/{code}/history")
async def get_stock_history(
    code: str,
    period: str = Query("1mo", description="期間（1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max）"),
    current_user = Depends(get_current_user)
):
    """過去の株価データを取得（yfinance経由）"""
    prices = await stock_search_service.get_historical_prices(code, period)
    
    if not prices:
        raise HTTPException(status_code=404, detail="Historical data not available")
    
    return {"code": code, "period": period, "prices": prices}