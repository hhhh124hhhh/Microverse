#!/usr/bin/env python3
"""
测试英雄技能伤害修复效果
"""

import asyncio
from game_ui import GameUIStatic

async def test_hero_power_fix():
    """测试英雄技能伤害修复"""
    print("🧪 测试英雄技能伤害修复...")

    # 创建静态UI实例
    ui = GameUIStatic()

    if not ui.game_engine:
        print("❌ 游戏引擎未加载，无法测试")
        return

    print("✅ 游戏引擎已加载")

    # 初始化游戏状态
    ui.update_game_state()

    # 模拟几个回合以获得足够法力值
    print("\n🔄 模拟前几个回合以获得法力值...")
    for i in range(2):  # 进行2个回合，获得3点法力
        if ui.game_engine:
            result = ui.game_engine.end_turn(0, auto_attack=False)
            if result.get("success"):
                ui.game_engine.end_turn(1, auto_attack=False)
                ui.update_game_state()
                player = ui.game_state.get("player", {})
                print(f"回合 {i+1} 结束，玩家法力值: {player.get('mana', 0)}")

    # 显示初始状态
    print("\n📊 准备测试时的游戏状态:")
    player = ui.game_state.get("player", {})
    opponent = ui.game_state.get("opponent", {})
    print(f"玩家生命值: {player.get('health', 0)}")
    print(f"玩家法力值: {player.get('mana', 0)}")
    print(f"对手生命值: {opponent.get('health', 0)}")

    # 检查是否可以使用英雄技能
    if player.get('mana', 0) >= 2:
        print("\n⚡ 测试使用英雄技能...")

        # 模拟英雄技能使用
        action_data = {'action': 'hero_power'}
        await ui._handle_hero_power_used(action_data)

        # 显示使用技能后的状态
        print("\n📊 使用英雄技能后的状态:")
        updated_player = ui.game_state.get("player", {})
        updated_opponent = ui.game_state.get("opponent", {})
        print(f"玩家生命值: {updated_player.get('health', 0)}")
        print(f"玩家法力值: {updated_player.get('mana', 0)}")
        print(f"对手生命值: {updated_opponent.get('health', 0)}")

        # 验证伤害是否生效
        damage_dealt = opponent.get('health', 0) - updated_opponent.get('health', 0)
        mana_used = player.get('mana', 0) - updated_player.get('mana', 0)

        print(f"\n🔍 验证结果:")
        print(f"造成的伤害: {damage_dealt}点")
        print(f"消耗的法力: {mana_used}点")

        if damage_dealt == 2 and mana_used == 2:
            print("✅ 英雄技能伤害修复成功！")
        else:
            print("❌ 英雄技能伤害修复失败")

        # 检查游戏是否结束
        if ui.game_engine.game_over:
            winner = ui.game_engine.get_winner()
            print(f"🏆 游戏结束，获胜者: {winner}")

    else:
        print("❌ 玩家法力值不足，无法测试英雄技能")

if __name__ == "__main__":
    asyncio.run(test_hero_power_fix())