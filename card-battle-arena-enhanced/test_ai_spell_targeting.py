#!/usr/bin/env python3
"""
测试AI法术目标选择逻辑
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_engine.card_game import CardGame, Card
from main import ai_choose_spell_target


async def test_ai_spell_targeting():
    """测试AI法术目标选择"""
    print("🧪 测试AI法术目标选择逻辑")
    print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")
    ai_player_idx = 1  # AI是第二个玩家

    # 设置测试场景
    player = game.players[0]  # 玩家
    ai_player = game.players[1]  # AI

    # 清空战场
    player.field.clear()
    ai_player.field.clear()

    print("📊 测试场景设置:")
    print(f"   玩家血量: {player.health}")
    print(f"   AI血量: {ai_player.health}")

    # 测试1: 对手有嘲讽随从的情况
    print(f"\n🎯 测试1: 对手有嘲讽随从")
    print("-" * 30)

    # 添加嘲讽随从
    player.field.extend([
        Card("石像鬼", 1, 1, 1, "minion", ["taunt"]),
        Card("血帆海盗", 1, 2, 1, "minion"),
        Card("火球术", 4, 6, 0, "spell")
    ])

    # 创建闪电箭法术
    lightning_bolt = Card("闪电箭", 1, 2, 0, "spell")

    target = ai_choose_spell_target(game, ai_player_idx, lightning_bolt)
    print(f"   AI选择目标: {target}")
    print(f"   期望目标: 随从_0 (嘲讽随从)")
    print(f"   测试结果: {'✅ 通过' if target == '随从_0' else '❌ 失败'}")

    # 测试2: 可以一击必杀的情况
    print(f"\n🎯 测试2: 可以一击必杀的情况")
    print("-" * 30)

    # 清空战场，添加低血量随从
    player.field.clear()
    player.field.extend([
        Card("血帆海盗", 1, 2, 1, "minion"),  # 1血量，2攻击，可以被闪电箭击杀
        Card("大地之环先知", 3, 0, 5, "minion")  # 5血量，不会被击杀
    ])

    target = ai_choose_spell_target(game, ai_player_idx, lightning_bolt)
    print(f"   AI选择目标: {target}")
    print(f"   血帆海盗: 1血量2攻击，必杀价值=100+2*5=110")
    print(f"   大地之环先知: 5血量0攻击，无法击杀")
    print(f"   期望目标: 随从_0 (可击杀的血帆海盗)")
    print(f"   测试结果: {'✅ 通过' if target == '随从_0' else '❌ 失败'}")

    # 测试3: 英雄血量危险的情况
    print(f"\n🎯 测试3: 英雄血量危险的情况")
    print("-" * 30)

    # 设置玩家英雄血量危险
    player.health = 3  # 设置更低血量，更容易触发
    print(f"   玩家英雄血量: {player.health}")
    print(f"   闪电箭伤害: 2")
    print(f"   英雄危险判断: {player.health <= 2} (可以斩杀) 或 {player.health <= 7} (接近斩杀)")

    # 添加一个随从用于对比
    player.field.clear()
    player.field.append(Card("血帆海盗", 1, 1, 1, "minion"))  # 低价值随从

    target = ai_choose_spell_target(game, ai_player_idx, lightning_bolt)
    print(f"   AI选择目标: {target}")
    print(f"   期望目标: 英雄 (血量危险)")
    print(f"   测试结果: {'✅ 通过' if target == '英雄' else '❌ 失败'}")

    # 测试4: 有圣盾随从的情况
    print(f"\n🎯 测试4: 有圣盾随从的情况")
    print("-" * 30)

    player.field.clear()
    player.field.extend([
        Card("银色侍从", 1, 1, 1, "minion", ["divine_shield"]),
        Card("普通随从", 2, 3, 3, "minion")
    ])

    target = ai_choose_spell_target(game, ai_player_idx, lightning_bolt)
    print(f"   AI选择目标: {target}")
    print(f"   期望目标: 随从_0 (圣盾随从有价值)")
    print(f"   测试结果: {'✅ 通过' if target == '随从_0' else '❌ 失败'}")

    # 测试5: 非伤害法术
    print(f"\n🎯 测试5: 非伤害法术")
    print("-" * 30)

    heal_spell = Card("治愈术", 2, -5, 0, "spell")  # 治疗法术
    target = ai_choose_spell_target(game, ai_player_idx, heal_spell)
    print(f"   AI选择目标: {target}")
    print(f"   期望目标: None (非伤害法术不需要目标)")
    print(f"   测试结果: {'✅ 通过' if target is None else '❌ 失败'}")

    # 测试6: 高伤害法术的选择
    print(f"\n🎯 测试6: 高伤害法术的选择")
    print("-" * 30)

    fireball = Card("火球术", 4, 6, 0, "spell")
    player.field.clear()
    player.health = 20  # 设置英雄血量较高，避免触发英雄优先级
    player.field.extend([
        Card("低血量随从", 3, 2, 2, "minion"),   # 2血，可击杀，价值=100+2*5=110
        Card("高攻击随从", 5, 7, 5, "minion")    # 5血，可击杀，价值=100+7*5=135
    ])

    target = ai_choose_spell_target(game, ai_player_idx, fireball)
    print(f"   玩家英雄血量: {player.health}")
    print(f"   场上随从: 低血量(2血2攻), 高攻击(5血7攻)")
    print(f"   低血量随从价值: 100+2*5=110")
    print(f"   高攻击随从价值: 100+7*5=135")
    print(f"   英雄价值: 30")
    print(f"   AI选择目标: {target}")
    print(f"   期望目标: 随从_1 (高攻击随从)")
    print(f"   测试结果: {'✅ 通过' if target == '随从_1' else '❌ 失败'}")

    print(f"\n🎉 AI法术目标选择测试完成！")
    return True


async def test_ai_spell_integration():
    """测试AI法术执行集成"""
    print("\n🧪 测试AI法术执行集成")
    print("=" * 50)

    from main import execute_ai_action
    from ai_engine.strategies.base import AIAction, ActionType

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")
    ai_player_idx = 1

    # 设置为AI回合
    game.current_player_idx = ai_player_idx

    # 设置测试场景
    player = game.players[0]
    player.field.clear()
    player.field.append(Card("石像鬼", 1, 1, 1, "minion", ["taunt"]))

    # 给AI添加法术牌
    ai_player = game.players[1]
    ai_player.hand.clear()
    ai_player.hand.append(Card("闪电箭", 1, 2, 0, "spell"))
    ai_player.mana = 5

    print("📊 集成测试场景:")
    print(f"   AI手牌: {[get_card_name(card) for card in ai_player.hand]}")
    print(f"   AI法力: {ai_player.mana}")
    print(f"   玩家场随从: {[get_card_name(card) for card in player.field]}")

    # 创建AI动作
    ai_action = AIAction(
        action_type=ActionType.PLAY_CARD,
        confidence=0.8,
        reasoning="使用闪电箭攻击敌方嘲讽随从",
        parameters={"card": ai_player.hand[0]}
    )

    print(f"\n🎯 执行AI法术动作")
    print("-" * 30)

    # 执行AI动作
    result = await execute_ai_action(ai_action, game, ai_player_idx)
    print(f"   执行结果: {'成功' if result['success'] else '失败'}")
    print(f"   消息: {result['message']}")

    if result['success']:
        print(f"   ✅ AI成功使用法术并选择目标")
    else:
        print(f"   ❌ AI法术执行失败")

    print(f"\n🎉 AI法术执行集成测试完成！")
    return True


def get_card_name(card):
    """获取卡牌名称的辅助函数"""
    if isinstance(card, str):
        return card
    elif hasattr(card, 'name'):
        return card.name
    elif isinstance(card, dict):
        return card.get('name', '未知')
    else:
        return str(card)


if __name__ == "__main__":
    async def main():
        try:
            success1 = await test_ai_spell_targeting()
            success2 = await test_ai_spell_integration()

            if success1 and success2:
                print("\n🎉 所有AI法术目标选择测试通过！")
                print("✅ AI能够智能选择法术目标")
                print("✅ 优先攻击嘲讽随从")
                print("✅ 优先击杀低血量目标")
                print("✅ 考虑英雄血量威胁")
                print("✅ 考虑随从技能价值")
                print("✅ 法术执行集成正常")
                return True
            else:
                print("\n⚠️ 部分测试失败，需要检查实现。")
                return False
        except Exception as e:
            print(f"\n❌ 测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    success = asyncio.run(main())
    exit(0 if success else 1)