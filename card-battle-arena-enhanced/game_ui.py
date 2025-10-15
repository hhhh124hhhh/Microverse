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


# ============================================================================
# TDD Layout重构部分
# ============================================================================

from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from typing import Any, Tuple, Optional, Union


class GameLayout:
    """基于Rich Layout的游戏界面布局管理器"""

    def __init__(self):
        """初始化Layout结构"""
        self.console = Console()
        self.layout_mode = "horizontal"  # 默认水平布局
        self._create_layout()

    def _create_layout(self):
        """创建基础Layout结构"""
        self.layout = Layout()

        # 主要垂直分割：上部游戏信息区，下部交互区
        self.layout.split_column(
            Layout(name="upper", ratio=3),
            Layout(name="lower", ratio=2)
        )

        # 上部横向分割：玩家状态 | 游戏区域 | 对手状态
        self.layout["upper"].split_row(
            Layout(name="player_status", size=30),
            Layout(name="game_area", ratio=1),
            Layout(name="opponent_status", size=30)
        )

        # 下部横向分割：手牌区域 | 命令区域
        self.layout["lower"].split_row(
            Layout(name="hand_area", ratio=3),
            Layout(name="command_area", size=25)
        )

        # 为游戏区域再细分：战场区域
        self.layout["game_area"].split_column(
            Layout(name="battlefield_area", ratio=1),
            Layout(name="info_area", size=3)
        )

    def adapt_to_width(self, width: int):
        """根据终端宽度适配布局模式"""
        if width < 80:
            self.layout_mode = "vertical"
            # 实现垂直布局逻辑（后续实现）
        elif width < 120:
            self.layout_mode = "compact"
            # 实现紧凑布局逻辑（后续实现）
        else:
            self.layout_mode = "horizontal"
            # 保持当前水平布局

    def update_player_status(self, player_data: dict):
        """更新玩家状态区域"""
        panel = create_player_status_panel(player_data)
        self.layout["player_status"].update(panel)

    def update_opponent_status(self, opponent_data: dict):
        """更新对手状态区域"""
        panel = create_opponent_status_panel(opponent_data)
        self.layout["opponent_status"].update(panel)

    def update_hand_area(self, hand_cards: list, current_mana: int):
        """更新手牌区域"""
        table = create_hand_cards_table(hand_cards, current_mana)
        self.layout["hand_area"].update(table)

    def update_battlefield_area(self, player_field: list, opponent_field: list):
        """更新战场区域"""
        component = create_battlefield_component(player_field, opponent_field)
        self.layout["battlefield_area"].update(component)

    def update_command_area(self, available_actions: list = None):
        """更新命令区域"""
        panel = create_command_panel(available_actions)
        self.layout["command_area"].update(panel)

    def update_battlefield_visibility(self, player_field: list, opponent_field: list):
        """更新战场区域可见性"""
        has_minions = len(player_field) > 0 or len(opponent_field) > 0
        # 暂时简化可见性控制逻辑，避免Layout访问错误
        # 后续在重构阶段完善
        pass


