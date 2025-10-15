#!/usr/bin/env python3
"""
TDD测试简化版: GameLayout组件测试
不依赖pytest，使用简单的assert语句
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_layout_basic_structure():
    """
    测试1.1: Layout基础结构创建
    红阶段：这个测试会失败，因为GameLayout类还不存在
    """
    print("运行测试1.1: Layout基础结构创建...")

    try:
        from game_ui import GameLayout
        layout = GameLayout()

        # 验证基础布局属性
        assert hasattr(layout, 'layout'), "应该有layout属性"
        assert hasattr(layout, 'console'), "应该有console属性"
        assert hasattr(layout, 'layout_mode'), "应该有layout_mode属性"

        # 验证Layout实例创建成功
        assert layout.layout is not None, "layout应该已创建"

        # 验证layout_mode有默认值
        assert layout.layout_mode in ["horizontal", "vertical", "compact"], "layout_mode应该有有效值"

        print("✅ 测试1.1通过")
        return True

    except ImportError as e:
        print(f"❌ 测试1.1失败 - 缺少模块: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试1.1失败 - {e}")
        return False


def test_player_status_component():
    """
    测试2.1: 玩家状态组件
    """
    print("运行测试2.1: 玩家状态组件...")

    try:
        from game_ui import create_player_status_panel
        from rich.console import Console

        player_data = {
            "health": 25,
            "max_health": 30,
            "mana": 4,
            "max_mana": 6,
            "hand_count": 5,
            "field_count": 2
        }

        panel = create_player_status_panel(player_data)

        # 使用Console渲染Panel以获取文本内容
        console = Console(width=80, file=None)
        with console.capture() as capture:
            console.print(panel)

        panel_text = capture.get()

        # 验证Panel包含必要信息
        assert "25/30" in panel_text, f"应该显示生命值信息，实际内容: {panel_text}"
        assert "4/6" in panel_text, f"应该显示法力值信息，实际内容: {panel_text}"
        assert "5张" in panel_text, f"应该显示手牌数量，实际内容: {panel_text}"
        assert "2个" in panel_text, f"应该显示随从数量，实际内容: {panel_text}"

        # 验证Panel类型和样式
        from rich.panel import Panel
        assert isinstance(panel, Panel), "应该返回Panel对象"

        print("✅ 测试2.1通过")
        return True

    except ImportError as e:
        print(f"❌ 测试2.1失败 - 缺少模块: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试2.1失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hand_cards_display():
    """
    测试2.2: 手牌展示组件
    """
    print("运行测试2.2: 手牌展示组件...")

    try:
        from game_ui import create_hand_cards_table
        from rich.console import Console

        hand_cards = [
            {"name": "火球术", "cost": 4, "attack": 0, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
            {"name": "暗影巫师", "cost": 8, "attack": 2, "health": 5, "type": "minion", "index": 2}  # 改为8费，确保不可出
        ]
        current_mana = 6

        table = create_hand_cards_table(hand_cards, current_mana)

        # 使用Console渲染Table以获取文本内容
        console = Console(width=80, file=None)
        with console.capture() as capture:
            console.print(table)

        table_text = capture.get()

        # 验证表格结构
        assert "火球术" in table_text, f"应该显示火球术，实际内容: {table_text[:200]}"
        assert "烈焰元素" in table_text, f"应该显示烈焰元素，实际内容: {table_text[:200]}"
        assert "暗影巫师" in table_text, f"应该显示暗影巫师，实际内容: {table_text[:200]}"
        assert "4" in table_text, f"应该显示费用4，实际内容: {table_text[:200]}"
        assert "3" in table_text, f"应该显示费用3，实际内容: {table_text[:200]}"

        # 验证可出性标记
        assert "✅" in table_text, f"应该有可出牌标记，实际内容: {table_text[:200]}"
        assert "❌" in table_text, f"应该有不可出牌标记，实际内容: {table_text[:200]}"

        # 验证Table类型
        from rich.table import Table
        assert isinstance(table, Table), "应该返回Table对象"

        print("✅ 测试2.2通过")
        return True

    except ImportError as e:
        print(f"❌ 测试2.2失败 - 缺少模块: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试2.2失败 - {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("🧪 开始TDD测试 - 红阶段（预期失败）")
    print("=" * 50)

    tests = [
        test_layout_basic_structure,
        test_player_status_component,
        test_hand_cards_display
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == 0:
        print("🎯 红阶段成功！所有测试都失败，现在可以开始绿阶段实现")
    else:
        print("⚠️  部分测试已通过，需要检查实现进度")

    return passed == 0  # 理想情况下应该全部失败


if __name__ == "__main__":
    run_all_tests()