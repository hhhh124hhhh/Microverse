#!/usr/bin/env python3
"""
测试卡牌平衡修复效果
"""

import asyncio
from game_ui import GameUIStatic

def analyze_spell_balance():
    """分析法术卡的平衡性"""
    print("🧪 分析法术卡平衡性...")

    # 创建游戏实例获取卡牌池
    from game_engine.card_game import CardGame
    game = CardGame()

    # 统计法术卡
    spell_cards = [card for card in game.card_pool if card.card_type == "spell"]
    spell_by_cost = {}

    for card in spell_cards:
        cost = card.cost
        if cost not in spell_by_cost:
            spell_by_cost[cost] = []
        spell_by_cost[cost].append(card)

    print("\n📊 法术卡按费用分析:")
    for cost in sorted(spell_by_cost.keys()):
        cards = spell_by_cost[cost]
        print(f"\n💰 {cost}费法术 ({len(cards)}张):")

        for card in cards:
            # 分析效果类型
            if card.attack > 0:
                effect_desc = f"伤害{card.attack}点"
                efficiency = card.attack / cost
                print(f"  • {card.name}: {effect_desc} (效率: {efficiency:.2f})")
            elif card.attack < 0:
                effect_desc = f"治疗{-card.attack}点"
                efficiency = -card.attack / cost
                print(f"  • {card.name}: {effect_desc} (效率: {efficiency:.2f})")
            else:
                effect_desc = "特殊效果"
                if "draw_cards" in card.mechanics:
                    effect_desc = "抽2张牌"
                elif "freeze" in card.mechanics:
                    effect_desc = "冻结效果"
                elif "return" in card.mechanics:
                    effect_desc = "返回手牌"
                print(f"  • {card.name}: {effect_desc}")

    # 检查平衡性
    print("\n🔍 平衡性分析:")

    # 检查1费法术
    if 1 in spell_by_cost:
        one_cost = spell_by_cost[1]
        damage_spells = [c for c in one_cost if c.attack > 0]
        if damage_spells:
            avg_damage_1 = sum(c.attack for c in damage_spells) / len(damage_spells)
            print(f"  • 1费伤害法术平均伤害: {avg_damage_1:.1f}")
        else:
            print("  • 1费法术无直接伤害")

    # 检查2费法术
    if 2 in spell_by_cost:
        two_cost = spell_by_cost[2]
        damage_spells = [c for c in two_cost if c.attack > 0]
        if damage_spells:
            avg_damage_2 = sum(c.attack for c in damage_spells) / len(damage_spells)
            print(f"  • 2费伤害法术平均伤害: {avg_damage_2:.1f}")
        else:
            print("  • 2费法术无直接伤害")

    # 检查伤害递增是否合理
    damage_by_cost = {}
    for cost in sorted(spell_by_cost.keys()):
        damage_spells = [c for c in spell_by_cost[cost] if c.attack > 0]
        if damage_spells:
            avg_damage = sum(c.attack for c in damage_spells) / len(damage_spells)
            damage_by_cost[cost] = avg_damage

    print("\n📈 伤害效率趋势:")
    for cost in sorted(damage_by_cost.keys()):
        efficiency = damage_by_cost[cost] / cost
        print(f"  • {cost}费: 平均{damage_by_cost[cost]:.1f}伤害 (效率: {efficiency:.2f})")

    # 检查重复性问题
    print("\n🔍 重复性检查:")
    damage_profiles = {}
    for card in spell_cards:
        if card.attack > 0:  # 只检查伤害法术
            profile = f"{card.cost}费{card.attack}伤"
            if profile not in damage_profiles:
                damage_profiles[profile] = []
            damage_profiles[profile].append(card.name)

    has_duplicates = False
    for profile, cards in damage_profiles.items():
        if len(cards) > 1:
            print(f"  ⚠️ 发现重复配置 {profile}: {', '.join(cards)}")
            has_duplicates = True

    if not has_duplicates:
        print("  ✅ 未发现重复的法术卡配置")

    return True

async def test_spell_balance():
    """测试法术卡平衡性的实际效果"""
    print("\n🎮 测试法术卡平衡性...")

    # 创建静态UI实例
    ui = GameUIStatic()

    if not ui.game_engine:
        print("❌ 游戏引擎未加载，无法测试")
        return

    print("✅ 游戏引擎已加载")

    # 初始化游戏状态
    ui.update_game_state()

    # 模拟几个回合以获得足够法力值
    print("\n🔄 模拟前几个回合以获得法力值...")
    for i in range(3):  # 进行3个回合，获得4点法力
        if ui.game_engine:
            result = ui.game_engine.end_turn(0, auto_attack=False)
            if result.get("success"):
                ui.game_engine.end_turn(1, auto_attack=False)
                ui.update_game_state()
                player = ui.game_state.get("player", {})
                print(f"回合 {i+1} 结束，玩家法力值: {player.get('mana', 0)}")

    # 显示玩家手牌
    print("\n🃏 玩家手牌:")
    player = ui.game_state.get("player", {})
    hand = player.get("current_player_state", {}).get("hand", [])

    spell_cards = []
    for card in hand:
        if card.get("type") == "spell":
            spell_cards.append(card)
            print(f"  • {card['name']} ({card['cost']}费): {card.get('description', '')}")
            if card.get("attack", 0) > 0:
                print(f"    💥 伤害: {card['attack']}点")
            elif card.get("attack", 0) < 0:
                print(f"    💚 治疗: {-card['attack']}点")

    if spell_cards:
        print(f"\n✅ 手中有 {len(spell_cards)} 张法术卡可用于测试")

        # 测试不同费用的法术
        for card in spell_cards[:3]:  # 测试前3张法术卡
            cost = card.get("cost", 0)
            if player.get("mana", 0) >= cost:
                print(f"\n⚡ 测试使用 {card['name']} ({cost}费)...")

                # 记录使用前的状态
                old_opponent_health = ui.game_state.get("opponent", {}).get("health", 0)
                old_mana = player.get("mana", 0)

                # 使用法术卡
                action_data = {'action': 'play_card', 'card_index': hand.index(card)}
                await ui._handle_card_played(action_data)

                # 显示使用后的状态
                ui.update_game_state()
                new_opponent_health = ui.game_state.get("opponent", {}).get("health", 0)
                new_mana = ui.game_state.get("player", {}).get("mana", 0)

                damage_dealt = old_opponent_health - new_opponent_health
                mana_used = old_mana - new_mana

                print(f"  📊 结果: 消耗{mana_used}点法力，造成{damage_dealt}点伤害")

                if damage_dealt > 0:
                    efficiency = damage_dealt / mana_used if mana_used > 0 else 0
                    print(f"  📈 效率: {efficiency:.2f}伤害/法力")
    else:
        print("\n❌ 手中没有法术卡，无法测试")

    print("\n🎯 卡牌平衡性修复测试完成!")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 卡牌平衡性修复测试")
    print("=" * 60)

    # 分析平衡性
    analyze_spell_balance()

    # 测试实际效果
    asyncio.run(test_spell_balance())