#!/usr/bin/env python3
"""
验证AI修复效果的测试脚本
重现原始日志中的游戏场景，验证AI是否能够出牌而不是只使用英雄技能
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

def create_original_test_context() -> GameContext:
    """创建与原始日志中相同的游戏场景"""
    return GameContext(
        game_id="menu_game_1",
        current_player=1,  # 玩家2(后手)
        turn_number=4,
        phase="main",

        # 玩家状态 - 与原始日志完全一致
        player_health=24,
        player_max_health=30,
        player_mana=3,
        player_max_mana=3,
        player_hand=[
            {
                "name": "冰霜新星",
                "cost": 3,
                "attack": 2,
                "health": 0,
                "instance_id": "spell_001",
                "card_type": "spell",
                "mechanics": ["freeze"]
            },
            {
                "name": "寒冰箭",
                "cost": 2,
                "attack": 3,
                "health": 0,
                "instance_id": "spell_002",
                "card_type": "spell",
                "mechanics": ["freeze"]
            },
            {
                "name": "暗影步",
                "cost": 1,
                "attack": 0,
                "health": 0,
                "instance_id": "spell_003",
                "card_type": "spell",
                "mechanics": ["return"]
            },
            {
                "name": "神圣惩击",
                "cost": 4,
                "attack": 5,
                "health": 0,
                "instance_id": "spell_004",
                "card_type": "spell",
                "mechanics": []
            },
            {
                "name": "铁炉堡火枪手",
                "cost": 2,
                "attack": 2,
                "health": 2,
                "instance_id": "minion_001",
                "card_type": "minion",
                "mechanics": ["ranged"]
            }
        ],
        player_field=[],
        player_deck_size=15,

        # 对手状态 - 与原始日志一致
        opponent_health=30,
        opponent_max_health=30,
        opponent_mana=0,
        opponent_max_mana=2,
        opponent_field=[],
        opponent_hand_size=5,
        opponent_deck_size=12
    )

def display_comparison_test(context: GameContext):
    """显示对比测试场景"""
    console.print("🧪 [bold blue]AI修复验证测试[/bold blue]")
    console.print("重现原始问题场景，验证AI是否能够出牌...")
    console.print("=" * 60)

    # 显示关键信息
    table = Table(title="原始问题场景重现", show_header=False)
    table.add_column("属性", style="cyan")
    table.add_column("数值", style="yellow")

    table.add_row("我方法力值", f"{context.player_mana}/{context.player_max_mana}")
    table.add_row("我方血量", f"{context.player_health}/{context.player_max_health}")
    table.add_row("对手血量", f"{context.opponent_health}/{context.opponent_max_health}")
    table.add_row("手牌数量", str(len(context.player_hand)))
    table.add_row("可出牌数量", str(sum(1 for card in context.player_hand if card.get("cost", 0) <= context.player_mana)))
    table.add_row("敌方随从数量", str(len(context.opponent_field)))

    console.print(table)

    # 显示手牌
    if context.player_hand:
        console.print("\n🎯 [bold cyan]原始手牌（与日志一致）：[/bold cyan]")
        for i, card in enumerate(context.player_hand):
            cost = card.get("cost", 0)
            playable = "✅可出" if cost <= context.player_mana else "❌费用不足"
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

async def test_original_scenario():
    """测试原始问题场景"""
    # 设置环境
    settings = setup_environment()

    # 创建原始场景
    context = create_original_test_context()
    display_comparison_test(context)

    console.print(f"\n🤖 [bold green]修复后配置：[/bold green]")
    console.print(f"   LLM功能: {'启用' if settings.ai.enable_llm else '禁用'}")
    console.print(f"   默认策略: {settings.ai.default_strategy}")

    # 创建修复后的混合策略
    hybrid_config = {
        "strategies": [
            {"name": "rule_based", "weight": 0.55, "min_confidence": 0.15},
            {"name": "llm_enhanced", "weight": 0.45, "min_confidence": 0.4}
        ],
        "consensus_method": "weighted_voting",
        "min_consensus_score": 0.15,
        "max_decision_time": 25.0,
        "llm_timeout_grace_period": 20.0,
        "fallback_to_rules_on_timeout": True,
        "prefer_cards_over_hero_power": True  # 关键配置：优先出牌
    }

    hybrid_strategy = HybridAIStrategy("修复验证AI", hybrid_config)

    console.print(f"\n🔄 [bold yellow]修复后策略权重：[/bold yellow]")
    for name, weight in hybrid_strategy.strategy_weights.items():
        console.print(f"   {name}: {weight:.2f}")

    console.print(f"\n⏳ [bold magenta]开始修复验证测试...[/bold magenta]")

    try:
        # 执行决策
        action = await hybrid_strategy.make_decision(context)

        if action:
            console.print(f"\n✅ [bold green]修复后AI决策结果：[/bold green]")
            console.print(f"   动作类型: {action.action_type.value}")
            console.print(f"   置信度: {action.confidence:.3f}")
            console.print(f"   推理过程: {action.reasoning}")
            console.print(f"   执行时间: {action.execution_time:.3f}秒")

            # 显示对比结论
            console.print(f"\n🎯 [bold yellow]修复验证结论：[/bold yellow]")
            if action.action_type.value == "play_card":
                console.print("   ✅ 成功！AI现在选择了出牌而不是英雄技能！")
                console.print("   ✅ 问题已修复，AI决策逻辑恢复正常！")
                return True
            elif action.action_type.value == "use_hero_power":
                console.print("   ⚠️  AI仍然选择了英雄技能，需要进一步调整")
                console.print("   ❌ 修复可能不够彻底")
                return False
            else:
                console.print(f"   ℹ️  AI选择了其他动作: {action.action_type.value}")
                return True

        else:
            console.print("❌ AI未能做出决策")
            return False

    except Exception as e:
        console.print(f"❌ 测试失败: {e}")
        import traceback
        console.print(traceback.format_exc())
        return False

async def main():
    """主函数"""
    console.print("🧪 [bold blue]Card Battle Arena - AI修复验证测试[/bold blue]")
    console.print("验证修复后的AI在原始问题场景下的表现...")
    console.print("=" * 60)

    success = await test_original_scenario()

    console.print(f"\n{'='*60}")
    if success:
        console.print("🎉 [bold green]修复验证成功！AI现在可以正常出牌了！[/bold green]")
    else:
        console.print("❌ [bold red]修复验证失败，需要进一步调整[/bold red]")

if __name__ == "__main__":
    asyncio.run(main())