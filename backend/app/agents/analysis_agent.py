from typing import List, Optional
from pydantic import BaseModel
from pydantic_ai import Agent
from datetime import datetime

from app.agents.base import BaseAgent
from app.agents.tools import StockAlert
from app.services.stock_service import StockService
from app.services.news_service import NewsService
from app.services.technical_service import TechnicalAnalysisService


class AnalysisResult(BaseModel):
    """分析結果の型定義"""
    stock_code: str
    stock_name: str
    analysis_summary: str
    technical_signals: str
    news_sentiment: str
    recommendation: str  # "buy" | "sell" | "hold" | "watch"
    confidence: float  # 0.0 - 1.0
    key_points: List[str]
    risks: List[str]


# PydanticAIエージェント定義
analysis_agent = Agent(
    model="openai:gpt-4o-mini",
    result_type=AnalysisResult,
    system_prompt="""
    あなたは株分析の専門家です。与えられた銘柄データ、テクニカル指標、ニュースを分析し、
    投資判断と根拠を提供してください。
    
    分析の観点：
    1. テクニカル分析: RSI、MACD、移動平均線等の指標
    2. ニュース分析: 最新ニュースの sentiment と影響
    3. リスク評価: 潜在的なリスク要因
    
    推奨アクション：
    - buy: 強く買い推奨
    - sell: 売り推奨
    - hold: 保有推奨
    - watch: 様子見推奨
    
    confidence は 0.0-1.0 で示し、分析の確信度を表してください。
    """
)


class AnalysisAgent(BaseAgent[AnalysisResult]):
    """分析エージェント実装"""
    
    def __init__(
        self,
        stock_service: StockService,
        news_service: NewsService,
        technical_service: TechnicalAnalysisService
    ):
        super().__init__(analysis_agent)
        self.stock_service = stock_service
        self.news_service = news_service
        self.technical_service = technical_service
    
    async def run(self, context: dict):
        """
        分析実行:
        1. 銘柄情報取得
        2. テクニカル分析
        3. ニュース取得・分析
        4. LLMで統合分析
        """
        stock_code = context.get("stock_code")
        alert = context.get("alert")  # 監視エージェントからのアラート
        
        if not stock_code:
            raise ValueError("stock_code is required")
        
        # 銘柄情報取得
        stock = await self.stock_service.get_stock_by_code(stock_code)
        if not stock:
            raise ValueError(f"Stock not found: {stock_code}")
        
        # 価格データ取得（60日分）
        prices = await self.stock_service.get_stock_prices(stock.id, days=60)
        
        # テクニカル分析
        technical = None
        if len(prices) >= 20:
            technical = self.technical_service.analyze(prices)
            technical_signals = self.technical_service.generate_signal(technical)
        else:
            technical_signals = "データ不足"
        
        # ニュース取得・分析
        news_articles = await self.news_service.search_stock_news(
            stock_code=stock_code,
            stock_name=stock.name,
            days=7
        )
        
        # ニュースの感情分析（簡易版）
        news_sentiment = self._analyze_news_sentiment(news_articles)
        
        # 最新価格情報
        latest_price = await self.stock_service.get_latest_price(stock.id)
        current_price = float(latest_price.close) if latest_price else 0
        
        # アラート情報を含めて分析
        alert_info = ""
        if alert:
            alert_info = f"\nアラート: {alert.message} (重要度: {alert.severity})"
        
        # LLMで分析
        result = await self.agent.run(
            f"""
            銘柄: {stock.name} ({stock_code})
            現在価格: {current_price}円
            PER: {stock.per or 'N/A'}
            PBR: {stock.pbr or 'N/A'}
            配当利回り: {stock.dividend_yield or 'N/A'}%
            
            テクニカル指標:
            - RSI: {technical.rsi:.1f} if technical and technical.rsi else 'N/A'}
            - MACD: {technical.macd:.2f} if technical and technical.macd else 'N/A'}
            - SMA5: {technical.sma_5:.0f} if technical and technical.sma_5 else 'N/A'}
            - SMA20: {technical.sma_20:.0f} if technical and technical.sma_20 else 'N/A'}
            - SMA60: {technical.sma_60:.0f} if technical and technical.sma_60 else 'N/A'}
            
            テクニカルシグナル: {technical_signals}
            
            ニュース分析:
            - 記事数: {len(news_articles)}
            - 全体的な感情: {news_sentiment}
            {alert_info}
            
            上記情報を基に、投資判断と根拠を提供してください。
            """
        )
        
        return result
    
    def _analyze_news_sentiment(self, articles: List) -> str:
        """ニュースの感情を簡易分析"""
        if not articles:
            return "ニュースなし"
        
        # 簡易的な感情カウント
        positive = sum(1 for a in articles if a.sentiment == "positive")
        negative = sum(1 for a in articles if a.sentiment == "negative")
        neutral = sum(1 for a in articles if a.sentiment == "neutral")
        
        total = len(articles)
        if total == 0:
            return "データなし"
        
        pos_ratio = positive / total
        neg_ratio = negative / total
        
        if pos_ratio > 0.5:
            return f"ポジティブ ({positive}/{total})"
        elif neg_ratio > 0.5:
            return f"ネガティブ ({negative}/{total})"
        else:
            return f"中立 ({neutral}/{total})"
    
    async def analyze_from_alert(
        self,
        stock_code: str,
        alert: StockAlert,
        orchestrator=None
    ) -> AnalysisResult:
        """
        アラートを受けて分析実行
        """
        context = {
            "stock_code": stock_code,
            "alert": alert
        }
        
        result = await self.execute(context)
        
        # 分析完了を通知
        if orchestrator:
            await orchestrator.request_recommendation(
                user_id=None,  # コンテキストから取得する必要あり
                analysis_result={
                    "stock_code": stock_code,
                    "analysis": result.dict()
                }
            )
        
        return result
