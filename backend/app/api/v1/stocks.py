from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.stock_search_service import StockSearchService
from app.schemas import StockSearchResponse

router = APIRouter()
stock_search_service = StockSearchService()


@router.get("/", response_model=List[StockSearchResponse])
@limiter.limit("20/minute")
async def search_stocks(
    request: Request,
    q: str = Query(..., description="検索キーワード（銘柄コードまたは銘柄名）"),
    limit: int = Query(20, ge=1, le=50),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """銘柄を検索（yfinance経由）"""
    results = await stock_search_service.search(q, limit)
    
    return [
        StockSearchResponse(
            code=result.code,
            name=result.name,
            market=result.market,
            sector=result.sector,
            per=None,
            pbr=None,
            dividend_yield=None,
            market_cap=None
        )
        for result in results
    ]


@router.get("/{code}/detail")
async def get_stock_detail(
    code: str,
    current_user = Depends(get_current_user)
):
    """銘柄詳細情報を取得（基本情報＋株価データ）"""
    info_result = await stock_search_service.get_stock_info(code)
    price_data = await stock_search_service.get_price_data(code)

    if not info_result and not price_data:
        raise HTTPException(status_code=404, detail="Stock not found")

    return {
        "code": code,
        "name": info_result.name if info_result else None,
        "market": info_result.market if info_result else None,
        "sector": info_result.sector if info_result else None,
        **(price_data or {}),
    }


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