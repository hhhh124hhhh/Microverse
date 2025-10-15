#!/usr/bin/env python3
"""
模拟用户可能遇到的真实场景 - 调试随从攻击选项显示问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def debug_real_scenario():
    """调试真实游戏场景中的随从攻击选项显示"""
    from rich.console import Console
    console = Console()

    console.print("🎯 [bold blue]真实场景调试 - 随从攻击选项显示[/bold blue]")
    console.print("=" * 50)

    # 场景1: 手中有可出牌 + 场上有可攻击随从
    console.print("📋 [bold cyan]场景1: 手中有可出牌 + 场上有可攻击随从[/bold cyan]")
    game = CardGame("测试玩家", "测试对手")
    player = game.players[0]

    # 添加法术到手牌（可出牌）
    player.hand.clear()
    spell = Card("狂野之怒", 1, 3, 0, "spell", [], "💢 释放原始怒火")
    player.hand.append(spell)
    player.mana = 10

    # 添加随从到场上并设置为可攻击
    minion = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    minion.can_attack = True
    player.field.append(minion)

    console.print(f"手牌数量: {len(player.hand)} (可出牌: {len([c for c in player.hand if c.cost <= player.mana])})")
    console.print(f"场上随从: {len(player.field)} (可攻击: {len([m for m in player.field if getattr(m, 'can_attack', False)])})")

    hints = game.get_simple_input_hints()
    console.print(f"底部提示: {hints}")
    has_attack_hint = "攻击" in hints  # 修复检测逻辑
    console.print(f"攻击提示显示: {'✅ 是' if has_attack_hint else '❌ 否'}")

    console.print("\n" + "-"*50 + "\n")

    # 场景2: 手中无牌 + 场上有可攻击随从
    console.print("📋 [bold cyan]场景2: 手中无牌 + 场上有可攻击随从[/bold cyan]")
    player.hand.clear()  # 清空手牌

    console.print(f"手牌数量: {len(player.hand)} (可出牌: {len([c for c in player.hand if c.cost <= player.mana])})")
    console.print(f"场上随从: {len(player.field)} (可攻击: {len([m for m in player.field if getattr(m, 'can_attack', False)])})")

    hints = game.get_simple_input_hints()
    console.print(f"底部提示: {hints}")
    has_attack_hint = "攻击" in hints  # 修复检测逻辑
    console.print(f"攻击提示显示: {'✅ 是' if has_attack_hint else '❌ 否'}")

    console.print("\n" + "-"*50 + "\n")

    # 场景3: 手中有可出牌 + 场上无随从
    console.print("📋 [bold cyan]场景3: 手中有可出牌 + 场上无随从[/bold cyan]")
    player.hand.append(spell)  # 重新添加法术
    player.field.clear()  # 清空场上

    console.print(f"手牌数量: {len(player.hand)} (可出牌: {len([c for c in player.hand if c.cost <= player.mana])})")
    console.print(f"场上随从: {len(player.field)}")

    hints = game.get_simple_input_hints()
    console.print(f"底部提示: {hints}")
    has_attack_hint = "攻击" in hints  # 修复检测逻辑
    console.print(f"攻击提示显示: {'✅ 是' if has_attack_hint else '❌ 否'}")

    console.print("\n" + "-"*50 + "\n")

    # 显示完整游戏界面
    console.print("📋 [bold magenta]完整游戏界面演示：[/bold magenta]")
    # 恢复场景1的状态
    player.hand.append(spell)
    minion.can_attack = True
    player.field.append(minion)

    game.display_status()

    console.print(f"\n🔍 [bold yellow]问题分析：[/bold yellow]")
    console.print("如果攻击选项没有显示，可能的原因：")
    console.print("1. 手牌优先级更高，攻击提示被覆盖")
    console.print("2. 随从的can_attack属性设置有问题")
    console.print("3. 提示文本被截断（终端宽度问题）")

if __name__ == "__main__":
    debug_real_scenario()