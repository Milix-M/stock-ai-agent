from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
import redis.asyncio as redis

from app.config import get_settings
from app.services.stock_service import StockService
from app.agents import MonitoringAgent, AgentTools, AgentOrchestrator, AgentSharedMemory

settings = get_settings()

# 非同期セッション作成用
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Redis接続
redis_client = redis.from_url(settings.REDIS_URL)


async def run_monitoring_task(user_id: str = None, stock_codes: list = None):
    """監視タスクを実行"""
    async with AsyncSessionLocal() as db:
        # サービスとツールの初期化
        stock_service = StockService(db)
        tools = AgentTools(stock_service)
        
        # エージェント初期化
        agent = MonitoringAgent(tools)
        
        # OrchestratorとMemory初期化
        orchestrator = AgentOrchestrator(redis_client)
        memory = AgentSharedMemory(redis_client)
        
        # コンテキスト構築
        context = {
            "user_id": user_id,
            "stock_codes": stock_codes or [],
            "threshold": 5.0,  # 5%閾値
        }
        
        try:
            # 監視実行
            result = await agent.monitor_and_notify(
                context=context,
                orchestrator=orchestrator
            )
            
            # 結果をログ
            return {
                "status": "success",
                "checked_stocks": result.checked_stocks,
                "alerts_found": result.triggered_count,
                "alerts": [
                    {
                        "code": a.stock_code,
                        "type": a.alert_type,
                        "severity": a.severity,
                        "message": a.message
                    }
                    for a in result.alerts
                ]
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


@shared_task(bind=True, max_retries=3)
def monitor_stocks_task(self, user_id: str = None, stock_codes: list = None):
    """
    株価監視タスク（Celery）
    定期的に株価を監視し、アラートを検知
    """
    try:
        result = asyncio.run(run_monitoring_task(user_id, stock_codes))
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def monitor_user_watchlist(user_id: str):
    """
    特定ユーザーのウォッチリストを監視
    """
    return asyncio.run(run_monitoring_task(user_id=user_id))
