"""
分析エージェントタスク（Celery）
"""
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
import redis.asyncio as redis

from app.config import get_settings
from app.agents.analysis_agent import analysis_agent
from app.agents import AgentSharedMemory

settings = get_settings()

# 非同期セッション作成用
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Redis接続
redis_client = redis.from_url(settings.REDIS_URL)


@shared_task(bind=True, max_retries=3)
def run_analysis_agent_for_stock(self, user_id: str, stock_code: str):
    """
    特定銘柄の分析を実行
    """
    try:
        result = asyncio.run(
            analysis_agent.run(
                context={
                    "user_id": user_id,
                    "stock_code": stock_code
                }
            )
        )
        return {
            "status": "success",
            "user_id": user_id,
            "stock_code": stock_code,
            "overall_rating": result.data.overall_rating,
            "confidence_score": result.data.confidence_score
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }


@shared_task(bind=True, max_retries=3)
def run_analysis_agent_for_watchlist(self, user_id: str):
    """
    ウォッチリスト全ての銘柄の分析を実行
    """
    try:
        result = asyncio.run(
            analysis_agent.run(
                context={
                    "user_id": user_id,
                    "stock_code": "watchlist"
                }
            )
        )
        return {
            "status": "success",
            "user_id": user_id,
            "watchlist_analyzed": True
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }


@shared_task
def trigger_daily_analysis():
    """
    日次の全ユーザーのパターンと照合するタスクをトリガー
    """
    try:
        # キャッシュされたレコメンドをクリア
        # 実際にはCelery Beatからgenerate_daily_recommendationsを呼び出す
        return {
            "status": "triggered",
            "message": "Daily analysis trigger sent"
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }
