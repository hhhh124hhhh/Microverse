"""
Card Battle Arena Enhanced - 卡牌游戏核心引擎
提供完整的游戏状态管理和回合制流程控制
"""
import random
import asyncio
import logging
import shutil
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


def get_terminal_width() -> int:
    """获取终端宽度，失败时返回默认值"""
    try:
        # 尝试获取真实的终端尺寸
        size = shutil.get_terminal_size()
        width = size.columns

        # 验证宽度的合理性
        if width < 20:  # 终端太窄，不正常
            return 80
        elif width > 300:  # 终端太宽，可能不正常
            return 120

        return width
    except:
        # 备用方法：使用环境变量
        try:
            import os
            if 'COLUMNS' in os.environ:
                width = int(os.environ['COLUMNS'])
                if 20 <= width <= 300:
                    return width
        except:
            pass

    # 最终备用值
    return 80


def calculate_table_widths(terminal_width: int, min_widths: Dict[str, int],
                          total_min_width: int) -> Dict[str, int]:
    """
    根据终端宽度动态计算表格列宽

    Args:
        terminal_width: 终端总宽度
        min_widths: 每列的最小宽度要求
        total_min_width: 所有列的最小宽度总和

    Returns:
        各列的实际宽度
    """
    # 处理终端宽度异常情况
    if terminal_width < 40:  # 极窄终端
        terminal_width = 40
    elif terminal_width > 200:  # 极宽终端限制
        terminal_width = 200

    # 调整边框和间距的预留宽度 - 考虑Panel和Layout的额外开销
    border_reserve = 20 if terminal_width > 80 else 15

    if terminal_width <= total_min_width + border_reserve:
        # 终端太窄，按比例缩放最小宽度
        scale_factor = (terminal_width - border_reserve) / total_min_width
        result = {}
        for key, width in min_widths.items():
            result[key] = max(1, int(width * scale_factor))
        return result

    # 计算可分配的额外宽度
    extra_width = terminal_width - total_min_width - border_reserve

    if extra_width <= 0:
        return min_widths

    # 智能分配额外宽度，优先保证关键列的可用性
    result = min_widths.copy()

    # 优先级分配：编号列 > 卡牌名称 > 属性 > 类型 > 状态
    # 编号列必须足够显示数字，优先分配
    if "index" in result:
        result["index"] = min(result["index"] + 2, 8)  # 确保编号列至少能显示2位数

    remaining_width = extra_width - (result["index"] - min_widths["index"])

    # 卡牌名称获得最大比例的额外宽度（最重要的信息）
    if "name" in result and remaining_width > 0:
        name_extra = min(remaining_width * 0.5, 15)  # 最多分配15个额外字符
        result["name"] = min(result["name"] + int(name_extra), 40)
        remaining_width -= int(name_extra)

    # 属性列获得剩余宽度的40%
    if "stats" in result and remaining_width > 0:
        stats_extra = min(remaining_width * 0.4, 8)
        result["stats"] = min(result["stats"] + int(stats_extra), 15)
        remaining_width -= int(stats_extra)

    # 类型列获得剩余宽度的30%
    if "type" in result and remaining_width > 0:
        type_extra = min(remaining_width * 0.3, 6)
        result["type"] = min(result["type"] + int(type_extra), 12)
        remaining_width -= int(type_extra)

    # 状态列获得剩余的所有宽度
    if "status" in result and remaining_width > 0:
        result["status"] = min(result["status"] + int(remaining_width), 12)

    return result


