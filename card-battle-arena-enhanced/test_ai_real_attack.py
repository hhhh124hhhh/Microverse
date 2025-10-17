#!/usr/bin/env python3
"""
AI实际攻击测试 - 验证AI攻击修复
"""

import asyncio
from game_engine.card_game import CardGame, Card
from main import execute_ai_action
from ai_engine.strategies.base import AIAction, ActionType

async def test_ai_real_attack():
    """测试AI实际攻击"""
    print("🧪 测试AI实际攻击修复")

    # 创建游戏实例
    game = CardGame("测试AI", "测试玩家")  # AI先手

    # 设置测试场景 - 注意现在AI是玩家0，真实玩家是玩家1
    ai_player = game.players[0]  # AI是先手
    player = game.players[1]     # 玩家是后手

    # 清空战场
    player.field.clear()
    ai_player.field.clear()

    # 添加测试随从
    player_minion = Card("邪犬", 1, 2, 1, "minion")
    ai_minion = Card("月盗", 1, 1, 2, "minion", ["stealth"])

    player.field.append(player_minion)  # 玩家（后手）的随从
    ai_player.field.append(ai_minion)    # AI（先手）的随从
    ai_minion.can_attack = True         # 设置为可攻击

    print(f"📊 测试场景:")
    print(f"   AI随从: {ai_minion.name} (可攻击: {ai_minion.can_attack})")
    print(f"   玩家随从: {player_minion.name}")

    # 创建AI攻击动作 - 使用正确的AIAction对象
    ai_action = AIAction(
        action_type=ActionType.ATTACK,
        confidence=0.9,
        reasoning=f"用 {ai_minion.name} 攻击 {player_minion.name}",
        parameters={
            "attacker": ai_minion,
            "target": player_minion
        }
    )

    print(f"\n🎯 执行AI攻击:")
    print(f"   攻击者: {ai_action.parameters['attacker'].name}")
    print(f"   目标: {ai_action.parameters['target'].name}")
    print(f"   推理: {ai_action.reasoning}")

    # 执行AI动作 - AI是玩家0
    result = await execute_ai_action(ai_action, game, 0)

    print(f"\n📋 攻击结果:")
    if result["success"]:
        print(f"   ✅ 攻击成功: {result['message']}")
        print(f"   玩家剩余血量: {player.health}")
        print(f"   AI随从血量: {ai_minion.health}")
        print(f"   玩家随从血量: {player_minion.health}")
    else:
        print(f"   ❌ 攻击失败: {result['message']}")

    # 测试多个目标
    print(f"\n🎯 测试多目标场景:")

    # 添加更多随从
    player.field.extend([
        Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"]),
        Card("血帆海盗", 1, 2, 1, "minion")
    ])

    print(f"   玩家场上随从: {[m.name for m in player.field]}")

    # 测试攻击每个目标
    for i, target_minion in enumerate(player.field):
        test_action = AIAction(
            action_type=ActionType.ATTACK,
            confidence=0.8,
            reasoning=f"用 {ai_minion.name} 攻击 {target_minion.name}",
            parameters={
                "attacker": ai_minion,
                "target": target_minion
            }
        )

        # 重新设置AI随从可攻击
        ai_minion.can_attack = True

        result = await execute_ai_action(test_action, game, 0)
        if result["success"]:
            print(f"   ✅ 攻击 {target_minion.name}: {result['message']}")
        else:
            print(f"   ❌ 攻击 {target_minion.name}: {result['message']}")

    return result["success"]

if __name__ == "__main__":
    success = asyncio.run(test_ai_real_attack())
    if success:
        print(f"\n🎉 AI实际攻击测试通过！")
    else:
        print(f"\n⚠️ AI实际攻击测试失败！")