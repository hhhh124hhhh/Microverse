#!/usr/bin/env python3
"""
调试随从攻击状态问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def debug_minion_attack_state():
    """调试随从攻击状态问题"""
    from rich.console import Console
    console = Console()

    console.print("🔍 [bold blue]随从攻击状态调试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试对手")
    player = game.players[0]
    opponent = game.players[1]

    # 添加随从到对手场上
    minion1 = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    minion2 = Card("鹰身女妖", 2, 2, 1, "minion", ["ranged"], "🦅 天空的猎手")

    opponent.field.append(minion1)
    opponent.field.append(minion2)

    # 测试场景1: 新上场的随从
    console.print("📋 [bold cyan]场景1: 新上场的随从[/bold cyan]")
    console.print("-" * 30)

    # 添加随从到玩家场上（新上场）
    player_minion = Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客")
    player.field.append(player_minion)

    # 检查攻击状态
    console.print(f"玩家随从数量: {len(player.field)}")
    for i, minion in enumerate(player.field):
        can_attack = getattr(minion, 'can_attack', False)
        console.print(f"  随从 {i} ({minion.name}) can_attack: {can_attack}")

    # 检查对手随从状态
    console.print(f"\n对手随从数量: {len(opponent.field)}")
    for i, minion in enumerate(opponent.field):
        can_attack = getattr(minion, 'can_attack', False)
        console.print(f"  随从 {i} ({minion.name}) can_attack: {can_attack}")

    # 结束回合（应该激活随从攻击状态）
    console.print(f"\n🔄 [yellow]结束玩家回合，激活AI回合[/yellow]")
    game.end_turn(0)

    # 测试场景2: AI回合后的随从状态
    console.print("\n📋 [bold cyan]场景2: AI回合后的随从状态[/bold cyan]")
    console.print("-" * 30)

    # 检查玩家随从状态（应该激活）
    console.print(f"玩家随从数量: {len(player.field)}")
    for i, minion in enumerate(player.field):
        can_attack = getattr(minion, 'can_attack', False)
        console.print(f"  随从 {i} ({minion.name}) can_attack: {can_attack}")

    # 检查对手随从状态（应该激活）
    console.print(f"\n对手随从数量: {len(opponent.field)}")
    for i, minion in enumerate(opponent.field):
        can_attack = getattr(minion, 'can_attack', False)
        console.print(f"  随从 {i} ({minion.name}) can_attack: {can_attack}")

    # 结束AI回合，回到玩家回合
    console.print(f"\n🔄 [yellow]结束AI回合，回到玩家回合[/yellow]")
    game.end_turn(1)

    # 测试场景3: 回到玩家回合后的状态
    console.print("\n📋 [bold cyan]场景3: 回到玩家回合后的随从状态[/bold cyan]")
    console.print("-" * 30)

    # 检查玩家随从状态（应该保持激活）
    console.print(f"玩家随从数量: {len(player.field)}")
    for i, minion in enumerate(player.field):
        can_attack = getattr(minion, 'can_attack', False)
        console.print(f"  随从 {i} ({minion.name}) can_attack: {can_attack}")

    # 检查对手随从状态（应该保持激活）
    console.print(f"\n对手随从数量: {len(opponent.field)}")
    for i, minion in enumerate(opponent.field):
        can_attack = getattr(minion, 'can_attack', False)
        console.print(f"  随从 {i} ({minion.name}) can_attack: {can_attack}")

    # 再次结束回合，测试攻击逻辑
    console.print(f"\n🔄 [yellow]再次结束玩家回合，测试战斗逻辑[/yellow]")
    initial_health = player.health
    initial_opponent_health = opponent.health

    # 模拟战斗
    messages = game._smart_combat_phase()

    console.print(f"战斗消息: {messages}")
    console.print(f"玩家血量: {player.health} -> {initial_health}")
    console.print(f"对手血量: {opponent.health} -> {initial_opponent_health}")

    console.print("\n🔧 [bold green]问题分析：[/bold green]")
    console.print("1. 新上场的随从应该设置为 can_attack = False")
    console.print("2. 回合开始时应该激活随从的 can_attack = True")
    console.print("3. 战斗阶段不应该重置攻击状态")
    console.print("4. 只有 can_attack = True 的随从才能攻击")

if __name__ == "__main__":
    debug_minion_attack_state()