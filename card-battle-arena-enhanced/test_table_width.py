#!/usr/bin/env python3
"""
测试表格宽度计算
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import calculate_table_widths, get_terminal_width
from rich.console import Console

console = Console()

def test_table_width():
    """测试表格宽度计算"""
    console.print("📏 [bold blue]表格宽度计算测试[/bold blue]")
    console.print("=" * 50)

    # 模拟游戏中的计算
    terminal_width = get_terminal_width()
    console.print(f"终端宽度: {terminal_width}")

    min_widths = {
        "index": 6,    # 编号 - 增加宽度确保数字可见
        "name": 12,    # 卡牌名称
        "cost": 3,     # 费用
        "stats": 6,    # 属性
        "type": 6,     # 类型
        "status": 6    # 状态
    }
    total_min_width = sum(min_widths.values())
    console.print(f"最小总宽度: {total_min_width}")

    # 计算实际列宽
    col_widths = calculate_table_widths(terminal_width, min_widths, total_min_width)
    console.print(f"计算的列宽: {col_widths}")
    console.print(f"属性列宽度: {col_widths['stats']}")

    # 测试不同终端宽度
    test_widths = [40, 60, 80, 100, 120]
    console.print(f"\n📊 [bold cyan]不同终端宽度的列宽测试：[/bold cyan]")
    for width in test_widths:
        col_widths = calculate_table_widths(width, min_widths, total_min_width)
        console.print(f"终端宽度 {width}: 属性列 = {col_widths['stats']}")

    # 测试极端情况
    console.print(f"\n🔧 [bold yellow]极端情况测试：[/bold yellow]")
    # 极窄终端
    narrow_widths = calculate_table_widths(40, min_widths, total_min_width)
    console.print(f"终端宽度 40: 属性列 = {narrow_widths['stats']}")

    # 测试手动创建表格与 Rich 自动调整的对比
    console.print(f"\n📋 [bold green]Rich 表格测试：[/bold green]")
    from rich.table import Table

    # 使用计算出的宽度
    stats_width = col_widths['stats']
    console.print(f"使用计算的属性列宽度: {stats_width}")

    # 创建一个测试表格
    test_table = Table(show_header=True)
    test_table.add_column("编号", width=8, justify="right")
    test_table.add_column("属性", width=stats_width, justify="center")

    # 添加测试数据
    test_data = [
        "🔥3",
        "💚5",
        "✨",
        "5/3",
        "[red]🔥3[/red]",
        "[green]💚5[/green]",
        "[blue]✨[/blue]",
        "[red]5[/red]/[green]3[/green]"
    ]

    for i, data in enumerate(test_data):
        console.print(f"添加行 {i}: '{data}' (长度: {len(data)})")
        test_table.add_row(str(i), data)

    console.print(test_table)

if __name__ == "__main__":
    test_table_width()