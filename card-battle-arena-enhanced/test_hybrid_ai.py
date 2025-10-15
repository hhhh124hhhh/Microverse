#!/usr/bin/env python3
"""
测试混合AI策略的决策效果
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_engine.strategies.hybrid import HybridAIStrategy
from game_engine.game_state.game_context import GameContext
from config.settings import setup_environment
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

def create_test_context() -> GameContext:
    """创建测试游戏上下文，包含各种情况的卡牌"""
    return GameContext(
        game_id="test_hybrid_ai",
        current_player=0,
        turn_number=8,
        phase="main",

        # 玩家状态 - 复杂的手牌配置
        player_health=20,
        player_max_health=30,
        player_mana=7,
        player_max_mana=7,
        player_hand=[
            {
                "name": "神圣惩击",
                "cost": 4,
                "attack": 5,
                "instance_id": "spell_001",
                "card_type": "spell",
                "mechanics": []
            },
            {
                "name": "炎爆术",
                "cost": 6,
                "attack": 10,
                "instance_id": "spell_002",
                "card_type": "spell",
                "mechanics": []
            },
            {
                "name": "暴风雪",
                "cost": 8,
                "attack": 0,
                "instance_id": "spell_003",
                "card_type": "spell",
                "mechanics": ["freeze"]
            },
            {
                "name": "铁甲战士",
                "cost": 3,
                "attack": 2,
                "health": 5,
                "instance_id": "minion_001",
                "card_type": "minion",
                "mechanics": ["taunt"]
            },
            {
                "name": "利爪德鲁伊",
                "cost": 5,
                "attack": 4,
                "health": 4,
                "instance_id": "minion_002",
                "card_type": "minion",
                "mechanics": ["charge"]
            }
        ],
        player_field=[
            {
                "name": "狼人渗透者",
                "attack": 3,
                "health": 2,
                "instance_id": "minion_003",
                "can_attack": True,
                "mechanics": ["stealth"]
            }
        ],
        player_deck_size=15,

        # 对手状态 - 强大的场面压力
        opponent_health=15,
        opponent_max_health=30,
        opponent_mana=6,
        opponent_max_mana=6,
        opponent_field=[
            {
                "name": "霜狼步兵",
                "attack": 4,
                "health": 3,
                "instance_id": "opp_minion_001",
                "can_attack": True,
                "mechanics": ["taunt"]
            },
            {
                "name": "石像鬼",
                "attack": 2,
                "health": 2,
                "instance_id": "opp_minion_002",
                "can_attack": True,
                "mechanics": ["divine_shield"]
            },
            {
                "name": "冰霜元素",
                "attack": 2,
                "health": 4,
                "instance_id": "opp_minion_003",
                "can_attack": False,
                "mechanics": ["freeze"]
            }
        ],
        opponent_hand_size=3,
        opponent_deck_size=12
    )

def display_test_context(context: GameContext):
    """显示测试上下文"""
    console.print("🧪 [bold blue]混合AI策略测试场景[/bold blue]")
    console.print("=" * 60)

    # 显示关键信息
    table = Table(title="测试场景设置", show_header=False)
    table.add_column("属性", style="cyan")
    table.add_column("数值", style="yellow")

    table.add_row("我方法力值", f"{context.player_mana}/{context.player_max_mana}")
    table.add_row("我方血量", f"{context.player_health}/{context.player_max_health}")
    table.add_row("对手血量", f"{context.opponent_health}/{context.opponent_max_health}")
    table.add_row("手牌数量", str(len(context.player_hand)))
    table.add_row("可出牌数量", str(sum(1 for card in context.player_hand if card.get("cost", 0) <= context.player_mana)))
    table.add_row("敌方随从数量", str(len(context.opponent_field)))
    table.add_row("敌方总攻击力", str(sum(m.get("attack", 0) for m in context.opponent_field)))

    console.print(table)

    # 显示手牌
    if context.player_hand:
        console.print("\n🎯 [bold cyan]测试手牌：[/bold cyan]")
        for i, card in enumerate(context.player_hand):
            cost = card.get("cost", 0)
            playable = "✅" if cost <= context.player_mana else "❌"
            attack = card.get("attack", 0)
            health = card.get("health", 0)
            mechanics = ", ".join(card.get("mechanics", []))

            card_info = f"{playable} {card.get('name')} ({cost}费)"
            if attack > 0:
                card_info += f" - {attack}攻击"
            if health > 0:
                card_info += f" {health}血量"
            if mechanics:
                card_info += f" [{mechanics}]"

            console.print(f"  {i+1}. {card_info}")

async def test_hybrid_strategy():
    """测试混合策略"""
    # 设置环境
    settings = setup_environment()

    # 创建测试上下文
    context = create_test_context()
    display_test_context(context)

    console.print(f"\n🤖 [bold green]配置信息：[/bold green]")
    console.print(f"   LLM功能: {'启用' if settings.ai.enable_llm else '禁用'}")
    console.print(f"   默认策略: {settings.ai.default_strategy}")

    # 创建混合策略
    hybrid_config = {
        "strategies": [
            {"name": "rule_based", "weight": 0.7, "min_confidence": 0.2},
            {"name": "llm_enhanced", "weight": 0.3, "min_confidence": 0.6}
        ],
        "consensus_method": "weighted_voting",
        "min_consensus_score": 0.2,
        "max_decision_time": 20.0,
        "llm_timeout_grace_period": 12.0,
        "fallback_to_rules_on_timeout": True
    }

    hybrid_strategy = HybridAIStrategy("测试混合AI", hybrid_config)

    console.print(f"\n🔄 [bold yellow]混合策略配置：[/bold yellow]")
    for name, weight in hybrid_strategy.strategy_weights.items():
        console.print(f"   {name}: {weight:.1f}")

    console.print(f"\n⏳ [bold magenta]开始AI决策测试...[/bold magenta]")

    try:
        # 执行决策
        action = await hybrid_strategy.make_decision(context)

        if action:
            console.print(f"\n✅ [bold green]AI决策结果：[/bold green]")
            console.print(f"   动作类型: {action.action_type.value}")
            console.print(f"   置信度: {action.confidence:.3f}")
            console.print(f"   推理过程: {action.reasoning}")
            console.print(f"   执行时间: {action.execution_time:.3f}秒")

            # 获取性能统计
            stats = hybrid_strategy.get_performance_stats()
            console.print(f"\n📊 [bold cyan]性能统计：[/bold cyan]")
            console.print(f"   决策次数: {stats.get('decisions_made', 0)}")
            console.print(f"   共识失败: {stats.get('consensus_failures', 0)}")
            console.print(f"   平均共识分数: {stats.get('average_consensus_score', 0):.3f}")

            console.print(f"\n🎯 [bold yellow]测试结论：[/bold yellow]")
            if action.action_type.value == "play_card":
                console.print("   ✅ AI成功选择了出牌，而不是英雄技能！")
                console.print("   ✅ 修复成功，AI决策逻辑正常工作！")
            else:
                console.print(f"   ⚠️  AI选择了: {action.action_type.value}")

        else:
            console.print("❌ AI未能做出决策")

    except Exception as e:
        console.print(f"❌ 测试失败: {e}")
        import traceback
        console.print(traceback.format_exc())

async def main():
    """主函数"""
    console.print("🧪 [bold blue]Card Battle Arena - 混合AI策略测试[/bold blue]")
    console.print("验证修复后的AI决策效果...")
    console.print("=" * 60)

    await test_hybrid_strategy()

if __name__ == "__main__":
    asyncio.run(main())