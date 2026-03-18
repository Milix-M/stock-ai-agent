from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.pattern_service import PatternService
from app.services.llm_service import LLMService
from app.schemas import PatternResponse, PatternCreate, PatternParseRequest, PatternParseResponse

router = APIRouter()


@router.get("/", response_model=List[PatternResponse])
async def list_patterns(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ユーザーの投資パターン一覧を取得"""
    service = PatternService(db)
    patterns = await service.get_user_patterns(str(current_user.id))
    return patterns


@router.post("/parse", response_model=PatternParseResponse)
async def parse_pattern(
    request: PatternParseRequest,
    current_user = Depends(get_current_user)
):
    """自然言語をパターンに解析"""
    llm_service = LLMService()
    
    try:
        parsed = await llm_service.parse_pattern(request.input)
        
        return PatternParseResponse(
            raw_input=request.input,
            parsed=parsed
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Pattern parsing failed: {str(e)}"
        )


@router.post("/", response_model=PatternResponse, status_code=status.HTTP_201_CREATED)
async def create_pattern(
    request: PatternCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """投資パターンを作成し、即座にマッチング・レコメンドを生成"""
    service = PatternService(db)
    
    try:
        pattern = await service.create_pattern(
            user_id=str(current_user.id),
            name=request.name,
            description=request.description,
            raw_input=request.raw_input,
            parsed_filters=request.parsed_filters
        )
        
        # パターン作成後、即座にレコメンド生成（バックグラウンドで非同期実行）
        import asyncio
        from app.tasks.recommendation_tasks import generate_recommendations_for_pattern
        
        # 非同期でレコメンド生成（ユーザー応答を待たない）
        asyncio.create_task(
            generate_recommendations_for_pattern(str(current_user.id), str(pattern.id))
        )
        
        return pattern
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{pattern_id}")
async def delete_pattern(
    pattern_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """投資パターンを削除"""
    service = PatternService(db)
    
    # パターン存在・所有権確認
    pattern = await service.get_pattern_by_id(pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    if str(pattern.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    success = await service.delete_pattern(pattern_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete pattern")
    
    return {"message": "Pattern deleted successfully"}


@router.patch("/{pattern_id}/toggle")
async def toggle_pattern(
    pattern_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """パターンの有効/無効を切り替え"""
    service = PatternService(db)
    
    pattern = await service.get_pattern_by_id(pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    
    if str(pattern.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated = await service.toggle_pattern_active(pattern_id)
    return {
        "message": f"Pattern {'activated' if updated.is_active else 'deactivated'}",
        "is_active": updated.is_active
    }
