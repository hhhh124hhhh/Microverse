#!/usr/bin/env python3
"""
调试AI攻击执行失败问题 - 无效的攻击目标错误
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from game_engine.card_game import CardGame, Card

def debug_ai_attack_target_issue():
    """调试AI攻击执行失败问题"""
    from rich.console import Console
    console = Console()

    console.print("🎯 [bold blue]AI攻击执行失败调试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")
    player = game.players[0]
    ai_player = game.players[1]

    # 场景1: 设置有随从的战场
    console.print("📋 [bold cyan]场景1: 设置战场状态[/bold cyan]")
    console.print("-" * 30)

    # 给玩家添加一个随从作为攻击目标
    player_minion = Card("狼人渗透者", 2, 3, 2, "minion", ["stealth"], "🐺 月影下的刺客")
    player_minion.can_attack = False  # 玩家随从不能攻击（休眠状态）
    player.field.append(player_minion)

    # 给AI添加一个可以攻击的随从
    ai_minion = Card("石像鬼", 1, 1, 1, "minion", ["divine_shield"], "🗿 古老守护者")
    ai_minion.can_attack = True  # AI随从可以攻击
    ai_player.field.append(ai_minion)

    console.print(f"玩家随从: {player_minion.name} ({player_minion.attack}/{player_minion.health}) - 可攻击: {player_minion.can_attack}")
    console.print(f"AI随从: {ai_minion.name} ({ai_minion.attack}/{ai_minion.health}) - 可攻击: {ai_minion.can_attack}")

    # 场景2: 测试各种攻击目标格式
    console.print("\n📋 [bold cyan]场景2: 测试攻击目标格式[/bold cyan]")
    console.print("-" * 30)

    # 从AI的角度看，应该能看到哪些攻击目标
    console.print("从AI角度看，可攻击的目标:")

    # 检查玩家英雄
    console.print(f"  玩家英雄: {player.name} - 血量: {player.health}")

    # 检查玩家随从
    for i, minion in enumerate(player.field):
        console.print(f"  玩家随从{i}: {minion.name} ({minion.attack}/{minion.health}) - 可攻击: {minion.can_attack}")

    # 场景3: 测试AI攻击决策
    console.print("\n📋 [bold cyan]场景3: 测试AI攻击决策[/bold cyan]")
    console.print("-" * 30)

    # 获取AI决策
    try:
        ai_decision = game.ai_engine.get_action(ai_player, player)
        console.print(f"AI决策: {ai_decision}")

        if ai_decision and 'action' in ai_decision:
            action = ai_decision['action']
            console.print(f"AI动作类型: {action}")

            if 'target' in ai_decision:
                target = ai_decision['target']
                console.print(f"AI攻击目标: {target}")
                console.print(f"目标类型: {type(target)}")

                # 测试这个目标是否有效
                console.print("\n🔍 [yellow]验证攻击目标有效性[/yellow]")

                # 检查目标是否匹配英雄
                if target == "英雄":
                    console.print("✅ 目标是英雄，应该有效")
                elif target.startswith("随从_"):
                    # 提取随从索引
                    try:
                        minion_index = int(target.split("_")[1])
                        console.print(f"📝 解析随从索引: {minion_index}")

                        if 0 <= minion_index < len(player.field):
                            target_minion = player.field[minion_index]
                            console.print(f"✅ 找到目标随从: {target_minion.name}")
                        else:
                            console.print(f"❌ 随从索引 {minion_index} 超出范围 (0-{len(player.field)-1})")
                    except (ValueError, IndexError):
                        console.print(f"❌ 无法解析随从索引: {target}")
                else:
                    console.print(f"❌ 未知的目标格式: {target}")

            if 'attacker' in ai_decision:
                attacker = ai_decision['attacker']
                console.print(f"AI攻击者: {attacker}")
                console.print(f"攻击者类型: {type(attacker)}")

                # 检查攻击者是否有效
                if attacker.startswith("随从_"):
                    try:
                        attacker_index = int(attacker.split("_")[1])
                        console.print(f"📝 解析攻击者索引: {attacker_index}")

                        if 0 <= attacker_index < len(ai_player.field):
                            attacker_minion = ai_player.field[attacker_index]
                            console.print(f"✅ 找到攻击随从: {attacker_minion.name}")
                            console.print(f"   攻击力: {attacker_minion.attack}, 可攻击: {attacker_minion.can_attack}")
                        else:
                            console.print(f"❌ 攻击者索引 {attacker_index} 超出范围")
                    except (ValueError, IndexError):
                        console.print(f"❌ 无法解析攻击者索引: {attacker}")
                else:
                    console.print(f"❌ 未知的攻击者格式: {attacker}")
        else:
            console.print("❌ AI没有返回有效的决策")

    except Exception as e:
        console.print(f"❌ AI决策过程出错: {e}")

    # 场景4: 手动测试攻击执行
    console.print("\n📋 [bold cyan]场景4: 手动测试攻击执行[/bold cyan]")
    console.print("-" * 30)

    # 测试正确的攻击格式
    test_attacks = [
        ("随从_0", "英雄"),
        ("随从_0", "随从_0"),
        ("hero", "hero"),  # 可能的错误格式
        ("minion_0", "hero"),  # 可能的错误格式
    ]

    for attacker_str, target_str in test_attacks:
        console.print(f"\n🔄 测试攻击: {attacker_str} -> {target_str}")

        try:
            # 使用游戏的攻击函数
            result = game.attack_with_minion(1, 0, target_str)  # AI是玩家1，使用第一个随从
            console.print(f"  结果: {result['success']}")
            console.print(f"  消息: {result['message']}")
        except Exception as e:
            console.print(f"  ❌ 攻击执行失败: {e}")

    # 场景5: 检查AI攻击日志
    console.print("\n📋 [bold cyan]场景5: 检查AI攻击逻辑[/bold cyan]")
    console.print("-" * 30)

    # 检查AI引擎的攻击逻辑
    if hasattr(game, 'ai_engine') and game.ai_engine:
        ai_engine = game.ai_engine
        console.print("AI引擎类型:", type(ai_engine).__name__)

        # 如果是混合AI，检查底层策略
        if hasattr(ai_engine, 'strategies'):
            console.print("底层策略:")
            for strategy_name, strategy in ai_engine.strategies.items():
                console.print(f"  - {strategy_name}: {type(strategy).__name__}")

        # 检查AI如何生成攻击目标
        console.print("\n🔍 [yellow]AI目标生成逻辑[/yellow]")
        console.print("AI应该能够看到以下攻击目标:")

        # 模拟AI视角
        ai_targets = []

        # 英雄总是有效目标
        ai_targets.append(("英雄", player.name, player.health))

        # 随从目标
        for i, minion in enumerate(player.field):
            ai_targets.append((f"随从_{i}", minion.name, minion.health, minion.attack))

        console.print("AI可见目标:")
        for target_info in ai_targets:
            console.print(f"  {target_info}")

    console.print("\n🎯 [bold green]问题分析总结：[/bold green]")
    console.print("1. 检查AI是否正确生成攻击目标格式")
    console.print("2. 验证攻击目标格式是否匹配游戏期望")
    console.print("3. 确认攻击执行逻辑是否正确处理目标格式")
    console.print("4. 检查是否存在中英文格式不匹配问题")

if __name__ == "__main__":
    debug_ai_attack_target_issue()