class GameUIWithLive:
    """带Live渲染功能的游戏UI（修复版本，支持用户交互）"""

    def __init__(self):
        self.layout_manager = GameLayout()
        self.live = None
        self.game_state = {}
        self._is_running = False
        self._last_update_time = 0
        self._min_update_interval = 0.1  # 最小更新间隔（秒）
        self._input_handler = UserInputHandler()

    def start_rendering(self):
        """开始Live渲染"""
        if self._is_running:
            return  # 防止重复启动

        from rich.live import Live
        import time

        self.live = Live(
            self.layout_manager.layout,
            console=self.layout_manager.console,
            refresh_per_second=4,  # 提高刷新率减少闪烁
            transient=False,  # 防止闪烁
            auto_refresh=True  # 自动刷新
        )

        try:
            self.live.start()
            self._is_running = True

            # 启动后立即刷新一次显示内容
            if self.game_state:
                self._force_refresh()

        except Exception as e:
            self.layout_manager.console.print(f"[red]❌ Live启动失败: {e}[/red]")
            self._is_running = False

    def _refresh_layout(self) -> None:
        """安全刷新布局（Live内部调用）"""
        # 这个方法会被Live自动调用，不需要手动实现
        pass

    def _force_refresh(self):
        """强制刷新显示内容"""
        if hasattr(self, 'live') and self.live:
            try:
                # 更新所有组件内容
                if self.game_state:
                    self._render_all_components()

                # 立即刷新Live显示
                self.live.refresh()
            except Exception as e:
                self.layout_manager.console.print(f"[red]❌ 强制刷新失败: {e}[/red]")

    def _render_all_components(self):
        """渲染所有UI组件"""
        if not self.game_state:
            return

        try:
            # 更新各个区域
            if "player" in self.game_state:
                self.layout_manager.update_player_status(self.game_state["player"])

            if "opponent" in self.game_state:
                self.layout_manager.update_opponent_status(self.game_state["opponent"])

            if "hand" in self.game_state and "player" in self.game_state:
                self.layout_manager.update_hand_area(
                    self.game_state["hand"],
                    self.game_state["player"].get("mana", 0)
                )

            if "battlefield" in self.game_state:
                self.layout_manager.update_battlefield_area(
                    self.game_state["battlefield"].get("player", []),
                    self.game_state["battlefield"].get("opponent", [])
                )

            # 更新命令区域
            available_commands = self._get_available_commands(self.game_state)
            self.layout_manager.update_command_area(available_commands)

        except Exception as e:
            self.layout_manager.console.print(f"[red]❌ 渲染组件失败: {e}[/red]")

    def update_game_state(self, game_state: dict):
        """更新游戏状态并重新渲染（带节流）"""
        import time

        # 总是更新游戏状态，即使Live没有启动
        if not game_state:
            return

        # 节流：避免过于频繁的更新（仅在Live运行时）
        if self._is_running and self.live:
            current_time = time.time()
            if current_time - self._last_update_time < self._min_update_interval:
                return

        try:
            # 检查状态是否真的发生了变化（仅在Live运行时）
            if self._is_running and not self._has_state_changed(game_state):
                return

            # 总是更新内部游戏状态
            self.game_state = game_state.copy()  # 深拷贝避免引用问题

            # 仅在Live运行时更新UI组件
            if self._is_running and self.live:
                # 更新各个区域
                if "player" in game_state:
                    self.layout_manager.update_player_status(game_state["player"])

                if "opponent" in game_state:
                    self.layout_manager.update_opponent_status(game_state["opponent"])

                if "hand" in game_state and "player" in game_state:
                    self.layout_manager.update_hand_area(
                        game_state["hand"],
                        game_state["player"].get("mana", 0)
                    )

                if "battlefield" in game_state:
                    self.layout_manager.update_battlefield_area(
                        game_state["battlefield"].get("player", []),
                        game_state["battlefield"].get("opponent", [])
                    )

                # 更新命令区域
                available_commands = self._get_available_commands(game_state)
                self.layout_manager.update_command_area(available_commands)

                self._last_update_time = time.time()

        except Exception as e:
            self.layout_manager.console.print(f"[red]❌ 更新游戏状态失败: {e}[/red]")

    def _has_state_changed(self, new_state: dict) -> bool:
        """检查游戏状态是否发生了变化"""
        if not self.game_state:
            return True

        # 检查关键字段是否变化
        key_fields = ["player", "opponent", "hand", "battlefield"]

        for field in key_fields:
            if field in new_state and field in self.game_state:
                if new_state[field] != self.game_state[field]:
                    return True
            elif field in new_state or field in self.game_state:
                return True  # 字段存在性变化

        return False

    def _get_available_commands(self, game_state: dict) -> list:
        """根据游戏状态获取可用命令"""
        commands = ["帮助", "设置"]

        if "player" in game_state:
            player = game_state["player"]
            mana = player.get("mana", 0)

            # 检查是否有可出的卡牌
            if "hand" in game_state:
                playable_cards = [
                    card for card in game_state["hand"]
                    if card.get("cost", 0) <= mana
                ]
                if playable_cards:
                    commands.insert(0, f"出牌 0-{len(playable_cards)-1}")

            # 检查是否可以使用英雄技能
            if mana >= 2:
                commands.insert(-1, "技能")

        commands.append("结束回合")
        return commands

    def stop_rendering(self):
        """停止Live渲染"""
        if self.live and self._is_running:
            try:
                self.live.stop()
                self._is_running = False
            except Exception as e:
                self.layout_manager.console.print(f"[yellow]⚠️ 停止Live时出错: {e}[/yellow]")
            finally:
                self.live = None

    async def process_user_input(self, input_str: str) -> Tuple[bool, str, Optional[dict]]:
        """
        处理用户输入并返回结果

        Args:
            input_str: 用户输入字符串

        Returns:
            (是否成功, 消息, 动作数据)
        """
        # 解析命令
        success, command_data = self._input_handler.parse_command(input_str)

        if not success:
            error_msg = self._input_handler.format_error_message('invalid_command')
            return False, error_msg, None

        command_type, params = command_data

        # 根据命令类型处理
        if command_type == 'help':
            help_text = self._input_handler.get_command_help()
            return True, help_text, None

        elif command_type == 'quit':
            return True, "👋 游戏已退出", {'action': 'quit'}

        elif command_type == 'play_card':
            return await self._handle_play_card(params)

        elif command_type == 'hero_power':
            return await self._handle_hero_power()

        elif command_type == 'attack':
            return await self._handle_attack(params)

        elif command_type == 'end_turn':
            return await self._handle_end_turn()

        else:
            error_msg = self._input_handler.format_error_message('invalid_command', f"未知命令类型: {command_type}")
            return False, error_msg, None

    async def _handle_play_card(self, card_index: int) -> Tuple[bool, str, Optional[dict]]:
        """处理出牌命令"""
        if not self.game_state or 'hand' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        # 检查手牌是否存在
        hand_cards = self.game_state.get('hand', [])
        if card_index >= len(hand_cards):
            max_index = len(hand_cards) - 1
            if max_index < 0:
                return False, "❌ 没有可出的手牌", None
            error_msg = self._input_handler.format_error_message('invalid_card', f"请选择0-{max_index}之间的卡牌")
            return False, error_msg, None

        # 检查卡牌是否可以出
        card = hand_cards[card_index]
        card_cost = card.get('cost', 0)
        current_mana = self.game_state.get('player', {}).get('mana', 0)

        can_play, error_msg = self._input_handler.can_play_card(card_cost, current_mana)
        if not can_play:
            return False, error_msg, None

        # 返回出牌动作
        card_name = card.get('name', '未知卡牌')
        success_msg = self._input_handler.format_success_message('play_card', card_name)
        return True, success_msg, {'action': 'play_card', 'card_index': card_index, 'card': card}

    async def _handle_hero_power(self) -> Tuple[bool, str, Optional[dict]]:
        """处理英雄技能命令"""
        if not self.game_state or 'player' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        current_mana = self.game_state.get('player', {}).get('mana', 0)
        can_use, error_msg = self._input_handler.can_use_hero_power(current_mana)
        if not can_use:
            return False, error_msg, None

        success_msg = self._input_handler.format_success_message('hero_power')
        return True, success_msg, {'action': 'hero_power'}

    async def _handle_attack(self, attack_params: Tuple[int, int]) -> Tuple[bool, str, Optional[dict]]:
        """处理攻击命令"""
        if not self.game_state or 'battlefield' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        attacker_index, target_index = attack_params

        # 检查战场状态
        battlefield = self.game_state.get('battlefield', {})
        player_field = battlefield.get('player', [])
        opponent_field = battlefield.get('opponent', [])

        # 验证攻击者索引
        if attacker_index >= len(player_field):
            max_attacker = len(player_field) - 1
            if max_attacker < 0:
                return False, "❌ 你没有可攻击的随从", None
            error_msg = self._input_handler.format_error_message('invalid_attack', f"请选择0-{max_attacker}之间的我方随从")
            return False, error_msg, None

        # 验证目标索引（可以攻击对手随从或英雄）
        max_target = len(opponent_field)  # 随从数量
        if target_index > max_target:  # 最后一个是英雄
            if max_target < 0:
                max_target = 0  # 只有英雄
            error_msg = self._input_handler.format_error_message('invalid_attack', f"请选择0-{max_target}之间的敌方目标")
            return False, error_msg, None

        # 检查攻击者是否可以攻击
        attacker = player_field[attacker_index]
        can_attack = attacker.get('can_attack', False)
        if not can_attack:
            attacker_name = attacker.get('name', '随从')
            error_msg = self._input_handler.format_error_message('cannot_attack', f"{attacker_name}当前无法攻击（可能刚上场或已攻击过）")
            return False, error_msg, None

        # 确定攻击目标
        is_attacking_hero = target_index == len(opponent_field)
        target_info = {'type': 'hero'} if is_attacking_hero else {'type': 'minion', 'index': target_index, 'minion': opponent_field[target_index]}

        attacker_name = attacker.get('name', '随从')
        target_name = '敌方英雄' if is_attacking_hero else opponent_field[target_index].get('name', '随从')

        success_msg = self._input_handler.format_success_message('attack', f"{attacker_name} 攻击 {target_name}")
        return True, success_msg, {
            'action': 'attack',
            'attacker_index': attacker_index,
            'attacker': attacker,
            'target': target_info
        }

    async def _handle_end_turn(self) -> Tuple[bool, str, Optional[dict]]:
        """处理结束回合命令"""
        success_msg = self._input_handler.format_success_message('end_turn')
        return True, success_msg, {'action': 'end_turn'}

    async def interactive_game_loop(self):
        """交互式游戏循环"""
        if not self._is_running:
            self.start_rendering()

        self.layout_manager.console.print("\n🎮 [bold green]游戏开始！[/bold green]")
        self.layout_manager.console.print("输入'help'查看可用命令，输入'quit'退出游戏")
        self.layout_manager.console.print("=" * 50)

        from rich.prompt import Prompt

        try:
            while self._is_running:
                # 获取用户输入
                try:
                    user_input = Prompt.ask("\n[bold cyan]请输入命令[/bold cyan]", default="", show_default=False)
                except KeyboardInterrupt:
                    user_input = "quit"

                if not user_input.strip():
                    continue

                # 处理用户输入
                success, message, action_data = await self.process_user_input(user_input)

                # 显示处理结果
                if success:
                    if action_data and action_data.get('action') == 'quit':
                        self.layout_manager.console.print(message)
                        break
                    else:
                        self.layout_manager.console.print(f"[green]{message}[/green]")

                        # 这里应该调用游戏引擎来执行动作
                        # 暂时只是模拟反馈
                        if action_data:
                            await self._simulate_action_result(action_data)
                else:
                    self.layout_manager.console.print(f"[red]{message}[/red]")

        except Exception as e:
            self.layout_manager.console.print(f"[red]❌ 游戏循环出错: {e}[/red]")
        finally:
            self.stop_rendering()

    async def _simulate_action_result(self, action_data: dict):
        """模拟动作执行结果（临时实现，后续集成真实游戏引擎）"""
        action = action_data.get('action')

        if action == 'play_card':
            # 模拟出牌后的状态变化
            await asyncio.sleep(0.5)
            self.layout_manager.console.print("[dim]🎯 卡牌已打出，等待游戏引擎处理...[/dim]")

        elif action == 'hero_power':
            # 模拟使用技能
            await asyncio.sleep(0.5)
            self.layout_manager.console.print("[dim]💪 英雄技能已使用，等待游戏引擎处理...[/dim]")

        elif action == 'attack':
            # 模拟攻击
            await asyncio.sleep(0.5)
            self.layout_manager.console.print("[dim]⚔️ 攻击已执行，等待游戏引擎处理...[/dim]")

        elif action == 'end_turn':
            # 模拟结束回合
            await asyncio.sleep(0.5)
            self.layout_manager.console.print("[dim]🔄 回合已结束，等待对手行动...[/dim]")

            # 模拟一些对手行动
            await self._simulate_opponent_turn()

    async def _simulate_opponent_turn(self):
        """模拟对手回合（临时实现）"""
        await asyncio.sleep(1)
        self.layout_manager.console.print("[dim]🤖 对手正在思考...[/dim]")
        await asyncio.sleep(1)
        self.layout_manager.console.print("[dim]🤖 对手结束回合[/dim]")
        self.layout_manager.console.print("[green]✅ 轮到你的回合！[/green]")


