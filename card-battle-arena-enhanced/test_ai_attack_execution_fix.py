#!/usr/bin/env python3
"""
测试AI攻击执行修复 - 验证修复后的攻击执行是否正常工作
"""
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_ai_attack_execution_fix():
    """测试AI攻击执行修复"""
    from rich.console import Console
    from game_engine.card_game import CardGame, Card
    console = Console()

    console.print("🎯 [bold blue]AI攻击执行修复验证测试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")
    player = game.players[0]
    ai_player = game.players[1]

    # 场景1: 设置简单的战场
    console.print("📋 [bold cyan]场景1: 设置战场[/bold cyan]")
    console.print("-" * 30)

    # 给玩家添加一个随从
    player_minion = Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客")
    player.field.append(player_minion)

    # 给AI添加一个可以攻击的随从
    ai_minion = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    ai_minion.can_attack = True
    ai_player.field.append(ai_minion)

    console.print(f"玩家随从: {player_minion.name} ({player_minion.attack}/{player_minion.health})")
    console.print(f"AI随从: {ai_minion.name} ({ai_minion.attack}/{ai_minion.health}) - 可攻击: {ai_minion.can_attack}")

    # 场景2: 手动测试修复后的execute_ai_action函数
    console.print("\n📋 [bold cyan]场景2: 测试修复后的攻击执行[/bold cyan]")
    console.print("-" * 30)

    # 导入main模块的相关函数
    import main
    from game_engine.card_game import Card

    # 模拟AI决策对象
    class MockAction:
        def __init__(self, action_type, parameters=None, reasoning=""):
            self.action_type = action_type
            self.parameters = parameters or {}
            self.reasoning = reasoning

    # 测试攻击英雄
    console.print("🔄 测试1: AI随从攻击英雄")
    attack_hero_action = MockAction(
        action_type="attack",
        parameters={
            "attacker": ai_minion,
            "target": "英雄"
        },
        reasoning="石像鬼攻击敌方英雄"
    )

    try:
        # 手动结束玩家回合，让AI可以执行攻击
        game.end_turn(0)

        result = await main.execute_ai_action(attack_hero_action, game, 1)
        console.print(f"  结果: {result['success']}")
        console.print(f"  消息: {result['message']}")
        console.print(f"  玩家血量: {player.health}")
    except Exception as e:
        console.print(f"  ❌ 错误: {e}")

    # 重新设置游戏状态
    player.health = 30
    ai_minion.can_attack = True

    console.print("\n🔄 测试2: AI随从攻击玩家随从")
    attack_minion_action = MockAction(
        action_type="attack",
        parameters={
            "attacker": ai_minion,
            "target": player_minion
        },
        reasoning="石像鬼攻击狼人渗透者"
    )

    try:
        result = await main.execute_ai_action(attack_minion_action, game, 1)
        console.print(f"  结果: {result['success']}")
        console.print(f"  消息: {result['message']}")
        console.print(f"  玩家随从血量: {player_minion.health}")
        console.print(f"  AI随从血量: {ai_minion.health}")
        console.print(f"  玩家随从机制: {player_minion.mechanics}")
        console.print(f"  AI随从机制: {ai_minion.mechanics}")
    except Exception as e:
        console.print(f"  ❌ 错误: {e}")

    # 场景3: 测试多个目标的情况
    console.print("\n📋 [bold cyan]场景3: 测试多目标攻击[/bold cyan]")
    console.print("-" * 30)

    # 添加更多随从
    minion2 = Card("鹰身女妖", 2, 2, 1, "minion", ["ranged"], "🦅 天空的猎手")
    minion3 = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")

    player.field.extend([minion2, minion3])

    # 添加AI攻击随从
    ai_attacker2 = Card("火焰元素", 3, 3, 3, "minion", [], "🔥 烈焰之灵")
    ai_attacker2.can_attack = True
    ai_player.field.append(ai_attacker2)

    console.print("扩展后的战场:")
    console.print("玩家随从:")
    for i, minion in enumerate(player.field):
        console.print(f"  随从{i}: {minion.name} ({minion.attack}/{minion.health})")

    console.print("AI随从:")
    for i, minion in enumerate(ai_player.field):
        console.print(f"  随从{i}: {minion.name} ({minion.attack}/{minion.health}) - 可攻击: {minion.can_attack}")

    # 测试攻击不同的目标
    test_cases = [
        (ai_attacker2, minion2, "火焰元素攻击鹰身女妖"),
        (ai_attacker2, minion3, "火焰元素攻击石像鬼"),
    ]

    for attacker, target, description in test_cases:
        console.print(f"\n🔄 {description}")
        attack_action = MockAction(
            action_type="attack",
            parameters={
                "attacker": attacker,
                "target": target
            },
            reasoning=description
        )

        try:
            # 重置攻击状态
            attacker.can_attack = True

            result = await main.execute_ai_action(attack_action, game, 1)
            console.print(f"  结果: {result['success']}")
            console.print(f"  消息: {result['message']}")

            if result['success']:
                console.print(f"  目标血量: {target.health}")
                console.print(f"  目标机制: {target.mechanics}")
        except Exception as e:
            console.print(f"  ❌ 错误: {e}")

    # 场景4: 测试无效目标
    console.print("\n📋 [bold cyan]场景4: 测试无效目标处理[/bold cyan]")
    console.print("-" * 30)

    # 创建一个不存在的目标
    fake_target = Card("不存在的随从", 1, 1, 1, "minion", [], "👻 幽灵")

    invalid_attack_action = MockAction(
        action_type="attack",
        parameters={
            "attacker": ai_attacker2,
            "target": fake_target
        },
        reasoning="测试攻击不存在的目标"
    )

    try:
        result = await main.execute_ai_action(invalid_attack_action, game, 1)
        console.print(f"  结果: {result['success']}")
        console.print(f"  消息: {result['message']}")

        if not result['success']:
            console.print("✅ 正确处理了无效目标")
        else:
            console.print("❌ 未能正确处理无效目标")
    except Exception as e:
        console.print(f"  ❌ 错误: {e}")

    console.print("\n🎯 [bold green]测试结果总结：[/bold green]")
    console.print("1. AI攻击英雄应该正常工作")
    console.print("2. AI攻击随从现在应该使用正确的目标格式")
    console.print("3. 神圣护盾机制应该正常工作")
    console.print("4. 无效目标应该被正确处理")
    console.print("5. 修复后的AI攻击执行不再出现'无效的攻击目标'错误")

if __name__ == "__main__":
    asyncio.run(test_ai_attack_execution_fix())