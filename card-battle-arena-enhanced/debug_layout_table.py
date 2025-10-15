#!/usr/bin/env python3
"""
专门调试Layout环境下的表格渲染问题
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from game_engine.card_game import get_terminal_width, calculate_table_widths

def debug_layout_table():
    """调试Layout环境下的表格问题"""
    console = Console()

    console.print("🔍 [bold blue]Layout 表格渲染调试[/bold blue]")
    console.print("=" * 50)

    # 获取终端宽度
    terminal_width = get_terminal_width()
    console.print(f"终端宽度: {terminal_width}")

    # 模拟游戏的列宽计算
    min_widths = {
        "index": 6,
        "name": 12,
        "cost": 5,     # 更新后的宽度
        "stats": 8,
        "type": 7,     # 更新后的宽度
        "status": 8    # 更新后的宽度
    }
    total_min_width = sum(min_widths.values())
    console.print(f"最小总宽度: {total_min_width}")

    # 计算实际列宽
    col_widths = calculate_table_widths(terminal_width, min_widths, total_min_width)
    console.print(f"计算的列宽: {col_widths}")

    # 测试1: 独立表格
    console.print(f"\n📊 [bold cyan]测试1: 独立表格[/bold cyan]")
    standalone_table = Table(title="独立表格", show_header=True)
    standalone_table.add_column("编号", style="yellow", width=col_widths["index"], justify="right")
    standalone_table.add_column("卡牌", style="bold white", width=col_widths["name"], justify="left")
    standalone_table.add_column("费用", style="blue", width=col_widths["cost"], justify="center")
    standalone_table.add_column("属性", style="red", width=col_widths["stats"], justify="center")
    standalone_table.add_column("类型", style="magenta", width=col_widths["type"], justify="center")
    standalone_table.add_column("状态", style="green", width=col_widths["status"], justify="center")

    # 添加测试数据
    test_data = [
        ("0", "狂野之怒", "1", "[red]🔥3[/red]", "法术", "[green]✅ 可出[/green]"),
        ("1", "治愈术", "2", "[green]💚5[/green]", "法术", "[green]✅ 可出[/green]"),
        ("2", "奥术智慧", "3", "[blue]✨[/blue]", "法术", "[green]✅ 可出[/green]"),
    ]

    for data in test_data:
        standalone_table.add_row(*data)

    console.print(standalone_table)

    # 测试2: Panel内的表格
    console.print(f"\n📋 [bold magenta]测试2: Panel内的表格[/bold magenta]")
    panel_table = Table(title="Panel表格", show_header=True)
    panel_table.add_column("编号", style="yellow", width=col_widths["index"], justify="right")
    panel_table.add_column("卡牌", style="bold white", width=col_widths["name"], justify="left")
    panel_table.add_column("费用", style="blue", width=col_widths["cost"], justify="center")
    panel_table.add_column("属性", style="red", width=col_widths["stats"], justify="center")
    panel_table.add_column("类型", style="magenta", width=col_widths["type"], justify="center")
    panel_table.add_column("状态", style="green", width=col_widths["status"], justify="center")

    for data in test_data:
        panel_table.add_row(*data)

    console.print(Panel(panel_table, border_style="cyan"))

    # 测试3: Layout中的表格（模拟游戏环境）
    console.print(f"\n🎮 [bold green]测试3: Layout中的表格（游戏环境）[/bold green]")

    layout = Layout()
    layout.split_row(
        Layout(name="left", ratio=1),
        Layout(name="center", ratio=2),
        Layout(name="right", ratio=1)
    )

    # 在center中创建表格
    layout_table = Table(title="🃏 你的手牌", show_header=True)
    layout_table.add_column("编号", style="yellow", width=col_widths["index"], justify="right")
    layout_table.add_column("卡牌", style="bold white", width=col_widths["name"], justify="left")
    layout_table.add_column("费用", style="blue", width=col_widths["cost"], justify="center")
    layout_table.add_column("属性", style="red", width=col_widths["stats"], justify="center")
    layout_table.add_column("类型", style="magenta", width=col_widths["type"], justify="center")
    layout_table.add_column("状态", style="green", width=col_widths["status"], justify="center")

    for data in test_data:
        layout_table.add_row(*data)

    layout["center"].update(Panel(layout_table, border_style="cyan"))

    # 填充左右两侧
    layout["left"].update(Panel("左侧区域", border_style="green"))
    layout["right"].update(Panel("右侧区域", border_style="red"))

    console.print(layout)

    # 测试4: 不指定宽度的自适应表格
    console.print(f"\n🔄 [bold yellow]测试4: 不指定宽度的自适应表格[/bold yellow]")

    auto_table = Table(title="🃏 你的手牌（自适应）", show_header=True)
    auto_table.add_column("编号", style="yellow", justify="right")
    auto_table.add_column("卡牌", style="bold white", justify="left")
    auto_table.add_column("费用", style="blue", justify="center")
    auto_table.add_column("属性", style="red", justify="center")
    auto_table.add_column("类型", style="magenta", justify="center")
    auto_table.add_column("状态", style="green", justify="center")

    for data in test_data:
        auto_table.add_row(*data)

    console.print(Panel(auto_table, border_style="cyan"))

    # 测试5: 使用min_width而不是width
    console.print(f"\n📏 [bold blue]测试5: 使用min_width的表格[/bold blue]")

    min_table = Table(title="🃏 你的手牌（min_width）", show_header=True)
    min_table.add_column("编号", style="yellow", min_width=min_widths["index"], justify="right")
    min_table.add_column("卡牌", style="bold white", min_width=min_widths["name"], justify="left")
    min_table.add_column("费用", style="blue", min_width=min_widths["cost"], justify="center")
    min_table.add_column("属性", style="red", min_width=min_widths["stats"], justify="center")
    min_table.add_column("类型", style="magenta", min_width=min_widths["type"], justify="center")
    min_table.add_column("状态", style="green", min_width=min_widths["status"], justify="center")

    for data in test_data:
        min_table.add_row(*data)

    console.print(Panel(min_table, border_style="cyan"))

if __name__ == "__main__":
    debug_layout_table()