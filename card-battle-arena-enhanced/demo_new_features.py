#!/usr/bin/env python3
"""
新功能演示脚本
展示简化的交互方式和自动攻击功能
"""
import asyncio
import random
from game_engine.card_game import CardGame


async def demo_simplified_interaction():
    """演示简化的交互方式"""
    print("🎮 演示: 简化交互方式和自动攻击")
    print("=" * 50)

    # 创建游戏
    game = CardGame("演示玩家", "AI对手")

    # 显示初始状态
    print(f"📋 第1回合 - {game.get_current_player().name}")
    game.display_status(use_rich=False)

    # 演示快速出牌
    current = game.get_current_player()
    if current.hand:
        print(f"\n🃏 演示快速出牌 - 直接输入数字:")
        for i, card in enumerate(current.hand):
            if current.can_play_card(card):
                print(f"  输入 {i}: 打出 {card.name} ({card.cost}费)")

        # 模拟玩家出牌
        playable_cards = [i for i, card in enumerate(current.hand) if current.can_play_card(card)]
        if playable_cards:
            card_idx = playable_cards[0]
            result = game.quick_play_card(0, card_idx)
            print(f"✅ 执行: {result['message']}")

            # 显示更新后的状态
            print(f"\n📊 出牌后状态:")
            print(f"  法力值: {current.mana}/{current.max_mana}")
            print(f"  手牌: {len(current.hand)} 张")
            print(f"  场上随从: {len(current.field)} 个")

            if current.field:
                for i, minion in enumerate(current.field):
                    attack_status = "可攻击" if getattr(minion, 'can_attack', False) else "不可攻击"
                    print(f"    随从{i}: {minion.name} ({minion.attack}/{minion.health}) - {attack_status}")

    # 演示自动攻击
    print(f"\n⚔️ 演示自动攻击功能:")
    print("  输入回车/空格结束回合，系统会自动进行最优攻击")

    # 模拟结束回合（启用自动攻击）
    result = game.end_turn(0, auto_attack=True)
    print(f"✅ {result['message']}")

    # 显示AI回合后的状态
    ai = game.get_current_player()
    player = game.get_opponent()
    print(f"\n🤖 AI回合后状态:")
    print(f"  玩家生命: {player.health}/{player.max_health}")
    print(f"  AI生命: {ai.health}/{ai.max_health}")
    print(f"  AI场上随从: {len(ai.field)} 个")


def demo_quick_commands():
    """演示快速命令"""
    print("\n🎯 快速命令演示:")
    print("=" * 50)
    print("✅ 新的交互方式:")
    print("  • 直接输入数字出牌 (如: 0, 1, 2)")
    print("  • 输入 '技' 或 '技能' 使用英雄技能")
    print("  • 输入回车或空格结束回合 (自动攻击)")
    print("  • 输入 '帮' 查看帮助")
    print("  • 输入 '状态' 查看游戏状态")
    print("  • 输入 '随从攻击 0 英雄' 手动攻击")
    print("  • 输入 '英雄攻击' 英雄直接攻击")
    print("  • 输入 '退出' 退出游戏")

    print("\n⚡ 智能特性:")
    print("  • 自动攻击: 结束回合时智能选择攻击目标")
    print("  • 优先击杀: 优先消灭低血量随从")
    print("  • 嘲讽处理: 自动处理嘲讽随从")
    print("  • 潜行机制: 潜行随从免疫反击")
    print("  • 快捷提示: 实时显示可用操作")


def demo_attack_intelligence():
    """演示攻击智能"""
    print("\n🧠 攻击智能演示:")
    print("=" * 50)

    # 创建测试场景
    game = CardGame("测试玩家", "测试AI")

    # 手动设置测试场景
    player = game.players[0]
    ai = game.players[1]

    # 添加一些随从到场上
    from game_engine.card_game import Card
    player.field.extend([
        Card("攻击随从", 3, 4, 3, "minion", ["taunt"]),
        Card("高攻随从", 4, 6, 2, "minion", []),
        Card("潜行随从", 2, 3, 2, "minion", ["stealth"])
    ])

    ai.field.extend([
        Card("低血随从", 2, 2, 1, "minion", []),
        Card("嘲讽随从", 3, 3, 5, "minion", ["taunt"]),
        Card("普通随从", 4, 4, 4, "minion", [])
    ])

    # 激活攻击状态
    for minion in player.field:
        minion.can_attack = True

    print("📊 测试场景:")
    print("  玩家随从:")
    for i, minion in enumerate(player.field):
        mechanics = f" [{', '.join(minion.mechanics)}]" if minion.mechanics else ""
        print(f"    {i}: {minion.name} ({minion.attack}/{minion.health}){mechanics}")

    print("  AI随从:")
    for i, minion in enumerate(ai.field):
        mechanics = f" [{', '.join(minion.mechanics)}]" if minion.mechanics else ""
        print(f"    {i}: {minion.name} ({minion.attack}/{minion.health}){mechanics}")

    print("\n🤖 智能攻击决策:")
    messages = game._smart_combat_phase()
    if messages:
        print("  执行的攻击:")
        for msg in messages:
            print(f"    • {msg}")
    else:
        print("  没有可执行的攻击")

    print(f"\n📈 攻击结果:")
    print(f"  玩家剩余随从: {len(player.field)} 个")
    print(f"  AI剩余随从: {len(ai.field)} 个")
    print(f"  AI生命值: {ai.health}/{ai.max_health}")


if __name__ == "__main__":
    print("🎮 Card Battle Arena Enhanced - 新功能演示")
    print("展示简化的交互方式和智能攻击系统\n")

    # 演示快速命令
    demo_quick_commands()

    # 演示攻击智能
    demo_attack_intelligence()

    # 演示交互方式
    asyncio.run(demo_simplified_interaction())

    print("\n🎉 新功能演示完成!")
    print("💡 现在你可以享受更简单、更智能的游戏体验了!")