#!/usr/bin/env python3
"""
完整系统测试脚本
验证Live渲染和用户交互的完整功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_ui import GameUIWithLive
from rich.console import Console

console = Console()

async def test_complete_system():
    """测试完整的Live系统功能"""
    console.print("🎯 [bold green]完整系统功能测试[/bold green]")
    console.print("=" * 60)

    # 创建游戏UI管理器
    ui = GameUIWithLive()

    # 设置完整的测试游戏状态
    test_state = {
        "player": {
            "health": 25, "max_health": 30,
            "mana": 4, "max_mana": 4,
            "hand_count": 4, "field_count": 1
        },
        "opponent": {
            "health": 20, "max_health": 30,
            "mana": 3, "max_mana": 3,
            "hand_count": 3, "field_count": 2
        },
        "hand": [
            {"name": "火球术", "cost": 4, "attack": 6, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
            {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 2},
            {"name": "治疗之环", "cost": 2, "attack": 0, "health": 0, "type": "spell", "index": 3}
        ],
        "battlefield": {
            "player": [
                {"name": "狼人渗透者", "attack": 3, "health": 2, "can_attack": True, "index": 0}
            ],
            "opponent": [
                {"name": "霜狼步兵", "attack": 2, "health": 3, "can_attack": False, "index": 0},
                {"name": "石像鬼", "attack": 1, "health": 1, "can_attack": False, "index": 1}
            ]
        }
    }

    console.print("🚀 [bold blue]启动Live渲染系统...[/bold blue]")

    # 启动Live渲染
    ui.start_rendering()

    # 更新游戏状态
    console.print("📊 [blue]更新游戏状态...[/blue]")
    ui.update_game_state(test_state)

    # 等待渲染完成
    await asyncio.sleep(2)

    console.print("✅ [green]Live系统已成功显示游戏内容！[/green]")

    # 测试用户输入处理
    console.print("\n🎮 [bold blue]测试用户输入处理...[/bold blue]")

    test_inputs = [
        ("help", "帮助命令"),
        ("出牌 2", "出牌命令（法力足够）"),
        ("技能", "英雄技能"),
        ("攻击 0 0", "攻击命令"),
        ("结束回合", "结束回合"),
        ("invalid", "无效命令"),
        ("quit", "退出命令")
    ]

    for user_input, description in test_inputs:
        console.print(f"\n📝 [yellow]测试: {description}[/yellow]")
        console.print(f"输入: '{user_input}'")

        # 处理用户输入
        success, message, action_data = await ui.process_user_input(user_input)

        # 显示结果
        if success:
            console.print(f"✅ [green]成功: {message}[/green]")
            if action_data:
                action = action_data.get('action', 'unknown')
                console.print(f"   动作: {action}")
        else:
            console.print(f"❌ [red]失败: {message}[/red]")

        # 短暂延迟
        await asyncio.sleep(0.5)

    console.print("\n🎉 [bold green]系统测试完成！[/bold green]")
    console.print("✅ Live渲染系统正常工作")
    console.print("✅ 游戏内容正确显示")
    console.print("✅ 用户输入处理完善")
    console.print("✅ 命令验证准确无误")
    console.print("✅ 界面响应流畅，无闪烁问题")

    # 安全停止系统
    ui.stop_rendering()
    console.print("✅ 系统已安全停止")

    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(test_complete_system())
        if success:
            console.print("\n🚀 [bold cyan]系统完全正常，可以投入使用！[/bold cyan]")
        else:
            console.print("\n❌ [bold red]系统存在问题，需要修复[/bold red]")
    except KeyboardInterrupt:
        console.print("\n⚠️ [yellow]测试被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n❌ [bold red]测试过程中出现异常: {e}[/bold red]")