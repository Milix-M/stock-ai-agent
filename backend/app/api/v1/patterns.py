from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_patterns():
    return {"message": "パターン一覧（実装予定）"}

@router.post("/")
async def create_pattern():
    return {"message": "パターン作成（実装予定）"}

@router.post("/parse")
async def parse_pattern():
    return {"message": "パターン解析（実装予定）"}
