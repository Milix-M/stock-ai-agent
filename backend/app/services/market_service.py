"""
マーケットデータサービス
実際の個別株データからマーケットデータを計算
"""
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime

import yfinance as yf

from app.services.stock_search_service import StockSearchService


class MarketService:
    """マーケットデータサービス"""
    
    # 日経平均に相当する主要銘柄
    NIKKEI_BLUE_CHIPS = [
        "7203",  # トヨタ
        "6758",  # ソニー
        "9984",  # ソフトバンク
        "8306",  # 三菱UFJ
        "6861",  # キーエンス
    ]
    
    # NYダウに相当する主要銘柄（ADR）
    DOW_COMPONENTS = [
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "JPM",   # JPMorgan
        "V",     # Visa
        "JNJ",   # Johnson & Johnson
    ]
    
    async def _calculate_market_index(
        self, 
        symbols: List[str], 
        name: str, 
        code: str
    ) -> Optional[Dict[str, Any]]:
        """
        個別株の変動率からマーケットインデックスを計算
        """
        stock_service = StockSearchService()
        
        total_change_percent = 0
        valid_count = 0
        total_volume = 0
        
        for symbol in symbols:
            try:
                price_data = await stock_service.get_price_data(symbol)
                if price_data and price_data.get("change_percent") is not None:
                    total_change_percent += price_data["change_percent"]
                    valid_count += 1
                    if price_data.get("volume"):
                        total_volume += price_data["volume"]
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        
        if valid_count == 0:
            return None
        
        # 平均変動率を計算
        avg_change_percent = total_change_percent / valid_count
        
        # 前日比を計算（仮想的な前日終値から）
        base_value = 37000 if code == "N225" else 39000  # 概算の基準値
        change = base_value * (avg_change_percent / 100)
        current = base_value + change
        
        return {
            "name": name,
            "code": code,
            "current": round(current, 2),
            "change": round(change, 2),
            "change_percent": round(avg_change_percent, 2),
            "volume": total_volume,
            "based_on": f"{valid_count} stocks"  # 計算元の銘柄数
        }
    
    async def get_nikkei_225(self) -> Optional[Dict[str, Any]]:
        """日経平均株価を取得（実際の株価から計算）"""
        return await self._calculate_market_index(
            self.NIKKEI_BLUE_CHIPS,
            "日経平均株価（推定）",
            "N225"
        )
    
    async def get_topix(self) -> Optional[Dict[str, Any]]:
        """TOPIXを取得（日経平均と同じ銘柄で計算）"""
        data = await self._calculate_market_index(
            self.NIKKEI_BLUE_CHIPS,
            "TOPIX（推定）",
            "TOPX"
        )
        if data:
            # TOPIXは日経より値が小さい
            data["current"] = round(data["current"] / 14.5, 2)  # 概算の換算
        return data
    
    async def get_dow_jones(self) -> Optional[Dict[str, Any]]:
        """ダウ平均を取得（実際の株価から計算）"""
        stock_service = StockSearchService()
        
        total_change_percent = 0
        valid_count = 0
        
        for symbol in self.DOW_COMPONENTS:
            try:
                # yfinanceは米国株も対応
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty and len(hist) >= 2:
                    latest = hist.iloc[-1]["Close"]
                    previous = hist.iloc[-2]["Close"]
                    change_pct = ((latest - previous) / previous) * 100
                    total_change_percent += change_pct
                    valid_count += 1
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                continue
        
        if valid_count == 0:
            return None
        
        avg_change_percent = total_change_percent / valid_count
        base_value = 38700  # 概算の基準値
        change = base_value * (avg_change_percent / 100)
        current = base_value + change
        
        return {
            "name": "NYダウ（推定）",
            "code": "DJI",
            "current": round(current, 2),
            "change": round(change, 2),
            "change_percent": round(avg_change_percent, 2),
            "based_on": f"{valid_count} US stocks"
        }
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """マーケット概況を一括取得"""
        # 並列で取得
        nikkei_task = asyncio.create_task(self.get_nikkei_225())
        topix_task = asyncio.create_task(self.get_topix())
        dow_task = asyncio.create_task(self.get_dow_jones())
        
        nikkei = await nikkei_task
        topix = await topix_task
        dow = await dow_task
        
        return {
            "indices": {
                "nikkei_225": nikkei,
                "topix": topix,
                "dow_jones": dow,
            },
            "updated_at": datetime.now().isoformat(),
            "data_source": "calculated_from_real_stocks"
        }