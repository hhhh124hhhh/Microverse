#!/usr/bin/env python3
"""
错误处理装饰器和工具函数
"""

import functools
import logging
import asyncio
from typing import Callable, Any, Optional, Union, List, Tuple
from error_handler import (
    ErrorHandler, ErrorCategory, ErrorSeverity, ErrorInfo,
    global_error_handler, handle_error, format_error_feedback
)

logger = logging.getLogger(__name__)


def safe_execute(
    default_return: Any = None,
    error_category: ErrorCategory = ErrorCategory.SYSTEM,
    error_severity: ErrorSeverity = ErrorSeverity.ERROR,
    log_errors: bool = True,
    re_raise: bool = False,
    context: dict = None
):
    """安全执行装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    error_info = handle_error(
                        exception=e,
                        category=error_category,
                        severity=error_severity,
                        title=f"函数 {func.__name__} 执行失败",
                        context={
                            "function": func.__name__,
                            "args": str(args)[:200],  # 限制长度
                            "kwargs": str(kwargs)[:200],
                            **(context or {})
                        }
                    )
                    if re_raise:
                        raise
                    return default_return
                else:
                    if re_raise:
                        raise
                    return default_return

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    error_info = handle_error(
                        exception=e,
                        category=error_category,
                        severity=error_severity,
                        title=f"函数 {func.__name__} 执行失败",
                        context={
                            "function": func.__name__,
                            "args": str(args)[:200],
                            "kwargs": str(kwargs)[:200],
                            **(context or {})
                        }
                    )
                    if re_raise:
                        raise
                    return default_return
                else:
                    if re_raise:
                        raise
                    return default_return

        # 根据函数是否是协程选择包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def validate_input(
    validators: List[Callable[[Any], bool]],
    error_message: str = "输入验证失败",
    error_category: ErrorCategory = ErrorCategory.VALIDATION
):
    """输入验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            for i, validator in enumerate(validators):
                if i < len(args):
                    if not validator(args[i]):
                        error_info = handle_error(
                            category=error_category,
                            severity=ErrorSeverity.ERROR,
                            title="输入验证失败",
                            message=error_message,
                            context={
                                "function": func.__name__,
                                "argument_index": i,
                                "argument_value": str(args[i])[:100]
                            }
                        )
                        return (False, format_error_feedback(error_info), None)
                else:
                    # 检查kwargs
                    for key, value in kwargs.items():
                        if not validator(value):
                            error_info = handle_error(
                                category=error_category,
                                severity=ErrorSeverity.ERROR,
                                title="输入验证失败",
                                message=error_message,
                                context={
                                    "function": func.__name__,
                                    "argument_key": key,
                                    "argument_value": str(value)[:100]
                                }
                            )
                            return (False, format_error_feedback(error_info), None)
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            for i, validator in enumerate(validators):
                if i < len(args):
                    if not validator(args[i]):
                        error_info = handle_error(
                            category=error_category,
                            severity=ErrorSeverity.ERROR,
                            title="输入验证失败",
                            message=error_message,
                            context={
                                "function": func.__name__,
                                "argument_index": i,
                                "argument_value": str(args[i])[:100]
                            }
                        )
                        return (False, format_error_feedback(error_info), None)
                else:
                    # 检查kwargs
                    for key, value in kwargs.items():
                        if not validator(value):
                            error_info = handle_error(
                                category=error_category,
                                severity=ErrorSeverity.ERROR,
                                title="输入验证失败",
                                message=error_message,
                                context={
                                    "function": func.__name__,
                                    "argument_key": key,
                                    "argument_value": str(value)[:100]
                                }
                            )
                            return (False, format_error_feedback(error_info), None)
            return func(*args, **kwargs)

        # 根据函数是否是协程选择包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    retry_on: tuple = (Exception,),
    error_category: ErrorCategory = ErrorCategory.SYSTEM
):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, {current_delay}秒后重试")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        error_info = handle_error(
                            exception=e,
                            category=error_category,
                            severity=ErrorSeverity.ERROR,
                            title=f"函数 {func.__name__} 重试失败",
                            context={
                                "function": func.__name__,
                                "max_retries": max_retries,
                                "attempts": attempt + 1
                            }
                        )
                        raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, {current_delay}秒后重试")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        error_info = handle_error(
                            exception=e,
                            category=error_category,
                            severity=ErrorSeverity.ERROR,
                            title=f"函数 {func.__name__} 重试失败",
                            context={
                                "function": func.__name__,
                                "max_retries": max_retries,
                                "attempts": attempt + 1
                            }
                        )
                        raise

        # 根据函数是否是协程选择包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ErrorCollector:
    """错误收集器 - 用于收集和管理多个错误"""

    def __init__(self):
        self.errors: List[ErrorInfo] = []
        self.max_errors = 100

    def add_error(self, error_info: ErrorInfo):
        """添加错误"""
        self.errors.append(error_info)
        # 限制错误数量
        if len(self.errors) > self.max_errors:
            self.errors = self.errors[-self.max_errors // 2:]

    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0

    def get_errors_by_category(self, category: ErrorCategory) -> List[ErrorInfo]:
        """按类别获取错误"""
        return [error for error in self.errors if error.category == category]

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ErrorInfo]:
        """按严重程度获取错误"""
        return [error for error in self.errors if error.severity == severity]

    def get_summary(self) -> dict:
        """获取错误摘要"""
        categories = {}
        severities = {}

        for error in self.errors:
            categories[error.category.value] = categories.get(error.category.value, 0) + 1
            severities[error.severity.value] = severities.get(error.severity.value, 0) + 1

        return {
            "total_errors": len(self.errors),
            "by_category": categories,
            "by_severity": severities,
            "recent_errors": self.errors[-5:]
        }

    def clear(self):
        """清空错误"""
        self.errors.clear()


def create_safe_result(success: bool, message: str, data: Any = None,
                      error_info: ErrorInfo = None) -> Tuple[bool, str, Any]:
    """创建安全的结果格式"""
    if success:
        return (True, message, data)
    else:
        if error_info:
            formatted_message = format_error_feedback(error_info)
            return (False, formatted_message, None)
        else:
            return (False, message, None)


# 便捷的错误处理函数
def handle_command_error(command: str, reason: str) -> Tuple[bool, str, None]:
    """处理命令错误"""
    error_info = handle_error(
        category=ErrorCategory.COMMAND,
        severity=ErrorSeverity.ERROR,
        title="命令执行错误",
        message=reason,
        context={"command": command, "reason": reason}
    )
    return create_safe_result(False, reason, None, error_info)


def handle_validation_error(input_value: str, reason: str) -> Tuple[bool, str, None]:
    """处理验证错误"""
    error_info = handle_error(
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.ERROR,
        title="输入验证错误",
        message=reason,
        context={"input": input_value, "reason": reason}
    )
    return create_safe_result(False, reason, None, error_info)


def handle_game_state_error(operation: str, reason: str) -> Tuple[bool, str, None]:
    """处理游戏状态错误"""
    error_info = handle_error(
        category=ErrorCategory.GAME_STATE,
        severity=ErrorSeverity.ERROR,
        title="游戏状态错误",
        message=reason,
        context={"operation": operation, "reason": reason}
    )
    return create_safe_result(False, reason, None, error_info)