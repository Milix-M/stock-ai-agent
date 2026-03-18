from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import redis.asyncio as redis_lib

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.config import get_settings
from app.services.recommendation_service import PatternMatcher
from app.services.pattern_service import PatternService
from app.services.stock_service import StockService

router = APIRouter()
settings = get_settings()


@router.get("/")
async def get_recommendations(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ユーザーの投資パターンに基づくレコメンドを取得
    """
    # サービス初期化
    pattern_service = PatternService(db)
    stock_service = StockService(db)
    matcher = PatternMatcher(stock_service)
    
    # ユーザーの有効なパターンを取得
    patterns = await pattern_service.get_active_patterns(str(current_user.id))
    
    if not patterns:
        return {
            "recommendations": [],
            "message": "有効な投資パターンがありません。パターンを作成してください。",
            "total": 0
        }
    
    # Redisからキャッシュを確認
    redis_client = redis_lib.from_url(settings.REDIS_URL)
    cache_key = f"recommendations:{current_user.id}"
    cached = await redis_client.get(cache_key)
    
    if cached:
        import json
        cached_data = json.loads(cached)
        return cached_data
    
    # パターンマッチング実行
    all_recommendations = []
    
    for pattern in patterns:
        matches = await matcher.match_pattern(pattern)
        
        for match in matches[:5]:  # パターンごと上位5件
            all_recommendations.append({
                "stock_code": match.stock_code,
                "stock_name": match.stock_name,
                "pattern_name": pattern.name,
                "match_score": match.match_score,
                "matched_criteria": match.matched_criteria,
                "reason": match.recommendation_reason
            })
    
    # スコア順にソート
    all_recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    
    result = {
        "recommendations": all_recommendations[:10],  # 上位10件
        "total": len(all_recommendations),
        "patterns_used": len(patterns)
    }
    
    # キャッシュに保存（30分間）
    await redis_client.setex(cache_key, 1800, str(result))
    
    return result
