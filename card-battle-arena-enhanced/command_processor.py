#!/usr/bin/env python3
"""
统一命令处理器 - 提供一致的命令处理接口
"""

from typing import Dict, List, Tuple, Optional, Any, Callable
import asyncio
import logging
from commands.base import Command, CommandContext
from commands.game_commands import (
    PlayCardCommand, AttackCommand, SpellCommand, SkillCommand,
    HeroAttackCommand, EndTurnCommand, HelpCommand, StatusCommand
)

logger = logging.getLogger(__name__)


class UnifiedCommandProcessor:
    """统一命令处理器"""

    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.command_handlers: Dict[str, Callable] = {}
        self._register_default_commands()

    def _register_default_commands(self):
        """注册默认命令"""
        default_commands = [
            PlayCardCommand(),
            AttackCommand(),
            SpellCommand(),
            SkillCommand(),
            HeroAttackCommand(),
            EndTurnCommand(),
            HelpCommand(),
            StatusCommand()
        ]

        for command in default_commands:
            self.register_command(command)

    def register_command(self, command: Command):
        """注册命令"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command

    def register_handler(self, command_type: str, handler: Callable):
        """注册命令处理器（兼容性）"""
        self.command_handlers[command_type] = handler

    async def process_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理命令"""
        command_text = context.command_text.strip()

        # 首先尝试匹配注册的命令
        for command_name, command in self.commands.items():
            if command.matches(command_text):
                if command.can_execute(context):
                    try:
                        return await command.execute(context)
                    except Exception as e:
                        error_msg = f"命令执行失败: {str(e)}"
                        logger.error(error_msg)
                        return False, error_msg, None
                else:
                    return False, f"当前无法执行命令: {command.name}", None

        # 尝试解析为数字命令
        if command_text.isdigit():
            return await self._handle_numbered_command(context)

        # 尝试解析为特定格式的命令
        return await self._handle_formatted_command(context)

    async def _handle_numbered_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理数字命令"""
        try:
            input_num = int(context.command_text)
            if 1 <= input_num <= len(context.available_commands):
                selected_command = context.available_commands[input_num - 1]
                context.ui.console.print(f"🎯 执行命令: {selected_command}")

                # 创建新的命令上下文
                new_context = CommandContext(
                    context.game, context.ui, context.player_idx,
                    selected_command, context.game_state, context.available_commands
                )

                return await self.process_command(new_context)
            else:
                return False, f"无效的命令编号: {input_num}", None
        except ValueError:
            return False, f"无效的数字命令: {context.command_text}", None

    async def _handle_formatted_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理格式化命令"""
        command_text = context.command_text.lower()

        # 出牌命令
        if command_text.startswith('出牌 ') or command_text.startswith('play '):
            return await self._handle_play_command(context)

        # 攻击命令
        if (command_text.startswith('随从攻击 ') or command_text.startswith('attack ') or
            "攻击" in command_text):
            return await self._handle_attack_command(context)

        # 法术命令
        if "法术" in command_text:
            return await self._handle_spell_command(context)

        # 技能命令
        if command_text in ['英雄技能', '技能', '技', 'power']:
            return await self._handle_skill_command(context)

        # 英雄攻击命令
        if command_text in ['英雄攻击', 'hero']:
            return await self._handle_hero_attack_command(context)

        # 结束回合命令
        if command_text in ['结束回合', '结束', 'end']:
            return await self._handle_end_turn_command(context)

        # 帮助命令
        if command_text in ['帮助', '帮', 'help', 'h']:
            return await self._handle_help_command(context)

        # 状态命令
        if command_text in ['状态', 'status']:
            return await self._handle_status_command(context)

        return False, f"未知命令: {context.command_text}", None

    async def _handle_play_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理出牌命令"""
        if 'play_handler' in self.command_handlers:
            return await self.command_handlers['play_handler'](context)
        return False, "出牌命令处理器未注册", None

    async def _handle_attack_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理攻击命令"""
        if 'attack_handler' in self.command_handlers:
            return await self.command_handlers['attack_handler'](context)
        return False, "攻击命令处理器未注册", None

    async def _handle_spell_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理法术命令"""
        if 'spell_handler' in self.command_handlers:
            return await self.command_handlers['spell_handler'](context)
        return False, "法术命令处理器未注册", None

    async def _handle_skill_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理技能命令"""
        if 'skill_handler' in self.command_handlers:
            return await self.command_handlers['skill_handler'](context)
        return False, "技能命令处理器未注册", None

    async def _handle_hero_attack_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理英雄攻击命令"""
        if 'hero_attack_handler' in self.command_handlers:
            return await self.command_handlers['hero_attack_handler'](context)
        return False, "英雄攻击命令处理器未注册", None

    async def _handle_end_turn_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理结束回合命令"""
        if 'end_turn_handler' in self.command_handlers:
            return await self.command_handlers['end_turn_handler'](context)
        return False, "结束回合命令处理器未注册", None

    async def _handle_help_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理帮助命令"""
        if 'help_handler' in self.command_handlers:
            return await self.command_handlers['help_handler'](context)

        # 默认帮助
        help_text = context.game.get_context_help()
        context.ui.console.print(help_text)
        return True, "显示帮助信息", None

    async def _handle_status_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理状态命令"""
        if 'status_handler' in self.command_handlers:
            return await self.command_handlers['status_handler'](context)

        # 默认状态显示
        context.game.display_status()
        return True, "显示游戏状态", None


# 全局命令处理器实例
command_processor = UnifiedCommandProcessor()