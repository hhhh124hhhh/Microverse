#!/usr/bin/env python3
"""
简单测试程序退出修复
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, '.')

async def cleanup_resources():
    """清理所有资源"""
    print("🧹 开始清理资源...")
    try:
        # 清理设置管理器
        try:
            from config.user_preferences import get_settings_manager
            manager = get_settings_manager()
            if hasattr(manager, 'save_all_settings'):
                manager.save_all_settings()
                print("✅ 设置保存完成")
        except Exception as e:
            print(f"⚠️ 保存设置时出错: {e}")

        # 强制垃圾回收
        try:
            import gc
            gc.collect()
            print("✅ 垃圾回收完成")
        except Exception as e:
            print(f"⚠️ 垃圾回收时出错: {e}")

        print("✅ 资源清理完成")

    except Exception as e:
        print(f"⚠️ 资源清理过程中出现错误: {e}")


async def main():
    """主函数"""
    try:
        print("🚀 程序启动测试...")

        # 模拟一些工作
        print("📝 模拟工作...")
        await asyncio.sleep(0.5)

        print("👋 准备正常退出...")
        await cleanup_resources()
        print("🎉 程序正常退出完成")
        return 0

    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
        await cleanup_resources()
        return 0
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        await cleanup_resources()
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断 (外部)")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 程序异常退出: {e}")
        sys.exit(1)