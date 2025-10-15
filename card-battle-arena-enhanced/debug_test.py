#!/usr/bin/env python3
"""
调试TDD测试
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_game_layout_basic():
    """测试GameLayout基础结构"""
    print("调试: 尝试导入GameLayout...")

    try:
        from game_ui import GameLayout
        print("✅ 导入成功")

        print("调试: 尝试创建GameLayout实例...")
        layout = GameLayout()
        print("✅ 实例创建成功")

        print("调试: 检查layout结构...")
        print(f"layout类型: {type(layout.layout)}")
        print(f"layout属性: {dir(layout.layout)}")

        print("调试: 检查主要区域...")
        print(f"layout._layouts: {layout.layout._layouts if hasattr(layout.layout, '_layouts') else '无 _layouts'}")

        # 尝试访问特定区域
        try:
            upper_area = layout.layout["upper"]
            print(f"✅ upper区域: {type(upper_area)}")
        except Exception as e:
            print(f"❌ 访问upper失败: {e}")

        # 尝试访问子区域
        try:
            player_status = layout.layout["upper"]["player_status"]
            print(f"✅ player_status区域: {type(player_status)}")
        except Exception as e:
            print(f"❌ 访问player_status失败: {e}")

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

def test_player_panel():
    """测试玩家状态面板"""
    print("\n调试: 测试玩家状态面板...")

    try:
        from game_ui import create_player_status_panel

        player_data = {
            "health": 25,
            "max_health": 30,
            "mana": 4,
            "max_mana": 6,
            "hand_count": 5,
            "field_count": 2
        }

        panel = create_player_status_panel(player_data)
        print(f"✅ 面板创建成功: {type(panel)}")
        print(f"面板内容: {str(panel)[:100]}...")

        # 检查内容
        panel_str = str(panel)
        if "25/30" in panel_str:
            print("✅ 包含生命值信息")
        else:
            print(f"❌ 不包含生命值信息，实际内容: {panel_str}")

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

def test_hand_table():
    """测试手牌表格"""
    print("\n调试: 测试手牌表格...")

    try:
        from game_ui import create_hand_cards_table

        hand_cards = [
            {"name": "火球术", "cost": 4, "attack": 0, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1}
        ]
        current_mana = 6

        table = create_hand_cards_table(hand_cards, current_mana)
        print(f"✅ 表格创建成功: {type(table)}")

        # 检查内容
        table_str = str(table)
        print(f"表格内容片段: {table_str[:200]}...")

        if "火球术" in table_str:
            print("✅ 包含火球术")
        else:
            print(f"❌ 不包含火球术")

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_game_layout_basic()
    test_player_panel()
    test_hand_table()