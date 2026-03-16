from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_stocks():
    return {"message": "銘柄一覧（実装予定）"}

@router.get("/{code}")
async def get_stock(code: str):
    return {"message": f"銘柄詳細 {code}（実装予定）"}
