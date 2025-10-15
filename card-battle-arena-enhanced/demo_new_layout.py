#!/usr/bin/env python3
"""
演示新的Rich Layout界面系统
展示TDD开发的成果
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


def create_demo_game_state():
    """创建演示游戏状态"""
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


def demo_static_layout():
    """演示静态Layout"""
    console = Console()
    console.print("🎮 [bold blue]Rich Layout系统演示[/bold blue]")
    console.print("=" * 50)

    layout_manager = GameLayout()
    game_state = create_demo_game_state()

    # 更新各个区域
    layout_manager.update_player_status(game_state["player"])
    layout_manager.update_opponent_status(game_state["opponent"])
    layout_manager.update_hand_area(game_state["hand"], game_state["player"]["mana"])
    layout_manager.update_battlefield_area(
        game_state["battlefield"]["player"],
        game_state["battlefield"]["opponent"]
    )
    layout_manager.update_command_area(["出牌 0-3", "技能", "结束回合", "帮助"])

    # 显示布局
    console.print(layout_manager.layout)


def demo_live_layout():
    """演示Live动态刷新"""
    console = Console()
    console.print("\n🔄 [bold green]Live动态刷新演示[/bold green]")
    console.print("模拟游戏状态变化...")
    console.print("按 Ctrl+C 停止演示")
    console.print("=" * 50)

    try:
        ui_manager = GameUIWithLive()
        ui_manager.start_rendering()

        # 模拟游戏状态变化
        states = [
            create_demo_game_state(),
            # 状态变化1: 玩家使用法术
            {
                "player": {
                    "health": 25, "max_health": 30, "mana": 2, "max_mana": 6,
                    "hand_count": 3, "field_count": 2
                },
                "opponent": {
                    "health": 12, "max_health": 30, "mana": 4, "max_mana": 4,
                    "hand_count": 3, "field_count": 1
                },
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
            # 状态变化2: 出新随从
            {
                "player": {
                    "health": 25, "max_health": 30, "mana": 0, "max_mana": 6,
                    "hand_count": 2, "field_count": 3
                },
                "opponent": {
                    "health": 12, "max_health": 30, "mana": 4, "max_mana": 4,
                    "hand_count": 3, "field_count": 1
                },
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

        for i in range(6):  # 演示6个状态变化
            state = states[i % len(states)]
            ui_manager.update_game_state(state)

            # 在控制台显示当前状态说明
            if i == 0:
                console.print("\n[dim]📋 初始状态[/dim]")
            elif i % 3 == 1:
                console.print("\n[dim]🔥 使用火球术！对手受伤[/dim]")
            elif i % 3 == 2:
                console.print("\n[dim]⚔️ 召唤烈焰元素！[/dim]")

            await asyncio.sleep(2)

    except KeyboardInterrupt:
        console.print("\n[yellow]演示已停止[/yellow]")
    finally:
        ui_manager.stop_rendering()


def demo_responsive_layout():
    """演示响应式布局"""
    console = Console()
    console.print("\n📱 [bold cyan]响应式布局演示[/bold cyan]")
    console.print("=" * 50)

    layout_manager = GameLayout()

    # 测试不同宽度
    widths = [60, 80, 100, 120, 140]

    for width in widths:
        console.print(f"\n🖥️  终端宽度: [bold yellow]{width}[/bold yellow] 列")
        layout_manager.adapt_to_width(width)
        console.print(f"布局模式: [bold green]{layout_manager.layout_mode}[/bold green]")


async def main():
    """主演示函数"""
    console = Console()
    console.print("🎯 [bold magenta]Rich Layout重构演示[/bold magenta]")
    console.print("通过TDD方式开发的新界面系统")
    console.print("=" * 60)

    # 演示1: 静态布局
    demo_static_layout()

    # 演示2: 响应式布局
    demo_responsive_layout()

    # 演示3: 动态刷新
    await demo_live_layout()


if __name__ == "__main__":
    asyncio.run(main())