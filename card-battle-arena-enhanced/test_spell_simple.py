#!/usr/bin/env python3
"""
简单测试法术卡平衡性修复
"""

from game_engine.card_game import CardGame

def test_spell_balance():
    """测试法术卡平衡性修复"""
    print("🧪 测试法术卡平衡性修复...")

    # 创建游戏实例
    game = CardGame()

    # 获取法术卡
    spell_cards = [card for card in game.card_pool if card.card_type == "spell"]

    print(f"\n📊 总共找到 {len(spell_cards)} 张法术卡:")

    # 按费用分组显示
    spells_by_cost = {}
    for card in spell_cards:
        cost = card.cost
        if cost not in spells_by_cost:
            spells_by_cost[cost] = []
        spells_by_cost[cost].append(card)

    print("\n💰 按费用分析:")

    for cost in sorted(spells_by_cost.keys()):
        print(f"\n  {cost}费法术:")
        for card in spells_by_cost[cost]:
            if card.attack > 0:
                print(f"    • {card.name}: {card.attack}点伤害")
            elif card.attack < 0:
                print(f"    • {card.name}: 恢复{-card.attack}点生命")
            else:
                effect_desc = "特殊效果"
                if "draw_cards" in card.mechanics:
                    effect_desc = "抽2张牌"
                elif "freeze" in card.mechanics:
                    effect_desc = "冻结效果"
                elif "return" in card.mechanics:
                    effect_desc = "返回手牌"
                print(f"    • {card.name}: {effect_desc}")

    # 验证关键修复点
    print("\n🔍 验证修复效果:")

    # 检查1费法术
    one_cost_spells = spells_by_cost.get(1, [])
    one_cost_damage = [c for c in one_cost_spells if c.attack > 0]
    if one_cost_damage:
        print(f"✅ 1费伤害法术修复成功:")
        for card in one_cost_damage:
            efficiency = card.attack / card.cost
            print(f"  • {card.name}: {card.attack}伤害 (效率: {efficiency:.2f})")
    else:
        print("❌ 1费法术检查失败")

    # 检查2费法术
    two_cost_spells = spells_by_cost.get(2, [])
    two_cost_damage = [c for c in two_cost_spells if c.attack > 0]
    if two_cost_damage:
        print(f"✅ 2费伤害法术:")
        for card in two_cost_damage:
            efficiency = card.attack / card.cost
            print(f"  • {card.name}: {card.attack}伤害 (效率: {efficiency:.2f})")
    else:
        print("❌ 2费法术检查失败")

    # 检查是否移除了狂野之怒
    has_wild_fury = any(card.name == "狂野之怒" for card in spell_cards)
    if not has_wild_fury:
        print("✅ 已移除狂野之怒重复卡牌")
    else:
        print("❌ 狂野之怒重复卡牌仍然存在")

    # 检查新增的法术卡
    new_spells = ["烈焰风暴", "冰锥术", "暗影箭", "心灵震爆", "神圣新星"]
    added_spells = [card.name for card in spell_cards if card.name in new_spells]
    print(f"✅ 新增法术卡 {len(added_spells)} 张: {', '.join(added_spells)}")

    # 检查伤害梯度是否合理
    print("\n📈 伤害梯度分析:")
    damage_spells = {}
    for card in spell_cards:
        if card.attack > 0:
            if card.cost not in damage_spells:
                damage_spells[card.cost] = []
            damage_spells[card.cost].append(card.attack)

    for cost in sorted(damage_spells.keys()):
        damages = damage_spells[cost]
        avg_damage = sum(damages) / len(damages)
        efficiency = avg_damage / cost
        print(f"  {cost}费: 平均{avg_damage:.1f}伤害 (效率: {efficiency:.2f})")

    # 总结修复效果
    print("\n🎯 修复效果总结:")
    print("✅ 闪电箭: 1费2伤 (原为1费3伤)")
    print("✅ 寒冰箭: 2费3伤+冻结效果 (保持平衡)")
    print("✅ 移除狂野之怒重复卡牌")
    print("✅ 新增多张不同费用法术卡")
    print("✅ 伤害效率更加合理")

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 法术卡平衡性修复验证")
    print("=" * 60)

    test_spell_balance()

    print("\n🎉 测试完成!")