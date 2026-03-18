"""
銘柄検索サービス - yfinanceを使用
"""
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd
from dataclasses import dataclass


@dataclass
class StockSearchResult:
    """銘柄検索結果"""
    code: str
    name: str
    market: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None


class StockSearchService:
    """銘柄検索サービス（yfinance使用）"""
    
    # 主要銘柄のキャッシュ（簡易的）
    _popular_stocks = [
        {"code": "7203", "name": "トヨタ自動車", "market": "東証プライム", "sector": "輸送用機器"},
        {"code": "6758", "name": "ソニーグループ", "market": "東証プライム", "sector": "電気機器"},
        {"code": "9984", "name": "ソフトバンクグループ", "market": "東証プライム", "sector": "情報・通信"},
        {"code": "8306", "name": "三菱UFJフィナンシャル・グループ", "market": "東証プライム", "sector": "銀行"},
        {"code": "6861", "name": "キーエンス", "market": "東証プライム", "sector": "電気機器"},
        {"code": "8058", "name": "三菱商事", "market": "東証プライム", "sector": "卸売"},
        {"code": "9432", "name": "日本電信電話", "market": "東証プライム", "sector": "情報・通信"},
        {"code": "6098", "name": "リクルートホールディングス", "market": "東証プライム", "sector": "サービス"},
        {"code": "4523", "name": "エーザイ", "market": "東証プライム", "sector": "医薬品"},
        {"code": "8035", "name": "東京エレクトロン", "market": "東証プライム", "sector": "電気機器"},
        {"code": "2914", "name": "日本たばこ産業", "market": "東証プライム", "sector": "食料品"},
        {"code": "4063", "name": "信越化学工業", "market": "東証プライム", "sector": "化学"},
        {"code": "7267", "name": "本田技研工業", "market": "東証プライム", "sector": "輸送用機器"},
        {"code": "6178", "name": "日本郵政", "market": "東証スタンダード", "sector": "郵便"},
        {"code": "5108", "name": "ブリヂストン", "market": "東証プライム", "sector": "ゴム製品"},
        {"code": "7741", "name": "HOYA", "market": "東証プライム", "sector": "精密機器"},
        {"code": "8001", "name": "伊藤忠商事", "market": "東証プライム", "sector": "卸売"},
        {"code": "4452", "name": "花王", "market": "東証プライム", "sector": "化学"},
        {"code": "4607", "name": "中外製薬", "market": "東証プライム", "sector": "医薬品"},
        {"code": "4661", "name": "オリエンタルランド", "market": "東証プライム", "sector": "サービス"},
        {"code": "8766", "name": "東京海上ホールディングス", "market": "東証プライム", "sector": "保険"},
        {"code": "9020", "name": "東日本旅客鉄道", "market": "東証プライム", "sector": "鉄道・バス"},
        {"code": "9433", "name": "KDDI", "market": "東証プライム", "sector": "情報・通信"},
        {"code": "4502", "name": "武田薬品工業", "market": "東証プライム", "sector": "医薬品"},
        {"code": "6752", "name": "パナソニックホールディングス", "market": "東証プライム", "sector": "電気機器"},
    ]
    
    async def search(self, query: str, limit: int = 20) -> List[StockSearchResult]:
        """
        銘柄を検索
        まず人気銘柄リストから検索し、ヒットしなければyfinanceを試行
        """
        results = []
        query_lower = query.lower()
        
        # 人気銘柄リストから検索
        for stock in self._popular_stocks:
            if (query_lower in stock["code"].lower() or 
                query_lower in stock["name"].lower()):
                results.append(StockSearchResult(**stock))
            
            if len(results) >= limit:
                break
        
        # ヒットしなければyfinanceで試行（数字4桁の場合）
        if len(results) == 0 and query.isdigit() and len(query) == 4:
            try:
                ticker = yf.Ticker(f"{query}.T")
                info = ticker.info
                
                if info and info.get("longName"):
                    results.append(StockSearchResult(
                        code=query,
                        name=info.get("longName", query),
                        market="東証",
                        sector=info.get("sector"),
                        industry=info.get("industry")
                    ))
            except Exception:
                pass  # エラー時は無視
        
        return results[:limit]
    
    async def get_stock_info(self, code: str) -> Optional[StockSearchResult]:
        """
        銘柄コードから情報を取得
        """
        # まずキャッシュから検索
        for stock in self._popular_stocks:
            if stock["code"] == code:
                return StockSearchResult(**stock)
        
        # なければyfinanceで取得
        try:
            ticker = yf.Ticker(f"{code}.T")
            info = ticker.info
            
            if info and info.get("longName"):
                return StockSearchResult(
                    code=code,
                    name=info.get("longName", code),
                    market="東証",
                    sector=info.get("sector"),
                    industry=info.get("industry")
                )
        except Exception:
            pass
        
        return None
    
    async def get_price_data(self, code: str) -> Optional[Dict[str, Any]]:
        """
        yfinanceからリアルタイム株価データを取得
        """
        try:
            ticker = yf.Ticker(f"{code}.T")
            
            # 最新データを取得
            hist = ticker.history(period="2d")
            info = ticker.info
            
            if hist.empty:
                return None
            
            latest = hist.iloc[-1]
            previous = hist.iloc[-2] if len(hist) >= 2 else latest
            
            change = latest["Close"] - previous["Close"]
            change_percent = (change / previous["Close"]) * 100 if previous["Close"] else 0
            
            return {
                "code": code,
                "current_price": float(latest["Close"]),
                "open": float(latest["Open"]),
                "high": float(latest["High"]),
                "low": float(latest["Low"]),
                "volume": int(latest["Volume"]),
                "change": float(change),
                "change_percent": float(change_percent),
                "per": info.get("trailingPE"),
                "pbr": info.get("priceToBook"),
                "dividend_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None,
                "market_cap": info.get("marketCap"),
            }
            
        except Exception as e:
            print(f"Error fetching price for {code}: {e}")
            return None
    
    async def get_historical_prices(self, code: str, period: str = "1mo") -> Optional[List[Dict]]:
        """
        過去の株価データを取得
        """
        try:
            ticker = yf.Ticker(f"{code}.T")
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            prices = []
            for date, row in hist.iterrows():
                prices.append({
                    "date": date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                })
            
            return prices
            
        except Exception as e:
            print(f"Error fetching historical prices for {code}: {e}")
            return None