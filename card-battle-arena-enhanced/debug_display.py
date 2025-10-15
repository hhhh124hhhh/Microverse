#!/usr/bin/env python3
"""
调试游戏界面显示问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card
from rich.console import Console

console = Console()

def debug_display():
    """调试显示问题"""
    console.print("🔍 [bold blue]游戏界面显示调试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("调试玩家", "调试对手")

    # 清空手牌，添加已知的法术牌
    game.players[0].hand.clear()

    # 添加法术牌
    card = Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火，对敌人造成3点伤害")
    game.players[0].hand.append(card)

    # 设置足够的法力值
    game.players[0].mana = 10
    game.players[0].max_mana = 10

    # 获取游戏状态
    state = game.get_game_state()
    current = state["current_player_state"]
    console.print(f"🎮 [bold cyan]游戏状态数据：[/bold cyan]")
    console.print(f"   手牌数量: {len(current['hand'])}")

    # 分析第一张卡牌
    if current['hand']:
        card_data = current['hand'][0]
        console.print(f"\n📋 [bold yellow]卡牌数据：[/bold yellow]")
        console.print(f"   名称: {card_data['name']}")
        console.print(f"   类型: {card_data['type']}")
        console.print(f"   攻击力: {card_data['attack']}")
        console.print(f"   血量: {card_data['health']}")

        # 模拟显示逻辑
        console.print(f"\n🎨 [bold green]显示逻辑模拟：[/bold green]")
        card_type = card_data.get('type', '')
        console.print(f"   卡牌类型: '{card_type}'")

        if card_type == "minion":
            stats = f"[red]{card_data['attack']}[/red]/[green]{card_data['health']}[/green]"
            console.print(f"   随从显示: '{stats}'")
        elif card_type == "spell":
            if card_data['attack'] > 0:
                stats = f"[red]🔥{card_data['attack']}[/red]"  # 伤害法术
                console.print(f"   伤害法术显示: '{stats}'")
            elif card_data['attack'] < 0:
                stats = f"[green]💚{-card_data['attack']}[/green]"  # 治疗法术
                console.print(f"   治疗法术显示: '{stats}'")
            else:
                stats = "[blue]✨[/blue]"  # 其他法术
                console.print(f"   其他法术显示: '{stats}'")
        else:
            stats = ""
            console.print(f"   未知类型显示: '{stats}'")

        # 检查字符串长度
        console.print(f"\n📏 [bold magenta]字符串分析：[/bold magenta]")
        console.print(f"   原始stats: '{stats}'")
        console.print(f"   长度: {len(stats)}")
        console.print(f"   字符: {[c for c in stats]}")

        # 检查 Rich 标签
        if '[' in stats and ']' in stats:
            console.print(f"   包含 Rich 标签: 是")
            # 提取纯文本
            import re
            plain_text = re.sub(r'\[/?[^\]]+\]', '', stats)
            console.print(f"   纯文本: '{plain_text}'")
            console.print(f"   纯文本长度: {len(plain_text)}")
        else:
            console.print(f"   包含 Rich 标签: 否")

    # 尝试手动创建表格
    console.print(f"\n📊 [bold cyan]手动表格测试：[/bold cyan]")
    from rich.table import Table
    from rich.panel import Panel

    manual_table = Table(title="手动测试表格", show_header=True)
    manual_table.add_column("编号", style="yellow", width=8, justify="right")
    manual_table.add_column("卡牌", style="bold white", width=20, justify="left")
    manual_table.add_column("费用", style="blue", width=4, justify="center")
    manual_table.add_column("属性", style="red", width=12, justify="center")

    # 使用与游戏相同的逻辑
    for card in current['hand']:
        card_type = card.get('type', '')
        if card_type == "minion":
            stats = f"[red]{card['attack']}[/red]/[green]{card['health']}[/green]"
        elif card_type == "spell":
            if card['attack'] > 0:
                stats = f"[red]🔥{card['attack']}[/red]"
            elif card['attack'] < 0:
                stats = f"[green]💚{-card['attack']}[/green]"
            else:
                stats = "[blue]✨[/blue]"
        else:
            stats = ""

        console.print(f"   添加行 - stats: '{stats}'")
        manual_table.add_row(
            f"[yellow]{card['index']}[/yellow]",
            f"[bold]{card['name']}[/bold]",
            f"[blue]{card['cost']}[/blue]",
            stats
        )

    console.print(Panel(manual_table, border_style="cyan"))

    console.print(f"\n🎮 [bold red]实际游戏界面：[/bold red]")
    game.display_status()

if __name__ == "__main__":
    debug_display()