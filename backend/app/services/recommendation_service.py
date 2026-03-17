from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from app.models import InvestmentPattern, Stock, StockPrice
from app.services.stock_service import StockService


@dataclass
class PatternMatch:
    """パターンマッチング結果"""
    stock_code: str
    stock_name: str
    match_score: float  # 0.0 ~ 1.0
    matched_criteria: List[str]
    missed_criteria: List[str]
    recommendation_reason: str


class PatternMatcher:
    """投資パターンマッチングサービス"""
    
    def __init__(self, stock_service: StockService):
        self.stock_service = stock_service
    
    async def match_pattern(
        self, 
        pattern: InvestmentPattern, 
        stock_codes: List[str] = None
    ) -> List[PatternMatch]:
        """
        投資パターンと銘柄をマッチング
        """
        filters = pattern.parsed_filters
        matches = []
        
        # 対象銘柄を取得
        if stock_codes:
            stocks = []
            for code in stock_codes:
                stock = await self.stock_service.get_stock_by_code(code)
                if stock:
                    stocks.append(stock)
        else:
            stocks = await self.stock_service.get_all_stocks()
        
        for stock in stocks:
            match_result = await self._evaluate_stock(stock, filters)
            if match_result["score"] >= 0.6:  # 60%以上マッチで採用
                matches.append(PatternMatch(
                    stock_code=stock.code,
                    stock_name=stock.name,
                    match_score=match_result["score"],
                    matched_criteria=match_result["matched"],
                    missed_criteria=match_result["missed"],
                    recommendation_reason=match_result["reason"]
                ))
        
        # スコア順にソート
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:20]  # 上位20件まで
    
    async def _evaluate_stock(
        self, 
        stock: Stock, 
        filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        個別銘柄をパターンフィルタで評価
        """
        matched = []
        missed = []
        score = 0.0
        total_criteria = 0
        
        # 指標データ取得
        latest_price = await self.stock_service.get_latest_price(stock.id)
        
        # PER評価
        if "per_max" in filters or "per_min" in filters:
            total_criteria += 1
            per_ok = self._check_range(
                stock.per, 
                filters.get("per_min"), 
                filters.get("per_max")
            )
            if per_ok:
                matched.append(f"PER: {stock.per}倍")
                score += 1.0
            else:
                missed.append(f"PER: {stock.per}倍（条件外）")
        
        # PBR評価
        if "pbr_max" in filters or "pbr_min" in filters:
            total_criteria += 1
            pbr_ok = self._check_range(
                stock.pbr,
                filters.get("pbr_min"),
                filters.get("pbr_max")
            )
            if pbr_ok:
                matched.append(f"PBR: {stock.pbr}倍")
                score += 1.0
            else:
                missed.append(f"PBR: {stock.pbr}倍（条件外）")
        
        # 配当利回り評価
        if "dividend_yield_min" in filters or "dividend_yield_max" in filters:
            total_criteria += 1
            div_ok = self._check_range(
                stock.dividend_yield,
                filters.get("dividend_yield_min"),
                filters.get("dividend_yield_max")
            )
            if div_ok:
                matched.append(f"配当利回り: {stock.dividend_yield}%")
                score += 1.0
            else:
                missed.append(f"配当利回り: {stock.dividend_yield}%（条件外）")
        
        # 時価総額評価
        if "market_cap_min" in filters or "market_cap_max" in filters:
            total_criteria += 1
            cap_ok = self._check_range(
                stock.market_cap,
                filters.get("market_cap_min"),
                filters.get("market_cap_max")
            )
            if cap_ok:
                cap_str = self._format_market_cap(stock.market_cap)
                matched.append(f"時価総額: {cap_str}")
                score += 1.0
            else:
                missed.append(f"時価総額: 条件外")
        
        # 価格変動評価
        if "price_change_min" in filters or "price_change_max" in filters:
            total_criteria += 1
            if latest_price:
                # 価格変動を計算（前日比）
                prices = await self.stock_service.get_stock_prices(stock.id, days=2)
                if len(prices) >= 2:
                    change_pct = ((prices[0].close - prices[1].close) / prices[1].close) * 100
                    change_ok = self._check_range(
                        change_pct,
                        filters.get("price_change_min"),
                        filters.get("price_change_max")
                    )
                    if change_ok:
                        matched.append(f"前日比: {change_pct:+.1f}%")
                        score += 1.0
                    else:
                        missed.append(f"前日比: {change_pct:+.1f}%（条件外）")
        
        # スコア計算
        final_score = score / total_criteria if total_criteria > 0 else 0.0
        
        # 推奨理由を生成
        reason = self._generate_reason(stock, matched, final_score)
        
        return {
            "score": final_score,
            "matched": matched,
            "missed": missed,
            "reason": reason
        }
    
    def _check_range(
        self, 
        value: Optional[float], 
        min_val: Optional[float], 
        max_val: Optional[float]
    ) -> bool:
        """値が範囲内かチェック"""
        if value is None:
            return False
        
        if min_val is not None and value < min_val:
            return False
        if max_val is not None and value > max_val:
            return False
        
        return True
    
    def _format_market_cap(self, cap: Optional[int]) -> str:
        """時価総額を読みやすくフォーマット"""
        if cap is None:
            return "不明"
        if cap >= 1_000_000_000_000:  # 1兆円以上
            return f"{cap / 1_000_000_000_000:.1f}兆円"
        elif cap >= 100_000_000:  # 1億円以上
            return f"{cap / 100_000_000:.0f}億円"
        else:
            return f"{cap:,}円"
    
    def _generate_reason(
        self, 
        stock: Stock, 
        matched_criteria: List[str], 
        score: float
    ) -> str:
        """推奨理由を生成"""
        if score >= 0.9:
            level = "非常に良く"
        elif score >= 0.75:
            level = "良く"
        elif score >= 0.6:
            level = "概ね"
        else:
            level = "やや"
        
        criteria_text = "、".join(matched_criteria[:3])  # 最大3項目
        
        return f"{stock.name}は{level}条件にマッチしています（{criteria_text}）"
    
    async def get_recommendations_for_user(
        self, 
        user_id: str, 
        patterns: List[InvestmentPattern]
    ) -> Dict[str, List[PatternMatch]]:
        """
        ユーザーの全パターンでレコメンドを生成
        """
        all_recommendations = {}
        
        for pattern in patterns:
            if not pattern.is_active:
                continue
            
            matches = await self.match_pattern(pattern)
            if matches:
                all_recommendations[pattern.name] = matches
        
        return all_recommendations