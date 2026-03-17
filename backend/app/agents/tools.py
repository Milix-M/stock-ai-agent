from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass

from app.services.stock_service import StockService


@dataclass
class StockAlert:
    """株価アラート"""
    stock_code: str
    stock_name: str
    alert_type: str  # "price_change" | "volume_surge" | "ma_cross"
    severity: str    # "info" | "warning" | "critical"
    message: str
    current_value: float
    threshold: float


class AgentTools:
    """エージェントが使用するツール集"""
    
    def __init__(self, stock_service: StockService):
        self.stock_service = stock_service
    
    async def fetch_stock_price(self, code: str) -> Optional[dict]:
        """株価を取得"""
        stock = await self.stock_service.get_stock_by_code(code)
        if not stock:
            return None
        
        price = await self.stock_service.get_latest_price(stock.id)
        if not price:
            return None
        
        return {
            "code": code,
            "name": stock.name,
            "close": float(price.close),
            "open": float(price.open) if price.open else None,
            "high": float(price.high) if price.high else None,
            "low": float(price.low) if price.low else None,
            "volume": price.volume,
            "date": price.date.isoformat() if price.date else None
        }
    
    async def check_price_threshold(self, code: str, threshold_percent: float) -> Optional[StockAlert]:
        """
        価格変動閾値をチェック
        threshold_percent: 閾値(%)、例: 5.0 = ±5%
        """
        stock = await self.stock_service.get_stock_by_code(code)
        if not stock:
            return None
        
        # 最新2日分の価格を取得
        prices = await self.stock_service.get_stock_prices(stock.id, days=2)
        if len(prices) < 2:
            return None
        
        latest = prices[0]
        previous = prices[1]
        
        change_percent = ((latest.close - previous.close) / previous.close) * 100
        
        if abs(change_percent) >= threshold_percent:
            severity = "critical" if abs(change_percent) >= 10 else "warning"
            direction = "上昇" if change_percent > 0 else "下落"
            
            return StockAlert(
                stock_code=code,
                stock_name=stock.name,
                alert_type="price_change",
                severity=severity,
                message=f"前日比{change_percent:.1f}%の{direction}（閾値: ±{threshold_percent}%）",
                current_value=float(latest.close),
                threshold=threshold_percent
            )
        
        return None
    
    async def detect_volume_surge(self, code: str, ratio: float = 2.0) -> Optional[StockAlert]:
        """
        出来高急増を検知
        ratio: 平均に対する倍率、例: 2.0 = 平均の2倍以上
        """
        stock = await self.stock_service.get_stock_by_code(code)
        if not stock:
            return None
        
        # 過去20日分の平均出来高を計算
        prices = await self.stock_service.get_stock_prices(stock.id, days=20)
        if len(prices) < 5:
            return None
        
        avg_volume = sum(p.volume for p in prices[1:]) / len(prices[1:])  # 最新除く
        latest = prices[0]
        
        if avg_volume > 0 and latest.volume >= avg_volume * ratio:
            return StockAlert(
                stock_code=code,
                stock_name=stock.name,
                alert_type="volume_surge",
                severity="warning",
                message=f"出来高急増: 平均の{latest.volume/avg_volume:.1f}倍（{latest.volume:,}株）",
                current_value=float(latest.volume),
                threshold=ratio
            )
        
        return None
    
    async def detect_moving_average_cross(
        self, 
        code: str, 
        short_window: int = 5, 
        long_window: int = 20
    ) -> Optional[StockAlert]:
        """
        移動平均線クロスを検知（ゴールデン/デッドクロス）
        """
        stock = await self.stock_service.get_stock_by_code(code)
        if not stock:
            return None
        
        prices = await self.stock_service.get_stock_prices(stock.id, days=long_window + 5)
        if len(prices) < long_window + 1:
            return None
        
        # 終値のリスト（古い順）
        closes = [float(p.close) for p in reversed(prices)]
        
        # 移動平均を計算
        short_ma_current = sum(closes[-short_window:]) / short_window
        long_ma_current = sum(closes[-long_window:]) / long_window
        
        short_ma_prev = sum(closes[-(short_window+1):-1]) / short_window
        long_ma_prev = sum(closes[-(long_window+1):-1]) / long_window
        
        # クロス検知
        if short_ma_prev <= long_ma_prev and short_ma_current > long_ma_current:
            # ゴールデンクロス
            return StockAlert(
                stock_code=code,
                stock_name=stock.name,
                alert_type="ma_cross",
                severity="info",
                message=f"ゴールデンクロス: {short_window}日MAが{long_window}日MAを上抜け",
                current_value=float(prices[0].close),
                threshold=long_window
            )
        elif short_ma_prev >= long_ma_prev and short_ma_current < long_ma_current:
            # デッドクロス
            return StockAlert(
                stock_code=code,
                stock_name=stock.name,
                alert_type="ma_cross",
                severity="info",
                message=f"デッドクロス: {short_window}日MAが{long_window}日MAを下抜け",
                current_value=float(prices[0].close),
                threshold=long_window
            )
        
        return None
    
    async def get_watchlist_codes(self, user_id: str) -> List[str]:
        """ユーザーのウォッチリスト銘柄コードを取得"""
        from sqlalchemy import select
        from app.models import Watchlist, Stock
        from sqlalchemy.ext.asyncio import AsyncSession
        
        # Note: This requires db session access, should be passed in constructor
        # For now, return empty list - will need proper implementation
        return []
