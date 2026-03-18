from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/overview")
async def get_market_overview(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """マーケット概況を取得"""
    service = MarketService()
    
    overview = await service.get_market_overview()
    
    return overview


@router.get("/nikkei")
async def get_nikkei(
    current_user = Depends(get_current_user)
):
    """日経平均株価を取得"""
    service = MarketService()
    
    data = await service.get_nikkei_225()
    
    if not data:
        return {"error": "Failed to fetch Nikkei 225 data"}
    
    return data