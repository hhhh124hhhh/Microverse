"""
AI引擎管理器
负责管理多种AI策略，实现策略选择和协调
基于12-factor agents原则设计
"""
import asyncio
import time
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

from .strategies.base import AIStrategy, AIAction, GameContext, ActionType, AIStrategyError
from .strategies.rule_based import RuleBasedStrategy
from .debug_tools import debugger


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIEngineConfig:
    """AI引擎配置"""
    default_strategy: str = "rule_based"
    max_decision_time: float = 20.0  # 增加到20秒，与配置文件保持一致
    enable_learning: bool = True
    enable_monitoring: bool = True
    strategy_configs: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.strategy_configs is None:
            self.strategy_configs = {}


class AIEngine:
    """AI引擎管理器"""

    def __init__(self, config: AIEngineConfig):
        self.config = config
        self.strategies: Dict[str, AIStrategy] = {}
        self.current_strategy: Optional[str] = None
        self.performance_history: List[Dict[str, Any]] = []
        self.total_games_played = 0
        self.total_decisions_made = 0

        # 注册内置策略
        self._register_builtin_strategies()

    def _register_builtin_strategies(self):
        """注册内置AI策略"""
        # 注册规则AI
        rule_config = self.config.strategy_configs.get("rule_based", {})
        self.register_strategy("rule_based", RuleBasedStrategy, rule_config)

    def register_strategy(self, name: str, strategy, config: Dict[str, Any] = None):
        """
        注册AI策略

        Args:
            name: 策略名称
            strategy: 策略实例或策略类
            config: 策略配置（如果strategy是类）
        """
        try:
            if isinstance(strategy, type):
                # 如果是策略类，需要实例化
                strategy_instance = strategy(name, config or {})
            else:
                # 如果是策略实例，直接使用
                strategy_instance = strategy

            self.strategies[name] = strategy_instance
            logger.info(f"成功注册AI策略: {name}")
        except Exception as e:
            logger.error(f"注册AI策略失败 {name}: {e}")
            raise AIStrategyError(f"无法注册策略 {name}: {e}")

    def unregister_strategy(self, name: str):
        """注销AI策略"""
        if name in self.strategies:
            del self.strategies[name]
            if self.current_strategy == name:
                self.current_strategy = None
            logger.info(f"成功注销AI策略: {name}")

    def set_strategy(self, strategy_name: str) -> bool:
        """
        设置当前使用的AI策略

        Args:
            strategy_name: 策略名称

        Returns:
            bool: 设置是否成功
        """
        if strategy_name not in self.strategies:
            logger.error(f"策略 {strategy_name} 不存在")
            return False

        self.current_strategy = strategy_name
        logger.info(f"切换到AI策略: {strategy_name}")
        return True

    def get_available_strategies(self) -> List[str]:
        """获取所有可用的AI策略"""
        return list(self.strategies.keys())

    async def make_decision(self, context: GameContext, strategy_name: Optional[str] = None) -> Optional[AIAction]:
        """
        基于游戏上下文做出AI决策

        Args:
            context: 游戏上下文
            strategy_name: 指定策略名称，如果为None则使用当前策略

        Returns:
            AIAction: AI决定的动作
        """
        # 确定使用的策略
        if strategy_name is None:
            strategy_name = self.current_strategy or self.config.default_strategy

        if strategy_name not in self.strategies:
            logger.error(f"策略 {strategy_name} 不可用")
            return None

        strategy = self.strategies[strategy_name]

        # 检查策略是否能处理当前上下文
        if not strategy.can_handle_context(context):
            logger.warning(f"策略 {strategy_name} 无法处理当前上下文")
            return None

        try:
            # 执行决策，带超时控制
            start_time = time.time()
            action = await asyncio.wait_for(
                strategy.execute_with_timing(context),
                timeout=self.config.max_decision_time
            )
            execution_time = time.time() - start_time

            # 记录决策
            self._record_decision(context, strategy_name, action, execution_time)

            if action:
                logger.info(f"AI决策完成: {action.action_type.value}, "
                          f"置信度: {action.confidence:.2f}, "
                          f"耗时: {action.execution_time:.3f}s")
                self.total_decisions_made += 1

                # 记录到调试工具
                debugger.record_decision(action, strategy_name, context)

            return action

        except asyncio.TimeoutError:
            logger.error(f"AI决策超时: {strategy_name}")
            return None
        except Exception as e:
            logger.error(f"AI决策失败: {e}")
            return None

    def _record_decision(self, context: GameContext, strategy_name: str,
                        action: Optional[AIAction], execution_time: float):
        """记录AI决策历史"""
        if not self.config.enable_monitoring:
            return

        record = {
            "timestamp": time.time(),
            "game_id": context.game_id,
            "turn_number": context.turn_number,
            "strategy_name": strategy_name,
            "action_type": action.action_type.value if action else None,
            "confidence": action.confidence if action else None,
            "reasoning": action.reasoning if action else None,
            "execution_time": execution_time,
            "board_score": self.strategies[strategy_name].evaluate_board_state(context)
        }

        self.performance_history.append(record)

        # 限制历史记录数量
        if len(self.performance_history) > 10000:
            self.performance_history = self.performance_history[-5000:]

    def get_strategy_performance(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """获取策略性能统计"""
        if strategy_name not in self.strategies:
            return None

        strategy = self.strategies[strategy_name]
        base_stats = strategy.get_performance_stats()

        # 添加引擎级别的统计
        strategy_records = [r for r in self.performance_history if r["strategy_name"] == strategy_name]

        if strategy_records:
            avg_confidence = sum(r["confidence"] or 0 for r in strategy_records) / len(strategy_records)
            avg_execution_time = sum(r["execution_time"] for r in strategy_records) / len(strategy_records)

            base_stats.update({
                "engine_avg_confidence": avg_confidence,
                "engine_avg_execution_time": avg_execution_time,
                "total_decisions_in_engine": len(strategy_records)
            })

        return base_stats

    def get_engine_stats(self) -> Dict[str, Any]:
        """获取引擎整体统计信息"""
        return {
            "total_games_played": self.total_games_played,
            "total_decisions_made": self.total_decisions_made,
            "available_strategies": self.get_available_strategies(),
            "current_strategy": self.current_strategy,
            "total_performance_records": len(self.performance_history),
            "config": asdict(self.config)
        }

    def start_new_game(self, game_id: str):
        """开始新游戏时的初始化"""
        self.total_games_played += 1
        logger.info(f"开始新游戏: {game_id}")

    def reset_statistics(self):
        """重置所有统计信息"""
        self.total_games_played = 0
        self.total_decisions_made = 0
        self.performance_history.clear()

        for strategy in self.strategies.values():
            strategy.reset_statistics()

        logger.info("AI引擎统计信息已重置")

    def save_performance_data(self, file_path: str):
        """保存性能数据到文件"""
        import json
        data = {
            "engine_stats": self.get_engine_stats(),
            "strategy_performance": {
                name: self.get_strategy_performance(name)
                for name in self.strategies.keys()
            },
            "decision_history": self.performance_history[-1000:]  # 只保存最近1000条
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"性能数据已保存到: {file_path}")

    def load_performance_data(self, file_path: str):
        """从文件加载性能数据"""
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 这里可以恢复一些统计数据
            logger.info(f"性能数据已从 {file_path} 加载")
        except Exception as e:
            logger.error(f"加载性能数据失败: {e}")

    def auto_select_best_strategy(self) -> str:
        """基于历史性能自动选择最佳策略"""
        if not self.strategies:
            return self.config.default_strategy

        best_strategy = None
        best_score = -1

        for strategy_name in self.strategies.keys():
            performance = self.get_strategy_performance(strategy_name)
            if performance and performance.get("success_rate", 0) > 0:
                # 综合评分：成功率 * (1 / 平均执行时间)
                score = performance["success_rate"]
                if performance.get("average_decision_time", 0) > 0:
                    score *= (1 / performance["average_decision_time"])

                if score > best_score:
                    best_score = score
                    best_strategy = strategy_name

        if best_strategy:
            self.set_strategy(best_strategy)
            logger.info(f"自动选择最佳策略: {best_strategy} (评分: {best_score:.2f})")
            return best_strategy

        return self.config.default_strategy