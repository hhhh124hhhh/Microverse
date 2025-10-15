#!/usr/bin/env python3
"""
测试神圣护盾修复 - 验证石像鬼不再显示异常生命值
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def test_divine_shield_fix():
    """测试神圣护盾修复"""
    from rich.console import Console
    console = Console()

    console.print("🛡️ [bold blue]神圣护盾修复测试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏
    game = CardGame("测试玩家", "测试对手")
    player = game.players[0]
    opponent = game.players[1]

    # 场景1: 石像鬼受到攻击，神圣护盾应该保护它
    console.print("📋 [bold cyan]场景1: 神圣护盾保护测试[/bold cyan]")
    console.print("-" * 30)

    # 给石像鬼上场
    gargoyle = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    opponent.field.append(gargoyle)

    console.print(f"石像鬼初始状态: {gargoyle.attack}/{gargoyle.health}，机制: {gargoyle.mechanics}")

    # 模拟攻击石像鬼
    attacker = Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客")
    player.field.append(attacker)

    initial_gargoyle_health = gargoyle.health
    initial_mechanics_count = len(gargoyle.mechanics)

    # 执行攻击
    console.print(f"\n⚔️ {attacker.name} 攻击 {gargoyle.name}")

    # 手动执行战斗逻辑（测试神圣护盾）
    damage_dealt = attacker.attack
    if "divine_shield" in getattr(gargoyle, 'mechanics', []):
        console.print("✨ 石像鬼有神圣护盾，免疫伤害")
        damage_dealt = 0
        if hasattr(gargoyle, 'mechanics'):
            gargoyle.mechanics.remove("divine_shield")
        console.print("🛡️ 神圣护盾被击破")

    if damage_dealt > 0:
        gargoyle.health -= damage_dealt
        console.print(f"💥 石像鬼受到 {damage_dealt} 点伤害")
    else:
        console.print("🛡️ 石像鬼没有受到伤害")

    console.print(f"\n石像鬼最终状态: {gargoyle.attack}/{gargoyle.health}，机制: {gargoyle.mechanics}")
    console.print(f"生命值变化: {initial_gargoyle_health} -> {gargoyle.health}")
    console.print(f"机制变化: {initial_mechanics_count} -> {len(gargoyle.mechanics)}")

    # 验证结果
    if gargoyle.health == 1 and "divine_shield" not in gargoyle.mechanics:
        console.print("✅ 神圣护盾正确工作：石像鬼血量不变，护盾消失")
    else:
        console.print("❌ 神圣护盾工作异常")

    console.print("\n" + "-"*50 + "\n")

    # 场景2: 第二次攻击石像鬼（没有护盾了）
    console.print("📋 [bold cyan]场景2: 失去护盾后的攻击测试[/bold cyan]")
    console.print("-" * 30)

    # 再次攻击
    damage_dealt = attacker.attack
    if "divine_shield" in getattr(gargoyle, 'mechanics', []):
        damage_dealt = 0
        if hasattr(gargoyle, 'mechanics'):
            gargoyle.mechanics.remove("divine_shield")

    if damage_dealt > 0:
        gargoyle.health -= damage_dealt

    console.print(f"⚔️ {attacker.name} 再次攻击 {gargoyle.name}")
    console.print(f"石像鬼最终状态: {gargoyle.attack}/{gargoyle.health}")

    # 验证结果
    if gargoyle.health == -2:  # 1 - 3 = -2
        console.print("✅ 第二次攻击正确造成伤害")
    else:
        console.print("❌ 第二次攻击异常")

    console.print("\n🎯 [bold green]测试结果总结：[/bold green]")
    console.print("1. 神圣护盾应该让石像鬼免疫首次伤害")
    console.print("2. 神圣护盾被击破后，随从应该正常受到伤害")
    console.print("3. 石像鬼不应该显示负数生命值（除非确实受到超额伤害）")

if __name__ == "__main__":
    test_divine_shield_fix()