"""
マーケットデータサービス
"""
from typing import Optional, Dict, Any
import asyncio
import yfinance as yf
import pandas as pd
from datetime import datetime


class MarketService:
    """マーケットデータサービス"""
    
    # フォールバックデータ（開発用・API失敗時）
    _fallback_data = {
        "nikkei_225": {
            "name": "日経平均株価",
            "code": "N225",
            "current": 36888.00,
            "change": 150.50,
            "change_percent": 0.41,
            "open": 36750.00,
            "high": 36950.00,
            "low": 36700.00,
            "volume": 1200000000,
            "is_fallback": True
        },
        "topix": {
            "name": "TOPIX",
            "code": "TOPX",
            "current": 2550.50,
            "change": 8.20,
            "change_percent": 0.32,
            "is_fallback": True
        },
        "dow_jones": {
            "name": "NYダウ",
            "code": "DJI",
            "current": 38714.00,
            "change": -35.20,
            "change_percent": -0.09,
            "is_fallback": True
        }
    }
    
    def _fetch_ticker_sync(self, symbol: str) -> Optional[Dict[str, Any]]:
        """同期処理でティッカー取得"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if hist.empty:
                print(f"No data for {symbol}")
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) >= 2 else latest
            
            change = latest["Close"] - previous["Close"]
            change_percent = (change / previous["Close"]) * 100 if previous["Close"] != 0 else 0
            
            return {
                "current": float(latest["Close"]),
                "change": float(change),
                "change_percent": float(change_percent),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "volume": int(latest["Volume"]) if not pd.isna(latest["Volume"]) else 0,
            }
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def _fetch_nikkei_sync(self) -> Optional[Dict[str, Any]]:
        """同期処理で日経平均を取得"""
        result = self._fetch_ticker_sync("^N225")
        if result:
            return {
                **result,
                "name": "日経平均株価",
                "code": "N225",
            }
        
        # フォールバック
        return self._fallback_data["nikkei_225"]
    
    def _fetch_topix_sync(self) -> Optional[Dict[str, Any]]:
        """同期処理でTOPIXを取得"""
        result = self._fetch_ticker_sync("^TOPX")
        if result:
            return {
                **result,
                "name": "TOPIX",
                "code": "TOPX",
            }
        
        return self._fallback_data["topix"]
    
    def _fetch_dow_sync(self) -> Optional[Dict[str, Any]]:
        """同期処理でダウ平均を取得"""
        result = self._fetch_ticker_sync("^DJI")
        if result:
            return {
                **result,
                "name": "NYダウ",
                "code": "DJI",
            }
        
        return self._fallback_data["dow_jones"]
    
    async def get_nikkei_225(self) -> Optional[Dict[str, Any]]:
        """日経平均株価を取得（非同期）"""
        return await asyncio.to_thread(self._fetch_nikkei_sync)
    
    async def get_topix(self) -> Optional[Dict[str, Any]]:
        """TOPIXを取得（非同期）"""
        return await asyncio.to_thread(self._fetch_topix_sync)
    
    async def get_dow_jones(self) -> Optional[Dict[str, Any]]:
        """ダウ平均を取得（非同期）"""
        return await asyncio.to_thread(self._fetch_dow_sync)
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """マーケット概況を一括取得（並列）"""
        # 並列で取得（タイムアウト付き）
        try:
            nikkei_task = asyncio.create_task(
                asyncio.wait_for(self.get_nikkei_225(), timeout=10.0)
            )
            topix_task = asyncio.create_task(
                asyncio.wait_for(self.get_topix(), timeout=10.0)
            )
            dow_task = asyncio.create_task(
                asyncio.wait_for(self.get_dow_jones(), timeout=10.0)
            )
            
            nikkei = await nikkei_task
            topix = await topix_task
            dow = await dow_task
            
        except asyncio.TimeoutError:
            print("Market data fetch timeout, using fallback")
            nikkei = self._fallback_data["nikkei_225"]
            topix = self._fallback_data["topix"]
            dow = self._fallback_data["dow_jones"]
        
        return {
            "indices": {
                "nikkei_225": nikkei,
                "topix": topix,
                "dow_jones": dow,
            },
            "updated_at": datetime.now().isoformat(),
            "data_source": "yahoo_fallback" if (nikkei and nikkei.get("is_fallback")) else "yahoo"
        }