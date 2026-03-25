from pydantic import BaseModel
from typing import List
from pydantic_ai import Agent

from app.agents.base import BaseAgent
from app.config import get_settings
from app.agents.tools import AgentTools, StockAlert

settings = get_settings()


class MonitoringResult(BaseModel):
    """監視結果の型定義"""
    alerts: List[StockAlert]
    checked_stocks: int
    triggered_count: int


# PydanticAIエージェント定義
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
monitoring_agent = Agent(
    model=_model,
    result_type=MonitoringResult,
    model_settings=_model_settings,  # OpenRouterの場合はbase_urlを設定
    system_prompt="""
    あなたは株価監視の専門家です。
    与えられた銘柄リストを監視し、重要な変化を検知してください。
    
    以下のアラートを検知します：
    1. 価格変動: 閾値を超えた上昇・下落
    2. 出来高急増: 平均に対して異常な取引量
    3. 移動平均線クロス: ゴールデン/デッドクロス
    
    閾値を超えた変化のみをアラートとして報告してください。
    アラートは重要度に応じて severity を設定してください：
    - critical: 10%以上の変動
    - warning: 5-10%の変動、出来高急増
    - info: 移動平均線クロスなど技術的シグナル
    """
)


class MonitoringAgent(BaseAgent[MonitoringResult]):
    """監視エージェント実装"""
    
    def __init__(self, agent_tools: AgentTools):
        super().__init__(monitoring_agent)
        self.tools = agent_tools
    
    async def run(self, context: dict):
        """
        監視ループ:
        1. 対象銘柄を取得
        2. 各種アラート検知ツールを実行
        3. 結果を集約
        """
        # 対象銘柄を取得（contextから or 全銘柄）
        stock_codes = context.get("stock_codes", [])
        user_id = context.get("user_id")
        threshold = context.get("threshold", 5.0)  # デフォルト5%
        
        if not stock_codes and user_id:
            # ユーザーのウォッチリストから取得
            stock_codes = await self.tools.get_watchlist_codes(user_id)
        
        if not stock_codes:
            # 全銘柄監視（テスト用に制限）
            stocks = await self.tools.stock_service.get_all_stocks()
            stock_codes = [s.code for s in stocks[:10]]  # 最初の10銘柄のみ
        
        alerts = []
        
        for code in stock_codes:
            try:
                # 価格変動チェック
                price_alert = await self.tools.check_price_threshold(code, threshold)
                if price_alert:
                    alerts.append(price_alert)
                
                # 出来高急増チェック
                volume_alert = await self.tools.detect_volume_surge(code, ratio=2.0)
                if volume_alert:
                    alerts.append(volume_alert)
                
                # 移動平均線クロスチェック
                ma_alert = await self.tools.detect_moving_average_cross(code)
                if ma_alert:
                    alerts.append(ma_alert)
                    
            except Exception as e:
                print(f"Error monitoring {code}: {e}")
                continue
        
        # PydanticAIエージェントで結果を構造化
        # （将来的にLLMでアラートの優先度付けや要約を行う）
        result = MonitoringResult(
            alerts=alerts,
            checked_stocks=len(stock_codes),
            triggered_count=len(alerts)
        )
        
        return result
    
    async def monitor_and_notify(self, context: dict, orchestrator=None):
        """
        監視を実行し、必要に応じて分析エージェントに依頼
        """
        result = await self.execute(context)
        
        # 重大なアラートがあれば分析エージェントに依頼
        critical_alerts = [a for a in result.alerts if a.severity in ["critical", "warning"]]
        
        if critical_alerts and orchestrator and context.get("user_id"):
            await orchestrator.request_analysis(
                user_id=context["user_id"],
                alerts=critical_alerts
            )
        
        return result
