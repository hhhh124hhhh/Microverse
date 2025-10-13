"""
基于规则的AI策略实现
参考原始card-battle-arena项目的AI逻辑，并进行增强
"""
from typing import Dict, List, Any, Optional, Tuple
import time
import random
from .base import AIStrategy, AIAction, ActionType, GameContext, AIStrategyError


class RuleBasedStrategy(AIStrategy):
    """基于规则的AI策略"""

    def __init__(self, name: str = "规则AI", config: Dict[str, Any] = None):
        default_config = {
            "mana_curve_preference": 0.7,  # 法力曲线偏好
            "board_control_weight": 0.8,   # 场面控制权重
            "face_damage_weight": 0.6,     # 直接伤害权重
            "card_value_weights": {        # 卡牌价值权重
                "attack": 1.0,
                "health": 0.8,
                "cost": -0.5,
                "taunt": 0.5,
                "charge": 0.3,
                "divine_shield": 0.4,
                "stealth": 0.2
            },
            "min_thinking_time": 0.1,      # 最小思考时间(秒)
            "max_thinking_time": 2.0       # 最大思考时间(秒)
        }
        if config:
            default_config.update(config)

        super().__init__(name, default_config)

    async def make_decision(self, context: GameContext) -> Optional[AIAction]:
        """
        基于规则做出决策
        决策优先级：出牌 -> 攻击 -> 使用英雄技能 -> 结束回合
        """
        possible_actions = []

        # 1. 评估出牌动作
        play_card_actions = self._evaluate_play_cards(context)
        possible_actions.extend(play_card_actions)

        # 2. 评估攻击动作
        attack_actions = self._evaluate_attacks(context)
        possible_actions.extend(attack_actions)

        # 3. 评估英雄技能
        hero_power_action = self._evaluate_hero_power(context)
        if hero_power_action:
            possible_actions.append(hero_power_action)

        # 4. 如果没有其他动作，考虑结束回合
        if not possible_actions:
            return AIAction(
                action_type=ActionType.END_TURN,
                confidence=0.9,
                reasoning="没有可执行的战术动作",
                parameters={}
            )

        # 选择最优动作
        best_action = self._select_best_action(possible_actions)

        # 模拟思考时间
        thinking_time = min(
            max(self.config["min_thinking_time"],
                random.uniform(0.1, 0.5)),
            self.config["max_thinking_time"]
        )
        await asyncio.sleep(thinking_time)

        return best_action

    def _evaluate_play_cards(self, context: GameContext) -> List[AIAction]:
        """评估所有可出的卡牌"""
        actions = []

        for card in context.player_hand:
            if card.get("cost", 0) <= context.player_mana:
                # 计算卡牌价值分数
                card_score = self._calculate_card_value(card, context)

                # 根据费用曲线调整分数
                cost = card.get("cost", 0)
                mana_efficiency = cost / max(1, context.player_mana)
                curve_bonus = (1 - abs(mana_efficiency - self.config["mana_curve_preference"])) * 0.3

                total_score = card_score + curve_bonus

                actions.append(AIAction(
                    action_type=ActionType.PLAY_CARD,
                    confidence=min(0.9, total_score / 10),
                    reasoning=f"出卡牌 {card.get('name', 'Unknown')}，价值分数: {card_score:.2f}",
                    parameters={"card": card, "target": None}
                ))

        return sorted(actions, key=lambda x: x.confidence, reverse=True)

    def _evaluate_attacks(self, context: GameContext) -> List[AIAction]:
        """评估所有可能的攻击动作"""
        actions = []

        for minion in context.player_field:
            if minion.get("can_attack", False) and minion.get("attack", 0) > 0:
                # 评估攻击对手英雄
                face_attack_score = self._calculate_face_attack_score(minion, context)
                actions.append(AIAction(
                    action_type=ActionType.ATTACK,
                    confidence=min(0.9, face_attack_score / 10),
                    reasoning=f"用 {minion.get('name', 'Unknown')} 攻击对手英雄",
                    parameters={"attacker": minion, "target": "opponent_hero"}
                ))

                # 评估攻击对手随从
                for enemy_minion in context.opponent_field:
                    attack_score = self._calculate_minion_attack_score(minion, enemy_minion, context)
                    if attack_score > 0:
                        actions.append(AIAction(
                            action_type=ActionType.ATTACK,
                            confidence=min(0.8, attack_score / 10),
                            reasoning=f"用 {minion.get('name', 'Unknown')} 攻击 {enemy_minion.get('name', 'Unknown')}",
                            parameters={"attacker": minion, "target": enemy_minion}
                        ))

        return sorted(actions, key=lambda x: x.confidence, reverse=True)

    def _evaluate_hero_power(self, context: GameContext) -> Optional[AIAction]:
        """评估使用英雄技能"""
        # 这里需要根据具体的英雄技能来实现
        # 简化实现：假设英雄技能消耗2点法力值
        if context.player_mana >= 2:
            return AIAction(
                action_type=ActionType.USE_HERO_POWER,
                confidence=0.6,
                reasoning="使用英雄技能",
                parameters={}
            )
        return None

    def _calculate_card_value(self, card: Dict[str, Any], context: GameContext) -> float:
        """计算卡牌价值分数"""
        weights = self.config["card_value_weights"]
        score = 0.0

        # 基础属性分数
        score += card.get("attack", 0) * weights["attack"]
        score += card.get("health", 0) * weights["health"]
        score += card.get("cost", 0) * weights["cost"]

        # 特殊能力加成
        mechanics = card.get("mechanics", [])
        for mechanic in mechanics:
            score += weights.get(mechanic, 0)

        # 场面状况调整
        if context.opponent_field and "taunt" in mechanics:
            score += 1.0  # 对手有随从时，嘲讽更有价值

        return max(0, score)

    def _calculate_face_attack_score(self, minion: Dict[str, Any], context: GameContext) -> float:
        """计算攻击对手英雄的分数"""
        attack = minion.get("attack", 0)
        health = minion.get("health", 0)

        # 基础分数
        base_score = attack * self.config["face_damage_weight"]

        # 血量优势加成
        health_diff = context.player_health - context.opponent_health
        if health_diff > 0:
            base_score *= 1.2  # 血量领先时更激进

        # 随从存续价值
        survival_value = health * 0.5
        if health > attack * 2:  # 随从很难被交换
            base_score += survival_value

        return max(0, base_score)

    def _calculate_minion_attack_score(self, attacker: Dict[str, Any],
                                     target: Dict[str, Any],
                                     context: GameContext) -> float:
        """计算攻击随从的分数"""
        attack_power = attacker.get("attack", 0)
        target_health = target.get("health", 0)
        target_attack = target.get("attack", 0)
        attacker_health = attacker.get("health", 0)

        # 检查目标特性
        target_mechanics = target.get("mechanics", [])
        is_taunt = "taunt" in target_mechanics
        is_stealth = "stealth" in target_mechanics

        # 无法攻击潜行随从
        if is_stealth:
            return 0

        score = 0.0

        # 击杀收益
        if attack_power >= target_health:
            kill_value = target_attack + 2  # 击杀奖励 = 攻击力 + 基础奖励
            score += kill_value * self.config["board_control_weight"]
        else:
            # 交换价值（是否值得用这个随从换）
            if attacker_health <= target_attack:
                score -= 2  # 不利交换
            else:
                score += 0.5  # 有利交换

        # 嘲讽优先
        if is_taunt:
            score *= 1.5

        return max(0, score)

    def _select_best_action(self, actions: List[AIAction]) -> AIAction:
        """从候选动作中选择最优的"""
        if not actions:
            raise AIStrategyError("没有可选择的动作")

        # 按置信度排序，选择最高置信度的动作
        return max(actions, key=lambda x: x.confidence)

    def evaluate_board_state(self, context: GameContext) -> float:
        """
        评估当前局面分数
        返回-1到1之间的分数，正数表示我方优势
        """
        # 血量优势
        health_diff = context.player_health - context.opponent_health
        health_score = health_diff / 30.0  # 归一化到[-1, 1]

        # 场面控制
        player_power = sum(m.get("attack", 0) for m in context.player_field)
        opponent_power = sum(m.get("attack", 0) for m in context.opponent_field)
        power_diff = player_power - opponent_power
        power_score = power_diff / 10.0  # 归一化到[-1, 1]

        # 手牌优势
        hand_diff = len(context.player_hand) - 5  # 假设5张是标准手牌数
        hand_score = hand_diff / 10.0

        # 法力值优势
        mana_diff = context.player_mana - context.opponent_mana
        mana_score = mana_diff / 10.0

        # 综合评分
        total_score = (
            health_score * 0.4 +
            power_score * 0.4 +
            hand_score * 0.1 +
            mana_score * 0.1
        )

        return max(-1, min(1, total_score))


# 导入asyncio用于sleep
import asyncio