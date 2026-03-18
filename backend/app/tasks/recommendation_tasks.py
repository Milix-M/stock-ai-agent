"""
レコメンドタスク
"""
from datetime import datetime
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio
import redis.asyncio as redis

from app.config import get_settings
from app.services.stock_search_service import StockSearchService
from app.services.pattern_service import PatternService
from app.services.watchlist_service import WatchlistService
from app.services.recommendation_service import PatternMatcher
from app.services.notification_service import NotificationService, NotificationPayload
from app.agents import AgentSharedMemory

settings = get_settings()

# 非同期セッション作成用
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Redis接続
redis_client = redis.from_url(settings.REDIS_URL)


async def generate_recommendations_for_pattern(user_id: str, pattern_id: str):
    """
    特定のパターンでレコメンドを生成
    パターン作成時に即座に実行
    検索順位: ウォッチリスト > セクター一致 > 人気銘柄
    """
    async with AsyncSessionLocal() as db:
        # サービス初期化
        pattern_service = PatternService(db)
        stock_search_service = StockSearchService()
        watchlist_service = WatchlistService(db)
        
        # パターン取得
        pattern = await pattern_service.get_pattern_by_id(pattern_id)
        if not pattern:
            return {"status": "error", "message": "Pattern not found"}
        
        # 検索対象銘柄を構築（優先順位付き）
        target_codes = []
        
        # 1. ウォッチリスト銘柄（最優先）
        watchlist_codes = await watchlist_service.get_watchlist_codes(user_id)
        target_codes.extend(watchlist_codes)
        
        # 2. パターンからセクター情報を抽出
        filters = pattern.parsed_filters.get("filters", {})
        target_sectors = filters.get("sectors", [])  # パターンに含まれる業種
        
        # 3. セクターに基づいて銘柄を追加
        if target_sectors:
            sector_codes = [
                s["code"] for s in stock_search_service._popular_stocks
                if s.get("sector") in target_sectors and s["code"] not in target_codes
            ]
            target_codes.extend(sector_codes)
        
        # 4. 人気銘柄をフォールバックとして追加
        popular_codes = [
            s["code"] for s in stock_search_service._popular_stocks
            if s["code"] not in target_codes
        ]
        target_codes.extend(popular_codes)
        
        # 重複排除（順序保持）
        seen = set()
        unique_codes = []
        for code in target_codes:
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)
        
        results = []
        for code in unique_codes:
            try:
                # 株価データ取得
                price_data = await stock_search_service.get_price_data(code)
                if not price_data:
                    continue
                
                # パターンフィルタで評価
                filters = pattern.parsed_filters.get("filters", {})
                score = 0
                matched = []
                
                # PER評価
                if "per_max" in filters and price_data.get("per"):
                    if price_data["per"] <= filters["per_max"]:
                        score += 1
                        matched.append(f"PER: {price_data['per']:.1f}倍")
                
                # PBR評価
                if "pbr_max" in filters and price_data.get("pbr"):
                    if price_data["pbr"] <= filters["pbr_max"]:
                        score += 1
                        matched.append(f"PBR: {price_data['pbr']:.1f}倍")
                
                # 配当利回り評価（yfinanceは%単位で返すことがあるため、適切に処理）
                if "dividend_yield_min" in filters and price_data.get("dividend_yield"):
                    # yfinanceは配当利回りを%単位（例：2.5）または配当額で返す場合がある
                    dividend_yield = price_data["dividend_yield"]
                    # 100以上の値は配当額とみなして利回りに変換（概算）
                    if dividend_yield > 100:
                        dividend_yield = (dividend_yield / price_data.get("current_price", 1)) * 100
                    if dividend_yield >= filters["dividend_yield_min"]:
                        score += 1
                        matched.append(f"配当: {dividend_yield:.1f}%")
                
                # スコアが1以上あればレコメンド（条件が少ないパターンにも対応）
                if score >= 1:
                    stock_info = await stock_search_service.get_stock_info(code)
                    results.append({
                        "stock_code": code,
                        "stock_name": stock_info.name if stock_info else code,
                        "pattern_name": pattern.name,
                        "match_score": min(score / 3, 1.0),  # 最大3項目で正規化
                        "matched_criteria": matched,
                        "current_price": price_data.get("current_price"),
                        "change_percent": price_data.get("change_percent"),
                        "reason": f"{stock_info.name if stock_info else code}は{pattern.name}に適合（{', '.join(matched)}）"
                    })
                    
            except Exception as e:
                print(f"Error evaluating {code}: {e}")
                continue
        
        # スコア順にソート
        results.sort(key=lambda x: x["match_score"], reverse=True)
        top_results = results[:5]  # 上位5件
        
        # Redisにキャッシュ
        cache_key = f"recommendations:{user_id}:{pattern_id}"
        await redis_client.setex(
            cache_key,
            3600,  # 1時間
            str({
                "pattern_name": pattern.name,
                "recommendations": top_results,
                "total_matches": len(results),
                "generated_at": datetime.now().isoformat()
            })
        )
        
        # レコメンドがある場合、プッシュ通知
        if top_results:
            try:
                notification_service = NotificationService(db)
                payload = NotificationPayload(
                    title=f"💡 新しいレコメンド: {pattern.name}",
                    body=f"{top_results[0]['stock_name']}など{len(top_results)}件の銘柄がマッチしました",
                    data={
                        "type": "new_recommendations",
                        "pattern_id": pattern_id,
                        "pattern_name": pattern.name,
                        "count": len(top_results)
                    }
                )
                await notification_service.send_notification(user_id, payload)
            except Exception as e:
                print(f"Notification failed: {e}")
        
        return {
            "status": "success",
            "pattern_id": pattern_id,
            "pattern_name": pattern.name,
            "recommendations_count": len(top_results),
            "recommendations": top_results
        }


async def generate_all_recommendations(user_id: str):
    """ユーザーの全パターンでレコメンドを生成"""
    async with AsyncSessionLocal() as db:
        pattern_service = PatternService(db)
        patterns = await pattern_service.get_active_patterns(user_id)
        
        all_results = []
        for pattern in patterns:
            result = await generate_recommendations_for_pattern(user_id, str(pattern.id))
            if result.get("status") == "success":
                all_results.extend(result.get("recommendations", []))
        
        # 重複排除（同じ銘柄が複数パターンにマッチする場合）
        seen = set()
        unique_results = []
        for r in all_results:
            if r["stock_code"] not in seen:
                seen.add(r["stock_code"])
                unique_results.append(r)
        
        # スコア順にソート
        unique_results.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "status": "success",
            "recommendations": unique_results[:10],
            "total_patterns": len(patterns)
        }


@shared_task(bind=True, max_retries=3)
def generate_daily_recommendations(self, user_id: str = None):
    """
    日次レコメンド生成タスク（Celery）
    """
    try:
        if user_id:
            result = asyncio.run(generate_all_recommendations(user_id))
            return result
        else:
            return {
                "status": "batch_scheduled",
                "message": "Batch recommendation generation scheduled"
            }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task
def generate_recommendations_task(user_id: str, pattern_id: str = None):
    """
    レコメンド生成タスク
    pattern_id指定時はそのパターンのみ、未指定時は全パターン
    """
    try:
        if pattern_id:
            result = asyncio.run(generate_recommendations_for_pattern(user_id, pattern_id))
        else:
            result = asyncio.run(generate_all_recommendations(user_id))
        return result
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }