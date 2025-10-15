#!/usr/bin/env python3
"""
简化版命令行游戏
专注于AI决策功能的演示
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_engine.strategies.rule_based import RuleBasedStrategy
from ai_engine.agents.agent_personality import PersonalityManager, PERSONALITY_PROFILES
from ai_engine.agents.ai_agent import AIAgent
from game_engine.game_state.game_context import GameContext
from config.settings import setup_environment
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()


def create_sample_game_context() -> GameContext:
    """创建示例游戏上下文"""
    return GameContext(
        game_id="sample_game_001",
        current_player=0,
        turn_number=5,
        phase="main",

        # 玩家状态
        player_health=25,
        player_max_health=30,
        player_mana=6,
        player_max_mana=6,
        player_hand=[
            {
                "name": "烈焰元素",
                "cost": 3,
                "attack": 5,
                "health": 3,
                "instance_id": "card_001",
                "card_type": "minion",
                "mechanics": []
            },
            {
                "name": "铁喙猫头鹰",
                "cost": 3,
                "attack": 2,
                "health": 2,
                "instance_id": "card_002",
                "card_type": "minion",
                "mechanics": ["taunt"]
            },
            {
                "name": "火球术",
                "cost": 4,
                "instance_id": "card_003",
                "card_type": "spell",
                "mechanics": []
            }
        ],
        player_field=[
            {
                "name": "狼人渗透者",
                "attack": 3,
                "health": 2,
                "instance_id": "minion_001",
                "can_attack": True,
                "mechanics": ["stealth"]
            }
        ],
        player_deck_size=20,

        # 对手状态
        opponent_health=20,
        opponent_max_health=30,
        opponent_mana=4,
        opponent_max_mana=4,
        opponent_field=[
            {
                "name": "霜狼步兵",
                "attack": 2,
                "health": 3,
                "instance_id": "opp_minion_001",
                "can_attack": True,
                "mechanics": ["taunt"]
            },
            {
                "name": "石像鬼",
                "attack": 1,
                "health": 1,
                "instance_id": "opp_minion_002",
                "can_attack": False,
                "mechanics": ["divine_shield"]
            }
        ],
        opponent_hand_size=4,
        opponent_deck_size=18
    )


def display_game_state(context: GameContext):
    """显示游戏状态"""
    # 创建游戏状态表格
    table = Table(title="🎮 游戏状态", show_header=True, header_style="bold magenta")
    table.add_column("属性", style="cyan", width=20)
    table.add_column("我方", style="green", width=30)
    table.add_column("对手", style="red", width=30)

    table.add_row("生命值", f"{context.player_health}/{context.player_max_health}",
                  f"{context.opponent_health}/{context.opponent_max_health}")

    # 法力值用颜色突出显示
    player_mana_ratio = context.player_mana / max(1, context.player_max_mana)
    opponent_mana_ratio = context.opponent_mana / max(1, context.opponent_max_mana)

    if player_mana_ratio >= 0.8:
        player_mana_style = "bold green"
    elif player_mana_ratio >= 0.5:
        player_mana_style = "bold yellow"
    else:
        player_mana_style = "red"

    if opponent_mana_ratio >= 0.8:
        opponent_mana_style = "bold green"
    elif opponent_mana_ratio >= 0.5:
        opponent_mana_style = "bold yellow"
    else:
        opponent_mana_style = "red"

    table.add_row("法力值",
                  f"[{player_mana_style}]{context.player_mana}/{context.player_max_mana}[/{player_mana_style}]",
                  f"[{opponent_mana_style}]{context.opponent_mana}/{context.opponent_max_mana}[/{opponent_mana_style}]")
    table.add_row("手牌数量", str(len(context.player_hand)), str(context.opponent_hand_size))
    table.add_row("场面随从", str(len(context.player_field)), str(len(context.opponent_field)))
    table.add_row("牌库数量", str(context.player_deck_size), str(context.opponent_deck_size))

    console.print(table)

    # 添加法力值使用情况面板
    if context.player_hand:
        playable_cards = sum(1 for card in context.player_hand if card.get("cost", 0) <= context.player_mana)
        total_cards = len(context.player_hand)

        # 计算平均手牌费用
        avg_cost = sum(card.get("cost", 0) for card in context.player_hand) / max(1, total_cards)

        mana_info = f"💰 [bold cyan]法力值分析:[/bold cyan]\n"
        mana_info += f"   可出牌: [green]{playable_cards}/{total_cards}[/green] 张\n"
        mana_info += f"   平均费用: [yellow]{avg_cost:.1f}[/yellow]\n"

        # 显示最大可出的费用
        max_playable_cost = max([card.get("cost", 0) for card in context.player_hand
                                if card.get("cost", 0) <= context.player_mana], default=0)
        if max_playable_cost > 0:
            mana_info += f"   最大可出: [bold green]{max_playable_cost}[/bold green] 费用牌"

        console.print(Panel(mana_info.strip(), title="法力值状态", border_style="cyan"))

    # 显示手牌
    if context.player_hand:
        hand_table = Table(title="🃏 我方手牌", show_header=True, header_style="bold blue")
        hand_table.add_column("名称", style="white", width=20)
        hand_table.add_column("费用", style="bold yellow", width=6, justify="center")
        hand_table.add_column("攻击", style="red", width=6, justify="center")
        hand_table.add_column("生命", style="green", width=6, justify="center")
        hand_table.add_column("类型", style="cyan", width=8)
        hand_table.add_column("关键词", style="magenta", width=12)

        # 按费用排序手牌，让高费用牌更明显
        sorted_hand = sorted(context.player_hand, key=lambda x: x.get("cost", 0), reverse=True)

        for i, card in enumerate(sorted_hand):
            mechanics = ", ".join(card.get("mechanics", [])) if card.get("mechanics") else "无"
            attack = str(card.get("attack", "")) if "attack" in card else ""
            health = str(card.get("health", "")) if "health" in card else ""
            cost = card.get("cost", 0)

            # 高亮显示法力值消耗，使用不同的颜色表示费用高低
            cost_style = "bold yellow"
            if cost >= 7:
                cost_style = "bold red"  # 高费用用红色
            elif cost >= 5:
                cost_style = "bold magenta"  # 中高费用用紫色
            elif cost <= 2:
                cost_style = "bold green"  # 低费用用绿色

            # 可出牌的手牌用特殊标记
            name_prefix = ""
            if cost <= context.player_mana:
                name_prefix = "✅ "  # 可出的牌
            else:
                name_prefix = "❌ "  # 不可出的牌

            hand_table.add_row(
                f"{name_prefix}{card.get('name', '未知')}",
                f"[{cost_style}]{cost}[/{cost_style}]",
                f"[red]{attack}[/red]" if attack else "",
                f"[green]{health}[/green]" if health else "",
                card.get("card_type", "未知"),
                mechanics
            )

        console.print(hand_table)

    # 显示场面
    if context.player_field or context.opponent_field:
        field_table = Table(title="⚔️ 战场", show_header=True, header_style="bold yellow")
        field_table.add_column("阵营", style="white", width=8)
        field_table.add_column("名称", style="white", width=16)
        field_table.add_column("攻击", style="red", width=6, justify="center")
        field_table.add_column("生命", style="green", width=6, justify="center")
        field_table.add_column("费用", style="yellow", width=6, justify="center")
        field_table.add_column("状态", style="cyan", width=8)
        field_table.add_column("关键词", style="magenta", width=12)

        # 我方场面
        for minion in context.player_field:
            mechanics = ", ".join(minion.get("mechanics", [])) if minion.get("mechanics") else "无"
            can_attack = minion.get("can_attack", False)
            cost = minion.get("cost", 0)  # 显示随从的原始费用

            # 状态显示更详细
            status = ""
            if can_attack:
                status = "🗡️可攻"
            else:
                status = "😴休眠"

            # 高亮显示高攻击力或高血量的随从
            attack = minion.get("attack", 0)
            health = minion.get("health", 0)
            attack_style = "bold red" if attack >= 5 else "red"
            health_style = "bold green" if health >= 5 else "green"

            field_table.add_row(
                "[green]我方[/green]",
                minion.get("name", "未知"),
                f"[{attack_style}]{attack}[/{attack_style}]",
                f"[{health_style}]{health}[/{health_style}]",
                f"[yellow]{cost}[/yellow]" if cost > 0 else "-",
                status,
                mechanics
            )

        # 对手场面
        for minion in context.opponent_field:
            mechanics = ", ".join(minion.get("mechanics", [])) if minion.get("mechanics") else "无"
            can_attack = minion.get("can_attack", False)
            cost = minion.get("cost", 0)

            # 状态显示
            status = ""
            if can_attack:
                status = "⚠️威胁"
            else:
                status = "😴休眠"

            # 对手随从用不同颜色标记威胁程度
            attack = minion.get("attack", 0)
            health = minion.get("health", 0)

            # 根据威胁程度使用不同颜色
            threat_style = "red"
            if attack >= 5:
                threat_style = "bold red"  # 高威胁
            elif attack >= 3:
                threat_style = "yellow"   # 中等威胁

            field_table.add_row(
                "[red]对手[/red]",
                minion.get("name", "未知"),
                f"[{threat_style}]{attack}[/{threat_style}]",
                f"[{threat_style}]{health}[/{threat_style}]",
                f"[yellow]{cost}[/yellow]" if cost > 0 else "-",
                status,
                mechanics
            )

        console.print(field_table)


def display_ai_decision(agent_name: str, personality_name: str, action, execution_time: float):
    """显示AI决策"""
    action_names = {
        "play_card": "出牌",
        "attack": "攻击",
        "use_hero_power": "使用英雄技能",
        "end_turn": "结束回合"
    }

    action_name = action_names.get(action.action_type.value, action.action_type.value)

    # 创建决策面板
    decision_text = f"""
