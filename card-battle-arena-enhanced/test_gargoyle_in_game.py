#!/usr/bin/env python3
"""
测试石像鬼在真实游戏中的表现
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def test_gargoyle_in_game():
    """测试石像鬼在真实游戏中的表现"""
    from rich.console import Console
    console = Console()

    console.print("🗿 [bold blue]石像鬼真实游戏测试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏
    game = CardGame("测试玩家", "测试对手")
    player = game.players[0]
    opponent = game.players[1]

    # 给对手添加石像鬼
    gargoyle = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    opponent.field.append(gargoyle)

    # 给玩家添加一个攻击随从
    attacker = Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客")
    attacker.can_attack = True
    player.field.append(attacker)

    console.print(f"初始状态:")
    console.print(f"  {attacker.name} ({attacker.attack}/{attacker.health}) - 可攻击: {attacker.can_attack}")
    console.print(f"  {gargoyle.name} ({gargoyle.attack}/{gargoyle.health}) - 机制: {gargoyle.mechanics}")

    # 手动执行攻击测试神圣护盾
    console.print(f"\n⚔️ 执行攻击: {attacker.name} -> {gargoyle.name}")

    # 使用游戏的攻击函数
    result = game.attack_with_minion(0, 0, "随从_0")

    console.print(f"攻击结果: {result['message']}")
    console.print(f"石像鬼状态: {gargoyle.attack}/{gargoyle.health}，机制: {gargoyle.mechanics}")

    # 验证神圣护盾是否正确工作
    if gargoyle.health == 1 and "divine_shield" not in gargoyle.mechanics:
        console.print("✅ 神圣护盾正确：石像鬼血量不变，护盾消失")
    else:
        console.print("❌ 神圣护盾异常")

    # 再次攻击测试
    if gargoyle.health > 0:
        console.print(f"\n⚔️ 第二次攻击: {attacker.name} -> {gargoyle.name}")

        # 重置攻击状态
        attacker.can_attack = True

        result2 = game.attack_with_minion(0, 0, "随从_0")
        console.print(f"攻击结果: {result2['message']}")
        console.print(f"石像鬼最终状态: {gargoyle.attack}/{gargoyle.health}")

        if gargoyle.health < 1:
            console.print("✅ 第二次攻击正确造成伤害")
        else:
            console.print("❌ 第二次攻击异常")

    console.print(f"\n🎯 [bold green]修复验证：[/bold green]")
    console.print("石像鬼现在应该:")
    console.print("1. 首次攻击被神圣护盾保护，血量不变")
    console.print("2. 神圣护盾消失")
    console.print("3. 第二次攻击正常造成伤害")
    console.print("4. 不会再出现异常的负数生命值显示")

if __name__ == "__main__":
    test_gargoyle_in_game()