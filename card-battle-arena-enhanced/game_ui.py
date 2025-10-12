#!/usr/bin/env python3
"""
Card Battle Arena Enhanced - 炫酷动画界面
使用Rich库创建动态、美观的终端游戏界面
"""
import asyncio
import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.progress import Progress, BarColumn, TextColumn, SpinnerColumn
from rich.align import Align
from rich.text import Text
from rich import box
from rich.live import Live
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.markdown import Markdown
from rich.rule import Rule
import pyfiglet


class GameUI:
    """炫酷的游戏界面类"""

    def __init__(self):
        self.console = Console()
        self.show_intro_animation = True

    def show_welcome_animation(self):
        """显示欢迎动画"""
        self.console.clear()

        # ASCII艺术标题
        title = pyfiglet.figlet_format("Card Battle", font="slant")
        subtitle = pyfiglet.figlet_format("Arena Enhanced", font="small")

        # 逐行显示动画
        for i, line in enumerate((title + "\n" + subtitle).split('\n')):
            if line.strip():
                self.console.print(line, style="cyan" if i < len(title.split('\n')) else "yellow")
                time.sleep(0.05)

        self.console.print()
        self.console.print(Rule("智能卡牌游戏AI系统", style="bold green"))

        # 加载动画
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]系统初始化中..."),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            transient=True,
        ) as progress:
            task1 = progress.add_task("🎮 加载游戏引擎...", total=100)
            for i in range(100):
                time.sleep(0.01)
                progress.update(task1, advance=1)

            task2 = progress.add_task("🤖 初始化AI系统...", total=100)
            for i in range(100):
                time.sleep(0.01)
                progress.update(task2, advance=1)

            task3 = progress.add_task("🔗 连接LLM服务...", total=100)
            for i in range(100):
                time.sleep(0.01)
                progress.update(task3, advance=1)

        self.console.print(Panel(
            "[bold green]✅ 系统初始化完成！[/bold green]\n"
            "[dim]准备好体验智能卡牌游戏的魅力了吗？[/dim]",
            box=box.DOUBLE,
            border_style="green"
        ))

        time.sleep(1)

    def show_main_menu(self):
        """显示主菜单"""
        while True:
            self.console.clear()

            # 菜单标题
            menu_title = Text("🎮 主菜单 - Card Battle Arena Enhanced", style="bold cyan")
            self.console.print(Align.center(menu_title))
            self.console.print()

            # 创建菜单表格
            menu_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            menu_table.add_column("选项", style="yellow", width=8)
            menu_table.add_column("功能描述", style="white")
            menu_table.add_column("说明", style="dim")

            menu_table.add_row("1", "🆚 人机对战", "[dim]玩家 vs AI - 智能对战[/dim]")
            menu_table.add_row("2", "🤖 AI对战", "[dim]AI vs AI - 观看AI对决[/dim]")
            menu_table.add_row("3", "🎯 交互模式", "[dim]自由游戏模式[/dim]")
            menu_table.add_row("4", "🧪 系统测试", "[dim]测试所有功能[/dim]")
            menu_table.add_row("5", "📊 性能基准", "[dim]测试系统性能[/dim]")
            menu_table.add_row("6", "⚙️ 系统设置", "[dim]配置游戏参数[/dim]")
            menu_table.add_row("7", "📋 帮助信息", "[dim]查看游戏帮助[/dim]")
            menu_table.add_row("0", "🚪 退出游戏", "[dim]退出系统[/dim]")

            self.console.print(Align.center(menu_table))
            self.console.print()

            # 获取用户输入
            choice = Prompt.ask(
                "[bold green]请选择游戏模式[/bold green]",
                choices=["1", "2", "3", "4", "5", "6", "7", "0"],
                default="1"
            )

            if choice == "0":
                if Confirm.ask("[red]确定要退出游戏吗？[/red]", default=False):
                    self.show_goodbye()
                    return "quit"
            elif choice == "1":
                return self.show_human_vs_ai_menu()
            elif choice == "2":
                return self.show_ai_vs_ai_menu()
            elif choice == "3":
                return self.show_interactive_menu()
            elif choice == "4":
                return self.show_test_menu()
            elif choice == "5":
                return self.show_benchmark_menu()
            elif choice == "6":
                self.show_settings()
            elif choice == "7":
                self.show_help()

    def show_human_vs_ai_menu(self):
        """人机对战菜单"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🆚 人机对战模式[/bold cyan]\n"
            "[dim]挑战智能AI，测试你的策略思维！[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        # AI难度选择
        difficulty_table = Table(title="选择AI难度", box=box.ROUNDED)
        difficulty_table.add_column("选项", style="yellow")
        difficulty_table.add_column("难度", style="white")
        difficulty_table.add_column("描述", style="dim")

        difficulty_table.add_row("1", "🟢 简单", "AI容易犯错，适合新手")
        difficulty_table.add_row("2", "🔵 普通", "AI正常发挥，平衡游戏")
        difficulty_table.add_row("3", "🟠 困难", "AI表现出色，有挑战性")
        difficulty_table.add_row("4", "🔴 专家", "AI发挥完美，极限挑战")

        self.console.print(difficulty_table)
        self.console.print()

        difficulty = Prompt.ask(
            "选择难度",
            choices=["1", "2", "3", "4"],
            default="2"
        )

        difficulty_map = {
            "1": "easy",
            "2": "normal",
            "3": "hard",
            "4": "expert"
        }

        # AI策略选择
        strategy_table = Table(title="选择AI策略", box=box.ROUNDED)
        strategy_table.add_column("选项", style="yellow")
        strategy_table.add_column("策略", style="white")
        strategy_table.add_column("描述", style="dim")

        strategy_table.add_row("1", "🧠 规则AI", "基于规则的稳健策略")
        strategy_table.add_row("2", "🤖 混合AI", "规则+LLM的智能策略")

        self.console.print(strategy_table)
        strategy = Prompt.ask(
            "选择策略",
            choices=["1", "2"],
            default="2"
        )

        strategy_map = {"1": "rule_based", "2": "hybrid"}

        # 游戏局数
        games = IntPrompt.ask("游戏局数", default=1)

        return {
            "mode": "human_vs_ai",
            "difficulty": difficulty_map[difficulty],
            "strategy": strategy_map[strategy],
            "games": games
        }

    def show_ai_vs_ai_menu(self):
        """AI对战菜单"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🤖 AI对战模式[/bold cyan]\n"
            "[dim]观看AI之间的智能对决，学习高级策略！[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        games = IntPrompt.ask("观看局数", default=3)

        return {
            "mode": "ai_vs_ai",
            "games": games
        }

    def show_interactive_menu(self):
        """交互模式菜单"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🎯 交互模式[/bold cyan]\n"
            "[dim]自由探索游戏功能，无压力游戏！[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        return {"mode": "interactive"}

    def show_test_menu(self):
        """测试菜单"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🧪 系统测试[/bold cyan]\n"
            "[dim]全面检测系统功能，确保一切正常！[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        test_table = Table(show_header=True, box=box.ROUNDED)
        test_table.add_column("选项", style="yellow")
        test_table.add_column("测试项目", style="white")
        test_table.add_row("1", "🤖 LLM集成测试")
        test_table.add_row("2", "🧠 AI策略测试")
        test_table.add_row("3", "🎭 AI人格测试")
        test_table.add_row("4", "🔧 全面系统测试")

        self.console.print(test_table)

        choice = Prompt.ask("选择测试项目", choices=["1", "2", "3", "4"], default="4")

        test_map = {
            "1": "deepseek",
            "2": "strategies",
            "3": "personalities",
            "4": "all"
        }

        return {
            "mode": "test",
            "test_type": test_map[choice]
        }

    def show_benchmark_menu(self):
        """性能基准测试菜单"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]📊 性能基准测试[/bold cyan]\n"
            "[dim]测试系统性能，优化运行效率！[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        iterations = IntPrompt.ask("测试迭代次数", default=100)

        return {
            "mode": "benchmark",
            "iterations": iterations
        }

    def show_settings(self):
        """显示设置"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]⚙️ 系统设置[/bold cyan]\n"
            "[dim]配置游戏参数，个性化体验！[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        settings_table = Table(title="当前设置", box=box.ROUNDED)
        settings_table.add_column("设置项", style="yellow")
        settings_table.add_column("当前值", style="white")
        settings_table.add_row("动画效果", "[green]开启[/green]")
        settings_table.add_row("音效", "[red]关闭[/red]")
        settings_table.add_row("语言", "[blue]中文[/blue]")
        settings_table.add_row("主题", "[magenta]默认[/magenta]")

        self.console.print(settings_table)
        self.console.print()

        self.console.print("[dim]设置功能开发中，敬请期待！[/dim]")
        Prompt.ask("按回车键返回主菜单", default="")

    def show_help(self):
        """显示帮助"""
        self.console.clear()
        help_content = """
# 🎮 游戏帮助

## 📋 基本操作

### 游戏命令
- **出牌 <编号>** - 打出指定编号的卡牌
- **技能** - 使用英雄技能（消耗2点法力）
- **结束回合** - 结束当前回合，轮到对手
- **状态** - 查看当前游戏状态
- **帮助** - 显示帮助信息
- **退出** - 退出游戏

### 游戏规则
1. **法力系统**: 每回合获得1点法力，最多10点
2. **卡牌类型**:
   - 🃏 **随从牌**: 上场战斗，有攻击力和生命值
   - ✨ **法术牌**: 使用后立即产生效果
3. **胜利条件**: 将对手生命值降至0

## 🤖 AI特性

### AI难度
- **简单**: AI经常失误，适合新手
- **普通**: AI正常发挥，适合练习
- **困难**: AI表现出色，需要策略
- **专家**: AI完美发挥，极限挑战

### AI策略
- **规则AI**: 基于预设规则的稳健策略
- **混合AI**: 结合规则和深度学习的智能策略

## 💡 游戏提示

1. 合理管理法力资源
2. 观察对手的策略模式
3. 平衡进攻和防守
4. 利用卡牌的特殊效果
5. 保持耐心，享受游戏！

祝您游戏愉快！🎉
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 游戏帮助",
            box=box.ROUNDED,
            border_style="blue"
        ))

        Prompt.ask("按回车键返回主菜单", default="")

    def show_goodbye(self):
        """显示告别动画"""
        self.console.clear()

        goodbye_messages = [
            "[bold green]感谢游玩 Card Battle Arena Enhanced！[/bold green]",
            "[bold cyan]期待下次再见！[/bold cyan]",
            "[bold yellow]游戏愉快！🎮[/bold yellow]"
        ]

        for message in goodbye_messages:
            self.console.print(Align.center(message))
            time.sleep(0.5)

        self.console.print()
        self.console.print(Align.center(Rule("Game Over", style="dim")))

    def show_game_result(self, winner, stats=None):
        """显示游戏结果"""
        self.console.clear()

        if winner == "玩家":
            result_text = "[bold green]🎉 恭喜你赢了！[/bold green]"
            border_style = "green"
        elif winner == "平局":
            result_text = "[bold yellow]🤝 平局！[/bold yellow]"
            border_style = "yellow"
        else:
            result_text = f"[bold red]😔 {winner} 获胜[/bold red]"
            border_style = "red"

        result_panel = Panel(
            result_text,
            title="游戏结果",
            box=box.DOUBLE,
            border_style=border_style
        )

        self.console.print(Align.center(result_panel))

        if stats:
            stats_table = Table(title="游戏统计", box=box.ROUNDED)
            stats_table.add_column("项目", style="yellow")
            stats_table.add_column("数值", style="white")

            for key, value in stats.items():
                stats_table.add_row(key, str(value))

            self.console.print(Align.center(stats_table))

    def show_ai_thinking(self, ai_name, duration=2):
        """显示AI思考动画"""
        thinking_messages = [
            f"🤖 {ai_name} 正在分析局势...",
            f"🧠 {ai_name} 计算最优策略...",
            f"⚡ {ai_name} 评估可能的行动...",
            f"💭 {ai_name} 做出决策..."
        ]

        start_time = time.time()
        message_index = 0

        while time.time() - start_time < duration:
            self.console.print(f"\r[blue]{thinking_messages[message_index % len(thinking_messages)]}[/blue]", end="")
            time.sleep(0.3)
            message_index += 1

        self.console.print("\r" + " " * 50 + "\r", end="")


if __name__ == "__main__":
    ui = GameUI()
    ui.show_welcome_animation()
    result = ui.show_main_menu()

    if result != "quit":
        print(f"选择的模式: {result}")