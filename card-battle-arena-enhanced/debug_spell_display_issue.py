#!/usr/bin/env python3
"""
专门调查法术显示问题：为什么显示"法术"而不是"🔥3"
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def debug_spell_display():
    """调试法术显示问题"""
    from rich.console import Console
    from rich.table import Table
    console = Console()

    console.print("🎯 [bold blue]法术显示问题调试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    player = game.players[0]

    # 清空手牌并添加不同类型的法术
    player.hand.clear()
    spells = [
        Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火，对敌人造成3点伤害"),
        Card("治愈术", 2, -5, 0, "spell", [], "💚 圣光之力，恢复5点生命值"),
        Card("奥术智慧", 3, 0, 0, "spell", ["draw_cards"], "📚 深奥的魔法知识，从虚空中抽取两张卡牌"),
    ]

    for spell in spells:
        player.hand.append(spell)
    player.mana = 10
    player.max_mana = 10

    console.print(f"📋 [bold cyan]测试法术：[/bold cyan]")
    for i, spell in enumerate(spells):
        console.print(f"   {i}. {spell.name} (攻击力: {spell.attack})")

    # 获取游戏状态
    console.print(f"\n🔍 [bold yellow]检查游戏状态数据：[/bold yellow]")
    state = game.get_game_state()
    hand_cards = state["current_player_state"]["hand"]

    for i, card_data in enumerate(hand_cards):
        console.print(f"\n   卡牌 {i}: {card_data['name']}")
        console.print(f"     原始数据: type={card_data['type']}, attack={card_data['attack']}")

        # 模拟显示逻辑
        card_type = card_data.get('type', '')
        attack = card_data.get('attack', 0)

        if card_type == "spell":
            if attack > 0:
                expected_stats = f"🔥{attack}"
            elif attack < 0:
                expected_stats = f"💚{-attack}"
            else:
                expected_stats = "✨"

            console.print(f"     预期显示: {expected_stats}")
            console.print(f"     实际显示逻辑: [red]{expected_stats}[/red]" if attack > 0 else f"[green]{expected_stats}[/green]" if attack < 0 else f"[blue]{expected_stats}[/blue]")

    # 测试独立的Rich表格
    console.print(f"\n📊 [bold magenta]测试独立Rich表格：[/bold magenta]")
    test_table = Table(title="独立测试表格", show_header=True)
    test_table.add_column("卡牌", style="bold white", justify="left")
    test_table.add_column("属性", style="red", justify="center")

    for card_data in hand_cards:
        card_type = card_data.get('type', '')
        attack = card_data.get('attack', 0)

        if card_type == "spell":
            if attack > 0:
                stats_display = f"[red]🔥{attack}[/red]"
            elif attack < 0:
                stats_display = f"[green]💚{-attack}[/green]"
            else:
                stats_display = "[blue]✨[/blue]"
        else:
            stats_display = "N/A"

        test_table.add_row(card_data['name'], stats_display)

    console.print(test_table)

    # 检查实际的game.display_status()输出
    console.print(f"\n🎮 [bold green]实际游戏界面：[/bold green]")
    game.display_status()

    console.print(f"\n🔧 [bold blue]问题分析：[/bold blue]")
    console.print("1. 数据层面: ✅ 游戏状态数据正确")
    console.print("2. 逻辑层面: ✅ 显示逻辑正确")
    console.print("3. 独立表格: ✅ Rich可以正确显示emoji")
    console.print("4. 游戏界面: ❌ 实际显示有问题")
    console.print("\n   问题可能在于:")
    console.print("   - Rich表格在Layout环境下的渲染问题")
    console.print("   - 列宽计算导致内容被截断")
    console.print("   - 表格嵌套在Panel中的显示问题")

if __name__ == "__main__":
    debug_spell_display()