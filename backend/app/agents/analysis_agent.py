"""
分析エージェント
ニュース・決算・テクニカル分析を実行
"""
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pydantic_ai import Agent, AgentTool, RunResult

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
_analysis_model = "openai:gpt-4o-mini"

# PydanticAIエージェント定義
analysis_agent = Agent(
    model=_analysis_model,
    result_type=StockAnalysisResult,
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
    
    @AgentTool
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
    
    @AgentTool
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
    
    @AgentTool
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
    
    @AgentTool
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
        
        # 1. 基本情報取得
        stock = await self.stock_service.get_stock_by_code(stock_code)
        if not stock:
            raise ValueError(f"Stock not found: {stock_code}")
        
        stock_name = stock_name or stock.name
        
        # 2. ニュース分析
        news_analysis_data = await self.analyze_news_sentiment(f"{stock_name} {stock_code}")
        news_analysis = NewsAnalysis(
            sentiment=news_analysis_data.get("sentiment", "neutral"),
            sentiment_score=news_analysis_data.get("score", 0.0),
            key_topics=[],
            risk_factors=[],
            opportunities=[]
        )
        
        # 3. 財務分析
        financial_data = await self.financial_service.get_financial_data(stock_code)
        financial_analysis = await self._analyze_financial(financial_data)
        
        # 4. テクニカル分析
        prices = await self.stock_service.get_stock_prices(stock.id, days=60)
        price_data = [
            {"close": float(p.close), "date": p.date.isoformat()}
            for p in prices
        ]
        technical_analysis_data = await self.technical_service.analyze_stock(price_data)
        technical_signals = self.technical_service.generate_signals(technical_analysis_data)
        technical_analysis = TechnicalAnalysis(
            trend="uptrend" if technical_analysis_data.sma_5 and technical_analysis_data.sma_20 
                      and technical_analysis_data.sma_5 > technical_analysis_data.sma_20 else "downtrend",
            momentum="strong" if technical_analysis_data.rsi and technical_analysis_data.rsi > 50 else "weak",
            volatility="medium",
            signals=technical_signals,
            support_levels=[],
            resistance_levels=[]
        )
        
        # 5. 総合評価
        overall_rating = self._determine_rating(
            news_analysis, financial_analysis, technical_analysis
        )
        confidence_score = self._calculate_confidence(
            news_analysis, financial_analysis, technical_analysis
        )
        
        # 6. 結果生成
        result = StockAnalysisResult(
            stock_code=stock_code,
            stock_name=stock_name,
            analysis_date=datetime.now().isoformat(),
            overall_rating=overall_rating,
            confidence_score=confidence_score,
            news_analysis=news_analysis,
            financial_analysis=financial_analysis,
            technical_analysis=technical_analysis,
            summary=self._generate_summary(
                stock_name, news_analysis, financial_analysis, technical_signals
            ),
            key_points=self._generate_key_points(
                news_analysis, financial_analysis, technical_signals
            ),
            risks=self._generate_risks(news_analysis, financial_analysis),
            recommendations=self._generate_recommendations(
                news_analysis, financial_analysis, technical_analysis
            )
        )
        
        return result
    
    async def _analyze_financial(self, financial_data) -> FinancialAnalysis:
        """財務データを分析"""
        if not financial_data:
            return FinancialAnalysis(
                revenue_trend="stable",
                profitability="medium",
                financial_health="moderate",
                valuation="fair",
                key_metrics={}
            )
        
        # 成長性判断
        revenue_trend = "stable"
        if financial_data.revenue_growth:
            if financial_data.revenue_growth > 0.1:
                revenue_trend = "growing"
            elif financial_data.revenue_growth < -0.1:
                revenue_trend = "declining"
        
        # 収益性判断
        profitability = "medium"
        if financial_data.revenue and financial_data.operating_profit:
            margin = financial_data.operating_profit / financial_data.revenue
            if margin > 0.15:
                profitability = "high"
            elif margin < 0.05:
                profitability = "low"
        
        # 財務健全性判断
        financial_health = "moderate"
        if financial_data.total_assets and financial_data.equity:
            equity_ratio = financial_data.equity / financial_data.total_assets
            if equity_ratio > 0.5:
                financial_health = "strong"
            elif equity_ratio < 0.3:
                financial_health = "weak"
        
        return FinancialAnalysis(
            revenue_trend=revenue_trend,
            profitability=profitability,
            financial_health=financial_health,
            valuation="fair",
            key_metrics={
                "revenue": financial_data.revenue,
                "operating_profit": financial_data.operating_profit,
                "net_profit": financial_data.net_profit,
                "eps": financial_data.eps,
                "revenue_growth": financial_data.revenue_growth,
            }
        )
    
    def _determine_rating(
        self, 
        news: NewsAnalysis, 
        financial: FinancialAnalysis, 
        technical
    ) -> str:
        """総合評価を決定"""
        score = 0
        
        # ニューススコア
        if news.sentiment == "positive":
            score += 1
        elif news.sentiment == "negative":
            score -= 1
        
        # 財務スコア
        if financial.revenue_trend == "growing":
            score += 1
        elif financial.revenue_trend == "declining":
            score -= 1
        
        if financial.profitability == "high":
            score += 1
        elif financial.profitability == "low":
            score -= 1
        
        # テクニカルスコア
        if technical.trend == "uptrend":
            score += 1
        elif technical.trend == "downtrend":
            score -= 1
        
        if score >= 2:
            return "buy"
        elif score <= -2:
            return "sell"
        return "hold"
    
    def _calculate_confidence(
        self, 
        news: NewsAnalysis, 
        financial: FinancialAnalysis, 
        technical
    ) -> float:
        """確信度を計算"""
        confidence = 0.5
        
        if news.key_topics:
            confidence += 0.1
        if financial.key_metrics:
            confidence += 0.2
        if technical.signals:
            confidence += 0.1
        
        return min(confidence, 0.9)
    
    def _generate_summary(
        self, 
        stock_name: str, 
        news: NewsAnalysis, 
        financial: FinancialAnalysis,
        signals: list
    ) -> str:
        """分析サマリーを生成"""
        parts = [f"{stock_name}の分析結果："]
        
        # ニュースサマリー
        if news.sentiment == "positive":
            parts.append("最近のニュースはポジティブです。")
        elif news.sentiment == "negative":
            parts.append("最近のニュースはネガティブです。")
        
        # 業績サマリー
        if financial.revenue_trend == "growing":
            parts.append("売上高は成長傾向にあります。")
        elif financial.revenue_trend == "declining":
            parts.append("売上高は減少傾向にあります。")
        
        # テクニカルサマリー
        if signals:
            parts.append(f"テクニカル指標では{signals[0]}が確認されています。")
        
        return "".join(parts)
    
    def _generate_key_points(
        self, 
        news: NewsAnalysis, 
        financial: FinancialAnalysis,
        signals: list
    ) -> List[str]:
        """重要ポイントを生成"""
        points = []
        
        if news.key_topics:
            points.append(f"注目トピック: {', '.join(news.key_topics[:3])}")
        
        if financial.revenue_growth:
            points.append(f"売上成長率: {financial.revenue_growth*100:.1f}%")
        
        if financial.eps:
            points.append(f"EPS: {financial.eps}円")
        
        if signals:
            points.extend(signals[:2])
        
        return points
    
    def _generate_risks(
        self, 
        news: NewsAnalysis, 
        financial: FinancialAnalysis
    ) -> List[str]:
        """リスク要因を生成"""
        risks = []
        
        if news.risk_factors:
            risks.extend(news.risk_factors)
        
        if financial.revenue_trend == "declining":
            risks.append("売上減少傾向")
        
        if financial.financial_health == "weak":
            risks.append("財務体質に懸念")
        
        return risks[:3]
    
    def _generate_recommendations(
        self, 
        news: NewsAnalysis, 
        financial: FinancialAnalysis,
        technical
    ) -> List[str]:
        """推奨アクションを生成"""
        recs = []
        
        rating = self._determine_rating(news, financial, technical)
        
        if rating == "buy":
            recs.append("買い検討：各指標がポジティブです")
        elif rating == "sell":
            recs.append("売り検討：リスクが高まっています")
        else:
            recs.append("様子見：判断材料が不十分です")
        
        return recs
