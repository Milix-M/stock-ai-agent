from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import joinedload

from app.models import Watchlist, Stock


class WatchlistService:
    """ウォッチリストサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_watchlist(self, user_id: str) -> List[Watchlist]:
        """ユーザーのウォッチリストを取得"""
        result = await self.db.execute(
            select(Watchlist)
            .where(Watchlist.user_id == user_id)
            .options(joinedload(Watchlist.stock))
            .order_by(Watchlist.created_at.desc())
        )
        return result.scalars().all()
    
    async def add_to_watchlist(
        self, 
        user_id: str, 
        stock_id: str, 
        alert_threshold: Optional[float] = None
    ) -> Watchlist:
        """ウォッチリストに追加"""
        # 既存チェック
        existing = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_id == stock_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Stock already in watchlist")
        
        watchlist = Watchlist(
            user_id=user_id,
            stock_id=stock_id,
            alert_threshold=alert_threshold
        )
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        return watchlist
    
    async def remove_from_watchlist(self, user_id: str, stock_id: str) -> bool:
        """ウォッチリストから削除"""
        result = await self.db.execute(
            delete(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_id == stock_id
                )
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def update_alert_threshold(
        self, 
        user_id: str, 
        stock_id: str, 
        threshold: Optional[float]
    ) -> Optional[Watchlist]:
        """アラート閾値を更新"""
        result = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_id == stock_id
                )
            )
        )
        watchlist = result.scalar_one_or_none()
        if watchlist:
            watchlist.alert_threshold = threshold
            await self.db.commit()
            await self.db.refresh(watchlist)
        return watchlist
    
    async def is_in_watchlist(self, user_id: str, stock_id: str) -> bool:
        """ウォッチリストに含まれているかチェック"""
        result = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == user_id,
                    Watchlist.stock_id == stock_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    async def get_watchlist_codes(self, user_id: str) -> List[str]:
        """ユーザーのウォッチリスト銘柄コードを取得"""
        result = await self.db.execute(
            select(Stock.code)
            .join(Watchlist)
            .where(Watchlist.user_id == user_id)
        )
        return [row[0] for row in result.all()]
