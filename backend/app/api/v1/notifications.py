from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.notification_service import NotificationService, NotificationPayload

router = APIRouter()


class SubscribeRequest(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


class UnsubscribeRequest(BaseModel):
    endpoint: str


@router.post("/subscribe")
async def subscribe_notifications(
    request: SubscribeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """プッシュ通知を購読"""
    service = NotificationService(db)
    
    try:
        subscription = await service.subscribe(
            user_id=str(current_user.id),
            endpoint=request.endpoint,
            p256dh=request.p256dh,
            auth=request.auth
        )
        return {"message": "Subscribed successfully", "subscription_id": str(subscription.id)}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/unsubscribe")
async def unsubscribe_notifications(
    request: UnsubscribeRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """プッシュ通知を解除"""
    service = NotificationService(db)
    
    success = await service.unsubscribe(
        user_id=str(current_user.id),
        endpoint=request.endpoint
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {"message": "Unsubscribed successfully"}


@router.get("/")
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """通知履歴を取得"""
    service = NotificationService(db)
    
    notifications = await service.get_notification_history(
        user_id=str(current_user.id),
        limit=limit,
        unread_only=unread_only
    )
    
    return notifications


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """通知を既読にする"""
    service = NotificationService(db)
    
    success = await service.mark_as_read(
        notification_id=notification_id,
        user_id=str(current_user.id)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Marked as read"}


# テスト用エンドポイント（開発時のみ）
@router.post("/test")
async def send_test_notification(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """テスト通知を送信"""
    service = NotificationService(db)
    
    payload = NotificationPayload(
        title="🧪 テスト通知",
        body="プッシュ通知のテストです。正常に動作しています！",
        data={"type": "test"}
    )
    
    result = await service.send_notification(
        user_id=str(current_user.id),
        payload=payload
    )
    
    return result
