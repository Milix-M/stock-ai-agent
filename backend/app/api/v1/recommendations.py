from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_recommendations():
    return {"message": "レコメンド取得（実装予定）"}
