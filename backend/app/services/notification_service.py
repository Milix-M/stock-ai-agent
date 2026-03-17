"""
プッシュ通知サービス
"""
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
import json

from pywebpush import webpush, WebPushException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import get_settings
from app.models import PushSubscription, Notification, User

settings = get_settings()


@dataclass
class NotificationPayload:
    """通知ペイロード"""
    title: str
    body: str
    icon: str = "/icon-192.png"
    badge: str = "/badge-72x72.png"
    data: dict = None
    actions: List[dict] = None
    require_interaction: bool = False


class NotificationService:
    """プッシュ通知サービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_claims = {
            "sub": settings.VAPID_CLAIMS_SUB or "mailto:admin@example.com"
        }
    
    async def get_user_subscriptions(self, user_id: str) -> List[PushSubscription]:
        """ユーザーの全購読情報を取得"""
        result = await self.db.execute(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        )
        return result.scalars().all()
    
    async def subscribe(
        self,
        user_id: str,
        endpoint: str,
        p256dh: str,
        auth: str
    ) -> PushSubscription:
        """プッシュ通知を購読"""
        # 既存チェック
        existing = await self.db.execute(
            select(PushSubscription).where(PushSubscription.endpoint == endpoint)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Subscription already exists")
        
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=endpoint,
            p256dh=p256dh,
            auth=auth
        )
        self.db.add(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)
        return subscription
    
    async def unsubscribe(self, user_id: str, endpoint: str) -> bool:
        """プッシュ通知を解除"""
        from sqlalchemy import delete
        
        result = await self.db.execute(
            delete(PushSubscription).where(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint
            )
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def send_notification(
        self,
        user_id: str,
        payload: NotificationPayload
    ) -> dict:
        """
        ユーザーにプッシュ通知を送信
        """
        subscriptions = await self.get_user_subscriptions(user_id)
        
        if not subscriptions:
            return {
                "status": "no_subscriptions",
                "message": "No push subscriptions found"
            }
        
        results = []
        failed_endpoints = []
        
        for sub in subscriptions:
            try:
                # 通知データを構築
                notification_data = {
                    "title": payload.title,
                    "body": payload.body,
                    "icon": payload.icon,
                    "badge": payload.badge,
                    "data": payload.data or {},
                    "requireInteraction": payload.require_interaction,
                }
                
                if payload.actions:
                    notification_data["actions"] = payload.actions
                
                # Web Push送信
                webpush(
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {
                            "p256dh": sub.p256dh,
                            "auth": sub.auth
                        }
                    },
                    data=json.dumps(notification_data),
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims
                )
                
                results.append({
                    "endpoint": sub.endpoint[:50] + "...",
                    "status": "sent"
                })
                
            except WebPushException as e:
                # 無効な購読を削除
                if e.response and e.response.status_code in [410, 404]:
                    failed_endpoints.append(sub.endpoint)
                    await self._remove_invalid_subscription(sub.id)
                else:
                    results.append({
                        "endpoint": sub.endpoint[:50] + "...",
                        "status": "failed",
                        "error": str(e)
                    })
        
        # 通知履歴を保存
        await self._save_notification_history(
            user_id=user_id,
            title=payload.title,
            body=payload.body,
            data=payload.data
        )
        
        return {
            "status": "completed",
            "sent_count": len([r for r in results if r["status"] == "sent"]),
            "failed_count": len(failed_endpoints) + len([r for r in results if r["status"] == "failed"]),
            "results": results
        }
    
    async def send_price_alert(
        self,
        user_id: str,
        stock_code: str,
        stock_name: str,
        change_percent: float,
        current_price: float
    ) -> dict:
        """価格変動アラートを送信"""
        direction = "📈" if change_percent > 0 else "📉"
        
        payload = NotificationPayload(
            title=f"{direction} {stock_name} ({stock_code})",
            body=f"前日比 {change_percent:+.1f}%（{current_price:,.0f}円）",
            data={
                "type": "price_alert",
                "stock_code": stock_code,
                "stock_name": stock_name,
                "change_percent": change_percent,
                "current_price": current_price
            },
            actions=[
                {
                    "action": "view",
                    "title": "詳細を見る"
                },
                {
                    "action": "dismiss",
                    "title": "閉じる"
                }
            ]
        )
        
        return await self.send_notification(user_id, payload)
    
    async def send_recommendation(
        self,
        user_id: str,
        stock_code: str,
        stock_name: str,
        pattern_name: str,
        match_score: float,
        reason: str
    ) -> dict:
        """レコメンド通知を送信"""
        payload = NotificationPayload(
            title=f"💡 {stock_name} がおすすめ",
            body=reason[:100] + "..." if len(reason) > 100 else reason,
            data={
                "type": "recommendation",
                "stock_code": stock_code,
                "stock_name": stock_name,
                "pattern": pattern_name,
                "score": match_score
            },
            require_interaction=True,
            actions=[
                {
                    "action": "view",
                    "title": "詳細を見る"
                },
                {
                    "action": "add_watchlist",
                    "title": "ウォッチリストに追加"
                }
            ]
        )
        
        return await self.send_notification(user_id, payload)
    
    async def _remove_invalid_subscription(self, subscription_id: str):
        """無効な購読を削除"""
        from sqlalchemy import delete
        await self.db.execute(
            delete(PushSubscription).where(PushSubscription.id == subscription_id)
        )
        await self.db.commit()
    
    async def _save_notification_history(
        self,
        user_id: str,
        title: str,
        body: str,
        data: dict
    ):
        """通知履歴を保存"""
        notification_type = data.get("type", "general") if data else "general"
        
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            body=body,
            data=data
        )
        self.db.add(notification)
        await self.db.commit()
    
    async def get_notification_history(
        self,
        user_id: str,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """通知履歴を取得"""
        query = select(Notification).where(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """通知を既読にする"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            await self.db.commit()
            return True
        return False
