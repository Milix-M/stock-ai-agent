import json
from datetime import datetime
from typing import Optional, List
import redis.asyncio as redis


class AgentSharedMemory:
    """
    Redisベースのエージェント間共有メモリ
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def save_monitoring_state(self, stock_code: str, state: dict):
        """監視状態を保存"""
        key = f"monitoring:{stock_code}"
        state["updated_at"] = datetime.utcnow().isoformat()
        await self.redis.hset(key, mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in state.items()
        })
        await self.redis.expire(key, 86400)  # 24時間保持
    
    async def get_monitoring_state(self, stock_code: str) -> Optional[dict]:
        """監視状態を取得"""
        key = f"monitoring:{stock_code}"
        data = await self.redis.hgetall(key)
        if not data:
            return None
        return {
            k: json.loads(v) if v.startswith("{") or v.startswith("[") else v
            for k, v in data.items()
        }
    
    async def save_analysis_history(self, stock_code: str, analysis: dict):
        """分析履歴を保存"""
        key = f"analysis_history:{stock_code}"
        analysis["timestamp"] = datetime.utcnow().isoformat()
        await self.redis.lpush(key, json.dumps(analysis))
        await self.redis.ltrim(key, 0, 99)  # 最新100件のみ保持
        await self.redis.expire(key, 604800)  # 7日間保持
    
    async def get_analysis_history(self, stock_code: str, limit: int = 10) -> List[dict]:
        """分析履歴を取得"""
        key = f"analysis_history:{stock_code}"
        data = await self.redis.lrange(key, 0, limit - 1)
        return [json.loads(d) for d in data]
    
    async def save_user_feedback(self, user_id: str, recommendation_id: str, feedback: dict):
        """ユーザーフィードバックを保存（学習用）"""
        key = f"feedback:{user_id}"
        feedback_data = {
            "recommendation_id": recommendation_id,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.redis.lpush(key, json.dumps(feedback_data))
        await self.redis.expire(key, 2592000)  # 30日間保持
    
    async def get_user_feedback(self, user_id: str, limit: int = 50) -> List[dict]:
        """ユーザーフィードバックを取得"""
        key = f"feedback:{user_id}"
        data = await self.redis.lrange(key, 0, limit - 1)
        return [json.loads(d) for d in data]
    
    async def get_user_context(self, user_id: str) -> dict:
        """
        ユーザーコンテキストを取得
        （過去のフィードバック、閲覧履歴、投資パターンを統合）
        """
        feedback = await self.get_user_feedback(user_id, limit=20)
        
        return {
            "user_id": user_id,
            "recent_feedback": feedback,
            "feedback_count": len(feedback),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def save_alert_status(self, alert_id: str, status: str, metadata: dict = None):
        """アラート状態を保存"""
        key = f"alert:{alert_id}"
        data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        if metadata:
            data["metadata"] = json.dumps(metadata)
        await self.redis.hset(key, mapping=data)
        await self.redis.expire(key, 604800)  # 7日間保持
    
    async def get_alert_status(self, alert_id: str) -> Optional[dict]:
        """アラート状態を取得"""
        key = f"alert:{alert_id}"
        data = await self.redis.hgetall(key)
        if not data:
            return None
        result = dict(data)
        if "metadata" in result:
            result["metadata"] = json.loads(result["metadata"])
        return result
