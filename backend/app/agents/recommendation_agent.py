"""
提案エージェント
パターンマッチング・提案生成・通知送信を実行
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.agents.base import BaseAgent
from app.agents.tools import AgentTools
from app.agents.memory import AgentSharedMemory
from app.services.recommendation_service import PatternMatcher, PatternMatch
from app.services.pattern_service import PatternService  # 後で作成
from app.models import InvestmentPattern


class Recommendation(BaseModel):
    """提案結果"""
    stock_code: str
    stock_name: str
    pattern_name: str
    match_score: float
    reason: str
    action: str  # "buy" | "watch" | "alert"
    priority: int  # 1-5, 5が最高優先


class RecommendationList(BaseModel):
    """提案リスト"""
    recommendations: List[Recommendation]
    generated_at: str
    total_matches: int
    user_id: str


class RecommendationAgent(BaseAgent[RecommendationList]):
    """提案エージェント実装"""
    
    def __init__(
        self,
        tools: AgentTools,
        pattern_matcher: PatternMatcher,
        memory: AgentSharedMemory
    ):
        super().__init__(None)  # PydanticAIエージェントは不使用
        self.tools = tools
        self.pattern_matcher = pattern_matcher
        self.memory = memory
    
    async def run(self, context: dict) -> RecommendationList:
        """
        提案フロー:
        1. ユーザーの投資パターンを取得
        2. パターンマッチング実行
        3. スコアに応じて優先度付け
        4. 通知判断
        """
        user_id = context.get("user_id")
        patterns = context.get("patterns", [])
        analysis_results = context.get("analysis_results", [])
        
        if not patterns:
            return RecommendationList(
                recommendations=[],
                generated_at=datetime.utcnow().isoformat(),
                total_matches=0,
                user_id=user_id or ""
            )
        
        all_recommendations = []
        
        for pattern in patterns:
            if not pattern.is_active:
                continue
            
            # パターンマッチング
            matches = await self.pattern_matcher.match_pattern(pattern)
            
            for match in matches:
                # 優先度計算
                priority = self._calculate_priority(match, analysis_results)
                
                # アクション決定
                action = self._determine_action(match.match_score, priority)
                
                recommendation = Recommendation(
                    stock_code=match.stock_code,
                    stock_name=match.stock_name,
                    pattern_name=pattern.name,
                    match_score=match.match_score,
                    reason=match.recommendation_reason,
                    action=action,
                    priority=priority
                )
                
                all_recommendations.append(recommendation)
        
        # スコア順にソート
        all_recommendations.sort(key=lambda x: (x.priority, x.match_score), reverse=True)
        
        # 上位10件に絞る
        top_recommendations = all_recommendations[:10]
        
        return RecommendationList(
            recommendations=top_recommendations,
            generated_at=datetime.utcnow().isoformat(),
            total_matches=len(all_recommendations),
            user_id=user_id or ""
        )
    
    async def generate_and_notify(
        self, 
        context: dict,
        orchestrator=None,
        notification_service=None
    ) -> RecommendationList:
        """
        提案を生成し、必要に応じて通知を送信
        """
        result = await self.execute(context)
        
        user_id = context.get("user_id")
        
        # 高優先度の提案を通知
        high_priority = [r for r in result.recommendations if r.priority >= 4]
        
        for rec in high_priority:
            if notification_service and user_id:
                await notification_service.send_recommendation(
                    user_id=user_id,
                    title=f"📈 {rec.stock_name} がおすすめ",
                    body=rec.reason,
                    data={
                        "stock_code": rec.stock_code,
                        "pattern": rec.pattern_name,
                        "score": rec.match_score,
                        "action": rec.action
                    }
                )
            
            # 履歴に保存
            await self.memory.save_analysis_history(rec.stock_code, {
                "type": "recommendation",
                "pattern": rec.pattern_name,
                "score": rec.match_score,
                "reason": rec.reason,
                "notified": True
            })
        
        return result
    
    def _calculate_priority(
        self, 
        match: PatternMatch, 
        analysis_results: List[Dict]
    ) -> int:
        """
        優先度を計算（1-5）
        """
        priority = 3  # デフォルト中程度
        
        # マッチスコアに基づく
        if match.match_score >= 0.95:
            priority += 2
        elif match.match_score >= 0.85:
            priority += 1
        
        # 分析結果があれば加味
        for analysis in analysis_results:
            if analysis.get("stock_code") == match.stock_code:
                if analysis.get("rating") == "buy":
                    priority += 1
                if analysis.get("confidence", 0) > 0.8:
                    priority += 1
        
        # 過去のフィードバックを確認
        # TODO: ユーザーが過去に類似銘柄で良い反応を示したか
        
        return min(max(priority, 1), 5)  # 1-5の範囲に収める
    
    def _determine_action(self, score: float, priority: int) -> str:
        """
        アクションを決定
        """
        if score >= 0.9 and priority >= 4:
            return "buy"
        elif score >= 0.7 or priority >= 3:
            return "watch"
        else:
            return "alert"
    
    async def filter_by_user_preferences(
        self,
        recommendations: List[Recommendation],
        user_id: str
    ) -> List[Recommendation]:
        """
        ユーザーの過去のフィードバックに基づきフィルタリング
        """
        feedback = await self.memory.get_user_feedback(user_id)
        
        # 過去に「無視」した銘柄を除外
        ignored_stocks = set()
        for f in feedback:
            if f.get("feedback", {}).get("action") == "dismissed":
                ignored_stocks.add(f.get("stock_code"))
        
        filtered = [
            r for r in recommendations 
            if r.stock_code not in ignored_stocks
        ]
        
        return filtered