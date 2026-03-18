"""
マーケットデータサービス
yfinanceを使用して実際の市場データを取得（リクエスト間隔付き）
"""
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

import yfinance as yf
import pandas as pd


class MarketService:
    """マーケットデータサービス"""
    
    # リクエスト間隔（秒）- 429エラー回避
    REQUEST_DELAY = 3
    
    async def _fetch_with_delay(self, ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """yfinanceでデータを取得（遅延付き）"""
        def _fetch():
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period='2d')
                
                if hist.empty or len(hist) < 2:
                    return None
                
                latest = hist.iloc[-1]
                previous = hist.iloc[-2]
                
                change = latest['Close'] - previous['Close']
                change_percent = (change / previous['Close']) * 100
                
                return {
                    'current': round(latest['Close'], 2),
                    'change': round(change, 2),
                    'change_percent': round(change_percent, 2),
                    'volume': int(latest['Volume']) if pd.notna(latest.get('Volume')) else 0,
                }
            except Exception as e:
                print(f"Error fetching {ticker_symbol}: {e}")
                return None
        
        result = await asyncio.to_thread(_fetch)
        
        # リクエスト間隔を空ける
        await asyncio.sleep(self.REQUEST_DELAY)
        
        return result
    
    async def get_nikkei_225(self) -> Optional[Dict[str, Any]]:
        """日経平均株価を取得"""
        data = await self._fetch_with_delay('^N225')
        
        if data:
            return {
                'name': '日経平均株価',
                'code': 'N225',
                **data
            }
        return None
    
    async def get_dow_jones(self) -> Optional[Dict[str, Any]]:
        """NYダウを取得"""
        data = await self._fetch_with_delay('^DJI')
        
        if data:
            return {
                'name': 'NYダウ',
                'code': 'DJI',
                **data
            }
        return None
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """マーケット概況を一括取得（順次実行）"""
        # 順番に取得（同時リクエストを避ける）
        nikkei = await self.get_nikkei_225()
        dow = await self.get_dow_jones()
        
        return {
            'indices': {
                'nikkei_225': nikkei,
                'dow_jones': dow,
            },
            'updated_at': datetime.now().isoformat(),
            'data_source': 'yahoo_finance'
        }