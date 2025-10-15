#!/usr/bin/env python3
"""
Layout集成测试
验证TDD开发的Rich Layout系统工作正常
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_ui import GameLayout, create_player_status_panel, create_hand_cards_table
from rich.console import Console


def test_integration():
    """集成测试"""
    console = Console()
    console.print("🧪 [bold blue]Layout系统集成测试[/bold blue]")
    console.print("=" * 50)

    # 测试1: 基础Layout创建
    console.print("\n📋 测试1: 基础Layout创建")
    try:
        layout = GameLayout()
        console.print("✅ GameLayout创建成功")
        console.print(f"   布局模式: {layout.layout_mode}")
    except Exception as e:
        console.print(f"❌ 失败: {e}")
        return False

    # 测试2: 组件创建
    console.print("\n📋 测试2: 组件创建")
    try:
        # 玩家状态面板
        player_data = {
            "health": 25, "max_health": 30,
            "mana": 6, "max_mana": 6,
            "hand_count": 4, "field_count": 2
        }
        player_panel = create_player_status_panel(player_data)
        console.print("✅ 玩家状态面板创建成功")

        # 手牌表格
        hand_cards = [
            {"name": "火球术", "cost": 4, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1}
        ]
        hand_table = create_hand_cards_table(hand_cards, 6)
        console.print("✅ 手牌表格创建成功")

    except Exception as e:
        console.print(f"❌ 失败: {e}")
        return False

    # 测试3: 布局更新
    console.print("\n📋 测试3: 布局更新")
    try:
        layout.update_player_status(player_data)
        layout.update_hand_area(hand_cards, 6)
        console.print("✅ 布局更新成功")
    except Exception as e:
        console.print(f"❌ 失败: {e}")
        return False

    # 测试4: 完整界面渲染
    console.print("\n📋 测试4: 完整界面渲染")
    try:
        # 添加对手状态
        opponent_data = {
            "health": 18, "max_health": 30,
            "mana": 4, "max_mana": 4,
            "hand_count": 3, "field_count": 1
        }
        layout.update_opponent_status(opponent_data)

        # 添加战场状态
        battlefield = {
            "player": [{"name": "狼人", "attack": 3, "health": 2, "can_attack": True}],
            "opponent": [{"name": "霜狼步兵", "attack": 2, "health": 3, "can_attack": False}]
        }
        layout.update_battlefield_area(battlefield["player"], battlefield["opponent"])

        # 添加命令区域
        layout.update_command_area(["出牌 0-1", "技能", "结束回合"])

        console.print("✅ 完整界面组装成功")

    except Exception as e:
        console.print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 显示最终界面
    console.print("\n🎮 [bold green]最终界面效果:[/bold green]")
    console.print(layout.layout)

    return True


if __name__ == "__main__":
    console = Console()
    success = test_integration()
    if success:
        console.print("\n🎉 [bold green]所有集成测试通过！[/bold green]")
        console.print("✅ TDD开发的Rich Layout系统工作正常")
    else:
        console.print("\n❌ [bold red]集成测试失败[/bold red]")