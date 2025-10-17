#!/usr/bin/env python3
"""
测试法术目标选择修复
"""

import asyncio
from game_engine.card_game import CardGame, Card

async def test_spell_fix():
    """测试法术目标选择修复"""
    print("🧪 测试法术目标选择修复")
    print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")

    # 设置测试场景
    player = game.players[0]     # 玩家先手
    ai_player = game.players[1]  # AI后手

    # 清空战场
    player.field.clear()
    ai_player.field.clear()

    # 添加测试随从
    ai_player.field.extend([
        Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"]),
        Card("血帆海盗", 1, 2, 1, "minion")
    ])

    # 添加法术卡牌到玩家手牌
    player.hand.append(Card("闪电箭", 1, 2, 0, "spell"))
    player.hand.append(Card("火球术", 4, 6, 0, "spell"))

    # 设置玩家法力值足够
    player.mana = 5
    player.max_mana = 5

    print(f"📊 测试场景:")
    print(f"   玩家法力值: {player.mana}/{player.max_mana}")
    print(f"   玩家手牌: {[f'{card.name}({card.cost}费)' for card in player.hand]}")
    print(f"   AI场随从: {[f'{minion.name}({minion.attack}/{minion.health})' for minion in ai_player.field]}")

    # 测试1: 玩家场没有随从，AI有随从的法术
    print(f"\n🎯 测试1: 玩家使用法术攻击AI随从")
    print("-" * 30)

    # 测试闪电箭攻击石像鬼（有圣盾）- 闪电箭在手牌第4张（索引3）
    result = game.play_card(0, 3, "随从_0")  # 闪电箭攻击石像鬼
    print(f"   闪电箭攻击石像鬼: {'成功' if result['success'] else '失败'}")
    if result["success"]:
        print(f"   结果: {result['message']}")
    else:
        print(f"   错误: {result['message']}")

    # 测试2: 玩家使用法术攻击AI英雄
    print(f"\n🎯 测试2: 玩家使用法术攻击AI英雄")
    print("-" * 30)

    # 重新添加一张闪电箭到玩家手牌，因为第一张已经用掉了
    player.hand.append(Card("闪电箭", 1, 2, 0, "spell"))
    player.mana = 5  # 恢复法力值

    result = game.play_card(0, len(player.hand)-1, "英雄")  # 使用最后一张闪电箭攻击英雄
    print(f"   闪电箭攻击英雄: {'成功' if result['success'] else '失败'}")
    if result["success"]:
        print(f"   结果: {result['message']}")
    else:
        print(f"   错误: {result['message']}")

    # 测试3: 法力值不足的情况
    print(f"\n🎯 测试3: 法力值不足")
    print("-" * 30)

    # 添加一张闪电箭用于测试
    player.hand.append(Card("闪电箭", 1, 2, 0, "spell"))
    player.mana = 0  # 设置法力值为0
    result = game.play_card(0, len(player.hand)-1, "英雄")  # 使用最后一张闪电箭攻击英雄
    print(f"   法力不足时使用闪电箭: {'成功' if result['success'] else '失败'}")
    if not result["success"]:
        print(f"   错误: {result['message']}")

    # 测试4: 多目标选择场景
    print(f"\n🎯 测试4: 多目标选择场景")
    print("-" * 30)

    # 清空手牌并添加新法术
    player.hand.clear()
    player.hand.append(Card("火球术", 4, 6, 0, "spell"))
    player.mana = 4  # 设置刚好够火球术的法力值

    result = game.play_card(0, 0)  # 不指定目标，应该返回需要选择目标
    print(f"   火球术不指定目标: {'成功' if result['success'] else '失败'}")
    if not result["success"]:
        print(f"   错误: {result['message']}")
        if result.get("need_target_selection"):
            print(f"   ✅ 正确返回需要目标选择")
            print(f"   可用目标: {result.get('available_targets', [])}")

      # 恢复法力值并测试
    player.mana = 10
    # 重新添加火球术，因为之前已经被用掉了
    player.hand.insert(0, Card("火球术", 4, 6, 0, "spell"))
    result = game.play_card(0, 0, "随从_0")  # 火球术攻击石像鬼
    print(f"   火球术攻击石像鬼: {'成功' if result['success'] else '失败'}")
    if result["success"]:
        print(f"   结果: {result['message']}")

    print(f"\n🎉 法术功能测试完成！")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_spell_fix())
    exit(0 if success else 1)