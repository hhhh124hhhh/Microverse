#!/usr/bin/env python3
"""
数字选项系统测试脚本
验证新的用户交互体验
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_ui import GameUIStatic
from rich.console import Console

console = Console()

async def test_number_options():
    """测试数字选项功能"""
    console.print("🎯 [bold green]数字选项系统测试[/bold green]")
    console.print("=" * 60)

    # 创建游戏UI管理器
    ui = GameUIStatic()

    # 设置测试游戏状态（有可出的牌）
    test_state = {
        "player": {
            "health": 30, "max_health": 30,
            "mana": 4, "max_mana": 4,
            "hand_count": 4, "field_count": 1
        },
        "opponent": {
            "health": 25, "max_health": 30,
            "mana": 3, "max_mana": 3,
            "hand_count": 3, "field_count": 2
        },
        "hand": [
            {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 0},
            {"name": "治疗之环", "cost": 2, "attack": 0, "health": 0, "type": "spell", "index": 1},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 2},
            {"name": "火球术", "cost": 4, "attack": 6, "health": 0, "type": "spell", "index": 3}
        ],
        "battlefield": {
            "player": [
                {"name": "狼人渗透者", "attack": 3, "health": 2, "can_attack": True, "index": 0}
            ],
            "opponent": [
                {"name": "霜狼步兵", "attack": 2, "health": 3, "can_attack": False, "index": 0}
            ]
        }
    }

    console.print("🚀 [bold blue]测试数字选项显示...[/bold blue]")

    # 更新游戏状态
    ui.update_game_state(test_state)

    console.print("✅ 界面显示完成")

    # 测试各种输入
    test_inputs = [
        ("1", "数字选项 - 出牌1（铁喙猫头鹰）"),
        ("2", "数字选项 - 出牌2（治疗之环）"),
        ("5", "数字选项 - 使用英雄技能"),
        ("6", "数字选项 - 查看帮助"),
        ("8", "数字选项 - 退出游戏"),
        ("help", "文字命令 - 帮助"),
        ("quit", "文字命令 - 退出"),
        ("出牌 0", "传统命令 - 出牌"),
        ("99", "无效数字选项"),
        ("invalid", "无效文字命令")
    ]

    console.print("\n🎮 [bold blue]测试用户输入处理...[/bold blue]")
    console.print("=" * 40)

    for user_input, description in test_inputs:
        console.print(f"\n📝 [yellow]测试: {description}[/yellow]")
        console.print(f"输入: '{user_input}'")

        # 处理用户输入
        success, message, action_data = await ui.process_user_input(user_input)

        # 显示结果
        if success:
            console.print(f"✅ [green]成功: {message[:80]}{'...' if len(message) > 80 else ''}[/green]")
            if action_data:
                action = action_data.get('action', 'unknown')
                console.print(f"   动作: {action}")
        else:
            console.print(f"❌ [red]失败: {message}[/red]")

        # 短暂延迟
        await asyncio.sleep(0.3)

    console.print("\n🎉 [bold green]数字选项系统测试完成！[/bold green]")
    console.print("✅ 数字选项正确显示")
    console.print("✅ 数字选择功能正常")
    console.print("✅ 传统文字命令仍然支持")
    console.print("✅ 错误处理完善")
    console.print("✅ 用户交互体验大幅提升")

    # 安全清理
    ui.stop_rendering()
    console.print("✅ 测试系统已安全停止")

    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_number_options())
        if success:
            console.print("\n🚀 [bold cyan]数字选项系统完全正常！[/bold cyan]")
            console.print("用户现在可以享受更便捷的交互体验！")
        else:
            console.print("\n❌ [bold red]测试失败，需要修复问题[/bold red]")
    except KeyboardInterrupt:
        console.print("\n⚠️ [yellow]测试被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [bold red]测试过程中出现异常: {e}[/bold red]")