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
from pathlib import Path
from typing import Any

# 导入设置管理
from config.user_preferences import get_settings_manager, SettingsChangeEvent


class GameUI:
    """炫酷的游戏界面类"""

    def __init__(self):
        self.console = Console()
        self.show_intro_animation = True

        # 初始化设置管理器
        self.settings_manager = get_settings_manager()

        # 注册设置变更回调
        self.settings_manager.register_change_callback(self._on_settings_changed)

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
        self.show_settings_interactive()

    def show_settings_interactive(self):
        """显示交互式设置菜单"""
        while True:
            self.console.clear()
            self.console.print(Panel(
                "[bold cyan]⚙️ 系统设置[/bold cyan]\n"
                "[dim]配置游戏参数，个性化体验！[/dim]",
                box=box.DOUBLE,
                border_style="cyan"
            ))

            # 显示当前设置概览
            prefs = self.settings_manager.user_preferences
            summary_text = prefs.get_display_settings_summary()
            self.console.print(Panel(
                f"[dim]{summary_text}[/dim]",
                title="当前设置概览",
                box=box.ROUNDED,
                border_style="blue"
            ))
            self.console.print()

            # 设置菜单
            settings_menu = Table(show_header=True, box=box.ROUNDED)
            settings_menu.add_column("选项", style="yellow", width=8)
            settings_menu.add_column("设置分类", style="white")
            settings_menu.add_column("说明", style="dim")

            settings_menu.add_row("1", "🎨 显示设置", "[dim]动画、主题、语言等[/dim]")
            settings_menu.add_row("2", "🎮 游戏设置", "[dim]AI策略、难度等[/dim]")
            settings_menu.add_row("3", "⌨️ 快捷键设置", "[dim]自定义快捷键[/dim]")
            settings_menu.add_row("4", "💾 导入/导出", "[dim]保存和加载配置[/dim]")
            settings_menu.add_row("5", "🔄 重置设置", "[dim]恢复默认配置[/dim]")
            settings_menu.add_row("0", "🔙 返回主菜单", "[dim]返回游戏主界面[/dim]")

            self.console.print(Align.center(settings_menu))
            self.console.print()

            choice = Prompt.ask(
                "[bold green]请选择设置项[/bold green]",
                choices=["1", "2", "3", "4", "5", "0"],
                default="0"
            )

            if choice == "0":
                break
            elif choice == "1":
                self._show_display_settings()
            elif choice == "2":
                self._show_game_settings()
            elif choice == "3":
                self._show_quick_action_settings()
            elif choice == "4":
                self._show_import_export_settings()
            elif choice == "5":
                self._reset_settings()

    def _show_display_settings(self):
        """显示设置"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🎨 显示设置[/bold cyan]\n"
            "[dim]配置界面显示效果[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        prefs = self.settings_manager.user_preferences

        # 创建显示设置表格
        display_table = Table(show_header=True, box=box.ROUNDED)
        display_table.add_column("编号", style="yellow", width=6)
        display_table.add_column("设置项", style="white")
        display_table.add_column("当前值", style="cyan")
        display_table.add_column("说明", style="dim")

        # 动画设置
        animation_status = "[green]开启[/green]" if prefs.animation_enabled else "[red]关闭[/red]"
        display_table.add_row("1", "动画效果", animation_status, "界面动画和过渡效果")

        # 音效设置
        sound_status = "[green]开启[/green]" if prefs.sound_enabled else "[red]关闭[/red]"
        display_table.add_row("2", "音效", sound_status, "游戏音效（开发中）")

        # 显示模式
        display_table.add_row("3", "显示模式", f"[blue]{prefs.display_mode.value}[/blue]", "界面布局方式")

        # 主题
        display_table.add_row("4", "界面主题", f"[magenta]{prefs.theme.value}[/magenta]", "颜色主题")

        # 语言
        display_table.add_row("5", "界面语言", f"[yellow]{prefs.language.value}[/yellow]", "界面显示语言")

        # AI思考显示
        thinking_status = "[green]显示[/green]" if prefs.show_ai_thinking else "[red]隐藏[/red]"
        display_table.add_row("6", "AI思考过程", thinking_status, "显示AI的决策分析")

        # 性能指标
        perf_status = "[green]显示[/green]" if prefs.show_performance_metrics else "[red]隐藏[/red]"
        display_table.add_row("7", "性能指标", perf_status, "显示系统性能数据")

        self.console.print(display_table)
        self.console.print()

        choice = Prompt.ask(
            "[bold green]选择要修改的设置项 (0返回)[/bold green]",
            choices=["0", "1", "2", "3", "4", "5", "6", "7"],
            default="0"
        )

        if choice == "0":
            return

        # 处理设置修改
        if choice == "1":  # 动画效果
            new_value = Confirm.ask("是否开启动画效果", default=prefs.animation_enabled)
            self.settings_manager.update_setting("display", "animation_enabled", new_value)

        elif choice == "2":  # 音效
            new_value = Confirm.ask("是否开启音效", default=prefs.sound_enabled)
            self.settings_manager.update_setting("display", "sound_enabled", new_value)

        elif choice == "3":  # 显示模式
            from config.user_preferences import DisplayMode
            modes = [mode.value for mode in DisplayMode]
            current_mode = prefs.display_mode.value
            new_mode = Prompt.ask(
                "选择显示模式",
                choices=modes,
                default=current_mode
            )
            self.settings_manager.update_setting("display", "display_mode", new_mode)

        elif choice == "4":  # 主题
            from config.user_preferences import Theme
            themes = [theme.value for theme in Theme]
            current_theme = prefs.theme.value
            new_theme = Prompt.ask(
                "选择界面主题",
                choices=themes,
                default=current_theme
            )
            self.settings_manager.update_setting("display", "theme", new_theme)

        elif choice == "5":  # 语言
            from config.user_preferences import Language
            languages = [lang.value for lang in Language]
            current_lang = prefs.language.value
            new_lang = Prompt.ask(
                "选择界面语言",
                choices=languages,
                default=current_lang
            )
            self.settings_manager.update_setting("display", "language", new_lang)

        elif choice == "6":  # AI思考显示
            new_value = Confirm.ask("是否显示AI思考过程", default=prefs.show_ai_thinking)
            self.settings_manager.update_setting("display", "show_ai_thinking", new_value)

        elif choice == "7":  # 性能指标
            new_value = Confirm.ask("是否显示性能指标", default=prefs.show_performance_metrics)
            self.settings_manager.update_setting("display", "show_performance_metrics", new_value)

        # 显示更新成功消息
        self.console.print()
        self.console.print(Panel(
            "[bold green]✅ 设置已更新[/bold green]",
            box=box.ROUNDED,
            border_style="green"
        ))
        Prompt.ask("按回车键继续", default="")

    def _show_game_settings(self):
        """游戏设置"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]🎮 游戏设置[/bold cyan]\n"
            "[dim]配置游戏相关参数[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        # 创建游戏设置表格
        game_table = Table(show_header=True, box=box.ROUNDED)
        game_table.add_column("编号", style="yellow", width=6)
        game_table.add_column("设置项", style="white")
        game_table.add_column("当前值", style="cyan")
        game_table.add_column("说明", style="dim")

        # AI策略
        current_strategy = self.settings_manager.game_settings.ai.default_strategy
        game_table.add_row("1", "默认AI策略", f"[blue]{current_strategy}[/blue]", "AI的决策策略")

        # AI人格
        current_personality = self.settings_manager.game_settings.ai.default_personality
        game_table.add_row("2", "默认AI人格", f"[magenta]{current_personality}[/magenta]", "AI的性格特征")

        # LLM功能
        llm_status = "[green]开启[/green]" if self.settings_manager.game_settings.ai.enable_llm else "[red]关闭[/red]"
        game_table.add_row("3", "LLM功能", llm_status, "高级AI分析功能")

        # AI决策时间
        current_time = self.settings_manager.game_settings.ai.max_decision_time
        game_table.add_row("4", "AI决策时间(秒)", f"[yellow]{current_time}[/yellow]", "AI最长思考时间")

        # 自动保存
        auto_save_status = "[green]开启[/green]" if self.settings_manager.user_preferences.auto_save else "[red]关闭[/red]"
        game_table.add_row("5", "自动保存", auto_save_status, "自动保存游戏进度")

        # 游戏提示
        tips_status = "[green]显示[/green]" if self.settings_manager.user_preferences.show_tips else "[red]隐藏[/red]"
        game_table.add_row("6", "游戏提示", tips_status, "显示游戏操作提示")

        self.console.print(game_table)
        self.console.print()

        choice = Prompt.ask(
            "[bold green]选择要修改的设置项 (0返回)[/bold green]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="0"
        )

        if choice == "0":
            return

        # 处理游戏设置修改
        if choice == "1":  # AI策略
            strategies = ["rule_based", "hybrid", "llm_enhanced"]
            current = self.settings_manager.game_settings.ai.default_strategy
            new_strategy = Prompt.ask(
                "选择默认AI策略",
                choices=strategies,
                default=current
            )
            self.settings_manager.update_setting("game", "default_strategy", new_strategy)

        elif choice == "2":  # AI人格
            personalities = [
                "aggressive_berserker", "wise_defender", "strategic_mastermind",
                "combo_enthusiast", "adaptive_learner", "fun_seeker"
            ]
            current = self.settings_manager.game_settings.ai.default_personality
            new_personality = Prompt.ask(
                "选择默认AI人格",
                choices=personalities,
                default=current
            )
            self.settings_manager.update_setting("game", "default_personality", new_personality)

        elif choice == "3":  # LLM功能
            current = self.settings_manager.game_settings.ai.enable_llm
            new_value = Confirm.ask("是否开启LLM功能", default=current)
            self.settings_manager.update_setting("game", "enable_llm", new_value)

        elif choice == "4":  # AI决策时间
            current = self.settings_manager.game_settings.ai.max_decision_time
            new_time = IntPrompt.ask("设置AI最长决策时间(秒)", default=current)
            if 1 <= new_time <= 30:  # 限制在合理范围内
                self.settings_manager.update_setting("game", "max_decision_time", new_time)
            else:
                self.console.print("[red]⚠️ 时间必须在1-30秒之间[/red]")
                Prompt.ask("按回车键继续", default="")

        elif choice == "5":  # 自动保存
            current = self.settings_manager.user_preferences.auto_save
            new_value = Confirm.ask("是否开启自动保存", default=current)
            self.settings_manager.update_setting("display", "auto_save", new_value)

        elif choice == "6":  # 游戏提示
            current = self.settings_manager.user_preferences.show_tips
            new_value = Confirm.ask("是否显示游戏提示", default=current)
            self.settings_manager.update_setting("display", "show_tips", new_value)

        # 显示更新成功消息
        self.console.print()
        self.console.print(Panel(
            "[bold green]✅ 游戏设置已更新[/bold green]",
            box=box.ROUNDED,
            border_style="green"
        ))
        Prompt.ask("按回车键继续", default="")

    def _show_quick_action_settings(self):
        """快捷键设置"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]⌨️ 快捷键设置[/bold cyan]\n"
            "[dim]自定义游戏快捷键[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        # 创建快捷键表格
        quick_table = Table(show_header=True, box=box.ROUNDED)
        quick_table.add_column("功能", style="white")
        quick_table.add_column("当前快捷键", style="cyan")
        quick_table.add_column("操作", style="yellow")

        quick_actions = self.settings_manager.user_preferences.quick_actions
        action_names = {
            "help": "帮助",
            "quit": "退出",
            "end_turn": "结束回合",
            "play_card": "出牌",
            "use_skill": "使用技能",
            "settings": "设置"
        }

        for key, name in action_names.items():
            current_key = quick_actions.get(key, "")
            quick_table.add_row(name, f"[blue]{current_key}[/blue]", "修改")

        self.console.print(quick_table)
        self.console.print()
        self.console.print("[dim]快捷键修改功能开发中...[/dim]")
        Prompt.ask("按回车键返回", default="")

    def _show_import_export_settings(self):
        """导入导出设置"""
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]💾 导入/导出设置[/bold cyan]\n"
            "[dim]保存和加载配置文件[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        ))

        import_export_table = Table(show_header=True, box=box.ROUNDED)
        import_export_table.add_column("选项", style="yellow", width=6)
        import_export_table.add_column("功能", style="white")
        import_export_table.add_column("说明", style="dim")

        import_export_table.add_row("1", "📤 导出设置", "将当前设置保存到文件")
        import_export_table.add_row("2", "📥 导入设置", "从文件加载设置")
        import_export_table.add_row("3", "💾 手动保存", "立即保存当前设置")
        import_export_table.add_row("0", "🔙 返回", "返回设置主菜单")

        self.console.print(import_export_table)
        self.console.print()

        choice = Prompt.ask(
            "[bold green]选择操作[/bold green]",
            choices=["0", "1", "2", "3"],
            default="0"
        )

        if choice == "1":  # 导出设置
            self._export_settings()
        elif choice == "2":  # 导入设置
            self._import_settings()
        elif choice == "3":  # 手动保存
            self.settings_manager.save_all_settings()
            self.console.print()
            self.console.print(Panel(
                "[bold green]✅ 设置已保存[/bold green]",
                box=box.ROUNDED,
                border_style="green"
            ))
            Prompt.ask("按回车键继续", default="")

    def _export_settings(self):
        """导出设置"""
        try:
            # 生成默认文件名
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"card_battle_settings_{timestamp}.json"

            filename = Prompt.ask(
                "输入导出文件名",
                default=default_filename
            )

            # 确保文件扩展名
            if not filename.endswith('.json'):
                filename += '.json'

            export_path = Path.home() / filename

            success = self.settings_manager.export_settings(export_path)

            if success:
                self.console.print()
                self.console.print(Panel(
                    f"[bold green]✅ 设置已导出到: {export_path}[/bold green]",
                    box=box.ROUNDED,
                    border_style="green"
                ))
            else:
                self.console.print()
                self.console.print(Panel(
                    "[bold red]❌ 导出失败[/bold red]",
                    box=box.ROUNDED,
                    border_style="red"
                ))

        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[bold red]❌ 导出过程中出现错误: {str(e)}[/bold red]",
                box=box.ROUNDED,
                border_style="red"
            ))

        Prompt.ask("按回车键继续", default="")

    def _import_settings(self):
        """导入设置"""
        try:
            filename = Prompt.ask("输入导入文件名")

            if not filename.endswith('.json'):
                filename += '.json'

            import_path = Path.home() / filename

            if not import_path.exists():
                self.console.print()
                self.console.print(Panel(
                    f"[bold red]❌ 文件不存在: {import_path}[/bold red]",
                    box=box.ROUNDED,
                    border_style="red"
                ))
                Prompt.ask("按回车键继续", default="")
                return

            # 确认导入
            if Confirm.ask(f"[yellow]确定要从 {import_path} 导入设置吗？[/yellow]", default=False):
                success = self.settings_manager.import_settings(import_path)

                if success:
                    self.console.print()
                    self.console.print(Panel(
                        "[bold green]✅ 设置导入成功[/bold green]",
                        box=box.ROUNDED,
                        border_style="green"
                    ))
                else:
                    self.console.print()
                    self.console.print(Panel(
                        "[bold red]❌ 导入失败，文件格式可能不正确[/bold red]",
                        box=box.ROUNDED,
                        border_style="red"
                    ))
            else:
                self.console.print("[dim]导入已取消[/dim]")

        except Exception as e:
            self.console.print()
            self.console.print(Panel(
                f"[bold red]❌ 导入过程中出现错误: {str(e)}[/bold red]",
                box=box.ROUNDED,
                border_style="red"
            ))

        Prompt.ask("按回车键继续", default="")

    def _reset_settings(self):
        """重置设置"""
        self.console.clear()
        self.console.print(Panel(
            "[bold red]⚠️ 重置设置[/bold red]\n"
            "[dim]这将恢复所有设置为默认值[/dim]",
            box=box.DOUBLE,
            border_style="red"
        ))

        self.console.print()
        if Confirm.ask("[bold red]确定要重置所有设置吗？此操作不可撤销！[/bold red]", default=False):
            self.settings_manager.reset_to_defaults()

            self.console.print()
            self.console.print(Panel(
                "[bold green]✅ 所有设置已重置为默认值[/bold green]",
                box=box.ROUNDED,
                border_style="green"
            ))
        else:
            self.console.print("[dim]重置操作已取消[/dim]")

        Prompt.ask("按回车键继续", default="")

    def _on_settings_changed(self, event: SettingsChangeEvent):
        """设置变更回调函数"""
        # 这里可以处理设置变更后的逻辑
        # 例如：重新加载主题、更新UI显示等
        pass

    def update_setting(self, category: str, key: str, value: Any) -> bool:
        """更新设置 - 对外接口"""
        return self.settings_manager.update_setting(category, key, value)

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