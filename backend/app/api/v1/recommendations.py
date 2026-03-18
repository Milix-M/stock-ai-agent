from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
import redis.asyncio as redis_lib
import json

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.config import get_settings
from app.services.pattern_service import PatternService
from app.services.stock_search_service import StockSearchService
from app.tasks.recommendation_tasks import generate_all_recommendations
import asyncio

router = APIRouter()
settings = get_settings()


@router.get("/")
async def get_recommendations(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    ユーザーの投資パターンに基づくレコメンドを取得
    リアルタイムでマッチングを実行
    """
    pattern_service = PatternService(db)
    
    # ユーザーの有効なパターンを取得
    patterns = await pattern_service.get_active_patterns(str(current_user.id))
    
    if not patterns:
        return {
            "recommendations": [],
            "message": "有効な投資パターンがありません。パターンを作成してください。",
            "total": 0,
            "patterns_used": 0
        }
    
    # Redisからキャッシュを確認
    redis_client = redis_lib.from_url(settings.REDIS_URL)
    cache_key = f"recommendations:{current_user.id}"
    cached = await redis_client.get(cache_key)
    
    if cached:
        try:
            cached_data = json.loads(cached)
            return {
                "recommendations": cached_data.get("recommendations", []),
                "total": cached_data.get("total", 0),
                "patterns_used": len(patterns),
                "cached": True
            }
        except:
            pass  # キャッシュ解析エラー時は再生成
    
    # リアルタイムでレコメンド生成
    result = await generate_all_recommendations(str(current_user.id))
    
    if result.get("status") == "success":
        recommendations = result.get("recommendations", [])
        
        # キャッシュに保存（5分間）
        await redis_client.setex(
            cache_key,
            300,  # 5分
            json.dumps({
                "recommendations": recommendations,
                "total": len(recommendations)
            })
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "patterns_used": result.get("total_patterns", 0),
            "cached": False
        }
    else:
        return {
            "recommendations": [],
            "message": "レコメンドの生成に失敗しました",
            "total": 0,
            "patterns_used": 0
        }