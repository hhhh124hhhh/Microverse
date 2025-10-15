#!/usr/bin/env python3
"""
展示界面变化的静态演示
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_ui import GameLayout
from rich.console import Console

console = Console()

def show_interface_comparison():
    """展示界面对比"""
    console.print("🎯 [bold red]真正的界面变化演示[/bold red]")
    console.print("=" * 70)

    console.print("\n❌ [bold red]问题：旧界面布局压缩[/bold red]")
    console.print("您之前看到的界面问题：")
    console.print("• 手牌表格被挤压，信息显示不全")
    console.print("• 三栏布局在小屏幕下不可用")
    console.print("• 卡牌编号、属性信息被截断")

    console.print("\n" + "─" * 70)
    console.print("\n✅ [bold green]解决方案：新的Rich Layout系统[/bold green]")

    # 创建并展示新界面
    layout_manager = GameLayout()

    # 示例游戏数据
    game_state = {
        "player": {
            "health": 25, "max_health": 30,
            "mana": 6, "max_mana": 6,
            "hand_count": 5, "field_count": 2
        },
        "opponent": {
            "health": 18, "max_health": 30,
            "mana": 4, "max_mana": 4,
            "hand_count": 3, "field_count": 1
        },
        "hand": [
            {"name": "火球术", "cost": 4, "attack": 6, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
            {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 2},
            {"name": "治疗之环", "cost": 2, "attack": 0, "health": 0, "type": "spell", "index": 3},
            {"name": "暗影巫师", "cost": 8, "attack": 2, "health": 5, "type": "minion", "index": 4}
        ],
        "battlefield": {
            "player": [
                {"name": "狼人渗透者", "attack": 3, "health": 2, "can_attack": True, "index": 0},
                {"name": "铁甲战士", "attack": 2, "health": 5, "can_attack": False, "index": 1}
            ],
            "opponent": [
                {"name": "霜狼步兵", "attack": 2, "health": 3, "can_attack": True, "index": 0}
            ]
        }
    }

    # 更新布局
    layout_manager.update_player_status(game_state["player"])
    layout_manager.update_opponent_status(game_state["opponent"])
    layout_manager.update_hand_area(game_state["hand"], game_state["player"]["mana"])
    layout_manager.update_battlefield_area(
        game_state["battlefield"]["player"],
        game_state["battlefield"]["opponent"]
    )
    layout_manager.update_command_area(["出牌 0-4", "技能", "结束回合", "帮助", "设置"])

    # 显示新界面
    console.print("\n🎮 [bold blue]新界面效果：[/bold blue]")
    console.print(layout_manager.layout)

    console.print("\n" + "─" * 70)
    console.print("\n📊 [bold cyan]关键改进点：[/bold cyan]")

    improvements = [
        "✅ **智能布局分配**：Rich Layout自动管理空间，避免内容压缩",
        "✅ **信息完整显示**：所有卡牌信息（编号、名称、费用、状态）都清晰可见",
        "✅ **响应式设计**：根据终端宽度自动调整布局（80/120列断点）",
        "✅ **组件化架构**：每个区域独立管理，易于维护和扩展",
        "✅ **可出性标记**：✅/❌ 清晰标识哪些卡牌可以使用",
        "✅ **状态指示器**：🗡️可攻、😴休眠、⚠️威胁等直观图标"
    ]

    for improvement in improvements:
        console.print(f"  {improvement}")

    console.print("\n🔧 [bold yellow]技术实现：[/bold yellow]")
    console.print("• 采用严格的TDD红-绿-重构循环开发")
    console.print("• 使用Rich Layout进行专业布局管理")
    console.print("• 组件化设计，每个功能都有独立测试")
    console.print("• 支持Live实时刷新和动态更新")

if __name__ == "__main__":
    show_interface_comparison()