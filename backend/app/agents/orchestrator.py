import json
import redis.asyncio as redis
from enum import Enum
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel


class MessageType(str, Enum):
    """エージェント間メッセージタイプ"""
    REQUEST_ANALYSIS = "request_analysis"
    REQUEST_RECOMMENDATION = "request_recommendation"
    ANALYSIS_COMPLETE = "analysis_complete"
    RECOMMENDATION_READY = "rec_ready"
    ALERT_TRIGGERED = "alert_triggered"
    FEEDBACK_RECEIVED = "feedback_received"


class AgentMessage(BaseModel):
    """エージェント間メッセージ"""
    message_id: UUID
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: dict
    timestamp: datetime
    priority: str = "normal"  # "low" | "normal" | "high"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class AgentOrchestrator:
    """
    エージェント間通信を管理（Redis Pub/Subベース）
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.channels = {
            "monitoring": "agent:monitoring",
            "analysis": "agent:analysis",
            "recommendation": "agent:recommendation"
        }
    
    async def publish(self, target_agent: str, message: AgentMessage):
        """メッセージを特定エージェントに送信"""
        channel = self.channels.get(target_agent)
        if channel:
            await self.redis.publish(channel, message.json())
    
    async def subscribe(self, agent_name: str):
        """エージェントが自分のチャンネルを購読"""
        channel = self.channels.get(agent_name)
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                yield AgentMessage(**data)
    
    # ヘルパーメソッド
    async def request_analysis(self, user_id: str, alerts: list):
        """分析エージェントに依頼"""
        message = AgentMessage(
            message_id=uuid4(),
            from_agent="monitoring",
            to_agent="analysis",
            message_type=MessageType.REQUEST_ANALYSIS,
            payload={
                "user_id": user_id,
                "alerts": [alert.__dict__ if hasattr(alert, '__dict__') else alert for alert in alerts]
            },
            timestamp=datetime.utcnow(),
            priority="high"
        )
        await self.publish("analysis", message)
    
    async def request_recommendation(self, user_id: str, analysis_result: dict):
        """提案エージェントに依頼"""
        message = AgentMessage(
            message_id=uuid4(),
            from_agent="analysis",
            to_agent="recommendation",
            message_type=MessageType.REQUEST_RECOMMENDATION,
            payload={
                "user_id": user_id,
                **analysis_result
            },
            timestamp=datetime.utcnow()
        )
        await self.publish("recommendation", message)
    
    async def notify_alert(self, user_id: str, alert: dict):
        """アラート発火を通知"""
        message = AgentMessage(
            message_id=uuid4(),
            from_agent="monitoring",
            to_agent="recommendation",
            message_type=MessageType.ALERT_TRIGGERED,
            payload={
                "user_id": user_id,
                "alert": alert
            },
            timestamp=datetime.utcnow(),
            priority="high"
        )
        await self.publish("recommendation", message)
