"""
卡牌系统基础类定义
定义游戏中各种卡牌的基础属性和接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid


class CardType(Enum):
    """卡牌类型"""
    MINION = "minion"        # 随从
    SPELL = "spell"          # 法术
    WEAPON = "weapon"        # 武器
    HERO = "hero"           # 英雄
    HERO_POWER = "hero_power"  # 英雄技能


class CardRarity(Enum):
    """卡牌稀有度"""
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class CardSet(Enum):
    """卡牌系列"""
    BASIC = "basic"
    CLASSIC = "classic"
    EXPERT1 = "expert1"
    GOBLINS_VS_GNOMES = "goblins_vs_gnomes"
    # 可以添加更多系列


class Mechanic(Enum):
    """关键词机制"""
    TAUNT = "taunt"                    # 嘲讽
    CHARGE = "charge"                  # 冲锋
    DIVINE_SHIELD = "divine_shield"    # 圣盾
    STEALTH = "stealth"                # 潜行
    WINDFURY = "windfury"              # 风怒
    POISONOUS = "poisonous"            # 剧毒
    LIFESTEAL = "lifesteal"            # 生命偷取
    CANT_BE_TARGETED = "cant_be_targeted"  # 无法成为目标


@dataclass
class CardStats:
    """卡牌基础属性"""
    attack: int = 0
    health: int = 0
    cost: int = 0
    armor: int = 0
    mana_cost: int = 0


@dataclass
class CardInfo:
    """卡牌基本信息"""
    id: str
    name: str
    description: str
    card_type: CardType
    rarity: CardRarity
    card_set: CardSet
    class_name: str  # 职业：战士、法师、牧师等
    mechanics: List[Mechanic] = field(default_factory=list)
    stats: CardStats = field(default_factory=CardStats)


@dataclass
class CardInstance:
    """卡牌实例（在游戏中的具体卡牌）"""
    card_info: CardInfo
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_attack: int = 0
    current_health: int = 0
    current_cost: int = 0
    damage_taken: int = 0
    is_dormant: bool = False  # 休眠
    is_silenced: bool = False  # 沉默
    is_stealthed: bool = False  # 潜行状态
    attacks_this_turn: int = 0
    can_attack: bool = False
    is_frozen: bool = False
    enchantments: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        # 初始化当前属性
        self.current_attack = self.card_info.stats.attack
        self.current_health = self.card_info.stats.health
        self.current_cost = self.card_info.stats.cost

    @property
    def is_alive(self) -> bool:
        """卡牌是否存活"""
        return self.current_health > 0

    @property
    def effective_attack(self) -> int:
        """有效攻击力"""
        if self.is_frozen or self.is_dormant:
            return 0
        return max(0, self.current_attack)

    @property
    def effective_health(self) -> int:
        """有效生命值"""
        return max(0, self.current_health - self.damage_taken)

    @property
    def has_taunt(self) -> bool:
        """是否有嘲讽"""
        return (not self.is_silenced and
                Mechanic.TAUNT in self.card_info.mechanics)

    @property
    def has_charge(self) -> bool:
        """是否有冲锋"""
        return (not self.is_silenced and
                Mechanic.CHARGE in self.card_info.mechanics)

    @property
    def has_divine_shield(self) -> bool:
        """是否有圣盾"""
        return (not self.is_silenced and
                Mechanic.DIVINE_SHIELD in self.card_info.mechanics)

    @property
    def has_windfury(self) -> bool:
        """是否有风怒"""
        return (not self.is_silenced and
                Mechanic.WINDFURY in self.card_info.mechanics)

    def take_damage(self, damage: int) -> int:
        """受到伤害，返回实际伤害值"""
        if damage <= 0:
            return 0

        # 圣盾保护
        if self.has_divine_shield:
            self._remove_divine_shield()
            return 0

        self.damage_taken += damage
        return damage

    def heal(self, amount: int) -> int:
        """治疗，返回实际治疗量"""
        if amount <= 0:
            return 0

        old_damage = self.damage_taken
        self.damage_taken = max(0, self.damage_taken - amount)
        return old_damage - self.damage_taken

    def restore_full_health(self):
        """完全恢复生命值"""
        self.damage_taken = 0

    def silence(self):
        """沉默卡牌"""
        self.is_silenced = True
        self.enchantments.clear()

    def _remove_divine_shield(self):
        """移除圣盾（简化实现）"""
        # 实际实现中需要处理圣盾移除的逻辑
        pass

    def add_enchantment(self, enchantment: Dict[str, Any]):
        """添加魔法效果"""
        self.enchantments.append(enchantment)
        self._apply_enchantment(enchantment)

    def _apply_enchantment(self, enchantment: Dict[str, Any]):
        """应用魔法效果"""
        enchant_type = enchantment.get("type")

        if enchant_type == "attack_buff":
            buff_amount = enchantment.get("amount", 0)
            self.current_attack += buff_amount
        elif enchant_type == "health_buff":
            buff_amount = enchantment.get("amount", 0)
            self.current_health += buff_amount
        elif enchant_type == "cost_reduction":
            reduction = enchantment.get("amount", 0)
            self.current_cost = max(0, self.current_cost - reduction)

    def get_state_summary(self) -> Dict[str, Any]:
        """获取卡牌状态摘要"""
        return {
            "instance_id": self.instance_id,
            "name": self.card_info.name,
            "card_type": self.card_info.card_type.value,
            "cost": self.current_cost,
            "attack": self.effective_attack,
            "health": self.effective_health,
            "max_health": self.current_health,
            "is_alive": self.is_alive,
            "can_attack": self.can_attack and self.effective_attack > 0,
            "mechanics": [m.value for m in self.card_info.mechanics if not self.is_silenced],
            "is_silenced": self.is_silenced,
            "is_frozen": self.is_frozen,
            "damage_taken": self.damage_taken
        }


class BaseCard(ABC):
    """卡牌基础类"""

    def __init__(self, card_info: CardInfo):
        self.card_info = card_info
        self._validation_rules = []

    @abstractmethod
    def can_play(self, game_state: 'GameState', player: 'Player') -> bool:
        """
        检查是否可以出牌

        Args:
            game_state: 游戏状态
            player: 出牌玩家

        Returns:
            bool: 是否可以出牌
        """
        pass

    @abstractmethod
    async def play_card(self, game_state: 'GameState', player: 'Player',
                       target: Optional['CardInstance'] = None) -> bool:
        """
        出牌效果

        Args:
            game_state: 游戏状态
            player: 出牌玩家
            target: 目标（可选）

        Returns:
            bool: 出牌是否成功
        """
        pass

    @abstractmethod
    def get_valid_targets(self, game_state: 'GameState',
                         player: 'Player') -> List['CardInstance']:
        """
        获取有效目标列表

        Args:
            game_state: 游戏状态
            player: 出牌玩家

        Returns:
            List[CardInstance]: 有效目标列表
        """
        pass

    def validate_play(self, game_state: 'GameState', player: 'Player',
                     target: Optional['CardInstance'] = None) -> tuple[bool, str]:
        """
        验证出牌合法性

        Returns:
            tuple[bool, str]: (是否合法, 原因)
        """
        # 基础验证
        if self.card_info.stats.cost > player.current_mana:
            return False, "法力值不足"

        if not self.can_play(game_state, player):
            return False, "当前状态下不能出这张牌"

        # 检查目标合法性
        if target is not None:
            valid_targets = self.get_valid_targets(game_state, player)
            if target not in valid_targets:
                return False, "无效目标"

        # 自定义验证规则
        for rule in self._validation_rules:
            is_valid, reason = rule(game_state, player, target)
            if not is_valid:
                return False, reason

        return True, ""

    def add_validation_rule(self, rule_func):
        """添加验证规则"""
        self._validation_rules.append(rule_func)

    def create_instance(self) -> CardInstance:
        """创建卡牌实例"""
        return CardInstance(card_info=self.card_info)

    def __repr__(self):
        return f"{self.card_info.name} ({self.card_info.card_type.value}) - " \
               f"{self.card_info.stats.cost}费 {self.card_info.stats.attack}/{self.card_info.stats.health}"


# 前向声明（避免循环导入）
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..game_state.game_state import GameState
    from ..game_state.player import Player