from dataclasses import dataclass
from typing import Optional

from app.services.stock_service import StockService


@dataclass
class AgentDeps:
    """
    エージェントが使用する依存性
    PydanticAIのdeps_typeに渡される
    """
    stock_service: StockService
    user_id: Optional[str] = None
    # 他のサービスが必要になったらここに追加
    # news_service: Optional[NewsService] = None
    # pattern_service: Optional[PatternService] = None
