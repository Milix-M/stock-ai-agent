"""
マーケットデータサービス
yfinanceを使用して実際の市場データを取得（キャッシュ付き）
"""
from typing import Optional, Dict, Any
import asyncio
from datetime import datetime

import yfinance as yf
import pandas as pd
import redis.asyncio as redis

from app.config import get_settings

settings = get_settings()


class MarketService:
    """マーケットデータサービス"""
    
    # リクエスト間隔（秒）- 429エラー回避
    REQUEST_DELAY = 3
    # キャッシュ有効期限（秒）- 30秒
    CACHE_TTL = 30
    
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
    
    async def _get_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Redisからキャッシュ取得"""
        try:
            cached = await self.redis.get(key)
            if cached:
                import json
                return json.loads(cached)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    async def _set_cache(self, key: str, data: Dict[str, Any]):
        """Redisにキャッシュ保存"""
        try:
            import json
            await self.redis.setex(
                key,
                self.CACHE_TTL,
                json.dumps(data)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
    
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
        """日経平均株価を取得（キャッシュ付き）"""
        cache_key = "market:nikkei_225"
        
        # キャッシュ確認
        cached = await self._get_cache(cache_key)
        if cached:
            return cached
        
        # キャッシュミス時はyfinanceから取得
        data = await self._fetch_with_delay('^N225')
        
        if data:
            result = {
                'name': '日経平均株価',
                'code': 'N225',
                **data
            }
            # キャッシュ保存
            await self._set_cache(cache_key, result)
            return result
        return None
    
    async def get_dow_jones(self) -> Optional[Dict[str, Any]]:
        """NYダウを取得（キャッシュ付き）"""
        cache_key = "market:dow_jones"
        
        # キャッシュ確認
        cached = await self._get_cache(cache_key)
        if cached:
            return cached
        
        # キャッシュミス時はyfinanceから取得
        data = await self._fetch_with_delay('^DJI')
        
        if data:
            result = {
                'name': 'NYダウ',
                'code': 'DJI',
                **data
            }
            # キャッシュ保存
            await self._set_cache(cache_key, result)
            return result
        return None
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """マーケット概況を一括取得（キャッシュ付き）"""
        cache_key = "market:overview"
        
        # キャッシュ確認
        cached = await self._get_cache(cache_key)
        if cached:
            cached['cached'] = True
            return cached
        
        # キャッシュミス時は取得
        nikkei = await self.get_nikkei_225()
        dow = await self.get_dow_jones()
        
        result = {
            'indices': {
                'nikkei_225': nikkei,
                'dow_jones': dow,
            },
            'updated_at': datetime.now().isoformat(),
            'data_source': 'yahoo_finance'
        }
        
        # キャッシュ保存
        await self._set_cache(cache_key, result)
        
        return result