[bold green]AI决策:[/bold green] {action_name}
[bold cyan]置信度:[/bold cyan] {action.confidence:.2f}
[bold yellow]推理:[/bold yellow] {action.reasoning}
[bold magenta]执行时间:[/bold magenta] {execution_time:.3f}秒
    """

    panel = Panel(
        decision_text.strip(),
        title=f"🤖 {agent_name} ({personality_name})",
        border_style="green"
    )
    console.print(panel)


async def demo_ai_personalities():
    """演示不同AI人格的决策"""
    console.print("🎭 [bold blue]AI人格决策演示[/bold blue]")
    console.print("=" * 50)

    # 创建游戏上下文
    context = create_sample_game_context()
    display_game_state(context)

    personality_manager = PersonalityManager()

    # 选择几种人格进行演示
    demo_personalities = ["aggressive_berserker", "wise_defender", "strategic_mastermind", "adaptive_learner"]

    for personality_name in demo_personalities:
        console.print(f"\n{'='*20} {personality_name} {'='*20}")

        profile = personality_manager.get_profile(personality_name)
        console.print(f"🎯 [bold cyan]{profile.name}[/bold cyan] - {profile.description}")
        console.print(f"   激进程度: {profile.aggression_level:.2f} | 风险容忍: {profile.risk_tolerance:.2f}")

        # 创建AI代理
        strategy = RuleBasedStrategy(f"{profile.name}_策略")
        agent = AIAgent(
            agent_id=f"agent_{personality_name}",
            personality=profile,
            ai_strategy=strategy
        )

        # AI决策
        console.print("\n🤔 AI正在思考...")
        action = await agent.make_decision(context)

        if action:
            display_ai_decision(
                agent.agent_id,
                profile.name,
                action,
                action.execution_time
            )
        else:
            console.print("[red]❌ AI无法做出决策[/red]")

        # 模拟学习
        game_result = {
            "won": personality_name == "adaptive_learner",  # 让学习者赢一次
            "opponent_id": "demo_opponent",
            "opponent_aggression": 0.6
        }
        agent.learn_from_game(game_result)

        stats = agent.get_performance_stats()
        console.print(f"📊 统计: {stats['games_played']}场游戏, "
                     f"胜率 {stats['win_rate']:.2f}, "
                     f"当前情感: {stats['current_emotion']}")

        await asyncio.sleep(1)  # 短暂停顿


async def interactive_mode():
    """交互式模式"""
    console.print("🎯 [bold green]交互式AI对战模式[/bold green]")
    console.print("输入命令与AI互动，输入 'help' 查看帮助")

    # 创建AI代理
    personality = PERSONALITY_PROFILES["adaptive_learner"]
    strategy = RuleBasedStrategy("交互AI")
    agent = AIAgent("interactive_ai", personality, strategy)

    context = create_sample_game_context()

    console.print(f"\n🤖 你的AI对手: {personality.name}")
    console.print(f"   {personality.description}")

    while True:
        try:
            command = console.input("\n[bold cyan]输入命令[/bold cyan] > ").strip().lower()

            if command in ['quit', 'exit', 'q']:
                console.print("👋 再见!")
                break
            elif command == 'help':
                help_text = """
