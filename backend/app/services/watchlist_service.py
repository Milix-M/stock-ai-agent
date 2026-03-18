from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete

from app.models import Watchlist


class WatchlistService:
    """ウォッチリストサービス - 銘柄コードのみ保存"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_watchlist_codes(self, user_id: str) -> List[str]:
        """ユーザーのウォッチリスト銘柄コードを取得"""
        result = await self.db.execute(
            select(Watchlist.stock_code)
            .where(Watchlist.user_id == user_id)
            .order_by(Watchlist.created_at.desc())
        )
        return [row[0] for row in result.all()]
    
    async def add_to_watchlist(
        self, 
        user_id: str, 
        stock_code: str,
        alert_threshold: Optional[float] = None
    ) -> Watchlist:
        """ウォッチリストに追加（コードのみ）"""
        # 既存チェック
        existing = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_code == stock_code
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Stock already in watchlist")
        
        watchlist = Watchlist(
            user_id=user_id,
            stock_code=stock_code,
            alert_threshold=alert_threshold
        )
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        return watchlist
    
    async def remove_from_watchlist(self, user_id: str, stock_code: str) -> bool:
        """ウォッチリストから削除"""
        result = await self.db.execute(
            delete(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_code == stock_code
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def is_in_watchlist(self, user_id: str, stock_code: str) -> bool:
        """ウォッチリストに含まれているかチェック"""
        result = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_code == stock_code
                )
            )
        )
        return result.scalar_one_or_none() is not None