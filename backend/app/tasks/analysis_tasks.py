from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
import redis.asyncio as redis

from app.config import get_settings
from app.services.stock_service import StockService
from app.services.news_service import NewsService
from app.services.technical_service import TechnicalAnalysisService
from app.agents import AnalysisAgent, AgentOrchestrator

settings = get_settings()

# 非同期セッション作成用
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Redis接続
redis_client = redis.from_url(settings.REDIS_URL)


async def run_analysis_task(stock_code: str, user_id: str = None):
    """分析タスクを実行"""
    async with AsyncSessionLocal() as db:
        # サービス初期化
        stock_service = StockService(db)
        news_service = NewsService()
        technical_service = TechnicalAnalysisService()
        
        # エージェント初期化
        agent = AnalysisAgent(
            stock_service=stock_service,
            news_service=news_service,
            technical_service=technical_service
        )
        
        # Orchestrator初期化
        orchestrator = AgentOrchestrator(redis_client)
        
        # コンテキスト構築
        context = {
            "stock_code": stock_code,
            "user_id": user_id
        }
        
        try:
            # 分析実行
            result = await agent.execute(context)
            
            # 結果をログ
            return {
                "status": "success",
                "stock_code": stock_code,
                "recommendation": result.recommendation,
                "confidence": result.confidence,
                "summary": result.analysis_summary,
                "signals": result.technical_signals,
                "key_points": result.key_points,
                "risks": result.risks
            }
            
        except Exception as e:
            return {
                "status": "error",
                "stock_code": stock_code,
                "error": str(e)
            }


@shared_task(bind=True, max_retries=3)
def analyze_stock_task(self, stock_code: str, user_id: str = None):
    """
    銘柄分析タスク（Celery）
    """
    try:
        result = asyncio.run(run_analysis_task(stock_code, user_id))
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def analyze_from_alert_task(stock_code: str, alert_data: dict, user_id: str = None):
    """
    アラートを受けて分析実行
    """
    from app.agents.tools import StockAlert
    
    # アラートデータを復元
    alert = StockAlert(
        stock_code=alert_data["stock_code"],
        stock_name=alert_data["stock_name"],
        alert_type=alert_data["alert_type"],
        severity=alert_data["severity"],
        message=alert_data["message"],
        current_value=alert_data["current_value"],
        threshold=alert_data["threshold"]
    )
    
    async def run():
        async with AsyncSessionLocal() as db:
            stock_service = StockService(db)
            news_service = NewsService()
            technical_service = TechnicalAnalysisService()
            
            agent = AnalysisAgent(
                stock_service=stock_service,
                news_service=news_service,
                technical_service=technical_service
            )
            
            orchestrator = AgentOrchestrator(redis_client)
            
            result = await agent.analyze_from_alert(
                stock_code=stock_code,
                alert=alert,
                orchestrator=orchestrator
            )
            
            return {
                "status": "success",
                "stock_code": stock_code,
                "recommendation": result.recommendation,
                "confidence": result.confidence
            }
    
    return asyncio.run(run())