def create_player_status_panel(player_data: dict):
    """创建玩家状态面板"""
    # 创建状态表格
    status_table = Table(show_header=False, box=None, padding=0)
    status_table.add_column("属性", style="cyan", width=8)
    status_table.add_column("数值", style="white")

    status_table.add_row("❤️ 生命值", f"{player_data.get('health', 0)}/{player_data.get('max_health', 0)}")
    status_table.add_row("💰 法力值", f"{player_data.get('mana', 0)}/{player_data.get('max_mana', 0)}")
    status_table.add_row("🃋 手牌", f"{player_data.get('hand_count', 0)}张")
    status_table.add_row("⚔️ 随从", f"{player_data.get('field_count', 0)}个")

    return Panel(
        status_table,
        title="👤 玩家状态",
        border_style="green"
    )


def create_opponent_status_panel(opponent_data: dict):
    """创建对手状态面板"""
    # 创建状态表格
    status_table = Table(show_header=False, box=None, padding=0)
    status_table.add_column("属性", style="cyan", width=8)
    status_table.add_column("数值", style="white")

    status_table.add_row("❤️ 生命值", f"{opponent_data.get('health', 0)}/{opponent_data.get('max_health', 0)}")
    status_table.add_row("💰 法力值", f"{opponent_data.get('mana', 0)}/{opponent_data.get('max_mana', 0)}")
    status_table.add_row("🃋 手牌", f"{opponent_data.get('hand_count', 0)}张")
    status_table.add_row("⚔️ 随从", f"{opponent_data.get('field_count', 0)}个")

    return Panel(
        status_table,
        title="🤖 对手状态",
        border_style="red"
    )


def create_hand_cards_table(hand_cards: list, current_mana: int):
    """创建手牌显示表格"""
    table = Table(title="🃏 你的手牌", show_header=True, header_style="bold blue")
    table.add_column("编号", style="white", width=4, justify="center")
    table.add_column("卡牌名称", style="white", width=16)
    table.add_column("费用", style="yellow", width=4, justify="center")
    table.add_column("属性", style="cyan", width=8)
    table.add_column("状态", style="green", width=8)

    for card in hand_cards:
        index = str(card.get("index", "?"))
        name = card.get("name", "未知")
        cost = str(card.get("cost", 0))
        card_type = card.get("type", "未知")

        # 修复：正确计算属性显示，包括法术威力
        if card_type == "minion":
            attack = card.get("attack", 0)
            health = card.get("health", 0)
            attributes = f"{attack}/{health}"
        elif card_type == "spell":
            # 修复：正确显示法术威力
            attack = card.get("attack", 0)
            if attack > 0:
                attributes = f"🔥{attack}"  # 伤害法术
            elif attack < 0:
                attributes = f"💚{-attack}"  # 治疗法术
            else:
                attributes = "✨"  # 其他法术
        else:
            attributes = "未知"

        # 判断可出性
        is_playable = card.get("cost", 0) <= current_mana
        status = "✅ 可出" if is_playable else "❌ 费用不足"

        table.add_row(index, name, cost, attributes, status)

    return table


