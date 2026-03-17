from typing import Optional, List
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models import Stock, StockPrice


class StockService:
    """株価データサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_stocks(self) -> List[Stock]:
        """全銘柄を取得"""
        result = await self.db.execute(select(Stock))
        return result.scalars().all()
    
    async def get_stock_by_code(self, code: str) -> Optional[Stock]:
        """銘柄コードで取得"""
        result = await self.db.execute(select(Stock).where(Stock.code == code))
        return result.scalar_one_or_none()
    
    async def search_stocks(self, query: str, limit: int = 20) -> List[Stock]:
        """銘柄を検索"""
        result = await self.db.execute(
            select(Stock)
            .where(
                and_(
                    Stock.code.ilike(f"%{query}%"),
                    Stock.name.ilike(f"%{query}%")
                )
            )
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_stock(self, code: str, name: str, market: Optional[str] = None,
                          sector: Optional[str] = None) -> Stock:
        """銘柄を作成"""
        stock = Stock(
            code=code,
            name=name,
            market=market,
            sector=sector
        )
        self.db.add(stock)
        await self.db.commit()
        await self.db.refresh(stock)
        return stock
    
    async def fetch_and_save_price(self, stock_code: str) -> Optional[StockPrice]:
        """yfinanceから株価を取得して保存"""
        try:
            # 銘柄を取得
            stock = await self.get_stock_by_code(stock_code)
            if not stock:
                return None
            
            # yfinanceで株価取得
            ticker = yf.Ticker(f"{stock_code}.T")  # 東証銘柄
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return None
            
            # 最新データ
            latest = hist.iloc[-1]
            
            # 既存データチェック（同日日付）
            today = datetime.now().date()
            result = await self.db.execute(
                select(StockPrice).where(
                    and_(
                        StockPrice.stock_id == stock.id,
                        StockPrice.date == today
                    )
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # 更新
                existing.open = float(latest['Open'])
                existing.high = float(latest['High'])
                existing.low = float(latest['Low'])
                existing.close = float(latest['Close'])
                existing.volume = int(latest['Volume'])
                existing.adjusted_close = float(latest.get('Adj Close', latest['Close']))
            else:
                # 新規作成
                price = StockPrice(
                    stock_id=stock.id,
                    date=today,
                    open=float(latest['Open']),
                    high=float(latest['High']),
                    low=float(latest['Low']),
                    close=float(latest['Close']),
                    volume=int(latest['Volume']),
                    adjusted_close=float(latest.get('Adj Close', latest['Close']))
                )
                self.db.add(price)
            
            await self.db.commit()
            
            # 銘柄情報も更新（PER, PBR等）
            info = ticker.info
            if info:
                stock.per = info.get('trailingPE')
                stock.pbr = info.get('priceToBook')
                stock.dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else None
                stock.market_cap = info.get('marketCap')
                await self.db.commit()
            
            return existing if existing else price
            
        except Exception as e:
            print(f"Error fetching price for {stock_code}: {e}")
            return None
    
    async def fetch_historical_prices(self, stock_code: str, period: str = "1y") -> List[StockPrice]:
        """過去の株価データを取得・保存"""
        try:
            stock = await self.get_stock_by_code(stock_code)
            if not stock:
                return []
            
            ticker = yf.Ticker(f"{stock_code}.T")
            hist = ticker.history(period=period)
            
            prices = []
            for date, row in hist.iterrows():
                price_date = date.date() if isinstance(date, datetime) else date
                
                # 既存チェック
                result = await self.db.execute(
                    select(StockPrice).where(
                        and_(
                            StockPrice.stock_id == stock.id,
                            StockPrice.date == price_date
                        )
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    existing.open = float(row['Open'])
                    existing.high = float(row['High'])
                    existing.low = float(row['Low'])
                    existing.close = float(row['Close'])
                    existing.volume = int(row['Volume'])
                    existing.adjusted_close = float(row.get('Adj Close', row['Close']))
                    prices.append(existing)
                else:
                    price = StockPrice(
                        stock_id=stock.id,
                        date=price_date,
                        open=float(row['Open']),
                        high=float(row['High']),
                        low=float(row['Low']),
                        close=float(row['Close']),
                        volume=int(row['Volume']),
                        adjusted_close=float(row.get('Adj Close', row['Close']))
                    )
                    self.db.add(price)
                    prices.append(price)
            
            await self.db.commit()
            return prices
            
        except Exception as e:
            print(f"Error fetching historical prices for {stock_code}: {e}")
            return []
    
    async def get_stock_prices(self, stock_id: str, days: int = 30) -> List[StockPrice]:
        """指定日数分の株価データを取得"""
        from_date = datetime.now() - timedelta(days=days)
        
        result = await self.db.execute(
            select(StockPrice)
            .where(
                and_(
                    StockPrice.stock_id == stock_id,
                    StockPrice.date >= from_date
                )
            )
            .order_by(StockPrice.date.desc())
        )
        return result.scalars().all()
    
    async def get_latest_price(self, stock_id: str) -> Optional[StockPrice]:
        """最新の株価を取得"""
        result = await self.db.execute(
            select(StockPrice)
            .where(StockPrice.stock_id == stock_id)
            .order_by(StockPrice.date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    def calculate_price_change(self, current: float, previous: float) -> dict:
        """価格変動を計算"""
        if not previous:
            return {"change": 0, "change_percent": 0}
        
        change = current - previous
        change_percent = (change / previous) * 100
        
        return {
            "change": round(change, 2),
            "change_percent": round(change_percent, 2)
        }
