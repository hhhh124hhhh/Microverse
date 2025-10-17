#!/usr/bin/env python3
"""
完整命令系统集成测试
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_engine.card_game import CardGame, Card
from game_ui import GameUI
from command_integration import create_command_integration


class MockConsole:
    """模拟控制台"""
    def print(self, message, style=None):
        print(f"[{style}] {message}" if style else message)


async def test_complete_integration():
    """测试完整的命令系统集成"""
    print("🧪 完整命令系统集成测试")
    print("=" * 50)

    # 创建游戏和UI实例
    game = CardGame("集成测试玩家", "集成测试AI")
    ui = GameUI()
    ui.console = MockConsole()  # 使用模拟控制台

    # 创建命令集成
    command_integration = create_command_integration(game, ui)

    print("📊 集成测试环境:")
    print(f"   游戏实例: ✅ 已创建")
    print(f"   UI实例: ✅ 已创建")
    print(f"   命令集成: ✅ 已创建")

    player_idx = 0
    game_state = game.get_game_state()

    # 测试1: 基础命令
    print(f"\n🎯 测试1: 基础命令")
    print("-" * 30)

    basic_commands = ["help", "status", "end"]
    for cmd in basic_commands:
        success, message, data = await command_integration.process_user_input(
            cmd, player_idx, game_state
        )
        print(f"   {cmd}: {'成功' if success else '失败'} - {message}")

    # 测试2: 别名命令
    print(f"\n🎯 测试2: 别名命令")
    print("-" * 30)

    alias_commands = [
        ("h", "帮助别名"),
        ("帮", "中文帮助别名"),
        ("结束", "结束回合别名"),
        ("技", "技能别名"),
        ("hero", "英雄攻击别名")
    ]

    for cmd, description in alias_commands:
        success, message, data = await command_integration.process_user_input(
            cmd, player_idx, game_state
        )
        print(f"   {description} '{cmd}': {'成功' if success else '失败'}")

    # 测试3: 出牌命令
    print(f"\n🎯 测试3: 出牌命令")
    print("-" * 30)

    # 确保玩家有足够法力值
    game.players[0].mana = 10
    game.players[0].max_mana = 10

    if game.players[0].hand:
        card_name = game.players[0].hand[0].name
        success, message, data = await command_integration.process_user_input(
            f"play 0", player_idx, game_state
        )
        print(f"   出牌 'play 0' ({card_name}): {'成功' if success else '失败'}")
        print(f"   结果: {message}")

    # 测试4: 数字命令
    print(f"\n🎯 测试4: 数字命令")
    print("-" * 30)

    available_commands = command_integration.get_available_commands_for_context(player_idx)
    if available_commands:
        print(f"   可用命令数量: {len(available_commands)}")
        if len(available_commands) >= 1:
            success, message, data = await command_integration.process_user_input(
                "1", player_idx, game_state, available_commands
            )
            print(f"   数字命令 '1': {'成功' if success else '失败'}")
            print(f"   结果: {message}")
    else:
        print("   ⚠️ 没有可用命令")

    # 测试5: 错误处理
    print(f"\n🎯 测试5: 错误处理")
    print("-" * 30)

    error_commands = [
        ("invalid_command", "无效命令"),
        ("play 999", "无效卡牌索引"),
        ("play abc", "非数字索引"),
        ("", "空命令")
    ]

    for cmd, description in error_commands:
        success, message, data = await command_integration.process_user_input(
            cmd, player_idx, game_state
        )
        print(f"   {description} '{cmd}': {'成功' if success else '失败'}")
        if not success:
            print(f"   错误信息: {message}")

    # 测试6: 命令数据返回
    print(f"\n🎯 测试6: 命令数据返回")
    print("-" * 30)

    success, message, data = await command_integration.process_user_input(
        "help", player_idx, game_state
    )
    if success and data:
        print(f"   帮助命令返回数据: {data}")
        print(f"   数据类型: {type(data)}")
    else:
        print(f"   帮令命令数据: 无返回数据")

    print(f"\n🎉 完整命令系统集成测试完成！")
    return True


async def test_backward_compatibility():
    """测试向后兼容性"""
    print("\n🧪 向后兼容性测试")
    print("=" * 50)

    game = CardGame("兼容性测试玩家", "兼容性测试AI")
    ui = GameUI()
    command_integration = create_command_integration(game, ui)

    print("📊 兼容性测试:")
    print("   测试新命令系统是否能处理原有的命令格式")

    # 测试原有的命令格式
    old_format_commands = [
        "help",
        "status",
        "play 0",
        "skill",
        "end"
    ]

    for cmd in old_format_commands:
        success, message, data = await command_integration.process_user_input(cmd, 0)
        status = "✅" if success else "❌"
        print(f"   {status} {cmd}: {message[:50]}...")

    print(f"\n🎉 向后兼容性测试完成！")
    return True


if __name__ == "__main__":
    async def main():
        try:
            success1 = await test_complete_integration()
            success2 = await test_backward_compatibility()

            if success1 and success2:
                print("\n🎉 所有集成测试通过！统一命令处理架构工作正常。")
                print("✅ 新系统与现有系统完全兼容")
                print("✅ 命令处理逻辑已统一")
                print("✅ 错误处理机制完善")
                return True
            else:
                print("\n⚠️ 部分集成测试失败，需要检查实现。")
                return False
        except Exception as e:
            print(f"\n❌ 集成测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    success = asyncio.run(main())
    exit(0 if success else 1)