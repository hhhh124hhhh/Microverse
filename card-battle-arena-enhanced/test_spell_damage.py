#!/usr/bin/env python3
"""
测试法术伤害和显示问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card
from rich.console import Console

console = Console()

def test_spell_damage_and_display():
    """测试法术伤害计算和显示"""
    console.print("🧪 [bold blue]法术伤害和显示测试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")

    # 清空手牌，添加已知的法术牌
    game.players[0].hand.clear()
    game.players[1].hand.clear()

    # 添加狂野之怒 (1费, 3伤害)
    card1 = Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火，对敌人造成3点伤害")
    game.players[0].hand.append(card1)

    # 添加治愈术 (2费, -5治疗)
    card2 = Card("治愈术", 2, -5, 0, "spell", [], "💚 圣光之力，恢复5点生命值")
    game.players[0].hand.append(card2)

    # 添加火球术 (4费, 6伤害)
    card3 = Card("火球术", 4, 6, 0, "spell", [], "🔥 法师经典法术，召唤炽热火球轰击敌人")
    game.players[0].hand.append(card3)

    # 设置足够的法力值
    game.players[0].mana = 10
    game.players[0].max_mana = 10

    # 让玩家先受伤，以便测试治疗
    game.players[0].health = 20

    # 记录初始血量
    initial_health = game.players[1].health
    console.print(f"📊 [bold cyan]测试设置：[/bold cyan]")
    console.print(f"   我方法力值: {game.players[0].mana}/{game.players[0].max_mana}")
    console.print(f"   我方血量: {game.players[0].health}/{game.players[0].max_health}")
    console.print(f"   对手初始血量: {initial_health}")
    console.print(f"   手牌数量: {len(game.players[0].hand)}")

    # 显示游戏状态，查看法术显示
    console.print(f"\n🎮 [bold green]测试1: 法术显示验证[/bold green]")
    game.display_status()

    # 测试出狂野之怒
    console.print(f"\n🔥 [bold yellow]测试2: 打出狂野之怒 (3伤害)[/bold yellow]")
    result = game.play_card(0, 0)
    console.print(f"   结果: {result['success']}")
    console.print(f"   消息: {result['message']}")
    console.print(f"   对手当前血量: {game.players[1].health}/{initial_health}")

    expected_health = initial_health - 3
    if game.players[1].health == expected_health:
        console.print("   ✅ 伤害计算正确")
    else:
        console.print(f"   ❌ 伤害计算错误，期望: {expected_health}, 实际: {game.players[1].health}")

    # 测试出治愈术
    console.print(f"\n💚 [bold yellow]测试3: 打出治愈术 (-5治疗)[/bold yellow]")
    before_heal = game.players[0].health
    result = game.play_card(0, 0)  # 现在第一张是治愈术
    console.print(f"   结果: {result['success']}")
    console.print(f"   消息: {result['message']}")
    console.print(f"   我方当前血量: {game.players[0].health}")

    expected_health = min(game.players[0].max_health, before_heal + 5)
    if game.players[0].health == expected_health:
        console.print("   ✅ 治疗计算正确")
    else:
        console.print(f"   ❌ 治疗计算错误，期望: {expected_health}, 实际: {game.players[0].health}")

    # 测试出火球术
    console.print(f"\n🔥 [bold yellow]测试4: 打出火球术 (6伤害)[/bold yellow]")
    before_damage = game.players[1].health
    result = game.play_card(0, 0)  # 现在第一张是火球术
    console.print(f"   结果: {result['success']}")
    console.print(f"   消息: {result['message']}")
    console.print(f"   对手当前血量: {game.players[1].health}")

    expected_health = before_damage - 6
    if game.players[1].health == expected_health:
        console.print("   ✅ 伤害计算正确")
    else:
        console.print(f"   ❌ 伤害计算错误，期望: {expected_health}, 实际: {game.players[1].health}")

    # 最终总结
    console.print(f"\n📋 [bold magenta]测试总结：[/bold magenta]")
    console.print(f"   最终我方血量: {game.players[0].health}/{game.players[0].max_health}")
    console.print(f"   最终对手血量: {game.players[1].health}/{game.players[1].max_health}")
    console.print(f"   总伤害计算: {initial_health - game.players[1].health} (应该是9)")
    console.print(f"   总治疗计算: {game.players[0].health - 30} (应该是5)")

    # 验证卡牌数据结构
    console.print(f"\n🔍 [bold cyan]卡牌数据结构验证：[/bold cyan]")
    if len(game.players[0].hand) > 0:
        card = game.players[0].hand[0]
        console.print(f"   手牌卡牌: {card}")
        console.print(f"   卡牌类型: {type(card)}")
        console.print(f"   卡牌属性: {card.__dict__ if hasattr(card, '__dict__') else 'N/A'}")

    return game.players[1].health == (initial_health - 9) and game.players[0].health == 35

if __name__ == "__main__":
    try:
        success = test_spell_damage_and_display()
        console.print(f"\n{'='*50}")
        if success:
            console.print("🎉 [bold green]所有测试通过！[/bold green]")
        else:
            console.print("❌ [bold red]测试失败，存在问题[/bold red]")
    except Exception as e:
        console.print(f"❌ [bold red]测试出错: {e}[/bold red]")
        import traceback
        console.print(traceback.format_exc())