def truncate_text(text: str, max_length: int, add_ellipsis: bool = True) -> str:
    """
    截断文本到指定长度

    Args:
        text: 要截断的文本
        max_length: 最大长度
        add_ellipsis: 是否添加省略号

    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text

    if add_ellipsis and max_length > 3:
        return text[:max_length-3] + "..."
    else:
        return text[:max_length]


def safe_get_card_attr(card, attr_name, default=None):
    """安全获取卡牌属性，支持对象和字典格式"""
    try:
        # 尝试直接访问属性（对象格式）
        return getattr(card, attr_name)
    except AttributeError:
        try:
            # 尝试字典访问
            return card[attr_name]
        except (KeyError, TypeError):
            return default

def get_card_name(card):
    """获取卡牌名称"""
    return safe_get_card_attr(card, 'name', '未知卡牌')

def get_card_attack(card):
    """获取卡牌攻击力"""
    return safe_get_card_attr(card, 'attack', 0)

def get_card_health(card):
    """获取卡牌血量"""
    return safe_get_card_attr(card, 'health', 0)

def get_minion_can_attack(card, default=False):
    """安全获取随从攻击状态"""
    try:
        # 优先尝试直接访问属性
        return getattr(card, 'can_attack', default)
    except:
        try:
            # 尝试字典访问
            return card['can_attack']
        except (KeyError, TypeError):
            # 如果是随从类型但没有攻击状态，默认为新上场不可攻击
            if safe_get_card_attr(card, 'card_type', '') == 'minion':
                return False  # 新上场的随从默认不能攻击
            return default

def ensure_minion_attack_state(card):
    """确保随从有正确的攻击状态"""
    if safe_get_card_attr(card, 'card_type', '') == 'minion':
        # 如果随从没有can_attack属性，设置为False
        if not hasattr(card, 'can_attack'):
            card.can_attack = False
        # 如果can_attack为None，设置为False
        elif getattr(card, 'can_attack') is None:
            card.can_attack = False
    return card


@dataclass
class Card:
    """卡牌数据类"""
    name: str
    cost: int
    attack: int
    health: int
    card_type: str  # "minion", "spell"
    mechanics: List[str] = field(default_factory=list)
    instance_id: str = ""
    description: str = ""

    def __post_init__(self):
        if not self.instance_id:
            self.instance_id = f"card_{random.randint(1000, 9999)}"
        # 为随从添加攻击状态标记
        if self.card_type == "minion":
            self.can_attack = False  # 新上场的随从本回合不能攻击


@dataclass
class Player:
    """玩家数据类"""
    name: str
    health: int = 30
    max_health: int = 30
    mana: int = 1
    max_mana: int = 1
    hand: List[Card] = field(default_factory=list)
    field: List[Card] = field(default_factory=list)
    deck_size: int = 25

    def can_play_card(self, card: Card) -> bool:
        """检查是否能打出卡牌"""
        return card.cost <= self.mana

    def use_mana(self, amount: int):
        """使用法力值"""
        self.mana = max(0, self.mana - amount)

    def gain_mana(self, amount: int):
        """获得法力值"""
        self.mana = min(self.max_mana, self.mana + amount)

    def start_turn(self):
        """回合开始"""
        if self.max_mana < 10:
            self.max_mana += 1
        self.mana = self.max_mana

    def draw_card(self, card: Card = None) -> Dict[str, Any]:
        """抽牌 - 支持疲劳伤害机制"""
        result = {"success": False, "fatigue_damage": 0, "message": ""}

        if len(self.hand) < 10 and card is not None:
            # 正常抽牌
            self.hand.append(card)
            self.deck_size = max(0, self.deck_size - 1)
            result["success"] = True
            result["message"] = f"抽到了 {card.name}"
        else:
            # 手牌已满，但牌组还有牌
            if self.deck_size > 0 and card is not None:
                # 牌被弃掉，但牌组数量减少
                self.deck_size = max(0, self.deck_size - 1)
                result["message"] = f"手牌已满，{card.name} 被弃掉"
            else:
                # 疲劳伤害
                if not hasattr(self, 'fatigue_count'):
                    self.fatigue_count = 0

                self.fatigue_count += 1
                self.health -= self.fatigue_count
                result["fatigue_damage"] = self.fatigue_count
                result["message"] = f"疲劳伤害 {self.fatigue_count} 点"

        return result


class CardGame:
    """卡牌游戏核心引擎"""

    def __init__(self, player1_name: str = "玩家1", player2_name: str = "玩家2"):
        self.players = [
            Player(player1_name),
            Player(player2_name)
        ]
        self.current_player_idx = 0
        self.turn_number = 1
        self.game_over = False
        self.winner = None

        # 初始化卡牌池
        self.card_pool = self._create_card_pool()

        # 初始抽牌
        self._initial_draw()

        logger.info(f"🎮 新游戏开始: {player1_name} vs {player2_name}")

    def _create_card_pool(self) -> List[Card]:
        """创建卡牌池 - 优化随从和法术比例"""
        return [
            # 基础随从牌 (增加数量和多样性)
            Card("烈焰元素", 3, 5, 3, "minion", [], "💥 火焰元素的愤怒，燃烧一切敌人"),
            Card("霜狼步兵", 2, 2, 3, "minion", ["taunt"], "🛡️ 诺森德的精锐步兵，身披重甲守护前线"),
            Card("铁喙猫头鹰", 3, 2, 2, "minion", ["taunt"], "🦉 夜空中的猎手，锐利的铁喙撕裂敌人"),
            Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客，悄无声息地接近目标"),
            Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者，神圣护盾保护其免受首次伤害"),
            Card("铁炉堡火枪手", 2, 2, 2, "minion", ["ranged"], "🔫 矮人神射手，远程精准打击敌人"),
            Card("暴风雪骑士", 6, 6, 5, "minion", ["taunt", "divine_shield"], "🌨️ 暴风城的精英骑士，身披圣铠手持坚盾"),
            Card("铁炉堡士兵", 2, 1, 4, "minion", ["taunt"], "⚔️ 铁炉堡的忠诚士兵，誓死守护阵地"),
            Card("暗影巫师", 3, 2, 3, "minion", ["spell_power"], "🧙‍♂️ 掌控暗影力量的神秘巫师"),
            # 新增更多随从牌
            Card("森林狼", 1, 1, 1, "minion", [], "🐺 野性的森林狼，凶猛的掠食者"),
            Card("鹰身女妖", 2, 2, 1, "minion", ["ranged"], "🦅 天空的猎手，远程攻击敌人"),
            Card("岩石元素", 4, 3, 5, "minion", ["taunt"], "🗿 坚固的岩石守护者"),
            Card("火焰元素", 3, 4, 4, "minion", [], "🔥 燃烧的元素，攻击力强大"),
            Card("冰霜元素", 4, 3, 5, "minion", ["freeze"], "❄️ 寒冰元素，能够冻结敌人"),
            Card("暗影猎手", 3, 3, 3, "minion", ["stealth"], "🌑 隐藏在阴影中的猎手"),

            # 平衡优化后的法术牌
            Card("火球术", 4, 6, 0, "spell", [], "🔥 法师经典法术，召唤炽热火球轰击敌人"),
            Card("闪电箭", 1, 2, 0, "spell", [], "⚡ 快速的闪电攻击，造成2点伤害"),
            Card("治愈术", 2, -5, 0, "spell", [], "💚 圣光之力，恢复5点生命值"),
            Card("奥术智慧", 3, 0, 0, "spell", ["draw_cards"], "📚 深奥的魔法知识，从虚空中抽取两张卡牌"),
            Card("寒冰箭", 2, 3, 0, "spell", ["freeze"], "❄️ 极寒之冰，冻结敌人并造成3点伤害"),
            Card("暗影步", 1, 0, 0, "spell", ["return"], "🌑 影子魔法，将一个随从返回手中重新部署"),
            Card("神圣惩击", 4, 5, 0, "spell", [], "✨ 圣光审判，对邪恶敌人造成5点伤害"),
            Card("治疗之环", 1, -2, 0, "spell", [], "💫 温和的治疗法术，恢复2点生命值"),
            # 新增中等费用法术
            Card("烈焰风暴", 5, 4, 0, "spell", [], "🔥 火焰风暴，对敌人造成4点伤害"),
            Card("冰锥术", 3, 2, 0, "spell", ["freeze"], "❄️ 冰锥攻击，冻结敌人并造成2点伤害"),
            Card("暗影箭", 3, 4, 0, "spell", [], "🌑 暗影能量箭，造成4点伤害"),
            # 高费用法术
            Card("炎爆术", 8, 10, 0, "spell", [], "🌋 毁灭性的火焰魔法，造成10点巨额伤害"),
            Card("冰霜新星", 3, 2, 0, "spell", ["freeze"], "❄️ 冰系范围法术，冻结所有敌人"),
            Card("心灵震爆", 6, 7, 0, "spell", [], "💢 精神冲击，造成7点伤害"),
            Card("神圣新星", 5, 3, 0, "spell", [], "✨ 圣光爆发，造成3点伤害并恢复2点生命")
        ]

    def _initial_draw(self):
        """初始抽牌 - 确保开局高可用性"""
        for player in self.players:
            for i in range(3):
                if player.deck_size > 0:
                    # 按费用分层抽牌，确保前期可用
                    if i == 0:
                        # 第一张牌：必须是1费随从
                        one_cost_minions = [card for card in self.card_pool
                                            if card.card_type == "minion" and card.cost == 1]
                        card = random.choice(one_cost_minions) if one_cost_minions else self._fallback_card()
                    elif i == 1:
                        # 第二张牌：优先1费，其次是1-2费
                        one_cost_cards = [card for card in self.card_pool if card.cost == 1]
                        if one_cost_cards:
                            card = random.choice(one_cost_cards)
                        else:
                            two_cost_cards = [card for card in self.card_pool if card.cost == 2]
                            card = random.choice(two_cost_cards) if two_cost_cards else self._fallback_card()
                    else:
                        # 第三张牌：优先1-2费，确保至少2张可用牌
                        early_playable = [card for card in self.card_pool if card.cost <= 2]
                        card = random.choice(early_playable) if early_playable else self._fallback_card()

                    draw_result = player.draw_card(card)
                    if not draw_result["success"]:
                        logger.warning(f"⚠️ 初始抽牌失败: {draw_result['message']}")

    def _fallback_card(self) -> Card:
        """备用卡牌选择，确保游戏能进行"""
        # 返回费用最低的卡牌
        min_cost = min(card.cost for card in self.card_pool)
        cheapest = [card for card in self.card_pool if card.cost == min_cost]
        return random.choice(cheapest)

    def _get_cheap_card(self) -> Card:
        """获取低费卡牌的备用方案"""
        # 按优先级返回低费卡牌
        cheap_cards = [card for card in self.card_pool if card.cost <= 2]
        if cheap_cards:
            return random.choice(cheap_cards)

        # 如果没有低费卡牌，返回费用最低的卡牌
        min_cost = min(card.cost for card in self.card_pool)
        cheapest = [card for card in self.card_pool if card.cost == min_cost]
        return random.choice(cheapest)

    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_idx]

    def get_opponent(self) -> Player:
        """获取对手"""
        return self.players[1 - self.current_player_idx]

    def _smart_draw_card(self, player: Player) -> Card:
        """智能抽牌系统 - 平衡随从和法术比例"""
        # 统计手牌中的随从和法术数量
        minion_count = sum(1 for card in player.hand if card.card_type == "minion")
        spell_count = sum(1 for card in player.hand if card.card_type == "spell")

        # 分离卡牌池中的随从和法术
        minions = [card for card in self.card_pool if card.card_type == "minion"]
        spells = [card for card in self.card_pool if card.card_type == "spell"]

        # 智能抽牌策略
        if minion_count < spell_count - 1:
            # 随从明显少于法术，提高随从概率
            weights = [0.8, 0.2]  # 80%随从，20%法术
        elif spell_count < minion_count - 1:
            # 法术明显少于随从，提高法术概率
            weights = [0.3, 0.7]  # 30%随从，70%法术
        else:
            # 相对平衡，使用正常权重
            weights = [0.6, 0.4]  # 60%随从，40%法术

        # 根据权重选择卡牌类型
        card_type = random.choices(["minion", "spell"], weights=weights)[0]

        if card_type == "minion" and minions:
            return random.choice(minions)
        elif card_type == "spell" and spells:
            return random.choice(spells)
        else:
            # 备用方案：随机选择
            return random.choice(self.card_pool)

    def start_turn(self):
        """开始新的回合"""
        current = self.get_current_player()
        current.start_turn()

        # 激活场上随从的攻击状态
        for minion in current.field:
            minion.can_attack = True

        # 智能抽牌系统 - 平衡随从和法术比例
        if current.deck_size > 0:
            card = self._smart_draw_card(current)
            draw_result = current.draw_card(card)

            if draw_result["success"]:
                logger.info(f"🃏 {current.name} {draw_result['message']}")
            elif draw_result["fatigue_damage"] > 0:
                logger.warning(f"💀 {current.name} 受到 {draw_result['fatigue_damage']} 点疲劳伤害，剩余血量: {current.health}")
            elif "被弃掉" in draw_result["message"]:
                logger.info(f"🗑️ {current.name} {draw_result['message']}")
        else:
            # 牌组已空，检查疲劳伤害
            draw_result = current.draw_card(None)  # 触发疲劳伤害
            if draw_result["fatigue_damage"] > 0:
                logger.warning(f"💀 {current.name} 受到 {draw_result['fatigue_damage']} 点疲劳伤害，剩余血量: {current.health}")

        self.turn_number += 1
        logger.info(f"🔄 回合 {self.turn_number} - {current.name} 回合")

    def play_card(self, player_idx: int, card_idx: int) -> Dict[str, Any]:
        """打出卡牌"""
        if player_idx != self.current_player_idx:
            return {"success": False, "message": "不是你的回合"}

        player = self.players[player_idx]
        if card_idx >= len(player.hand):
            return {"success": False, "message": "无效的卡牌索引"}

        card = player.hand[card_idx]

        if not player.can_play_card(card):
            return {"success": False, "message": f"法力值不足，需要 {card.cost} 点法力"}

        # 扣除法力
        player.use_mana(card.cost)

        # 从手牌移除
        player.hand.pop(card_idx)

        result = {
            "success": True,
            "card": card,
            "message": f"{player.name} 打出了 {get_card_name(card)}"
        }

        # 根据卡牌类型执行效果
        if card.card_type == "minion":
            # 随从上场
            player.field.append(card)
            result["message"] += f" ({card.attack}/{card.health})"
            logger.info(f"  ⚔️ {result['message']}")

        elif card.card_type == "spell":
            # 法术效果
            opponent = self.get_opponent()
            if "draw_cards" in card.mechanics:
                # 抽牌法术
                cards_drawn = 0
                for _ in range(2):
                    if opponent.deck_size > 0:
                        draw_card = random.choice(self.card_pool)
                        draw_result = opponent.draw_card(draw_card)
                        if draw_result["success"]:
                            cards_drawn += 1
                        else:
                            logger.info(f"📚 {opponent.name} {draw_result['message']}")
                result["message"] += f"，抽了{cards_drawn}张牌"
                logger.info(f"  📚 {result['message']}")
            elif "freeze" in card.mechanics:
                # 冻结法术 - 造成伤害并冻结对手场上所有随从
                opponent.health -= card.attack
                # 冻结对手场上所有随从（简化实现）
                for minion in opponent.field:
                    # 在这个简化版本中，我们只是记录冻结效果
                    # 实际的冻结机制需要更复杂的实现
                    pass
                result["message"] += f"，造成 {card.attack} 点伤害并冻结所有敌人"
                logger.info(f"  ❄️ {result['message']}")
            elif "return" in card.mechanics:
                # 返回手牌法术 - 选择一个友方随从返回手牌
                if player.field:
                    # 简化实现：返回第一个随从到手牌
                    returned_minion = player.field.pop(0)
                    player.hand.append(returned_minion)
                    result["message"] += f"，将 {get_card_name(returned_minion)} 返回手牌"
                    logger.info(f"  🌙 {result['message']}")
                else:
                    result["message"] += "，但没有随从可以返回"
                    logger.info(f"  🌙 {result['message']}")
            elif card.attack > 0:
                # 伤害法术
                opponent.health -= card.attack
                result["message"] += f"，造成 {card.attack} 点伤害"
                logger.info(f"  🔥 {result['message']}")
            elif card.attack < 0:
                # 治疗法术
                player.health = min(player.max_health, player.health - card.attack)
                result["message"] += f"，恢复 {-card.attack} 点生命"
                logger.info(f"  💚 {result['message']}")

        # 检查游戏结束
        self._check_game_over()

        return result

    def use_hero_power(self, player_idx: int) -> Dict[str, Any]:
        """使用英雄技能"""
        if player_idx != self.current_player_idx:
            return {"success": False, "message": "不是你的回合"}

        player = self.players[player_idx]
        if player.mana < 2:
            return {"success": False, "message": "法力值不足，需要2点法力"}

        # 使用英雄技能（简化版：造成2点伤害）
        player.use_mana(2)
        opponent = self.get_opponent()
        opponent.health -= 2

        result = {
            "success": True,
            "message": f"{player.name} 使用英雄技能，造成2点伤害"
        }
        logger.info(f"  ⚡ {result['message']}")

        self._check_game_over()
        return result

    def end_turn(self, player_idx: int, auto_attack: bool = True) -> Dict[str, Any]:
        """结束回合"""
        if player_idx != self.current_player_idx:
            return {"success": False, "message": "不是你的回合"}

        # 执行战斗阶段（支持自动攻击）
        if auto_attack:
            messages = self._smart_combat_phase()
            if messages:
                logger.info(f"⚔️ 自动攻击: {'; '.join(messages)}")
        else:
            self._combat_phase()

        # 切换玩家
        self.current_player_idx = 1 - self.current_player_idx

        # 开始对手回合
        self.start_turn()

        return {
            "success": True,
            "message": f"回合结束，轮到 {self.get_current_player().name}"
        }

    def _smart_combat_phase(self) -> List[str]:
        """智能战斗阶段 - 自动进行最优攻击"""
        current = self.get_current_player()
        opponent = self.get_opponent()
        messages = []

        # 为新上场的随从设置攻击状态 - 只在回合开始时激活
        # 注意：这个函数在战斗阶段被调用，不应该重置攻击状态
        for minion in current.field:
            ensure_minion_attack_state(minion)
            # 不在这里强制设置can_attack，保持原有状态

        # 获取可攻击的随从
        attackable_minions = [i for i, minion in enumerate(current.field)
                            if get_minion_can_attack(minion, False)]

        if not attackable_minions:
            return messages

        # 如果对手没有随从，全部攻击英雄
        if not opponent.field:
            for minion_idx in attackable_minions:
                minion = current.field[minion_idx]
                opponent.health -= get_card_attack(minion)
                minion.can_attack = False
                # 兼容不同的卡牌数据格式
                minion_name = get_card_name(minion)
                messages.append(f"{minion_name} 攻击英雄 {get_card_attack(minion)} 点")
        else:
            # 智能攻击决策
            used_minions = set()

            # 优先处理：消灭低血量随从
            for minion_idx in attackable_minions:
                if minion_idx in used_minions or minion_idx >= len(current.field):
                    continue

                minion = current.field[minion_idx]

                # 寻找可以一击必杀的目标
                for target_idx, target in enumerate(opponent.field):
                    if get_card_health(target) <= get_card_attack(minion):
                        # 执行攻击 - 处理神圣护盾
                        damage_dealt = get_card_attack(minion)

                        # 检查目标是否有神圣护盾
                        if "divine_shield" in getattr(target, 'mechanics', []):
                            # 神圣护盾免疫首次伤害
                            damage_dealt = 0
                            # 移除神圣护盾
                            if hasattr(target, 'mechanics'):
                                target.mechanics.remove("divine_shield")
                            logger.info(f"  ✨ {get_card_name(target)} 的神圣护盾被击破")
                            # 神圣护盾被击破时，不会造成伤害
                            break  # 跳出这个目标，因为伤害被免疫了

                        target.health = get_card_health(target) - damage_dealt
                        minion.can_attack = False
                        # 兼容不同的卡牌数据格式
                        minion_name = get_card_name(minion)
                        target_name = get_card_name(target)
                        messages.append(f"{minion_name} 击败 {target_name}")

                        # 反击（除非潜行）
                        if "stealth" not in getattr(minion, 'mechanics', []):
                            minion.health = get_card_health(minion) - get_card_attack(target)

                        # 移除死亡的随从
                        if target.health <= 0:
                            opponent.field.remove(target)
                        if minion.health <= 0:
                            current.field.remove(minion)
                            break

                        used_minions.add(minion_idx)
                        break

            # 随机处理剩余可攻击的随从
            remaining_minions = [i for i in attackable_minions if i not in used_minions]
            for minion_idx in remaining_minions:
                if minion_idx >= len(current.field):  # 随从可能已死亡
                    continue

                minion = current.field[minion_idx]
                if not get_minion_can_attack(minion, False):
                    continue

                # 随机选择目标
                targets = []

                # 添加随从目标（优先非嘲讽）
                non_taunt_targets = [i for i, m in enumerate(opponent.field) if "taunt" not in m.mechanics]
                if non_taunt_targets:
                    targets.extend([f"随从_{i}" for i in non_taunt_targets])
                else:
                    targets.extend([f"随从_{i}" for i in range(len(opponent.field))])

                # 如果没有嘲讽随从，可以攻击英雄
                if not any("taunt" in m.mechanics for m in opponent.field):
                    targets.append("英雄")

                if targets:
                    target = random.choice(targets)
                    if target == "英雄":
                        opponent.health -= minion.attack
                        minion.can_attack = False
                        # 兼容不同的卡牌数据格式
                        minion_name = get_card_name(minion)
                        messages.append(f"{minion_name} 攻击英雄 {minion.attack} 点")
                    else:
                        target_idx = int(target.split("_")[1])
                        if target_idx < len(opponent.field):
                            target_minion = opponent.field[target_idx]

                            # 处理神圣护盾
                            damage_dealt = minion.attack
                            if "divine_shield" in getattr(target_minion, 'mechanics', []):
                                # 神圣护盾免疫首次伤害
                                damage_dealt = 0
                                # 移除神圣护盾
                                if hasattr(target_minion, 'mechanics'):
                                    target_minion.mechanics.remove("divine_shield")
                                logger.info(f"  ✨ {get_card_name(target_minion)} 的神圣护盾被击破")

                            target_minion.health -= damage_dealt
                            minion.can_attack = False
                            # 兼容不同的卡牌数据格式
                            minion_name = get_card_name(minion)
                            target_name = get_card_name(target_minion)
                            messages.append(f"{minion_name} vs {target_name}")

                            # 反击
                            if "stealth" not in getattr(minion, 'mechanics', []):
                                minion.health -= target_minion.attack

                            # 移除死亡的随从
                            if target_minion.health <= 0:
                                opponent.field.remove(target_minion)
                            if minion.health <= 0:
                                current.field.remove(minion)

        return messages

    def quick_play_card(self, player_idx: int, card_index: int) -> Dict[str, Any]:
        """快速出牌 - 直接使用卡牌索引"""
        if player_idx != self.current_player_idx:
            return {"success": False, "message": "不是你的回合"}

        player = self.players[player_idx]
        if card_index >= len(player.hand):
            return {"success": False, "message": "无效的卡牌索引"}

        card = player.hand[card_index]

        if not player.can_play_card(card):
            return {"success": False, "message": f"法力值不足，需要 {card.cost} 点法力"}

        # 扣除法力
        player.use_mana(card.cost)

        # 从手牌移除
        player.hand.pop(card_index)

        result = {
            "success": True,
            "card": card,
            "message": f"{player.name} 打出了 {get_card_name(card)}"
        }

        # 根据卡牌类型执行效果
        if card.card_type == "minion":
            # 随从上场，标记可以攻击
            player.field.append(card)
            # 新上场的随从本回合不能攻击（冲锋机制暂未实现）
            card.can_attack = False
            result["message"] += f" ({card.attack}/{card.health})"
            logger.info(f"  ⚔️ {result['message']}")

        elif card.card_type == "spell":
            # 法术效果
            opponent = self.get_opponent()
            if "draw_cards" in card.mechanics:
                # 抽牌法术
                cards_drawn = 0
                for _ in range(2):
                    if opponent.deck_size > 0:
                        draw_card = random.choice(self.card_pool)
                        draw_result = opponent.draw_card(draw_card)
                        if draw_result["success"]:
                            cards_drawn += 1
                        else:
                            logger.info(f"📚 {opponent.name} {draw_result['message']}")
                result["message"] += f"，抽了{cards_drawn}张牌"
                logger.info(f"  📚 {result['message']}")
            elif "freeze" in card.mechanics:
                # 冻结法术 - 造成伤害并冻结对手场上所有随从
                opponent.health -= card.attack
                # 冻结对手场上所有随从（简化实现）
                for minion in opponent.field:
                    # 在这个简化版本中，我们只是记录冻结效果
                    # 实际的冻结机制需要更复杂的实现
                    pass
                result["message"] += f"，造成 {card.attack} 点伤害并冻结所有敌人"
                logger.info(f"  ❄️ {result['message']}")
            elif "return" in card.mechanics:
                # 返回手牌法术 - 选择一个友方随从返回手牌
                if player.field:
                    # 简化实现：返回第一个随从到手牌
                    returned_minion = player.field.pop(0)
                    player.hand.append(returned_minion)
                    result["message"] += f"，将 {get_card_name(returned_minion)} 返回手牌"
                    logger.info(f"  🌙 {result['message']}")
                else:
                    result["message"] += "，但没有随从可以返回"
                    logger.info(f"  🌙 {result['message']}")
            elif card.attack > 0:
                # 伤害法术
                opponent.health -= card.attack
                result["message"] += f"，造成 {card.attack} 点伤害"
                logger.info(f"  🔥 {result['message']}")
            elif card.attack < 0:
                # 治疗法术
                player.health = min(player.max_health, player.health - card.attack)
                result["message"] += f"，恢复 {-card.attack} 点生命"
                logger.info(f"  💚 {result['message']}")

        # 检查游戏结束
        self._check_game_over()

        return result

    def _combat_phase(self):
        """战斗阶段"""
        current = self.get_current_player()
        opponent = self.get_opponent()

        # 如果对手没有随从，直接攻击英雄
        if not opponent.field and current.field:
            for minion in current.field:
                opponent.health -= minion.attack
                # 兼容不同的卡牌数据格式
                minion_name = get_card_name(minion)
                logger.info(f"  ⚔️ {minion_name} 攻击英雄，造成 {minion.attack} 点伤害")

        # 随从对战
        elif current.field and opponent.field:
            # 简化：随机选择一个随从进行攻击
            attacker = random.choice(current.field)

            # 优先攻击没有嘲讽的随从
            non_taunt_targets = [m for m in opponent.field if "taunt" not in m.mechanics]
            if non_taunt_targets:
                defender = random.choice(non_taunt_targets)
            else:
                defender = random.choice(opponent.field)

            # 执行攻击 - 处理神圣护盾
            damage_dealt = attacker.attack
            if "divine_shield" in getattr(defender, 'mechanics', []):
                # 神圣护盾免疫首次伤害
                damage_dealt = 0
                # 移除神圣护盾
                if hasattr(defender, 'mechanics'):
                    defender.mechanics.remove("divine_shield")
                logger.info(f"  ✨ {get_card_name(defender)} 的神圣护盾被击破")

            defender.health -= damage_dealt
            # 兼容不同的卡牌数据格式
            attacker_name = get_card_name(attacker)
            defender_name = get_card_name(defender)
            logger.info(f"  ⚔️ {attacker_name} vs {defender_name} ({damage_dealt} damage)")

            # 移除死亡的随从
            if defender.health <= 0:
                opponent.field.remove(defender)
                logger.info(f"  💀 {defender_name} 被击败")

    def _check_game_over(self):
        """检查游戏是否结束"""
        for i, player in enumerate(self.players):
            if player.health <= 0:
                self.game_over = True
                self.winner = self.players[1 - i].name
                logger.info(f"🏁 游戏结束! {self.winner} 获胜!")
                return True

        # 检查平局（超过30回合）
        if self.turn_number > 30:
            self.game_over = True
            p1, p2 = self.players
            if p1.health > p2.health:
                self.winner = p1.name
            elif p2.health > p1.health:
                self.winner = p2.name
            else:
                self.winner = "平局"
            logger.info(f"🏁 游戏结束! {self.winner}")
            return True

        return False

    def get_game_state(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        current = self.get_current_player()
        opponent = self.get_opponent()

        return {
            "turn_number": self.turn_number,
            "current_player": current.name,
            "game_over": self.game_over,
            "winner": self.winner,
            "current_player_state": {
                "name": current.name,
                "health": current.health,
                "max_health": current.max_health,
                "mana": current.mana,
                "max_mana": current.max_mana,
                "hand_count": len(current.hand),
                "field_count": len(current.field),
                "hand": [
                    {
                        "index": i,
                        "name": get_card_name(card),
                        "cost": card.cost,
                        "attack": card.attack,
                        "health": card.health,
                        "type": card.card_type,
                        "description": card.description,
                        "mechanics": card.mechanics,
                        "playable": current.can_play_card(card)
                    } for i, card in enumerate(current.hand)
                ],
                "field": [
                    {
                        "name": get_card_name(card),
                        "attack": card.attack,
                        "health": card.health,
                        "mechanics": card.mechanics
                    } for card in current.field
                ]
            },
            "opponent_state": {
                "name": opponent.name,
                "health": opponent.health,
                "max_health": opponent.max_health,
                "mana": opponent.mana,
                "max_mana": opponent.max_mana,
                "hand_count": len(opponent.hand),
                "field_count": len(opponent.field),
                "field": [
                    {
                        "name": get_card_name(card),
                        "attack": get_card_attack(card),
                        "health": get_card_health(card),
                        "mechanics": safe_get_card_attr(card, 'mechanics', [])
                    } for card in opponent.field
                ]
            }
        }

    def display_status(self, use_rich=True):
        """显示游戏状态"""
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.progress import Progress, BarColumn, TextColumn
        from rich.layout import Layout
        import time

        if use_rich:
            console = Console()
            state = self.get_game_state()
            current = state["current_player_state"]
            opponent = state["opponent_state"]

            # 创建主布局
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="main"),
                Layout(name="footer", size=4)  # 增加footer高度
            )

            # 标题区域
            header_content = f"[bold cyan]🎮 第 {state['turn_number']} 回合 - {current['name']} 的回合[/bold cyan]"
            layout["header"].update(Panel(header_content, style="bold blue"))

            # 主区域
            layout["main"].split_row(
                Layout(name="player_info", ratio=1),
                Layout(name="game_area", ratio=2),
                Layout(name="opponent_info", ratio=1)
            )

            # 玩家信息
            player_table = Table(title="👤 玩家状态", show_header=False)
            player_table.add_column("属性", style="cyan")
            player_table.add_column("数值", style="green")
            player_table.add_row("❤️ 生命值", f"{current['health']}/{current['max_health']}")
            player_table.add_row("💰 法力值", f"{current['mana']}/{current['max_mana']}")
            player_table.add_row("🃋 手牌", f"{current['hand_count']} 张")
            player_table.add_row("⚔️ 随从", f"{current['field_count']} 个")
            layout["player_info"].update(Panel(player_table, border_style="green"))

            # 游戏区域 - 创建手牌、我方场地区域和对手场地区域的布局
            game_layout = Layout()
            game_layout.split_column(
                Layout(name="hand_area", ratio=1),
                Layout(name="field_section", ratio=1)
            )

            # 场地区域再分为我方和对手
            game_layout["field_section"].split_row(
                Layout(name="player_field", ratio=1),
                Layout(name="opponent_field", ratio=1)
            )

            # 手牌显示 - 使用动态宽度
            if current["hand"]:
                # 获取终端宽度并计算列宽
                terminal_width = get_terminal_width()

                # 最终优化列结构
                min_widths = {
                    "index": 3,    # 编号 - 最简化
                    "name": 12,    # 卡牌名称 - 平衡长度
                    "cost": 2,     # 费用 - 最简化
                    "stats": 6,    # 属性 - 确保emoji可见
                    "playable": 3  # 状态 - 最简化
                }
                total_min_width = sum(min_widths.values())

                # 计算实际列宽
                col_widths = calculate_table_widths(terminal_width, min_widths, total_min_width)

                hand_table = Table(title="🃏 你的手牌", show_header=True)
                hand_table.add_column("#", style="yellow", justify="right")
                hand_table.add_column("卡牌", style="bold white", justify="left")
                hand_table.add_column("费", style="blue", justify="center")
                hand_table.add_column("属性", style="red", justify="center")
                hand_table.add_column("状态", style="green", justify="center")

                for card in current["hand"]:
                    # 简化状态显示
                    status = "✅" if card["playable"] else "❌"

                    # 卡牌类型和机制简短显示
                    card_type = card.get('type', '')
                    type_symbol = "⚔️" if card_type == "minion" else "🔮"  # 随从/法术符号

                    # 显示攻击力和血量（随从牌）或效果值（法术牌）
                    if card_type == "minion":
                        stats = f"[red]{card['attack']}[/red]/[green]{card['health']}[/green]"
                    elif card_type == "spell":
                        if card['attack'] > 0:
                            stats = f"[red]🔥{card['attack']}[/red]"  # 伤害法术
                        elif card['attack'] < 0:
                            stats = f"[green]💚{-card['attack']}[/green]"  # 治疗法术
                        else:
                            stats = "[blue]✨[/blue]"  # 其他法术
                    else:
                        stats = ""

                    # 卡牌名称（包含类型符号）
                    card_name_with_type = f"{type_symbol} {card['name']}"

                    hand_table.add_row(
                        f"[yellow]{card['index']}[/yellow]",
                        f"[bold]{card_name_with_type}[/bold]",
                        f"[blue]{card['cost']}[/blue]",
                        stats,  # emoji属性显示
                        f"[green]{status}[/green]"
                    )

                game_layout["hand_area"].update(Panel(hand_table, border_style="cyan"))
            else:
                game_layout["hand_area"].update(Panel("[dim]手牌为空[/dim]", border_style="dim"))

            # 我方场上随从显示 - 使用动态宽度
            if current["field"]:
                # 复用已获取的终端宽度
                if 'terminal_width' not in locals():
                    terminal_width = get_terminal_width()

                # 随从表格的最小列宽
                field_min_widths = {
                    "index": 6,      # 编号 - 增加宽度确保数字可见
                    "name": 10,      # 随从名称
                    "stats": 6,      # 属性
                    "status": 8,     # 状态
                    "effects": 8     # 特效
                }
                field_total_min = sum(field_min_widths.values())

                # 计算随从表格的实际列宽
                field_col_widths = calculate_table_widths(terminal_width, field_min_widths, field_total_min)

                player_field_table = Table(title="⚔️ 你的随从", show_header=True)
                player_field_table.add_column("编号", style="yellow", width=field_col_widths["index"], justify="right")
                player_field_table.add_column("随从", style="bold white", width=field_col_widths["name"], justify="left")
                player_field_table.add_column("属性", style="red", width=field_col_widths["stats"], justify="center")
                player_field_table.add_column("状态", style="green", width=field_col_widths["status"], justify="center")
                player_field_table.add_column("特效", style="blue", width=field_col_widths["effects"], justify="center")

                for i, card in enumerate(current["field"]):
                    # 确保随从有正确的攻击状态
                    ensure_minion_attack_state(card)

                    # 攻击状态
                    can_attack = get_minion_can_attack(card, False)
                    attack_status = "[green]⚔️可攻击[/green]" if can_attack else "[red]😴休眠[/red]"

                    # 特效标记
                    mechanics_map = {
                        "taunt": "🛡️嘲讽",
                        "divine_shield": "✨圣盾",
                        "stealth": "🌑潜行",
                        "ranged": "🏹远程",
                        "spell_power": "🔥法强"
                    }
                    mechanics_display = " ".join([mechanics_map.get(m, m) for m in card.get('mechanics', [])])

                    # 使用智能截断确保内容不会超出列宽
                    minion_name_display = truncate_text(get_card_name(card), field_col_widths["name"] - 2)
                    mechanics_display_truncated = truncate_text(mechanics_display or "无", field_col_widths["effects"])

                    player_field_table.add_row(
                        f"[yellow]{i}[/yellow]",
                        f"[bold]{minion_name_display}[/bold]",
                        f"[red]{get_card_attack(card)}[/red]/[green]{get_card_health(card)}[/green]",
                        attack_status,
                        f"[blue]{mechanics_display_truncated}[/blue]" if mechanics_display else "[dim]无[/dim]"
                    )

                game_layout["player_field"].update(Panel(player_field_table, border_style="green"))
            else:
                game_layout["player_field"].update(Panel("[dim]场上没有随从[/dim]", border_style="dim"))

            # 对手场上随从显示 - 使用动态宽度
            if opponent["field"]:
                # 复用已获取的终端宽度和列宽配置
                if 'terminal_width' not in locals():
                    terminal_width = get_terminal_width()
                field_min_widths = {
                    "index": 6, "name": 10, "stats": 6, "status": 8, "effects": 8
                }
                field_total_min = sum(field_min_widths.values())
                field_col_widths = calculate_table_widths(terminal_width, field_min_widths, field_total_min)

                opponent_field_table = Table(title="🤖 对手随从", show_header=True)
                opponent_field_table.add_column("编号", style="yellow", width=field_col_widths["index"], justify="right")
                opponent_field_table.add_column("随从", style="bold white", width=field_col_widths["name"], justify="left")
                opponent_field_table.add_column("属性", style="red", width=field_col_widths["stats"], justify="center")
                opponent_field_table.add_column("状态", style="red", width=field_col_widths["status"], justify="center")
                opponent_field_table.add_column("特效", style="blue", width=field_col_widths["effects"], justify="center")

                for i, card in enumerate(opponent["field"]):
                    # 对手随从状态 - 简化显示，只显示是否可攻击（潜行等特殊状态）
                    can_attack = get_minion_can_attack(card, False)
                    attack_status = "[red]⚔️可攻击[/red]" if can_attack else "[dim]😴休眠[/dim]"

                    # 特效标记
                    mechanics_map = {
                        "taunt": "🛡️嘲讽",
                        "divine_shield": "✨圣盾",
                        "stealth": "🌑潜行",
                        "ranged": "🏹远程",
                        "spell_power": "🔥法强"
                    }
                    mechanics_display = " ".join([mechanics_map.get(m, m) for m in card.get('mechanics', [])])

                    # 使用智能截断确保内容不会超出列宽
                    minion_name_display = truncate_text(get_card_name(card), field_col_widths["name"] - 2)
                    mechanics_display_truncated = truncate_text(mechanics_display or "无", field_col_widths["effects"])

                    opponent_field_table.add_row(
                        f"[yellow]{i}[/yellow]",
                        f"[bold]{minion_name_display}[/bold]",
                        f"[red]{get_card_attack(card)}[/red]/[green]{get_card_health(card)}[/green]",
                        attack_status,
                        f"[blue]{mechanics_display_truncated}[/blue]" if mechanics_display else "[dim]无[/dim]"
                    )

                game_layout["opponent_field"].update(Panel(opponent_field_table, border_style="red"))
            else:
                game_layout["opponent_field"].update(Panel("[dim]对手没有随从[/dim]", border_style="dim"))

            layout["game_area"].update(Panel(game_layout, border_style="blue"))

            # 对手信息
            opponent_table = Table(title="🤖 对手状态", show_header=False)
            opponent_table.add_column("属性", style="red")
            opponent_table.add_column("数值", style="yellow")
            opponent_table.add_row("❤️ 生命值", f"{opponent['health']}/{opponent['max_health']}")
            opponent_table.add_row("💰 法力值", f"{opponent['mana']}/{opponent['max_mana']}")
            opponent_table.add_row("🃋 手牌", f"{opponent['hand_count']} 张")
            opponent_table.add_row("⚔️ 随从", f"{opponent['field_count']} 个")
            layout["opponent_info"].update(Panel(opponent_table, border_style="red"))

            # 底部 - 带智能截断检测的操作提示
            hints = self.get_simple_input_hints()

            # 检测提示是否被截断
            try:
                import shutil
                terminal_width = shutil.get_terminal_size().columns
                # 如果提示文本接近终端宽度，添加省略号提示
                if len(hints) > terminal_width - 8:
                    hint_text = f"[green]{hints}[/green] [dim](输入 'h' 查看完整帮助)[/dim]"
                else:
                    hint_text = f"[green]{hints}[/green]"
            except:
                hint_text = f"[green]{hints}[/green]"

            # 使用更紧凑的Panel配置，减少边距
            footer_panel = Panel(
                hint_text,
                style="dim green",
                padding=(0, 1),  # 上下0，左右1的边距
                border_style="dim"
            )
            layout["footer"].update(footer_panel)

            # 显示界面
            console.clear()
            console.print(layout)

        else:
            # 原始文本模式
            state = self.get_game_state()
            current = state["current_player_state"]
            opponent = state["opponent_state"]

            print(f"\n🎮 第 {state['turn_number']} 回合 - {current['name']} 的回合")
            print(f"💰 法力值: {current['mana']}/{current['max_mana']}")
            print(f"❤️ 生命值: 你 {current['health']}/{current['max_health']} vs 对手 {opponent['health']}/{opponent['max_health']}")
            print(f"👥 场面随从: 你 {current['field_count']} vs 对手 {opponent['field_count']}")
            print(f"🃋 手牌数量: 你 {current['hand_count']} vs 对手 {opponent['hand_count']}")

            if current["hand"]:
                print(f"\n🃏 你的手牌:")
                for card in current["hand"]:
                    status = "✅ 可出" if card["playable"] else "❌ 法力不足"
                    mechanics_str = f" [{', '.join(card.get('mechanics', []))}]" if card.get('mechanics') else ""
                    type_map = {"minion": "随从", "spell": "法术"}
                    card_type = card.get('type', '')
                    card_type_cn = type_map.get(card_type, card_type)

                    # 显示攻击力和血量（随从牌）或效果值（法术牌）
                    if card_type == "minion":
                        stats = f"({card['attack']}/{card['health']})"
                    elif card_type == "spell":
                        if card['attack'] > 0:
                            stats = f"(🔥{card['attack']}伤害)"  # 伤害法术
                        elif card['attack'] < 0:
                            stats = f"(💚{-card['attack']}治疗)"  # 治疗法术
                        else:
                            stats = "(✨特殊)"  # 其他法术
                    else:
                        stats = ""

                    print(f"  {card['index']}. {card['name']} {stats} ({card['cost']}费) - {card_type_cn}{mechanics_str}")
                    print(f"     {card['description']} {status}")

            # 显示场上随从
            if current["field"]:
                print(f"\n⚔️ 你的随从:")
                for i, card in enumerate(current["field"]):
                    # 确保随从有正确的攻击状态
                    ensure_minion_attack_state(card)

                    can_attack = get_minion_can_attack(card, False)
                    attack_status = "⚔️可攻击" if can_attack else "😴休眠"

                    mechanics_map = {
                        "taunt": "🛡️嘲讽",
                        "divine_shield": "✨圣盾",
                        "stealth": "🌑潜行",
                        "ranged": "🏹远程",
                        "spell_power": "🔥法强"
                    }
                    mechanics_display = " ".join([mechanics_map.get(m, m) for m in card.get('mechanics', [])])

                    print(f"  {i}. {get_card_name(card)} ({card.attack}/{card.health}) - {attack_status}")
                    if mechanics_display:
                        print(f"     特效: {mechanics_display}")

            # 显示对手场上随从
            if opponent["field"]:
                print(f"\n🤖 对手随从:")
                for i, card in enumerate(opponent["field"]):
                    mechanics_map = {
                        "taunt": "🛡️嘲讽",
                        "divine_shield": "✨圣盾",
                        "stealth": "🌑潜行",
                        "ranged": "🏹远程",
                        "spell_power": "🔥法强"
                    }
                    mechanics_display = " ".join([mechanics_map.get(m, m) for m in card.get('mechanics', [])])

                    print(f"  {i}. {get_card_name(card)} ({card.attack}/{card.health})")
                    if mechanics_display:
                        print(f"     特效: {mechanics_display}")

    def get_available_commands(self) -> List[str]:
        """获取可用命令"""
        if self.game_over:
            return ["退出", "重新开始"]

        current = self.get_current_player()
        commands = ["帮助", "状态", "退出"]

        # 检查可出的牌 - 简化为数字提示
        playable_cards = [i for i, card in enumerate(current.hand) if current.can_play_card(card)]
        if playable_cards:
            commands.append("直接输入数字出牌")

        # 检查场上随从是否可以攻击
        attackable_minions = [i for i, minion in enumerate(current.field)
                            if get_minion_can_attack(minion, False)]
        if attackable_minions:
            commands.append("随从攻击 <编号> <目标>")

        # 检查英雄是否可以攻击
        opponent = self.get_opponent()
        if (not opponent.field or # 对手没有随从时可以攻击英雄
            any("taunt" not in minion.mechanics for minion in opponent.field)):
            commands.append("英雄攻击")

        # 检查英雄技能
        if current.mana >= 2:
            commands.append("英雄技能 (技)")

        # 检查场上随从的特殊能力
        for i, minion in enumerate(current.field):
            if "spell_power" in minion.mechanics:
                commands.append("释放法术 <编号>")
            if "stealth" in minion.mechanics:
                commands.append("解除潜行 <编号>")

        commands.append("结束回合 (回车/空格)")

        return commands

    def get_simple_input_hints(self) -> str:
        """获取简单的输入提示 - 带终端宽度检测和文本截断保护"""
        if self.game_over:
            return "退出: q | 重新: r"

        try:
            # 尝试获取终端宽度
            import shutil
            terminal_width = shutil.get_terminal_size().columns
        except:
            # 如果获取失败，使用默认宽度
            terminal_width = 80

        current = self.get_current_player()
        hints = []

        # 可出的牌 - 根据终端宽度动态调整
        playable_cards = [i for i, card in enumerate(current.hand) if current.can_play_card(card)]
        if playable_cards:
            # 只显示数量和第一个编号，节省空间
            if len(playable_cards) == 1:
                hints.append(f"出牌: {playable_cards[0]}")
            else:
                hints.append(f"出牌: {playable_cards[0]}等{len(playable_cards)}张")

        # 检查场上随从是否可以攻击
        attackable_minions = [i for i, minion in enumerate(current.field)
                            if get_minion_can_attack(minion, False)]
        if attackable_minions:
            # 添加随从攻击提示
            if len(attackable_minions) == 1:
                hints.append(f"攻击: {attackable_minions[0]}")
            else:
                hints.append(f"攻击: {attackable_minions[0]}等{len(attackable_minions)}个")

        # 英雄技能 - 简化
        if current.mana >= 2:
            hints.append("技能: s")

        # 最核心的快捷操作 - 使用简写
        hints.extend(["结束: Enter", "帮助: h"])

        # 组合提示文本
        full_hint = " | ".join(hints)

        # 如果终端太窄，进一步简化
        if terminal_width < 70:
            # 超紧凑模式 - 确保攻击提示也显示
            short_hints = []

            # 优先显示可出牌
            if playable_cards:
                short_hints.append(f"出:{playable_cards[0]}")

            # 添加攻击提示（这是关键修复！）
            attackable_minions = [i for i, minion in enumerate(current.field)
                                if get_minion_can_attack(minion, False)]
            if attackable_minions:
                if len(attackable_minions) == 1:
                    short_hints.append(f"攻:{attackable_minions[0]}")
                else:
                    short_hints.append(f"攻:{attackable_minions[0]}等")

            # 添加技能提示
            if current.mana >= 2:
                short_hints.append("技:s")

            short_hints.extend(["结束:Enter", "帮助:h"])
            full_hint = " | ".join(short_hints)
        elif terminal_width < 90:
            # 紧凑模式 - 确保攻击提示也显示
            compact_hints = []

            # 优先显示可出牌
            if playable_cards:
                compact_hints.append(f"出牌 {playable_cards[0]}")
                if len(playable_cards) > 1:
                    compact_hints[0] += f"等{len(playable_cards)}张"

            # 添加攻击提示（这是关键修复！）
            attackable_minions = [i for i, minion in enumerate(current.field)
                                if get_minion_can_attack(minion, False)]
            if attackable_minions:
                if len(attackable_minions) == 1:
                    compact_hints.append(f"攻击 {attackable_minions[0]}")
                else:
                    compact_hints.append(f"攻击 {attackable_minions[0]}等{len(attackable_minions)}个")

            # 添加技能提示
            if current.mana >= 2:
                compact_hints.append("技能 s")

            compact_hints.extend(["结束 Enter", "帮助 h"])
            full_hint = " | ".join(compact_hints)

        # 最终截断保护 - 确保不会超出终端宽度
        if len(full_hint) > terminal_width - 4:  # 留4个字符的边距
            full_hint = full_hint[:terminal_width-7] + "..."

        return full_hint

    def get_context_help(self) -> str:
        """获取上下文相关的帮助信息"""
        current = self.get_current_player()

        # 基础帮助
        help_lines = [
            "🎮 [bold cyan]游戏帮助[/bold cyan]",
            "",
        ]

        # 根据当前游戏状态添加相应帮助
        playable_cards = [i for i, card in enumerate(current.hand) if current.can_play_card(card)]
        attackable_minions = [i for i, minion in enumerate(current.field)
                            if get_minion_can_attack(minion, False)]

        # 出牌帮助
        if playable_cards:
            help_lines.append(f"🃏 [yellow]可出牌: {', '.join(map(str, playable_cards))}[/yellow]")
            help_lines.append("   直接输入数字出牌 (如: 0, 1, 2)")
        else:
            help_lines.append("🃏 [dim]当前无可出牌 (法力不足)[/dim]")

        # 技能帮助
        if current.mana >= 2:
            help_lines.append("⚡ [yellow]英雄技能可用 (2费)[/yellow]")
            help_lines.append("   输入 '技' 或 '技能' 使用")
        else:
            help_lines.append("⚡ [dim]英雄技能需要2点法力[/dim]")

        # 攻击帮助
        if attackable_minions:
            help_lines.append(f"⚔️ [yellow]可攻击随从: {', '.join(map(str, attackable_minions))}[/yellow]")
            help_lines.append("   输入 '随从攻击 <编号> <目标>' 手动攻击")
        else:
            help_lines.append("⚔️ [dim]无可攻击随从[/dim]")

        # 基础操作
        help_lines.extend([
            "",
            "🎯 [bold]基础操作:[/bold]",
            "• [yellow]回车/空格[/yellow] 结束回合 (自动攻击)",
            "• [yellow]状态[/yellow] 查看详细游戏状态",
            "• [yellow]退出[/yellow] 退出游戏",
            "",
            "💡 [dim]提示: 随从会自动攻击最优目标[/dim]",
            "💡 [dim]更多帮助: 项目文档[/dim]",
        ])

        return "\n".join(help_lines)

    def get_minion_attack_targets(self, player_idx: int, minion_idx: int) -> List[str]:
        """获取随从可攻击的目标"""
        if player_idx >= len(self.players) or minion_idx >= len(self.players[player_idx].field):
            return []

        current_player = self.players[player_idx]
        opponent = self.players[1 - player_idx]
        minion = current_player.field[minion_idx]

        # 检查随从是否可以攻击
        if not get_minion_can_attack(minion, False):
            return []

        targets = []

        # 如果对手有随从，优先攻击嘲讽随从
        taunt_minions = [f"随从_{i}" for i, m in enumerate(opponent.field) if "taunt" in m.mechanics]
        if taunt_minions:
            targets.extend(taunt_minions)
        else:
            # 可以攻击所有随从
            for i in range(len(opponent.field)):
                targets.append(f"随从_{i}")

            # 如果没有随从或有非嘲讽随从，可以攻击英雄
            if not opponent.field or any("taunt" not in m.mechanics for m in opponent.field):
                targets.append("英雄")

        return targets

    def attack_with_minion(self, player_idx: int, minion_idx: int, target: str) -> Dict[str, Any]:
        """随从攻击"""
        if player_idx != self.current_player_idx:
            return {"success": False, "message": "不是你的回合"}

        current = self.players[player_idx]
        opponent = self.players[1 - player_idx]

        if minion_idx >= len(current.field):
            return {"success": False, "message": "无效的随从编号"}

        minion = current.field[minion_idx]

        # 检查随从是否可以攻击
        if not get_minion_can_attack(minion, False):
            return {"success": False, "message": "该随从本回合无法攻击"}

        # 解析攻击目标
        if target == "英雄":
            # 攻击英雄
            opponent.health -= minion.attack
            result_message = f"{minion.name} 攻击英雄，造成 {minion.attack} 点伤害"

            # 标记随从已攻击
            minion.can_attack = False

            logger.info(f"  ⚔️ {result_message}")

        elif target.startswith("随从_"):
            try:
                target_idx = int(target.split("_")[1])
                if target_idx >= len(opponent.field):
                    return {"success": False, "message": "无效的目标编号"}

                target_minion = opponent.field[target_idx]

                # 检查是否必须攻击嘲讽
                taunt_minions = [m for m in opponent.field if "taunt" in m.mechanics]
                if taunt_minions and target_minion not in taunt_minions:
                    return {"success": False, "message": "必须先攻击嘲讽随从"}

                # 执行战斗 - 处理神圣护盾
                damage_dealt = minion.attack
                shield_broken = False

                # 检查目标是否有神圣护盾
                if "divine_shield" in getattr(target_minion, 'mechanics', []):
                    # 神圣护盾免疫首次伤害
                    damage_dealt = 0
                    # 移除神圣护盾
                    if hasattr(target_minion, 'mechanics'):
                        target_minion.mechanics.remove("divine_shield")
                    shield_broken = True
                    logger.info(f"  ✨ {target_minion.name} 的神圣护盾被击破")

                # 应用伤害
                if damage_dealt > 0:
                    target_minion.health -= damage_dealt

                # 反击（除非潜行）
                if "stealth" not in getattr(minion, 'mechanics', []):
                    minion.health -= target_minion.attack

                result_message = f"{minion.name} vs {target_minion.name}"

                # 标记随从已攻击
                minion.can_attack = False

                # 移除死亡的随从
                if target_minion.health <= 0:
                    opponent.field.remove(target_minion)
                    result_message += f"，{target_minion.name} 被击败"

                if minion.health <= 0:
                    current.field.remove(minion)
                    result_message += f"，{minion.name} 被击败"

                logger.info(f"  ⚔️ {result_message}")

            except (IndexError, ValueError):
                return {"success": False, "message": "目标格式错误"}
        else:
            return {"success": False, "message": "无效的攻击目标"}

        # 检查游戏结束
        self._check_game_over()

        # 构建详细的返回结果
        result = {
            "success": True,
            "message": result_message,
            "attacker_name": get_card_name(minion),
            "damage": minion.attack,
            "target_destroyed": False
        }

        # 根据攻击目标类型添加目标信息
        if target == "英雄":
            result["target_name"] = "敌方英雄"
            result["damage"] = minion.attack
        else:
            # 随从对战
            result["target_name"] = get_card_name(target_minion) if 'target_minion' in locals() else "敌方随从"
            result["damage"] = damage_dealt if 'damage_dealt' in locals() else minion.attack
            result["target_destroyed"] = target_minion.health <= 0 if 'target_minion' in locals() else False

        return result

    def attack_with_hero(self, player_idx: int) -> Dict[str, Any]:
        """英雄攻击"""
        if player_idx != self.current_player_idx:
            return {"success": False, "message": "不是你的回合"}

        current = self.players[player_idx]
        opponent = self.players[1 - player_idx]

        # 检查是否有武器（简化版：英雄可以攻击）
        hero_attack = 1  # 简化：英雄固定攻击力为1

        # 检查是否可以攻击英雄
        if opponent.field:
            taunt_minions = [m for m in opponent.field if "taunt" in m.mechanics]
            if taunt_minions:
                return {"success": False, "message": "必须先攻击嘲讽随从"}

        # 执行攻击
        opponent.health -= hero_attack
        result_message = f"英雄攻击，造成 {hero_attack} 点伤害"

        logger.info(f"  ⚔️ {result_message}")

        # 检查游戏结束
        self._check_game_over()

        return {
            "success": True,
            "message": result_message
        }