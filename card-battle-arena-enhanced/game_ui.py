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
import re
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
        while True:
            self.console.clear()

            # 帮助菜单
            help_menu = Table(show_header=True, box=box.ROUNDED)
            help_menu.add_column("选项", style="yellow", width=8)
            help_menu.add_column("帮助分类", style="white")
            help_menu.add_column("说明", style="dim")

            help_menu.add_row("1", "🎮 基本操作", "[dim]游戏命令和规则说明[/dim]")
            help_menu.add_row("2", "🃏 卡牌特效", "[dim]详细说明各种卡牌特效[/dim]")
            help_menu.add_row("3", "🤖 AI系统", "[dim]AI难度和策略介绍[/dim]")
            help_menu.add_row("4", "💡 游戏技巧", "[dim]策略建议和游戏提示[/dim]")
            help_menu.add_row("0", "🔙 返回主菜单", "[dim]返回游戏主界面[/dim]")

            self.console.print(Align.center(help_menu))
            self.console.print()

            choice = Prompt.ask(
                "[bold green]请选择帮助分类[/bold green]",
                choices=["1", "2", "3", "4", "0"],
                default="0"
            )

            if choice == "0":
                break
            elif choice == "1":
                self._show_basic_help()
            elif choice == "2":
                self._show_card_effects_help()
            elif choice == "3":
                self._show_ai_help()
            elif choice == "4":
                self._show_tips_help()

    def _show_basic_help(self):
        """显示基本操作帮助"""
        help_content = """
# 🎮 基本操作指南

## 📋 游戏命令

### 基础命令
- **出牌 <编号>** 或 **<编号>** - 打出指定编号的手牌
- **攻击 <随从> <目标>** - 指挥随从攻击目标
- **技能** - 使用英雄技能（消耗2点法力）
- **结束回合** - 结束当前回合，轮到对手行动
- **帮助** 或 **?** - 显示帮助信息
- **退出** - 退出游戏

## 🎯 游戏规则

### 法力系统
- 每回合开始时获得1点法力值
- 法力值上限最多为10点
- 出牌需要消耗相应的法力值

### 卡牌类型
- **🃏 随从牌**:
  - 上场战斗，有攻击力和生命值
  - 刚上场的随从需要等待一回合才能攻击
  - 可以拥有特殊特效（嘲讽、圣盾等）

- **✨ 法术牌**:
  - 使用后立即产生效果
  - 可能造成伤害、治疗或提供其他效果

### 胜利条件
- 将对手英雄的生命值降至0即可获胜
- 对手将你的生命值降至0则失败

## 💡 界面说明

### 状态面板
- **❤️ 生命值**: 当前/最大生命值
- **💰 法力值**: 当前可用/最大法力值
- **🃋 手牌数**: 当前手牌数量
- **⚔️ 随从数**: 战场上随从数量

### 战场信息
- **阵营**: 👤玩家 / 🤖对手
- **随从**: 随从名称
- **属性**: 攻击力/生命值
- **状态**: 🗡️可攻击 / 😴休眠中
- **特效**: 显示随从拥有的特殊能力

### 手牌显示
- **编号**: 卡牌的选择编号
- **卡牌名称**: 卡牌的名称
- **费用**: 打出此牌需要的法力值
- **属性**: 随从的攻击/生命 或 法术的威力
- **状态**: ✅可出 / ❌费用不足
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 基本操作指南",
            box=box.ROUNDED,
            border_style="blue"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    def _show_card_effects_help(self):
        """显示卡牌特效帮助"""
        help_content = """
# 🃏 卡牌特效详解

## 🛡️ 防御型特效

### 🛡️ 嘲讽 (Taunt)
- **效果**: 强制敌方随从优先攻击具有嘲讽的随从
- **策略价值**: 保护其他随从和英雄，是防御战术的核心
- **搭配建议**: 与高血量随从配合效果更佳
- **克制方法**: 使用法术牌或具有特效的随从处理

### ✨ 圣盾 (Divine Shield)
- **效果**: 免疫下一次受到的伤害，受到伤害后圣盾消失
- **策略价值**: 有效对抗高攻击力单体攻击
- **恢复方式**: 特定法术可以重新获得圣盾
- **注意事项**: 只能抵挡一次伤害，之后消失

### 🌑 潜行 (Stealth)
- **效果**: 敌方无法选择潜行随从作为目标，攻击后解除潜行
- **策略价值**: 保护关键随从免受法术和攻击
- **持续时间**: 直到随从造成伤害为止
- **克制方法**: 范围效果法术或攻击其他目标

## ⚔️ 攻击型特效

### ⚡ 冲锋 (Charge)
- **效果**: 随从可以立即攻击，无需等待一回合
- **策略价值**: 快速施加压力，抢夺节奏优势
- **常见搭配**: 高攻击力随从
- **风险**: 容易成为敌方目标

### 💨 风怒 (Windfury)
- **效果**: 每回合可以攻击两次
- **策略价值**: 大幅提升输出能力
- **注意事项**: 每次攻击都需要独立的攻击目标
- **搭配建议**: 配合治疗或圣盾效果

### 🏹 远程 (Ranged)
- **效果**: 可以从安全距离攻击，避免受到部分反击伤害
- **策略价值**: 安全输出，保护脆弱的随从
- **射程**: 通常可以攻击任何敌方目标
- **定位**: 后排输出单位

## 🔥 魔法型特效

### 🔥 法术强度 (Spell Power)
- **效果**: 提升己方法术的伤害效果
- **策略价值**: 增强法术卡牌的威力
- **计算方式**: 通常按百分比提升法术伤害
- **搭配**: 与伤害法术配合使用

### 💀 吸血 (Lifesteal)
- **效果**: 造成伤害的同时为英雄恢复等量生命值
- **策略价值**: 提供持续的续航能力
- **限制**: 只能通过攻击触发
- **价值**: 在持久战中表现出色

### ☠️ 剧毒 (Poisonous)
- **效果**: 对随从造成任何伤害即可直接消灭目标
- **策略价值**: 高效处理大型随从
- **注意事项**: 对英雄无效，只对随从生效
- **策略**: 用于清除敌方强力随从

## 🎯 特殊机制

### 复合特效
许多卡牌拥有多种特效组合：
- **嘲讽+圣盾**: 理想的防御组合
- **冲锋+风怒**: 强大的进攻组合
- **潜行+吸血**: 持续续航的组合

### 特效互动
- **圣盾 vs 剧毒**: 圣盾可以抵挡剧毒的即死效果
- **嘲讽 vs 潜行**: 潜行随从无法被强制攻击嘲讽目标
- **风怒 vs 法术强度**: 风怒随从受益于法术强度加成

## 💡 策略建议

### 早期游戏
- 优先使用冲锋随从抢夺节奏
- 利用嘲讽随从保护英雄
- 合理使用潜行随从进行安全输出

### 中期游戏
- 圣盾随从提供稳定的场面控制
- 风怒随从可以快速清理场面
- 法术强度随从配合法术进行爆发

