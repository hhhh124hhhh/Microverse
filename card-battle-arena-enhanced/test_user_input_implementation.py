#!/usr/bin/env python3
"""
用户输入功能实现测试
验证TDD实现的UserInputHandler和GameUIWithLive交互功能
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_ui import UserInputHandler, GameUIWithLive
from rich.console import Console

console = Console()

def test_input_handler():
    """测试输入处理器"""
    console.print("🧪 [bold blue]测试1: UserInputHandler功能[/bold blue]")

    handler = UserInputHandler()

    # 测试命令解析
    test_commands = [
        ("出牌 0", ("play_card", 0)),
        ("play 1", ("play_card", 1)),
        ("2", ("play_card", 2)),
        ("技能", ("hero_power", None)),
        ("skill", ("hero_power", None)),
        ("结束回合", ("end_turn", None)),
        ("end turn", ("end_turn", None)),
        ("攻击 0 1", ("attack", (0, 1))),
        ("help", ("help", None)),
        ("退出", ("quit", None)),
        ("invalid", None)
    ]

    console.print("✅ 命令解析测试:")
    for cmd, expected in test_commands:
        success, result = handler.parse_command(cmd)
        if expected is None:
            assert not success, f"命令 '{cmd}' 应该解析失败"
            console.print(f"  ❌ '{cmd}' -> 正确识别为无效命令")
        else:
            assert success and result == expected, f"命令 '{cmd}' 解析错误: 期望 {expected}, 得到 {result}"
            console.print(f"  ✅ '{cmd}' -> {result}")

    # 测试卡牌索引验证
    console.print("\n✅ 卡牌索引验证测试:")
    valid, error = handler.validate_card_index(0, 2)
    assert valid, "索引0应该有效"
    console.print(f"  ✅ 索引0有效")

    valid, error = handler.validate_card_index(3, 2)
    assert not valid, "索引3应该无效"
    console.print(f"  ✅ 索引3无效: {error}")

    # 测试出牌条件检查
    console.print("\n✅ 出牌条件检查测试:")
    can_play, error = handler.can_play_card(2, 3)
    assert can_play, "3点法力应该能出2点费用的牌"
    console.print(f"  ✅ 3法力出2费牌: 可以")

    can_play, error = handler.can_play_card(4, 3)
    assert not can_play, "3点法力不能出4点费用的牌"
    console.print(f"  ✅ 3法力出4费牌: 不可以 - {error}")

    console.print("\n✅ UserInputHandler所有测试通过！")
    return True

async def test_game_ui_interactive():
    """测试GameUIWithLive交互功能"""
    console.print("\n🧪 [bold blue]测试2: GameUIWithLive交互功能[/bold blue]")

    ui = GameUIWithLive()

    # 创建测试游戏状态
    test_state = {
        "player": {
            "health": 25, "max_health": 30,
            "mana": 4, "max_mana": 4,
            "hand_count": 3, "field_count": 1
        },
        "opponent": {
            "health": 20, "max_health": 30,
            "mana": 3, "max_mana": 3,
            "hand_count": 4, "field_count": 2
        },
        "hand": [
            {"name": "火球术", "cost": 4, "attack": 6, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
            {"name": "铁喙猫头鹰", "cost": 2, "attack": 2, "health": 2, "type": "minion", "index": 2}
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

    # 更新游戏状态
    ui.update_game_state(test_state)

    console.print("✅ 游戏状态更新完成")

    # 测试各种用户输入
    test_inputs = [
        ("help", "帮助命令"),
        ("出牌 0", "出牌命令（法力足够）"),
        ("出牌 1", "出牌命令（法力足够）"),
        ("出牌 5", "出牌命令（无效索引）"),
        ("技能", "英雄技能"),
        ("攻击 0 0", "攻击命令"),
        ("攻击 0 2", "攻击敌方英雄"),
        ("结束回合", "结束回合"),
        ("invalid", "无效命令")
    ]

    console.print("\n✅ 用户输入处理测试:")
    for user_input, description in test_inputs:
        success, message, action_data = await ui.process_user_input(user_input)
        console.print(f"  {description}:")
        console.print(f"    输入: '{user_input}'")
        console.print(f"    结果: {'✅ 成功' if success else '❌ 失败'}")
        console.print(f"    消息: {message[:60]}{'...' if len(message) > 60 else ''}")
        if action_data:
            console.print(f"    动作: {action_data.get('action', 'unknown')}")

    # 测试游戏状态验证
    console.print("\n✅ 游戏状态验证测试:")

    # 测试法力不足的情况
    low_mana_state = test_state.copy()
    low_mana_state["player"]["mana"] = 1
    ui.update_game_state(low_mana_state)

    success, message, action_data = await ui.process_user_input("出牌 0")
    assert not success, "法力不足时出牌应该失败"
    console.print(f"  ✅ 法力不足出牌: 正确拒绝 - {message}")

    # 测试没有随从时的攻击
    empty_field_state = test_state.copy()
    empty_field_state["battlefield"]["player"] = []
    ui.update_game_state(empty_field_state)

    success, message, action_data = await ui.process_user_input("攻击 0 0")
    assert not success, "没有随从时攻击应该失败"
    console.print(f"  ✅ 无随从攻击: 正确拒绝 - {message}")

    console.print("\n✅ GameUIWithLive交互功能测试通过！")
    return True

def test_error_handling():
    """测试错误处理"""
    console.print("\n🧪 [bold blue]测试3: 错误处理机制[/bold blue]")

    handler = UserInputHandler()

    # 测试各种错误消息格式
    error_tests = [
        ('invalid_command', '', '未知命令'),
        ('invalid_card', '索引超出范围', '无效卡牌选择'),
        ('insufficient_mana', '需要4点法力', '法力不足'),
        ('cannot_attack', '随从休眠', '无法攻击')
    ]

    console.print("✅ 错误消息格式测试:")
    for error_type, details, description in error_tests:
        message = handler.format_error_message(error_type, details)
        # invalid_command 使用 ❓ 符号，其他使用 ❌
        expected_symbol = '❓' if error_type == 'invalid_command' else '❌'
        assert expected_symbol in message, f"错误消息应该包含{expected_symbol}符号: {message}"
        console.print(f"  ✅ {description}: {message[:40]}{'...' if len(message) > 40 else ''}")

    console.print("\n✅ 错误处理机制测试通过！")
    return True

async def run_user_input_implementation_tests():
    """运行用户输入实现测试"""
    console.print("🎯 [bold green]用户输入功能实现测试套件[/bold green]")
    console.print("=" * 60)

    tests = [
        ("UserInputHandler功能", test_input_handler),
        ("GameUIWithLive交互功能", test_game_ui_interactive),
        ("错误处理机制", test_error_handling)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            console.print(f"\n🔍 执行测试: {test_name}")
            if asyncio.iscoroutinefunction(test_func):
                # 异步测试
                result = await test_func()
            else:
                # 同步测试
                result = test_func()

            if result:
                passed += 1
                console.print(f"✅ {test_name} - 通过")
            else:
                console.print(f"❌ {test_name} - 失败")

        except Exception as e:
            console.print(f"❌ {test_name} - 异常: {e}")

    console.print(f"\n📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        console.print("🎉 [bold green]所有用户输入功能测试通过！[/bold green]")
        console.print("✅ 输入验证正常工作")
        console.print("✅ 命令解析准确无误")
        console.print("✅ 错误处理机制完善")
        console.print("✅ 游戏状态验证有效")
        return True
    else:
        console.print("❌ [bold red]部分测试失败[/bold red]")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_user_input_implementation_tests())

    if success:
        console.print("\n🚀 [bold cyan]下一步：集成到主菜单模式[/bold cyan]")
        console.print("• 在main.py中启用交互式游戏循环")
        console.print("• 连接真实的游戏引擎")
        console.print("• 实现完整的游戏流程")
    else:
        console.print("\n❌ 需要修复用户输入功能问题")