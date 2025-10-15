#!/usr/bin/env python3
"""
简单的AI调试脚本，用于诊断AI卡住的问题
"""

import asyncio
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from game_engine.card_game import Card, CardGame
from ai_engine.agents.ai_agent import AIAgent
from ai_engine.agents.agent_personality import PersonalityProfile, PersonalityManager
from ai_engine.strategies.rule_based import RuleBasedStrategy

console = Console()

def create_test_game():
    """创建测试游戏"""
    game = CardGame()
    
    # 初始化玩家
    game.players[0].name = "玩家"
    game.players[1].name = "AI对手"
    
    # 设置初始状态
    game.players[0].health = 30
    game.players[1].health = 30
    game.players[0].mana = 5
    game.players[1].mana = 5
    game.players[0].max_mana = 5
    game.players[1].max_mana = 5
    
    return game

def create_simple_ai_agent():
    """创建简单的规则AI代理"""
    from ai_engine.agents.agent_personality import PlayStyle
    
    # 创建人格配置
    personality = PersonalityProfile(
        name="测试AI",
        description="用于调试的简单AI",
        traits=[],
        play_style=PlayStyle.MIDRANGE,
        risk_tolerance=0.5,
        aggression_level=0.5,
        patience_level=0.5,
        thinking_time_range=(0.1, 0.5),
        emotion_factor=0.5,
        learning_rate=0.1
    )
    
    # 创建规则策略
    strategy = RuleBasedStrategy("调试策略")
    
    # 创建AI代理
    ai_agent = AIAgent("test_debug_ai", personality, strategy)
    
    return ai_agent

async def test_simple_ai_decision():
    """测试简单AI决策"""
    console.print("[bold yellow]开始测试简单AI决策[/bold yellow]")
    
    # 创建游戏和AI
    game = create_test_game()
    ai_agent = create_simple_ai_agent()
    
    # 给AI添加一些测试卡牌
    test_cards = [
        Card("火球术", 4, 6, 0, "spell", [], "造成6点伤害"),
        Card("霜狼步兵", 2, 2, 3, "minion", ["taunt"], "嘲讽随从"),
        Card("治疗术", 2, 0, 5, "spell", [], "恢复5点生命")
    ]
    
    game.players[1].hand.clear()
    for card in test_cards:
        game.players[1].hand.append(card)
    
    # 设置足够的法力值
    game.players[1].mana = 10
    game.players[1].max_mana = 10
    
    console.print(f"\n[bold cyan]游戏状态:[/bold cyan]")
    console.print(f"  玩家血量: {game.players[0].health}")
    console.print(f"  AI血量: {game.players[1].health}")
    console.print(f"  AI法力: {game.players[1].mana}/{game.players[1].max_mana}")
    
    console.print(f"\n[bold green]AI手牌:[/bold green]")
    for i, card in enumerate(game.players[1].hand):
        console.print(f"  {i}. {card.name} ({card.cost}费) - {card.description}")
    
    # 测试AI决策
    console.print(f"\n[bold magenta]AI开始决策...[/bold magenta]")
    start_time = asyncio.get_event_loop().time()
    
    try:
        # 使用AI代理的决策方法
        action = ai_agent.decide_action(game.players[1], game)
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        
        if action:
            console.print(f"[bold green]✅ AI决策完成！[/bold green]")
            console.print(f"  动作类型: {action.action_type.value}")
            console.print(f"  置信度: {action.confidence:.2f}")
            console.print(f"  推理: {action.reasoning}")
            console.print(f"  耗时: {elapsed_time:.2f}秒")
        else:
            console.print(f"[bold red]❌ AI无法做出决策[/bold red]")
            console.print(f"  耗时: {elapsed_time:.2f}秒")
            
    except Exception as e:
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        console.print(f"[bold red]💥 AI决策出错: {e}[/bold red]")
        console.print(f"  耗时: {elapsed_time:.2f}秒")
        import traceback
        console.print(f"[red]详细错误信息:[/red]")
        console.print(traceback.format_exc())

if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.DEBUG)
    
    # 运行测试
    asyncio.run(test_simple_ai_decision())