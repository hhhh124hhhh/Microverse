#!/usr/bin/env python3
"""
测试初始抽牌修复效果
验证玩家一开始能获得低费卡牌
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from game_engine.card_game import CardGame

console = Console()

def test_initial_draw_distribution():
    """测试初始抽牌分布"""
    console.print("🧪 [bold blue]测试初始抽牌分布[/bold blue]")
    console.print("=" * 60)

    try:
        # 进行多次测试
        test_rounds = 10
        cost_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0}
        card_types = {"minion": 0, "spell": 0}
        first_cards = []

        for round_num in range(test_rounds):
            console.print(f"\n📋 [cyan]测试轮次 {round_num + 1}:[/cyan]")

            game = CardGame("玩家", "AI")
            player = game.players[0]

            # 分析初始手牌
            round_costs = []
            for i, card in enumerate(player.hand):
                cost = card.cost
                card_type = card.card_type
                round_costs.append(cost)
                cost_distribution[cost] += 1
                card_types[card_type] += 1

                if i == 0:  # 记录第一张牌
                    first_cards.append(f"{card.name} ({cost}费)")

                # 显示每张牌
                status = "✅ 可出" if cost <= 1 else f"❌ 需{cost}费"
                card_type_cn = "随从" if card_type == "minion" else "法术"
                console.print(f"  {i+1}. {card.name} ({cost}费) - {card_type_cn} {status}")

            # 计算这轮的平均费用
            avg_cost = sum(round_costs) / len(round_costs)
            console.print(f"  平均费用: {avg_cost:.1f}")

        # 统计结果
        console.print(f"\n📊 [bold blue]总体统计 ({test_rounds}轮):[/bold blue]")
        console.print("=" * 40)

        console.print(f"📋 [cyan]费用分布:[/cyan]")
        total_cards = sum(cost_distribution.values())
        for cost in sorted(cost_distribution.keys()):
            if cost_distribution[cost] > 0:
                percentage = (cost_distribution[cost] / total_cards) * 100
                console.print(f"  {cost}费: {cost_distribution[cost]}张 ({percentage:.1f}%)")

        console.print(f"\n📋 [cyan]卡牌类型分布:[/cyan]")
        for card_type, count in card_types.items():
            percentage = (count / total_cards) * 100
            type_cn = "随从" if card_type == "minion" else "法术"
            console.print(f"  {type_cn}: {count}张 ({percentage:.1f}%)")

        console.print(f"\n📋 [cyan]第一张牌记录:[/cyan]")
        for i, card_info in enumerate(first_cards, 1):
            console.print(f"  轮{i}: {card_info}")

        # 评估结果
        low_cost_cards = sum(cost_distribution[cost] for cost in [1, 2])
        low_cost_percentage = (low_cost_cards / total_cards) * 100

        console.print(f"\n✅ [green]评估结果:[/green]")
        console.print(f"  1-2费卡牌: {low_cost_cards}张 ({low_cost_percentage:.1f}%)")
        console.print(f"  期望: 至少60%的初始卡牌应该是1-2费")

        if low_cost_percentage >= 60:
            console.print("[green]✅ 初始抽牌分配合理！[/green]")
            return True
        else:
            console.print("[red]❌ 初始抽牌分配不合理，需要更多低费卡牌[/red]")
            return False

    except Exception as e:
        console.print(f"[red]💥 测试出错: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False

def test_first_card_priority():
    """测试第一张牌优先级"""
    console.print("\n🧪 [bold blue]测试第一张牌优先级[/bold blue]")
    console.print("=" * 60)

    try:
        # 测试多轮，看第一张牌是否总是低费随从
        test_rounds = 20
        first_card_results = []

        for round_num in range(test_rounds):
            game = CardGame("玩家", "AI")
            player = game.players[0]
            first_card = player.hand[0]

            result = {
                "name": first_card.name,
                "cost": first_card.cost,
                "type": first_card.card_type,
                "is_minion": first_card.card_type == "minion",
                "is_cheap": first_card.cost <= 1
            }
            first_card_results.append(result)

        # 统计结果
        cheap_minion_count = sum(1 for r in first_card_results if r["is_minion"] and r["is_cheap"])
        cheap_minion_percentage = (cheap_minion_count / test_rounds) * 100

        console.print(f"📋 [cyan]第一张牌统计 ({test_rounds}轮):[/cyan]")
        console.print(f"  1费随从: {cheap_minion_count}轮 ({cheap_minion_percentage:.1f}%)")

        # 显示一些例子
        console.print(f"\n📋 [cyan]第一张牌示例:[/cyan]")
        for i, result in enumerate(first_card_results[:5], 1):
            card_type_cn = "随从" if result["type"] == "minion" else "法术"
            status = "✅" if result["is_cheap"] else f"❌ ({result['cost']}费)"
            console.print(f"  {i}. {result['name']} - {card_type_cn} {status}")

        if len(first_card_results) > 5:
            console.print("  ...")

        # 评估
        console.print(f"\n✅ [green]评估结果:[/green]")
        if cheap_minion_percentage >= 50:
            console.print(f"[green]✅ 第一张牌优先级合理 ({cheap_minion_percentage:.1f}%)[/green]")
            return True
        else:
            console.print(f"[red]❌ 第一张牌优先级不合理 ({cheap_minion_percentage:.1f}%)[/red]")
            return False

    except Exception as e:
        console.print(f"[red]💥 测试出错: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False

def test_playable_start():
    """测试开局可用性"""
    console.print("\n🧪 [bold blue]测试开局可用性[/bold blue]")
    console.print("=" * 60)

    try:
        test_rounds = 10
        playable_counts = []

        for round_num in range(test_rounds):
            game = CardGame("玩家", "AI")
            player = game.players[0]

            # 计算可出的牌数（玩家有1点法力）
            playable = sum(1 for card in player.hand if card.cost <= 1)
            playable_counts.append(playable)

            console.print(f"轮 {round_num + 1}: 可出 {playable}/3 张牌")

        avg_playable = sum(playable_counts) / len(playable_counts)
        playable_percentage = (avg_playable / 3) * 100

        console.print(f"\n📊 [bold blue]开局可用性统计:[/bold blue]")
        console.print(f"  平均可出牌数: {avg_playable:.1f}/3")
        console.print(f"  可用性: {playable_percentage:.1f}%")

        if playable_percentage >= 50:
            console.print(f"[green]✅ 开局可用性良好 ({playable_percentage:.1f}%)[/green]")
            return True
        else:
            console.print(f"[red]❌ 开局可用性不足 ({playable_percentage:.1f}%)[/red]")
            return False

    except Exception as e:
        console.print(f"[red]💥 测试出错: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())
        return False

if __name__ == "__main__":
    tests = [
        ("初始抽牌分布", test_initial_draw_distribution),
        ("第一张牌优先级", test_first_card_priority),
        ("开局可用性", test_playable_start)
    ]

    results = []

    for test_name, test_func in tests:
        console.print(f"\n🚀 开始测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                console.print(f"[green]✅ {test_name} 测试通过[/green]")
            else:
                console.print(f"[red]❌ {test_name} 测试失败[/red]")
        except Exception as e:
            console.print(f"[red]💥 {test_name} 测试异常: {e}[/red]")
            results.append((test_name, False))

    # 输出总结
    console.print(f"\n📊 [bold blue]测试总结[/bold blue]")
    console.print("=" * 40)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        color = "green" if result else "red"
        console.print(f"[{color}]  {test_name}: {status}[/{color}]")

    console.print(f"\n🎯 [bold]总体结果: {passed}/{total} 个测试通过[/bold]")

    if passed == total:
        console.print("[bold green]🎉 初始抽牌修复成功！[/bold green]")
        console.print("\n✨ 修复效果:")
        console.print("  ✅ 玩家开局获得低费卡牌")
        console.print("  ✅ 第一张牌优先1费随从")
        console.print("  ✅ 开局可用性大幅提升")
    else:
        console.print(f"[bold red]⚠️  还有 {total - passed} 个问题需要修复[/bold red]")

    sys.exit(0 if passed == total else 1)