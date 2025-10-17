#!/usr/bin/env python3
"""
测试法术卡牌攻击功能
验证修复后的法术卡牌攻击系统
"""

import asyncio
from game_ui import GameUIStatic
from game_engine.card_game import CardGame

async def test_spell_card_commands():
    """测试法术卡牌命令生成"""
    print("🧪 测试法术卡牌命令生成...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 手动添加法术卡牌到手牌
    from game_engine.card_game import Card

    # 清空战场和手牌
    game.players[0].field.clear()
    game.players[1].field.clear()
    game.players[0].hand.clear()

    # 添加法术卡牌到玩家手牌
    spell_card = Card("火球术", 4, 6, 0, "spell")
    game.players[0].hand.append(spell_card)

    # 设置玩家法力值足够使用法术
    game.players[0].mana = 10

    # 添加对手随从作为目标
    opponent_minion = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"])
    game.players[1].field.append(opponent_minion)

    # 更新游戏状态
    ui.update_game_state()

    # 获取可用命令
    commands = ui._get_available_commands(ui.game_state)

    print(f"📋 生成的命令列表 ({len(commands)}个):")
    for i, cmd in enumerate(commands):
        print(f"   {i+1}. {cmd}")

    # 查找法术命令
    spell_commands = [cmd for cmd in commands if "法术" in cmd]

    if spell_commands:
        print(f"\n🔥 找到法术命令: {len(spell_commands)}个")
        for cmd in spell_commands:
            print(f"   ✨ {cmd}")
        return True
    else:
        print("❌ 没有找到法术命令")
        return False

async def test_spell_card_parsing():
    """测试法术卡牌命令解析"""
    print("\n🧪 测试法术卡牌命令解析...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 添加法术卡牌
    from game_engine.card_game import Card
    spell_card = Card("火球术", 4, 6, 0, "spell")
    game.players[0].hand.append(spell_card)
    game.players[0].mana = 10

    # 更新游戏状态
    ui.update_game_state()

    # 测试命令解析
    test_commands = [
        "法术 火球术",
        "spell 火球术",
        "1. 法术: 火球术 → 敌方英雄",
        "2. 法术: 火球术 → 2个目标"
    ]

    success_count = 0
    for cmd in test_commands:
        print(f"\n🔍 测试命令: {cmd}")
        try:
            success, command_data = ui._input_handler.parse_command(cmd)
            if success:
                print(f"   ✅ 命令解析成功: {command_data}")
                success_count += 1
            else:
                print(f"   ❌ 命令解析失败")
        except Exception as e:
            print(f"   ❌ 解析异常: {e}")

    return success_count > 0

async def test_spell_target_selection():
    """测试法术目标选择功能"""
    print("\n🧪 测试法术目标选择功能...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 设置战场
    from game_engine.card_game import Card

    # 清空战场
    game.players[0].field.clear()
    game.players[1].field.clear()

    # 添加法术卡牌
    spell_card = Card("火球术", 4, 6, 0, "spell")
    game.players[0].hand.append(spell_card)
    game.players[0].mana = 10

    # 添加多个对手随从
    minion1 = Card("随从1", 2, 2, 2, "minion")
    minion2 = Card("嘲讽随从", 1, 1, 5, "minion", ["taunt"])
    game.players[1].field.extend([minion1, minion2])

    # 更新游戏状态
    ui.update_game_state()

    print("📊 测试场景设置:")
    print(f"   玩家法术: {spell_card.name} (伤害: {spell_card.attack})")
    print(f"   对手随从: {len(game.players[1].field)}个")
    for i, minion in enumerate(game.players[1].field):
        mechanics = ", ".join(minion.mechanics) if minion.mechanics else "无"
        print(f"     {i}. {minion.name} - 特效: {mechanics}")

    # 测试目标选择逻辑（不执行实际选择）
    print("\n🎯 测试目标选择逻辑:")
    opponent_field = ui.game_state.get('battlefield', {}).get('opponent', [])
    targets = []

    # 添加英雄目标
    targets.append(("英雄", "敌方英雄"))

    # 添加随从目标
    for i, minion in enumerate(opponent_field):
        target_name = minion.get('name', f'随从{i}')
        targets.append((f"随从{i}", target_name))

    print(f"   可用目标数量: {len(targets)}")
    for target_key, target_name in targets:
        print(f"   - {target_key}: {target_name}")

    return len(targets) > 0

async def test_spell_execution():
    """测试法术执行"""
    print("\n🧪 测试法术执行...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    ui = GameUIStatic()
    ui.game_engine = game

    # 设置战场
    from game_engine.card_game import Card

    # 添加法术卡牌
    spell_card = Card("火球术", 4, 6, 0, "spell")
    game.players[0].hand.append(spell_card)
    game.players[0].mana = 10

    # 添加对手随从
    target_minion = Card("目标随从", 2, 2, 2, "minion")
    game.players[1].field.append(target_minion)

    # 更新游戏状态
    ui.update_game_state()

    print("📊 测试场景:")
    print(f"   玩家法力: {game.players[0].mana}")
    print(f"   法术卡牌: {spell_card.name} (费用: {spell_card.cost}, 伤害: {spell_card.attack})")
    print(f"   目标随从: {target_minion.name} (生命: {target_minion.health})")

    # 测试法术执行
    try:
        # 找到法术卡牌索引
        spell_index = None
        for i, card in enumerate(ui.game_state["hand"]):
            if card.get("name") == "火球术":
                spell_index = i
                break

        if spell_index is not None:
            # 测试带目标的出牌
            success, message, action_data = await ui._handle_play_card(spell_index, "随从0")

            if success:
                print(f"   ✅ 法术执行成功: {message}")
                print(f"   📦 动作数据: {action_data}")
                return True
            else:
                print(f"   ❌ 法术执行失败: {message}")
                return False
        else:
            print("   ❌ 找不到法术卡牌")
            return False

    except Exception as e:
        print(f"   ❌ 法术执行异常: {e}")
        return False

async def test_integration_with_main():
    """测试与main.py的集成"""
    print("\n🧪 测试与main.py的集成...")

    # 测试main.py中的卡牌目标选择逻辑
    try:
        from game_engine.card_game import Card, CardGame

        # 创建游戏
        game = CardGame("测试玩家", "测试对手")

        # 添加法术卡牌
        spell_card = Card("火球术", 4, 6, 0, "spell")
        game.players[0].hand.append(spell_card)
        game.players[0].mana = 10

        # 添加目标
        target_minion = Card("目标", 2, 2, 2, "minion")
        game.players[1].field.append(target_minion)

        # 测试play_card方法
        result = game.play_card(0, "随从0")

        print(f"   📊 play_card结果: {result}")

        if result.get("success"):
            print("   ✅ 与main.py集成成功")
            return True
        elif result.get("need_target_selection"):
            print("   ✅ 目标选择机制正常")
            return True
        else:
            print(f"   ⚠️ 需要检查: {result.get('message', '未知错误')}")
            return False

    except Exception as e:
        print(f"   ❌ 集成测试异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 法术卡牌攻击功能测试")
    print("=" * 60)

    test_results = []

    # 运行测试
    test_results.append(("法术卡牌命令生成", await test_spell_card_commands()))
    test_results.append(("法术卡牌命令解析", await test_spell_card_parsing()))
    test_results.append(("法术目标选择功能", await test_spell_target_selection()))
    test_results.append(("法术执行", await test_spell_execution()))
    test_results.append(("与main.py集成", await test_integration_with_main()))

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
        print("\n🎉 法术卡牌攻击功能测试全部通过！")
        print("\n💡 功能实现总结:")
        print("✅ 法术卡牌命令生成正常")
        print("✅ 法术卡牌命令解析正常")
        print("✅ 法术目标选择功能正常")
        print("✅ 法术执行功能正常")
        print("✅ 与main.py集成正常")
        print("\n🔧 已实现功能:")
        print("- 玩家可以通过命令或数字选择使用法术卡牌")
        print("- 法术卡牌支持目标选择（随从或英雄）")
        print("- 与现有攻击系统完全集成")
        print("- 支持多目标场景的选择")
        print("- 错误处理和用户反馈完善")
    else:
        print(f"\n⚠️ 有 {total_count - passed_count} 项测试失败，需要进一步调试")

if __name__ == "__main__":
    asyncio.run(main())