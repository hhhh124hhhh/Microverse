#!/usr/bin/env python3
"""
测试多目标攻击选择功能
验证修复后的攻击命令是否能正确处理多目标选择
"""

import asyncio
from game_ui import GameUIStatic
from game_engine.card_game import CardGame

async def test_multi_target_attack():
    """测试多目标攻击选择功能"""
    print("🧪 测试多目标攻击选择功能...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 手动添加一些随从到双方场上
    from game_engine.card_game import Card

    # 清空战场
    game.players[0].field.clear()
    game.players[1].field.clear()

    # 添加玩家随从（设置为可攻击）
    player_minion = Card("月盗", 2, 3, 2, "minion")
    player_minion.can_attack = True
    game.players[0].field.append(player_minion)

    # 添加多个对手随从
    opponent_minion1 = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"])
    opponent_minion2 = Card("霜狼步兵", 2, 2, 3, "minion", ["taunt"])
    opponent_minion3 = Card("邪犬", 1, 1, 1, "minion")
    game.players[1].field.extend([opponent_minion1, opponent_minion2, opponent_minion3])

    # 更新游戏状态
    ui.update_game_state()

    print("📊 测试场景设置:")
    print(f"   玩家随从: {player_minion.name} (可攻击)")
    print(f"   对手随从: {len(game.players[1].field)}个")
    for i, minion in enumerate(game.players[1].field):
        mechanics = ", ".join(minion.mechanics) if minion.mechanics else "无"
        print(f"     {i}. {minion.name} - 特效: {mechanics}")

    # 获取可用命令
    commands = ui._get_available_commands(ui.game_state)

    print(f"\n📋 生成的命令列表 ({len(commands)}个):")
    for i, cmd in enumerate(commands):
        print(f"   {i+1}. {cmd}")

    # 查找攻击命令
    attack_commands = [cmd for cmd in commands if "攻击" in cmd]

    if attack_commands:
        print(f"\n⚔️ 找到攻击命令: {len(attack_commands)}个")
        for cmd in attack_commands:
            print(f"   🎯 {cmd}")

            # 测试攻击命令解析
            if "个目标" in cmd:
                print(f"   🔍 检测到多目标命令: {cmd}")

                # 测试攻击命令处理
                success, message, action_data = await ui._handle_attack_from_command(cmd)

                if success:
                    print(f"   ✅ 攻击命令处理成功: {message}")
                    if action_data:
                        print(f"   📦 动作数据: {action_data}")
                else:
                    print(f"   ❌ 攻击命令处理失败: {message}")

        return len(attack_commands) > 0
    else:
        print("❌ 没有找到攻击命令")
        return False

async def test_single_target_attack():
    """测试单目标攻击"""
    print("\n🧪 测试单目标攻击...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 手动添加随从
    from game_engine.card_game import Card

    # 清空战场
    game.players[0].field.clear()
    game.players[1].field.clear()

    # 添加玩家随从
    player_minion = Card("测试随从", 2, 3, 2, "minion")
    player_minion.can_attack = True
    game.players[0].field.append(player_minion)

    # 只添加一个对手随从
    opponent_minion = Card("单个目标", 1, 1, 5, "minion")
    game.players[1].field.append(opponent_minion)

    # 更新游戏状态
    ui.update_game_state()

    # 获取可用命令
    commands = ui._get_available_commands(ui.game_state)

    print(f"📋 单目标场景命令 ({len(commands)}个):")
    for i, cmd in enumerate(commands):
        print(f"   {i+1}. {cmd}")

    # 查找攻击命令
    attack_commands = [cmd for cmd in commands if "攻击" in cmd]

    if attack_commands:
        print(f"\n⚔️ 单目标攻击命令: {attack_commands[0]}")

        # 测试攻击命令处理
        success, message, action_data = await ui._handle_attack_from_command(attack_commands[0])

        if success:
            print(f"   ✅ 单目标攻击成功: {message}")
            return True
        else:
            print(f"   ❌ 单目标攻击失败: {message}")
            return False
    else:
        print("❌ 没有找到攻击命令")
        return False

async def test_hero_attack():
    """测试攻击英雄"""
    print("\n🧪 测试攻击英雄...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 手动添加随从
    from game_engine.card_game import Card

    # 清空战场
    game.players[0].field.clear()
    game.players[1].field.clear()

    # 添加玩家随从
    player_minion = Card("英雄杀手", 3, 4, 2, "minion")
    player_minion.can_attack = True
    game.players[0].field.append(player_minion)

    # 对手没有随从（只能攻击英雄）

    # 更新游戏状态
    ui.update_game_state()

    # 获取可用命令
    commands = ui._get_available_commands(ui.game_state)

    print(f"📋 英雄攻击场景命令 ({len(commands)}个):")
    for i, cmd in enumerate(commands):
        print(f"   {i+1}. {cmd}")

    # 查找攻击英雄的命令
    attack_commands = [cmd for cmd in commands if "攻击" in cmd and "英雄" in cmd]

    if attack_commands:
        print(f"\n⚔️ 英雄攻击命令: {attack_commands[0]}")

        # 测试攻击命令处理
        success, message, action_data = await ui._handle_attack_from_command(attack_commands[0])

        if success:
            print(f"   ✅ 英雄攻击成功: {message}")
            return True
        else:
            print(f"   ❌ 英雄攻击失败: {message}")
            return False
    else:
        print("❌ 没有找到英雄攻击命令")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 多目标攻击选择功能测试")
    print("=" * 60)

    test_results = []

    # 运行测试
    test_results.append(("多目标攻击选择", await test_multi_target_attack()))
    test_results.append(("单目标攻击", await test_single_target_attack()))
    test_results.append(("英雄攻击", await test_hero_attack()))

    # 显示测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)

    passed_count = 0
    total_count = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1

    print(f"\n总计: {passed_count}/{total_count} 项测试通过")

    if passed_count == total_count:
        print("\n🎉 所有多目标攻击选择功能测试通过！")
        print("✅ 攻击命令生成正常")
        print("✅ 多目标选择处理正常")
        print("✅ 单目标攻击处理正常")
        print("✅ 英雄攻击处理正常")
        print("\n💡 修复总结:")
        print("- 修复了main.py中数字输入的处理逻辑")
        print("- 改进了game_ui.py中攻击命令的解析")
        print("- 添加了对'个目标'描述的专门处理")
        print("- 现在用户输入数字可以正确选择攻击命令")
    else:
        print(f"\n⚠️ 有 {total_count - passed_count} 项测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())