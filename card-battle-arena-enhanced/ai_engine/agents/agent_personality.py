"""
AI代理人格系统
定义不同性格的AI代理，每个代理有独特的决策风格和偏好
"""
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import random


class PersonalityTrait(Enum):
    """性格特征枚举"""
    AGGRESSIVE = "aggressive"          # 激进
    DEFENSIVE = "defensive"           # 防御
    CONTROL_ORIENTED = "control"      # 控制型
    COMBO_ORIENTED = "combo"          # 连锁型
    VALUE_ORIENTED = "value"          # 价值型
    RISK_TAKER = "risk_taker"         # 冒险型
    CAUTIOUS = "cautious"             # 谨慎型
    ADAPTIVE = "adaptive"             # 适应性
    METAGAMER = "metagamer"           # 环境适应型
    FUN_LOVING = "fun_loving"         # 娱乐型


class PlayStyle(Enum):
    """游戏风格"""
    TEMPO = "tempo"                   # 快节奏
    MIDRANGE = "midrange"            # 中速
    CONTROL = "control"              # 控制
    AGGRO = "aggro"                  # 快攻
    RAMP = "ramp"                    # 跳费
    OTK = "otk"                      # 一击必杀
    COMBO_ORIENTED = "combo"         # 连锁型


@dataclass
class PersonalityProfile:
    """人格配置档案"""
    name: str
    description: str
    traits: List[PersonalityTrait]
    play_style: PlayStyle

    # 决策权重
    risk_tolerance: float = 0.5        # 风险容忍度 0-1
    aggression_level: float = 0.5     # 激进程度 0-1
    patience_level: float = 0.5       # 耐心程度 0-1

    # 卡牌偏好
    card_preferences: Dict[str, float] = field(default_factory=dict)
    mana_curve_preference: float = 0.5  # 法力曲线偏好

    # 行为模式
    thinking_time_range: tuple[float, float] = (0.5, 2.0)  # 思考时间范围
    emotion_factor: float = 0.5      # 情感因素 0-1
    learning_rate: float = 0.5       # 学习速率 0-1

    # 特殊行为
    emote_frequency: float = 0.3     # 表情使用频率
    bm_frequency: float = 0.1        # 嘲讽频率

    def get_decision_weight(self, factor: str) -> float:
        """获取决策权重"""
        weight_map = {
            "risk": self.risk_tolerance,
            "aggression": self.aggression_level,
            "patience": self.patience_level,
            "emotion": self.emotion_factor
        }
        return weight_map.get(factor, 0.5)


