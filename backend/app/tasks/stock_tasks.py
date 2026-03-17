from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import asyncio

from app.config import get_settings
from app.services.stock_service import StockService

settings = get_settings()

# 非同期セッション作成用
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def fetch_all_prices_async():
    """全銘柄の株価を取得"""
    async with AsyncSessionLocal() as db:
        service = StockService(db)
        stocks = await service.get_all_stocks()
        
        results = []
        for stock in stocks:
            try:
                price = await service.fetch_and_save_price(stock.code)
                results.append({
                    "code": stock.code,
                    "success": price is not None
                })
            except Exception as e:
                results.append({
                    "code": stock.code,
                    "success": False,
                    "error": str(e)
                })
        
        return results


@shared_task(bind=True, max_retries=3)
def fetch_daily_stock_prices(self):
    """全銘柄の日次株価を取得（Celeryタスク）"""
    try:
        result = asyncio.run(fetch_all_prices_async())
        return {
            "status": "success",
            "processed": len(result),
            "results": result
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


async def fetch_watchlist_prices_async():
    """ウォッチリスト銘柄のみ取得"""
    from sqlalchemy import select
    from app.models import Watchlist, Stock
    
    async with AsyncSessionLocal() as db:
        # ウォッチリストにある銘柄を取得
        result = await db.execute(
            select(Stock).join(Watchlist).distinct()
        )
        stocks = result.scalars().all()
        
        service = StockService(db)
        results = []
        
        for stock in stocks:
            try:
                price = await service.fetch_and_save_price(stock.code)
                results.append({
                    "code": stock.code,
                    "success": price is not None
                })
            except Exception as e:
                results.append({
                    "code": stock.code,
                    "success": False,
                    "error": str(e)
                })
        
        return results


@shared_task
def fetch_watchlist_prices():
    """ウォッチリスト銘柄の株価を取得"""
    try:
        result = asyncio.run(fetch_watchlist_prices_async())
        return {
            "status": "success",
            "processed": len(result),
            "results": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
