from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any
from pydantic_ai import Agent
from pydantic_ai.result import RunResult

ResultT = TypeVar("ResultT")


class BaseAgent(ABC, Generic[ResultT]):
    """
    全エージェントの基底クラス
    PydanticAIのAgentをラップし、共通機能を提供
    """
    
    def __init__(self, agent: Agent, memory=None, ops=None):
        self.agent = agent
        self.memory = memory
        self.ops = ops
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def run(self, context: dict) -> RunResult[ResultT]:
        """エージェントのメイン実行ロジック"""
        pass
    
    async def execute(self, context: dict) -> RunResult[ResultT]:
        """
        実行ラッパー（トレース・ログ記録）
        """
        # TODO: AgentOpsでトレース記録
        try:
            result = await self.run(context)
            return result
        except Exception as e:
            # TODO: エラーログ記録
            raise
