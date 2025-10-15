#!/usr/bin/env python3
"""
集成新Layout系统的游戏演示
展示真正的界面变化
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_ui import GameLayout, GameUIWithLive
from rich.console import Console
from rich.live import Live
import time

console = Console()

def create_sample_game_state():
    """创建示例游戏状态"""
    return {
        "player": {
            "health": 25,
            "max_health": 30,
            "mana": 6,
            "max_mana": 6,
            "hand_count": 4,
            "field_count": 2
        },
        "opponent": {
            "health": 18,
            "max_health": 30,
            "mana": 4,
            "max_mana": 4,
            "hand_count": 3,
            "field_count": 1
        },
        "hand": [
            {"name": "火球术", "cost": 4, "attack": 6, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
            {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 2},
            {"name": "暗影巫师", "cost": 8, "attack": 2, "health": 5, "type": "minion", "index": 3}
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

def demo_old_vs_new():
    """对比演示：旧界面 vs 新Layout界面"""
    console.print("🎯 [bold red]界面变化对比演示[/bold red]")
    console.print("=" * 60)

    # 旧界面模拟（显示当前问题）
    console.print("\n❌ [bold red]旧界面问题[/bold red]")
    console.print("• 三栏水平布局导致内容压缩")
    console.print("• 卡牌信息显示不全")
    console.print("• 小屏幕下完全不可用")

    console.print("\n" + "─" * 50)

    # 新界面展示
    console.print("\n✅ [bold green]新Rich Layout界面[/bold green]")
    demo_new_interface()

def demo_new_interface():
    """演示新界面"""
    layout_manager = GameLayout()
    game_state = create_sample_game_state()

    # 更新各个区域
    layout_manager.update_player_status(game_state["player"])
    layout_manager.update_opponent_status(game_state["opponent"])
    layout_manager.update_hand_area(game_state["hand"], game_state["player"]["mana"])
    layout_manager.update_battlefield_area(
        game_state["battlefield"]["player"],
        game_state["battlefield"]["opponent"]
    )
    layout_manager.update_command_area(["出牌 0-3", "技能", "结束回合", "帮助"])

    # 显示新界面
    console.print(layout_manager.layout)

def demo_responsive():
    """演示响应式特性"""
    console.print("\n📱 [bold cyan]响应式布局演示[/bold cyan]")
    console.print("=" * 40)

    layout_manager = GameLayout()

    # 测试不同宽度
    test_cases = [
        (70, "超窄屏 - 垂直布局"),
        (90, "窄屏 - 紧凑布局"),
        (120, "标准屏 - 水平布局"),
        (160, "宽屏 - 舒适布局")
    ]

    for width, description in test_cases:
        layout_manager.adapt_to_width(width)
        console.print(f"\n🖥️  {description} ({width}列)")
        console.print(f"   布局模式: [bold green]{layout_manager.layout_mode}[/bold green]")

async def demo_live_updates():
    """演示动态更新"""
    console.print("\n🔄 [bold blue]动态更新演示[/bold blue]")
    console.print("模拟游戏过程中的界面变化...")
    console.print("按 Ctrl+C 停止演示")
    console.print("=" * 50)

    ui_manager = GameUIWithLive()
    ui_manager.start_rendering()

    # 模拟游戏状态序列
    game_states = [
        create_sample_game_state(),
        # 状态1: 使用火球术
        {
            "player": {"health": 25, "max_health": 30, "mana": 2, "max_mana": 6, "hand_count": 3, "field_count": 2},
            "opponent": {"health": 12, "max_health": 30, "mana": 4, "max_mana": 4, "hand_count": 3, "field_count": 1},
            "hand": [
                {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
                {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 2},
                {"name": "暗影巫师", "cost": 8, "attack": 2, "health": 5, "type": "minion", "index": 3}
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
        },
        # 状态2: 出新随从
        {
            "player": {"health": 25, "max_health": 30, "mana": 0, "max_mana": 6, "hand_count": 2, "field_count": 3},
            "opponent": {"health": 12, "max_health": 30, "mana": 4, "max_mana": 4, "hand_count": 3, "field_count": 1},
            "hand": [
                {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 2},
                {"name": "暗影巫师", "cost": 8, "attack": 2, "health": 5, "type": "minion", "index": 3}
            ],
            "battlefield": {
                "player": [
                    {"name": "狼人渗透者", "attack": 3, "health": 2, "can_attack": False, "index": 0},
                    {"name": "铁甲战士", "attack": 2, "health": 5, "can_attack": False, "index": 1},
                    {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "can_attack": True, "index": 2}
                ],
                "opponent": [
                    {"name": "霜狼步兵", "attack": 2, "health": 3, "can_attack": True, "index": 0}
                ]
            }
        }
    ]

    messages = [
        "📋 初始状态",
        "🔥 使用火球术！对手血量 12/30",
        "⚔️ 召唤烈焰元素！战场变化"
    ]

    try:
        for i, (state, message) in enumerate(zip(game_states, messages)):
            ui_manager.update_game_state(state)
            console.print(f"\n[dim]{message}[/dim]")
            await asyncio.sleep(3)
    except KeyboardInterrupt:
        console.print("\n[yellow]演示已停止[/yellow]")
    finally:
        ui_manager.stop_rendering()

async def main():
    """主演示函数"""
    console.print("🎮 [bold magenta]Rich Layout集成演示[/bold magenta]")
    console.print("展示TDD开发的真正界面变化")
    console.print("=" * 70)

    # 对比演示
    demo_old_vs_new()

    # 响应式演示
    demo_responsive()

    # 动态更新演示
    await demo_live_updates()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]演示结束[/yellow]")