### 后期游戏
- 吸血随从提供续航能力
- 剧毒随从处理大型威胁
- 复合特效随从通常能决定胜负
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 卡牌特效详解",
            box=box.ROUNDED,
            border_style="purple"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    def _show_ai_help(self):
        """显示AI系统帮助"""
        help_content = """
# 🤖 AI系统详解

## 🎯 AI难度等级

### 🟢 简单难度
- **特点**: AI经常失误，决策较为随机
- **适合**: 新手玩家学习游戏机制
- **行为**:
  - 经常出不符合当前局势的牌
  - 攻击目标选择不够优化
  - 资源管理效率较低

### 🔵 普通难度
- **特点**: AI正常发挥，平衡的游戏体验
- **适合**: 一般玩家练习和娱乐
- **行为**:
  - 基本合理的出牌顺序
  - 正确的攻击目标选择
  - 适度的资源管理

### 🟠 困难难度
- **特点**: AI表现出色，需要玩家认真应对
- **适合**: 有经验的玩家挑战
- **行为**:
  - 优化的出牌策略
  - 精准的攻击时机把握
  - 高效的资源利用

### 🔴 专家难度
- **特点**: AI完美发挥，提供极限挑战
- **适合**: 高手玩家测试策略
- **行为**:
  - 近乎完美的决策
  - 复杂的战术组合
  - 最优的资源管理

## 🧠 AI策略系统

### 规则AI (Rule-Based AI)
- **原理**: 基于预设的规则和决策树
- **特点**:
  - 决策速度快，响应及时
  - 行为可预测，便于学习应对
  - 稳定性强，不会出现明显失误
- **适用场景**:
  - 新手教学
  - 稳定的游戏体验
  - 性能要求较高的环境

### 混合AI (Hybrid AI)
- **原理**: 结合规则系统和深度学习技术
- **特点**:
  - 更智能的决策能力
  - 能够适应不同局势
  - 具有一定的学习能力
- **技术优势**:
  - 大语言模型(LLM)加持
  - 动态策略调整
  - 更接近人类的思维方式

## 🎭 AI个性系统

### 适应性学习者 (Adaptive Learner)
- **特点**: 根据对手行为调整策略
- **风格**: 平衡型，能够适应各种局势
- **优势**:
  - 学习对手的习惯
  - 动态调整战术
  - 中庸但全面的策略

### 激进狂战士 (Aggressive Berserker)
- **特点**: 倾向于快速进攻
- **风格**: 快节奏，高压力
- **战术**:
  - 优先出低费高攻随从
  - 积极攻击英雄
  - 追求速胜

### 智慧防御者 (Wise Defender)
- **特点**: 注重防御和资源积累
- **风格**: 稳健，后发制人
- **战术**:
  - 优先建立防御
  - 合理使用资源
  - 等待最佳时机

## 📊 AI决策机制

### 信息收集
- **手牌分析**: 评估可用卡牌的价值
- **场面判断**: 分析双方战场局势
- **资源计算**: 考虑法力值和卡牌优势

### 策略制定
- **短期目标**: 当前回合的最优行动
- **长期规划**: 未来几回合的战略布局
- **风险评估**: 各种选择的成功概率

### 动作执行
- **出牌顺序**: 最优的卡牌打出序列
- **攻击选择**: 最有效的攻击目标
- **技能使用**: 英雄技能的最佳时机

## 💡 对战AI的建议

### 观察AI行为
- 注意AI的出牌模式
- 分析AI的攻击偏好
- 预测AI的可能行动

### 制定针对性策略
- 利用AI的决策特点
- 选择合适的反制战术
- 控制游戏节奏

### 心理战术
- 制造假象诱导AI失误
- 控制信息暴露程度
- 在关键时刻出奇制胜
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 AI系统详解",
            box=box.ROUNDED,
            border_style="cyan"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    def _show_tips_help(self):
        """显示游戏技巧帮助"""
        help_content = """
# 💡 游戏策略与技巧

## 🎯 核心策略原则

### 1. 法力管理
- **效率优先**: 确保每回合的法力都得到充分利用
- **曲线规划**: 合理安排低费和高费卡牌的比例
- **预留余地**: 为关键卡牌保留足够法力

### 2. 节奏控制
- **主动权**: 把握进攻和防守的时机
- **响应式**: 根据对手行动调整策略
- **压制力**: 在关键时刻施加压力

### 3. 资源优势
- **卡牌优势**: 保持手牌数量不低于对手
- **场面控制**: 维持战场上的主动权
- **生命管理**: 平衡进攻和自我保护

## 🃏 卡牌使用技巧

### 随从牌使用
- **时机把握**:
  - 早期：建立场面优势
  - 中期：巩固控制和交换
  - 后期：终结比赛或扭转局势

- **位置安排**:
  - 保护重要随从
  - 利用嘲讽随从
  - 考虑攻击顺序

- **特效配合**:
  - 嘲讽随从保护高价值目标
  - 圣盾随从处理威胁单位
  - 冲锋随从抢夺先手

### 法术牌使用
- **即时效果**: 把握使用时机
- **combo配合**: 与其他卡牌形成连击
- **应急用途**: 危急情况下的救命稻草

## ⚔️ 战斗技巧

### 攻击选择
- **优先级判断**:
  1. 威胁最大的敌方随从
  2. 具有危险特效的随从
  3.敌方英雄（在安全的情况下）

- **交换计算**:
  - 评估我方损失
  - 考虑长远收益
  - 避免不必要的牺牲

### 防守策略
- **嘲讽利用**: 合理布置嘲讽随从
- **圣盾保护**: 用圣盾随从挡伤害
- **潜行突袭**: 保持潜行随从的安全

## 🎮 不同阶段策略

### 早期游戏 (1-4回合)
**目标**: 建立基础，积累资源
- 出低费随从控制场面
- 合理使用法术清理威胁
- 保护英雄生命值

### 中期游戏 (5-8回合)
**目标**: 扩大优势，稳定控制
- 出中等费用的强力随从
- 进行有利的随从交换
- 开始施加压力

### 后期游戏 (9+回合)
**目标**: 终结比赛，扭转局势
- 使用高费终极卡牌
- 寻找致命一击的机会
- 应对对手的强力反击

## 🤖 对战AI特殊技巧

### AI行为分析
- **模式识别**: 识别AI的决策模式
- **规律利用**: 利用AI的行为规律
- **弱点攻击**: 针对AI的策略弱点

### 心理战术
- **信息控制**: 隐藏关键信息
- **假象制造**: 引导AI错误决策
- **节奏变化**: 打乱AI的部署

## 📈 进阶技巧

### 概率计算
- **抽牌期望**: 计算关键卡牌的抽到概率
- **伤害预估**: 预测未来几回合的伤害输出
- **风险评估**: 评估各种选择的成功概率

### 组合战术
- **连击配合**: 多张卡牌的连续使用
- **特效协同**: 不同特效的配合使用
- **时机把控**: 在最合适的时机出手

