from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
import redis.asyncio as redis
from datetime import datetime

from app.config import get_settings
from app.services.stock_service import StockService
from app.services.news_service import NewsService
from app.services.financial_service import FinancialService
from app.services.technical_service import TechnicalAnalysisService
from app.agents import (
    AnalysisAgent, 
    AgentTools, 
    AgentOrchestrator,
    AgentSharedMemory
)

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
        financial_service = FinancialService()
        technical_service = TechnicalAnalysisService()
        tools = AgentTools(stock_service)
        
        # エージェント初期化
        agent = AnalysisAgent(
            tools=tools,
            news_service=news_service,
            financial_service=financial_service,
            technical_service=technical_service
        )
        
        # Orchestrator初期化
        orchestrator = AgentOrchestrator(redis_client)
        
        # コンテキスト構築
        context = {
            "stock_code": stock_code,
            "user_id": user_id,
        }
        
        try:
            # 分析実行
            result = await agent.execute(context)
            
            # 分析結果をRedisに保存（履歴として）
            memory = AgentSharedMemory(redis_client)
            await memory.save_analysis_history(stock_code, {
                "rating": result.overall_rating,
                "confidence": result.confidence_score,
                "summary": result.summary,
                "date": datetime.now().isoformat()
            })
            
            # 重要な分析結果があれば提案エージェントに依頼
            if result.overall_rating in ["buy", "sell"] and result.confidence_score > 0.6:
                await orchestrator.request_recommendation(
                    user_id=user_id or "system",
                    analysis_result={
                        "stock_code": stock_code,
                        "stock_name": result.stock_name,
                        "rating": result.overall_rating,
                        "confidence": result.confidence_score,
                        "summary": result.summary,
                        "key_points": result.key_points
                    }
                )
            
            return {
                "status": "success",
                "stock_code": stock_code,
                "rating": result.overall_rating,
                "confidence": result.confidence_score,
                "summary": result.summary,
                "key_points": result.key_points,
                "risks": result.risks,
                "recommendations": result.recommendations
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
def analyze_alerted_stocks(user_id: str, stock_codes: list):
    """
    アラートが発火した銘柄を分析
    """
    results = []
    for code in stock_codes:
        result = asyncio.run(run_analysis_task(code, user_id))
        results.append(result)
    
    return {
        "status": "success",
        "analyzed_count": len(results),
        "results": results
    }
