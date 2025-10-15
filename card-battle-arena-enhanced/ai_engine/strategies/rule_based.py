"""
基于规则的AI策略实现
参考原始card-battle-arena项目的AI逻辑，并进行增强
"""
from typing import Dict, List, Any, Optional, Tuple
import time
import random
import asyncio
from .base import AIStrategy, AIAction, ActionType, GameContext, AIStrategyError


class RuleBasedStrategy(AIStrategy):
    """基于规则的AI策略"""

    def __init__(self, name: str = "规则AI", config: Optional[Dict[str, Any]] = None):
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
                curve_bonus = (1 - abs(mana_efficiency - self.config["mana_curve_preference"])) * 0.5

                total_score = card_score + curve_bonus

                # 改进的置信度计算 - 使用更合理的缩放
                confidence = self._calculate_play_card_confidence(total_score, card, context)

                actions.append(AIAction(
                    action_type=ActionType.PLAY_CARD,
                    confidence=confidence,
                    reasoning=f"出卡牌 {card.get('name', 'Unknown')}，价值分数: {card_score:.2f}，总分数: {total_score:.2f}",
                    parameters={"card": card, "target": None}
                ))

        return sorted(actions, key=lambda x: x.confidence, reverse=True)

    def _calculate_play_card_confidence(self, total_score: float, card: Dict[str, Any], context: GameContext) -> float:
        """计算出牌的置信度"""
        # 提高基础置信度 - 改为除以3而不是5，让出牌更有吸引力
        base_confidence = min(0.95, total_score / 3.0 + 0.2)  # 基础值+0.2，除以3提高分数

        # 卡牌类型调整
        card_type = card.get("card_type", "")
        if card_type == "spell":
            # 法术牌通常有直接效果，置信度更高
            base_confidence *= 1.2
        elif card_type == "minion":
            # 随从牌需要持续站场，根据场面调整
            if not context.player_field:
                base_confidence *= 1.4  # 空场时出随从价值大幅提升
            else:
                base_confidence *= 1.1  # 有随从时也适当提高

        # 法力效率奖励 - 提高奖励系数
        cost = card.get("cost", 0)
        if cost > 0:
            mana_efficiency_bonus = min(0.2, (context.player_mana - cost) * 0.04)  # 奖励翻倍
            base_confidence += mana_efficiency_bonus

        # 手牌数量调整 - 手牌少时更倾向于出牌
        if len(context.player_hand) <= 3:
            base_confidence += 0.15  # 提高奖励
        elif len(context.player_hand) <= 5:
            base_confidence += 0.08

        # 血量优势调整
        health_diff = context.player_health - context.opponent_health
        if health_diff < -10:  # 血量大劣时更积极
            base_confidence += 0.2
        elif health_diff < -5:  # 小劣时也适当提高
            base_confidence += 0.1

        # 法力值利用率奖励 - 新增
        mana_usage_ratio = cost / max(1, context.player_mana)
        if 0.5 <= mana_usage_ratio <= 1.0:  # 合理的法力使用
            base_confidence += 0.1

        # 对手场面压力 - 新增
        if len(context.opponent_field) > len(context.player_field):
            base_confidence += 0.12  # 对手场面优势时更需要出牌

        # 确保置信度在合理范围内
        return max(0.2, min(0.98, base_confidence))  # 最低置信度提高到0.2

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
        if context.player_mana < 2:
            return None

        # 动态计算英雄技能的价值
        hero_power_value = self._calculate_hero_power_value(context)

        # 降低基础置信度 - 让英雄技能不那么优先
        base_confidence = min(0.6, hero_power_value / 12.0)  # 除以12而不是8，上限降低到0.6

        # 场面情况调整 - 降低调整幅度
        confidence_adjustment = 0.0

        # 如果场面落后，英雄技能更有价值，但减少奖励
        if len(context.player_field) < len(context.opponent_field):
            confidence_adjustment += 0.05  # 从0.1降到0.05

        # 如果法力值有富余，但减少奖励
        if context.player_mana >= 5:  # 提高条件
            confidence_adjustment += 0.05  # 从0.1降到0.05

        # 如果手牌较少但不是极少，使用英雄技能来补充节奏
        if len(context.player_hand) <= 1:  # 只有手牌极少时才给奖励
            confidence_adjustment += 0.08  # 从0.15降到0.08

        # 如果有可出的牌，降低英雄技能的优先级 - 新增惩罚项
        playable_cards = [card for card in context.player_hand if card.get("cost", 0) <= context.player_mana]
        if len(playable_cards) > 0:
            confidence_adjustment -= 0.15  # 有可出牌时降低英雄技能优先级

        # 如果我方场面已经领先，降低英雄技能价值 - 新增惩罚项
        if len(context.player_field) > len(context.opponent_field):
            confidence_adjustment -= 0.1

        final_confidence = min(0.7, base_confidence + confidence_adjustment)  # 降低上限到0.7
        final_confidence = max(0.1, final_confidence)  # 确保不低于0.1

        return AIAction(
            action_type=ActionType.USE_HERO_POWER,
            confidence=final_confidence,
            reasoning=f"使用英雄技能，价值评估: {hero_power_value:.2f}",
            parameters={}
        )

    def _calculate_card_value(self, card: Dict[str, Any], context: GameContext) -> float:
        """计算卡牌价值分数"""
        card_type = card.get("card_type", "")

        if card_type == "spell":
            return self._calculate_spell_card_value(card, context)
        elif card_type == "minion":
            return self._calculate_minion_card_value(card, context)
        else:
            # 通用计算方法（作为后备）
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

    def _calculate_hero_power_value(self, context: GameContext) -> float:
        """计算英雄技能的价值"""
        base_value = 3.0  # 英雄技能基础价值

        # 根据英雄类型调整价值（这里可以扩展为具体的英雄判断）
        # 简化实现：假设是法师英雄，技能造成1点伤害
        hero_power_damage = 1.0

        # 对高血量敌人使用更有价值
        if context.opponent_health >= 15:
            base_value += hero_power_damage * 1.2
        else:
            base_value += hero_power_damage * 0.8

        # 清理随从的价值（如果敌方有危险随从）
        for enemy_minion in context.opponent_field:
            enemy_attack = enemy_minion.get("attack", 0)
            enemy_health = enemy_minion.get("health", 0)

            # 对高攻击随从使用英雄技能更有价值
            if enemy_attack >= 3:
                base_value += 1.5

            # 对低血量随从可能完成击杀
            if enemy_health <= hero_power_damage:
                base_value += 2.0

        # 场面控制价值
        if not context.player_field:
            # 我方空场，需要用技能拖延
            base_value += 1.0

        # 法力效率考虑
        mana_efficiency = 2.0 / context.player_mana  # 2费技能的相对效率
        if mana_efficiency > 0.5:  # 如果法力值充裕
            base_value += 0.5

        return base_value

    def _calculate_spell_card_value(self, card: Dict[str, Any], context: GameContext) -> float:
        """专门计算法术牌的价值"""
        if card.get("card_type") != "spell":
            return 0.0

        damage = card.get("attack", 0)  # 法术的攻击力数值
        cost = card.get("cost", 0)

        # 基础伤害价值
        damage_value = damage * 1.2  # 法术伤害权重更高

        # 目标价值评估
        # 1. 直接伤害对手英雄的价值
        face_damage_value = damage * self.config["face_damage_weight"]

        # 如果能造成大量伤害，价值更高
        if damage >= 5:
            face_damage_value *= 1.3

        # 2. 解场价值（假设可以用来打随从）
        board_clear_value = 0.0
        for enemy_minion in context.opponent_field:
            enemy_health = enemy_minion.get("health", 0)
            enemy_attack = enemy_minion.get("attack", 0)

            # 如果能击杀高威胁随从
            if damage >= enemy_health and enemy_attack >= 3:
                board_clear_value += enemy_attack + 2.0

        # 取最高价值
        spell_value = max(face_damage_value, board_clear_value)

        # 法力效率调整
        if cost > 0:
            mana_efficiency = spell_value / cost
            if mana_efficiency > 2.0:  # 高效率法术
                spell_value *= 1.2
            elif mana_efficiency < 1.0:  # 低效率法术
                spell_value *= 0.9

        # 血量优势调整
        health_diff = context.player_health - context.opponent_health
        if health_diff < 0:  # 我方血量劣势，急需伤害
            spell_value *= 1.3
        elif health_diff > 10:  # 我方血量大优，可以慢打
            spell_value *= 0.9

        return spell_value

    def _calculate_minion_card_value(self, card: Dict[str, Any], context: GameContext) -> float:
        """专门计算随从牌的价值"""
        if card.get("card_type") != "minion":
            return 0.0

        attack = card.get("attack", 0)
        health = card.get("health", 0)
        cost = card.get("cost", 0)
        mechanics = card.get("mechanics", [])

        # 基础身材价值
        stats_value = (attack + health) * 0.8

        # 站场价值
        board_value = attack * 0.6 + health * 0.4

        # 特殊能力价值
        mechanic_value = 0.0
        weights = self.config["card_value_weights"]

        for mechanic in mechanics:
            if mechanic in weights:
                mechanic_value += weights[mechanic]

        # 根据场面情况调整特殊能力价值
        if context.opponent_field:
            # 敌方有随从时，嘲讽更有价值
            if "taunt" in mechanics:
                mechanic_value += 1.5
            # 圣盾在有敌方随从时更有价值
            if "divine_shield" in mechanics:
                mechanic_value += 1.0
        else:
            # 敌方空场时，冲锋更有价值
            if "charge" in mechanics:
                mechanic_value += 1.5

        # 法力效率
        if cost > 0:
            mana_efficiency = (attack + health) / cost
            if mana_efficiency > 2.0:
                board_value *= 1.2

        # 场面需求调整
        if not context.player_field:
            # 我方空场，急需随从
            board_value *= 1.4
        elif len(context.player_field) < len(context.opponent_field):
            # 场面落后，需要随从
            board_value *= 1.2

        return stats_value + board_value + mechanic_value


# 导入asyncio用于sleep
import asyncio