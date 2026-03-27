from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.db.session import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    authenticate_user,
    create_user,
    get_user_by_email,
    decode_token,
)
from app.models.models import User, PasswordResetToken
from app.schemas import RegisterRequest, Token, LoginRequest, RefreshTokenRequest, PasswordResetRequest, PasswordResetConfirm

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register(
    request: Request,
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """ユーザー登録"""
    # メールアドレス重複チェック
    existing_user = await get_user_by_email(db, body.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # ユーザー作成
    user = await create_user(
        db=db,
        email=body.email,
        password=body.password,
        display_name=body.display_name
    )
    
    # トークン生成
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """ログイン（OAuth2形式）"""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/login/json", response_model=Token)
async def login_json(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """ログイン（JSON形式）"""
    user = await authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """トークンリフレッシュ"""
    payload = decode_token(request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # ユーザー存在確認
    from app.core.security import get_user_by_id
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # 新しいトークン生成
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/password-reset/request")
@limiter.limit("5/minute")
async def request_password_reset(
    request: Request,
    body: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """パスワードリセット要求（開発モード：トークンをレスポンスで返す）"""
    import secrets
    from datetime import timedelta
    from sqlalchemy import select

    user = await get_user_by_email(db, body.email)

    if user:
        # 既存の未使用トークンを無効化
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        )
        result = await db.execute(stmt)
        for old_token in result.scalars().all():
            old_token.used = True

        # 新しいリセットトークン生成
        reset_token_str = secrets.token_urlsafe(32)
        reset_token = PasswordResetToken(
            id=str(__import__('uuid').uuid4()),
            user_id=user.id,
            token=reset_token_str,
            expires_at=datetime.utcnow() + timedelta(minutes=30),
        )
        db.add(reset_token)
        await db.commit()

        return {
            "message": "リセットトークンを生成しました（開発モード）",
            "reset_token": reset_token_str,
            "dev_mode": True,
        }

    # メールアドレスが存在しなくても同じレスポンス（セキュリティのため）
    return {
        "message": "リセットトークンを生成しました（開発モード）",
        "reset_token": None,
        "dev_mode": True,
    }


@router.post("/password-reset/confirm")
async def confirm_password_reset(
    body: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """パスワードリセット確認"""
    from sqlalchemy import select
    from app.core.security import get_password_hash

    if len(body.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="パスワードは8文字以上必要です"
        )

    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token == body.token,
        PasswordResetToken.used == False,
    )
    result = await db.execute(stmt)
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="無効なリセットトークンです"
        )

    if reset_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="リセットトークンの有効期限が切れています"
        )

    # ユーザーのパスワードを更新
    user_stmt = select(User).where(User.id == reset_token.user_id)
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ユーザーが見つかりません"
        )

    user.password_hash = get_password_hash(body.new_password)
    reset_token.used = True
    await db.commit()

    return {"message": "パスワードを更新しました"}
