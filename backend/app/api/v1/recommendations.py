from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis_lib
import json
import traceback

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.config import get_settings
from app.services.pattern_service import PatternService
from app.tasks.recommendation_tasks import generate_all_recommendations

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
    
    # リアルタイムでレコメンド生成
    try:
        result = await generate_all_recommendations(str(current_user.id))
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        traceback.print_exc()
        return {
            "recommendations": [],
            "message": f"レコメンドの生成に失敗しました: {str(e)}",
            "total": 0,
            "patterns_used": len(patterns)
        }
    
    if result.get("status") == "success":
        recommendations = result.get("recommendations", [])
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "patterns_used": result.get("total_patterns", 0),
            "cached": False
        }
    else:
        error_msg = result.get("error", "不明なエラー") if result else "レスポンスなし"
        return {
            "recommendations": [],
            "message": f"レコメンドの生成に失敗しました: {error_msg}",
            "total": 0,
            "patterns_used": 0
        }