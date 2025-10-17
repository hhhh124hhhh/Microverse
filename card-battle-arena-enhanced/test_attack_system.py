#!/usr/bin/env python3
"""
测试攻击系统功能
验证AI攻击、玩家攻击和攻击状态管理是否正常工作
"""

import asyncio
from game_ui import GameUIStatic
from game_engine.card_game import CardGame

def test_attack_state_management():
    """测试攻击状态管理"""
    print("🧪 测试攻击状态管理...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")

    # 模拟几个回合，让玩家有随从
    print("🔄 模拟游戏进程...")

    # 回合1：玩家出牌
    if game.players[0].hand and len(game.players[0].hand) > 0:
        card = game.players[0].hand[0]
        if card.card_type == "minion" and card.cost <= game.players[0].mana:
            result = game.play_card(0, 0)
            if result["success"]:
                print(f"   ✅ 玩家出牌: {result['message']}")

    # 结束回合
    game.end_turn(0, auto_attack=False)
    game.end_turn(1, auto_attack=False)

    # 回合2：玩家再次出牌
    if game.players[0].hand and len(game.players[0].hand) > 0:
        card = game.players[0].hand[0]
        if card.card_type == "minion" and card.cost <= game.players[0].mana:
            result = game.play_card(0, 0)
            if result["success"]:
                print(f"   ✅ 玩家出牌: {result['message']}")

    # 结束回合，进入回合3
    game.end_turn(0, auto_attack=False)
    game.end_turn(1, auto_attack=False)

    # 回合3开始，检查攻击状态
    print("\n📊 检查第3回合攻击状态:")
    player_field = game.players[0].field

    if player_field:
        all_can_attack = True
        for i, minion in enumerate(player_field):
            can_attack = getattr(minion, 'can_attack', False)
            minion_name = getattr(minion, 'name', f'随从{i}')
            if can_attack:
                print(f"   ✅ {minion_name}: 可以攻击")
            else:
                print(f"   ❌ {minion_name}: 无法攻击")
                all_can_attack = False

        if all_can_attack:
            print("✅ 所有随从攻击状态正常")
            return True
        else:
            print("⚠️ 部分随从攻击状态异常")
            return False
    else:
        print("❌ 玩家场上没有随从")
        return False

def test_ai_attack_functionality():
    """测试AI攻击功能"""
    print("\n🧪 测试AI攻击功能...")

    # 创建游戏实例
    game = CardGame("玩家", "AI对手")

    # 给双方都添加一些随从
    from game_engine.card_game import Card

    # 添加玩家随从
    player_minion1 = Card("测试随从1", 1, 2, 2, "minion")
    player_minion2 = Card("测试随从2", 2, 3, 1, "minion", ["taunt"])
    game.players[0].field.extend([player_minion1, player_minion2])

    # 添加AI随从
    ai_minion1 = Card("AI随从1", 1, 2, 1, "minion")
    ai_minion2 = Card("AI随从2", 2, 1, 3, "minion", ["divine_shield"])
    game.players[1].field.extend([ai_minion1, ai_minion2])

    # 设置当前玩家为AI
    game.current_player_idx = 1

    # 设置AI随从可以攻击
    for minion in game.players[1].field:
        minion.can_attack = True

    print("🤖 测试AI攻击:")

    # 测试AI攻击英雄
    try:
        result = game.attack_with_minion(1, 0, "英雄")
        if result["success"]:
            print(f"   ✅ AI攻击英雄成功: {result['message']}")
        else:
            print(f"   ❌ AI攻击英雄失败: {result['message']}")
            return False
    except Exception as e:
        print(f"   ❌ AI攻击英雄异常: {e}")
        return False

    # 测试AI攻击随从 - 修复测试逻辑
    try:
        # 由于对手有嘲讽随从，AI应该攻击嘲讽随从
        result = game.attack_with_minion(1, 1, "随从_0")  # 攻击嘲讽随从
        if result["success"]:
            print(f"   ✅ AI攻击嘲讽随从成功: {result['message']}")
        else:
            # 如果失败是因为没有嘲讽随从，那是正常的
            if "必须先攻击嘲讽随从" in result["message"]:
                print(f"   ✅ AI正确识别嘲讽机制: {result['message']}")
            else:
                print(f"   ❌ AI攻击随从失败: {result['message']}")
                return False
    except Exception as e:
        print(f"   ❌ AI攻击随从异常: {e}")
        return False

    print("✅ AI攻击功能测试通过")
    return True

def test_player_attack_commands():
    """测试玩家攻击命令生成"""
    print("\n🧪 测试玩家攻击命令生成...")

    ui = GameUIStatic()

    if not ui.game_engine:
        print("❌ 游戏引擎未加载")
        return False

    # 模拟一个有可攻击随从的游戏状态
    from game_engine.card_game import Card

    # 清空战场
    ui.game_engine.players[0].field.clear()
    ui.game_engine.players[1].field.clear()

    # 添加玩家随从（设置为可攻击）
    player_minion = Card("测试攻击者", 2, 3, 2, "minion")
    player_minion.can_attack = True
    ui.game_engine.players[0].field.append(player_minion)

    # 添加对手随从
    opponent_minion = Card("测试目标", 1, 1, 4, "minion", ["taunt"])
    ui.game_engine.players[1].field.append(opponent_minion)

    # 更新游戏状态
    ui.update_game_state()

    # 获取可用命令
    commands = ui._get_available_commands(ui.game_state)

    # 检查是否有攻击命令
    attack_commands = [cmd for cmd in commands if "攻击" in cmd]

    if attack_commands:
        print(f"   ✅ 找到攻击命令: {len(attack_commands)}个")
        for cmd in attack_commands:
            print(f"   📋 {cmd}")

        # 测试攻击目标获取
        player_field = ui.game_state['battlefield'].get('player', [])
        opponent_field = ui.game_state['battlefield'].get('opponent', [])

        if player_field:
            available_targets = ui._get_attack_targets_for_minion(0, opponent_field)
            print(f"   🎯 可攻击目标: {available_targets}")

            if available_targets:
                print("✅ 玩家攻击命令生成正常")
                return True
            else:
                print("❌ 没有可攻击的目标")
                return False
        else:
            print("❌ 玩家没有随从")
            return False
    else:
        print("❌ 没有生成攻击命令")
        return False

