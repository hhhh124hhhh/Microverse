#!/usr/bin/env python3
"""
命令基类定义
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any


class Command(ABC):
    """命令基类"""

    def __init__(self, name: str, description: str, aliases: List[str] = None):
        self.name = name
        self.description = description
        self.aliases = aliases or []

    @abstractmethod
    async def execute(self, context: 'CommandContext') -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行命令"""
        pass

    @abstractmethod
    def can_execute(self, context: 'CommandContext') -> bool:
        """检查是否可以执行命令"""
        pass

    def matches(self, command_text: str) -> bool:
        """检查命令文本是否匹配此命令"""
        command_text = command_text.strip().lower()
        if command_text == self.name.lower():
            return True
        return any(command_text == alias.lower() for alias in self.aliases)


class CommandContext:
    """命令上下文 - 包含执行命令所需的所有信息"""

    def __init__(self, game, ui, player_idx: int, command_text: str,
                 game_state: Dict[str, Any] = None, available_commands: List[str] = None):
        self.game = game
        self.ui = ui
        self.player_idx = player_idx
        self.command_text = command_text
        self.game_state = game_state or {}
        self.available_commands = available_commands or []

    def get_current_player(self):
        """获取当前玩家"""
        return self.game.players[self.player_idx]

    def get_opponent(self):
        """获取对手"""
        return self.game.players[1 - self.player_idx]