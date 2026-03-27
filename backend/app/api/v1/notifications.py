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


# --- 通知設定 endpoints ---

from app.models import NotificationSetting
from sqlalchemy import select as sa_select


class NotificationSettingsResponse(BaseModel):
    recommend_enabled: bool = True
    recommend_min_score: float = 0.7
    price_alert_enabled: bool = True
    price_alert_threshold: float = 5.0
    volume_surge_enabled: bool = True
    volume_surge_multiplier: float = 2.0
    daily_report_enabled: bool = True


class NotificationSettingsUpdate(BaseModel):
    recommend_enabled: bool | None = None
    recommend_min_score: float | None = None
    price_alert_enabled: bool | None = None
    price_alert_threshold: float | None = None
    volume_surge_enabled: bool | None = None
    volume_surge_multiplier: float | None = None
    daily_report_enabled: bool | None = None


@router.get("/settings")
async def get_notification_settings(
    current_user=Depends(get_current_user),
    db: AsyncSession=Depends(get_db),
):
    """通知設定を取得（未設定ならデフォルト返す）"""
    result = await db.execute(
        sa_select(NotificationSetting).where(NotificationSetting.user_id == current_user.id)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        return NotificationSettingsResponse()

    return NotificationSettingsResponse(
        recommend_enabled=setting.recommend_enabled,
        recommend_min_score=float(setting.recommend_min_score) if setting.recommend_min_score is not None else 0.7,
        price_alert_enabled=setting.price_alert_enabled,
        price_alert_threshold=float(setting.price_alert_threshold) if setting.price_alert_threshold is not None else 5.0,
        volume_surge_enabled=setting.volume_surge_enabled,
        volume_surge_multiplier=float(setting.volume_surge_multiplier) if setting.volume_surge_multiplier is not None else 2.0,
        daily_report_enabled=setting.daily_report_enabled,
    )


@router.put("/settings")
async def update_notification_settings(
    request: NotificationSettingsUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession=Depends(get_db),
):
    """通知設定を更新（upsert）"""
    result = await db.execute(
        sa_select(NotificationSetting).where(NotificationSetting.user_id == current_user.id)
    )
    setting = result.scalar_one_or_none()

    if not setting:
        setting = NotificationSetting(user_id=current_user.id)
        db.add(setting)

    update_data = request.model_dump(exclude_none=True)
    for key, value in update_data.items():
        setattr(setting, key, value)

    await db.commit()
    await db.refresh(setting)

    return {"message": "Settings updated successfully"}


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
