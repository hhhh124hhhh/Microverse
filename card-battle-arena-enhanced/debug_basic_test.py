#!/usr/bin/env python3
"""
基本功能测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console

console = Console()

def test_basic_functionality():
    """测试基本功能"""
    console.print("[bold green]✅ 基本功能测试开始[/bold green]")
    
    # 测试导入
    try:
        from game_engine.card_game import Card
        console.print("[bold blue]✅ Card类导入成功[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]❌ Card类导入失败: {e}[/bold red]")
        return
    
    try:
        from ai_engine.strategies.rule_based import RuleBasedStrategy
        console.print("[bold blue]✅ RuleBasedStrategy类导入成功[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]❌ RuleBasedStrategy类导入失败: {e}[/bold red]")
        return
    
    try:
        from ai_engine.strategies.base import GameContext
        console.print("[bold blue]✅ GameContext类导入成功[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]❌ GameContext类导入失败: {e}[/bold red]")
        return
    
    # 测试创建对象
    try:
        card = Card("测试卡牌", 3, 2, 3, "minion", [], "测试描述")
        console.print("[bold blue]✅ Card对象创建成功[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]❌ Card对象创建失败: {e}[/bold red]")
        return
    
    try:
        strategy = RuleBasedStrategy("测试策略")
        console.print("[bold blue]✅ RuleBasedStrategy对象创建成功[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]❌ RuleBasedStrategy对象创建失败: {e}[/bold red]")
        return
    
    try:
        context = GameContext(
            game_id="test_001",
            current_player=0,
            turn_number=1,
            phase="main",
            player_hand=[],
            player_field=[],
            opponent_field=[],
            player_mana=5,
            opponent_mana=5,
            player_health=30,
            opponent_health=30
        )
        console.print("[bold blue]✅ GameContext对象创建成功[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]❌ GameContext对象创建失败: {e}[/bold red]")
        return
    
    console.print("[bold green]🎉 所有基本功能测试通过！[/bold green]")

if __name__ == "__main__":
    test_basic_functionality()