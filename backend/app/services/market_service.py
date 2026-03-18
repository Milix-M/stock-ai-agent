"""
マーケットデータサービス
"""
from typing import Optional, Dict, Any
import asyncio
import yfinance as yf


class MarketService:
    """マーケットデータサービス"""
    
    def _fetch_nikkei_sync(self) -> Optional[Dict[str, Any]]:
        """同期処理で日経平均を取得"""
        try:
            ticker = yf.Ticker("^N225")
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) >= 2 else latest
            
            change = latest["Close"] - previous["Close"]
            change_percent = (change / previous["Close"]) * 100 if previous["Close"] else 0
            
            return {
                "name": "日経平均株価",
                "code": "N225",
                "current": float(latest["Close"]),
                "change": float(change),
                "change_percent": float(change_percent),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "volume": int(latest["Volume"]) if latest["Volume"] else 0,
            }
        except Exception as e:
            print(f"Error fetching Nikkei 225: {e}")
            return None
    
    def _fetch_topix_sync(self) -> Optional[Dict[str, Any]]:
        """同期処理でTOPIXを取得"""
        try:
            ticker = yf.Ticker("^TOPX")
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) >= 2 else latest
            
            change = latest["Close"] - previous["Close"]
            change_percent = (change / previous["Close"]) * 100 if previous["Close"] else 0
            
            return {
                "name": "TOPIX",
                "code": "TOPX",
                "current": float(latest["Close"]),
                "change": float(change),
                "change_percent": float(change_percent),
            }
        except Exception as e:
            print(f"Error fetching TOPIX: {e}")
            return None
    
    def _fetch_dow_sync(self) -> Optional[Dict[str, Any]]:
        """同期処理でダウ平均を取得"""
        try:
            ticker = yf.Ticker("^DJI")
            hist = ticker.history(period="2d")
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) >= 2 else latest
            
            change = latest["Close"] - previous["Close"]
            change_percent = (change / previous["Close"]) * 100 if previous["Close"] else 0
            
            return {
                "name": "NYダウ",
                "code": "DJI",
                "current": float(latest["Close"]),
                "change": float(change),
                "change_percent": float(change_percent),
            }
        except Exception as e:
            print(f"Error fetching Dow Jones: {e}")
            return None
    
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
            "updated_at": None
        }