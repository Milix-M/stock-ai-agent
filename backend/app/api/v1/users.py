from fastapi import APIRouter

router = APIRouter()

@router.get("/me")
async def get_current_user():
    return {"message": "ユーザー情報取得（実装予定）"}
