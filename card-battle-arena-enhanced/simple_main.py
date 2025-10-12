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
    table.add_row("法力值", f"{context.player_mana}/{context.player_max_mana}",
                  f"{context.opponent_mana}/{context.opponent_max_mana}")
    table.add_row("手牌数量", str(len(context.player_hand)), str(context.opponent_hand_size))
    table.add_row("场面随从", str(len(context.player_field)), str(len(context.opponent_field)))
    table.add_row("牌库数量", str(context.player_deck_size), str(context.opponent_deck_size))

    console.print(table)

    # 显示手牌
    if context.player_hand:
        hand_table = Table(title="🃏 我方手牌", show_header=True, header_style="bold blue")
        hand_table.add_column("名称", style="white")
        hand_table.add_column("费用", style="yellow")
        hand_table.add_column("攻击", style="red")
        hand_table.add_column("生命", style="green")
        hand_table.add_column("类型", style="cyan")
        hand_table.add_column("关键词", style="magenta")

        for card in context.player_hand:
            mechanics = ", ".join(card.get("mechanics", [])) if card.get("mechanics") else "无"
            attack = str(card.get("attack", "")) if "attack" in card else ""
            health = str(card.get("health", "")) if "health" in card else ""

            hand_table.add_row(
                card.get("name", "未知"),
                str(card.get("cost", 0)),
                attack,
                health,
                card.get("card_type", "未知"),
                mechanics
            )

        console.print(hand_table)

    # 显示场面
    if context.player_field or context.opponent_field:
        field_table = Table(title="⚔️ 战场", show_header=True, header_style="bold yellow")
        field_table.add_column("阵营", style="white")
        field_table.add_column("名称", style="white")
        field_table.add_column("攻击", style="red")
        field_table.add_column("生命", style="green")
        field_table.add_column("可攻击", style="yellow")
        field_table.add_column("关键词", style="magenta")

        # 我方场面
        for minion in context.player_field:
            mechanics = ", ".join(minion.get("mechanics", [])) if minion.get("mechanics") else "无"
            can_attack = "✅" if minion.get("can_attack", False) else "❌"

            field_table.add_row(
                "我方",
                minion.get("name", "未知"),
                str(minion.get("attack", 0)),
                str(minion.get("health", 0)),
                can_attack,
                mechanics
            )

        # 对手场面
        for minion in context.opponent_field:
            mechanics = ", ".join(minion.get("mechanics", [])) if minion.get("mechanics") else "无"
            can_attack = "✅" if minion.get("can_attack", False) else "❌"

            field_table.add_row(
                "对手",
                minion.get("name", "未知"),
                str(minion.get("attack", 0)),
                str(minion.get("health", 0)),
                can_attack,
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