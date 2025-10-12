"""
游戏上下文定义
连接游戏引擎和AI引擎的数据接口
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from ..cards.base import CardInstance


@dataclass
class GameContext:
    """
    游戏上下文信息
    这是游戏引擎和AI引擎之间的数据接口
    """
    # 基础游戏信息
    game_id: str
    current_player: int  # 0 或 1
    turn_number: int
    phase: str  # draw, main, end, combat

    # 玩家状态
    player_health: int
    player_max_health: int
    player_mana: int
    player_max_mana: int
    player_hand: List[Dict[str, Any]]
    player_field: List[Dict[str, Any]]
    player_deck_size: int

    # 对手状态
    opponent_health: int
    opponent_max_health: int
    opponent_mana: int
    opponent_max_mana: int
    opponent_field: List[Dict[str, Any]]
    opponent_hand_size: int
    opponent_deck_size: int

    # 额外信息
    tavern_tier: int = 0  # 酒馆等级（如果适用）
    coins: int = 0        # 金币（如果适用）
    game_mode: str = "standard"  # 游戏模式

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于LLM处理"""
        return asdict(self)

    @classmethod
    def from_game_state(cls, game_state: 'GameState', current_player_index: int) -> 'GameContext':
        """
        从完整游戏状态创建游戏上下文

        Args:
            game_state: 完整游戏状态
            current_player_index: 当前玩家索引

        Returns:
            GameContext: 游戏上下文
        """
        current_player = game_state.players[current_player_index]
        opponent = game_state.players[1 - current_player_index]

        # 转换手牌
        player_hand = [card.get_state_summary() for card in current_player.hand]
        player_field = [card.get_state_summary() for card in current_player.battlefield]
        opponent_field = [card.get_state_summary() for card in opponent.battlefield]

        return cls(
            game_id=game_state.game_id,
            current_player=current_player_index,
            turn_number=game_state.turn_number,
            phase=game_state.current_phase,
            player_health=current_player.health,
            player_max_health=current_player.max_health,
            player_mana=current_player.current_mana,
            player_max_mana=current_player.max_mana,
            player_hand=player_hand,
            player_field=player_field,
            player_deck_size=len(current_player.deck),
            opponent_health=opponent.health,
            opponent_max_health=opponent.max_health,
            opponent_mana=opponent.current_mana,
            opponent_max_mana=opponent.max_mana,
            opponent_field=opponent_field,
            opponent_hand_size=len(opponent.hand),
            opponent_deck_size=len(opponent.deck)
        )

    def get_key_features(self) -> Dict[str, Any]:
        """
        提取关键特征用于AI分析
        """
        return {
            "health_advantage": self.player_health - self.opponent_health,
            "mana_advantage": self.player_mana - self.opponent_mana,
            "field_control": len(self.player_field) - len(self.opponent_field),
            "hand_advantage": len(self.player_hand) - self.opponent_hand_size,
            "total_attack_power": sum(card.get("attack", 0) for card in self.player_field),
            "opponent_total_attack": sum(card.get("attack", 0) for card in self.opponent_field),
            "has_taunt_minions": any(card.get("mechanics", []).count("taunt") > 0 for card in self.player_field),
            "opponent_has_taunt": any(card.get("mechanics", []).count("taunt") > 0 for card in self.opponent_field),
            "turn_number": self.turn_number,
            "phase": self.phase
        }

    def get_playable_cards(self) -> List[Dict[str, Any]]:
        """获取可出的卡牌"""
        playable = []
        for card in self.player_hand:
            if card.get("cost", 0) <= self.player_mana:
                playable.append(card)
        return playable

    def get_attack_opportunities(self) -> List[Dict[str, Any]]:
        """获取攻击机会"""
        opportunities = []

        for attacker in self.player_field:
            if attacker.get("can_attack", False) and attacker.get("attack", 0) > 0:
                # 可以攻击对手英雄
                opportunities.append({
                    "attacker": attacker,
                    "target": "opponent_hero",
                    "damage": attacker.get("attack", 0)
                })

                # 可以攻击对手随从
                for target in self.opponent_field:
                    # 检查是否可以攻击（潜行、嘲讽等）
                    if self._can_attack_target(attacker, target):
                        opportunities.append({
                            "attacker": attacker,
                            "target": target,
                            "damage": attacker.get("attack", 0)
                        })

        return opportunities

    def _can_attack_target(self, attacker: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """检查是否可以攻击目标"""
        target_mechanics = target.get("mechanics", [])

        # 无法攻击潜行随从
        if "stealth" in target_mechanics:
            return False

        # 如果有嘲讽，必须优先攻击嘲讽
        opponent_has_taunt = any(
            "taunt" in card.get("mechanics", [])
            for card in self.opponent_field
        )

        if opponent_has_taunt and "taunt" not in target_mechanics:
            return False

        return True

    def evaluate_danger_level(self) -> float:
        """
        评估当前局面的危险程度
        0-1之间，1表示最危险
        """
        danger_score = 0.0

        # 血量危险
        health_ratio = self.player_health / self.player_max_health
        if health_ratio < 0.2:
            danger_score += 0.4
        elif health_ratio < 0.4:
            danger_score += 0.2

        # 场面劣势
        field_advantage = len(self.player_field) - len(self.opponent_field)
        if field_advantage < -2:
            danger_score += 0.3
        elif field_advantage < -1:
            danger_score += 0.15

        # 攻击力劣势
        my_attack = sum(card.get("attack", 0) for card in self.player_field)
        opp_attack = sum(card.get("attack", 0) for card in self.opponent_field)
        attack_advantage = my_attack - opp_attack

        if attack_advantage < -7:
            danger_score += 0.3
        elif attack_advantage < -3:
            danger_score += 0.15

        return min(1.0, danger_score)


# 前向声明
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_state import GameState