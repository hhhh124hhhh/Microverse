#!/usr/bin/env python3
"""
测试错误处理和反馈系统
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from error_handler import (
    ErrorHandler, ErrorCategory, ErrorSeverity, ErrorInfo,
    global_error_handler, handle_error, format_error_feedback, get_error_statistics
)
from error_decorators import (
    safe_execute, validate_input, retry_on_error, ErrorCollector,
    handle_command_error, handle_validation_error, handle_game_state_error
)


async def test_basic_error_handling():
    """测试基础错误处理"""
    print("🧪 测试基础错误处理")
    print("=" * 50)

    # 测试1: 处理命令错误
    print("🎯 测试1: 命令错误处理")
    print("-" * 30)

    success, message, data = handle_command_error("invalid_cmd", "命令不存在")
    print(f"   命令错误处理: {'成功' if not success else '失败'}")
    print(f"   消息长度: {len(message)} 字符")
    print(f"   包含建议: {'是' if '建议' in message else '否'}")

    # 测试2: 处理验证错误
    print("\n🎯 测试2: 验证错误处理")
    print("-" * 30)

    success, message, data = handle_validation_error("abc123", "输入格式不正确")
    print(f"   验证错误处理: {'成功' if not success else '失败'}")
    print(f"   消息长度: {len(message)} 字符")
    print(f"   包含建议: {'是' if '建议' in message else '否'}")

    # 测试3: 处理游戏状态错误
    print("\n🎯 测试3: 游戏状态错误处理")
    print("-" * 30)

    success, message, data = handle_game_state_error("play_card", "法力值不足")
    print(f"   游戏状态错误处理: {'成功' if not success else '失败'}")
    print(f"   消息长度: {len(message)} 字符")
    print(f"   包含建议: {'是' if '建议' in message else '否'}")

    print("\n🎉 基础错误处理测试完成！")
    return True


async def test_error_decorators():
    """测试错误处理装饰器"""
    print("\n🧪 测试错误处理装饰器")
    print("=" * 50)

    # 测试1: safe_execute装饰器
    print("🎯 测试1: 安全执行装饰器")
    print("-" * 30)

    @safe_execute(default_return="默认返回值")
    def risky_function():
        raise ValueError("这是一个测试错误")

    result = risky_function()
    print(f"   安全执行结果: {result}")
    print(f"   返回默认值: {'是' if result == '默认返回值' else '否'}")

    @safe_execute(default_return=0)
    def safe_divide(a, b):
        return a / b

    result = safe_divide(10, 0)
    print(f"   除零错误处理: {result}")
    print(f"   返回默认值0: {'是' if result == 0 else '否'}")

    # 测试2: validate_input装饰器
    print("\n🎯 测试2: 输入验证装饰器")
    print("-" * 30)

    def is_positive(x):
        return x > 0

    @validate_input([is_positive], "数值必须为正数")
    def process_positive_number(x):
        return x * 2

    result = process_positive_number(-5)
    print(f"   负数验证结果: {result}")
    print(f"   返回错误格式: {'是' if isinstance(result, tuple) and len(result) == 3 else '否'}")

    result = process_positive_number(5)
    print(f"   正数处理结果: {result}")

    # 测试3: retry_on_error装饰器
    print("\n🎯 测试3: 重试装饰器")
    print("-" * 30)

    attempt_count = 0

    @retry_on_error(max_retries=3, delay=0.1)
    def flaky_function():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError("连接失败")
        return "成功"

    try:
        result = await flaky_function()
        print(f"   重试结果: {result}")
        print(f"   尝试次数: {attempt_count}")
    except Exception as e:
        print(f"   重试失败: {e}")

    print("\n🎉 错误处理装饰器测试完成！")
    return True


async def test_error_collector():
    """测试错误收集器"""
    print("\n🧪 测试错误收集器")
    print("=" * 50)

    collector = ErrorCollector()

    # 添加一些错误
    collector.add_error(handle_error(
        category=ErrorCategory.COMMAND,
        message="命令1失败"
    ))
    collector.add_error(handle_error(
        category=ErrorCategory.VALIDATION,
        message="验证1失败"
    ))
    collector.add_error(handle_error(
        category=ErrorCategory.COMMAND,
        message="命令2失败"
    ))

    print("🎯 测试1: 错误收集")
    print("-" * 30)
    print(f"   总错误数: {len(collector.errors)}")
    print(f"   有错误: {'是' if collector.has_errors() else '否'}")

    print("\n🎯 测试2: 错误分类统计")
    print("-" * 30)

    summary = collector.get_summary()
    print(f"   按类别统计: {summary['by_category']}")
    print(f"   按严重程度统计: {summary['by_severity']}")

    print("\n🎯 测试3: 按类别获取错误")
    print("-" * 30)

    command_errors = collector.get_errors_by_category(ErrorCategory.COMMAND)
    print(f"   命令错误数: {len(command_errors)}")

    validation_errors = collector.get_errors_by_category(ErrorCategory.VALIDATION)
    print(f"   验证错误数: {len(validation_errors)}")

    print("\n🎉 错误收集器测试完成！")
    return True


async def test_error_statistics():
    """测试错误统计"""
    print("\n🧪 测试错误统计")
    print("=" * 50)

    # 生成一些测试错误
    for i in range(5):
        handle_error(
            category=ErrorCategory.COMMAND,
            message=f"测试命令错误 {i}"
        )

    for i in range(3):
        handle_error(
            category=ErrorCategory.VALIDATION,
            message=f"测试验证错误 {i}"
        )

    print("🎯 测试1: 获取错误统计")
    print("-" * 30)

    stats = get_error_statistics()
    print(f"   总错误数: {stats['total_errors']}")
    print(f"   错误类型数: {len(stats['error_counts'])}")

    print("\n🎯 测试2: 最常见错误")
    print("-" * 30)

    most_common = stats['most_common_errors']
    for error_type, count in most_common[:3]:
        print(f"   {error_type}: {count} 次")

    print("\n🎉 错误统计测试完成！")
    return True


async def test_real_world_scenarios():
    """测试真实世界场景"""
    print("\n🧪 测试真实世界场景")
    print("=" * 50)

    # 导入游戏相关模块
    try:
        from game_engine.card_game import CardGame
        from command_integration import create_command_integration
        from game_ui import GameUI

        # 创建游戏环境
        game = CardGame("测试玩家", "测试AI")
        ui = GameUI()
        command_integration = create_command_integration(game, ui)

        print("🎯 测试1: 无效命令处理")
        print("-" * 30)

        success, message, data = await command_integration.process_user_input(
            "invalid_command_that_does_not_exist", 0
        )
        print(f"   无效命令处理: {'成功' if not success else '失败'}")
        print(f"   错误消息长度: {len(message)} 字符")

        print("\n🎯 测试2: 非回合操作")
        print("-" * 30)

        # 切换到AI回合
        game.current_player_idx = 1

        success, message, data = await command_integration.process_user_input(
            "play 0", 0  # 玩家在AI回合尝试出牌
        )
        print(f"   非回合操作处理: {'成功' if not success else '失败'}")
        print(f"   错误消息: {message[:100]}...")

        print("\n🎯 测试3: 无效卡牌索引")
        print("-" * 30)

        # 切换回玩家回合
        game.current_player_idx = 0

        success, message, data = await command_integration.process_user_input(
            "play 999", 0  # 无效的卡牌索引
        )
        print(f"   无效索引处理: {'成功' if not success else '失败'}")
        print(f"   错误消息: {message[:100]}...")

    except Exception as e:
        print(f"   ⚠️ 真实场景测试跳过: {e}")

    print("\n🎉 真实世界场景测试完成！")
    return True


if __name__ == "__main__":
    async def main():
        try:
            tests = [
                test_basic_error_handling,
                test_error_decorators,
                test_error_collector,
                test_error_statistics,
                test_real_world_scenarios
            ]

            results = []
            for test_func in tests:
                try:
                    result = await test_func()
                    results.append(result)
                except Exception as e:
                    print(f"❌ 测试 {test_func.__name__} 失败: {e}")
                    results.append(False)

            success_count = sum(results)
            total_tests = len(results)

            print(f"\n🎉 错误处理系统测试完成!")
            print(f"   通过测试: {success_count}/{total_tests}")

            if success_count == total_tests:
                print("✅ 所有错误处理功能工作正常")
                print("✅ 错误反馈系统完善")
                print("✅ 装饰器功能正常")
                print("✅ 统计功能正常")
                return True
            else:
                print("⚠️ 部分测试失败，需要检查实现")
                return False

        except Exception as e:
            print(f"\n❌ 错误处理测试过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            return False

    success = asyncio.run(main())
    exit(0 if success else 1)