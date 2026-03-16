from fastapi import APIRouter

router = APIRouter()

@router.post("/register")
async def register():
    return {"message": "ユーザー登録（実装予定）"}

@router.post("/login")
async def login():
    return {"message": "ログイン（実装予定）"}

@router.post("/refresh")
async def refresh_token():
    return {"message": "トークンリフレッシュ（実装予定）"}
