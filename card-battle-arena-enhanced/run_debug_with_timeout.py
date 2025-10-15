#!/usr/bin/env python3
"""
带超时机制运行调试脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def run_debug_script():
    """运行调试脚本并设置超时"""
    try:
        # 导入调试脚本
        import debug_ai_stuck_fixed
        
        # 设置5秒超时
        await asyncio.wait_for(debug_ai_stuck_fixed.test_ai_decision(), timeout=5.0)
    except asyncio.TimeoutError:
        print("⏰ 调试脚本执行超时（5秒）")
    except Exception as e:
        print(f"❌ 调试脚本执行出错: {e}")

if __name__ == "__main__":
    asyncio.run(run_debug_script())