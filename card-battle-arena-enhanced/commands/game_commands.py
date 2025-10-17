#!/usr/bin/env python3
"""
游戏相关命令实现
"""

from typing import Dict, List, Tuple, Optional, Any
import logging

from .base import Command, CommandContext

logger = logging.getLogger(__name__)


class PlayCardCommand(Command):
    """出牌命令"""

    def __init__(self):
        super().__init__("play", "打出卡牌", ["出牌"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以出牌"""
        player = context.get_current_player()
        return len(player.hand) > 0

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行出牌命令"""
        try:
            # 解析出牌参数
            parts = context.command_text.split()
            if len(parts) < 2:
                return False, "请指定要出的卡牌索引", None

            card_index = int(parts[1])
            target = None
            if len(parts) > 2:
                target = " ".join(parts[2:])

            # 执行出牌
            result = context.game.play_card(context.player_idx, card_index, target)
            if result["success"]:
                return True, result["message"], {"action": "play_card", "result": result}
            else:
                return False, result["message"], None

        except (ValueError, IndexError):
            return False, "无效的出牌命令格式", None
        except Exception as e:
            logger.error(f"出牌命令执行错误: {e}")
            return False, f"出牌失败: {str(e)}", None


class AttackCommand(Command):
    """攻击命令"""

    def __init__(self):
        super().__init__("attack", "随从攻击", ["攻击", "随从攻击"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以攻击"""
        player = context.get_current_player()
        return len(player.field) > 0

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行攻击命令"""
        try:
            # 使用现有的攻击处理逻辑
            if hasattr(context.ui, '_handle_attack_from_command'):
                return await context.ui._handle_attack_from_command(context.command_text)
            else:
                return False, "攻击处理功能未实现", None
        except Exception as e:
            logger.error(f"攻击命令执行错误: {e}")
            return False, f"攻击失败: {str(e)}", None


class SpellCommand(Command):
    """法术命令"""

    def __init__(self):
        super().__init__("spell", "使用法术", ["法术"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以使用法术"""
        player = context.get_current_player()
        # 检查手牌中是否有法术卡
        return any(card.card_type == "spell" for card in player.hand)

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行法术命令"""
        try:
            # 使用现有的法术处理逻辑
            if hasattr(context.ui, '_handle_spell_from_command'):
                return await context.ui._handle_spell_from_command(context.command_text)
            elif hasattr(context.ui, '_handle_spell_command'):
                return await context.ui._handle_spell_command(context.command_text)
            else:
                return False, "法术处理功能未实现", None
        except Exception as e:
            logger.error(f"法术命令执行错误: {e}")
            return False, f"法术失败: {str(e)}", None


class SkillCommand(Command):
    """技能命令"""

    def __init__(self):
        super().__init__("skill", "使用英雄技能", ["技能", "英雄技能", "技", "power", "英雄技能", "技"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以使用技能"""
        player = context.get_current_player()
        return player.mana >= 2

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行技能命令"""
        try:
            result = context.game.use_hero_power(context.player_idx)
            if result["success"]:
                return True, result["message"], {"action": "hero_power", "result": result}
            else:
                return False, result["message"], None
        except Exception as e:
            logger.error(f"技能命令执行错误: {e}")
            return False, f"技能失败: {str(e)}", None


class HeroAttackCommand(Command):
    """英雄攻击命令"""

    def __init__(self):
        super().__init__("hero", "英雄攻击", ["hero_attack", "英雄攻击", "hero"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以英雄攻击"""
        # 简化：总是可以攻击（实际游戏可能需要武器）
        return True

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行英雄攻击命令"""
        try:
            result = context.game.attack_with_hero(context.player_idx)
            if result["success"]:
                return True, result["message"], {"action": "hero_attack", "result": result}
            else:
                return False, result["message"], None
        except Exception as e:
            logger.error(f"英雄攻击命令执行错误: {e}")
            return False, f"英雄攻击失败: {str(e)}", None


class EndTurnCommand(Command):
    """结束回合命令"""

    def __init__(self):
        super().__init__("end", "结束回合", ["end_turn", "结束回合", "结束", "end"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以结束回合"""
        return True  # 总是可以结束回合

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行结束回合命令"""
        try:
            result = context.game.end_turn(context.player_idx)
            if result["success"]:
                return True, result["message"], {"action": "end_turn", "result": result}
            else:
                return False, result["message"], None
        except Exception as e:
            logger.error(f"结束回合命令执行错误: {e}")
            return False, f"结束回合失败: {str(e)}", None


class HelpCommand(Command):
    """帮助命令"""

    def __init__(self):
        super().__init__("help", "显示帮助信息", ["帮助", "帮", "h"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以显示帮助"""
        return True

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行帮助命令"""
        try:
            help_text = context.game.get_context_help()
            context.ui.console.print(help_text)
            return True, "显示帮助信息", {"action": "show_help"}
        except Exception as e:
            logger.error(f"帮助命令执行错误: {e}")
            return False, f"显示帮助失败: {str(e)}", None


class StatusCommand(Command):
    """状态命令"""

    def __init__(self):
        super().__init__("status", "显示游戏状态", ["状态", "status"])

    def can_execute(self, context: CommandContext) -> bool:
        """检查是否可以显示状态"""
        return True

    async def execute(self, context: CommandContext) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """执行状态命令"""
        try:
            context.game.display_status()
            return True, "显示游戏状态", {"action": "show_status"}
        except Exception as e:
            logger.error(f"状态命令执行错误: {e}")
            return False, f"显示状态失败: {str(e)}", None