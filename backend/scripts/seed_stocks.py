"""
銘柄データシードスクリプト
東証上場銘柄をデータベースに投入
"""
import asyncio
import csv
import io
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.models import Stock
from app.services.stock_service import StockService


# 主要銘柄のモックデータ（開発用）
# 実際の運用では、東証からのCSVデータやAPIを使用
MOCK_STOCKS = [
    # 日経平均株価構成銘柄（一部）
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
    {"code": "7741", "name": "HOYA", "market": "東証プライム", "sector": "精密機器"},
    {"code": "8001", "name": "伊藤忠商事", "market": "東証プライム", "sector": "卸売"},
    {"code": "4452", "name": "花王", "market": "東証プライム", "sector": "化学"},
    {"code": "4607", "name": "中外製薬", "market": "東証プライム", "sector": "医薬品"},
    {"code": "4661", "name": "オリエンタルランド", "market": "東証プライム", "sector": "サービス"},
    {"code": "8766", "name": "東京海上ホールディングス", "market": "東証プライム", "sector": "保険"},
    {"code": "9020", "name": "東日本旅客鉄道", "market": "東証プライム", "sector": "鉄道・バス"},
    {"code": "9433", "name": "KDDI", "market": "東証プライム", "sector": "情報・通信"},
    {"code": "4502", "name": "武田薬品工業", "market": "東証プライム", "sector": "医薬品"},
    {"code": "6752", "name": "パナソニックホールディングス", "market": "東証プライム", "sector": "電気機器"},
    {"code": "7270", "name": "SUBARU", "market": "東証プライム", "sector": "輸送用機器"},
    {"code": "4503", "name": "アステラス製薬", "market": "東証プライム", "sector": "医薬品"},
    {"code": "9022", "name": "東海旅客鉄道", "market": "東証プライム", "sector": "鉄道・バス"},
    {"code": "8002", "name": "丸紅", "market": "東証プライム", "sector": "卸売"},
    {"code": "8411", "name": "みずほフィナンシャルグループ", "market": "東証プライム", "sector": "銀行"},
    {"code": "8767", "name": "MS&ADインシュアランスグループ", "market": "東証プライム", "sector": "保険"},
    {"code": "6367", "name": "ダイキン工業", "market": "東証プライム", "sector": "機械"},
    {"code": "6902", "name": "デンソー", "market": "東証プライム", "sector": "電気機器"},
    {"code": "6301", "name": "小松製作所", "market": "東証プライム", "sector": "機械"},
    {"code": "9021", "name": "西日本旅客鉄道", "market": "東証プライム", "sector": "鉄道・バス"},
    {"code": "3382", "name": "セブン＆アイ・ホールディングス", "market": "東証プライム", "sector": "小売"},
    {"code": "8113", "name": "ユニ・チャーム", "market": "東証プライム", "sector": "パルプ・紙"},
    {"code": "9434", "name": "ソフトバンク", "market": "東証プライム", "sector": "情報・通信"},
    {"code": "8053", "name": "住友商事", "market": "東証プライム", "sector": "卸売"},
    {"code": "6501", "name": "日立製作所", "market": "東証プライム", "sector": "電気機器"},
    {"code": "4061", "name": "デンカ", "market": "東証プライム", "sector": "化学"},
    {"code": "4568", "name": "第一三共", "market": "東証プライム", "sector": "医薬品"},
    {"code": "9613", "name": "NTTデータグループ", "market": "東証プライム", "sector": "情報・通信"},
    {"code": "2269", "name": "明治ホールディングス", "market": "東証プライム", "sector": "食料品"},
    {"code": "2502", "name": "アサヒグループホールディングス", "market": "東証プライム", "sector": "食料品"},
    {"code": "7003", "name": "三菱重工業", "market": "東証プライム", "sector": "機械"},
    {"code": "2413", "name": "エブリシング", "market": "東証プライム", "sector": "サービス"},
]


async def seed_stocks():
    """銘柄データをシード"""
    async with AsyncSessionLocal() as db:
        print(f"🌱 Seeding {len(MOCK_STOCKS)} stocks...")
        
        created_count = 0
        skipped_count = 0
        
        for stock_data in MOCK_STOCKS:
            # 既存チェック
            existing = await db.execute(
                select(Stock).where(Stock.code == stock_data["code"])
            )
            if existing.scalar_one_or_none():
                skipped_count += 1
                continue
            
            # 新規作成
            stock = Stock(
                code=stock_data["code"],
                name=stock_data["name"],
                market=stock_data.get("market"),
                sector=stock_data.get("sector"),
            )
            db.add(stock)
            created_count += 1
            
            # 10件ごとにコミット
            if created_count % 10 == 0:
                await db.commit()
                print(f"  ... {created_count} stocks created")
        
        await db.commit()
        print(f"✅ Done! Created: {created_count}, Skipped: {skipped_count}")


async def fetch_stock_prices():
    """シード後の株価データ取得"""
    async with AsyncSessionLocal() as db:
        stock_service = StockService(db)
        stocks = await stock_service.get_all_stocks()
        
        print(f"\n📊 Fetching prices for {len(stocks)} stocks...")
        
        success_count = 0
        failed_count = 0
        
        for stock in stocks:
            try:
                price = await stock_service.fetch_and_save_price(stock.code)
                if price:
                    success_count += 1
                    print(f"  ✓ {stock.code}: {stock.name}")
                else:
                    failed_count += 1
                    print(f"  ✗ {stock.code}: No data")
            except Exception as e:
                failed_count += 1
                print(f"  ✗ {stock.code}: {e}")
        
        print(f"\n✅ Prices fetched! Success: {success_count}, Failed: {failed_count}")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/app")
    
    from app.models import Stock
    from sqlalchemy import select
    
    print("🚀 Starting database seed...\n")
    
    # 銘柄シード
    asyncio.run(seed_stocks())
    
    # 株価取得
    # asyncio.run(fetch_stock_prices())
    
    print("\n🎉 Seed completed!")
