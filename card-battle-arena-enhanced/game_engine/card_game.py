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
                logger.info(f"🃏 {current.name} 抽取了 {card.name}")

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
            "message": f"{player.name} 打出了 {card.name}"
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
                opponent.health -= minion.attack
                minion.can_attack = False
                messages.append(f"{minion.name} 攻击英雄 {minion.attack} 点")
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
                    if target.health <= minion.attack:
                        # 执行攻击
                        target.health -= minion.attack
                        minion.can_attack = False
                        messages.append(f"{minion.name} 击败 {target.name}")

                        # 反击（除非潜行）
                        if "stealth" not in getattr(minion, 'mechanics', []):
                            minion.health -= target.attack

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
                        messages.append(f"{minion.name} 攻击英雄 {minion.attack} 点")
                    else:
                        target_idx = int(target.split("_")[1])
                        if target_idx < len(opponent.field):
                            target_minion = opponent.field[target_idx]
                            target_minion.health -= minion.attack
                            minion.can_attack = False
                            messages.append(f"{minion.name} vs {target_minion.name}")

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
            "message": f"{player.name} 打出了 {card.name}"
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
                logger.info(f"  ⚔️ {minion.name} 攻击英雄，造成 {minion.attack} 点伤害")

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

            logger.info(f"  ⚔️ {attacker.name} vs {defender.name} ({attacker.attack} damage)")

            # 移除死亡的随从
            if defender.health <= 0:
                opponent.field.remove(defender)
                logger.info(f"  💀 {defender.name} 被击败")

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
                        "name": card.name,
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
                        "name": card.name,
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
                        "name": card.name,
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
                Layout(name="footer", size=3)
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

            # 游戏区域 - 手牌显示
            if current["hand"]:
                hand_table = Table(title="🃏 你的手牌", show_header=True)
                hand_table.add_column("编号", style="yellow", width=4)
                hand_table.add_column("卡牌", style="bold white", width=20)
                hand_table.add_column("费用", style="blue", width=6)
                hand_table.add_column("类型", style="magenta", width=8)
                hand_table.add_column("状态", style="green", width=8)

                for card in current["hand"]:
                    status = "[green]✅ 可出[/green]" if card["playable"] else "[red]❌ 法力不足[/red]"
                    mechanics_str = f" [{', '.join(card.get('mechanics', []))}]" if card.get('mechanics') else ""

                    # 卡牌类型中文映射
                    type_map = {"minion": "随从", "spell": "法术"}
                    card_type_cn = type_map.get(card['type'], card['type'])

                    hand_table.add_row(
                        f"[yellow]{card['index']}[/yellow]",
                        f"[bold]{card['name']}[/bold]",
                        f"[blue]{card['cost']}费[/blue]",
                        f"[magenta]{card_type_cn}[/magenta]{mechanics_str}",
                        status
                    )
                    hand_table.add_row("", f"[dim]{card['description']}[/dim]", "", "", "")

                layout["game_area"].update(Panel(hand_table, border_style="cyan"))
            else:
                layout["game_area"].update(Panel("[dim]手牌为空[/dim]", border_style="dim"))

            # 对手信息
            opponent_table = Table(title="🤖 对手状态", show_header=False)
            opponent_table.add_column("属性", style="red")
            opponent_table.add_column("数值", style="yellow")
            opponent_table.add_row("❤️ 生命值", f"{opponent['health']}/{opponent['max_health']}")
            opponent_table.add_row("💰 法力值", f"{opponent['mana']}/{opponent['max_mana']}")
            opponent_table.add_row("🃋 手牌", f"{opponent['hand_count']} 张")
            opponent_table.add_row("⚔️ 随从", f"{opponent['field_count']} 个")
            layout["opponent_info"].update(Panel(opponent_table, border_style="red"))

            # 底部 - 简化操作提示
            hints = self.get_simple_input_hints()
            hint_text = f"[bold green]💡 快捷操作:[/bold green] {hints}"
            layout["footer"].update(Panel(hint_text, style="green"))

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
                    print(f"  {card['index']}. {card['name']} ({card['cost']}费) - {card_type_cn}{mechanics_str}")
                    print(f"     {card['description']} {status}")

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
        """获取简单的输入提示"""
        if self.game_over:
            return "输入 '退出' 结束游戏"

        current = self.get_current_player()
        hints = []

        # 可出的牌
        playable_cards = [i for i, card in enumerate(current.hand) if current.can_play_card(card)]
        if playable_cards:
            card_hints = [f"[{i}]{card.name}" for i, card in enumerate(current.hand) if current.can_play_card(card)]
            hints.append("出牌: " + ", ".join(card_hints))

        # 英雄技能
        if current.mana >= 2:
            hints.append("英雄技能: 技")

        # 快捷操作
        hints.append("结束回合: 回车/空格")
        hints.append("帮助: 帮")

        return " | ".join(hints)

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