"""
设置功能的单元测试
遵循TDD方法，先定义测试用例，再实现功能
"""
import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.settings import GameSettings, AISettings, MonitoringSettings
from game_ui import UserPreferences


class TestUserPreferences:
    """用户偏好设置测试"""

    def test_default_preferences(self):
        """测试默认偏好设置"""
        prefs = UserPreferences()

        assert prefs.animation_enabled == True
        assert prefs.sound_enabled == False
        assert prefs.language == "zh_CN"
        assert prefs.theme == "default"
        assert prefs.display_mode == "normal"
        assert prefs.auto_save == True
        assert prefs.show_tips == True

    def test_preferences_serialization(self):
        """测试偏好设置序列化"""
        prefs = UserPreferences()
        prefs.animation_enabled = False
        prefs.sound_enabled = True
        prefs.language = "en_US"

        # 测试转换为字典
        data = prefs.to_dict()
        assert data["animation_enabled"] == False
        assert data["sound_enabled"] == True
        assert data["language"] == "en_US"

        # 测试从字典恢复
        new_prefs = UserPreferences()
        new_prefs.from_dict(data)
        assert new_prefs.animation_enabled == False
        assert new_prefs.sound_enabled == True
        assert new_prefs.language == "en_US"

    def test_preferences_file_operations(self, tmp_path):
        """测试偏好设置文件操作"""
        prefs = UserPreferences()
        prefs.animation_enabled = False
        prefs.language = "en_US"

        # 测试保存到文件
        config_file = tmp_path / "test_prefs.json"
        prefs.save_to_file(config_file)
        assert config_file.exists()

        # 测试从文件加载
        new_prefs = UserPreferences()
        new_prefs.load_from_file(config_file)
        assert new_prefs.animation_enabled == False
        assert new_prefs.language == "en_US"


class TestSettingsManager:
    """设置管理器测试"""

    def test_create_settings_manager(self):
        """测试创建设置管理器"""
        from game_ui import SettingsManager
        manager = SettingsManager()

        assert manager.user_preferences is not None
        assert manager.game_settings is not None
        assert manager.ai_settings is not None

    def test_update_display_settings(self):
        """测试更新显示设置"""
        from game_ui import SettingsManager
        manager = SettingsManager()

        # 测试更新动画设置
        success = manager.update_setting("display", "animation_enabled", False)
        assert success == True
        assert manager.user_preferences.animation_enabled == False

        # 测试更新无效设置
        success = manager.update_setting("display", "invalid_setting", True)
        assert success == False

    def test_update_game_settings(self):
        """测试更新游戏设置"""
        from game_ui import SettingsManager
        manager = SettingsManager()

        # 测试更新AI策略
        success = manager.update_setting("game", "default_strategy", "rule_based")
        assert success == True
        assert manager.game_settings.default_strategy == "rule_based"

        # 测试更新AI人格
        success = manager.update_setting("game", "default_personality", "aggressive_berserker")
        assert success == True
        assert manager.game_settings.default_personality == "aggressive_berserker"

    def test_reset_to_defaults(self):
        """测试重置为默认设置"""
        from game_ui import SettingsManager
        manager = SettingsManager()

        # 修改一些设置
        manager.update_setting("display", "animation_enabled", False)
        manager.update_setting("game", "default_strategy", "rule_based")

        # 重置为默认
        manager.reset_to_defaults()

        # 验证重置结果
        assert manager.user_preferences.animation_enabled == True
        assert manager.game_settings.default_strategy == "hybrid"

    def test_export_import_settings(self, tmp_path):
        """测试导出导入设置"""
        from game_ui import SettingsManager
        manager = SettingsManager()

        # 修改设置
        manager.update_setting("display", "animation_enabled", False)
        manager.update_setting("game", "default_strategy", "rule_based")

        # 导出设置
        export_file = tmp_path / "exported_settings.json"
        success = manager.export_settings(export_file)
        assert success == True
        assert export_file.exists()

        # 创建新的管理器并导入设置
        new_manager = SettingsManager()
        new_manager.update_setting("display", "animation_enabled", True)  # 改为不同值
        new_manager.update_setting("game", "default_strategy", "hybrid")

        success = new_manager.import_settings(export_file)
        assert success == True

        # 验证导入结果
        assert new_manager.user_preferences.animation_enabled == False
        assert new_manager.game_settings.default_strategy == "rule_based"

    def test_validate_settings(self):
        """测试设置验证"""
        from game_ui import SettingsManager
        manager = SettingsManager()

        # 测试有效设置
        assert manager.validate_settings() == True

        # 测试无效设置值
        manager.game_settings.default_strategy = "invalid_strategy"
        assert manager.validate_settings() == False

        # 测试修复无效设置
        manager.fix_invalid_settings()
        assert manager.game_settings.default_strategy in ["rule_based", "hybrid", "llm_enhanced"]

    def test_settings_change_notification(self):
        """测试设置变更通知"""
        from game_ui import SettingsManager, SettingsChangeEvent
        manager = SettingsManager()

        # 注册回调函数
        callback_called = False
        callback_data = None

        def test_callback(event: SettingsChangeEvent):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = event

        manager.register_change_callback(test_callback)

        # 更新设置
        manager.update_setting("display", "animation_enabled", False)

        # 验证回调被调用
        assert callback_called == True
        assert callback_data.category == "display"
        assert callback_data.key == "animation_enabled"
        assert callback_data.old_value == True
        assert callback_data.new_value == False


class TestSettingsIntegration:
    """设置系统集成测试"""

    def test_settings_ui_integration(self):
        """测试与UI系统的集成"""
        from game_ui import GameUI, SettingsManager

        # 创建UI实例
        ui = GameUI()
        assert ui.settings_manager is not None

        # 测试通过UI更新设置
        success = ui.update_setting("display", "animation_enabled", False)
        assert success == True
        assert ui.settings_manager.user_preferences.animation_enabled == False

    def test_settings_persistence(self, tmp_path):
        """测试设置持久化"""
        from game_ui import SettingsManager

        # 使用临时目录
        original_config_dir = Path.home() / ".card_battle_arena"
        with patch('pathlib.Path.home', return_value=tmp_path):
            manager = SettingsManager()

            # 更新设置
            manager.update_setting("display", "animation_enabled", False)
            manager.update_setting("game", "default_strategy", "rule_based")

            # 保存设置
            manager.save_all_settings()

            # 创建新的管理器并加载设置
            new_manager = SettingsManager()
            new_manager.load_all_settings()

            # 验证设置被正确加载
            assert new_manager.user_preferences.animation_enabled == False
            assert new_manager.game_settings.default_strategy == "rule_based"

    @patch('game_ui.Prompt.ask')
    def test_settings_menu_interaction(self, mock_prompt):
        """测试设置菜单交互"""
        from game_ui import GameUI

        # 模拟用户输入
        mock_prompt.side_effect = ["1", "2", "n", "0"]  # 动画->音效->不保存->返回

        ui = GameUI()

        # 记录初始设置
        initial_animation = ui.settings_manager.user_preferences.animation_enabled
        initial_sound = ui.settings_manager.user_preferences.sound_enabled

        # 显示设置菜单（会处理用户输入）
        ui.show_settings_interactive()

        # 验证设置被更新（由于选择了不保存，应该回滚）
        # 这取决于具体实现，可能在交互过程中临时保存，最后决定是否持久化


if __name__ == "__main__":
    pytest.main([__file__, "-v"])