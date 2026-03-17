from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.watchlist_service import WatchlistService
from app.services.stock_service import StockService
from app.schemas import WatchlistResponse, WatchlistCreate

router = APIRouter()


@router.get("/", response_model=List[WatchlistResponse])
async def get_watchlist(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリスト一覧を取得"""
    service = WatchlistService(db)
    watchlist = await service.get_user_watchlist(str(current_user.id))
    return watchlist


@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    request: WatchlistCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリストに追加"""
    service = WatchlistService(db)
    
    # 銘柄存在確認
    stock_service = StockService(db)
    stock = await stock_service.get_stock_by_code(request.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    try:
        watchlist = await service.add_to_watchlist(
            user_id=str(current_user.id),
            stock_id=str(stock.id),
            alert_threshold=request.alert_threshold
        )
        
        # リレーションを明示的に読み込む
        await db.refresh(watchlist, ['stock'])
        
        return watchlist
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{stock_code}")
async def remove_from_watchlist(
    stock_code: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ウォッチリストから削除"""
    service = WatchlistService(db)
    stock_service = StockService(db)
    
    # 銘柄取得
    stock = await stock_service.get_stock_by_code(stock_code)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # 削除実行
    success = await service.remove_from_watchlist(
        user_id=str(current_user.id),
        stock_id=str(stock.id)
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
    service = WatchlistService(db)
    stock_service = StockService(db)
    
    stock = await stock_service.get_stock_by_code(stock_code)
    if not stock:
        return {"in_watchlist": False}
    
    is_in = await service.is_in_watchlist(
        user_id=str(current_user.id),
        stock_id=str(stock.id)
    )
    
    return {"in_watchlist": is_in}
