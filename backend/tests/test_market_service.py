"""
マーケットサービスのテスト
"""
import pytest
import asyncio
from app.services.market_service import MarketService


@pytest.mark.asyncio
async def test_get_nikkei_225():
    """日経平均が取得できるかテスト（フォールバック含む）"""
    service = MarketService()
    
    # タイムアウト付きで実行
    try:
        result = await asyncio.wait_for(
            service.get_nikkei_225(),
            timeout=15.0
        )
        
        assert result is not None
        assert "name" in result
        assert "current" in result
        assert result["code"] == "N225"
        print(f"✅ 日経平均: {result['current']} (フォールバック: {result.get('is_fallback', False)})")
    except asyncio.TimeoutError:
        pytest.fail("日経平均の取得がタイムアウトしました")
    except Exception as e:
        pytest.fail(f"日経平均の取得に失敗: {e}")


@pytest.mark.asyncio
async def test_get_topix():
    """TOPIXが取得できるかテスト"""
    service = MarketService()
    
    try:
        result = await asyncio.wait_for(
            service.get_topix(),
            timeout=15.0
        )
        
        assert result is not None
        assert "name" in result
        assert result["code"] == "TOPX"
        print(f"✅ TOPIX: {result['current']}")
    except asyncio.TimeoutError:
        pytest.fail("TOPIXの取得がタイムアウトしました")
    except Exception as e:
        pytest.fail(f"TOPIXの取得に失敗: {e}")


@pytest.mark.asyncio
async def test_get_dow_jones():
    """NYダウが取得できるかテスト"""
    service = MarketService()
    
    try:
        result = await asyncio.wait_for(
            service.get_dow_jones(),
            timeout=15.0
        )
        
        assert result is not None
        assert "name" in result
        assert result["code"] == "DJI"
        print(f"✅ NYダウ: {result['current']}")
    except asyncio.TimeoutError:
        pytest.fail("NYダウの取得がタイムアウトしました")
    except Exception as e:
        pytest.fail(f"NYダウの取得に失敗: {e}")


@pytest.mark.asyncio
async def test_get_market_overview():
    """マーケット概況が取得できるかテスト（並列実行）"""
    service = MarketService()
    
    try:
        result = await asyncio.wait_for(
            service.get_market_overview(),
            timeout=30.0
        )
        
        assert result is not None
        assert "indices" in result
        assert "updated_at" in result
        assert "data_source" in result
        
        nikkei = result["indices"]["nikkei_225"]
        topix = result["indices"]["topix"]
        dow = result["indices"]["dow_jones"]
        
        assert nikkei is not None
        assert topix is not None
        assert dow is not None
        
        print(f"✅ 概況取得完了 (ソース: {result['data_source']}):")
        print(f"   日経平均: {nikkei['current']}")
        print(f"   TOPIX: {topix['current']}")
        print(f"   NYダウ: {dow['current']}")
        
    except asyncio.TimeoutError:
        pytest.fail("マーケット概況の取得がタイムアウトしました")
    except Exception as e:
        pytest.fail(f"マーケット概況の取得に失敗: {e}")


@pytest.mark.asyncio
async def test_fallback_data():
    """フォールバックデータが正しく設定されているかテスト"""
    service = MarketService()
    
    # フォールバックデータの検証
    assert "nikkei_225" in service._fallback_data
    assert "topix" in service._fallback_data
    assert "dow_jones" in service._fallback_data
    
    nikkei = service._fallback_data["nikkei_225"]
    assert nikkei["code"] == "N225"
    assert nikkei["current"] > 0
    
    print("✅ フォールバックデータは正常に設定されています")


if __name__ == "__main__":
    # 直接実行用
    pytest.main([__file__, "-v", "-s"])