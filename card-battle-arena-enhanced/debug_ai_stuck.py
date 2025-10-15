#!/usr/bin/env python3
"""
调试AI卡住问题
"""
import sys
from pathlib import Path
import asyncio
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card
from ai_engine.agents.ai_agent import AIAgent
from ai_engine.strategies.hybrid import HybridAIStrategy
from ai_engine.agents.agent_personality import PersonalityProfile, PersonalityTrait, PlayStyle
from rich.console import Console

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

console = Console()

def create_test_game_with_ai():
    """创建测试游戏和AI代理"""
    console.print("🧪 [bold blue]创建测试游戏和AI代理[/bold blue]")
    
    # 创建游戏
    game = CardGame("测试玩家", "AI对手")
    
    # 创建AI策略
    strategy = HybridAIStrategy("测试混合AI")
    
    # 创建AI人格
    personality = PersonalityProfile(
        name="测试AI",
        description="用于测试的AI人格",
        traits=[PersonalityTrait.ADAPTIVE],
        play_style=PlayStyle.MIDRANGE,
        aggression_level=0.5,
        risk_tolerance=0.5,
        emotion_factor=0.5,
        learning_rate=0.1,
        thinking_time_range=(0.1, 0.5)
    )
    
    # 创建AI代理
    ai_agent = AIAgent("test_ai", personality, strategy)
    
    return game, ai_agent

async def test_ai_decision():
    """测试AI决策过程"""
    console.print("🎯 [bold yellow]开始测试AI决策过程[/bold yellow]")
    
    # 创建测试游戏和AI
    game, ai_agent = create_test_game_with_ai()
    
    # 显示初始状态
    console.print(f"📋 [bold cyan]初始游戏状态：[/bold cyan]")
    console.print(f"   玩家血量: {game.players[0].health}")
    console.print(f"   AI血量: {game.players[1].health}")
    console.print(f"   玩家法力: {game.players[0].mana}/{game.players[0].max_mana}")
    console.print(f"   AI法力: {game.players[1].mana}/{game.players[1].max_mana}")
    
    # 给AI添加一些卡牌
    ai_cards = [
        Card("火球术", 4, 6, 0, "spell", [], "造成6点伤害"),
        Card("霜狼步兵", 2, 2, 3, "minion", ["taunt"], "嘲讽随从"),
        Card("治疗术", 2, -5, 0, "spell", [], "恢复5点生命")
    ]
    
    game.players[1].hand.clear()
    for card in ai_cards:
        game.players[1].hand.append(card)
    
    # 设置足够的法力值
    game.players[1].mana = 10
    game.players[1].max_mana = 10
    
    console.print(f"\n🃏 [bold green]AI手牌：[/bold green]")
    for i, card in enumerate(game.players[1].hand):
        console.print(f"   {i}. {card.name} ({card.cost}费)")
    
    # 让AI进行决策
    console.print(f"\n🤖 [bold magenta]AI开始决策...[/bold magenta]")
    start_time = asyncio.get_event_loop().time()
    
    try:
        # 使用AI代理的决策方法
        action = ai_agent.decide_action(game.players[1], game)
        
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        
        if action:
            console.print(f"✅ [bold green]AI决策完成！[/bold green]")
            console.print(f"   动作类型: {action.action_type.value}")
            console.print(f"   置信度: {action.confidence:.2f}")
            console.print(f"   推理: {action.reasoning}")
            console.print(f"   耗时: {elapsed_time:.2f}秒")
        else:
            console.print(f"❌ [bold red]AI无法做出决策[/bold red]")
            console.print(f"   耗时: {elapsed_time:.2f}秒")
            
    except Exception as e:
        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time
        console.print(f"💥 [bold red]AI决策出错: {e}[/bold red]")
        console.print(f"   耗时: {elapsed_time:.2f}秒")
        import traceback
        console.print(f"   详细错误: {traceback.format_exc()}")

def main():
    """主函数"""
    console.print("🔍 [bold blue]AI卡住问题调试工具[/bold blue]")
    console.print("=" * 50)
    
    # 运行异步测试
    asyncio.run(test_ai_decision())
    
    console.print(f"\n🎯 [bold yellow]测试完成[/bold yellow]")

if __name__ == "__main__":
    main()