### 适应性策略
- **灵活调整**: 根据局势变化调整策略
- **应急方案**: 准备应对突发情况的计划
- **长期规划**: 制定多回合的战略布局

## 🎯 常见错误避免

### 新手常见错误
1. **法力浪费**: 未能充分利用每回合的法力
2. **过度进攻**: 忽视防守的重要性
3. **资源管理**: 不合理使用关键卡牌
4. **目标选择**: 攻击优先级判断错误

### 进阶玩家误区
1. **思维固化**: 依赖固定战术模式
2. **信息忽视**: 忽略重要的游戏信息
3. **情绪影响**: 让情绪影响决策判断
4. **过度自信**: 低估对手的应对能力

## 🏆 成功心态

### 游戏态度
- **学习心态**: 从每局游戏中学习经验
- **耐心冷静**: 在压力下保持冷静思考
- **享受过程**: 享受策略思考的乐趣

### 持续进步
- **复盘总结**: 分析游戏中的关键决策
- **战术更新**: 不断学习和尝试新战术
- **交流学习**: 与其他玩家交流心得

记住：最好的策略是能够根据具体局势灵活调整的策略！
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 游戏策略与技巧",
            box=box.ROUNDED,
            border_style="green"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

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

            # 检查是否有可攻击的随从
            if "battlefield" in game_state:
                player_field = game_state["battlefield"].get("player", [])
                attackable_minions = [
                    minion for minion in player_field
                    if minion.get("can_attack", False)
                ]
                if attackable_minions:
                    # 添加攻击命令选项
                    commands.insert(-1, f"攻击 0-{len(attackable_minions)-1}")

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

        elif command_type == 'spell':
            return await self._handle_spell_by_name(params)

        elif command_type == 'end_turn':
            return await self._handle_end_turn()

        else:
            error_msg = self._input_handler.format_error_message('invalid_command', f"未知命令类型: {command_type}")
            return False, error_msg, None

    async def _handle_play_card(self, card_index: int, target: Optional[str] = None) -> Tuple[bool, str, Optional[dict]]:
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

        action_data = {'action': 'play_card', 'card_index': card_index, 'card': card}
        if target:
            action_data['target'] = target

        return True, success_msg, action_data

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
    battlefield_table.add_column("特效", style="blue", width=8)

    # 玩家随从
    for minion in player_field:
        name = minion.get("name", "未知")
        attack = minion.get("attack", 0)
        health = minion.get("health", 0)
        can_attack = minion.get("can_attack", False)
        mechanics = minion.get("mechanics", [])

        attributes = f"{attack}/{health}"
        status = "🗡️ 可攻" if can_attack else "😴 休眠"

        # 特效显示
        mechanics_display = _format_mechanics_display(mechanics)

        battlefield_table.add_row("👤 玩家", name, attributes, status, mechanics_display)

    # 对手随从
    for minion in opponent_field:
        name = minion.get("name", "未知")
        attack = minion.get("attack", 0)
        health = minion.get("health", 0)
        can_attack = minion.get("can_attack", False)
        mechanics = minion.get("mechanics", [])

        attributes = f"{attack}/{health}"
        status = "⚠️ 威胁" if can_attack else "😴 休眠"

        # 特效显示
        mechanics_display = _format_mechanics_display(mechanics)

        battlefield_table.add_row("🤖 对手", name, attributes, status, mechanics_display)

    return battlefield_table


