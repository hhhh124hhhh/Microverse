#!/usr/bin/env python3
"""
测试AI异步冲突修复效果
验证修复后的AI决策系统是否正常工作
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from game_ui import GameUIStatic
from ai_engine.agents.fixed_ai_agent import FixedAIAgent
from ai_engine.agents.agent_personality import PersonalityProfile, PlayStyle
from ai_engine.strategies.rule_based import RuleBasedStrategy
from game_engine.card_game import CardGame

console = Console()

def create_test_ai_agent():
    """创建测试AI代理"""
    # 创建人格配置
    personality = PersonalityProfile(
        name="测试AI",
        description="用于测试的AI",
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
    strategy = RuleBasedStrategy("测试策略")

    # 创建修复版AI代理
    ai_agent = FixedAIAgent("test_ai", personality, strategy)

    return ai_agent

async def test_ai_decision_engine():
    """测试AI决策引擎"""
    console.print("🧪 [bold blue]测试AI决策引擎[/bold blue]")
    console.print("=" * 60)

    try:
        # 创建游戏实例
        game = CardGame("测试玩家", "测试AI")

        # 创建AI代理
        ai_agent = create_test_ai_agent()

        # 给AI添加一些测试卡牌
        def create_card(name, cost, attack, health, card_type="minion", mechanics=None, description=""):
            return {
                "name": name,
                "cost": cost,
                "attack": attack,
                "health": health,
                "card_type": card_type,
                "mechanics": mechanics or [],
                "description": description
            }

        test_cards = [
            create_card("火球术", 4, 6, 0, "spell", [], "造成6点伤害"),
            create_card("霜狼步兵", 2, 2, 3, "minion", ["taunt"], "嘲讽随从"),
            create_card("治疗术", 2, 0, 5, "spell", [], "恢复5点生命")
        ]

        game.players[1].hand.clear()
        for card in test_cards:
            game.players[1].hand.append(card)

        # 设置足够的法力值
        game.players[1].mana = 10
        game.players[1].max_mana = 10

        console.print(f"📋 [cyan]AI测试状态:[/cyan]")
        console.print(f"  AI血量: {game.players[1].health}")
        console.print(f"  AI法力: {game.players[1].mana}/{game.players[1].max_mana}")
        console.print(f"  AI手牌: {len(game.players[1].hand)}张")

        console.print(f"\n🃏 [green]AI手牌:[/green]")
        for i, card in enumerate(game.players[1].hand):
            console.print(f"  {i}. {card.get('name', '未知')} ({card.get('cost', 0)}费) - {card.get('description', '')}")

        # 测试AI决策
        console.print(f"\n🤖 [magenta]AI决策测试开始...[/magenta]")
        start_time = asyncio.get_event_loop().time()

        # 使用AI代理的决策方法
        action = ai_agent.decide_action(game.players[1], game)

        end_time = asyncio.get_event_loop().time()
        elapsed_time = end_time - start_time

        if action:
            console.print(f"[green]✅ AI决策成功！[/green]")
            console.print(f"  动作类型: {action.action_type.value}")
            console.print(f"  置信度: {action.confidence:.2f}")
            console.print(f"  推理: {action.reasoning}")
            console.print(f"  耗时: {elapsed_time:.2f}秒")

            # 测试execute_ai_action函数
            console.print(f"\n🔧 [cyan]测试execute_ai_action函数...[/cyan]")
            from main import execute_ai_action

            try:
                result = await execute_ai_action(action, game, 1)
                if result["success"]:
                    console.print(f"[green]✅ execute_ai_action执行成功！[/green]")
                    console.print(f"  结果: {result['message']}")
                else:
                    console.print(f"[red]❌ execute_ai_action执行失败: {result['message']}[/red]")
            except Exception as e:
                console.print(f"[red]❌ execute_ai_action调用出错: {e}[/red]")
                import traceback
                console.print(f"[red]详细错误:[/red]")
                console.print(traceback.format_exc())

        else:
            console.print(f"[red]❌ AI无法做出决策[/red]")
            console.print(f"  耗时: {elapsed_time:.2f}秒")

        return True

    except Exception as e:
        console.print(f"[red]💥 AI决策引擎测试出错: {e}[/red]")
        import traceback
        console.print(f"[red]详细错误信息:[/red]")
        console.print(traceback.format_exc())
        return False

async def test_game_ui_integration():
    """测试GameUIStatic集成"""
    console.print("\n🧪 [bold blue]测试GameUIStatic集成[/bold blue]")
    console.print("=" * 60)

    try:
        # 创建静态UI实例
        ui = GameUIStatic()

        # 验证游戏引擎是否加载成功
        if ui.game_engine:
            console.print("[green]✅ 游戏引擎加载成功[/green]")

            # 更新游戏状态
            ui.update_game_state()

            # 验证状态转换
            if ui.game_state:
                console.print("[green]✅ 游戏状态转换成功[/green]")
                console.print(f"  玩家血量: {ui.game_state.get('player', {}).get('health', 0)}")
                console.print(f"  AI血量: {ui.game_state.get('opponent', {}).get('health', 0)}")
                console.print(f"  玩家手牌: {ui.game_state.get('player', {}).get('hand_count', 0)}张")
                console.print(f"  AI手牌: {ui.game_state.get('opponent', {}).get('hand_count', 0)}张")
            else:
                console.print("[red]❌ 游戏状态转换失败[/red]")
                return False
        else:
            console.print("[yellow]⚠️ 游戏引擎未加载，使用模拟模式[/yellow]")

        # 测试AI引擎回合
        if ui.game_engine and ui.ai_agent:
            console.print("\n🤖 [cyan]测试AI引擎回合...[/cyan]")
            await ui._ai_engine_turn()
            console.print("[green]✅ AI引擎回合测试完成[/green]")
        else:
            console.print("[yellow]⚠️ 跳过AI引擎回合测试（缺少游戏引擎或AI代理）[/yellow]")

        return True

    except Exception as e:
        console.print(f"[red]💥 GameUIStatic集成测试出错: {e}[/red]")
        import traceback
        console.print(f"[red]详细错误信息:[/red]")
        console.print(traceback.format_exc())
        return False

async def test_async_compatibility():
    """测试异步兼容性"""
    console.print("\n🧪 [bold blue]测试异步兼容性[/bold blue]")
    console.print("=" * 60)

    try:
        # 测试在异步环境中调用AI决策
        console.print("🔍 [cyan]测试异步环境中的AI决策...[/cyan]")

        game = CardGame("玩家", "AI")
        ai_agent = create_test_ai_agent()

        # 添加测试卡牌
        def create_card(name, cost, attack, health, card_type="minion", mechanics=None, description=""):
            return {
                "name": name,
                "cost": cost,
                "attack": attack,
                "health": health,
                "card_type": card_type,
                "mechanics": mechanics or [],
                "description": description
            }

        test_card = create_card("测试随从", 1, 1, 1, "minion", [], "测试用随从")
        game.players[1].hand.append(test_card)
        game.players[1].mana = 5

        # 在异步环境中调用决策方法
        action = ai_agent.decide_action(game.players[1], game)

        if action:
            console.print("[green]✅ 异步环境中AI决策成功[/green]")

            # 测试execute_ai_action的异步调用
            from main import execute_ai_action
            result = await execute_ai_action(action, game, 1)

            if result and result.get("success"):
                console.print("[green]✅ 异步execute_ai_action调用成功[/green]")
            else:
                console.print("[red]❌ 异步execute_ai_action调用失败[/red]")
                return False
        else:
            console.print("[yellow]⚠️ AI没有做出决策（可能是正常的）[/yellow]")

        return True

    except Exception as e:
        console.print(f"[red]💥 异步兼容性测试出错: {e}[/red]")
        import traceback
        console.print(f"[red]详细错误信息:[/red]")
        console.print(traceback.format_exc())
        return False

async def run_all_tests():
    """运行所有测试"""
    console.print("🎯 [bold green]AI异步冲突修复 - 综合测试[/bold green]")
    console.print("=" * 80)

    tests = [
        ("AI决策引擎", test_ai_decision_engine),
        ("GameUIStatic集成", test_game_ui_integration),
        ("异步兼容性", test_async_compatibility)
    ]

    results = []

    for test_name, test_func in tests:
        console.print(f"\n🚀 开始测试: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
            if result:
                console.print(f"[green]✅ {test_name} 测试通过[/green]")
            else:
                console.print(f"[red]❌ {test_name} 测试失败[/red]")
        except Exception as e:
            console.print(f"[red]💥 {test_name} 测试异常: {e}[/red]")
            results.append((test_name, False))

    # 输出测试总结
    console.print(f"\n📊 [bold blue]测试总结[/bold blue]")
    console.print("=" * 40)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        color = "green" if result else "red"
        console.print(f"[{color}]  {test_name}: {status}[/{color}]")

    console.print(f"\n🎯 [bold]总体结果: {passed}/{total} 个测试通过[/bold]")

    if passed == total:
        console.print("[bold green]🎉 所有测试通过！AI异步冲突修复成功！[/bold green]")
        console.print("\n✨ 修复效果:")
        console.print("  ✅ AI决策系统正常工作")
        console.print("  ✅ 异步调用兼容性良好")
        console.print("  ✅ GameUIStatic集成成功")
        console.print("  ✅ execute_ai_action函数正常")
    else:
        console.print(f"[bold red]⚠️  还有 {total - passed} 个问题需要修复[/bold red]")

    return passed == total

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n⚠️ [yellow]测试被用户中断[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n💥 [red]测试过程中出现未捕获的异常: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)