def create_battlefield_component(player_field: list, opponent_field: list):
    """创建战场状态组件"""
    if not player_field and not opponent_field:
        return Panel("战场上没有随从", title="⚔️ 战场", border_style="yellow")

    # 创建战场表格
    battlefield_table = Table(title="⚔️ 战场", show_header=True)
    battlefield_table.add_column("阵营", style="white", width=8)
    battlefield_table.add_column("随从", style="white", width=12)
    battlefield_table.add_column("属性", style="cyan", width=8)
    battlefield_table.add_column("状态", style="yellow", width=8)

    # 玩家随从
    for minion in player_field:
        name = minion.get("name", "未知")
        attack = minion.get("attack", 0)
        health = minion.get("health", 0)
        can_attack = minion.get("can_attack", False)

        attributes = f"{attack}/{health}"
        status = "🗡️ 可攻" if can_attack else "😴 休眠"

        battlefield_table.add_row("👤 玩家", name, attributes, status)

    # 对手随从
    for minion in opponent_field:
        name = minion.get("name", "未知")
        attack = minion.get("attack", 0)
        health = minion.get("health", 0)
        can_attack = minion.get("can_attack", False)

        attributes = f"{attack}/{health}"
        status = "⚠️ 威胁" if can_attack else "😴 休眠"

        battlefield_table.add_row("🤖 对手", name, attributes, status)

    return battlefield_table


def create_command_panel(available_actions: list = None):
    """创建命令提示面板"""
    if available_actions is None:
        available_actions = ["出牌", "技能", "结束回合", "帮助"]

    commands_text = "\n".join([f"• {action}" for action in available_actions])

    return Panel(
        commands_text,
        title="💬 可用命令",
        border_style="blue"
    )


# ============================================================================
# 用户输入处理类（TDD实现）
# ============================================================================

import re


class UserInputHandler:
    """用户输入处理器 - TDD实现"""

    def __init__(self):
        """初始化输入处理器"""
        self.command_patterns = {
            'play_card': [
                re.compile(r'^出牌\s*(\d+)$', re.IGNORECASE),
                re.compile(r'^play\s*(\d+)$', re.IGNORECASE),
                re.compile(r'^(\d+)$', re.IGNORECASE)  # 简单数字输入
            ],
            'hero_power': [
                re.compile(r'^技能$', re.IGNORECASE),
                re.compile(r'^skill$', re.IGNORECASE),
                re.compile(r'^power$', re.IGNORECASE)
            ],
            'end_turn': [
                re.compile(r'^结束回合$', re.IGNORECASE),
                re.compile(r'^end\s*turn$', re.IGNORECASE),
                re.compile(r'^end$', re.IGNORECASE)
            ],
            'attack': [
                re.compile(r'^攻击\s*(\d+)\s*(\d+)$', re.IGNORECASE),
                re.compile(r'^attack\s*(\d+)\s*(\d+)$', re.IGNORECASE)
            ],
            'help': [
                re.compile(r'^帮助$', re.IGNORECASE),
                re.compile(r'^help$', re.IGNORECASE),
                re.compile(r'^\?$', re.IGNORECASE)
            ],
            'quit': [
                re.compile(r'^退出$', re.IGNORECASE),
                re.compile(r'^quit$', re.IGNORECASE),
                re.compile(r'^exit$', re.IGNORECASE)
            ]
        }

    def parse_command(self, input_str: str) -> Tuple[bool, Optional[Tuple[str, Union[int, None, Tuple]]]]:
        """
        解析用户输入命令

        Args:
            input_str: 用户输入字符串

        Returns:
            (是否成功, (命令类型, 参数)) 或 (False, None)
        """
        if not input_str or not input_str.strip():
            return False, None

        input_str = input_str.strip()

        # 尝试匹配所有命令模式
        for command, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = pattern.match(input_str)
                if match:
                    # 根据命令类型提取参数
                    if command == 'play_card':
                        card_index = int(match.group(1))
                        return True, (command, card_index)
                    elif command == 'attack':
                        attacker_index = int(match.group(1))
                        target_index = int(match.group(2))
                        return True, (command, (attacker_index, target_index))
                    elif command in ['hero_power', 'end_turn', 'help', 'quit']:
                        return True, (command, None)

        return False, None

    def validate_card_index(self, index: int, max_index: int) -> Tuple[bool, str]:
        """
        验证卡牌索引是否有效

        Args:
            index: 卡牌索引
            max_index: 最大有效索引

        Returns:
            (是否有效, 错误信息)
        """
        if index < 0:
            return False, "❌ 卡牌索引不能为负数"

        if index > max_index:
            return False, f"❌ 无效的卡牌编号，请选择0-{max_index}之间的卡牌"

        return True, ""

    def validate_attack_indices(self, attacker_index: int, target_index: int,
                              max_attacker: int, max_target: int) -> Tuple[bool, str]:
        """
        验证攻击索引是否有效

        Args:
            attacker_index: 攻击者索引
            target_index: 目标索引
            max_attacker: 最大攻击者索引
            max_target: 最大目标索引

        Returns:
            (是否有效, 错误信息)
        """
        # 验证攻击者索引
        attacker_valid, attacker_error = self.validate_card_index(attacker_index, max_attacker)
        if not attacker_valid:
            return False, attacker_error

        # 验证目标索引
        target_valid, target_error = self.validate_card_index(target_index, max_target)
        if not target_valid:
            return False, target_error

        # 验证不能攻击自己
        if attacker_index == target_index:
            return False, "❌ 不能攻击自己的随从"

        return True, ""

    def can_play_card(self, card_cost: int, current_mana: int) -> Tuple[bool, str]:
        """
        检查是否可以出牌

        Args:
            card_cost: 卡牌费用
            current_mana: 当前法力值

        Returns:
            (是否可以, 错误信息)
        """
        if card_cost > current_mana:
            return False, f"❌ 法力不足，需要{card_cost}点法力，当前只有{current_mana}点"

        return True, ""

    def can_use_hero_power(self, current_mana: int, hero_power_cost: int = 2) -> Tuple[bool, str]:
        """
        检查是否可以使用英雄技能

        Args:
            current_mana: 当前法力值
            hero_power_cost: 英雄技能费用

        Returns:
            (是否可以, 错误信息)
        """
        if current_mana < hero_power_cost:
            return False, f"❌ 法力不足，需要{hero_power_cost}点法力才能使用技能"

        return True, ""

    def get_command_help(self) -> str:
        """获取命令帮助信息"""
        help_text = """
📋 可用命令：

🃏 **出牌命令**：
  • 出牌 <编号>   - 打出指定编号的卡牌
  • play <编号>   - 英文出牌命令
  • <编号>        - 直接输入数字出牌

⚔️ **攻击命令**：
  • 攻击 <我方随从> <敌方目标> - 命令随从攻击
  • attack <我方随从> <敌方目标> - 英文攻击命令

💪 **其他命令**：
  • 技能 / skill - 使用英雄技能（消耗2法力）
  • 结束回合 / end turn - 结束当前回合
  • 帮助 / help / ? - 显示帮助信息
  • 退出 / quit / exit - 退出游戏

💡 **提示**：
  • 卡牌编号见手牌区域
  • 绿色✅表示可以出牌，红色❌表示法力不足
  • 随从状态：🗡️可攻击，😴休眠中
        """.strip()

        return help_text

    def format_error_message(self, error_type: str, details: str = "") -> str:
        """
        格式化错误消息

        Args:
            error_type: 错误类型
            details: 错误详情

        Returns:
            格式化的错误消息
        """
        error_messages = {
            'invalid_command': "❓ 未知命令，输入'help'查看帮助",
            'invalid_card': f"❌ 无效的卡牌选择：{details}",
            'invalid_attack': f"❌ 无效的攻击目标：{details}",
            'insufficient_mana': f"❌ 法力不足：{details}",
            'cannot_attack': f"❌ 无法攻击：{details}",
            'game_error': f"❌ 游戏错误：{details}"
        }

        base_message = error_messages.get(error_type, "❌ 未知错误")

        if details:
            return f"{base_message}\n{details}"
        return base_message

    def format_success_message(self, action: str, details: str = "") -> str:
        """
        格式化成功消息

        Args:
            action: 动作类型
            details: 详情

        Returns:
            格式化的成功消息
        """
        success_messages = {
            'play_card': "✅ 成功打出卡牌",
            'hero_power': "💪 成功使用英雄技能",
            'attack': "⚔️ 攻击执行成功",
            'end_turn': "🔄 回合结束"
        }

        base_message = success_messages.get(action, "✅ 操作成功")

        if details:
            return f"{base_message}：{details}"
        return base_message