def _format_mechanics_display(mechanics: list) -> str:
    """格式化特效显示"""
    if not mechanics:
        return "无"

    # 特效映射表
    mechanics_map = {
        "taunt": "🛡️嘲讽",
        "divine_shield": "✨圣盾",
        "stealth": "🌑潜行",
        "ranged": "🏹远程",
        "spell_power": "🔥法强",
        "windfury": "💨风怒",
        "lifesteal": "💀吸血",
        "poisonous": "☠️剧毒",
        "charge": "⚡冲锋"
    }

    # 转换特效为显示文本
    display_texts = []
    for mechanic in mechanics:
        display_text = mechanics_map.get(mechanic, mechanic)
        display_texts.append(display_text)

    return " ".join(display_texts) if display_texts else "无"


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
            'spell': [
                re.compile(r'^法术\s*(.+)$', re.IGNORECASE),
                re.compile(r'^spell\s*(.+)$', re.IGNORECASE)
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
                    elif command == 'spell':
                        spell_name = match.group(1).strip()
                        return True, (command, spell_name)
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
  • 数字选择攻击 - 当有可攻击随从时，选择对应数字

💪 **其他命令**：
  • 技能 / skill - 使用英雄技能（消耗2法力）
  • 结束回合 / end turn - 结束当前回合
  • 帮助 / help / ? - 显示帮助信息
  • 退出 / quit / exit - 退出游戏

💡 **提示**：
  • 卡牌编号见手牌区域
  • 绿色✅表示可以出牌，红色❌表示法力不足
  • 随从状态：🗡️可攻击，😴休眠中
  • 当随从显示🗡️时，可以在命令中选择攻击
  • 攻击格式：攻击 <随从索引> <目标索引>
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
                    "mechanics": getattr(minion, 'mechanics', []),
                    "index": i
                })

            # AI随从
            for i, minion in enumerate(ai_player.field):
                battlefield["opponent"].append({
                    "name": minion.name if hasattr(minion, 'name') else str(minion),
                    "attack": minion.attack if hasattr(minion, 'attack') else 0,
                    "health": minion.health if hasattr(minion, 'health') else 0,
                    "can_attack": getattr(minion, 'can_attack', False),
                    "mechanics": getattr(minion, 'mechanics', []),
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
                "battlefield": battlefield,
                "turn_number": self.game_engine.turn_number
            }

        except Exception as e:
            self.console.print(f"[red]❌ 转换游戏状态失败: {e}[/red]")
            return {}

    def _render_static_display(self):
        """静态渲染游戏状态"""
        try:
            self.console.clear()

            # 渲染标题（包含轮数信息）
            turn_number = self.game_state.get("turn_number", 1)
            title_text = f"🎮 Card Battle Arena Enhanced - 静态版 (第{turn_number}轮)"
            self.console.print(Align.center(Text(title_text, style="bold cyan")))
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
                    commands.append(f"{len(commands)+1}. 出牌 {card_name} (费用{card.get('cost', 0)})")

            # 检查是否有可攻击的随从 - 修复攻击命令生成
            if "battlefield" in game_state:
                player_field = game_state["battlefield"].get("player", [])
                opponent_field = game_state["battlefield"].get("opponent", [])

                attackable_minions = []
                for i, minion in enumerate(player_field):
                    if minion.get("can_attack", False):
                        attackable_minions.append((i, minion))

                if attackable_minions:
                    for minion_idx, minion in attackable_minions:
                        minion_name = minion.get("name", "随从")

                        # 检查可攻击的目标
                        available_targets = self._get_attack_targets_for_minion(minion_idx, opponent_field)

                        if available_targets:
                            if len(available_targets) == 1:
                                target_desc = available_targets[0]
                            else:
                                target_desc = f"{len(available_targets)}个目标"

                            commands.append(f"{len(commands)+1}. 攻击: {minion_name} → {target_desc}")

            # 检查是否可以使用英雄技能
            if mana >= 2:
                commands.append(f"{len(commands)+1}. 使用英雄技能 (2法力)")

            # 检查是否有可攻击的法术卡牌
            spell_cards = []
            for i, card in enumerate(game_state["hand"]):
                # 检查是否为法术卡牌且有攻击力，并且法力值足够
                is_spell = card.get("type") == "spell"
                has_attack = card.get("attack", 0) > 0
                can_afford = card.get("cost", 0) <= mana

                if is_spell and has_attack and can_afford:
                    # 伤害法术卡牌
                    spell_cards.append((i, card))

            if spell_cards:
                for i, card in spell_cards:
                    card_name = card.get("name", "法术")
                    # 检查是否有多个目标
                    if opponent_field:
                        # 检查嘲讽机制
                        taunt_minions = [m for m in opponent_field if "taunt" in m.get("mechanics", [])]
                        if len(taunt_minions) > 0:
                            # 有嘲讽，只能攻击嘲讽
                            if len(taunt_minions) == 1:
                                target_desc = f"{taunt_minions[0].get('name', '嘲讽随从')}"
                            else:
                                target_desc = f"{len(taunt_minions)}个嘲讽目标"
                        else:
                            # 没有嘲讽，可以攻击随从或英雄
                            if len(opponent_field) == 1:
                                target_desc = f"{opponent_field[0].get('name', '随从')}或英雄"
                            else:
                                target_desc = f"{len(opponent_field)+1}个目标"
                    else:
                        # 没有随从，只能攻击英雄
                        target_desc = "敌方英雄"

                    commands.append(f"{len(commands)+1}. 法术: {card_name} → {target_desc}")

        # 添加固定命令
        commands.append(f"{len(commands)+1}. 结束回合")
        commands.append(f"{len(commands)+1}. 查看帮助")
        commands.append(f"{len(commands)+1}. 游戏设置")
        commands.append(f"{len(commands)+1}. 退出游戏")

        return commands

    def _get_attack_targets_for_minion(self, minion_idx: int, opponent_field: list) -> list:
        """获取指定随从可攻击的目标列表"""
        targets = []

        if not opponent_field:
            # 对手没有随从，可以攻击英雄
            targets.append("敌方英雄")
        else:
            # 检查是否有嘲讽随从
            taunt_minions = []
            non_taunt_minions = []

            for i, minion in enumerate(opponent_field):
                mechanics = minion.get("mechanics", [])
                if "taunt" in mechanics:
                    taunt_minions.append(f"{minion.get('name', '随从')}({i})")
                else:
                    non_taunt_minions.append(f"{minion.get('name', '随从')}({i})")

            # 如果有嘲讽随从，必须攻击嘲讽
            if taunt_minions:
                targets.extend(taunt_minions)
            else:
                # 没有嘲讽，可以攻击任何随从或英雄
                targets.extend(non_taunt_minions)
                targets.append("敌方英雄")

        return targets

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

        elif command_type == 'spell':
            return await self._handle_spell_by_name(params)

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

        elif "攻击" in selected_command:
            return await self._handle_attack_from_command(selected_command)

        elif "法术" in selected_command:
            return await self._handle_spell_command(selected_command)

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

    async def _handle_attack_from_command(self, command: str) -> Tuple[bool, str, Optional[dict]]:
        """从命令字符串处理攻击命令 - 改进版本支持目标选择"""
        try:
            # 解析攻击命令，例如 "1. 攻击: 邪犬 → 石像鬼" 或 "2. 攻击: 愤怒的小鸡 → 敌方英雄"
            if "→" not in command:
                # 简单的攻击命令，需要用户选择目标
                return await self._handle_attack_target_selection(command)

            parts = command.split(" → ")
            if len(parts) != 2:
                return False, f"❌ 无法解析攻击命令: {command}", None

            attacker_part = parts[0].strip()
            target_part = parts[1].strip()

            # 提取随从名称 (去掉"攻击: "前缀和编号)
            if "攻击:" in attacker_part:
                minion_name = attacker_part.split("攻击:")[1].strip()
            else:
                minion_name = attacker_part

            # 检查是否为多目标描述（如"3个目标"）
            if "个目标" in target_part:
                # 提取随从名称，进入目标选择流程
                return await self._handle_attack_target_selection(f"攻击: {minion_name}")

            # 获取可攻击的随从列表
            if not self.game_state or 'battlefield' not in self.game_state:
                return False, "❌ 游戏状态未初始化", None

            player_field = self.game_state['battlefield'].get('player', [])
            attackable_minions = [
                (i, minion) for i, minion in enumerate(player_field)
                if minion.get('can_attack', False)
            ]

            if not attackable_minions:
                return False, "❌ 没有可攻击的随从", None

            # 查找匹配的随从
            selected_minion = None
            selected_index = None

            # 尝试按名称匹配
            for i, minion in attackable_minions:
                if minion_name in minion.get('name', ''):
                    selected_minion = minion
                    selected_index = i
                    break

            # 如果名称匹配失败，尝试按数字匹配
            if selected_minion is None and minion_name.isdigit():
                index = int(minion_name) - 1  # 转换为0-based索引
                if 0 <= index < len(attackable_minions):
                    selected_index, selected_minion = attackable_minions[index]

            if selected_minion is None:
                return False, f"❌ 找不到随从: {minion_name}", None

            # 解析攻击目标
            opponent_field = self.game_state['battlefield'].get('opponent', [])

            if "英雄" in target_part or "敌方英雄" in target_part:
                # 攻击英雄
                target_info = {'type': 'hero'}
                target_name = '敌方英雄'
            else:
                # 攻击随从 - 解析目标索引
                target_idx = None
                target_name = target_part

                # 尝试从目标描述中提取索引
                import re
                match = re.search(r'\((\d+)\)', target_part)
                if match:
                    target_idx = int(match.group(1))
                else:
                    # 尝试按名称匹配
                    for i, minion in enumerate(opponent_field):
                        if minion.get('name', '') in target_part:
                            target_idx = i
                            break

                if target_idx is not None and target_idx < len(opponent_field):
                    target_minion = opponent_field[target_idx]
                    target_info = {'type': 'minion', 'index': target_idx, 'minion': target_minion}
                    target_name = target_minion.get('name', '随从')
                else:
                    return False, f"❌ 找不到攻击目标: {target_part}", None

            attacker_name = selected_minion.get('name', '随从')

            success_msg = self._input_handler.format_success_message('attack', f"{attacker_name} 攻击 {target_name}")
            return True, success_msg, {
                'action': 'attack',
                'attacker_index': selected_index,
                'attacker': selected_minion,
                'target': target_info
            }

        except Exception as e:
            return False, f"❌ 处理攻击命令时出错: {str(e)}", None

    async def _handle_attack_target_selection(self, command: str) -> Tuple[bool, str, Optional[dict]]:
        """处理需要目标选择的攻击命令"""
        try:
            # 提取随从名称
            if "攻击:" in command:
                minion_name = command.split("攻击:")[1].strip()
            else:
                return False, f"❌ 无法解析攻击命令: {command}", None

            # 获取可攻击的随从
            player_field = self.game_state['battlefield'].get('player', [])
            attackable_minions = [
                (i, minion) for i, minion in enumerate(player_field)
                if minion.get('can_attack', False)
            ]

            selected_minion = None
            selected_index = None

            for i, minion in attackable_minions:
                if minion_name in minion.get('name', ''):
                    selected_minion = minion
                    selected_index = i
                    break

            if selected_minion is None:
                return False, f"❌ 找不到随从: {minion_name}", None

            # 获取可选目标
            opponent_field = self.game_state['battlefield'].get('opponent', [])
            available_targets = self._get_attack_targets_for_minion(selected_index, opponent_field)

            if not available_targets:
                return False, "❌ 没有可攻击的目标", None

            if len(available_targets) == 1:
                # 只有一个目标，直接攻击
                target = available_targets[0]
                if "英雄" in target:
                    target_info = {'type': 'hero'}
                    target_name = '敌方英雄'
                else:
                    # 解析随从目标
                    import re
                    match = re.search(r'\((\d+)\)', target)
                    if match:
                        target_idx = int(match.group(1))
                        if target_idx < len(opponent_field):
                            target_minion = opponent_field[target_idx]
                            target_info = {'type': 'minion', 'index': target_idx, 'minion': target_minion}
                            target_name = target_minion.get('name', '随从')
                        else:
                            return False, f"❌ 目标索引无效: {target_idx}", None
                    else:
                        return False, f"❌ 无法解析目标: {target}", None

                attacker_name = selected_minion.get('name', '随从')
                success_msg = self._input_handler.format_success_message('attack', f"{attacker_name} 攻击 {target_name}")
                return True, success_msg, {
                    'action': 'attack',
                    'attacker_index': selected_index,
                    'attacker': selected_minion,
                    'target': target_info
                }
            else:
                # 多个目标，需要用户选择
                self.console.print(f"\n⚔️ {selected_minion.get('name', '随从')} 可以攻击以下目标:")
                for i, target in enumerate(available_targets):
                    self.console.print(f"   {i+1}. {target}")

                target_choice = Prompt.ask(
                    "请选择攻击目标",
                    choices=[str(i+1) for i in range(len(available_targets))],
                    default="1"
                )

                target_idx = int(target_choice) - 1
                selected_target = available_targets[target_idx]

                if "英雄" in selected_target:
                    target_info = {'type': 'hero'}
                    target_name = '敌方英雄'
                else:
                    import re
                    match = re.search(r'\((\d+)\)', selected_target)
                    if match:
                        target_idx = int(match.group(1))
                        if target_idx < len(opponent_field):
                            target_minion = opponent_field[target_idx]
                            target_info = {'type': 'minion', 'index': target_idx, 'minion': target_minion}
                            target_name = target_minion.get('name', '随从')
                        else:
                            return False, f"❌ 目标索引无效: {target_idx}", None
                    else:
                        return False, f"❌ 无法解析目标: {selected_target}", None

                attacker_name = selected_minion.get('name', '随从')
                success_msg = self._input_handler.format_success_message('attack', f"{attacker_name} 攻击 {target_name}")
                return True, success_msg, {
                    'action': 'attack',
                    'attacker_index': selected_index,
                    'attacker': selected_minion,
                    'target': target_info
                }

        except Exception as e:
            return False, f"❌ 处理攻击目标选择时出错: {str(e)}", None

    async def _handle_play_card(self, card_index: int, target: Optional[str] = None) -> Tuple[bool, str, Optional[dict]]:
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

        action_data = {'action': 'play_card', 'card_index': card_index, 'card': card}
        if target:
            action_data['target'] = target

        return True, success_msg, action_data

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
        if self.game_engine:
            # 使用真正的游戏引擎
            try:
                result = self.game_engine.use_hero_power(0)  # 0是玩家索引
                if result.get("success", False):
                    damage = result.get("damage", 0)
                    self.console.print(f"[green]✅ 英雄技能造成{damage}点伤害！[/green]")

                    # 立即更新状态
                    self.update_game_state()

                    # 检查游戏是否结束
                    if self.game_engine.game_over:
                        winner = self.game_engine.get_winner()
                        self.console.print(f"\n[bold yellow]🎮 游戏结束！{winner}获胜！[/bold yellow]")
                else:
                    reason = result.get("reason", "未知错误")
                    self.console.print(f"[red]❌ 英雄技能失败: {reason}[/red]")
            except Exception as e:
                self.console.print(f"[red]❌ 游戏引擎英雄技能出错: {e}[/red]")
        else:
            # 回退到模拟模式 - 只减少法力值
            if 'player' in self.game_state:
                self.game_state['player']['mana'] -= 2

            await asyncio.sleep(0.5)
            self.console.print("[dim]💪 英雄技能已使用（模拟模式）[/dim]")

    async def _handle_attack_executed(self, action_data: dict):
        """处理攻击执行并更新状态"""
        if self.game_engine:
            # 使用真正的游戏引擎执行攻击
            try:
                attacker_index = action_data.get('attacker_index')
                target_info = action_data.get('target')

                # 确定攻击目标类型
                if target_info['type'] == 'hero':
                    # 攻击敌方英雄
                    target_type = 'hero'
                    target_index = None
                else:
                    # 攻击敌方随从
                    target_type = 'minion'
                    target_index = target_info.get('index')

                # 构造正确的target字符串
                if target_type == 'hero':
                    target_str = "英雄"
                else:
                    target_str = f"随从_{target_index}"

                # 执行攻击（使用正确的3参数格式）
                result = self.game_engine.attack_with_minion(0, attacker_index, target_str)

                if result.get("success", False):
                    attacker_name = result.get("attacker_name", "随从")
                    target_name = result.get("target_name", "目标")
                    damage = result.get("damage", 0)

                    self.console.print(f"[green]✅ {attacker_name} 对 {target_name} 造成 {damage} 点伤害！[/green]")

                    # 如果目标被摧毁，显示额外信息
                    if result.get("target_destroyed", False):
                        self.console.print(f"[red]💀 {target_name} 被摧毁了！[/red]")

                    # 立即更新状态
                    self.update_game_state()

                    # 检查游戏是否结束
                    if self.game_engine.game_over:
                        winner = self.game_engine.get_winner()
                        self.console.print(f"\n[bold yellow]🎮 游戏结束！{winner}获胜！[/bold yellow]")
                else:
                    error_msg = result.get("message", "攻击失败")
                    self.console.print(f"[red]❌ 攻击失败: {error_msg}[/red]")

            except Exception as e:
                self.console.print(f"[red]❌ 游戏引擎攻击出错: {e}[/red]")
        else:
            # 回退到模拟模式
            await self._simulate_attack_executed(action_data)

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

        self.console.print(f"[green]✅ 第{self.game_state.get('turn_number', 1)}回合开始！[/green]")

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

    async def _simulate_attack_executed(self, action_data: dict):
        """模拟攻击执行（回退模式）"""
        attacker_index = action_data.get('attacker_index')
        target_info = action_data.get('target')
        attacker = action_data.get('attacker')

        if not attacker or not self.game_state:
            return

        attacker_name = attacker.get('name', '随从')
        attacker_attack = attacker.get('attack', 0)

        if target_info['type'] == 'hero':
            # 攻击敌方英雄
            target_name = '敌方英雄'

            # 减少敌方英雄生命值
            if 'opponent' in self.game_state:
                self.game_state['opponent']['health'] -= attacker_attack

            self.console.print(f"[green]✅ {attacker_name} 对 {target_name} 造成 {attacker_attack} 点伤害！[/green]")

            # 检查是否击败了敌方英雄
            if self.game_state['opponent']['health'] <= 0:
                self.game_state['opponent']['health'] = 0
                self.console.print(f"\n[bold yellow]🎮 游戏结束！玩家获胜！[/bold yellow]")
        else:
            # 攻击敌方随从
            target_minion = target_info.get('minion')
            target_index = target_info.get('index')

            if target_minion:
                target_name = target_minion.get('name', '随从')
                target_health = target_minion.get('health', 0)

                # 计算伤害
                damage_dealt = attacker_attack
                target_health_after = target_health - damage_dealt

                # 更新敌方随从生命值
                if 'battlefield' in self.game_state and 'opponent' in self.game_state['battlefield']:
                    opponent_field = self.game_state['battlefield']['opponent']
                    if target_index < len(opponent_field):
                        opponent_field[target_index]['health'] = target_health_after

                self.console.print(f"[green]✅ {attacker_name} 对 {target_name} 造成 {damage_dealt} 点伤害！[/green]")

                # 检查是否摧毁了目标
                if target_health_after <= 0:
                    self.console.print(f"[red]💀 {target_name} 被摧毁了！[/red]")
                    # 从战场移除被摧毁的随从
                    if 'battlefield' in self.game_state and 'opponent' in self.game_state['battlefield']:
                        opponent_field = self.game_state['battlefield']['opponent']
                        if target_index < len(opponent_field):
                            opponent_field.pop(target_index)
                            # 更新敌方随从数量
                            if 'opponent' in self.game_state:
                                self.game_state['opponent']['field_count'] = len(opponent_field)

        # 攻击者设置为已攻击状态
        if 'battlefield' in self.game_state and 'player' in self.game_state['battlefield']:
            player_field = self.game_state['battlefield']['player']
            if attacker_index < len(player_field):
                player_field[attacker_index]['can_attack'] = False

        await asyncio.sleep(0.5)

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

    def show_help(self):
        """显示帮助（静态版本）"""
        while True:
            self.console.clear()

            # 帮助菜单
            help_menu = Table(show_header=True, box=box.ROUNDED)
            help_menu.add_column("选项", style="yellow", width=8)
            help_menu.add_column("帮助分类", style="white")
            help_menu.add_column("说明", style="dim")

            help_menu.add_row("1", "🎮 基本操作", "[dim]游戏命令和规则说明[/dim]")
            help_menu.add_row("2", "🃏 卡牌特效", "[dim]详细说明各种卡牌特效[/dim]")
            help_menu.add_row("3", "🤖 AI系统", "[dim]AI难度和策略介绍[/dim]")
            help_menu.add_row("4", "💡 游戏技巧", "[dim]策略建议和游戏提示[/dim]")
            help_menu.add_row("0", "🔙 返回游戏", "[dim]返回游戏界面[/dim]")

            self.console.print(Align.center(help_menu))
            self.console.print()

            choice = Prompt.ask(
                "[bold green]请选择帮助分类[/bold green]",
                choices=["1", "2", "3", "4", "0"],
                default="0"
            )

            if choice == "0":
                break
            elif choice == "1":
                self._show_basic_help()
            elif choice == "2":
                self._show_card_effects_help()
            elif choice == "3":
                self._show_ai_help()
            elif choice == "4":
                self._show_tips_help()

    def _show_basic_help(self):
        """显示基本操作帮助"""
        help_content = """
# 🎮 基本操作指南

## 📋 游戏命令

### 基础命令
- **出牌 <编号>** 或 **<编号>** - 打出指定编号的手牌
- **攻击 <随从> <目标>** - 指挥随从攻击目标
- **技能** - 使用英雄技能（消耗2点法力）
- **结束回合** - 结束当前回合，轮到对手行动
- **帮助** 或 **?** - 显示帮助信息
- **退出** - 退出游戏

## 🎯 游戏规则

### 法力系统
- 每回合开始时获得1点法力值
- 法力值上限最多为10点
- 出牌需要消耗相应的法力值

### 卡牌类型
- **🃏 随从牌**:
  - 上场战斗，有攻击力和生命值
  - 刚上场的随从需要等待一回合才能攻击
  - 可以拥有特殊特效（嘲讽、圣盾等）

- **✨ 法术牌**:
  - 使用后立即产生效果
  - 可能造成伤害、治疗或提供其他效果

### 胜利条件
- 将对手英雄的生命值降至0即可获胜
- 对手将你的生命值降至0则失败

## 💡 界面说明

### 状态面板
- **❤️ 生命值**: 当前/最大生命值
- **💰 法力值**: 当前可用/最大法力值
- **🃋 手牌数**: 当前手牌数量
- **⚔️ 随从数**: 战场上随从数量

### 战场信息
- **阵营**: 👤玩家 / 🤖对手
- **随从**: 随从名称
- **属性**: 攻击力/生命值
- **状态**: 🗡️可攻击 / 😴休眠中
- **特效**: 显示随从拥有的特殊能力

### 手牌显示
- **编号**: 卡牌的选择编号
- **卡牌名称**: 卡牌的名称
- **费用**: 打出此牌需要的法力值
- **属性**: 随从的攻击/生命 或 法术的威力
- **状态**: ✅可出 / ❌费用不足
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 基本操作指南",
            box=box.ROUNDED,
            border_style="blue"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    def _show_card_effects_help(self):
        """显示卡牌特效帮助"""
        help_content = """
# 🃏 卡牌特效详解

## 🛡️ 防御型特效

### 🛡️ 嘲讽 (Taunt)
- **效果**: 强制敌方随从优先攻击具有嘲讽的随从
- **策略价值**: 保护其他随从和英雄，是防御战术的核心
- **搭配建议**: 与高血量随从配合效果更佳
- **克制方法**: 使用法术牌或具有特效的随从处理

### ✨ 圣盾 (Divine Shield)
- **效果**: 免疫下一次受到的伤害，受到伤害后圣盾消失
- **策略价值**: 有效对抗高攻击力单体攻击
- **恢复方式**: 特定法术可以重新获得圣盾
- **注意事项**: 只能抵挡一次伤害，之后消失

### 🌑 潜行 (Stealth)
- **效果**: 敌方无法选择潜行随从作为目标，攻击后解除潜行
- **策略价值**: 保护关键随从免受法术和攻击
- **持续时间**: 直到随从造成伤害为止
- **克制方法**: 范围效果法术或攻击其他目标

## ⚔️ 攻击型特效

### ⚡ 冲锋 (Charge)
- **效果**: 随从可以立即攻击，无需等待一回合
- **策略价值**: 快速施加压力，抢夺节奏优势
- **常见搭配**: 高攻击力随从
- **风险**: 容易成为敌方目标

### 💨 风怒 (Windfury)
- **效果**: 每回合可以攻击两次
- **策略价值**: 大幅提升输出能力
- **注意事项**: 每次攻击都需要独立的攻击目标
- **搭配建议**: 配合治疗或圣盾效果

### 🏹 远程 (Ranged)
- **效果**: 可以从安全距离攻击，避免受到部分反击伤害
- **策略价值**: 安全输出，保护脆弱的随从
- **射程**: 通常可以攻击任何敌方目标
- **定位**: 后排输出单位

## 🔥 魔法型特效

### 🔥 法术强度 (Spell Power)
- **效果**: 提升己方法术的伤害效果
- **策略价值**: 增强法术卡牌的威力
- **计算方式**: 通常按百分比提升法术伤害
- **搭配**: 与伤害法术配合使用

### 💀 吸血 (Lifesteal)
- **效果**: 造成伤害的同时为英雄恢复等量生命值
- **策略价值**: 提供持续的续航能力
- **限制**: 只能通过攻击触发
- **价值**: 在持久战中表现出色

### ☠️ 剧毒 (Poisonous)
- **效果**: 对随从造成任何伤害即可直接消灭目标
- **策略价值**: 高效处理大型随从
- **注意事项**: 对英雄无效，只对随从生效
- **策略**: 用于清除敌方强力随从

## 🎯 特殊机制

### 复合特效
许多卡牌拥有多种特效组合：
- **嘲讽+圣盾**: 理想的防御组合
- **冲锋+风怒**: 强大的进攻组合
- **潜行+吸血**: 持续续航的组合

### 特效互动
- **圣盾 vs 剧毒**: 圣盾可以抵挡剧毒的即死效果
- **嘲讽 vs 潜行**: 潜行随从无法被强制攻击嘲讽目标
- **风怒 vs 法术强度**: 风怒随从受益于法术强度加成

## 💡 策略建议

### 早期游戏
- 优先使用冲锋随从抢夺节奏
- 利用嘲讽随从保护英雄
- 合理使用潜行随从进行安全输出

### 中期游戏
- 圣盾随从提供稳定的场面控制
- 风怒随从可以快速清理场面
- 法术强度随从配合法术进行爆发

### 后期游戏
- 吸血随从提供续航能力
- 剧毒随从处理大型威胁
- 复合特效随从通常能决定胜负
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 卡牌特效详解",
            box=box.ROUNDED,
            border_style="purple"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    def _show_ai_help(self):
        """显示AI系统帮助"""
        help_content = """
# 🤖 AI系统详解

## 🎯 AI难度等级

### 🟢 简单难度
- **特点**: AI经常失误，决策较为随机
- **适合**: 新手玩家学习游戏机制
- **行为**:
  - 经常出不符合当前局势的牌
  - 攻击目标选择不够优化
  - 资源管理效率较低

### 🔵 普通难度
- **特点**: AI正常发挥，平衡的游戏体验
- **适合**: 一般玩家练习和娱乐
- **行为**:
  - 基本合理的出牌顺序
  - 正确的攻击目标选择
  - 适度的资源管理

### 🟠 困难难度
- **特点**: AI表现出色，需要玩家认真应对
- **适合**: 有经验的玩家挑战
- **行为**:
  - 优化的出牌策略
  - 精准的攻击时机把握
  - 高效的资源利用

### 🔴 专家难度
- **特点**: AI完美发挥，提供极限挑战
- **适合**: 高手玩家测试策略
- **行为**:
  - 近乎完美的决策
  - 复杂的战术组合
  - 最优的资源管理

## 🧠 AI策略系统

### 规则AI (Rule-Based AI)
- **原理**: 基于预设的规则和决策树
- **特点**:
  - 决策速度快，响应及时
  - 行为可预测，便于学习应对
  - 稳定性强，不会出现明显失误
- **适用场景**:
  - 新手教学
  - 稳定的游戏体验
  - 性能要求较高的环境

### 混合AI (Hybrid AI)
- **原理**: 结合规则系统和深度学习技术
- **特点**:
  - 更智能的决策能力
  - 能够适应不同局势
  - 具有一定的学习能力
- **技术优势**:
  - 大语言模型(LLM)加持
  - 动态策略调整
  - 更接近人类的思维方式

## 🎭 AI个性系统

### 适应性学习者 (Adaptive Learner)
- **特点**: 根据对手行为调整策略
- **风格**: 平衡型，能够适应各种局势
- **优势**:
  - 学习对手的习惯
  - 动态调整战术
  - 中庸但全面的策略

### 激进狂战士 (Aggressive Berserker)
- **特点**: 倾向于快速进攻
- **风格**: 快节奏，高压力
- **战术**:
  - 优先出低费高攻随从
  - 积极攻击英雄
  - 追求速胜

### 智慧防御者 (Wise Defender)
- **特点**: 注重防御和资源积累
- **风格**: 稳健，后发制人
- **战术**:
  - 优先建立防御
  - 合理使用资源
  - 等待最佳时机

## 💡 对战AI的建议

### 观察AI行为
- 注意AI的出牌模式
- 分析AI的攻击偏好
- 预测AI的可能行动

### 制定针对性策略
- 利用AI的决策特点
- 选择合适的反制战术
- 控制游戏节奏

### 心理战术
- 制造假象诱导AI失误
- 控制信息暴露程度
- 在关键时刻出奇制胜
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 AI系统详解",
            box=box.ROUNDED,
            border_style="cyan"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    def _show_tips_help(self):
        """显示游戏技巧帮助"""
        help_content = """
# 💡 游戏策略与技巧

## 🎯 核心策略原则

### 1. 法力管理
- **效率优先**: 确保每回合的法力都得到充分利用
- **曲线规划**: 合理安排低费和高费卡牌的比例
- **预留余地**: 为关键卡牌保留足够法力

### 2. 节奏控制
- **主动权**: 把握进攻和防守的时机
- **响应式**: 根据对手行动调整策略
- **压制力**: 在关键时刻施加压力

### 3. 资源优势
- **卡牌优势**: 保持手牌数量不低于对手
- **场面控制**: 维持战场上的主动权
- **生命管理**: 平衡进攻和自我保护

## 🃏 卡牌使用技巧

### 随从牌使用
- **时机把握**:
  - 早期：建立场面优势
  - 中期：巩固控制和交换
  - 后期：终结比赛或扭转局势

- **位置安排**:
  - 保护重要随从
  - 利用嘲讽随从
  - 考虑攻击顺序

- **特效配合**:
  - 嘲讽随从保护高价值目标
  - 圣盾随从处理威胁单位
  - 冲锋随从抢夺先手

### 法术牌使用
- **即时效果**: 把握使用时机
- **combo配合**: 与其他卡牌形成连击
- **应急用途**: 危急情况下的救命稻草

## ⚔️ 战斗技巧

### 攻击选择
- **优先级判断**:
  1. 威胁最大的敌方随从
  2. 具有危险特效的随从
  3.敌方英雄（在安全的情况下）

- **交换计算**:
  - 评估我方损失
  - 考虑长远收益
  - 避免不必要的牺牲

### 防守策略
- **嘲讽利用**: 合理布置嘲讽随从
- **圣盾保护**: 用圣盾随从挡伤害
- **潜行突袭**: 保持潜行随从的安全

## 💡 快速上手建议

1. **合理管理法力资源**
2. **观察对手的策略模式**
3. **平衡进攻和防守**
4. **利用卡牌的特殊效果**
5. **保持耐心，享受游戏！**

记住：最好的策略是能够根据具体局势灵活调整的策略！
        """

        self.console.print(Panel(
            Markdown(help_content),
            title="📖 游戏策略与技巧",
            box=box.ROUNDED,
            border_style="green"
        ))

        Prompt.ask("按回车键返回帮助菜单", default="")

    async def _handle_spell_command(self, command: str) -> Tuple[bool, str, Optional[dict]]:
        """从命令字符串处理法术命令"""
        try:
            # 解析法术命令，例如 "1. 法术: 火球术 → 石像鬼"
            if "→" not in command:
                # 简单的法术命令，需要用户选择目标
                return await self._handle_spell_target_selection(command)

            parts = command.split(" → ")
            if len(parts) != 2:
                return False, f"❌ 无法解析法术命令: {command}", None

            spell_part = parts[0].strip()
            target_part = parts[1].strip()

            # 提取法术名称 (去掉"法术: "前缀和编号)
            if "法术:" in spell_part:
                spell_name = spell_part.split("法术:")[1].strip()
            else:
                spell_name = spell_part

            # 检查是否为多目标描述
            if "个目标" in target_part:
                return await self._handle_spell_target_selection(f"法术: {spell_name}")

            # 解析攻击目标
            if "英雄" in target_part or "敌方英雄" in target_part:
                target = "英雄"
            else:
                # 尝试从目标描述中提取索引
                import re
                match = re.search(r'\((\d+)\)', target_part)
                if match:
                    target_idx = int(match.group(1))
                    target = f"随从{target_idx}"
                else:
                    target = target_part

            return await self._handle_spell_by_name_with_target(spell_name, target)

        except Exception as e:
            return False, f"❌ 法术命令处理异常: {str(e)}", None

    async def _handle_spell_by_name(self, spell_name: str) -> Tuple[bool, str, Optional[dict]]:
        """根据法术名称处理法术命令"""
        if not self.game_state or 'hand' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        # 在手牌中查找法术卡牌
        spell_card = None
        spell_index = None
        for i, card in enumerate(self.game_state["hand"]):
            if (card.get("type") == "spell" and
                card.get("attack", 0) > 0 and
                spell_name in card.get("name", "")):
                spell_card = card
                spell_index = i
                break

        if spell_card is None:
            return False, f"❌ 找不到法术卡牌: {spell_name}", None

        # 检查法力值是否足够
        player_mana = self.game_state.get("player", {}).get("mana", 0)
        card_cost = spell_card.get("cost", 0)
        if card_cost > player_mana:
            return False, f"❌ 法力值不足，需要 {card_cost} 点法力", None

        # 使用已有的出牌逻辑
        return await self._handle_play_card(spell_index)

    async def _handle_spell_by_name_with_target(self, spell_name: str, target: str) -> Tuple[bool, str, Optional[dict]]:
        """根据法术名称和目标处理法术命令"""
        if not self.game_state or 'hand' not in self.game_state:
            return False, "❌ 游戏状态未初始化", None

        # 在手牌中查找法术卡牌
        spell_card = None
        spell_index = None
        for i, card in enumerate(self.game_state["hand"]):
            if (card.get("type") == "spell" and
                card.get("attack", 0) > 0 and
                spell_name in card.get("name", "")):
                spell_card = card
                spell_index = i
                break

        if spell_card is None:
            return False, f"❌ 找不到法术卡牌: {spell_name}", None

        # 检查法力值是否足够
        player_mana = self.game_state.get("player", {}).get("mana", 0)
        card_cost = spell_card.get("cost", 0)
        if card_cost > player_mana:
            return False, f"❌ 法力值不足，需要 {card_cost} 点法力", None

        # 使用已有的出牌逻辑，并提供目标
        return await self._handle_play_card(spell_index, target)

    async def _handle_spell_target_selection(self, command: str) -> Tuple[bool, str, Optional[dict]]:
        """处理法术目标选择"""
        # 提取法术名称
        if "法术:" in command:
            spell_name = command.split("法术:")[1].strip()
        else:
            spell_name = command

        # 获取可用目标
        opponent_field = self.game_state.get('battlefield', {}).get('opponent', [])
        targets = []

        # 添加英雄目标
        targets.append(("英雄", "敌方英雄"))

        # 添加随从目标
        for i, minion in enumerate(opponent_field):
            target_name = minion.get('name', f'随从{i}')
            targets.append((f"随从{i}", target_name))

        if not targets:
            return False, "❌ 没有可用的攻击目标", None

        # 构建选择菜单
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.prompt import IntPrompt

        console = Console()
        console.print()
        console.print(Panel(
            f"[bold yellow]🎯 选择 {spell_name} 的目标[/bold yellow]",
            box=box.ROUNDED,
            border_style="yellow"
        ))

        # 创建目标选择表格
        target_table = Table(show_header=True, box=box.ROUNDED)
        target_table.add_column("选项", style="cyan", width=8)
        target_table.add_column("目标", style="white")

        for i, (target_key, target_name) in enumerate(targets):
            target_table.add_row(f"{i+1}", target_name)

        console.print(target_table)

        # 获取用户选择
        choice = IntPrompt.ask("请选择目标", choices=[str(i+1) for i in range(len(targets))])

        if 1 <= choice <= len(targets):
            selected_target = targets[choice-1][0]
            return await self._handle_spell_by_name_with_target(spell_name, selected_target)
        else:
            return False, "❌ 无效的目标选择", None


# ============================================================================
# TDD测试入口
# ============================================================================

if __name__ == "__main__":
    ui = GameUI()
    ui.show_welcome_animation()
    result = ui.show_main_menu()

    if result != "quit":
        print(f"选择的模式: {result}")