#!/usr/bin/env python3
"""
专门测试法术显示问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card
from rich.console import Console

console = Console()

def test_spell_display():
    """测试法术显示问题"""
    console.print("🧪 [bold blue]法术显示问题测试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")

    # 清空手牌，添加已知的法术牌
    game.players[0].hand.clear()

    # 添加不同类型的法术
    cards = [
        Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火，对敌人造成3点伤害"),
        Card("治愈术", 2, -5, 0, "spell", [], "💚 圣光之力，恢复5点生命值"),
        Card("火球术", 4, 6, 0, "spell", [], "🔥 法师经典法术，召唤炽热火球轰击敌人"),
        Card("奥术智慧", 3, 0, 0, "spell", ["draw_cards"], "📚 深奥的魔法知识，从虚空中抽取两张卡牌"),
    ]

    for card in cards:
        game.players[0].hand.append(card)

    # 设置足够的法力值
    game.players[0].mana = 10
    game.players[0].max_mana = 10

    console.print(f"📋 [bold cyan]测试法术：[/bold cyan]")
    for i, card in enumerate(game.players[0].hand):
        console.print(f"   {i}. {card.name} - {card.card_type} (攻击力: {card.attack}, 血量: {card.health})")

    # 获取游戏状态数据
    state = game.get_game_state()
    current_hand = state["current_player_state"]["hand"]

    console.print(f"\n🔍 [bold yellow]游戏状态中的手牌数据：[/bold yellow]")
    for card_data in current_hand:
        console.print(f"   {card_data['name']}: type={card_data['type']}, attack={card_data['attack']}, health={card_data['health']}")

    # 模拟显示逻辑
    console.print(f"\n🎨 [bold green]模拟显示逻辑：[/bold green]")
    for card in current_hand:
        card_type = card.get('type', '')
        if card_type == "minion":
            stats = f"{card['attack']}/{card['health']}"
        elif card_type == "spell":
            if card['attack'] > 0:
                stats = f"🔥{card['attack']}"  # 伤害法术
            elif card['attack'] < 0:
                stats = f"💚{-card['attack']}"  # 治疗法术
            else:
                stats = "✨"  # 其他法术
        else:
            stats = ""

        console.print(f"   {card['name']}: 显示为 '{stats}'")

    # 检查终端宽度和列宽计算
    console.print(f"\n📏 [bold magenta]终端宽度测试：[/bold magenta]")
    try:
        import shutil
        terminal_width = shutil.get_terminal_size().columns
        console.print(f"   终端宽度: {terminal_width}")

        # 模拟列宽计算
        min_widths = {
            "index": 6, "name": 12, "cost": 3, "stats": 6, "type": 6, "status": 6
        }
        total_min_width = sum(min_widths.values())
        console.print(f"   最小总宽度: {total_min_width}")

        # 使用游戏中的函数计算
        from game_engine.card_game import calculate_table_widths
        col_widths = calculate_table_widths(terminal_width, min_widths, total_min_width)
        console.print(f"   计算后的列宽: {col_widths}")
        console.print(f"   属性列宽度: {col_widths['stats']}")

        # 检查法术显示内容是否超出列宽
        for card in current_hand:
            card_type = card.get('type', '')
            if card_type == "spell":
                if card['attack'] > 0:
                    stats = f"🔥{card['attack']}"
                elif card['attack'] < 0:
                    stats = f"💚{-card['attack']}"
                else:
                    stats = "✨"

                stats_len = len(stats)
                max_len = col_widths['stats']
                console.print(f"   {card['name']}: '{stats}' (长度: {stats_len}, 最大: {max_len}) - {'✅正常' if stats_len <= max_len else '❌超出'}")

    except Exception as e:
        console.print(f"   错误: {e}")

    console.print(f"\n🎮 [bold cyan]实际游戏界面：[/bold cyan]")
    game.display_status()

if __name__ == "__main__":
    test_spell_display()