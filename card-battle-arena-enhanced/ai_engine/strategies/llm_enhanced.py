"""
大模型增强的AI策略
结合规则AI和LLM分析，实现更智能的决策
"""
import asyncio
import json
import time
from typing import Dict, List, Any, Optional
import logging

from .base import AIStrategy, AIAction, ActionType, GameContext, AIStrategyError
from .rule_based import RuleBasedStrategy
from ..llm_integration.base import LLMManager, LLMMessage


logger = logging.getLogger(__name__)


class LLMEnhancedStrategy(AIStrategy):
    """大模型增强的AI策略"""

    def __init__(self, name: str = "LLM增强AI", config: Dict[str, Any] = None):
        default_config = {
            # LLM配置
            "llm_client": "openai",
            "llm_temperature": 0.3,
            "llm_max_tokens": 1000,

            # 混合决策配置
            "llm_weight": 0.6,  # LLM决策权重
            "rule_weight": 0.4,  # 规则决策权重
            "llm_confidence_threshold": 0.7,  # LLM置信度阈值

            # 性能配置
            "enable_llm_caching": True,
            "cache_ttl": 30,  # 缓存时间(秒)
            "max_analysis_time": 3.0,  # 最大分析时间

            # 回退配置
            "fallback_to_rule": True,
            "max_retries": 2
        }

        if config:
            default_config.update(config)

        super().__init__(name, default_config)

        # 初始化规则AI作为基础策略
        rule_config = config.get("rule_config", {}) if config else {}
        self.rule_strategy = RuleBasedStrategy(f"{name}_规则层", rule_config)

        # LLM管理器
        self.llm_manager: Optional[LLMManager] = None
        self.llm_cache: Dict[str, Dict[str, Any]] = {}

        # 统计信息
        self.llm_calls = 0
        self.llm_successes = 0
        self.llm_failures = 0
        self.cache_hits = 0

    def set_llm_manager(self, llm_manager: LLMManager):
        """设置LLM管理器"""
        self.llm_manager = llm_manager

    async def make_decision(self, context: GameContext) -> Optional[AIAction]:
        """
        使用LLM增强的决策过程
        结合规则AI和LLM分析
        """
        if not self.llm_manager:
            logger.warning("LLM管理器未设置，回退到规则AI")
            return await self.rule_strategy.execute_with_timing(context)

        try:
            # 1. 获取规则AI的决策
            rule_action = await self.rule_strategy.execute_with_timing(context)

            # 2. 获取LLM分析（带超时控制）
            llm_action = await asyncio.wait_for(
                self._get_llm_decision(context),
                timeout=self.config["max_analysis_time"]
            )

            # 3. 混合决策
            final_action = self._combine_decisions(rule_action, llm_action, context)

            if final_action:
                logger.info(f"LLM增强AI决策: {final_action.action_type.value}, "
                          f"置信度: {final_action.confidence:.2f}")

            return final_action

        except asyncio.TimeoutError:
            logger.warning("LLM分析超时，使用规则AI决策")
            self.llm_failures += 1
            return rule_action
        except Exception as e:
            logger.error(f"LLM增强AI决策失败: {e}")
            self.llm_failures += 1

            if self.config["fallback_to_rule"]:
                return rule_action
            return None

    async def _get_llm_decision(self, context: GameContext) -> Optional[AIAction]:
        """获取LLM决策"""
        # 检查缓存
        cache_key = self._generate_cache_key(context)
        if self._is_cache_valid(cache_key):
            return self._get_cached_decision(cache_key)

        try:
            # 准备LLM分析的prompt
            llm_response = await self._analyze_with_llm(context)
            llm_action = self._parse_llm_response(llm_response, context)

            # 缓存结果
            if self.config["enable_llm_caching"]:
                self._cache_decision(cache_key, llm_action)

            self.llm_calls += 1
            if llm_action:
                self.llm_successes += 1
            else:
                self.llm_failures += 1

            return llm_action

        except Exception as e:
            logger.error(f"LLM决策失败: {e}")
            self.llm_failures += 1
            return None

    async def _analyze_with_llm(self, context: GameContext) -> str:
        """使用LLM分析游戏状态"""
        system_prompt = """你是一个专业的卡牌游戏AI。请分析当前游戏状态并给出决策建议。

你的任务：
1. 分析当前局面优劣
2. 识别最佳行动方案
3. 评估每个行动的优先级
4. 给出具体的决策建议

请以JSON格式回复，格式如下：
{
    "analysis": "局面分析",
    "board_score": 0.8,
    "recommended_actions": [
        {
            "action_type": "play_card|attack|use_hero_power|end_turn",
            "target": "目标描述",
            "confidence": 0.9,
            "reasoning": "决策理由"
        }
    ]
}

决策规则：
- play_card: 出牌，需要指定卡牌信息
- attack: 攻击，需要指定攻击者和目标
- use_hero_power: 使用英雄技能
- end_turn: 结束回合

置信度范围：0-1，1表示完全确定"""

        user_prompt = f"""请分析以下游戏状态：

游戏ID: {context.game_id}
当前玩家: 玩家{context.current_player}
回合数: {context.turn_number}
阶段: {context.phase}

我方状态：
- 生命值: {context.player_health}
- 法力值: {context.player_mana}/{context.player_mana + context.turn_number - 1}
- 手牌数量: {len(context.player_hand)}
- 场面随从: {len(context.player_field)}个

我方手牌：
{self._format_hand_cards(context.player_hand)}

我方场面：
{self._format_field_cards(context.player_field)}

对手状态：
- 生命值: {context.opponent_health}
- 法力值: {context.opponent_mana}
- 场面随从: {len(context.opponent_field)}个

对手场面：
{self._format_field_cards(context.opponent_field)}

请给出最佳决策建议。"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

        # 调用LLM
        response = await self.llm_manager.analyze_with_fallback(
            messages,
            preferred_client=self.config["llm_client"]
        )

        return response.content

    def _parse_llm_response(self, llm_response: str, context: GameContext) -> Optional[AIAction]:
        """解析LLM响应为AIAction"""
        try:
            # 尝试解析JSON响应
            response_data = json.loads(llm_response)

            recommended_actions = response_data.get("recommended_actions", [])
            if not recommended_actions:
                return None

            # 选择置信度最高的动作
            best_action_data = max(recommended_actions, key=lambda x: x.get("confidence", 0))

            action_type_str = best_action_data.get("action_type", "end_turn")
            action_type = self._parse_action_type(action_type_str)

            confidence = best_action_data.get("confidence", 0.5)
            reasoning = best_action_data.get("reasoning", "LLM决策建议")

            # 验证置信度阈值
            if confidence < self.config["llm_confidence_threshold"]:
                logger.info(f"LLM置信度 {confidence:.2f} 低于阈值 {self.config['llm_confidence_threshold']}")
                return None

            parameters = {}
            if action_type == ActionType.PLAY_CARD:
                # 这里需要根据实际卡牌信息来构建参数
                parameters["card"] = self._find_best_card_to_play(context)
            elif action_type == ActionType.ATTACK:
                parameters.update(self._find_best_attack(context))
            elif action_type == ActionType.USE_HERO_POWER:
                parameters = {}

            return AIAction(
                action_type=action_type,
                confidence=confidence,
                reasoning=f"LLM分析: {reasoning}",
                parameters=parameters
            )

        except json.JSONDecodeError as e:
            logger.error(f"LLM响应JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"LLM响应解析失败: {e}")
            return None

    def _combine_decisions(self, rule_action: Optional[AIAction],
                          llm_action: Optional[AIAction],
                          context: GameContext) -> Optional[AIAction]:
        """结合规则AI和LLM的决策"""
        if not rule_action and not llm_action:
            return None

        if not rule_action:
            return llm_action

        if not llm_action:
            return rule_action

        # 计算加权置信度
        rule_weight = self.config["rule_weight"]
        llm_weight = self.config["llm_weight"]

        # 根据当前局面调整权重
        board_score = self.evaluate_board_state(context)
        if abs(board_score) > 0.5:  # 局面明显优/劣势时，更依赖规则
            rule_weight *= 1.2
            llm_weight *= 0.8
        else:  # 局面均衡时，更依赖LLM
            rule_weight *= 0.8
            llm_weight *= 1.2

        # 归一化权重
        total_weight = rule_weight + llm_weight
        rule_weight /= total_weight
        llm_weight /= total_weight

        # 选择最优动作
        rule_score = rule_action.confidence * rule_weight
        llm_score = llm_action.confidence * llm_weight

        if llm_score > rule_score:
            # 合并推理信息
            combined_reasoning = f"LLM({llm_score:.2f}): {llm_action.reasoning} | 规则AI({rule_score:.2f}): {rule_action.reasoning}"
            llm_action.reasoning = combined_reasoning
            return llm_action
        else:
            combined_reasoning = f"规则AI({rule_score:.2f}): {rule_action.reasoning} | LLM({llm_score:.2f}): {llm_action.reasoning}"
            rule_action.reasoning = combined_reasoning
            return rule_action

    def evaluate_board_state(self, context: GameContext) -> float:
        """评估局面状态，委托给规则AI"""
        return self.rule_strategy.evaluate_board_state(context)

    # 辅助方法
    def _format_hand_cards(self, hand_cards: List[Dict[str, Any]]) -> str:
        """格式化手牌信息"""
        if not hand_cards:
            return "无手牌"

        result = []
        for i, card in enumerate(hand_cards):
            card_info = f"{i+1}. {card.get('name', 'Unknown')} ({card.get('cost', 0)}费)"
            if 'attack' in card:
                card_info += f" {card['attack']}/{card.get('health', 0)}"
            result.append(card_info)

        return "\n".join(result)

    def _format_field_cards(self, field_cards: List[Dict[str, Any]]) -> str:
        """格式化场面卡牌信息"""
        if not field_cards:
            return "无随从"

        result = []
        for i, card in enumerate(field_cards):
            card_info = f"{i+1}. {card.get('name', 'Unknown')} {card.get('attack', 0)}/{card.get('health', 0)}"
            if not card.get('can_attack', True):
                card_info += " (无法攻击)"
            result.append(card_info)

        return "\n".join(result)

    def _parse_action_type(self, action_type_str: str) -> ActionType:
        """解析动作类型"""
        action_map = {
            "play_card": ActionType.PLAY_CARD,
            "attack": ActionType.ATTACK,
            "use_hero_power": ActionType.USE_HERO_POWER,
            "end_turn": ActionType.END_TURN
        }
        return action_map.get(action_type_str, ActionType.END_TURN)

    def _find_best_card_to_play(self, context: GameContext) -> Optional[Dict[str, Any]]:
        """找到最佳出牌（简化实现）"""
        playable_cards = [card for card in context.player_hand if card.get("cost", 0) <= context.player_mana]
        if playable_cards:
            # 简单选择：优先出高费用卡牌
            return max(playable_cards, key=lambda x: x.get("cost", 0))
        return None

    def _find_best_attack(self, context: GameContext) -> Dict[str, Any]:
        """找到最佳攻击（简化实现）"""
        attackers = [card for card in context.player_field if card.get("can_attack", True)]
        if not attackers:
            return {}

        # 简单策略：用攻击力最高的随从攻击对手英雄
        best_attacker = max(attackers, key=lambda x: x.get("attack", 0))
        return {
            "attacker": best_attacker,
            "target": "opponent_hero"
        }

    def _generate_cache_key(self, context: GameContext) -> str:
        """生成缓存键"""
        # 基于关键游戏状态生成哈希
        key_data = f"{context.game_id}_{context.turn_number}_{len(context.player_hand)}_{len(context.player_field)}_{context.player_mana}"
        return str(hash(key_data))

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if not self.config["enable_llm_caching"]:
            return False

        if cache_key not in self.llm_cache:
            return False

        cache_time = self.llm_cache[cache_key].get("timestamp", 0)
        return (time.time() - cache_time) < self.config["cache_ttl"]

    def _get_cached_decision(self, cache_key: str) -> Optional[AIAction]:
        """获取缓存的决策"""
        self.cache_hits += 1
        return self.llm_cache[cache_key].get("action")

    def _cache_decision(self, cache_key: str, action: Optional[AIAction]):
        """缓存决策"""
        self.llm_cache[cache_key] = {
            "action": action,
            "timestamp": time.time()
        }

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        base_stats = super().get_performance_stats()

        # 添加LLM相关统计
        llm_stats = {
            "llm_calls": self.llm_calls,
            "llm_successes": self.llm_successes,
            "llm_failures": self.llm_failures,
            "llm_success_rate": self.llm_successes / max(1, self.llm_calls),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(1, self.llm_calls),
            "cache_size": len(self.llm_cache)
        }

        base_stats.update(llm_stats)

        # 添加规则AI统计
        if self.rule_strategy:
            base_stats["rule_strategy_stats"] = self.rule_strategy.get_performance_stats()

        return base_stats

    def reset_statistics(self):
        """重置统计信息"""
        super().reset_statistics()
        self.llm_calls = 0
        self.llm_successes = 0
        self.llm_failures = 0
        self.cache_hits = 0
        self.llm_cache.clear()

        if self.rule_strategy:
            self.rule_strategy.reset_statistics()