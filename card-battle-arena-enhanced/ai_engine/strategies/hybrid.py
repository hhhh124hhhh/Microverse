"""
混合AI决策系统
结合多种AI策略，实现更智能和鲁棒的决策
基于集成学习的思想，采用投票和权重机制
"""
import asyncio
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from .base import AIStrategy, AIAction, ActionType, GameContext, AIStrategyError
from .rule_based import RuleBasedStrategy
from .llm_enhanced import LLMEnhancedStrategy


logger = logging.getLogger(__name__)


class ConsensusMethod(Enum):
    """共识方法枚举"""
    WEIGHTED_VOTING = "weighted_voting"  # 加权投票
    MAJORITY_VOTING = "majority_voting"  # 多数投票
    CONFIDENCE_BASED = "confidence_based"  # 基于置信度
    PERFORMANCE_BASED = "performance_based"  # 基于历史性能


@dataclass
class StrategyWeight:
    """策略权重配置"""
    strategy_name: str
    weight: float
    min_confidence: float = 0.3
    max_votes: int = 1


@dataclass
class HybridDecision:
    """混合决策结果"""
    action: AIAction
    consensus_score: float  # 共识程度 0-1
    participating_strategies: List[str]
    voting_details: Dict[str, Any]
    execution_time: float


class HybridAIStrategy(AIStrategy):
    """混合AI策略"""

    def __init__(self, name: str = "混合AI", config: Dict[str, Any] = None):
        default_config = {
            # 策略配置 - 平衡权重，让LLM有更多话语权
            "strategies": [
                {"name": "rule_based", "weight": 0.55, "min_confidence": 0.15},  # 降低规则策略权重，降低要求
                {"name": "llm_enhanced", "weight": 0.45, "min_confidence": 0.4}   # 提高LLM权重，降低要求
            ],

            # 共识方法
            "consensus_method": ConsensusMethod.WEIGHTED_VOTING.value,

            # 性能阈值
            "min_consensus_score": 0.15,  # 进一步降低最小共识分数
            "max_decision_time": 25.0,    # 增加最大决策时间，给LLM更多时间

            # 自适应配置
            "enable_adaptive_weights": True,  # 启用自适应权重
            "performance_window": 10,         # 减少性能评估窗口，更快适应
            "weight_adjustment_factor": 0.2,  # 提高权重调整因子，更快调整

            # 容错配置
            "fallback_strategy": "rule_based",
            "min_participating_strategies": 1,
            "enable_strategy_replacement": True,

            # 优化：LLM超时处理配置
            "llm_timeout_handling": "graceful_degradation",  # 优雅降级
            "llm_timeout_grace_period": 20.0,  # 增加LLM超时宽限期
            "fallback_to_rules_on_timeout": True,  # 超时时优先使用规则策略
            "prefer_cards_over_hero_power": True  # 新增：优先出牌而不是英雄技能
        }

        if config:
            default_config.update(config)

        super().__init__(name, default_config)

        # 初始化子策略
        self.sub_strategies: Dict[str, AIStrategy] = {}
        self.strategy_weights: Dict[str, float] = {}
        self.strategy_performance: Dict[str, List[float]] = {}

        # 统计信息
        self.consensus_history: List[float] = []
        self.strategy_usage_count: Dict[str, int] = {}
        self.decisions_made = 0
        self.consensus_failures = 0

        # 初始化策略
        self._initialize_strategies()

    def _initialize_strategies(self):
        """初始化子策略"""
        for strategy_config in self.config["strategies"]:
            strategy_name = strategy_config["name"]
            weight = strategy_config["weight"]

            if strategy_name == "rule_based":
                strategy = RuleBasedStrategy(f"{self.name}_规则层")
            elif strategy_name == "llm_enhanced":
                llm_config = self.config.get("llm_config", {})
                strategy = LLMEnhancedStrategy(f"{self.name}_LLM层", llm_config)
            else:
                logger.warning(f"未知策略类型: {strategy_name}")
                continue

            self.sub_strategies[strategy_name] = strategy
            self.strategy_weights[strategy_name] = weight
            self.strategy_performance[strategy_name] = []
            self.strategy_usage_count[strategy_name] = 0

            logger.info(f"初始化子策略: {strategy_name}, 权重: {weight}")

    def register_sub_strategy(self, name: str, strategy: AIStrategy, weight: float = 1.0):
        """注册子策略"""
        self.sub_strategies[name] = strategy
        self.strategy_weights[name] = weight
        self.strategy_performance[name] = []
        self.strategy_usage_count[name] = 0
        logger.info(f"注册子策略: {name}, 权重: {weight}")

    def set_llm_manager(self, llm_manager):
        """设置LLM管理器"""
        for strategy in self.sub_strategies.values():
            if hasattr(strategy, 'set_llm_manager'):
                strategy.set_llm_manager(llm_manager)

    async def make_decision(self, context: GameContext) -> Optional[AIAction]:
        """
        使用混合策略做出决策
        """
        start_time = time.time()
        logger.info("🎯 混合AI开始决策过程...")

        try:
            # 获取所有子策略的决策
            logger.info("📊 步骤1: 收集各策略决策...")
            strategy_decisions = await self._collect_strategy_decisions(context)

            if not strategy_decisions:
                logger.warning("❌ 没有策略返回有效决策，使用回退策略")
                return await self._fallback_decision(context)

            # 显示收集到的决策
            logger.info(f"✅ 收集到 {len(strategy_decisions)} 个策略决策:")
            for strategy_name, action in strategy_decisions:
                logger.info(f"   - {strategy_name}: {action.action_type.value} (置信度: {action.confidence:.2f})")

            # 生成混合决策
            logger.info("🔄 步骤2: 生成混合决策...")
            hybrid_decision = await self._generate_hybrid_decision(strategy_decisions, context)

            # 验证决策质量
            logger.info("✔️ 步骤3: 验证决策质量...")
            if not self._validate_decision(hybrid_decision):
                logger.warning(f"❌ 混合决策未通过验证 (共识分数: {hybrid_decision.consensus_score:.2f})，使用回退策略")
                return await self._fallback_decision(context)

            # 更新性能统计
            execution_time = time.time() - start_time
            self._update_performance_stats(hybrid_decision, execution_time)

            # 自适应调整权重
            if self.config["enable_adaptive_weights"]:
                logger.info("🔧 步骤4: 自适应调整权重...")
                self._adaptive_weight_adjustment(hybrid_decision)

            self.decisions_made += 1
            logger.info(f"🎉 混合AI决策完成: {hybrid_decision.action.action_type.value}, "
                      f"共识分数: {hybrid_decision.consensus_score:.2f}, "
                      f"耗时: {hybrid_decision.execution_time:.3f}s")
            logger.info(f"💭 推理过程: {hybrid_decision.action.reasoning}")

            # 显示参与决策的策略
            if hybrid_decision.participating_strategies:
                logger.info(f"👥 参与策略: {', '.join(hybrid_decision.participating_strategies)}")

            return hybrid_decision.action

        except Exception as e:
            logger.error(f"💥 混合AI决策失败: {e}")
            self.consensus_failures += 1
            return await self._fallback_decision(context)

    async def _collect_strategy_decisions(self, context: GameContext) -> List[Tuple[str, AIAction]]:
        """收集所有子策略的决策"""
        decisions = []
        tasks = []

        # 并行执行所有策略
        for strategy_name, strategy in self.sub_strategies.items():
            if strategy.can_handle_context(context):
                task = asyncio.create_task(
                    self._execute_strategy_with_timeout(strategy, strategy_name, context)
                )
                tasks.append(task)

        # 等待所有策略完成
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, tuple) and result[0] and result[1]:
                    decisions.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"策略执行异常: {result}")

        return decisions

    async def _execute_strategy_with_timeout(self, strategy: AIStrategy,
                                          strategy_name: str,
                                          context: GameContext) -> Tuple[str, Optional[AIAction]]:
        """带超时的策略执行"""
        try:
            # 根据配置动态设置超时时间
            if strategy_name == "llm_enhanced":
                timeout = self.config.get("llm_timeout_grace_period", 15.0)
                logger.info(f"🧠 执行LLM增强策略（超时: {timeout}秒）...")
            else:
                timeout = 6.0  # 规则策略给6秒，稍微增加但保持响应性
                logger.info(f"📋 执行规则策略（超时: {timeout}秒）...")

            action = await asyncio.wait_for(
                strategy.execute_with_timing(context),
                timeout=timeout
            )

            if action:
                self.strategy_usage_count[strategy_name] += 1
                logger.info(f"✅ 策略 {strategy_name} 决策完成: {action.action_type.value}, "
                          f"置信度: {action.confidence:.2f}, 耗时: {action.execution_time:.3f}s")
                return strategy_name, action
            else:
                logger.warning(f"❌ 策略 {strategy_name} 无法做出决策")

        except asyncio.TimeoutError:
            logger.warning(f"⏰ 策略 {strategy_name} 执行超时（{timeout}秒）")

            # LLM策略超时时的特殊处理
            if strategy_name == "llm_enhanced" and self.config.get("fallback_to_rules_on_timeout", True):
                logger.info("🔄 LLM策略超时，启动优雅降级机制...")
                # 立即执行规则策略作为回退
                if "rule_based" in self.sub_strategies:
                    try:
                        rule_strategy = self.sub_strategies["rule_based"]
                        fallback_action = await asyncio.wait_for(
                            rule_strategy.execute_with_timing(context),
                            timeout=3.0
                        )
                        if fallback_action:
                            logger.info(f"🛡️ 规则策略回退成功: {fallback_action.action_type.value}")
                            return "rule_based_fallback", fallback_action
                    except Exception as fallback_error:
                        logger.error(f"回退规则策略也失败: {fallback_error}")

        except Exception as e:
            logger.error(f"💥 策略 {strategy_name} 执行失败: {e}")

        return strategy_name, None

    async def _generate_hybrid_decision(self, strategy_decisions: List[Tuple[str, AIAction]],
                                      context: GameContext) -> HybridDecision:
        """生成混合决策"""
        consensus_method = ConsensusMethod(self.config["consensus_method"])

        if consensus_method == ConsensusMethod.WEIGHTED_VOTING:
            return self._weighted_voting_decision(strategy_decisions, context)
        elif consensus_method == ConsensusMethod.MAJORITY_VOTING:
            return self._majority_voting_decision(strategy_decisions, context)
        elif consensus_method == ConsensusMethod.CONFIDENCE_BASED:
            return self._confidence_based_decision(strategy_decisions, context)
        elif consensus_method == ConsensusMethod.PERFORMANCE_BASED:
            return self._performance_based_decision(strategy_decisions, context)
        else:
            return self._weighted_voting_decision(strategy_decisions, context)

    def _weighted_voting_decision(self, strategy_decisions: List[Tuple[str, AIAction]],
                                context: GameContext) -> HybridDecision:
        """加权投票决策"""
        # 按动作类型分组
        action_groups = {}
        for strategy_name, action in strategy_decisions:
            action_type = action.action_type
            if action_type not in action_groups:
                action_groups[action_type] = []
            action_groups[action_type].append((strategy_name, action))

        # 计算每个动作组的加权分数
        best_action = None
        best_score = -1
        best_details = {}

        for action_type, actions in action_groups.items():
            total_weight = 0
            total_confidence = 0
            participating_strategies = []

            for strategy_name, action in actions:
                weight = self.strategy_weights.get(strategy_name, 1.0)
                confidence = action.confidence

                # 应用出牌优先策略
                if self.config.get("prefer_cards_over_hero_power", False):
                    if action_type == ActionType.PLAY_CARD:
                        # 在出牌和英雄技能之间选择时，优先出牌
                        confidence *= 1.3  # 给出牌30%的加成
                    elif action_type == ActionType.USE_HERO_POWER:
                        # 如果有出牌选项，降低英雄技能优先级
                        if ActionType.PLAY_CARD in action_groups:
                            confidence *= 0.7  # 给英雄技能30%的惩罚

                total_weight += weight
                total_confidence += weight * confidence
                participating_strategies.append(strategy_name)

            # 平均置信度
            avg_confidence = total_confidence / max(1, total_weight)

            if avg_confidence > best_score:
                best_score = avg_confidence
                # 选择置信度最高的动作作为代表
                best_action = max(actions, key=lambda x: x[1].confidence)[1]
                best_details = {
                    "method": "weighted_voting",
                    "total_weight": total_weight,
                    "avg_confidence": avg_confidence,
                    "action_count": len(actions),
                    "prefer_cards": self.config.get("prefer_cards_over_hero_power", False)
                }

        # 计算共识分数
        consensus_score = self._calculate_consensus_score(strategy_decisions, best_action)

        return HybridDecision(
            action=best_action or AIAction(ActionType.END_TURN, 0.5, "无有效决策", {}),
            consensus_score=consensus_score,
            participating_strategies=[s[0] for s in strategy_decisions],
            voting_details=best_details,
            execution_time=0.0
        )

    def _majority_voting_decision(self, strategy_decisions: List[Tuple[str, AIAction]],
                                context: GameContext) -> HybridDecision:
        """多数投票决策"""
        # 统计每个动作类型的投票数
        action_votes = {}
        for strategy_name, action in strategy_decisions:
            action_type = action.action_type
            if action_type not in action_votes:
                action_votes[action_type] = []
            action_votes[action_type].append((strategy_name, action))

        # 找到投票数最多的动作类型
        if not action_votes:
            best_action_type = ActionType.END_TURN
            best_actions = []
        else:
            best_action_type = max(action_votes.keys(), key=lambda x: len(action_votes[x]))
            best_actions = action_votes[best_action_type]

        # 选择置信度最高的动作
        best_action = max(best_actions, key=lambda x: x[1].confidence)[1] if best_actions else None

        # 计算共识分数（基于投票比例）
        total_votes = len(strategy_decisions)
        majority_votes = len(best_actions)
        consensus_score = majority_votes / max(1, total_votes)

        voting_details = {
            "method": "majority_voting",
            "total_votes": total_votes,
            "majority_votes": majority_votes,
            "winning_action_type": best_action_type.value
        }

        return HybridDecision(
            action=best_action or AIAction(ActionType.END_TURN, 0.5, "无有效决策", {}),
            consensus_score=consensus_score,
            participating_strategies=[s[0] for s in strategy_decisions],
            voting_details=voting_details,
            execution_time=0.0
        )

    def _confidence_based_decision(self, strategy_decisions: List[Tuple[str, AIAction]],
                                 context: GameContext) -> HybridDecision:
        """基于置信度的决策"""
        if not strategy_decisions:
            best_action = AIAction(ActionType.END_TURN, 0.5, "无有效决策", {})
            consensus_score = 0.0
        else:
            # 选择置信度最高的动作
            best_strategy, best_action = max(strategy_decisions, key=lambda x: x[1].confidence)
            consensus_score = best_action.confidence

        voting_details = {
            "method": "confidence_based",
            "best_strategy": best_strategy if strategy_decisions else None,
            "confidence": consensus_score
        }

        return HybridDecision(
            action=best_action,
            consensus_score=consensus_score,
            participating_strategies=[s[0] for s in strategy_decisions],
            voting_details=voting_details,
            execution_time=0.0
        )

    def _performance_based_decision(self, strategy_decisions: List[Tuple[str, AIAction]],
                                  context: GameContext) -> HybridDecision:
        """基于历史性能的决策"""
        # 计算每个策略的性能加权分数
        scored_decisions = []
        for strategy_name, action in strategy_decisions:
            performance_score = self._calculate_strategy_performance(strategy_name)
            weighted_confidence = action.confidence * performance_score
            scored_decisions.append((weighted_confidence, strategy_name, action))

        if not scored_decisions:
            best_action = AIAction(ActionType.END_TURN, 0.5, "无有效决策", {})
            consensus_score = 0.0
        else:
            # 选择性能加权分数最高的动作
            _, best_strategy, best_action = max(scored_decisions, key=lambda x: x[0])
            consensus_score = best_action.confidence

        voting_details = {
            "method": "performance_based",
            "best_strategy": best_strategy if scored_decisions else None,
            "performance_weighted_score": max([s[0] for s in scored_decisions]) if scored_decisions else 0
        }

        return HybridDecision(
            action=best_action,
            consensus_score=consensus_score,
            participating_strategies=[s[0] for s in strategy_decisions],
            voting_details=voting_details,
            execution_time=0.0
        )

    def _calculate_consensus_score(self, strategy_decisions: List[Tuple[str, AIAction]],
                                 selected_action: AIAction) -> float:
        """计算共识分数"""
        if not strategy_decisions:
            return 0.0

        # 计算动作类型的一致性
        action_types = [action.action_type for _, action in strategy_decisions]
        selected_type = selected_action.action_type

        type_agreement = sum(1 for at in action_types if at == selected_type) / len(action_types)

        # 计算置信度的一致性
        confidences = [action.confidence for _, action in strategy_decisions]
        confidence_variance = statistics.variance(confidences) if len(confidences) > 1 else 0
        confidence_agreement = 1 - min(1, confidence_variance * 4)  # 方差越小，一致性越高

        # 综合共识分数
        consensus_score = (type_agreement * 0.7 + confidence_agreement * 0.3)

        return max(0, min(1, consensus_score))

    def _calculate_strategy_performance(self, strategy_name: str) -> float:
        """计算策略历史性能分数"""
        if strategy_name not in self.strategy_performance:
            return 1.0

        performances = self.strategy_performance[strategy_name]
        if not performances:
            return 1.0

        # 使用最近的性能数据
        window_size = min(self.config["performance_window"], len(performances))
        recent_performances = performances[-window_size:]

        # 计算平均性能
        avg_performance = sum(recent_performances) / len(recent_performances)

        # 映射到权重系数 (0.1 - 2.0)
        weight_factor = 0.1 + (avg_performance * 1.9)

        return weight_factor

    def _validate_decision(self, hybrid_decision: HybridDecision) -> bool:
        """验证决策质量"""
        # 检查共识分数阈值
        if hybrid_decision.consensus_score < self.config["min_consensus_score"]:
            return False

        # 检查参与策略数量
        if len(hybrid_decision.participating_strategies) < self.config["min_participating_strategies"]:
            return False

        # 检查动作有效性
        if not hybrid_decision.action or hybrid_decision.action.confidence < 0.1:
            return False

        return True

    async def _fallback_decision(self, context: GameContext) -> Optional[AIAction]:
        """回退决策策略"""
        fallback_name = self.config["fallback_strategy"]
        if fallback_name in self.sub_strategies:
            try:
                fallback_strategy = self.sub_strategies[fallback_name]
                action = await fallback_strategy.execute_with_timing(context)
                logger.info(f"使用回退策略: {fallback_name}")
                return action
            except Exception as e:
                logger.error(f"回退策略也失败: {e}")

        # 最后的保险：结束回合
        return AIAction(
            action_type=ActionType.END_TURN,
            confidence=0.3,
            reasoning="所有策略都失败，结束回合",
            parameters={}
        )

    def _update_performance_stats(self, hybrid_decision: HybridDecision, execution_time: float):
        """更新性能统计"""
        hybrid_decision.execution_time = execution_time
        self.consensus_history.append(hybrid_decision.consensus_score)

        # 限制历史记录长度
        if len(self.consensus_history) > 1000:
            self.consensus_history = self.consensus_history[-500:]

    def _adaptive_weight_adjustment(self, hybrid_decision: HybridDecision):
        """自适应权重调整"""
        if not self.config["enable_adaptive_weights"]:
            return

        # 这里可以根据决策结果调整策略权重
        # 简化实现：基于共识分数调整
        adjustment_factor = self.config["weight_adjustment_factor"]

        for strategy_name in hybrid_decision.participating_strategies:
            if strategy_name in self.strategy_weights:
                # 根据共识质量调整权重
                weight_adjustment = adjustment_factor * hybrid_decision.consensus_score
                self.strategy_weights[strategy_name] *= (1 + weight_adjustment)

        # 归一化权重
        total_weight = sum(self.strategy_weights.values())
        if total_weight > 0:
            for strategy_name in self.strategy_weights:
                self.strategy_weights[strategy_name] /= total_weight

    def evaluate_board_state(self, context: GameContext) -> float:
        """评估局面状态（使用加权平均）"""
        if not self.sub_strategies:
            return 0.0

        scores = []
        weights = []

        for strategy_name, strategy in self.sub_strategies.items():
            try:
                score = strategy.evaluate_board_state(context)
                weight = self.strategy_weights.get(strategy_name, 1.0)
                scores.append(score)
                weights.append(weight)
            except Exception as e:
                logger.warning(f"策略 {strategy_name} 评估局面失败: {e}")

        if not scores:
            return 0.0

        # 加权平均
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        total_weight = sum(weights)

        return weighted_sum / max(1, total_weight)

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        base_stats = super().get_performance_stats()

        # 添加混合策略特有的统计
        hybrid_stats = {
            "decisions_made": self.decisions_made,
            "consensus_failures": self.consensus_failures,
            "average_consensus_score": sum(self.consensus_history) / max(1, len(self.consensus_history)),
            "consensus_score_distribution": {
                "excellent": sum(1 for s in self.consensus_history if s > 0.8),
                "good": sum(1 for s in self.consensus_history if 0.6 < s <= 0.8),
                "fair": sum(1 for s in self.consensus_history if 0.4 < s <= 0.6),
                "poor": sum(1 for s in self.consensus_history if s <= 0.4)
            },
            "strategy_weights": self.strategy_weights.copy(),
            "strategy_usage_count": self.strategy_usage_count.copy()
        }

        # 添加子策略统计
        sub_strategy_stats = {}
        for name, strategy in self.sub_strategies.items():
            sub_strategy_stats[name] = strategy.get_performance_stats()

        hybrid_stats["sub_strategies"] = sub_strategy_stats
        base_stats.update(hybrid_stats)

        return base_stats

    def reset_statistics(self):
        """重置统计信息"""
        super().reset_statistics()
        self.consensus_history.clear()
        self.decisions_made = 0
        self.consensus_failures = 0

        for strategy in self.sub_strategies.values():
            strategy.reset_statistics()

        for count_key in self.strategy_usage_count:
            self.strategy_usage_count[count_key] = 0