from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_watchlist():
    return {"message": "ウォッチリスト取得（実装予定）"}

@router.post("/")
async def add_to_watchlist():
    return {"message": "ウォッチリスト追加（実装予定）"}
