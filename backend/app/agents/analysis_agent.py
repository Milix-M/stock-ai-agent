"""
分析エージェント
ニュース・決算・テクニカル分析を実行
"""
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pydantic_ai import Agent, Tool
from pydantic_ai.result import RunResult

from app.agents.base import BaseAgent
from app.config import get_settings
from app.services.news_service import NewsService
from app.services.financial_service import FinancialService
from app.services.technical_service import TechnicalAnalysisService
from app.services.stock_service import StockService

settings = get_settings()


class NewsAnalysis(BaseModel):
    """ニュース分析結果"""
    sentiment: str  # "positive" | "negative" | "neutral"
    sentiment_score: float  # -1.0 ～ 1.0
    key_topics: List[str]
    risk_factors: List[str]
    opportunities: List[str]


class FinancialAnalysis(BaseModel):
    """財務分析結果"""
    revenue_trend: str  # "growing" | "declining" | "stable"
    profitability: str  # "high" | "medium" | "low"
    financial_health: str  # "strong" | "moderate" | "weak"
    valuation: str  # "undervalued" | "fair" | "overvalued"
    key_metrics: Dict[str, Any]


class TechnicalAnalysis(BaseModel):
    """テクニカル分析結果"""
    trend: str  # "uptrend" | "downtrend" | "sideways"
    momentum: str  # "strong" | "weak" | "neutral"
    volatility: str  # "high" | "medium" | "low"
    signals: List[str]
    support_levels: List[float]
    resistance_levels: List[float]


class StockAnalysisResult(BaseModel):
    """銘柄分析結果"""
    stock_code: str
    stock_name: str
    analysis_date: str
    overall_rating: str  # "buy" | "hold" | "sell"
    confidence_score: float  # 0.0 ～ 1.0
    
    # 各分析結果
    news_analysis: Optional[NewsAnalysis] = None
    financial_analysis: Optional[FinancialAnalysis] = None
    technical_analysis: Optional[TechnicalAnalysis] = None
    
    # サマリー
    summary: str
    key_points: List[str]
    risks: List[str]
    recommendations: List[str]


# APIキーの設定
# OpenAIとOpenRouterの両方をサポート
_api_key = None
if settings.LLM_PROVIDER == "openai":
    _api_key = settings.OPENAI_API_KEY
elif settings.LLM_PROVIDER == "openrouter":
    _api_key = settings.OPENROUTER_API_KEY
    # OpenRouterの場合は環境変数を設定
    import os
    os.environ['OPENAI_API_KEY'] = _api_key

# モデル名と設定の設定
if settings.LLM_PROVIDER == "openai":
    _model = "openai:gpt-4o-mini"
    _model_settings = None
elif settings.LLM_PROVIDER == "openrouter":
    # OpenRouterのモデル名とbase_url
    _model = "anthropic/claude-3.5-sonnet"
    _model_settings = {
        "base_url": "https://openrouter.ai/api/v1"
    }
else:
    _model = "openai:gpt-4o-mini"
    _model_settings = None

# PydanticAIエージェント定義
analysis_agent = Agent(
    model=_model,
    result_type=StockAnalysisResult,
    model_settings=_model_settings,  # OpenRouterの場合はbase_urlを設定
    system_prompt="""
    あなたは株式分析の専門家です。
    提供されたデータに基づいて、銘柄の包括的な分析を行ってください。
    
    分析観点：
    1. ニュース・市場センチメント
    2. 財務状況・業績トレンド
    3. テクニカル指標・価格動向
    
    出力は以下の形式で行ってください：
    - overall_rating: "buy", "hold", "sell"のいずれか
    - confidence_score: 0.0～1.0の確信度
    - summary: 分析サマリー（3-4文）
    - key_points: 重要ポイント（3-5項目）
    - risks: リスク要因（2-3項目）
    - recommendations: 推奨アクション（1-2項目）
    
    客観的なデータに基づき、過度な推奨は避けてください。
    """
)


class AnalysisAgent(BaseAgent[StockAnalysisResult]):
    """分析エージェント実装"""
    
    def __init__(
        self,
        stock_service: StockService,
        news_service: NewsService,
        financial_service: FinancialService,
        technical_service: TechnicalAnalysisService
    ):
        super().__init__(analysis_agent)
        self.stock_service = stock_service
        self.news_service = news_service
        self.financial_service = financial_service
        self.technical_service = technical_service
    
    @Tool
    async def fetch_stock_price(self, code: str) -> dict:
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
    
    @Tool
    async def analyze_news_sentiment(self, query: str) -> dict:
        """ニュースの感情分析"""
        news_articles = await self.news_service.search_news(query, days=7, max_results=10)
        
        if not news_articles:
            return {"sentiment": "neutral", "score": 0.0}
        
        # 簡易的なセンチメント分析
        sentiments = []
        for article in news_articles:
            if hasattr(article, 'sentiment'):
                sentiments.append(article.sentiment)
        
        positive = sentiments.count("positive")
        negative = sentiments.count("negative")
        total = len(sentiments)
        
        if total > 0:
            score = (positive - negative) / total
        else:
            score = 0.0
        
        sentiment = "neutral"
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        
        return {
            "sentiment": sentiment,
            "score": score,
            "article_count": total
        }
    
    @Tool
    async def check_financial_health(self, stock_code: str) -> dict:
        """財務健全性を確認"""
        financial = await self.financial_service.get_financial_data(stock_code)
        if not financial:
            return {"health": "unknown"}
        
        health = "moderate"
        if financial.total_assets and financial.equity:
            equity_ratio = financial.equity / financial.total_assets
            if equity_ratio > 0.5:
                health = "strong"
            elif equity_ratio < 0.3:
                health = "weak"
        
        return {
            "health": health,
            "equity_ratio": equity_ratio if financial.total_assets and financial.equity else None
        }
    
    @Tool
    async def analyze_technical_trend(self, stock_code: str) -> dict:
        """テクニカルトレンド分析"""
        prices = await self.stock_service.get_stock_prices_by_code(stock_code, days=60)
        if len(prices) < 20:
            return {"trend": "unknown"}
        
        closes = [float(p.close) for p in prices]
        
        # 5日・20日移動平均
        sma_5 = sum(closes[-5:]) / 5
        sma_20 = sum(closes[-20:]) / 20
        
        trend = "sideways"
        if sma_5 > sma_20 * 1.02:
            trend = "uptrend"
        elif sma_5 < sma_20 * 0.98:
            trend = "downtrend"
        
        return {
            "trend": trend,
            "sma_5": sma_5,
            "sma_20": sma_20
        }
    
    async def run(self, context: dict) -> RunResult[StockAnalysisResult]:
        """
        分析フロー：
        1. 対象銘柄の基本情報取得
        2. ニュース検索・分析
        3. 財務データ確認
        4. テクニカル指標計算
        5. 総合分析レポート生成
        """
        stock_code = context.get("stock_code")
        stock_name = context.get("stock_name")
        user_id = context.get("user_id")
        
        if not stock_code:
            raise ValueError("stock_code is required")
        
        # PydanticAIエージェント実行
        result = await analysis_agent.run(
            context={
                "stock_code": stock_code,
                "stock_name": stock_name,
                "user_id": user_id
            }
        )
        
        return result