[bold yellow]可用命令:[/bold yellow]
  [green]ai[/green]      - 查看AI决策
  [green]state[/green]   - 显示游戏状态
  [green]stats[/green]   - 查看AI统计
  [green]learn[/green]   - 模拟学习
  [green]new[/green]     - 新游戏
  [green]help[/green]    - 显示帮助
  [green]quit[/green]    - 退出游戏
                """
                console.print(Panel(help_text.strip(), title="帮助", border_style="blue"))
            elif command == 'state':
                display_game_state(context)
            elif command == 'ai':
                console.print("🤔 AI正在思考...")
                action = await agent.make_decision(context)
                if action:
                    display_ai_decision(
                        agent.agent_id,
                        personality.name,
                        action,
                        action.execution_time
                    )
                else:
                    console.print("[red]❌ AI无法做出决策[/red]")
            elif command == 'stats':
                stats = agent.get_performance_stats()
                stats_text = f"""
[bold green]AI统计信息:[/bold green]
  人格: {stats['personality']}
  游戏场次: {stats['games_played']}
  胜率: {stats['win_rate']:.2f}
  总决策数: {stats['total_decisions']}
  当前情感: {stats['current_emotion']}
  情感强度: {stats['emotion_intensity']:.2f}
                """
                console.print(Panel(stats_text.strip(), title="AI统计", border_style="green"))
            elif command == 'learn':
                # 模拟游戏结果
                import random
                won = random.choice([True, False])
                game_result = {
                    "won": won,
                    "opponent_id": "human_player",
                    "opponent_aggression": 0.5
                }
                agent.learn_from_game(game_result)
                result_text = "胜利" if won else "失败"
                console.print(f"📚 AI从{result_text}中学习...")
            elif command == 'new':
                context = create_sample_game_context()
                console.print("🆕 开始新游戏!")
                display_game_state(context)
            else:
                console.print(f"[red]未知命令: {command}[/red]")
                console.print("输入 'help' 查看可用命令")

        except KeyboardInterrupt:
            console.print("\n👋 再见!")
            break
        except EOFError:
            console.print("\n👋 再见!")
            break


async def main():
    """主函数"""
    console.print("🎮 [bold blue]Card Battle Arena Enhanced - 简化版[/bold blue]")
    console.print("🤖 [bold green]智能AI决策系统演示[/bold green]")
    console.print("=" * 60)

    # 设置环境
    settings = setup_environment()

    # 显示配置信息
    console.print(f"📋 [yellow]配置信息:[/yellow]")
    console.print(f"   默认AI策略: {settings.ai.default_strategy}")
    console.print(f"   默认AI人格: {settings.ai.default_personality}")
    console.print(f"   LLM功能: {'启用' if settings.ai.enable_llm else '禁用'}")
    console.print(f"   监控功能: {'启用' if settings.monitoring.enable_monitoring else '禁用'}")

    if not settings.ai.enable_llm:
        console.print("\n[yellow]⚠️  LLM功能未启用，请配置DeepSeek API密钥以获得完整体验[/yellow]")
        console.print("   编辑 .env 文件并设置 DEEPSEEK_API_KEY")

    console.print("\n[bold cyan]选择运行模式:[/bold cyan]")
    console.print("1. AI人格演示")
    console.print("2. 交互式模式")

    try:
        # 检查是否在交互环境中
        import sys
        if sys.stdin.isatty():
            choice = console.input("请输入选择 (1/2): ").strip()
        else:
            console.print("检测到非交互环境，自动运行AI人格演示")
            choice = "1"

        if choice == "1":
            await demo_ai_personalities()
        elif choice == "2":
            await interactive_mode()
        else:
            console.print("[red]无效选择，运行AI人格演示[/red]")
            await demo_ai_personalities()

    except KeyboardInterrupt:
        console.print("\n👋 程序被用户中断")
    except Exception as e:
        console.print(f"[red]❌ 程序运行出错: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())