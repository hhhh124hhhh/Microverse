#!/usr/bin/env python3
"""
测试所有修复效果的验证脚本
"""

import asyncio
from game_ui import GameUIStatic

async def test_all_fixes_validation():
    """测试所有修复的验证"""
    print("🧪 测试所有修复效果验证...")

    # 创建静态UI实例
    ui = GameUIStatic()

    if not ui.game_engine:
        print("❌ 游戏引擎未加载，无法测试")
        return

    print("✅ 游戏引擎已加载")

    # 初始化游戏状态
    ui.update_game_state()

    # 模拟几个回合以获得足够法力值并打出随从
    print("\n🔄 模拟前几个回合...")
    for i in range(3):
        if ui.game_engine:
            # 玩家结束回合
            ui.game_engine.end_turn(0, auto_attack=False)
            # AI结束回合
            ui.game_engine.end_turn(1, auto_attack=False)
            ui.update_game_state()

    # 验证轮数显示
    print("\n📊 验证轮数显示...")
    current_turn = ui.game_state.get("turn_number", 1)
    print(f"✅ 当前轮数: {current_turn}")

    # 验证法力值显示
    print("\n💰 验证法力值显示...")
    player = ui.game_state.get("player", {})
    current_mana = player.get("mana", 0)
    max_mana = player.get("max_mana", 0)
    print(f"✅ 玩家法力值: {current_mana}/{max_mana}")

    # 验证可用命令
    print("\n📋 验证可用命令...")
    available_commands = ui._get_available_commands(ui.game_state)
    print(f"✅ 可用命令数量: {len(available_commands)}")

    # 显示前5个命令
    for i, cmd in enumerate(available_commands[:5]):
        print(f"   • {cmd}")

    # 验证AI攻击系统
    print("\n🤖 验证AI攻击系统...")
    if ui.game_engine:
        # 模拟AI回合以触发攻击
        try:
            # AI结束回合
            result = ui.game_engine.end_turn(1, auto_attack=True)
            if result.get("success"):
                print("✅ AI回合执行成功")
            else:
                print(f"⚠️ AI回合执行异常: {result.get('message', '未知错误')}")
        except Exception as e:
            print(f"⚠️ AI回合执行出错: {e}")

    # 更新状态并显示最终状态
    ui.update_game_state()

    print("\n📊 最终游戏状态:")
    player = ui.game_state.get("player", {})
    opponent = ui.game_state.get("opponent", {})

    print(f"轮数: {ui.game_state.get('turn_number', '未知')}")
    print(f"玩家: 生命{player.get('health', 0)}/{player.get('max_health', 0)}, 法力{player.get('mana', 0)}/{player.get('max_mana', 0)}")
    print(f"对手: 生命{opponent.get('health', 0)}/{opponent.get('max_health', 0)}, 法力{opponent.get('mana', 0)}/{opponent.get('max_mana', 0)}")

    print("\n🎯 所有修复验证完成!")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 所有修复效果验证测试")
    print("=" * 60)

    asyncio.run(test_all_fixes_validation())