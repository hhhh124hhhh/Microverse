#!/usr/bin/env python3
"""
调试AI连续攻击问题
"""

import asyncio
from game_engine.card_game import CardGame, Card
from ai_engine.strategies.base import AIAction, ActionType
from main import execute_ai_action

async def debug_consecutive_attacks():
    """调试连续攻击问题"""
    print("🔍 调试AI连续攻击问题")
    print("=" * 40)

    # 创建游戏实例
    game = CardGame("AI", "玩家")

    ai_player = game.players[0]
    player = game.players[1]

    # 清空战场
    player.field.clear()
    ai_player.field.clear()

    # 添加一个强力的AI随从和多个玩家目标
    ai_player.field.append(Card("强盗", 2, 2, 5, "minion"))  # 高血量
    player.field.extend([
        Card("目标1", 1, 1, 1, "minion"),
        Card("目标2", 1, 1, 1, "minion"),
        Card("目标3", 1, 1, 1, "minion")
    ])

    # 设置随从可以攻击（多次）
    for minion in ai_player.field:
        minion.can_attack = True
        minion.attacks_this_turn = 0  # 重置攻击次数

    print(f"📊 初始状态:")
    print(f"   AI随从: {[f'{m.name}({m.attack}/{m.health}) 可攻击:{m.can_attack}' for m in ai_player.field]}")
    print(f"   玩家随从: {[f'{m.name}({m.attack}/{m.health})' for m in player.field]}")

    # 尝试连续攻击
    for i in range(3):
        print(f"\n🎯 尝试攻击{i+1}:")

        # 检查AI随从状态
        alive_attackers = [m for m in ai_player.field if m.health > 0 and m.can_attack]
        print(f"   可攻击的AI随从: {[f'{m.name}({m.attack}/{m.health})' for m in alive_attackers]}")

        if not alive_attackers:
            print(f"   ❌ 没有可攻击的AI随从")
            break

        attacker = alive_attackers[0]

        # 找到存活的玩家目标
        alive_targets = [m for m in player.field if m.health > 0]
        print(f"   存活的玩家目标: {[f'{m.name}({m.attack}/{m.health})' for m in alive_targets]}")

        if not alive_targets:
            target = "英雄"
        else:
            target = alive_targets[0]

        print(f"   攻击: {attacker.name} -> {target.name if hasattr(target, 'name') else target}")

        ai_action = AIAction(
            action_type=ActionType.ATTACK,
            confidence=0.9,
            reasoning=f"调试攻击{i+1}",
            parameters={
                "attacker": attacker,
                "target": target
            }
        )

        result = await execute_ai_action(ai_action, game, 0)
        print(f"   结果: {result['success']} - {result['message']}")

        # 检查攻击后状态
        print(f"   攻击后AI随从: {attacker.name}({attacker.attack}/{attacker.health}) 可攻击:{attacker.can_attack}")

        # 手动重置攻击状态来测试
        if attacker.health > 0:
            attacker.can_attack = True
            print(f"   🔧 手动重置{attacker.name}为可攻击")

if __name__ == "__main__":
    asyncio.run(debug_consecutive_attacks())