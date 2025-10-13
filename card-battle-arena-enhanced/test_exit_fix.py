#!/usr/bin/env python3
"""
测试程序退出修复
"""

import asyncio
import sys
import signal

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

        # 取消所有未完成的异步任务
        try:
            tasks = [task for task in asyncio.all_tasks() if not task.done()]
            if tasks:
                print(f"🔄 取消 {len(tasks)} 个异步任务...")
                for task in tasks:
                    task.cancel()
                # 等待任务取消完成
                await asyncio.gather(*tasks, return_exceptions=True)
                print("✅ 异步任务取消完成")
        except Exception as e:
            print(f"⚠️ 取消异步任务时出错: {e}")

        print("✅ 资源清理完成")

    except Exception as e:
        print(f"⚠️ 资源清理过程中出现错误: {e}")


async def test_program():
    """测试程序运行"""
    print("🚀 程序启动测试...")

    # 模拟一些工作
    await asyncio.sleep(1)
    print("📝 模拟工作完成...")

    # 正常退出
    print("👋 准备正常退出...")
    await cleanup_resources()
    print("🎉 程序正常退出完成")


def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n📡 接收到信号 {signum}")
    print("👋 程序被中断，正在优雅退出...")

    # 创建新的事件循环来处理清理
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(cleanup_resources())
        print("✅ 优雅退出完成")
    except Exception as e:
        print(f"⚠️ 退出清理时出错: {e}")
    finally:
        loop.close()
        sys.exit(0)


async def main():
    """主函数"""
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        await test_program()
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