#!/usr/bin/env python3
"""
命令系统集成模块 - 将统一命令处理器集成到现有系统
"""

from typing import Tuple, Optional, Dict, Any
import logging
from command_processor import UnifiedCommandProcessor, CommandContext

logger = logging.getLogger(__name__)


class CommandIntegration:
    """命令系统集成类"""

    def __init__(self, game, ui):
        self.game = game
        self.ui = ui
        self.processor = UnifiedCommandProcessor()
        self._setup_handlers()

    def _setup_handlers(self):
        """设置命令处理器（兼容性处理）"""
        # 注册兼容性处理器
        self.processor.register_handler('attack_handler', self._handle_attack_command)
        self.processor.register_handler('spell_handler', self._handle_spell_command)
        self.processor.register_handler('play_handler', self._handle_play_command)

    async def _handle_attack_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理攻击命令（兼容性）"""
        if hasattr(self.ui, '_handle_attack_from_command'):
            return await self.ui._handle_attack_from_command(context.command_text)
        return False, "攻击处理功能未实现", None

    async def _handle_spell_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理法术命令（兼容性）"""
        if hasattr(self.ui, '_handle_spell_from_command'):
            success, message, action_data = await self.ui._handle_spell_from_command(context.command_text)
            if success and action_data:
                # 执行法术动作
                if hasattr(self.ui, '_execute_spell_action'):
                    success, result_message = await self.ui._execute_spell_action(action_data, context.game)
                    return success, result_message, action_data
            return success, message, action_data
        elif hasattr(self.ui, '_handle_spell_command'):
            return await self.ui._handle_spell_command(context.command_text)
        return False, "法术处理功能未实现", None

    async def _handle_play_command(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理出牌命令（兼容性）"""
        try:
            parts = context.command_text.split()
            if len(parts) >= 2:
                card_index = int(parts[1])
                target = None
                if len(parts) > 2:
                    target = " ".join(parts[2:])

                result = context.game.play_card(context.player_idx, card_index, target)
                if result["success"]:
                    return True, result["message"], {"action": "play_card", "result": result}
                else:
                    return False, result["message"], None
            else:
                return False, "请指定要出的卡牌索引", None
        except (ValueError, IndexError):
            return False, "无效的出牌命令格式", None

    async def process_user_input(self, user_input: str, player_idx: int,
                                game_state: Dict[str, Any] = None,
                                available_commands: list = None) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """处理用户输入的主接口"""
        try:
            # 创建命令上下文
            context = CommandContext(
                game=self.game,
                ui=self.ui,
                player_idx=player_idx,
                command_text=user_input,
                game_state=game_state,
                available_commands=available_commands or []
            )

            # 使用统一命令处理器处理
            return await self.processor.process_command(context)

        except Exception as e:
            logger.error(f"命令处理错误: {e}")
            return False, f"命令处理失败: {str(e)}", None

    def get_available_commands_for_context(self, player_idx: int) -> list:
        """获取指定玩家的可用命令"""
        # 复用现有的游戏命令获取逻辑
        original_commands = self.game.get_available_commands()

        # 如果可以，使用UI的增强命令获取
        if hasattr(self.ui, '_get_available_commands'):
            game_state = self.game.get_game_state()
            return self.ui._get_available_commands(game_state)

        return original_commands


def create_command_integration(game, ui) -> CommandIntegration:
    """创建命令集成实例的工厂函数"""
    return CommandIntegration(game, ui)