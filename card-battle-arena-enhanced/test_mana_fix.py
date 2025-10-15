#!/usr/bin/env python3
"""
测试玩家回合法力值问题
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

def test_mana_progression():
    """测试法力值增长"""
    console.print("🧪 [bold blue]测试法力值增长系统[/bold blue]")
    console.print("=" * 60)

    try:
        # 创建游戏
        game = CardGame("玩家", "AI")

        console.print(f"📋 [cyan]初始状态:[/cyan]")
        console.print(f"  玩家法力: {game.players[0].mana}/{game.players[0].max_mana}")
        console.print(f"  AI法力: {game.players[1].mana}/{game.players[1].max_mana}")

        # 模拟前几个回合
        for turn in range(1, 8):
            console.print(f"\n--- 回合 {turn} ---")

            # 玩家回合
            game.players[0].start_turn()
            console.print(f"玩家回合开始后法力: {game.players[0].mana}/{game.players[0].max_mana}")

            # 结束玩家回合
            game.end_turn(0)

            # AI回合
            game.players[1].start_turn()
            console.print(f"AI回合开始后法力: {game.players[1].mana}/{game.players[1].max_mana}")

            # 结束AI回合
            game.end_turn(1)

        console.print(f"\n✅ [green]法力值增长测试完成[/green]")

    except Exception as e:
        console.print(f"[red]💥 测试出错: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())

def test_ui_state_conversion():
    """测试UI状态转换中的法力值显示"""
    console.print("\n🧪 [bold blue]测试UI状态转换[/bold blue]")
    console.print("=" * 60)

    try:
        from game_ui import GameUIStatic

        # 创建UI实例
        ui = GameUIStatic()

        # 手动设置游戏状态
        ui.game_engine = CardGame("玩家", "AI")

        # 模拟进行到第7回合
        for _ in range(6):  # 进行6次完整的回合
            ui.game_engine.players[0].start_turn()
            ui.game_engine.end_turn(0)
            ui.game_engine.players[1].start_turn()
            ui.game_engine.end_turn(1)

        # 开始第7回合（玩家回合）
        ui.game_engine.players[0].start_turn()

        console.print(f"📋 [cyan]游戏引擎状态 (回合7):[/cyan]")
        console.print(f"  玩家法力: {ui.game_engine.players[0].mana}/{ui.game_engine.players[0].max_mana}")
        console.print(f"  AI法力: {ui.game_engine.players[1].mana}/{ui.game_engine.players[1].max_mana}")

        # 转换为UI状态
        ui_state = ui._convert_engine_state_to_ui_state()

        console.print(f"\n📋 [cyan]UI状态转换结果:[/cyan]")
        player_state = ui_state.get('player', {})
        opponent_state = ui_state.get('opponent', {})

        console.print(f"  玩家法力 (UI): {player_state.get('mana', 0)}/{player_state.get('max_mana', 0)}")
        console.print(f"  AI法力 (UI): {opponent_state.get('mana', 0)}/{opponent_state.get('max_mana', 0)}")

        # 检查是否一致
        engine_mana = ui.game_engine.players[0].mana
        ui_mana = player_state.get('mana', 0)

        if engine_mana == ui_mana:
            console.print(f"[green]✅ 法力值显示一致[/green]")
        else:
            console.print(f"[red]❌ 法力值显示不一致！[/red]")
            console.print(f"  游戏引擎: {engine_mana}")
            console.print(f"  UI显示: {ui_mana}")

    except Exception as e:
        console.print(f"[red]💥 UI状态转换测试出错: {e}[/red]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    test_mana_progression()
    test_ui_state_conversion()