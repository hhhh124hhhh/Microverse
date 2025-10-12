"""
AI策略基础接口定义
基于12-factor agents原则和Microverse AI框架设计
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import uuid


class ActionType(Enum):
    """AI动作类型枚举"""
    PLAY_CARD = "play_card"
    ATTACK = "attack"
    USE_HERO_POWER = "use_hero_power"
    END_TURN = "end_turn"


@dataclass
class AIAction:
    """AI动作数据结构"""
    action_type: ActionType
    confidence: float  # 0-1之间的置信度
    reasoning: str     # 决策推理过程
    parameters: Dict[str, Any]
    execution_time: float = 0.0

    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError("置信度必须在0-1之间")


@dataclass
class GameContext:
    """游戏上下文信息"""
    game_id: str
    current_player: int
    turn_number: int
    phase: str
    player_hand: List[Dict[str, Any]]
    player_field: List[Dict[str, Any]]
    opponent_field: List[Dict[str, Any]]
    player_mana: int
    opponent_mana: int
    player_health: int
    opponent_health: int


class AIStrategy(ABC):
    """AI策略基础接口"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.strategy_id = str(uuid.uuid4())
        self.total_decisions = 0
        self.successful_decisions = 0
        self.average_decision_time = 0.0

    @abstractmethod
    async def make_decision(self, context: GameContext) -> Optional[AIAction]:
        """
        基于游戏上下文做出决策

        Args:
            context: 当前游戏状态和上下文信息

        Returns:
            AIAction: 决定的动作，如果无法决策返回None
        """
        pass

    @abstractmethod
    def evaluate_board_state(self, context: GameContext) -> float:
        """
        评估当前局面分数

        Args:
            context: 游戏上下文

        Returns:
            float: 局面评分 (-1到1之间，正数表示优势)
        """
        pass

    def can_handle_context(self, context: GameContext) -> bool:
        """
        检查策略是否能处理当前上下文

        Args:
            context: 游戏上下文

        Returns:
            bool: 是否能处理
        """
        return True

    async def execute_with_timing(self, context: GameContext) -> Optional[AIAction]:
        """
        带时间统计的决策执行

        Args:
            context: 游戏上下文

        Returns:
            AIAction: 决定的动作
        """
        start_time = time.time()

        try:
            action = await self.make_decision(context)

            # 记录执行时间
            execution_time = time.time() - start_time
            if action:
                action.execution_time = execution_time

            # 更新统计信息
            self._update_statistics(execution_time, action is not None)

            return action

        except Exception as e:
            print(f"AI策略 {self.name} 执行失败: {e}")
            self._update_statistics(time.time() - start_time, False)
            return None

    def _update_statistics(self, execution_time: float, success: bool):
        """更新策略统计信息"""
        self.total_decisions += 1
        if success:
            self.successful_decisions += 1

        # 更新平均执行时间
        self.average_decision_time = (
            (self.average_decision_time * (self.total_decisions - 1) + execution_time)
            / self.total_decisions
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取策略性能统计"""
        return {
            "name": self.name,
            "strategy_id": self.strategy_id,
            "total_decisions": self.total_decisions,
            "success_rate": self.successful_decisions / max(1, self.total_decisions),
            "average_decision_time": self.average_decision_time,
            "config": self.config
        }

    def reset_statistics(self):
        """重置统计信息"""
        self.total_decisions = 0
        self.successful_decisions = 0
        self.average_decision_time = 0.0


class AIStrategyError(Exception):
    """AI策略异常基类"""
    pass


class StrategyNotAvailableError(AIStrategyError):
    """策略不可用异常"""
    pass


class InvalidContextError(AIStrategyError):
    """无效上下文异常"""
    pass