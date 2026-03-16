from fastapi import APIRouter

router = APIRouter()

@router.post("/subscribe")
async def subscribe_notification():
    return {"message": "通知購読（実装予定）"}

@router.post("/unsubscribe")
async def unsubscribe_notification():
    return {"message": "通知解除（実装予定）"}
