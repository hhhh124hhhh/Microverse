"""
Card Battle Arena Enhanced - 卡牌游戏核心引擎
提供完整的游戏状态管理和回合制流程控制
"""
import random
import asyncio
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


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

    def draw_card(self, card: Card):
        """抽牌"""
        if len(self.hand) < 10:
            self.hand.append(card)
            self.deck_size = max(0, self.deck_size - 1)
            return True
        return False


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
        """创建卡牌池"""
        return [
            Card("烈焰元素", 3, 5, 3, "minion", [], "💥 火焰元素的愤怒，燃烧一切敌人"),
            Card("霜狼步兵", 2, 2, 3, "minion", ["taunt"], "🛡️ 诺森德的精锐步兵，身披重甲守护前线"),
            Card("铁喙猫头鹰", 3, 2, 2, "minion", ["taunt"], "🦉 夜空中的猎手，锐利的铁喙撕裂敌人"),
            Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客，悄无声息地接近目标"),
            Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者，神圣护盾保护其免受首次伤害"),
            Card("火球术", 4, 6, 0, "spell", [], "🔥 法师经典法术，召唤炽热火球轰击敌人"),
            Card("闪电箭", 1, 3, 0, "spell", [], "⚡ 萨满祭司的呼唤，天雷惩罚敌人"),
            Card("治愈术", 2, -5, 0, "spell", [], "💚 圣光之力，恢复5点生命值"),
            Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火，对敌人造成3点伤害"),
            Card("奥术智慧", 3, 0, 0, "spell", ["draw_cards"], "📚 深奥的魔法知识，从虚空中抽取两张卡牌"),
            Card("寒冰箭", 2, 3, 0, "spell", ["freeze"], "❄️ 极寒之冰，冻结敌人并造成3点伤害"),
            Card("铁炉堡火枪手", 2, 2, 2, "minion", ["ranged"], "🔫 矮人神射手，远程精准打击敌人"),
            Card("暴风雪骑士", 6, 6, 5, "minion", ["taunt", "divine_shield"], "🌨️ 暴风城的精英骑士，身披圣铠手持坚盾"),
            Card("暗影步", 1, 0, 0, "spell", ["return"], "🌑 影子魔法，将一个随从返回手中重新部署"),
            Card("炎爆术", 8, 10, 0, "spell", [], "🌋 毁灭性的火焰魔法，造成10点巨额伤害"),
            Card("冰霜新星", 3, 2, 0, "spell", ["freeze"], "❄️ 冰系范围法术，冻结所有敌人"),
            Card("神圣惩击", 4, 5, 0, "spell", [], "✨ 圣光审判，对邪恶敌人造成5点伤害"),
            Card("铁炉堡士兵", 2, 1, 4, "minion", ["taunt"], "⚔️ 铁炉堡的忠诚士兵，誓死守护阵地"),
            Card("暗影巫师", 3, 2, 3, "minion", ["spell_power"], "🧙‍♂️ 掌控暗影力量的神秘巫师"),
            Card("治疗之环", 1, -2, 0, "spell", [], "💫 温和的治疗法术，恢复2点生命值"),
        ]

    def _initial_draw(self):
        """初始抽牌"""
        for player in self.players:
            for _ in range(3):
                if player.deck_size > 0:
                    card = random.choice(self.card_pool)
                    player.draw_card(card)

    def get_current_player(self) -> Player:
        """获取当前玩家"""
        return self.players[self.current_player_idx]

    def get_opponent(self) -> Player:
        """获取对手"""
        return self.players[1 - self.current_player_idx]

    def start_turn(self):
        """开始新的回合"""
        current = self.get_current_player()
        current.start_turn()

        # 激活场上随从的攻击状态
        for minion in current.field:
            minion.can_attack = True

        # 抽一张牌
        if current.deck_size > 0:
            card = random.choice(self.card_pool)
            if current.draw_card(card):
                logger.info(f"🃏 {current.name} 抽取了 {get_card_name(card)}")

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
                for _ in range(2):
                    if opponent.deck_size > 0:
                        draw_card = random.choice(self.card_pool)
                        opponent.draw_card(draw_card)
                result["message"] += "，抽了2张牌"
                logger.info(f"  📚 {result['message']}")
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

        # 为新上场的随从设置攻击状态
        for minion in current.field:
            if not hasattr(minion, 'can_attack'):
                minion.can_attack = True
            elif minion.can_attack is None:
                minion.can_attack = True

        # 获取可攻击的随从
        attackable_minions = [i for i, minion in enumerate(current.field)
                            if getattr(minion, 'can_attack', False)]

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
                        # 执行攻击
                        target.health = get_card_health(target) - get_card_attack(minion)
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
                if not getattr(minion, 'can_attack', False):
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
                            target_minion.health -= minion.attack
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
                for _ in range(2):
                    if opponent.deck_size > 0:
                        draw_card = random.choice(self.card_pool)
                        opponent.draw_card(draw_card)
                result["message"] += "，抽了2张牌"
                logger.info(f"  📚 {result['message']}")
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

            # 执行攻击
            defender.health -= attacker.attack
            # 兼容不同的卡牌数据格式
            attacker_name = get_card_name(attacker)
            defender_name = get_card_name(defender)
            logger.info(f"  ⚔️ {attacker_name} vs {defender_name} ({attacker.attack} damage)")

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
                        "attack": card.attack,
                        "health": card.health,
                        "mechanics": card.mechanics
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

            # 游戏区域 - 创建手牌和场地区域的布局
            game_layout = Layout()
            game_layout.split_column(
                Layout(name="hand_area", ratio=1),
                Layout(name="field_area", ratio=1)
            )

            # 手牌显示
            if current["hand"]:
                hand_table = Table(title="🃏 你的手牌", show_header=True)
                hand_table.add_column("编号", style="yellow", width=4)
                hand_table.add_column("卡牌", style="bold white", width=16)
                hand_table.add_column("费用", style="blue", width=4)
                hand_table.add_column("属性", style="red", width=8)
                hand_table.add_column("类型", style="magenta", width=8)
                hand_table.add_column("状态", style="green", width=8)

                for card in current["hand"]:
                    status = "[green]✅ 可出[/green]" if card["playable"] else "[red]❌ 法力不足[/red]"
                    mechanics_str = f" [{', '.join(card.get('mechanics', []))}]" if card.get('mechanics') else ""

                    # 卡牌类型中文映射
                    type_map = {"minion": "随从", "spell": "法术"}
                    card_type_cn = type_map.get(card['type'], card['type'])

                    # 显示攻击力和血量（随从牌）或效果值（法术牌）
                    if card['type'] == "minion":
                        stats = f"[red]{card['attack']}[/red]/[green]{card['health']}[/green]"
                    elif card['type'] == "spell":
                        if card['attack'] > 0:
                            stats = f"[red]🔥{card['attack']}[/red]"  # 伤害法术
                        elif card['attack'] < 0:
                            stats = f"[green]💚{-card['attack']}[/green]"  # 治疗法术
                        else:
                            stats = "[blue]✨[/blue]"  # 其他法术
                    else:
                        stats = ""

                    hand_table.add_row(
                        f"[yellow]{card['index']}[/yellow]",
                        f"[bold]{card['name']}[/bold]",
                        f"[blue]{card['cost']}[/blue]",
                        stats,
                        f"[magenta]{card_type_cn}[/magenta]{mechanics_str}",
                        status
                    )

                game_layout["hand_area"].update(Panel(hand_table, border_style="cyan"))
            else:
                game_layout["hand_area"].update(Panel("[dim]手牌为空[/dim]", border_style="dim"))

            # 场上随从显示
            if current["field"]:
                field_table = Table(title="⚔️ 你的随从", show_header=True)
                field_table.add_column("编号", style="yellow", width=4)
                field_table.add_column("随从", style="bold white", width=16)
                field_table.add_column("属性", style="red", width=8)
                field_table.add_column("状态", style="green", width=10)
                field_table.add_column("特效", style="blue", width=12)

                for i, card in enumerate(current["field"]):
                    # 攻击状态
                    can_attack = getattr(card, 'can_attack', False)
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

                    field_table.add_row(
                        f"[yellow]{i}[/yellow]",
                        f"[bold]{get_card_name(card)}[/bold]",
                        f"[red]{card.attack}[/red]/[green]{card.health}[/green]",
                        attack_status,
                        mechanics_display or "[dim]无[/dim]"
                    )

                game_layout["field_area"].update(Panel(field_table, border_style="green"))
            else:
                game_layout["field_area"].update(Panel("[dim]场上没有随从[/dim]", border_style="dim"))

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
                    card_type_cn = type_map.get(card['type'], card['type'])

                    # 显示攻击力和血量（随从牌）或效果值（法术牌）
                    if card['type'] == "minion":
                        stats = f"({card['attack']}/{card['health']})"
                    elif card['type'] == "spell":
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
                    can_attack = getattr(card, 'can_attack', False)
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
                            if getattr(minion, 'can_attack', False)]
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

        # 英雄技能 - 简化
        if current.mana >= 2:
            hints.append("技能: s")

        # 最核心的快捷操作 - 使用简写
        hints.extend(["结束: Enter", "帮助: h"])

        # 组合提示文本
        full_hint = " | ".join(hints)

        # 如果终端太窄，进一步简化
        if terminal_width < 70:
            # 超紧凑模式
            if playable_cards:
                short_hints = [f"出:{playable_cards[0]}"]
                if current.mana >= 2:
                    short_hints.append("技:s")
                short_hints.extend(["结束:Enter", "帮助:h"])
            else:
                short_hints = []
                if current.mana >= 2:
                    short_hints.append("技:s")
                short_hints.extend(["结束:Enter", "帮助:h"])
            full_hint = " | ".join(short_hints)
        elif terminal_width < 90:
            # 紧凑模式 - 去掉多余文字
            if playable_cards:
                compact_hints = [f"出牌 {playable_cards[0]}"]
                if len(playable_cards) > 1:
                    compact_hints[0] += f"等{len(playable_cards)}张"
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
                            if getattr(minion, 'can_attack', False)]

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
        if not getattr(minion, 'can_attack', False):
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
        if not getattr(minion, 'can_attack', False):
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

                # 执行战斗
                target_minion.health -= minion.attack

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

        return {
            "success": True,
            "message": result_message
        }

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