# 预定义人格配置
PERSONALITY_PROFILES = {
    "aggressive_berserker": PersonalityProfile(
        name="狂战士",
        description="极度激进的战斗风格，追求快速击败对手",
        traits=[PersonalityTrait.AGGRESSIVE, PersonalityTrait.RISK_TAKER],
        play_style=PlayStyle.AGGRO,
        risk_tolerance=0.8,
        aggression_level=0.9,
        patience_level=0.2,
        card_preferences={
            "high_attack": 1.5,
            "charge": 1.3,
            "direct_damage": 1.4,
            "taunt": 0.7
        },
        thinking_time_range=(0.3, 1.0),
        emotion_factor=0.8,
        bm_frequency=0.3
    ),

    "wise_defender": PersonalityProfile(
        name="智慧守护者",
        description="谨慎的防御型玩家，重视场面控制和生存",
        traits=[PersonalityTrait.DEFENSIVE, PersonalityTrait.CAUTIOUS],
        play_style=PlayStyle.CONTROL,
        risk_tolerance=0.2,
        aggression_level=0.3,
        patience_level=0.9,
        card_preferences={
            "taunt": 1.5,
            "healing": 1.4,
            "removal": 1.3,
            "card_draw": 1.2
        },
        thinking_time_range=(1.0, 3.0),
        emotion_factor=0.3,
        bm_frequency=0.05
    ),

    "strategic_mastermind": PersonalityProfile(
        name="战略大师",
        description="善于长期规划，重视价值交换和资源管理",
        traits=[PersonalityTrait.CONTROL_ORIENTED, PersonalityTrait.VALUE_ORIENTED],
        play_style=PlayStyle.MIDRANGE,
        risk_tolerance=0.5,
        aggression_level=0.5,
        patience_level=0.8,
        card_preferences={
            "card_draw": 1.4,
            "board_clear": 1.3,
            "value_generation": 1.5,
            "flexibility": 1.2
        },
        thinking_time_range=(1.5, 2.5),
        emotion_factor=0.4,
        learning_rate=0.7
    ),

    "combo_enthusiast": PersonalityProfile(
        name="连锁爱好者",
        description="喜欢寻找复杂配合，追求华丽的连锁效果",
        traits=[PersonalityTrait.COMBO_ORIENTED, PersonalityTrait.RISK_TAKER],
        play_style=PlayStyle.COMBO_ORIENTED,
        risk_tolerance=0.7,
        aggression_level=0.6,
        patience_level=0.6,
        card_preferences={
            "combo": 1.8,
            "spell_power": 1.4,
            "card_generation": 1.3,
            "copy_effects": 1.5
        },
        thinking_time_range=(2.0, 4.0),
        emotion_factor=0.7,
        learning_rate=0.8
    ),

    "adaptive_learner": PersonalityProfile(
        name="适应性学习者",
        description="能够根据对手风格调整策略的多面手",
        traits=[PersonalityTrait.ADAPTIVE, PersonalityTrait.METAGAMER],
        play_style=PlayStyle.MIDRANGE,
        risk_tolerance=0.5,
        aggression_level=0.5,
        patience_level=0.5,
        card_preferences={},  # 根据情况动态调整
        thinking_time_range=(0.8, 2.5),
        emotion_factor=0.5,
        learning_rate=0.9
    ),

    "fun_seeker": PersonalityProfile(
        name="娱乐玩家",
        description="追求有趣和创意的玩法，不拘一格",
        traits=[PersonalityTrait.FUN_LOVING, PersonalityTrait.RISK_TAKER],
        play_style=PlayStyle.TEMPO,
        risk_tolerance=0.6,
        aggression_level=0.6,
        patience_level=0.4,
        card_preferences={
            "random_effects": 1.5,
            "fun_mechanics": 1.4,
            "unusual_interactions": 1.3
        },
        thinking_time_range=(0.5, 1.5),
        emotion_factor=0.9,
        emote_frequency=0.8
    )
}


