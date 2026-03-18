from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

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
    
    async def create_pattern(
        self,
        user_id: str,
        name: str,
        description: Optional[str],
        raw_input: str,
        parsed_filters: dict
    ) -> InvestmentPattern:
        """パターンを作成"""
        pattern = InvestmentPattern(
            user_id=user_id,
            name=name,
            description=description,
            raw_input=raw_input,
            parsed_filters=parsed_filters,
            is_active=True
        )
        self.db.add(pattern)
        await self.db.commit()
        await self.db.refresh(pattern)
        return pattern
    
    async def delete_pattern(self, pattern_id: str) -> bool:
        """パターンを削除"""
        result = await self.db.execute(
            delete(InvestmentPattern).where(InvestmentPattern.id == pattern_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def toggle_pattern_active(self, pattern_id: str) -> InvestmentPattern:
        """パターンの有効/無効を切り替え"""
        pattern = await self.get_pattern_by_id(pattern_id)
        if not pattern:
            raise ValueError("Pattern not found")
        
        pattern.is_active = not pattern.is_active
        await self.db.commit()
        await self.db.refresh(pattern)
        return pattern
