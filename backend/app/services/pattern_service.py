from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import InvestmentPattern


class PatternService:
    """投資パターンサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_patterns(self, user_id: str) -> List[InvestmentPattern]:
        """ユーザーの全パターンを取得"""
        result = await self.db.execute(
            select(InvestmentPattern)
            .where(InvestmentPattern.user_id == user_id)
            .order_by(InvestmentPattern.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_active_patterns(self, user_id: str) -> List[InvestmentPattern]:
        """有効なパターンのみ取得"""
        result = await self.db.execute(
            select(InvestmentPattern)
            .where(
                InvestmentPattern.user_id == user_id,
                InvestmentPattern.is_active == True
            )
        )
        return result.scalars().all()
    
    async def get_pattern_by_id(self, pattern_id: str) -> Optional[InvestmentPattern]:
        """IDでパターンを取得"""
        result = await self.db.execute(
            select(InvestmentPattern).where(InvestmentPattern.id == pattern_id)
        )
        return result.scalar_one_or_none()
