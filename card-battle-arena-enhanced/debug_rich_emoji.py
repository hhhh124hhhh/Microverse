#!/usr/bin/env python3
"""
专门测试 Rich 表格的 emoji 截断问题
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import shutil

console = Console()

def test_emoji_truncation():
    """测试 emoji 截断问题"""
    console.print("🔍 [bold blue]Rich 表格 Emoji 截断测试[/bold blue]")
    console.print("=" * 50)

    # 获取终端宽度
    terminal_width = shutil.get_terminal_size().columns
    console.print(f"终端宽度: {terminal_width}")

    # 测试不同宽度的列
    test_widths = [4, 6, 8, 10, 12]

    for width in test_widths:
        console.print(f"\n📏 [bold cyan]测试列宽: {width}[/bold cyan]")

        # 创建简单表格
        table = Table(show_header=True)
        table.add_column("编号", width=6, justify="right")
        table.add_column("属性", width=width, justify="center")

        # 测试数据
        test_data = [
            ("0", "🔥3"),
            ("1", "💚5"),
            ("2", "✨"),
            ("3", "5/3"),
            ("4", "[red]🔥3[/red]"),
            ("5", "[green]💚5[/green]"),
            ("6", "[blue]✨[/blue]"),
            ("7", "[red]5[/red]/[green]3[/green]")
        ]

        for idx, stats in test_data:
            table.add_row(idx, stats)

        console.print(table)

        # 检查实际内容长度
        console.print(f"   测试数据长度: {[len(stats) for _, stats in test_data]}")

    # 测试不指定宽度的情况
    console.print(f"\n🔄 [bold yellow]不指定列宽的测试：[/bold yellow]")
    auto_table = Table(show_header=True)
    auto_table.add_column("编号", justify="right")
    auto_table.add_column("属性", justify="center")

    for idx, stats in test_data:
        auto_table.add_row(idx, stats)

    console.print(auto_table)

    # 测试使用 min_width 而不是 width
    console.print(f"\n📏 [bold magenta]使用 min_width 而不是 width：[/bold magenta]")
    min_table = Table(show_header=True)
    min_table.add_column("编号", min_width=6, justify="right")
    min_table.add_column("属性", min_width=8, justify="center")

    for idx, stats in test_data:
        min_table.add_row(idx, stats)

    console.print(min_table)

    # 测试带 overflow 参数
    console.print(f"\n🔄 [bold green]测试 overflow 参数：[/bold green]")
    overflow_table = Table(show_header=True)
    overflow_table.add_column("编号", width=6, justify="right")
    overflow_table.add_column("属性", width=8, justify="center", overflow="fold")

    for idx, stats in test_data:
        overflow_table.add_row(idx, stats)

    console.print(overflow_table)

def test_game_table_scenario():
    """测试游戏表格的具体场景"""
    console.print(f"\n🎮 [bold blue]游戏表格场景测试[/bold blue]")
    console.print("=" * 50)

    # 模拟游戏的表格设置
    terminal_width = shutil.get_terminal_size().columns
    console.print(f"终端宽度: {terminal_width}")

    # 游戏中的列宽计算
    min_widths = {
        "index": 6,    # 编号
        "name": 12,    # 卡牌名称
        "cost": 3,     # 费用
        "stats": 6,    # 属性
        "type": 6,     # 类型
        "status": 6    # 状态
    }

    # 模拟 calculate_table_widths 的简化逻辑
    total_min_width = sum(min_widths.values())
    console.print(f"最小总宽度: {total_min_width}")

    if terminal_width > total_min_width + 12:
        # 有足够宽度，分配额外空间
        extra_width = terminal_width - total_min_width - 12
        console.print(f"额外宽度: {extra_width}")

        # 优先分配给属性列
        min_widths["stats"] = min(min_widths["stats"] + 4, 10)
        console.print(f"调整后的属性列宽度: {min_widths['stats']}")

    # 创建游戏风格的表格
    game_table = Table(title="🃏 手牌测试", show_header=True)
    game_table.add_column("编号", style="yellow", width=min_widths["index"], justify="right")
    game_table.add_column("卡牌", style="bold white", width=min_widths["name"], justify="left")
    game_table.add_column("费用", style="blue", width=min_widths["cost"], justify="center")
    game_table.add_column("属性", style="red", width=min_widths["stats"], justify="center")
    game_table.add_column("类型", style="magenta", width=min_widths["type"], justify="center")
    game_table.add_column("状态", style="green", width=min_widths["status"], justify="center")

    # 添加测试数据
    test_cards = [
        ("0", "狂野之怒", "1", "[red]🔥3[/red]", "法术", "[green]✅ 可出[/green]"),
        ("1", "治愈术", "2", "[green]💚5[/green]", "法术", "[green]✅ 可出[/green]"),
        ("2", "奥术智慧", "3", "[blue]✨[/blue]", "法术", "[green]✅ 可出[/green]"),
        ("3", "烈焰元素", "3", "[red]5[/red]/[green]3[/green]", "随从", "[green]✅ 可出[/green]"),
    ]

    for card_data in test_cards:
        game_table.add_row(*card_data)

    console.print(Panel(game_table, border_style="cyan"))

if __name__ == "__main__":
    test_emoji_truncation()
    test_game_table_scenario()