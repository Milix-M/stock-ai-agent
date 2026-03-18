from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.users import get_current_user
from app.services.stock_service import StockService

router = APIRouter()


@router.post("/seed")
async def seed_database(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    開発用: データベースに銘柄データをシード
    """
    # 簡易的な管理者チェック（実際の運用では適切な権限管理が必要）
    import os
    
    stock_service = StockService(db)
    
    # モック銘柄データ
    mock_stocks = [
        {"code": "7203", "name": "トヨタ自動車", "market": "東証プライム", "sector": "輸送用機器"},
        {"code": "6758", "name": "ソニーグループ", "market": "東証プライム", "sector": "電気機器"},
        {"code": "9984", "name": "ソフトバンクグループ", "market": "東証プライム", "sector": "情報・通信"},
        {"code": "8306", "name": "三菱UFJフィナンシャル・グループ", "market": "東証プライム", "sector": "銀行"},
        {"code": "6861", "name": "キーエンス", "market": "東証プライム", "sector": "電気機器"},
        {"code": "8058", "name": "三菱商事", "market": "東証プライム", "sector": "卸売"},
        {"code": "9432", "name": "日本電信電話", "market": "東証プライム", "sector": "情報・通信"},
        {"code": "6098", "name": "リクルートホールディングス", "market": "東証プライム", "sector": "サービス"},
        {"code": "4523", "name": "エーザイ", "market": "東証プライム", "sector": "医薬品"},
        {"code": "8035", "name": "東京エレクトロン", "market": "東証プライム", "sector": "電気機器"},
        {"code": "2914", "name": "日本たばこ産業", "market": "東証プライム", "sector": "食料品"},
        {"code": "4063", "name": "信越化学工業", "market": "東証プライム", "sector": "化学"},
        {"code": "7267", "name": "本田技研工業", "market": "東証プライム", "sector": "輸送用機器"},
        {"code": "6178", "name": "日本郵政", "market": "東証スタンダード", "sector": "郵便"},
        {"code": "5108", "name": "ブリヂストン", "market": "東証プライム", "sector": "ゴム製品"},
    ]
    
    created = 0
    skipped = 0
    
    for stock_data in mock_stocks:
        existing = await stock_service.get_stock_by_code(stock_data["code"])
        if existing:
            skipped += 1
            continue
        
        await stock_service.create_stock(
            code=stock_data["code"],
            name=stock_data["name"],
            market=stock_data.get("market"),
            sector=stock_data.get("sector")
        )
        created += 1
    
    return {
        "message": "Database seeded successfully",
        "created": created,
        "skipped": skipped,
        "total": len(mock_stocks)
    }
