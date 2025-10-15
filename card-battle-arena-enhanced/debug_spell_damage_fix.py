#!/usr/bin/env python3
"""
专门调查和修复法术伤害计算问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def debug_spell_damage():
    """调试法术伤害计算问题"""
    from rich.console import Console
    console = Console()

    console.print("🔍 [bold blue]法术伤害计算调试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    player = game.players[0]
    opponent = game.players[1]

    console.print(f"🎮 [bold cyan]初始状态：[/bold cyan]")
    console.print(f"   玩家血量: {player.health}")
    console.print(f"   对手血量: {opponent.health}")

    # 清空手牌并添加法术
    player.hand.clear()
    spell = Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火，对敌人造成3点伤害")
    player.hand.append(spell)
    player.mana = 10
    player.max_mana = 10

    console.print(f"\n📋 [bold yellow]添加法术：[/bold yellow]")
    console.print(f"   法术: {spell.name}")
    console.print(f"   攻击力: {spell.attack}")
    console.print(f"   描述: {spell.description}")

    # 记录对手初始血量
    initial_opponent_health = opponent.health
    console.print(f"\n🎯 [bold red]出牌前对手血量：[/bold red] {initial_opponent_health}")

    # 打出法术
    console.print(f"\n⚔️ [bold green]打出法术：[/bold green]")
    result = game.play_card(0, 0)  # 使用索引0，目标0（对手英雄）
    console.print(f"   结果: {result['message']}")

    # 检查对手血量变化
    final_opponent_health = opponent.health
    damage_dealt = initial_opponent_health - final_opponent_health
    console.print(f"\n💔 [bold red]伤害效果：[/bold red]")
    console.print(f"   对手最终血量: {final_opponent_health}")
    console.print(f"   实际造成伤害: {damage_dealt}")

    # 检查游戏状态
    state = game.get_game_state()
    opponent_state = state["opponent_state"]
    console.print(f"   游戏状态中对手血量: {opponent_state['health']}")

    # 分析问题
    console.print(f"\n🔧 [bold blue]问题分析：[/bold blue]")
    if damage_dealt == spell.attack:
        console.print(f"   ✅ [bold green]伤害计算正确！[/bold green]")
        console.print(f"   预期伤害: {spell.attack}, 实际伤害: {damage_dealt}")
    elif damage_dealt == 0:
        console.print(f"   ❌ [bold red]没有造成伤害！[/bold red]")
        console.print(f"   可能的原因:")
        console.print(f"   1. 法术伤害逻辑有问题")
        console.print(f"   2. 目标选择有问题")
        console.print(f"   3. 伤害应用逻辑有问题")
    else:
        console.print(f"   ⚠️ [bold yellow]伤害不匹配！[/bold yellow]")
        console.print(f"   预期伤害: {spell.attack}, 实际伤害: {damage_dealt}")

    # 检查游戏日志
    console.print(f"\n📝 [bold magenta]检查游戏日志：[/bold magenta]")
    if hasattr(game, 'game_log') and game.game_log:
        for log_entry in game.game_log[-5:]:  # 显示最后5条日志
            console.print(f"   {log_entry}")
    else:
        console.print("   没有游戏日志")

    # 检查CardGame的execute_spell_effect方法
    console.print(f"\n🔍 [bold cyan]检查法术执行逻辑：[/bold cyan]")
    console.print(f"   法术类型: {spell.card_type}")
    console.print(f"   法术攻击力: {spell.attack}")
    console.print(f"   法术效果: {spell.abilities_list}")

    # 尝试手动调用伤害逻辑
    console.print(f"\n🧪 [bold yellow]手动测试伤害逻辑：[/bold yellow]")
    test_health = 30
    test_damage = spell.attack
    final_health = test_health - test_damage
    console.print(f"   手动计算: {test_health} - {test_damage} = {final_health}")

    if final_health == opponent.health:
        console.print(f"   ✅ 手动计算与游戏结果一致")
    else:
        console.print(f"   ❌ 手动计算与游戏结果不一致")

if __name__ == "__main__":
    debug_spell_damage()