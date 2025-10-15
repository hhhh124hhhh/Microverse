#!/usr/bin/env python3
"""
直接调用规则AI策略的调试脚本
"""

import asyncio
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from game_engine.card_game import Card
from ai_engine.strategies.rule_based import RuleBasedStrategy
from ai_engine.strategies.base import GameContext

console = Console()

def create_test_context():
    """创建测试上下文"""
    # 创建测试手牌
    player_hand = [
        {
            "name": "火球术",
            "cost": 4,
            "attack": 6,
            "health": 0,
            "card_type": "spell",
            "mechanics": [],
            "description": "造成6点伤害"
        },
        {
            "name": "霜狼步兵",
            "cost": 2,
            "attack": 2,
            "health": 3,
            "card_type": "minion",
            "mechanics": ["taunt"],
            "description": "嘲讽随从",
            "can_attack": False
        },
        {
            "name": "治疗术",
            "cost": 2,
            "attack": 0,
            "health": 5,
            "card_type": "spell",
            "mechanics": [],
            "description": "恢复5点生命"
        }
    ]
    
    # 创建测试场面
    player_field = []
    opponent_field = [
        {
            "name": "石像鬼",
            "cost": 1,
            "attack": 1,
            "health": 1,
            "card_type": "minion",
            "mechanics": [],
            "description": "基础随从",
            "can_attack": True
        }
    ]
    
    # 创建游戏上下文
    context = GameContext(
        game_id="test_game_001",
        current_player=1,
        turn_number=2,
        phase="main",
        player_hand=player_hand,
        player_field=player_field,
        opponent_field=opponent_field,
        player_mana=10,
        opponent_mana=3,
        player_health=30,
        opponent_health=24
    )
    
    return context

def test_rule_based_strategy_direct():
    """直接测试规则AI策略（同步方式）"""
    console.print("[bold yellow]开始直接测试规则AI策略[/bold yellow]")
    
    # 创建测试上下文
    context = create_test_context()
    
    console.print(f"\n[bold cyan]游戏上下文:[/bold cyan]")
    console.print(f"  玩家血量: {context.player_health}")
    console.print(f"  对手血量: {context.opponent_health}")
    console.print(f"  玩家法力: {context.player_mana}")
    console.print(f"  对手法力: {context.opponent_mana}")
    console.print(f"  回合数: {context.turn_number}")
    
    console.print(f"\n[bold green]玩家手牌:[/bold green]")
    for i, card in enumerate(context.player_hand):
        console.print(f"  {i}. {card['name']} ({card['cost']}费) - {card['description']}")
    
    console.print(f"\n[bold green]对手场面:[/bold green]")
    for i, card in enumerate(context.opponent_field):
        console.print(f"  {i}. {card['name']} ({card['attack']}/{card['health']})")
    
    # 创建规则AI策略
    strategy = RuleBasedStrategy("测试规则策略")
    
    # 测试AI决策
    console.print(f"\n[bold magenta]规则AI开始决策...[/bold magenta]")
    start_time = asyncio.get_event_loop().time()
    
    try:
        # 直接调用决策方法（不使用async）
        # 这里我们直接调用内部方法来诊断问题
        console.print(f"[dim]评估出牌动作...[/dim]")
        play_actions = strategy._evaluate_play_cards(context)
        console.print(f"[dim]找到 {len(play_actions)} 个出牌动作[/dim]")
        
        for action in play_actions:
            console.print(f"  - {action.action_type.value}: {action.reasoning} (置信度: {action.confidence:.2f})")
        
        console.print(f"[dim]评估攻击动作...[/dim]")
        attack_actions = strategy._evaluate_attacks(context)
        console.print(f"[dim]找到 {len(attack_actions)} 个攻击动作[/dim]")
        
        for action in attack_actions:
            console.print(f"  - {action.action_type.value}: {action.reasoning} (置信度: {action.confidence:.2f})")
        
        console.print(f"[dim]评估英雄技能...[/dim]")
        hero_action = strategy._evaluate_hero_power(context)
        if hero_action:
            console.print(f"  - {hero_action.action_type.value}: {hero_action.reasoning} (置信度: {hero_action.confidence:.2f})")
        else:
            console.print(f"  - 无英雄技能动作")
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        console.print(f"[bold green]✅ 规则AI评估完成！[/bold green]")
        console.print(f"  耗时: {elapsed_time:.2f}秒")
            
    except Exception as e:
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        console.print(f"[bold red]💥 规则AI评估出错: {e}[/bold red]")
        console.print(f"  耗时: {elapsed_time:.2f}秒")
        import traceback
        console.print(f"[red]详细错误信息:[/red]")
        console.print(traceback.format_exc())

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.DEBUG)
    
    # 运行测试
    test_rule_based_strategy_direct()