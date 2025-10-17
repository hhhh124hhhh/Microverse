#!/usr/bin/env python3
"""
统一错误处理和反馈系统
"""

import logging
import traceback
from typing import Dict, List, Tuple, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
import sys

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """错误严重程度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """错误类别"""
    COMMAND = "command"
    GAME_STATE = "game_state"
    VALIDATION = "validation"
    SYSTEM = "system"
    NETWORK = "network"
    USER_INPUT = "user_input"
    AI_DECISION = "ai_decision"
    UI_DISPLAY = "ui_display"


@dataclass
class ErrorInfo:
    """错误信息"""
    error_id: str
    category: ErrorCategory
    severity: ErrorSeverity
    title: str
    message: str
    details: Optional[str] = None
    suggestions: List[str] = None
    exception: Optional[Exception] = None
    timestamp: Optional[float] = None
    context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.context is None:
            self.context = {}


class FeedbackManager:
    """反馈管理器 - 提供用户友好的错误信息和建议"""

    def __init__(self):
        self.error_templates = self._load_error_templates()
        self.suggestions = self._load_suggestions()

    def _load_error_templates(self) -> Dict[str, str]:
        """加载错误模板"""
        return {
            # 命令错误
            "command_not_found": "❌ 未知命令: {command}",
            "invalid_command_format": "❌ 命令格式错误: {reason}",
            "command_not_available": "⚠️ 当前无法执行命令: {command}",

            # 游戏状态错误
            "not_your_turn": "⚠️ 不是你的回合",
            "insufficient_mana": "⚠️ 法力值不足，需要 {required} 点法力",
            "invalid_card_index": "❌ 无效的卡牌索引: {index}",
            "invalid_target": "❌ 无效的目标: {target}",

            # 验证错误
            "validation_failed": "❌ 验证失败: {reason}",
            "invalid_input": "❌ 无效的输入: {input}",

            # 系统错误
            "system_error": "❌ 系统错误: {error}",
            "unexpected_error": "❌ 发生意外错误，请重试",

            # AI错误
            "ai_decision_failed": "⚠️ AI决策失败: {reason}",
            "ai_execution_failed": "⚠️ AI动作执行失败: {reason}",

            # UI错误
            "ui_display_error": "⚠️ 界面显示错误: {reason}",
        }

    def _load_suggestions(self) -> Dict[str, List[str]]:
        """加载建议"""
        return {
            "command_not_found": [
                "输入 'h' 或 'help' 查看可用命令",
                "检查命令拼写是否正确",
                "使用数字命令选择菜单项"
            ],
            "invalid_command_format": [
                "查看命令帮助了解正确格式",
                "使用简化命令格式"
            ],
            "not_your_turn": [
                "等待你的回合开始",
                "输入 'status' 查看当前回合信息"
            ],
            "insufficient_mana": [
                "等待下回合获得更多法力值",
                "选择费用更低的卡牌",
                "结束当前回合"
            ],
            "invalid_card_index": [
                "输入 'status' 查看手牌",
                "使用有效的卡牌编号",
                "检查手牌是否为空"
            ],
            "ai_decision_failed": [
                "AI正在重新思考策略",
                "AI可能需要更多时间分析局势"
            ],
            "system_error": [
                "保存游戏进度",
                "重新启动游戏",
                "如果问题持续，请联系开发者"
            ]
        }

    def format_error(self, error_info: ErrorInfo) -> str:
        """格式化错误信息"""
        template_key = self._get_template_key(error_info)
        template = self.error_templates.get(template_key, "❌ 未知错误: {error}")

        # 格式化主要错误信息
        try:
            if error_info.context:
                formatted_message = template.format(**error_info.context)
            else:
                formatted_message = template.format(error=error_info.message)
        except KeyError:
            # 如果格式化失败，使用基本格式
            formatted_message = f"❌ {error_info.title}: {error_info.message}"

        # 添加建议
        suggestions_key = template_key
        if suggestions_key in self.suggestions and self.suggestions[suggestions_key]:
            suggestions_text = "\n💡 建议:\n" + "\n".join(f"   • {s}" for s in self.suggestions[suggestions_key])
            formatted_message += suggestions_text

        # 添加详细信息（仅在调试模式或严重错误时）
        if error_info.details and (error_info.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]):
            formatted_message += f"\n📋 详细信息: {error_info.details}"

        return formatted_message

    def _get_template_key(self, error_info: ErrorInfo) -> str:
        """根据错误信息获取模板键"""
        # 简化实现：基于错误类别和消息内容
        if error_info.category == ErrorCategory.COMMAND:
            if "not found" in error_info.message.lower():
                return "command_not_found"
            elif "format" in error_info.message.lower():
                return "invalid_command_format"
            else:
                return "command_not_available"
        elif error_info.category == ErrorCategory.GAME_STATE:
            if "turn" in error_info.message.lower():
                return "not_your_turn"
            elif "mana" in error_info.message.lower():
                return "insufficient_mana"
            elif "index" in error_info.message.lower():
                return "invalid_card_index"
            elif "target" in error_info.message.lower():
                return "invalid_target"
        elif error_info.category == ErrorCategory.VALIDATION:
            return "validation_failed"
        elif error_info.category == ErrorCategory.AI_DECISION:
            return "ai_decision_failed"
        elif error_info.category == ErrorCategory.SYSTEM:
            return "system_error"

        return "unexpected_error"


class ErrorHandler:
    """统一错误处理器"""

    def __init__(self, enable_debug: bool = False):
        self.feedback_manager = FeedbackManager()
        self.enable_debug = enable_debug
        self.error_history: List[ErrorInfo] = []
        self.error_counts: Dict[str, int] = {}

    def handle_error(self,
                    exception: Exception = None,
                    category: ErrorCategory = ErrorCategory.SYSTEM,
                    severity: ErrorSeverity = ErrorSeverity.ERROR,
                    title: str = None,
                    message: str = None,
                    context: Dict[str, Any] = None,
                    suggestions: List[str] = None) -> ErrorInfo:
        """处理错误"""

        # 生成错误ID
        error_id = self._generate_error_id(category, message or str(exception))

        # 创建错误信息
        error_info = ErrorInfo(
            error_id=error_id,
            category=category,
            severity=severity,
            title=title or self._get_default_title(category),
            message=message or str(exception) if exception else "未知错误",
            exception=exception,
            context=context or {},
            suggestions=suggestions or []
        )

        # 添加详细信息（调试模式）
        if self.enable_debug and exception:
            error_info.details = f"{type(exception).__name__}: {str(exception)}\n{traceback.format_exc()}"

        # 记录错误
        self._log_error(error_info)
        self._update_error_history(error_info)

        return error_info

    def _generate_error_id(self, category: ErrorCategory, message: str) -> str:
        """生成错误ID"""
        import time
        import hashlib
        timestamp = int(time.time())
        content = f"{category.value}_{message}_{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

    def _get_default_title(self, category: ErrorCategory) -> str:
        """获取默认标题"""
        titles = {
            ErrorCategory.COMMAND: "命令错误",
            ErrorCategory.GAME_STATE: "游戏状态错误",
            ErrorCategory.VALIDATION: "验证错误",
            ErrorCategory.SYSTEM: "系统错误",
            ErrorCategory.NETWORK: "网络错误",
            ErrorCategory.USER_INPUT: "用户输入错误",
            ErrorCategory.AI_DECISION: "AI决策错误",
            ErrorCategory.UI_DISPLAY: "界面显示错误"
        }
        return titles.get(category, "未知错误")

    def _log_error(self, error_info: ErrorInfo):
        """记录错误到日志"""
        log_level = {
            ErrorSeverity.INFO: logger.info,
            ErrorSeverity.WARNING: logger.warning,
            ErrorSeverity.ERROR: logger.error,
            ErrorSeverity.CRITICAL: logger.critical
        }.get(error_info.severity, logger.error)

        log_message = f"[{error_info.error_id}] {error_info.title}: {error_info.message}"
        if error_info.context:
            log_message += f" | Context: {error_info.context}"

        log_level(log_message)

    def _update_error_history(self, error_info: ErrorInfo):
        """更新错误历史"""
        self.error_history.append(error_info)

        # 限制历史记录数量
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-500:]

        # 更新错误计数
        error_type = f"{error_info.category.value}_{error_info.title}"
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误统计摘要"""
        return {
            "total_errors": len(self.error_history),
            "error_counts": dict(self.error_counts),
            "recent_errors": self.error_history[-10:],
            "most_common_errors": sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        }

    def format_user_feedback(self, error_info: ErrorInfo) -> str:
        """为用户格式化错误反馈"""
        return self.feedback_manager.format_error(error_info)


# 全局错误处理器实例
global_error_handler = ErrorHandler()


def handle_error(exception: Exception = None, **kwargs) -> ErrorInfo:
    """全局错误处理函数"""
    return global_error_handler.handle_error(exception, **kwargs)


def format_error_feedback(error_info: ErrorInfo) -> str:
    """格式化错误反馈"""
    return global_error_handler.format_user_feedback(error_info)


def get_error_statistics() -> Dict[str, Any]:
    """获取错误统计"""
    return global_error_handler.get_error_summary()