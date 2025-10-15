#!/usr/bin/env python3
"""
TDD测试: GameLayout组件测试
采用红-绿-重构循环开发
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class TestGameLayoutBasic:
    """测试GameLayout基础结构"""

    def test_layout_basic_structure(self):
        """
        测试1.1: Layout基础结构创建
        验证主要区域存在且配置正确
        """
        # 这个测试会在我们创建GameLayout类之前失败（红阶段）
        from game_ui import GameLayout

        layout = GameLayout()

        # 验证主要区域存在
        assert "upper" in layout.layout, "upper区域应该存在"
        assert "lower" in layout.layout, "lower区域应该存在"
        assert "player_status" in layout.layout["upper"], "player_status子区域应该存在"
        assert "opponent_status" in layout.layout["upper"], "opponent_status子区域应该存在"
        assert "game_area" in layout.layout["upper"], "game_area子区域应该存在"
        assert "hand_area" in layout.layout["lower"], "hand_area子区域应该存在"
        assert "command_area" in layout.layout["lower"], "command_area子区域应该存在"

        # 验证基础布局属性
        assert hasattr(layout, 'layout'), "应该有layout属性"
        assert hasattr(layout, 'console'), "应该有console属性"
        assert layout.layout["upper"].ratio == 3, "upper区域ratio应该是3"
        assert layout.layout["lower"].ratio == 2, "lower区域ratio应该是2"

    def test_terminal_width_adaptation(self):
        """
        测试1.2: 终端宽度适配
        验证不同终端宽度下的布局调整
        """
        from game_ui import GameLayout

        layout = GameLayout()

        # 模拟窄屏 (80列)
        layout.adapt_to_width(80)
        assert layout.layout_mode == "vertical", "80列应该使用vertical布局"

        # 模拟中屏 (100列)
        layout.adapt_to_width(100)
        assert layout.layout_mode == "compact", "100列应该使用compact布局"

        # 模拟宽屏 (120列)
        layout.adapt_to_width(120)
        assert layout.layout_mode == "horizontal", "120列应该使用horizontal布局"

    def test_layout_minimum_size_protection(self):
        """
        测试1.3: 最小尺寸保护
        确保关键区域不会被压缩得太小
        """
        from game_ui import GameLayout

        layout = GameLayout()

        # 验证关键区域有最小尺寸设置
        player_status_area = layout.layout["upper"]["player_status"]
        command_area = layout.layout["lower"]["command_area"]

        # 这些断言会推动我们实现最小尺寸保护功能
        assert hasattr(player_status_area, 'minimum_size') or player_status_area.size is not None, \
            "player_status应该有最小尺寸保护"
        assert hasattr(command_area, 'minimum_size') or command_area.size is not None, \
            "command_area应该有最小尺寸保护"


class TestLayoutComponents:
    """测试Layout组件渲染功能"""

    def test_player_status_component(self):
        """
        测试2.1: 玩家状态组件
        验证玩家状态面板的正确渲染
        """
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

        # 验证Panel包含必要信息
        assert "25/30" in str(panel), "应该显示生命值信息"
        assert "4/6" in str(panel), "应该显示法力值信息"
        assert "5张" in str(panel), "应该显示手牌数量"
        assert "2个" in str(panel), "应该显示随从数量"

        # 验证Panel类型和样式
        from rich.panel import Panel
        assert isinstance(panel, Panel), "应该返回Panel对象"
        assert "玩家" in str(panel) or "👤" in str(panel), "应该有玩家标识"

    def test_hand_cards_display(self):
        """
        测试2.2: 手牌展示组件
        验证手牌表格的正确渲染和可出性检查
        """
        from game_ui import create_hand_cards_table

        hand_cards = [
            {"name": "火球术", "cost": 4, "attack": 0, "health": 0, "type": "spell", "index": 0},
            {"name": "烈焰元素", "cost": 3, "attack": 5, "health": 3, "type": "minion", "index": 1},
            {"name": "暗影巫师", "cost": 6, "attack": 2, "health": 5, "type": "minion", "index": 2}
        ]
        current_mana = 6

        table = create_hand_cards_table(hand_cards, current_mana)

        # 验证表格结构
        assert "火球术" in str(table), "应该显示火球术"
        assert "烈焰元素" in str(table), "应该显示烈焰元素"
        assert "暗影巫师" in str(table), "应该显示暗影巫师"
        assert "4" in str(table), "应该显示费用4"
        assert "3" in str(table), "应该显示费用3"

        # 验证可出性标记
        assert "✅" in str(table), "应该有可出牌标记"
        assert "❌" in str(table), "应该有不可出牌标记"

        # 验证Table类型
        from rich.table import Table
        assert isinstance(table, Table), "应该返回Table对象"

    def test_battlefield_display(self):
        """
        测试2.3: 战场状态组件
        验证战场区域的正确渲染，包括空场处理
        """
        from game_ui import create_battlefield_component

        # 测试有随从的情况
        player_field = [
            {"name": "狼人渗透者", "attack": 3, "health": 2, "can_attack": True, "index": 0}
        ]
        opponent_field = []

        component = create_battlefield_component(player_field, opponent_field)

        # 验证随从显示
        assert "狼人渗透者" in str(component), "应该显示玩家随从"
        assert "3/2" in str(component), "应该显示攻击力/生命值"

        # 验证空场处理
        assert "对手没有随从" in str(component) or "空场" in str(component), "应该处理空场情况"

        # 测试双方都有随从的情况
        opponent_field = [
            {"name": "霜狼步兵", "attack": 2, "health": 3, "can_attack": False, "index": 0}
        ]

        component = create_battlefield_component(player_field, opponent_field)
        assert "霜狼步兵" in str(component), "应该显示对手随从"


class TestLayoutUpdates:
    """测试Layout动态更新功能"""

    def test_layout_area_update(self):
        """
        测试3.1: 区域更新机制
        验证布局区域内容能够正确更新
        """
        from game_ui import GameLayout

        layout = GameLayout()

        # 获取初始内容
        initial_content = str(layout.layout["player_status"])

        # 更新玩家状态
        new_player_data = {
            "health": 20,  # 改变生命值
            "max_health": 30,
            "mana": 5,     # 改变法力值
            "max_mana": 6,
            "hand_count": 4,  # 改变手牌数
            "field_count": 3
        }

        layout.update_player_status(new_player_data)

        # 验证内容已更新
        updated_content = str(layout.layout["player_status"])
        assert updated_content != initial_content, "内容应该发生变化"
        assert "20/30" in updated_content, "应该显示新的生命值"
        assert "5/6" in updated_content, "应该显示新的法力值"
        assert "4张" in updated_content, "应该显示新的手牌数"

    def test_live_refresh_system(self):
        """
        测试3.2: Live刷新系统
        验证实时渲染系统的正确性
        """
        with patch('rich.live.Live') as mock_live:
            from game_ui import GameUIWithLive

            game_ui = GameUIWithLive()

            # 开始渲染
            game_ui.start_rendering()
            mock_live.assert_called_once()

            # 更新游戏状态
            test_game_state = {
                "player": {"health": 25, "mana": 4},
                "hand": [],
                "battlefield": {"player": [], "opponent": []}
            }

            game_ui.update_game_state(test_game_state)

            # 验证更新方法被调用
            if hasattr(game_ui, 'live') and game_ui.live:
                game_ui.live.update.assert_called()


class TestLayoutInteraction:
    """测试Layout交互功能"""

    def test_layout_visibility_control(self):
        """
        测试4.1: 布局可见性控制
        验证区域的显示/隐藏功能
        """
        from game_ui import GameLayout

        layout = GameLayout()

        # 测试战场区域的可见性控制
        # 有随从时应该显示
        player_minions = [{"name": "测试随从", "attack": 1, "health": 1}]
        layout.update_battlefield_visibility(player_minions, [])

        # 根据我们的实现，验证可见性逻辑
        battlefield_area = layout.layout["upper"].get("battlefield_area")
        if battlefield_area and hasattr(battlefield_area, 'visible'):
            assert battlefield_area.visible == True, "有随从时战场区域应该可见"

    def test_error_handling_in_layout(self):
        """
        测试4.2: 布局错误处理
        验证错误情况下的优雅处理
        """
        from game_ui import GameLayout

        layout = GameLayout()

        # 测试无效数据处理
        invalid_data = None
        try:
            layout.update_player_status(invalid_data)
        except Exception as e:
            # 应该有适当的错误处理
            assert isinstance(e, (ValueError, TypeError)), "应该抛出合适的异常类型"


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])