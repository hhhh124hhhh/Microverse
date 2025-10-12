"""
游戏配置管理
支持环境变量和配置文件的加载
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class AISettings:
    """AI配置"""
    default_strategy: str = "hybrid"
    default_personality: str = "adaptive_learner"
    enable_llm: bool = True
    max_decision_time: float = 5.0

    # DeepSeek配置
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"

    # OpenAI配置（可选）
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"

    # Claude配置（可选）
    claude_api_key: Optional[str] = None
    claude_model: str = "claude-3-haiku-20240307"


@dataclass
class GameSettings:
    """游戏配置"""
    mode: str = "demo"
    difficulty: str = "normal"
    games: int = 1
    quiet: bool = False
    verbose: bool = False

    # 显示配置
    show_thinking: bool = True
    show_emotions: bool = True
    show_performance: bool = True


@dataclass
class MonitoringSettings:
    """监控配置"""
    enable_monitoring: bool = True
    log_level: str = "INFO"
    export_metrics: bool = False
    metrics_file: str = "performance_metrics.json"


@dataclass
class Settings:
    """完整配置"""
    ai: AISettings
    game: GameSettings
    monitoring: MonitoringSettings


class SettingsManager:
    """配置管理器"""

    def __init__(self):
        self._settings: Optional[Settings] = None

    def load_settings(self) -> Settings:
        """加载配置"""
        if self._settings is None:
            self._settings = Settings(
                ai=self._load_ai_settings(),
                game=self._load_game_settings(),
                monitoring=self._load_monitoring_settings()
            )
        return self._settings

    def _load_ai_settings(self) -> AISettings:
        """加载AI配置"""
        return AISettings(
            default_strategy=os.getenv("DEFAULT_AI_STRATEGY", "hybrid"),
            default_personality=os.getenv("DEFAULT_PERSONALITY", "adaptive_learner"),
            enable_llm=os.getenv("ENABLE_LLM", "true").lower() == "true",
            max_decision_time=float(os.getenv("MAX_DECISION_TIME", "5.0")),

            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY"),
            deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),

            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),

            claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
            claude_model=os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")
        )

    def _load_game_settings(self) -> GameSettings:
        """加载游戏配置"""
        return GameSettings(
            mode=os.getenv("GAME_MODE", "demo"),
            difficulty=os.getenv("GAME_DIFFICULTY", "normal"),
            games=int(os.getenv("GAME_COUNT", "1")),
            quiet=os.getenv("QUIET", "false").lower() == "true",
            verbose=os.getenv("VERBOSE", "false").lower() == "true",

            show_thinking=os.getenv("SHOW_THINKING", "true").lower() == "true",
            show_emotions=os.getenv("SHOW_EMOTIONS", "true").lower() == "true",
            show_performance=os.getenv("SHOW_PERFORMANCE", "true").lower() == "true"
        )

    def _load_monitoring_settings(self) -> MonitoringSettings:
        """加载监控配置"""
        return MonitoringSettings(
            enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            export_metrics=os.getenv("EXPORT_METRICS", "false").lower() == "true",
            metrics_file=os.getenv("METRICS_FILE", "performance_metrics.json")
        )

    def validate_settings(self, settings: Settings) -> bool:
        """验证配置有效性"""
        # 检查必需的API密钥
        if settings.ai.enable_llm and not settings.ai.deepseek_api_key:
            print("⚠️  警告: 未配置DeepSeek API密钥，LLM功能将被禁用")
            settings.ai.enable_llm = False

        # 检查策略和人格的有效性
        valid_strategies = ["rule_based", "hybrid", "llm_enhanced"]
        if settings.ai.default_strategy not in valid_strategies:
            print(f"⚠️  无效的策略: {settings.ai.default_strategy}，使用默认策略")
            settings.ai.default_strategy = "hybrid"

        valid_personalities = [
            "aggressive_berserker", "wise_defender", "strategic_mastermind",
            "combo_enthusiast", "adaptive_learner", "fun_seeker"
        ]
        if settings.ai.default_personality not in valid_personalities:
            print(f"⚠️  无效的人格: {settings.ai.default_personality}，使用默认人格")
            settings.ai.default_personality = "adaptive_learner"

        return True

    def get_env_file_path(self) -> Path:
        """获取环境文件路径"""
        return Path(__file__).parent.parent / ".env"

    def create_env_file(self):
        """创建环境变量文件"""
        env_file = self.get_env_file_path()
        if not env_file.exists():
            example_file = env_file.with_suffix(".example")
            if example_file.exists():
                import shutil
                shutil.copy(example_file, env_file)
                print(f"✅ 已创建环境变量文件: {env_file}")
                print("请编辑 .env 文件并填入你的API密钥")
            else:
                print("⚠️  找不到环境变量示例文件")


# 全局配置管理器实例
settings_manager = SettingsManager()


def get_settings() -> Settings:
    """获取配置"""
    return settings_manager.load_settings()


def setup_environment():
    """设置环境"""
    settings = get_settings()
    settings_manager.validate_settings(settings)

    # 如果没有.env文件，创建一个
    if not settings_manager.get_env_file_path().exists():
        settings_manager.create_env_file()

    return settings