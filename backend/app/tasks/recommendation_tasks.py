"""
レコメンドタスク
"""
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
import redis.asyncio as redis

from app.config import get_settings
from app.services.stock_service import StockService
from app.services.pattern_service import PatternService
from app.services.recommendation_service import PatternMatcher
from app.agents import (
    RecommendationAgent,
    AgentTools,
    AgentSharedMemory
)

settings = get_settings()

# 非同期セッション作成用
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Redis接続
redis_client = redis.from_url(settings.REDIS_URL)


async def generate_recommendations_task(user_id: str):
    """レコメンドを生成"""
    async with AsyncSessionLocal() as db:
        # サービス初期化
        stock_service = StockService(db)
        pattern_service = PatternService(db)
        pattern_matcher = PatternMatcher(stock_service)
        tools = AgentTools(stock_service)
        memory = AgentSharedMemory(redis_client)
        
        # エージェント初期化
        agent = RecommendationAgent(
            tools=tools,
            pattern_matcher=pattern_matcher,
            memory=memory
        )
        
        # ユーザーパターン取得
        patterns = await pattern_service.get_active_patterns(user_id)
        
        if not patterns:
            return {
                "status": "no_patterns",
                "message": "No active patterns found",
                "user_id": user_id
            }
        
        # コンテキスト構築
        context = {
            "user_id": user_id,
            "patterns": patterns,
            "analysis_results": []  # 分析結果があれば追加
        }
        
        try:
            # レコメンド生成
            result = await agent.execute(context)
            
            # 結果をRedisに保存
            await redis_client.setex(
                f"recommendations:{user_id}",
                3600,  # 1時間保持
                str(result.dict())
            )
            
            return {
                "status": "success",
                "user_id": user_id,
                "total_recommendations": len(result.recommendations),
                "top_recommendations": [
                    {
                        "stock_code": r.stock_code,
                        "stock_name": r.stock_name,
                        "pattern": r.pattern_name,
                        "score": r.match_score,
                        "priority": r.priority
                    }
                    for r in result.recommendations[:5]
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "user_id": user_id,
                "error": str(e)
            }


@shared_task(bind=True, max_retries=3)
def generate_daily_recommendations(self, user_id: str = None):
    """
    日次レコメンド生成タスク（Celery）
    """
    try:
        if user_id:
            result = asyncio.run(generate_recommendations_task(user_id))
            return result
        else:
            # 全ユーザーのレコメンドを生成
            # TODO: 全ユーザー取得ロジック
            return {
                "status": "batch_scheduled",
                "message": "Batch recommendation generation scheduled"
            }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