# ============================================================================
# 静态UI系统（禁用Live，避免无限循环）
# ============================================================================

class GameUIStatic:
    """静态游戏UI系统 - 集成真正的游戏引擎"""

    def __init__(self):
        self.layout_manager = GameLayout()
        self.game_state = {}
        self._input_handler = UserInputHandler()
        self.console = Console()

        # 集成真正的游戏引擎
        self.game_engine = None
        self._initialize_game_engine()

    def _initialize_game_engine(self):
        """初始化真正的游戏引擎"""
        try:
            from game_engine.card_game import CardGame
            from ai_engine.agents.fixed_ai_agent import FixedAIAgent
            from ai_engine.agents.agent_personality import PersonalityManager

            # 创建AI对手
            personality_manager = PersonalityManager()
            profile = personality_manager.get_profile("adaptive_learner")

            # 如果没有找到指定的人格，使用默认人格
            if not profile:
                from ai_engine.agents.agent_personality import PersonalityProfile, PlayStyle
                profile = PersonalityProfile(
                    name="回退AI",
                    description="简单的回退AI",
                    traits=[],
                    play_style=PlayStyle.MIDRANGE,
                    risk_tolerance=0.5,
                    aggression_level=0.5,
                    patience_level=0.5,
                    thinking_time_range=(0.1, 0.5),
                    emotion_factor=0.5,
                    learning_rate=0.1
                )

            # 创建规则AI策略（简单稳定）
            from ai_engine.strategies.rule_based import RuleBasedStrategy
            strategy = RuleBasedStrategy("AI对手")

            ai_agent = FixedAIAgent("ai_opponent", profile, strategy)

            # 创建游戏实例
            self.game_engine = CardGame("玩家", "AI对手")
            self.ai_agent = ai_agent

            self.console.print("[dim]✅ 真正的游戏引擎已加载[/dim]")

        except Exception as e:
            self.console.print(f"[yellow]⚠️ 游戏引擎加载失败，使用模拟模式: {e}[/yellow]")
            self.game_engine = None

    def update_game_state(self, game_state: dict = None):
        """更新游戏状态并静态渲染"""
        # 如果有游戏引擎，从引擎获取真实状态
        if self.game_engine:
            self.game_state = self._convert_engine_state_to_ui_state()
        elif game_state:
            # 回退到手动提供的状态
            self.game_state = game_state.copy()
        else:
            return

        # 立即静态渲染一次
        self._render_static_display()

    def _convert_engine_state_to_ui_state(self) -> dict:
        """将游戏引擎状态转换为UI状态"""
        try:
            if not self.game_engine:
                return {}

            # 获取玩家和AI状态
            player = self.game_engine.players[0]  # 玩家
            ai_player = self.game_engine.players[1]  # AI

            # 转换手牌
            hand = []
            for i, card in enumerate(player.hand):
                hand.append({
                    "name": card.name if hasattr(card, 'name') else str(card),
                    "cost": card.cost if hasattr(card, 'cost') else 0,
                    "attack": card.attack if hasattr(card, 'attack') else 0,
                    "health": card.health if hasattr(card, 'health') else 0,
                    "type": card.card_type if hasattr(card, 'card_type') else "minion",
                    "index": i
                })

            # 转换战场
            battlefield = {
                "player": [],
                "opponent": []
            }

            # 玩家随从
            for i, minion in enumerate(player.field):
                battlefield["player"].append({
                    "name": minion.name if hasattr(minion, 'name') else str(minion),
                    "attack": minion.attack if hasattr(minion, 'attack') else 0,
                    "health": minion.health if hasattr(minion, 'health') else 0,
                    "can_attack": getattr(minion, 'can_attack', False),
                    "index": i
                })

            # AI随从
            for i, minion in enumerate(ai_player.field):
                battlefield["opponent"].append({
                    "name": minion.name if hasattr(minion, 'name') else str(minion),
                    "attack": minion.attack if hasattr(minion, 'attack') else 0,
                    "health": minion.health if hasattr(minion, 'health') else 0,
                    "can_attack": getattr(minion, 'can_attack', False),
                    "index": i
                })

            # 返回UI状态
            return {
                "player": {
                    "health": player.health,
                    "max_health": player.max_health,
                    "mana": player.mana,
                    "max_mana": player.max_mana,
                    "hand_count": len(player.hand),
                    "field_count": len(player.field)
                },
                "opponent": {
                    "health": ai_player.health,
                    "max_health": ai_player.max_health,
                    "mana": ai_player.mana,
                    "max_mana": ai_player.max_mana,
                    "hand_count": len(ai_player.hand),
                    "field_count": len(ai_player.field)
                },
                "hand": hand,
                "battlefield": battlefield
            }

        except Exception as e:
            self.console.print(f"[red]❌ 转换游戏状态失败: {e}[/red]")
            return {}

    def _render_static_display(self):
        """静态渲染游戏状态"""
        try:
            self.console.clear()

            # 渲染标题
            self.console.print(Align.center(Text("🎮 Card Battle Arena Enhanced - 静态版", style="bold cyan")))
            self.console.print()

            # 渲染各个区域
            if "player" in self.game_state:
                player_panel = create_player_status_panel(self.game_state["player"])
                self.console.print(player_panel)

            if "battlefield" in self.game_state:
                battlefield_component = create_battlefield_component(
                    self.game_state["battlefield"].get("player", []),
                    self.game_state["battlefield"].get("opponent", [])
                )
                self.console.print(battlefield_component)

            if "hand" in self.game_state and "player" in self.game_state:
                hand_table = create_hand_cards_table(
                    self.game_state["hand"],
                    self.game_state["player"].get("mana", 0)
                )
                self.console.print(hand_table)

            if "opponent" in self.game_state:
                opponent_panel = create_opponent_status_panel(self.game_state["opponent"])
                self.console.print(opponent_panel)

            # 渲染命令区域
            available_commands = self._get_available_commands(self.game_state)
            command_panel = create_command_panel(available_commands)
            self.console.print(command_panel)

        except Exception as e:
            self.console.print(f"[red]❌ 静态渲染失败: {e}[/red]")

    def _get_available_commands(self, game_state: dict) -> list:
        """根据游戏状态获取可用命令（带数字选项）"""
        commands = []

        if "player" in game_state:
            player = game_state["player"]
            mana = player.get("mana", 0)

            # 检查是否有可出的卡牌
            if "hand" in game_state:
                playable_cards = [
                    card for card in game_state["hand"]
                    if card.get("cost", 0) <= mana
                ]
                for i, card in enumerate(playable_cards):
                    card_name = card.get("name", "未知卡牌")
                    commands.append(f"{i+1}. 出牌 {card_name} (费用{card.get('cost', 0)})")

            # 检查是否可以使用英雄技能
            if mana >= 2:
                commands.append(f"{len(commands)+1}. 使用英雄技能 (2法力)")

        # 添加固定命令
        commands.append(f"{len(commands)+1}. 结束回合")
        commands.append(f"{len(commands)+1}. 查看帮助")
        commands.append(f"{len(commands)+1}. 游戏设置")
        commands.append(f"{len(commands)+1}. 退出游戏")

        return commands

    async def process_user_input(self, input_str: str) -> Tuple[bool, str, Optional[dict]]:
        """处理用户输入（支持数字选项）"""
        input_str = input_str.strip()

        # 尝试数字选项处理
        if input_str.isdigit():
            return await self._handle_number_choice(int(input_str))

        # 解析命令
        success, command_data = self._input_handler.parse_command(input_str)

        if not success:
            error_msg = self._input_handler.format_error_message('invalid_command')
            return False, error_msg, None

        command_type, params = command_data

        # 根据命令类型处理
        if command_type == 'help':
            help_text = self._input_handler.get_command_help()
            return True, help_text, None

        elif command_type == 'quit':
            return True, "👋 游戏已退出", {'action': 'quit'}

        elif command_type == 'play_card':
            return await self._handle_play_card(params)

        elif command_type == 'hero_power':
            return await self._handle_hero_power()

        elif command_type == 'attack':
            return await self._handle_attack(params)

        elif command_type == 'end_turn':
            return await self._handle_end_turn()

        else:
            error_msg = self._input_handler.format_error_message('invalid_command', f"未知命令类型: {command_type}")
            return False, error_msg, None

    async def _handle_number_choice(self, choice: int) -> Tuple[bool, str, Optional[dict]]:
        """处理数字选择"""
        commands = self._get_available_commands(self.game_state)

        if choice < 1 or choice > len(commands):
            return False, f"❌ 无效选择，请输入1-{len(commands)}之间的数字", None

        selected_command = commands[choice - 1]

        # 解析选择的命令
        if "出牌" in selected_command:
            # 找到对应的卡牌索引
            playable_cards = [
                card for card in self.game_state.get("hand", [])
                if card.get("cost", 0) <= self.game_state.get("player", {}).get("mana", 0)
            ]
            card_commands = [cmd for cmd in commands if "出牌" in cmd]
            card_index = card_commands.index(selected_command)
            if card_index < len(playable_cards):
                actual_card_index = self.game_state["hand"].index(playable_cards[card_index])
                return await self._handle_play_card(actual_card_index)

        elif "英雄技能" in selected_command:
            return await self._handle_hero_power()

        elif "结束回合" in selected_command:
            return await self._handle_end_turn()

        elif "帮助" in selected_command:
            help_text = self._input_handler.get_command_help()
            return True, help_text, None

        elif "设置" in selected_command:
            return True, "⚙️ 游戏设置功能开发中...", None

        elif "退出" in selected_command:
            return True, "👋 游戏已退出", {'action': 'quit'}

        return False, f"❌ 无法处理命令: {selected_command}", None

    async def _handle_play_card(self, card_index: int) -> Tuple[bool, str, Optional[dict]]:
        """处理出牌命令"""
        if not self.game_state or 'hand' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        # 检查手牌是否存在
        hand_cards = self.game_state.get('hand', [])
        if card_index >= len(hand_cards):
            max_index = len(hand_cards) - 1
            if max_index < 0:
                return False, "❌ 没有可出的手牌", None
            error_msg = self._input_handler.format_error_message('invalid_card', f"请选择0-{max_index}之间的卡牌")
            return False, error_msg, None

        # 检查卡牌是否可以出
        card = hand_cards[card_index]
        card_cost = card.get('cost', 0)
        current_mana = self.game_state.get('player', {}).get('mana', 0)

        can_play, error_msg = self._input_handler.can_play_card(card_cost, current_mana)
        if not can_play:
            return False, error_msg, None

        # 返回出牌动作
        card_name = card.get('name', '未知卡牌')
        success_msg = self._input_handler.format_success_message('play_card', card_name)
        return True, success_msg, {'action': 'play_card', 'card_index': card_index, 'card': card}

    async def _handle_hero_power(self) -> Tuple[bool, str, Optional[dict]]:
        """处理英雄技能命令"""
        if not self.game_state or 'player' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        current_mana = self.game_state.get('player', {}).get('mana', 0)
        can_use, error_msg = self._input_handler.can_use_hero_power(current_mana)
        if not can_use:
            return False, error_msg, None

        success_msg = self._input_handler.format_success_message('hero_power')
        return True, success_msg, {'action': 'hero_power'}

    async def _handle_attack(self, attack_params: Tuple[int, int]) -> Tuple[bool, str, Optional[dict]]:
        """处理攻击命令"""
        if not self.game_state or 'battlefield' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        attacker_index, target_index = attack_params

        # 检查战场状态
        battlefield = self.game_state.get('battlefield', {})
        player_field = battlefield.get('player', [])
        opponent_field = battlefield.get('opponent', [])

        # 验证攻击者索引
        if attacker_index >= len(player_field):
            max_attacker = len(player_field) - 1
            if max_attacker < 0:
                return False, "❌ 你没有可攻击的随从", None
            error_msg = self._input_handler.format_error_message('invalid_attack', f"请选择0-{max_attacker}之间的我方随从")
            return False, error_msg, None

        # 验证目标索引（可以攻击对手随从或英雄）
        max_target = len(opponent_field)  # 随从数量
        if target_index > max_target:  # 最后一个是英雄
            if max_target < 0:
                max_target = 0  # 只有英雄
            error_msg = self._input_handler.format_error_message('invalid_attack', f"请选择0-{max_target}之间的敌方目标")
            return False, error_msg, None

        # 检查攻击者是否可以攻击
        attacker = player_field[attacker_index]
        can_attack = attacker.get('can_attack', False)
        if not can_attack:
            attacker_name = attacker.get('name', '随从')
            error_msg = self._input_handler.format_error_message('cannot_attack', f"{attacker_name}当前无法攻击（可能刚上场或已攻击过）")
            return False, error_msg, None

        # 确定攻击目标
        is_attacking_hero = target_index == len(opponent_field)
        target_info = {'type': 'hero'} if is_attacking_hero else {'type': 'minion', 'index': target_index, 'minion': opponent_field[target_index]}

        attacker_name = attacker.get('name', '随从')
        target_name = '敌方英雄' if is_attacking_hero else opponent_field[target_index].get('name', '随从')

        success_msg = self._input_handler.format_success_message('attack', f"{attacker_name} 攻击 {target_name}")
        return True, success_msg, {
            'action': 'attack',
            'attacker_index': attacker_index,
            'attacker': attacker,
            'target': target_info
        }

    async def _handle_end_turn(self) -> Tuple[bool, str, Optional[dict]]:
        """处理结束回合命令"""
        success_msg = self._input_handler.format_success_message('end_turn')
        return True, success_msg, {'action': 'end_turn'}

    async def interactive_game_loop(self):
        """交互式游戏循环（静态版本）"""
        self.console.print("\n🎮 [bold green]游戏开始！[/bold green]")
        self.console.print("💡 [yellow]提示：输入数字选择命令，或输入文字命令（如：help、quit等）[/yellow]")
        self.console.print("=" * 50)

        from rich.prompt import Prompt

        try:
            while True:
                # 获取用户输入
                try:
                    user_input = Prompt.ask("\n[bold cyan]请输入命令[/bold cyan]", default="", show_default=False)
                except KeyboardInterrupt:
                    user_input = "quit"

                if not user_input.strip():
                    continue

                # 处理用户输入
                success, message, action_data = await self.process_user_input(user_input)

                # 显示处理结果
                if success:
                    if action_data and action_data.get('action') == 'quit':
                        self.console.print(message)
                        break
                    else:
                        self.console.print(f"[green]{message}[/green]")

                        # 执行动作并更新游戏状态
                        if action_data:
                            await self._execute_action_and_update_state(action_data)

                        # 重新渲染界面
                        self._render_static_display()
                else:
                    self.console.print(f"[red]{message}[/red]")

        except Exception as e:
            self.console.print(f"[red]❌ 游戏循环出错: {e}[/red]")

    async def _execute_action_and_update_state(self, action_data: dict):
        """执行动作并更新游戏状态"""
        action = action_data.get('action')

        if action == 'play_card':
            await self._handle_card_played(action_data)

        elif action == 'hero_power':
            await self._handle_hero_power_used(action_data)

        elif action == 'attack':
            await self._handle_attack_executed(action_data)

        elif action == 'end_turn':
            await self._handle_turn_ended(action_data)

    async def _handle_card_played(self, action_data: dict):
        """处理卡牌打出并更新状态"""
        card_index = action_data.get('card_index')
        card = action_data.get('card')

        if self.game_engine:
            # 使用真正的游戏引擎
            try:
                result = self.game_engine.play_card(0, card_index)  # 0是玩家索引
                if result["success"]:
                    self.console.print(f"[green]✅ {result['message']}[/green]")

                    # 立即更新状态
                    self.update_game_state()
                else:
                    self.console.print(f"[red]❌ 出牌失败: {result['message']}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ 游戏引擎出牌出错: {e}[/red]")
        else:
            # 回退到模拟模式
            await self._simulate_card_played(card_index, card)

    async def _handle_hero_power_used(self, action_data: dict):
        """处理英雄技能使用并更新状态"""
        # 更新玩家状态 - 减少2点法力
        if 'player' in self.game_state:
            self.game_state['player']['mana'] -= 2

        await asyncio.sleep(0.5)
        self.console.print("[dim]💪 英雄技能已使用[/dim]")

    async def _handle_attack_executed(self, action_data: dict):
        """处理攻击执行并更新状态"""
        await asyncio.sleep(0.5)
        self.console.print("[dim]⚔️ 攻击已执行[/dim]")

    async def _handle_turn_ended(self, action_data: dict):
        """处理回合结束并让AI行动"""
        if self.game_engine:
            # 使用真正的游戏引擎
            try:
                result = self.game_engine.end_turn(0, auto_attack=True)
                if result["success"]:
                    self.console.print(f"[green]✅ {result['message']}[/green]")

                    # AI自动行动
                    await self._ai_engine_turn()
                else:
                    self.console.print(f"[red]❌ 结束回合失败: {result['message']}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ 游戏引擎结束回合出错: {e}[/red]")
        else:
            # 回退到模拟模式
            await self._simulate_turn_ended(action_data)

    async def _ai_turn(self):
        """AI对手回合"""
        self.console.print("[dim]🤖 AI正在思考...[/dim]")
        await asyncio.sleep(1)

        # AI出牌逻辑
        if 'opponent' in self.game_state:
            opponent_mana = self.game_state['opponent'].get('mana', 0)
            opponent_hand = self.game_state.get('opponent_hand', [])

            # 如果AI有手牌且法力足够，尝试出牌
            if opponent_hand and opponent_mana >= 1:
                # 找出AI能出的最便宜的牌
                playable_cards = [
                    card for card in opponent_hand
                    if card.get('cost', 0) <= opponent_mana
                ]

                if playable_cards:
                    # AI出最便宜的牌
                    ai_card = min(playable_cards, key=lambda x: x.get('cost', 0))
                    card_cost = ai_card.get('cost', 0)

                    # 更新AI状态
                    self.game_state['opponent']['mana'] -= card_cost
                    self.game_state['opponent']['hand_count'] = len(opponent_hand) - 1

                    # 如果是随从，添加到战场
                    if ai_card.get('type') == 'minion':
                        if 'battlefield' not in self.game_state:
                            self.game_state['battlefield'] = {'player': [], 'opponent': []}

                        battlefield_minion = {
                            'name': ai_card.get('name'),
                            'attack': ai_card.get('attack'),
                            'health': ai_card.get('health'),
                            'can_attack': False,
                            'index': len(self.game_state['battlefield']['opponent'])
                        }
                        self.game_state['battlefield']['opponent'].append(battle_minion)
                        self.game_state['opponent']['field_count'] = len(self.game_state['battlefield']['opponent'])

                    card_name = ai_card.get('name')
                    self.console.print(f"[dim]🤖 AI打出了 {card_name}[/dim]")
                else:
                    self.console.print("[dim]🤖 AI没有可出的牌[/dim]")

        # AI结束回合
        await asyncio.sleep(0.5)
        self.console.print("[dim]🤖 AI结束回合[/dim]")

        # 新回合开始 - 双方法力增长
        if 'player' in self.game_state and self.game_state['player']['max_mana'] < 10:
            self.game_state['player']['max_mana'] += 1
            self.game_state['player']['mana'] = self.game_state['player']['max_mana']

        if 'opponent' in self.game_state and self.game_state['opponent']['max_mana'] < 10:
            self.game_state['opponent']['max_mana'] += 1
            self.game_state['opponent']['mana'] = self.game_state['opponent']['max_mana']

        self.console.print("[green]✅ 第{self.game_state['player']['max_mana']}回合开始！[/green]")

    async def _simulate_card_played(self, card_index: int, card: dict):
        """模拟卡牌打出（回退模式）"""
        # 更新手牌 - 移除打出的卡牌
        if 'hand' in self.game_state and card_index < len(self.game_state['hand']):
            # 重新索引手牌
            self.game_state['hand'] = [
                {**card, 'index': i}
                for i, card in enumerate(self.game_state['hand'])
                if card.get('index') != card_index
            ]

        # 更新玩家状态 - 减少法力值
        if 'player' in self.game_state:
            card_cost = card.get('cost', 0)
            self.game_state['player']['mana'] -= card_cost
            self.game_state['player']['hand_count'] = len(self.game_state.get('hand', []))

        # 如果是随从牌，添加到战场
        if card.get('type') == 'minion':
            if 'battlefield' not in self.game_state:
                self.game_state['battlefield'] = {'player': [], 'opponent': []}

            # 添加随从到玩家战场
            battlefield_minion = {
                'name': card.get('name'),
                'attack': card.get('attack'),
                'health': card.get('health'),
                'can_attack': False,  # 刚上场的随从不能攻击
                'index': len(self.game_state['battlefield']['player'])
            }
            self.game_state['battlefield']['player'].append(battlefield_minion)

            # 更新玩家状态
            self.game_state['player']['field_count'] = len(self.game_state['battlefield']['player'])

        await asyncio.sleep(0.5)
        self.console.print(f"[dim]✅ {card.get('name')} 已添加到战场[/dim]")

    async def _simulate_turn_ended(self, action_data: dict):
        """模拟回合结束（回退模式）"""
        await asyncio.sleep(0.5)
        self.console.print("[dim]🔄 玩家回合结束[/dim]")

        # AI对手行动
        await self._ai_turn()

    async def _ai_engine_turn(self):
        """AI引擎回合（使用真正的AI）"""
        if not self.game_engine or not self.ai_agent:
            return

        try:
            self.console.print("[dim]🤖 AI正在思考...[/dim]")
            await asyncio.sleep(1)

            # 让AI执行决策
            current_ai = self.game_engine.players[1]  # AI玩家

            # AI决策和执行
            while not self.game_engine.game_over and self.game_engine.current_player_idx == 1:
                # 获取AI决策
                action = self.ai_agent.decide_action(current_ai, self.game_engine)

                if action:
                    # 执行AI动作
                    from main import execute_ai_action
                    result = await execute_ai_action(action, self.game_engine, 1)

                    if result["success"]:
                        self.console.print(f"[dim]🤖 {result['message']}[/dim]")
                        # 立即更新UI状态以显示AI的动作结果
                        self.update_game_state()
                        # 每次动作后短暂延迟，让AI可以继续决策
                        await asyncio.sleep(0.5)
                    else:
                        self.console.print(f"[dim]⚠️ AI动作失败: {result['message']}[/dim]")
                        # 动作失败，尝试结束回合
                        break
                else:
                    # AI没有合适的动作，结束回合
                    break

            # 确保AI结束自己的回合
            if not self.game_engine.game_over and self.game_engine.current_player_idx == 1:
                end_result = self.game_engine.end_turn(1, auto_attack=True)
                if end_result["success"]:
                    self.console.print(f"[dim]🤖 AI结束回合[/dim]")

            # 检查游戏是否结束
            if self.game_engine.game_over:
                winner = self.game_engine.get_winner()
                self.console.print(f"\n[bold yellow]🎮 游戏结束！{winner}获胜！[/bold yellow]")
            else:
                self.console.print("[green]✅ 轮到你的回合！[/green]")

        except Exception as e:
            self.console.print(f"[red]❌ AI回合执行出错: {e}[/red]")
            # 回退到模拟AI
            await self._ai_turn()

    def stop_rendering(self):
        """停止渲染（静态版本，无需特殊操作）"""
        pass


# ============================================================================
# TDD测试入口
# ============================================================================

if __name__ == "__main__":
    ui = GameUI()
    ui.show_welcome_animation()
    result = ui.show_main_menu()

    if result != "quit":
        print(f"选择的模式: {result}")