from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.watchlist_service import WatchlistService
from app.services.stock_search_service import StockSearchService

router = APIRouter()


@router.get("/")
async def get_watchlist(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリストを取得（リアルタイム株価付き）"""
    watchlist_service = WatchlistService(db)
    stock_search_service = StockSearchService()
    
    # DBからウォッチリスト取得（コードのみ）
    watchlist_codes = await watchlist_service.get_watchlist_codes(str(current_user.id))
    
    # 各銘柄のリアルタイムデータを取得
    results = []
    for code in watchlist_codes:
        # 銘柄情報取得
        info = await stock_search_service.get_stock_info(code)
        # 株価取得
        price = await stock_search_service.get_price_data(code)
        
        if info:
            results.append({
                "stock_code": code,
                "stock_name": info.name,
                "market": info.market,
                "sector": info.sector,
                "current_price": price.get("current_price") if price else None,
                "change_percent": price.get("change_percent") if price else None,
                "per": price.get("per") if price else None,
                "pbr": price.get("pbr") if price else None,
                "dividend_yield": price.get("dividend_yield") if price else None,
            })
    
    return results


@router.post("/")
async def add_to_watchlist(
    request: dict,  # { "stock_code": "7203" }
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリストに追加（コードのみ保存）"""
    watchlist_service = WatchlistService(db)
    stock_search_service = StockSearchService()
    
    stock_code = request.get("stock_code")
    if not stock_code:
        raise HTTPException(status_code=400, detail="stock_code is required")
    
    # 銘柄存在確認（API経由）
    info = await stock_search_service.get_stock_info(stock_code)
    if not info:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # 追加
    try:
        await watchlist_service.add_to_watchlist(
            user_id=str(current_user.id),
            stock_code=stock_code
        )
        return {
            "message": "Added to watchlist",
            "stock_code": stock_code,
            "stock_name": info.name
        }
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{stock_code}")
async def remove_from_watchlist(
    stock_code: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリストから削除"""
    watchlist_service = WatchlistService(db)
    
    success = await watchlist_service.remove_from_watchlist(
        user_id=str(current_user.id),
        stock_code=stock_code
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Stock not in watchlist")
    
    return {"message": "Removed from watchlist"}


@router.get("/{stock_code}/check")
async def check_watchlist(
    stock_code: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリストに含まれているかチェック"""
    watchlist_service = WatchlistService(db)
    
    is_in = await watchlist_service.is_in_watchlist(
        user_id=str(current_user.id),
        stock_code=stock_code
    )
    
    return {"in_watchlist": is_in}