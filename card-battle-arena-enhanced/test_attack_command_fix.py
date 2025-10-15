#!/usr/bin/env python3
"""
测试随从攻击命令修复效果
"""

import asyncio
from game_ui import GameUIStatic

async def test_attack_command_fix():
    """测试随从攻击命令修复"""
    print("🧪 测试随从攻击命令修复...")

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

    # 再进行几个回合获得更多法力并打出随从
    print("\n🃏 模拟打出随从...")
    for i in range(2):
        if ui.game_engine:
            # 玩家结束回合
            ui.game_engine.end_turn(0, auto_attack=False)
            # AI结束回合
            ui.game_engine.end_turn(1, auto_attack=False)
            ui.update_game_state()

    # 尝试打出随从牌
    player = ui.game_engine.players[0]
    print(f"\n💰 玩家当前法力: {player.mana}")
    print(f"🃋 玩家手牌数量: {len(player.hand)}")

    # 检查手牌中是否有随从
    for i, card in enumerate(player.hand):
        print(f"手牌 {i}: {card.name} (费用: {card.cost}, 类型: {card.card_type})")
        if card.card_type == "minion" and card.cost <= player.mana:
            print(f"✅ 打出随从: {card.name}")
            result = ui.game_engine.play_card(0, i)
            if result.get("success"):
                print(f"   {result.get('message', '成功')}")
                ui.update_game_state()
                break
            else:
                print(f"   ❌ 出牌失败: {result.get('message', '未知错误')}")

    # 模拟一个完整的回合使随从可以攻击
    print("\n⚔️ 模拟随从获得攻击能力...")
    if ui.game_engine:
        # 玩家结束回合
        ui.game_engine.end_turn(0, auto_attack=False)
        # AI结束回合
        ui.game_engine.end_turn(1, auto_attack=False)
        ui.update_game_state()

    # 显示当前游戏状态
    print("\n📊 当前游戏状态:")
    player = ui.game_engine.players[0]
    print(f"玩家生命值: {player.health}")
    print(f"玩家法力值: {player.mana}")
    print(f"玩家随从数量: {len(player.field)}")

    # 检查是否有可攻击的随从
    attackable_minions = []
    for i, minion in enumerate(player.field):
        can_attack = getattr(minion, 'can_attack', False)
        print(f"随从 {i}: {minion.name} ({minion.attack}/{minion.health}) - {'🗡️ 可攻击' if can_attack else '😴 休眠'}")
        if can_attack:
            attackable_minions.append((i, minion))

    if attackable_minions:
        print(f"\n✅ 找到 {len(attackable_minions)} 个可攻击的随从")

        # 测试攻击命令生成
        available_commands = ui._get_available_commands(ui.game_state)
        print(f"\n📋 可用命令数量: {len(available_commands)}")

        attack_commands = [cmd for cmd in available_commands if "攻击" in cmd]
        print(f"⚔️ 攻击命令数量: {len(attack_commands)}")

        for cmd in attack_commands:
            print(f"   • {cmd}")

        if attack_commands:
            # 测试处理攻击命令
            test_command = attack_commands[0]
            print(f"\n🧪 测试处理命令: {test_command}")

            success, message, action_data = await ui._handle_attack_from_command(test_command)

            if success:
                print(f"✅ 命令处理成功: {message}")
                if action_data:
                    print(f"   动作: {action_data.get('action')}")
                    print(f"   攻击者索引: {action_data.get('attacker_index')}")
                    print(f"   目标: {action_data.get('target')}")
            else:
                print(f"❌ 命令处理失败: {message}")
    else:
        print("\n❌ 没有可攻击的随从")

    print("\n🎯 随从攻击命令修复测试完成!")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 随从攻击命令修复验证")
    print("=" * 60)

    asyncio.run(test_attack_command_fix())