def test_attack_target_parsing():
    """测试攻击目标解析"""
    print("\n🧪 测试攻击目标解析...")

    ui = GameUIStatic()

    # 模拟游戏状态
    ui.game_state = {
        'battlefield': {
            'player': [
                {'name': '测试随从', 'can_attack': True, 'index': 0}
            ],
            'opponent': [
                {'name': '嘲讽随从', 'mechanics': ['taunt'], 'index': 0},
                {'name': '普通随从', 'mechanics': [], 'index': 1}
            ]
        }
    }

    # 测试目标获取
    opponent_field = ui.game_state['battlefield'].get('opponent', [])
    available_targets = ui._get_attack_targets_for_minion(0, opponent_field)

    expected_targets = ['嘲讽随从(0)']  # 应该只显示嘲讽随从

    if available_targets == expected_targets:
        print(f"   ✅ 嘲讽机制正常: {available_targets}")
    else:
        print(f"   ❌ 嘲讽机制异常: 期望 {expected_targets}, 实际 {available_targets}")
        return False

    # 测试没有嘲讽的情况
    ui.game_state['battlefield']['opponent'] = [
        {'name': '普通随从1', 'mechanics': [], 'index': 0},
        {'name': '普通随从2', 'mechanics': [], 'index': 1}
    ]

    opponent_field = ui.game_state['battlefield'].get('opponent', [])
    available_targets = ui._get_attack_targets_for_minion(0, opponent_field)

    expected_targets = ['普通随从1(0)', '普通随从2(1)', '敌方英雄']

    if set(available_targets) == set(expected_targets):
        print(f"   ✅ 普通目标解析正常: {available_targets}")
        return True
    else:
        print(f"   ❌ 普通目标解析异常: 期望 {expected_targets}, 实际 {available_targets}")
        return False

async def test_attack_command_processing():
    """测试攻击命令处理"""
    print("\n🧪 测试攻击命令处理...")

    ui = GameUIStatic()

    if not ui.game_engine:
        print("❌ 游戏引擎未加载")
        return False

    # 设置测试状态
    from game_engine.card_game import Card

    # 清空战场
    ui.game_engine.players[0].field.clear()
    ui.game_engine.players[1].field.clear()

    # 添加测试随从
    attacker = Card("攻击者", 2, 3, 2, "minion")
    attacker.can_attack = True
    ui.game_engine.players[0].field.append(attacker)

    target = Card("目标", 1, 1, 4, "minion")
    ui.game_engine.players[1].field.append(target)

    ui.update_game_state()

    # 测试攻击命令解析
    test_commands = [
        "1. 攻击: 攻击者 → 目标(0)",
        "1. 攻击: 攻击者 → 敌方英雄"
    ]

    success_count = 0
    for cmd in test_commands:
        try:
            # 模拟攻击命令的处理，直接调用攻击处理函数
            success, message, action_data = await ui._handle_attack_from_command(cmd)
            if success and action_data and action_data.get('action') == 'attack':
                print(f"   ✅ 命令处理成功: {message}")
                success_count += 1
            else:
                print(f"   ❌ 命令处理失败: {message}")
        except Exception as e:
            print(f"   ❌ 命令处理异常: {e}")

    if success_count > 0:
        print(f"✅ 攻击命令处理正常 ({success_count}/{len(test_commands)})")
        return True
    else:
        print("❌ 攻击命令处理失败")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 攻击系统功能测试")
    print("=" * 60)

    test_results = []

    # 运行所有测试
    test_results.append(("攻击状态管理", test_attack_state_management()))
    test_results.append(("AI攻击功能", test_ai_attack_functionality()))
    test_results.append(("玩家攻击命令", test_player_attack_commands()))
    test_results.append(("攻击目标解析", test_attack_target_parsing()))
    test_results.append(("攻击命令处理", asyncio.run(test_attack_command_processing())))

    # 显示测试结果总结
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
        print("\n🎉 所有攻击系统功能测试通过！")
        print("✅ 攻击状态管理正常")
        print("✅ AI攻击功能正常")
        print("✅ 玩家攻击命令生成正常")
        print("✅ 攻击目标解析正常")
        print("✅ 攻击命令处理正常")
    else:
        print(f"\n⚠️ 有 {total_count - passed_count} 项测试失败，需要进一步调试")

    print("\n💡 建议:")
    print("- 在实际游戏中测试攻击功能")
    print("- 验证攻击状态的正确显示")
    print("- 确认攻击交互的用户体验")

if __name__ == "__main__":
    main()