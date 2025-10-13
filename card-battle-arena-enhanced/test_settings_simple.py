#!/usr/bin/env python3
"""
设置功能简化测试脚本
验证设置功能的基本流程
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_user_preferences():
    """测试用户偏好设置"""
    print("🧪 测试用户偏好设置...")

    try:
        from config.user_preferences import UserPreferences, DisplayMode, Theme, Language

        # 测试默认设置
        prefs = UserPreferences()
        assert prefs.animation_enabled == True
        assert prefs.sound_enabled == False
        assert prefs.language == Language.ZH_CN
        assert prefs.theme == Theme.DEFAULT
        print("✅ 默认设置测试通过")

        # 测试序列化
        prefs.animation_enabled = False
        prefs.sound_enabled = True
        prefs.language = Language.EN_US

        data = prefs.to_dict()
        assert data["animation_enabled"] == False
        assert data["sound_enabled"] == True
        assert data["language"] == "en_US"
        print("✅ 序列化测试通过")

        # 测试反序列化
        new_prefs = UserPreferences()
        new_prefs.from_dict(data)
        assert new_prefs.animation_enabled == False
        assert new_prefs.sound_enabled == True
        assert new_prefs.language == Language.EN_US
        print("✅ 反序列化测试通过")

        # 测试文件操作
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = Path(f.name)

        prefs.save_to_file(temp_file)
        assert temp_file.exists()
        print("✅ 文件保存测试通过")

        loaded_prefs = UserPreferences()
        loaded_prefs.load_from_file(temp_file)
        assert loaded_prefs.animation_enabled == False
        assert loaded_prefs.language == Language.EN_US
        print("✅ 文件加载测试通过")

        # 清理
        temp_file.unlink()

        print("✅ 用户偏好设置测试全部通过！")
        return True

    except Exception as e:
        print(f"❌ 用户偏好设置测试失败: {e}")
        return False

def test_settings_manager():
    """测试设置管理器"""
    print("\n🧪 测试设置管理器...")

    try:
        from config.user_preferences import SettingsManager, SettingsChangeEvent

        # 使用临时目录进行测试
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = SettingsManager(config_dir)

            # 测试初始设置
            assert manager.user_preferences is not None
            assert manager.game_settings is not None
            print("✅ 设置管理器初始化测试通过")

            # 测试更新设置
            old_value = manager.user_preferences.animation_enabled
            success = manager.update_setting("display", "animation_enabled", False)
            assert success == True
            assert manager.user_preferences.animation_enabled == False
            print("✅ 设置更新测试通过")

            # 测试无效设置
            success = manager.update_setting("display", "invalid_setting", True)
            assert success == False
            print("✅ 无效设置处理测试通过")

            # 测试重置
            manager.user_preferences.animation_enabled = False
            manager.reset_to_defaults()
            assert manager.user_preferences.animation_enabled == True
            print("✅ 设置重置测试通过")

            # 测试导出导入
            export_file = config_dir / "test_export.json"
            success = manager.export_settings(export_file)
            assert success == True
            assert export_file.exists()
            print("✅ 设置导出测试通过")

            # 修改设置后导入
            manager.update_setting("display", "animation_enabled", False)
            new_manager = SettingsManager(config_dir)
            success = new_manager.import_settings(export_file)
            assert success == True
            print("✅ 设置导入测试通过")

            # 测试设置验证
            manager.game_settings.ai.default_strategy = "invalid_strategy"
            is_valid = manager.validate_settings()
            assert is_valid == False
            print("✅ 设置验证测试通过")

            # 测试设置修复
            manager.fix_invalid_settings()
            assert manager.game_settings.ai.default_strategy in ["rule_based", "hybrid", "llm_enhanced"]
            print("✅ 设置修复测试通过")

        print("✅ 设置管理器测试全部通过！")
        return True

    except Exception as e:
        print(f"❌ 设置管理器测试失败: {e}")
        return False

def test_ui_integration():
    """测试UI集成"""
    print("\n🧪 测试UI集成...")

    try:
        from game_ui import GameUI

        # 创建UI实例
        ui = GameUI()
        assert ui.settings_manager is not None
        print("✅ UI设置管理器初始化测试通过")

        # 测试通过UI更新设置
        success = ui.update_setting("display", "animation_enabled", False)
        assert success == True
        assert ui.settings_manager.user_preferences.animation_enabled == False
        print("✅ UI设置更新测试通过")

        print("✅ UI集成测试全部通过！")
        return True

    except Exception as e:
        print(f"❌ UI集成测试失败: {e}")
        return False

def test_settings_display():
    """测试设置显示功能"""
    print("\n🧪 测试设置显示功能...")

    try:
        from config.user_preferences import UserPreferences, DisplayMode, Theme, Language

        prefs = UserPreferences()

        # 测试设置摘要
        summary = prefs.get_display_settings_summary()
        assert "动画" in summary
        assert "音效" in summary
        assert "语言" in summary
        assert "主题" in summary
        print("✅ 设置摘要测试通过")

        # 测试设置验证
        prefs.console_width = 120  # 有效值
        errors = prefs.validate()
        assert len(errors) == 0
        print("✅ 有效设置验证测试通过")

        prefs.console_width = 300  # 无效值
        errors = prefs.validate()
        assert len(errors) > 0
        assert "控制台宽度" in errors[0]
        print("✅ 无效设置验证测试通过")

        print("✅ 设置显示功能测试全部通过！")
        return True

    except Exception as e:
        print(f"❌ 设置显示功能测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("🚀 开始设置功能测试...\n")

    test_results = []

    # 运行各项测试
    test_results.append(test_user_preferences())
    test_results.append(test_settings_manager())
    test_results.append(test_ui_integration())
    test_results.append(test_settings_display())

    # 统计结果
    passed = sum(test_results)
    total = len(test_results)

    print(f"\n📊 测试结果统计:")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 所有设置功能测试通过！设置功能开发完成！")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)