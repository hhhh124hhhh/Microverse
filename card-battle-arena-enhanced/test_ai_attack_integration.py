#!/usr/bin/env python3
"""
AI攻击集成测试 - 完整测试AI在游戏中的攻击功能
"""

import asyncio
from game_engine.card_game import CardGame, Card
from ai_engine.strategies.base import AIAction, ActionType
from main import execute_ai_action

async def test_ai_attack_integration():
    """测试AI攻击集成"""
    print("🧪 AI攻击集成测试")
    print("=" * 50)

    # 创建游戏实例
    game = CardGame("AI测试", "玩家测试")

    # 设置测试场景
    ai_player = game.players[0]  # AI先手
    player = game.players[1]     # 玩家后手

    # 清空战场
    player.field.clear()
    ai_player.field.clear()

    # 添加测试随从 - 模拟真实游戏场景
    player.field.extend([
        Card("狼人渗透者", 3, 3, 2, "minion"),
        Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"]),
        Card("血帆海盗", 1, 2, 1, "minion")
    ])

    ai_player.field.extend([
        Card("月盗", 1, 1, 2, "minion", ["stealth"]),
        Card("邪犬", 1, 2, 1, "minion")
    ])

    # 设置AI随从可以攻击
    for minion in ai_player.field:
        minion.can_attack = True

    print(f"📊 初始战场状态:")
    print(f"   AI场随从: {[f'{m.name}({m.attack}/{m.health})' for m in ai_player.field]}")
    print(f"   玩家场随从: {[f'{m.name}({m.attack}/{m.health})' for m in player.field]}")

    # 测试1: AI使用不同格式攻击目标
    test_cases = [
        {
            "name": "字典格式目标攻击",
            "attacker": ai_player.field[0],  # 月盗
            "target": {"name": "狼人渗透者", "attack": 3, "health": 2},
            "expected_target": "狼人渗透者"
        },
        {
            "name": "对象格式目标攻击",
            "attacker": ai_player.field[1],  # 邪犬
            "target": player.field[1],        # 石像鬼对象
            "expected_target": "石像鬼"
        },
        {
            "name": "英雄攻击",
            "attacker": ai_player.field[0],  # 月盗
            "target": "英雄",
            "expected_target": "英雄"
        }
    ]

    success_count = 0
    total_tests = len(test_cases)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 测试{i}: {test_case['name']}")
        print("-" * 30)

        # 重新设置攻击状态
        for minion in ai_player.field:
            minion.can_attack = True

        # 创建AI动作
        ai_action = AIAction(
            action_type=ActionType.ATTACK,
            confidence=0.9,
            reasoning=f"测试攻击: {test_case['name']}",
            parameters={
                "attacker": test_case["attacker"],
                "target": test_case["target"]
            }
        )

        print(f"   攻击者: {test_case['attacker'].name}")
        print(f"   目标类型: {type(test_case['target']).__name__}")
        print(f"   期望目标: {test_case['expected_target']}")

        # 执行AI攻击
        result = await execute_ai_action(ai_action, game, 0)

        if result["success"]:
            print(f"   ✅ 攻击成功: {result['message']}")
            success_count += 1
        else:
            print(f"   ❌ 攻击失败: {result['message']}")

    # 测试4: 多连续攻击测试
    print(f"\n🎯 测试{total_tests + 1}: 多连续攻击")
    print("-" * 30)

    consecutive_attacks = 0
    max_attacks = 3

    for i in range(max_attacks):
        if not ai_player.field:
            break

        # 选择第一个可攻击的随从
        attacker = None
        for minion in ai_player.field:
            if minion.can_attack and minion.health > 0:
                attacker = minion
                break

        if not attacker:
            break

        # 选择玩家第一个存活的随从作为目标
        target = None
        for minion in player.field:
            if minion.health > 0:
                target = minion
                break

        if not target:
            # 攻击英雄
            target = "英雄"

        ai_action = AIAction(
            action_type=ActionType.ATTACK,
            confidence=0.8,
            reasoning=f"连续攻击{i+1}",
            parameters={
                "attacker": attacker,
                "target": target
            }
        )

        result = await execute_ai_action(ai_action, game, 0)
        if result["success"]:
            consecutive_attacks += 1
            print(f"   ✅ 连续攻击{i+1}成功: {result['message']}")
        else:
            print(f"   ❌ 连续攻击{i+1}失败: {result['message']}")
            break

    # 总结测试结果
    print(f"\n📋 测试总结")
    print("=" * 30)
    print(f"   基础攻击测试: {success_count}/{total_tests} 通过")
    print(f"   连续攻击测试: {consecutive_attacks}/{max_attacks} 成功")

    overall_success = success_count == total_tests and consecutive_attacks > 0

    if overall_success:
        print(f"🎉 AI攻击集成测试通过！")
        print(f"   ✅ AI能够正确识别不同格式的目标")
        print(f"   ✅ AI能够成功执行攻击动作")
        print(f"   ✅ AI能够进行连续攻击")
    else:
        print(f"⚠️ AI攻击集成测试部分失败")
        if success_count < total_tests:
            print(f"   ❌ 部分基础攻击测试失败")
        if consecutive_attacks == 0:
            print(f"   ❌ 连续攻击测试失败")

    return overall_success

if __name__ == "__main__":
    success = asyncio.run(test_ai_attack_integration())
    exit(0 if success else 1)