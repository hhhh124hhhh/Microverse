#!/usr/bin/env python3
"""
带日志记录的测试脚本
"""

import sys
import logging
import os

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_log_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting debug test")
    
    try:
        logger.info("Testing basic print")
        print("Hello from print!")
        sys.stdout.flush()
        
        logger.info("Testing imports")
        import rich
        logger.info("Rich imported successfully")
        
        from rich.console import Console
        console = Console()
        console.print("[green]Rich console works![/green]")
        logger.info("Rich console created successfully")
        
        logger.info("All tests completed")
        
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()