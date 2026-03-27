import pytest
from unittest.mock import MagicMock
from dataclasses import dataclass


# ==========================================
# Mock Data Classes
# ==========================================

@dataclass
class MockStockSearchResult:
    """モック用銘柄検索結果"""
    code: str
    name: str
    market: str = "東証プライム"
    sector: str = "テクノロジー"
    industry: str = "ITサービス"


# ==========================================
# GET /stocks/ (Search)
# ==========================================

@pytest.mark.asyncio
async def test_search_stocks_success(async_http_client, auth_headers, mock_stock_search_service):
    """銘柄検索成功（モック使用）"""
    # モックの戻り値を設定
    mock_results = [
        MockStockSearchResult(
            code="7203",
            name="トヨタ自動車",
            market="東証プライム",
            sector="輸送用機器"
        ),
        MockStockSearchResult(
            code="6758",
            name="ソニーグループ",
            market="東証プライム",
            sector="電気機器"
        ),
    ]
    mock_stock_search_service.search.return_value = mock_results
    
    response = await async_http_client.get(
        "/api/v1/stocks/",
        params={"q": "トヨタ"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["code"] == "7203"
    assert data[0]["name"] == "トヨタ自動車"
    assert data[1]["code"] == "6758"
    
    # モックが呼ばれたことを確認
    mock_stock_search_service.search.assert_called_once_with("トヨタ", 20)


@pytest.mark.asyncio
async def test_search_stocks_no_results(async_http_client, auth_headers, mock_stock_search_service):
    """検索結果なし"""
    mock_stock_search_service.search.return_value = []
    
    response = await async_http_client.get(
        "/api/v1/stocks/",
        params={"q": "存在しない銘柄"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_search_stocks_custom_limit(async_http_client, auth_headers, mock_stock_search_service):
    """カスタム件数指定"""
    mock_stock_search_service.search.return_value = []
    
    response = await async_http_client.get(
        "/api/v1/stocks/",
        params={"q": "テスト", "limit": 5},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    mock_stock_search_service.search.assert_called_once_with("テスト", 5)


@pytest.mark.asyncio
async def test_search_stocks_unauthorized(async_http_client, mock_stock_search_service):
    """認証なしで検索"""
    response = await async_http_client.get("/api/v1/stocks/", params={"q": "テスト"})
    
    assert response.status_code == 401
    mock_stock_search_service.search.assert_not_called()


@pytest.mark.asyncio
async def test_search_stocks_missing_query(async_http_client, auth_headers):
    """検索キーワードなし"""
    response = await async_http_client.get("/api/v1/stocks/", headers=auth_headers)
    
    assert response.status_code == 422  # バリデーションエラー


@pytest.mark.asyncio
async def test_search_stocks_limit_too_large(async_http_client, auth_headers, mock_stock_search_service):
    """上限超過の件数"""
    mock_stock_search_service.search.return_value = []
    
    response = await async_http_client.get(
        "/api/v1/stocks/",
        params={"q": "テスト", "limit": 100},
        headers=auth_headers
    )
    
    assert response.status_code == 422


# ==========================================
# GET /stocks/{code}/detail
# ==========================================

@pytest.mark.asyncio
async def test_get_stock_detail_success(async_http_client, auth_headers, mock_stock_search_service):
    """銘柄詳細取得成功"""
    # モック設定
    from app.services.stock_search_service import StockSearchResult
    
    mock_stock_search_service.get_stock_info.return_value = StockSearchResult(
        code="7203",
        name="トヨタ自動車",
        market="東証プライム",
        sector="輸送用機器"
    )
    
    mock_stock_search_service.get_price_data.return_value = {
        "price": 2500.0,
        "change": 50.0,
        "change_percent": 2.04,
        "date": "2024-01-15"
    }
    
    response = await async_http_client.get(
        "/api/v1/stocks/7203/detail",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "7203"
    assert data["name"] == "トヨタ自動車"
    assert data["price"] == 2500.0
    
    # モックが呼ばれたことを確認
    mock_stock_search_service.get_stock_info.assert_called_once_with("7203")
    mock_stock_search_service.get_price_data.assert_called_once_with("7203")


@pytest.mark.asyncio
async def test_get_stock_detail_not_found(async_http_client, auth_headers, mock_stock_search_service):
    """銘柄が見つからない"""
    mock_stock_search_service.get_stock_info.return_value = None
    mock_stock_search_service.get_price_data.return_value = None
    
    response = await async_http_client.get(
        "/api/v1/stocks/NOTFOUND/detail",
        headers=auth_headers
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_stock_detail_unauthorized(async_http_client, mock_stock_search_service):
    """認証なしで詳細取得"""
    response = await async_http_client.get("/api/v1/stocks/7203/detail")
    
    assert response.status_code == 401


# ==========================================
# GET /stocks/{code}/price
# ==========================================

@pytest.mark.asyncio
async def test_get_stock_price_success(async_http_client, auth_headers, mock_stock_search_service):
    """株価取得成功"""
    mock_stock_search_service.get_price_data.return_value = {
        "price": 3000.0,
        "change": 100.0,
        "change_percent": 3.45,
        "date": "2024-01-15",
        "volume": 1000000
    }
    
    response = await async_http_client.get(
        "/api/v1/stocks/6758/price",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 3000.0
    assert data["change"] == 100.0
    assert data["change_percent"] == 3.45
    
    mock_stock_search_service.get_price_data.assert_called_once_with("6758")


@pytest.mark.asyncio
async def test_get_stock_price_not_found(async_http_client, auth_headers, mock_stock_search_service):
    """株価データが見つからない"""
    mock_stock_search_service.get_price_data.return_value = None
    
    response = await async_http_client.get(
        "/api/v1/stocks/NOTFOUND/price",
        headers=auth_headers
    )
    
    assert response.status_code == 404


# ==========================================
# GET /stocks/{code}/history
# ==========================================

@pytest.mark.asyncio
async def test_get_stock_history_success(async_http_client, auth_headers, mock_stock_search_service):
    """過去の株価データ取得成功"""
    mock_stock_search_service.get_historical_prices.return_value = [
        {"date": "2024-01-10", "close": 2400.0},
        {"date": "2024-01-11", "close": 2450.0},
        {"date": "2024-01-12", "close": 2500.0},
    ]
    
    response = await async_http_client.get(
        "/api/v1/stocks/7203/history",
        params={"period": "1mo"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "7203"
    assert data["period"] == "1mo"
    assert "prices" in data
    assert len(data["prices"]) == 3
    
    mock_stock_search_service.get_historical_prices.assert_called_once_with("7203", "1mo")


@pytest.mark.asyncio
async def test_get_stock_history_custom_period(async_http_client, auth_headers, mock_stock_search_service):
    """カスタム期間指定"""
    mock_stock_search_service.get_historical_prices.return_value = []
    
    response = await async_http_client.get(
        "/api/v1/stocks/7203/history",
        params={"period": "3mo"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    mock_stock_search_service.get_historical_prices.assert_called_once_with("7203", "3mo")


@pytest.mark.asyncio
async def test_get_stock_history_default_period(async_http_client, auth_headers, mock_stock_search_service):
    """デフォルト期間（1mo）"""
    mock_stock_search_service.get_historical_prices.return_value = []
    
    response = await async_http_client.get(
        "/api/v1/stocks/7203/history",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    mock_stock_search_service.get_historical_prices.assert_called_once_with("7203", "1mo")


@pytest.mark.asyncio
async def test_get_stock_history_not_found(async_http_client, auth_headers, mock_stock_search_service):
    """履歴データが見つからない"""
    mock_stock_search_service.get_historical_prices.return_value = None
    
    response = await async_http_client.get(
        "/api/v1/stocks/NOTFOUND/history",
        headers=auth_headers
    )
    
    assert response.status_code == 404