class PersonalityManager:
    """人格管理器"""

    def __init__(self):
        self.profiles = PERSONALITY_PROFILES.copy()
        self.custom_profiles: Dict[str, PersonalityProfile] = {}

    def get_profile(self, name: str) -> Optional[PersonalityProfile]:
        """获取人格配置"""
        return self.profiles.get(name) or self.custom_profiles.get(name)

    def register_custom_profile(self, profile: PersonalityProfile):
        """注册自定义人格"""
        self.custom_profiles[profile.name] = profile

    def get_random_profile(self) -> PersonalityProfile:
        """获取随机人格"""
        all_profiles = {**self.profiles, **self.custom_profiles}
        return random.choice(list(all_profiles.values()))

    def get_profiles_by_trait(self, trait: PersonalityTrait) -> List[PersonalityProfile]:
        """根据特征获取人格列表"""
        all_profiles = {**self.profiles, **self.custom_profiles}
        return [p for p in all_profiles.values() if trait in p.traits]

    def get_profiles_by_style(self, style: PlayStyle) -> List[PersonalityProfile]:
        """根据游戏风格获取人格列表"""
        all_profiles = {**self.profiles, **self.custom_profiles}
        return [p for p in all_profiles.values() if p.play_style == style]

    def create_hybrid_profile(self, name: str, base_profiles: List[str],
                            weights: List[float]) -> PersonalityProfile:
        """创建混合人格配置"""
        if len(base_profiles) != len(weights):
            raise ValueError("基础配置和权重数量不匹配")

        # 归一化权重
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # 获取基础配置
        profiles = [self.get_profile(bp) for bp in base_profiles]
        if any(p is None for p in profiles):
            raise ValueError("存在无效的基础配置")

        # 计算加权平均属性
        risk_tolerance = sum(p.risk_tolerance * w for p, w in zip(profiles, weights))
        aggression_level = sum(p.aggression_level * w for p, w in zip(profiles, weights))
        patience_level = sum(p.patience_level * w for p, w in zip(profiles, weights))

        # 合并特征和偏好
        all_traits = set()
        for profile in profiles:
            all_traits.update(profile.traits)

        merged_preferences = {}
        for profile in profiles:
            for key, value in profile.card_preferences.items():
                if key in merged_preferences:
                    merged_preferences[key] = (merged_preferences[key] + value) / 2
                else:
                    merged_preferences[key] = value

        # 选择出现频率最高的游戏风格
        style_votes = {}
        for profile in profiles:
            style = profile.play_style
            style_votes[style] = style_votes.get(style, 0) + 1

        dominant_style = max(style_votes.keys(), key=lambda x: style_votes[x])

        # 计算时间范围
        min_times = [p.thinking_time_range[0] for p in profiles]
        max_times = [p.thinking_time_range[1] for p in profiles]

        return PersonalityProfile(
            name=name,
            description=f"混合人格: {', '.join(base_profiles)}",
            traits=list(all_traits),
            play_style=dominant_style,
            risk_tolerance=risk_tolerance,
            aggression_level=aggression_level,
            patience_level=patience_level,
            card_preferences=merged_preferences,
            thinking_time_range=(min(min_times), max(max_times)),
            emotion_factor=sum(p.emotion_factor * w for p, w in zip(profiles, weights))
        )

    def evolve_personality(self, profile: PersonalityProfile,
                          game_outcomes: List[Dict[str, Any]]) -> PersonalityProfile:
        """基于游戏结果进化人格"""
        evolved_profile = PersonalityProfile(
            name=profile.name,
            description=profile.description + " (进化版)",
            traits=profile.traits.copy(),
            play_style=profile.play_style,
            risk_tolerance=profile.risk_tolerance,
            aggression_level=profile.aggression_level,
            patience_level=profile.patience_level,
            card_preferences=profile.card_preferences.copy(),
            thinking_time_range=profile.thinking_time_range,
            emotion_factor=profile.emotion_factor,
            learning_rate=profile.learning_rate
        )

        if not game_outcomes:
            return evolved_profile

        # 计算胜率
        win_rate = sum(1 for outcome in game_outcomes if outcome.get("won", False)) / len(game_outcomes)

        # 根据表现调整属性
        if win_rate < 0.4:  # 表现不佳，需要调整
            adjustment = profile.learning_rate * 0.1

            # 如果过于激进导致失败，降低激进程度
            if profile.aggression_level > 0.7:
                evolved_profile.aggression_level = max(0.3, profile.aggression_level - adjustment)
                evolved_profile.patience_level = min(0.9, profile.patience_level + adjustment)

            # 如果过于保守导致失败，提高激进程度
            elif profile.aggression_level < 0.3:
                evolved_profile.aggression_level = min(0.7, profile.aggression_level + adjustment)
                evolved_profile.risk_tolerance = min(0.8, profile.risk_tolerance + adjustment)

        elif win_rate > 0.7:  # 表现优秀，强化当前风格
            reinforcement = profile.learning_rate * 0.05

            # 强化成功的特征
            evolved_profile.aggression_level = min(1.0, profile.aggression_level + reinforcement * 0.5)
            evolved_profile.emotion_factor = min(1.0, profile.emotion_factor + reinforcement * 0.3)

        return evolved_profile