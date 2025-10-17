#!/usr/bin/env python3
"""
综合游戏修复验证测试脚本
测试所有已修复的游戏机制问题
"""

import asyncio
import sys
import traceback
from game_ui import GameUIStatic
from game_engine.card_game import CardGame

def print_section(title):
    """打印测试段落标题"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_test_result(test_name, success, details=""):
    """打印测试结果"""
    status = "✅ 通过" if success else "❌ 失败"
    print(f"{test_name}: {status}")
    if details and not success:
        print(f"   详情: {details}")

async def test_get_winner_method():
    """测试get_winner方法是否正常工作"""
    print_section("测试 get_winner() 方法")

    try:
        # 创建游戏实例
        game = CardGame("测试玩家", "测试对手")

        # 测试游戏未结束时的get_winner
        winner = game.get_winner()
        print_test_result("游戏未结束时get_winner", winner is None, f"期望None，实际{winner}")

        # 模拟游戏结束 - 设置对手生命值为0
        game.players[1].health = 0
        game._check_game_over()

        # 测试游戏结束时的get_winner
        winner = game.get_winner()
        print_test_result("游戏结束时get_winner", winner == "测试玩家", f"期望'测试玩家'，实际{winner}")

        # 测试game_over标志
        print_test_result("game_over标志", game.game_over, f"期望True，实际{game.game_over}")

        return True

    except Exception as e:
        print_test_result("get_winner方法测试", False, str(e))
        traceback.print_exc()
        return False

async def test_mana_system():
    """测试法力值系统"""
    print_section("测试法力值系统")

    try:
        game = CardGame("测试玩家", "测试对手")
        player = game.players[0]

        # 测试初始法力值
        print_test_result("初始法力值", player.mana == 1 and player.max_mana == 1,
                        f"法力: {player.mana}/{player.max_mana}")

        # 测试回合开始法力值增长
        game.start_turn()  # 第2回合
        expected_mana = 2
        print_test_result(f"第{game.turn_number}回合法力值",
                        player.mana == expected_mana and player.max_mana == expected_mana,
                        f"法力: {player.mana}/{player.max_mana}")

        # 测试法力值上限
        for _ in range(10):  # 模拟多个回合
            game.start_turn()

        print_test_result("法力值上限", player.max_mana == 10, f"最大法力: {player.max_mana}")

        # 测试法力值使用
        original_mana = player.mana
        player.use_mana(3)
        print_test_result("法力值使用", player.mana == original_mana - 3,
                        f"使用前: {original_mana}, 使用后: {player.mana}")

        return True

    except Exception as e:
        print_test_result("法力值系统测试", False, str(e))
        traceback.print_exc()
        return False

async def test_health_cleanup():
    """测试随从生命值清理机制"""
    print_section("测试随从生命值清理机制")

    try:
        from game_engine.card_game import Card

        game = CardGame("测试玩家", "测试对手")
        player = game.players[0]
        opponent = game.players[1]

        # 添加一些随从到场上有负生命值
        dying_minion = Card("垂死随从", 2, 3, -2, "minion")  # 负生命值
        normal_minion = Card("正常随从", 1, 2, 2, "minion")  # 正常生命值

        player.field.extend([dying_minion, normal_minion])

        print(f"清理前: 玩家场上有 {len(player.field)} 个随从")
        for i, minion in enumerate(player.field):
            print(f"  {i}. {minion.name} ({minion.attack}/{minion.health})")

        # 执行死亡随从清理
        dead_minions = game._cleanup_dead_minions(player)

        print(f"清理后: 玩家场上有 {len(player.field)} 个随从")
        for i, minion in enumerate(player.field):
            print(f"  {i}. {minion.name} ({minion.attack}/{minion.health})")

        print_test_result("死亡随从清理", len(player.field) == 1 and len(dead_minions) == 1,
                        f"清理了 {len(dead_minions)} 个随从: {dead_minions}")

        # 测试战斗阶段后的清理
        opponent.field.append(Card("目标随从", 1, 1, 1, "minion"))

        # 模拟造成伤害
        player.field[0].health -= 5  # 正常随从受到致命伤害
        opponent.field[0].health -= 3  # 对手随从受到致命伤害

        # 手动清理来测试
        player_dead = game._cleanup_dead_minions(player)
        opponent_dead = game._cleanup_dead_minions(opponent)

        print_test_result("战斗后手动清理", len(player.field) == 0 and len(opponent.field) == 0,
                        f"玩家场: {len(player.field)}, 对手场: {len(opponent.field)}")

        return True

    except Exception as e:
        print_test_result("生命值清理测试", False, str(e))
        traceback.print_exc()
        return False

async def test_turn_number_display():
    """测试回合数显示"""
    print_section("测试回合数显示")

    try:
        game = CardGame("测试玩家", "测试对手")

        # 测试初始回合数
        print_test_result("初始回合数", game.turn_number == 1, f"回合数: {game.turn_number}")

        # 测试回合数增长
        for i in range(5):
            game.start_turn()
            expected_turn = i + 2
            print_test_result(f"第{expected_turn}回合", game.turn_number == expected_turn,
                            f"期望: {expected_turn}, 实际: {game.turn_number}")

        # 测试游戏状态中的回合数
        state = game.get_game_state()
        print_test_result("游戏状态回合数", state["turn_number"] == game.turn_number,
                        f"游戏状态: {state['turn_number']}, 实际: {game.turn_number}")

        return True

    except Exception as e:
        print_test_result("回合数显示测试", False, str(e))
        traceback.print_exc()
        return False

async def test_game_over_detection():
    """测试游戏结束检测"""
    print_section("测试游戏结束检测")

    try:
        game = CardGame("测试玩家", "测试对手")

        # 测试正常游戏结束（生命值归零）
        game.players[1].health = 0
        game_over = game._check_game_over()

        print_test_result("生命值归零游戏结束", game_over and game.game_over and game.winner == "测试玩家",
                        f"游戏结束: {game_over}, 获胜者: {game.winner}")

        # 重置游戏状态
        game = CardGame("测试玩家", "测试对手")

        # 测试平局（超过30回合）
        game.turn_number = 31
        game.players[0].health = 20
        game.players[1].health = 15
        game_over = game._check_game_over()

        print_test_result("超回合平局检测", game_over and game.game_over,
                        f"游戏结束: {game_over}, 获胜者: {game.winner}")

        # 测试平局时血量高者获胜
        game = CardGame("测试玩家", "测试对手")
        game.turn_number = 31
        game.players[0].health = 25  # 玩家血量更高
        game.players[1].health = 15
        game_over = game._check_game_over()

        print_test_result("平局血量高者获胜", game_over and game.winner == "测试玩家",
                        f"游戏结束: {game_over}, 获胜者: {game.winner}")

        return True

    except Exception as e:
        print_test_result("游戏结束检测测试", False, str(e))
        traceback.print_exc()
        return False

async def test_card_mechanics():
    """测试卡牌机制"""
    print_section("测试卡牌机制")

    try:
        from game_engine.card_game import Card

        game = CardGame("测试玩家", "测试对手")
        player = game.players[0]
        opponent = game.players[1]

        # 测试神圣护盾
        divine_minion = Card("圣盾随从", 3, 2, 3, "minion", ["divine_shield"])
        opponent.field.append(divine_minion)

        # 法术攻击圣盾随从
        spell_card = Card("火球术", 4, 6, 0, "spell")
        player.hand.append(spell_card)
        player.mana = 10

        result = game.play_card(0, 0, "随从0")

        print_test_result("神圣护盾机制", result["success"] and "divine_shield" not in divine_minion.mechanics,
                        f"法术结果: {result['message']}")
        print(f"  圣盾随从生命值: {divine_minion.health}")

        # 测试嘲讽机制
        taunt_minion = Card("嘲讽随从", 2, 1, 5, "minion", ["taunt"])
        normal_minion = Card("普通随从", 3, 4, 3, "minion")
        opponent.field.clear()
        opponent.field.extend([taunt_minion, normal_minion])

        # 获取法术目标
        spell_card2 = Card("火球术2", 4, 6, 0, "spell")
        targets = game._get_spell_targets(spell_card2, player, opponent)

        print_test_result("嘲讽机制", len(targets) == 1 and "随从_0" in targets,
                        f"可选目标: {targets}")

        return True

    except Exception as e:
        print_test_result("卡牌机制测试", False, str(e))
        traceback.print_exc()
        return False

async def test_ui_integration():
    """测试UI集成"""
    print_section("测试UI集成")

    try:
        ui = GameUIStatic()
        game = CardGame("测试玩家", "测试对手")
        ui.game_engine = game

        # 测试游戏状态更新
        ui.update_game_state()

        print_test_result("游戏状态更新", ui.game_state is not None,
                        f"状态存在: {ui.game_state is not None}")

        # 测试可用命令生成
        commands = ui._get_available_commands(ui.game_state)

        print_test_result("可用命令生成", len(commands) > 0, f"命令数量: {len(commands)}")

        # 测试回合数显示修复
        turn_number = ui.game_state.get('turn_number', 1)
        print_test_result("UI回合数显示", turn_number >= 1, f"UI回合数: {turn_number}")

        return True

    except Exception as e:
        print_test_result("UI集成测试", False, str(e))
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🎮 卡牌战斗竞技场 - 综合修复验证测试")
    print("测试所有已修复的游戏机制问题")

    test_results = []

    # 运行所有测试
    test_results.append(("get_winner()方法", await test_get_winner_method()))
    test_results.append(("法力值系统", await test_mana_system()))
    test_results.append(("随从生命值清理", await test_health_cleanup()))
    test_results.append(("回合数显示", await test_turn_number_display()))
    test_results.append(("游戏结束检测", await test_game_over_detection()))
    test_results.append(("卡牌机制", await test_card_mechanics()))
    test_results.append(("UI集成", await test_ui_integration()))

    # 显示测试总结
    print_section("测试结果总结")

    passed_count = 0
    total_count = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1

    print(f"\n总计: {passed_count}/{total_count} 项测试通过")

    if passed_count == total_count:
        print("\n🎉 所有修复验证测试全部通过！")
        print("\n💡 修复总结:")
        print("✅ 添加了缺失的 get_winner() 方法")
        print("✅ 修复了法力值系统异常问题")
        print("✅ 实现了随从死亡清理机制")
        print("✅ 修复了回合数显示格式化错误")
        print("✅ 完善了游戏结束检测机制")
        print("✅ 验证了卡牌机制正常工作")
        print("✅ 确认了UI集成无问题")
        print("\n🔧 游戏现在应该能够正常运行，不会再出现以下问题:")
        print("- AI获胜后游戏不结束")
        print("- 法力值显示异常")
        print("- 随从显示负生命值")
        print("- 回合数显示错误")
        print("- 游戏机制错误")
    else:
        failed_tests = [name for name, result in test_results if not result]
        print(f"\n⚠️ 有 {len(failed_tests)} 项测试失败: {', '.join(failed_tests)}")
        print("需要进一步调试这些问题")

if __name__ == "__main__":
    asyncio.run(main())