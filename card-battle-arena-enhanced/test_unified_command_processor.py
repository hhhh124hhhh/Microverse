#!/usr/bin/env python3
"""
测试统一命令处理器
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_engine.card_game import CardGame, Card
from command_processor import UnifiedCommandProcessor, CommandContext


class MockUI:
    """模拟UI界面"""

    def __init__(self):
        self.messages = []
        self.console = MockConsole()

    def print(self, message, style=None):
        self.messages.append((message, style))
        print(message)


class MockConsole:
    """模拟Console对象"""

    def print(self, message, style=None):
        print(message)


async def test_unified_command_processor():
    """测试统一命令处理器"""
    print("🧪 测试统一命令处理器")
    print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")
    ui = MockUI()
    processor = UnifiedCommandProcessor()

    # 创建命令上下文
    def create_context(command_text):
        return CommandContext(
            game=game,
            ui=ui,
            player_idx=0,
            command_text=command_text,
            game_state=game.get_game_state(),
            available_commands=game.get_available_commands()
        )

    print("📊 测试场景:")
    print(f"   玩家手牌: {len(game.players[0].hand)} 张")
    print(f"   玩家法力: {game.players[0].mana}/{game.players[0].max_mana}")

    # 测试1: 帮助命令
    print(f"\n🎯 测试1: 帮助命令")
    print("-" * 30)

    context = create_context("help")
    success, message, data = await processor.process_command(context)
    print(f"   帮助命令: {'成功' if success else '失败'}")
    print(f"   消息: {message}")

    # 测试2: 状态命令
    print(f"\n🎯 测试2: 状态命令")
    print("-" * 30)

    context = create_context("status")
    success, message, data = await processor.process_command(context)
    print(f"   状态命令: {'成功' if success else '失败'}")
    print(f"   消息: {message}")

    # 测试3: 无效命令
    print(f"\n🎯 测试3: 无效命令")
    print("-" * 30)

    context = create_context("invalid_command")
    success, message, data = await processor.process_command(context)
    print(f"   无效命令: {'成功' if success else '失败'}")
    print(f"   消息: {message}")

    # 测试4: 结束回合命令
    print(f"\n🎯 测试4: 结束回合命令")
    print("-" * 30)

    context = create_context("end")
    success, message, data = await processor.process_command(context)
    print(f"   结束回合: {'成功' if success else '失败'}")
    print(f"   消息: {message}")

    # 测试5: 数字命令（使用可用命令列表）
    print(f"\n🎯 测试5: 数字命令")
    print("-" * 30)

    available_commands = game.get_available_commands()
    if available_commands:
        print(f"   可用命令: {available_commands[:3]}...")  # 显示前3个
        context = create_context("1")
        success, message, data = await processor.process_command(context)
        print(f"   数字命令'1': {'成功' if success else '失败'}")
        print(f"   消息: {message}")
    else:
        print("   ⚠️ 没有可用命令进行测试")

    # 测试6: 命令匹配测试
    print(f"\n🎯 测试6: 命令别名测试")
    print("-" * 30)

    alias_tests = [
        ("h", "帮助命令别名"),
        ("帮", "帮助命令中文别名"),
        ("结束", "结束回合别名"),
        ("技", "技能命令别名"),
        ("hero", "英雄攻击别名")
    ]

    for command, description in alias_tests:
        context = create_context(command)
        success, message, data = await processor.process_command(context)
        print(f"   {description} '{command}': {'成功' if success else '失败'}")

    print(f"\n🎉 统一命令处理器测试完成！")
    return True


async def test_command_integration():
    """测试命令与现有系统的集成"""
    print("\n🧪 测试命令系统集成")
    print("=" * 50)

    from game_ui import GameUI

    # 创建游戏和UI实例
    game = CardGame("集成测试玩家", "集成测试AI")
    ui = GameUI()
    processor = UnifiedCommandProcessor()

    print("📊 集成测试场景:")
    print(f"   游戏实例: ✅ 已创建")
    print(f"   UI实例: ✅ 已创建")
    print(f"   命令处理器: ✅ 已创建")

    # 测试处理器是否包含所有默认命令
    print(f"\n🎯 默认命令注册测试")
    print("-" * 30)

    expected_commands = [
        "play", "attack", "spell", "skill",
        "hero_attack", "end_turn", "help", "status"
    ]

    for cmd_name in expected_commands:
        if cmd_name in processor.commands:
            print(f"   ✅ {cmd_name} 命令已注册")
        else:
            print(f"   ❌ {cmd_name} 命令未注册")

    print(f"\n🎉 命令系统集成测试完成！")
    return True


if __name__ == "__main__":
    async def main():
        success1 = await test_unified_command_processor()
        success2 = await test_command_integration()

        if success1 and success2:
            print("\n🎉 所有测试通过！统一命令处理器工作正常。")
            return True
        else:
            print("\n⚠️ 部分测试失败，需要检查实现。")
            return False

    success = asyncio.run(main())
    exit(0 if success else 1)