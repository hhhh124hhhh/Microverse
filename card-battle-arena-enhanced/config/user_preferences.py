"""
用户偏好设置管理
提供游戏用户界面的个性化配置
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum


class DisplayMode(Enum):
    """显示模式"""
    NORMAL = "normal"
    COMPACT = "compact"
    DETAILED = "detailed"
    MINIMAL = "minimal"


class Theme(Enum):
    """主题"""
    DEFAULT = "default"
    DARK = "dark"
    LIGHT = "light"
    COLORFUL = "colorful"
    RETRO = "retro"


class Language(Enum):
    """语言"""
    ZH_CN = "zh_CN"
    EN_US = "en_US"
    JA_JP = "ja_JP"


@dataclass
class UserPreferences:
    """用户偏好设置"""

    # 显示设置
    animation_enabled: bool = True
    sound_enabled: bool = False
    display_mode: DisplayMode = DisplayMode.NORMAL
    theme: Theme = Theme.DEFAULT
    language: Language = Language.ZH_CN

    # 游戏体验设置
    auto_save: bool = True
    show_tips: bool = True
    show_ai_thinking: bool = True
    show_performance_metrics: bool = False
    confirm_before_quit: bool = True

    # 界面设置
    console_width: int = 80
    color_scheme: str = "default"
    show_line_numbers: bool = False
    font_size: int = 12

    # 快捷键设置
    quick_actions: Dict[str, str] = field(default_factory=lambda: {
        "help": "h",
        "quit": "q",
        "end_turn": "enter",
        "play_card": "p",
        "use_skill": "s",
        "settings": "esc"
    })

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)

        # 处理枚举类型
        data["display_mode"] = self.display_mode.value
        data["theme"] = self.theme.value
        data["language"] = self.language.value

        return data

    def from_dict(self, data: Dict[str, Any]):
        """从字典恢复设置"""
        for key, value in data.items():
            if hasattr(self, key):
                # 处理枚举类型
                if key == "display_mode":
                    self.display_mode = DisplayMode(value)
                elif key == "theme":
                    self.theme = Theme(value)
                elif key == "language":
                    self.language = Language(value)
                else:
                    setattr(self, key, value)

    def save_to_file(self, file_path: Path):
        """保存到文件"""
        data = self.to_dict()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, file_path: Path):
        """从文件加载"""
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.from_dict(data)
        else:
            raise FileNotFoundError(f"设置文件不存在: {file_path}")

    def get_display_settings_summary(self) -> str:
        """获取显示设置的摘要信息"""
        return (
            f"动画: {'开启' if self.animation_enabled else '关闭'} | "
            f"音效: {'开启' if self.sound_enabled else '关闭'} | "
            f"语言: {self.language.value.upper()} | "
            f"主题: {self.theme.value}"
        )

    def validate(self) -> List[str]:
        """验证设置的有效性"""
        errors = []

        if self.console_width < 40 or self.console_width > 200:
            errors.append("控制台宽度必须在40-200之间")

        if self.font_size < 8 or self.font_size > 48:
            errors.append("字体大小必须在8-48之间")

        if not isinstance(self.quick_actions, dict):
            errors.append("快捷键设置必须是字典格式")

        return errors


class SettingsChangeEvent:
    """设置变更事件"""

    def __init__(self, category: str, key: str, old_value: Any, new_value: Any):
        self.category = category
        self.key = key
        self.old_value = old_value
        self.new_value = new_value
        self.timestamp = None  # 可以添加时间戳


class SettingsManager:
    """设置管理器 - 统一管理所有设置"""

    def __init__(self, config_dir: Optional[Path] = None):
        from .settings import get_settings

        # 配置目录
        if config_dir is None:
            self.config_dir = Path.home() / ".card_battle_arena"
        else:
            self.config_dir = config_dir

        self.config_dir.mkdir(exist_ok=True)

        # 加载各种设置
        self.user_preferences = UserPreferences()
        self.game_settings = get_settings()

        # 设置文件路径
        self.prefs_file = self.config_dir / "user_preferences.json"
        self.game_config_file = self.config_dir / "game_config.json"

        # 变更回调函数列表
        self._change_callbacks: List[Callable[[SettingsChangeEvent], None]] = []

        # 加载已保存的设置
        self.load_all_settings()

    def load_all_settings(self):
        """加载所有设置"""
        try:
            # 加载用户偏好
            if self.prefs_file.exists():
                self.user_preferences.load_from_file(self.prefs_file)
        except Exception as e:
            print(f"⚠️  加载用户偏好失败: {e}")

        # 游戏设置通过settings.py加载，这里不需要额外处理

    def save_all_settings(self):
        """保存所有设置"""
        try:
            # 保存用户偏好
            self.user_preferences.save_to_file(self.prefs_file)
        except Exception as e:
            print(f"⚠️  保存用户偏好失败: {e}")

        # 游戏设置通常通过环境变量管理，这里暂时不处理

    def update_setting(self, category: str, key: str, value: Any) -> bool:
        """更新设置"""
        old_value = None
        updated = False

        try:
            if category == "display":
                if hasattr(self.user_preferences, key):
                    old_value = getattr(self.user_preferences, key)
                    setattr(self.user_preferences, key, value)
                    updated = True

            elif category == "game":
                if hasattr(self.game_settings.game, key):
                    old_value = getattr(self.game_settings.game, key)
                    setattr(self.game_settings.game, key, value)
                    updated = True
                elif hasattr(self.game_settings.ai, key):
                    old_value = getattr(self.game_settings.ai, key)
                    setattr(self.game_settings.ai, key, value)
                    updated = True

            elif category == "quick_actions":
                if key in self.user_preferences.quick_actions:
                    old_value = self.user_preferences.quick_actions[key]
                    self.user_preferences.quick_actions[key] = value
                    updated = True

            # 如果更新成功，触发变更事件
            if updated:
                event = SettingsChangeEvent(category, key, old_value, value)
                self._notify_change(event)

            return updated

        except Exception as e:
            print(f"⚠️  更新设置失败: {e}")
            return False

    def get_setting(self, category: str, key: str) -> Any:
        """获取设置值"""
        try:
            if category == "display":
                return getattr(self.user_preferences, key)
            elif category == "game":
                if hasattr(self.game_settings.game, key):
                    return getattr(self.game_settings.game, key)
                elif hasattr(self.game_settings.ai, key):
                    return getattr(self.game_settings.ai, key)
            elif category == "quick_actions":
                return self.user_preferences.quick_actions.get(key)
        except AttributeError:
            return None

        return None

    def reset_to_defaults(self):
        """重置为默认设置"""
        # 重置用户偏好
        old_prefs = self.user_preferences
        self.user_preferences = UserPreferences()

        # 重置游戏设置
        from .settings import get_settings
        self.game_settings = get_settings()

        # 通知变更
        event = SettingsChangeEvent("system", "reset", old_prefs, self.user_preferences)
        self._notify_change(event)

    def export_settings(self, file_path: Path) -> bool:
        """导出设置到文件"""
        try:
            export_data = {
                "user_preferences": self.user_preferences.to_dict(),
                "game_settings": {
                    "default_strategy": self.game_settings.ai.default_strategy,
                    "default_personality": self.game_settings.ai.default_personality,
                    "enable_llm": self.game_settings.ai.enable_llm,
                    "max_decision_time": self.game_settings.ai.max_decision_time,
                    "show_thinking": self.game_settings.game.show_thinking,
                    "show_emotions": self.game_settings.game.show_emotions,
                    "show_performance": self.game_settings.game.show_performance
                },
                "version": "1.0",
                "export_time": str(Path.ctime(file_path) if file_path.exists() else "unknown")
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"⚠️  导出设置失败: {e}")
            return False

    def import_settings(self, file_path: Path) -> bool:
        """从文件导入设置"""
        try:
            if not file_path.exists():
                print(f"⚠️  设置文件不存在: {file_path}")
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # 导入用户偏好
            if "user_preferences" in import_data:
                self.user_preferences.from_dict(import_data["user_preferences"])

            # 导入游戏设置
            if "game_settings" in import_data:
                game_data = import_data["game_settings"]
                for key, value in game_data.items():
                    if hasattr(self.game_settings.ai, key):
                        setattr(self.game_settings.ai, key, value)
                    elif hasattr(self.game_settings.game, key):
                        setattr(self.game_settings.game, key, value)

            return True

        except Exception as e:
            print(f"⚠️  导入设置失败: {e}")
            return False

    def validate_settings(self) -> bool:
        """验证所有设置的有效性"""
        # 验证用户偏好
        pref_errors = self.user_preferences.validate()
        if pref_errors:
            print("⚠️  用户偏好设置错误:")
            for error in pref_errors:
                print(f"  - {error}")
            return False

        # 验证游戏设置
        try:
            valid_strategies = ["rule_based", "hybrid", "llm_enhanced"]
            if self.game_settings.ai.default_strategy not in valid_strategies:
                return False

            valid_personalities = [
                "aggressive_berserker", "wise_defender", "strategic_mastermind",
                "combo_enthusiast", "adaptive_learner", "fun_seeker"
            ]
            if self.game_settings.ai.default_personality not in valid_personalities:
                return False

        except Exception:
            return False

        return True

    def fix_invalid_settings(self):
        """修复无效设置"""
        # 修复用户偏好
        if not (40 <= self.user_preferences.console_width <= 200):
            self.user_preferences.console_width = 80

        if not (8 <= self.user_preferences.font_size <= 48):
            self.user_preferences.font_size = 12

        # 修复游戏设置
        valid_strategies = ["rule_based", "hybrid", "llm_enhanced"]
        if self.game_settings.ai.default_strategy not in valid_strategies:
            self.game_settings.ai.default_strategy = "hybrid"

        valid_personalities = [
            "aggressive_berserker", "wise_defender", "strategic_mastermind",
            "combo_enthusiast", "adaptive_learner", "fun_seeker"
        ]
        if self.game_settings.ai.default_personality not in valid_personalities:
            self.game_settings.ai.default_personality = "adaptive_learner"

    def register_change_callback(self, callback: Callable[[SettingsChangeEvent], None]):
        """注册设置变更回调函数"""
        self._change_callbacks.append(callback)

    def _notify_change(self, event: SettingsChangeEvent):
        """通知设置变更"""
        for callback in self._change_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"⚠️  设置变更回调执行失败: {e}")


# 全局设置管理器实例
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """获取全局设置管理器实例"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager