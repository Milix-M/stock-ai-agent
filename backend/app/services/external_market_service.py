"""
外部APIマーケットデータサービス
Alpha Vantage等のサードパーティAPIを使用
"""
from typing import Optional, Dict, Any
import httpx
import os
from datetime import datetime


class ExternalMarketService:
    """外部APIを使用したマーケットデータサービス"""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    async def _fetch_alpha_vantage(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Alpha Vantageからデータを取得"""
        if not self.alpha_vantage_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "function": "GLOBAL_QUOTE",
                        "symbol": symbol,
                        "apikey": self.alpha_vantage_key
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                quote = data.get("Global Quote", {})
                
                if not quote:
                    return None
                
                return {
                    "current": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": float(quote.get("10. change percent", "0%").replace("%", "")),
                    "volume": int(quote.get("06. volume", 0)),
                }
        except Exception as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            return None
    
    async def get_nikkei_225(self) -> Optional[Dict[str, Any]]:
        """日経平均を取得"""
        # Alpha Vantageのシンボル: N225
        data = await self._fetch_alpha_vantage("N225")
        
        if data:
            return {
                "name": "日経平均株価",
                "code": "N225",
                **data
            }
        return None
    
    async def get_dow_jones(self) -> Optional[Dict[str, Any]]:
        """ダウ平均を取得"""
        # Alpha Vantageのシンボル: DJI
        data = await self._fetch_alpha_vantage("DJI")
        
        if data:
            return {
                "name": "NYダウ",
                "code": "DJI",
                **data
            }
        return None
    
    async def get_sp500(self) -> Optional[Dict[str, Any]]:
        """S&P500を取得"""
        # Alpha Vantageのシンボル: SPX
        data = await self._fetch_alpha_vantage("SPX")
        
        if data:
            return {
                "name": "S&P500",
                "code": "SPX",
                **data
            }
        return None