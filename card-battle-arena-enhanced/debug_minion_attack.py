#!/usr/bin/env python3
"""
调试随从攻击选项问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def debug_minion_attack():
    """调试随从攻击问题"""
    from rich.console import Console
    console = Console()

    console.print("🔍 [bold blue]调试随从攻击选项[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("调试玩家", "调试对手")
    current = game.get_current_player()

    console.print(f"🎮 [bold cyan]初始状态：[/bold cyan]")
    console.print(f"   法力值: {current.mana}/{current.max_mana}")
    console.print(f"   手牌数量: {len(current.hand)}")
    console.print(f"   场上随从: {len(current.field)}")

    # 清空手牌，添加石像鬼
    current.hand.clear()
    gargoyle = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    current.hand.append(gargoyle)

    console.print(f"\n📋 [bold yellow]添加石像鬼到手牌[/bold yellow]")
    console.print(f"   手牌: {[card.name for card in current.hand]}")
    console.print(f"   场上随从: {len(current.field)}")

    # 打出石像鬼
    console.print(f"\n⚔️ [bold green]打出石像鬼[/bold green]")
    result = game.play_card(0, 0)
    console.print(f"   结果: {result['message']}")
    console.print(f"   场上随从: {len(current.field)}")

    if current.field:
        minion = current.field[0]
        console.print(f"   随从状态: {minion.name} (can_attack={getattr(minion, 'can_attack', 'N/A')})")

        # 手动设置为可攻击（模拟下一回合）
        minion.can_attack = True
        console.print(f"   设置可攻击: {minion.name} (can_attack={minion.can_attack})")

        # 检查攻击逻辑
        from game_engine.card_game import get_minion_can_attack
        can_attack = get_minion_can_attack(minion, False)
        console.print(f"   检查可攻击: {can_attack}")

        # 获取可用命令
        commands = game.get_available_commands()
        console.print(f"\n📋 [bold magenta]可用命令：[/bold magenta]")
        for i, cmd in enumerate(commands):
            console.print(f"   {i+1}. {cmd}")

        # 检查具体逻辑
        console.print(f"\n🔧 [bold blue]详细检查：[/bold blue]")
        attackable_minions = [i for i, minion in enumerate(current.field)
                             if get_minion_can_attack(minion, False)]
        console.print(f"   可攻击随从索引: {attackable_minions}")
        console.print(f"   场上随从总数: {len(current.field)}")

        # 检查游戏状态
        state = game.get_game_state()
        current_state = state["current_player_state"]
        console.print(f"   游戏状态中的场上随从: {len(current_state['field'])}")
        for i, field_minion in enumerate(current_state['field']):
            console.print(f"     {i}: {field_minion['name']}")

    # 显示游戏界面
    console.print(f"\n🎮 [bold cyan]当前游戏界面：[/bold cyan]")
    game.display_status()

if __name__ == "__main__":
    debug_minion_attack()