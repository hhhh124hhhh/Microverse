#!/usr/bin/env python3
"""
测试1费随从多样性修复效果
验证新的卡牌机制是否正常工作
"""

import asyncio
from game_engine.card_game import CardGame

def test_card_pool_diversity():
    """测试卡牌池多样性"""
    print("🧪 测试1费随从池多样性...")

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")

    # 统计1费随从
    one_cost_minions = [card for card in game.card_pool
                       if card.card_type == "minion" and card.cost == 1]

    print(f"✅ 找到 {len(one_cost_minions)} 种不同的1费随从:")

    # 显示所有1费随从的信息
    for card in one_cost_minions:
        mechanics_str = f"[{', '.join(card.mechanics)}]" if card.mechanics else "无特效"
        print(f"   • {card.name} ({card.attack}/{card.health}) - {mechanics_str}")
        print(f"     {card.description}")

    # 验证是否有足够的多样性
    if len(one_cost_minions) >= 8:
        print(f"✅ 1费随从池多样性充足 ({len(one_cost_minions)} 种)")
    else:
        print(f"⚠️ 1费随从池多样性不足 ({len(one_cost_minions)} 种)")

    return len(one_cost_minions)

def test_no_duplicate_cards():
    """测试无重复卡牌机制"""
    print("\n🧪 测试防重复卡牌机制...")

    # 进行多轮测试
    total_tests = 5
    duplicate_count = 0

    for test_round in range(total_tests):
        print(f"\n🔄 测试轮次 {test_round + 1}/{total_tests}")

        game = CardGame("测试玩家", "测试对手")

        # 检查玩家初始手牌是否有重复
        player_hand_names = [card.name for card in game.players[0].hand]
        opponent_hand_names = [card.name for card in game.players[1].hand]

        player_duplicates = len(player_hand_names) != len(set(player_hand_names))
        opponent_duplicates = len(opponent_hand_names) != len(set(opponent_hand_names))

        if player_duplicates:
            print(f"   ❌ 玩家手牌有重复: {player_hand_names}")
            duplicate_count += 1
        else:
            print(f"   ✅ 玩家手牌无重复: {player_hand_names}")

        if opponent_duplicates:
            print(f"   ❌ 对手手牌有重复: {opponent_hand_names}")
            duplicate_count += 1
        else:
            print(f"   ✅ 对手手牌无重复: {opponent_hand_names}")

        # 模拟几轮抽牌测试
        for round_num in range(3):
            if game.players[0].deck_size > 0:
                # 玩家抽牌
                game.start_turn()  # 这会触发抽牌

                # 检查新手牌是否有重复
                new_hand_names = [card.name for card in game.players[0].hand]
                new_duplicates = len(new_hand_names) != len(set(new_hand_names))

                if new_duplicates:
                    print(f"   ❌ 第{round_num+1}轮抽牌后出现重复: {new_hand_names}")
                    duplicate_count += 1
                    break
                else:
                    print(f"   ✅ 第{round_num+1}轮抽牌后无重复")

    print(f"\n📊 测试结果: {total_tests} 轮测试中有 {duplicate_count} 次重复")

    if duplicate_count == 0:
        print("✅ 防重复机制工作正常")
    else:
        print(f"⚠️ 防重复机制需要改进 ({duplicate_count} 次重复)")

    return duplicate_count

def test_strategic_diversity():
    """测试策略多样性"""
    print("\n🧪 测试1费随从策略多样性...")

    game = CardGame("测试玩家", "测试对手")

    # 统计1费随从的不同特性
    one_cost_minions = [card for card in game.card_pool
                       if card.card_type == "minion" and card.cost == 1]

    # 分析不同类型的随从
    attack_types = {}  # 攻击力分布
    health_types = {}  # 血量分布
    mechanics_count = {}  # 特效统计

    for card in one_cost_minions:
        # 统计攻击力
        attack_types[card.attack] = attack_types.get(card.attack, 0) + 1

        # 统计血量
        health_types[card.health] = health_types.get(card.health, 0) + 1

        # 统计特效
        if card.mechanics:
            for mechanic in card.mechanics:
                mechanics_count[mechanic] = mechanics_count.get(mechanic, 0) + 1
        else:
            mechanics_count["无特效"] = mechanics_count.get("无特效", 0) + 1

    print("📈 1费随从攻击力分布:")
    for attack, count in sorted(attack_types.items()):
        print(f"   • {attack}点攻击: {count}种随从")

    print("\n📈 1费随从血量分布:")
    for health, count in sorted(health_types.items()):
        print(f"   • {health}点血量: {count}种随从")

    print("\n📈 1费随从特效分布:")
    for mechanic, count in sorted(mechanics_count.items()):
        print(f"   • {mechanic}: {count}种随从")

    # 计算多样性得分
    diversity_score = len(attack_types) + len(health_types) + len(mechanics_count)
    print(f"\n🎯 策略多样性得分: {diversity_score}")

    if diversity_score >= 6:
        print("✅ 策略多样性充足")
    else:
        print("⚠️ 策略多样性有待提升")

    return diversity_score

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 1费随从多样性修复效果验证测试")
    print("=" * 60)

    # 运行所有测试
    card_count = test_card_pool_diversity()
    duplicate_count = test_no_duplicate_cards()
    diversity_score = test_strategic_diversity()

    # 总结测试结果
    print("\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    print(f"🃏 1费随从种类数量: {card_count}")
    print(f"🔄 重复卡牌测试: {duplicate_count} 次重复")
    print(f"🎯 策略多样性得分: {diversity_score}")

    # 总体评价
    if card_count >= 8 and duplicate_count == 0 and diversity_score >= 6:
        print("\n🎉 修复效果优秀！1费随从池已显著改善")
        print("✅ 卡牌多样性充足")
        print("✅ 防重复机制正常")
        print("✅ 策略选择丰富")
    elif card_count >= 6 and duplicate_count <= 1 and diversity_score >= 4:
        print("\n👍 修复效果良好，但有改进空间")
    else:
        print("\n⚠️ 修复效果需要进一步改进")

    print("\n🎮 建议进行实际游戏测试以验证游戏体验")

if __name__ == "__main__":
    main()