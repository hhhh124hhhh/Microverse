#!/usr/bin/env python3
"""
带错误处理的测试脚本
"""

import sys
import traceback

def main():
    try:
        print("Hello, World!")
        sys.stdout.flush()
        
        # 测试导入
        try:
            import rich
            print("Rich imported successfully")
            sys.stdout.flush()
        except ImportError as e:
            print(f"Rich import error: {e}")
            sys.stdout.flush()
        
        # 测试基本功能
        try:
            from rich.console import Console
            console = Console()
            console.print("[green]Rich console works![/green]")
        except Exception as e:
            print(f"Rich console error: {e}")
            traceback.print_exc()
            sys.stdout.flush()
            
    except Exception as e:
        print(f"Main error: {e}")
        traceback.print_exc()
        sys.stdout.flush()

if __name__ == "__main__":
    main()