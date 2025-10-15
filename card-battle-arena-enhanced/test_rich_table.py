#!/usr/bin/env python3
"""
测试 Rich 表格对 emoji 的处理
"""
from rich.console import Console
from rich.table import Table

console = Console()

def test_rich_table_with_emoji():
    """测试 Rich 表格对 emoji 的处理"""
    console.print("🧪 [bold blue]Rich 表格 Emoji 测试[/bold blue]")
    console.print("=" * 50)

    # 创建表格
    table = Table(title="测试表格", show_header=True)
    table.add_column("编号", style="yellow", width=6, justify="right")
    table.add_column("卡牌", style="bold white", width=20, justify="left")
    table.add_column("费用", style="blue", width=4, justify="center")
    table.add_column("属性", style="red", width=12, justify="center")
    table.add_column("类型", style="magenta", width=8, justify="center")

    # 测试数据
    test_data = [
        ("0", "狂野之怒", "1", "🔥3", "法术"),
        ("1", "治愈术", "2", "💚5", "法术"),
        ("2", "火球术", "4", "🔥6", "法术"),
        ("3", "奥术智慧", "3", "✨", "法术"),
        ("4", "烈焰元素", "3", "5/3", "随从"),
    ]

    # 添加行
    for idx, name, cost, stats, card_type in test_data:
        table.add_row(
            f"[yellow]{idx}[/yellow]",
            f"[bold]{name}[/bold]",
            f"[blue]{cost}[/blue]",
            f"[red]{stats}[/red]",
            f"[magenta]{card_type}[/magenta]"
        )

    # 显示表格
    console.print(table)

    # 测试单独的 emoji 显示
    console.print("\n🔍 [bold yellow]单独 Emoji 测试：[/bold yellow]")
    console.print("🔥3")
    console.print("💚5")
    console.print("✨")
    console.print("[red]🔥3[/red]")
    console.print("[green]💚5[/green]")
    console.print("[blue]✨[/blue]")

    # 测试不同宽度的列
    console.print("\n📏 [bold magenta]不同列宽测试：[/bold magenta]")

    narrow_table = Table(title="窄列表格", show_header=True)
    narrow_table.add_column("编号", width=4)
    narrow_table.add_column("属性", width=4)  # 故意设得很窄

    narrow_table.add_row("0", "🔥3")
    narrow_table.add_row("1", "💚5")
    narrow_table.add_row("2", "✨")

    console.print(narrow_table)

    wide_table = Table(title="宽列表格", show_header=True)
    wide_table.add_column("编号", width=8)
    wide_table.add_column("属性", width=16)  # 足够宽

    wide_table.add_row("0", "🔥3")
    wide_table.add_row("1", "💚5")
    wide_table.add_row("2", "✨")

    console.print(wide_table)

if __name__ == "__main__":
    test_rich_table_with_emoji()