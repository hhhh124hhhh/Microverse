"""
AI引擎模块
智能卡牌游戏AI系统的核心组件
"""

from .engine import AIEngine, AIEngineConfig
from .strategies.base import AIStrategy, AIAction, ActionType, GameContext
from .strategies.rule_based import RuleBasedStrategy
try:
    from .strategies.llm_enhanced import LLMEnhancedStrategy
except ImportError:
    LLMEnhancedStrategy = None
from .strategies.hybrid import HybridAIStrategy
from .agents.agent_personality import (
    PersonalityProfile, PersonalityManager, PersonalityTrait, PlayStyle,
    PERSONALITY_PROFILES
)
from .agents.ai_agent import AIAgent, AgentMemory
from .llm_integration.base import LLMManager, BaseLLMClient, LLMMessage
from .llm_integration.deepseek_client import DeepSeekClient

# 可选导入OpenAI
try:
    from .llm_integration.openai_client import OpenAIClient
except ImportError:
    OpenAIClient = None
from .monitoring import (
    PerformanceMonitor, PerformanceMetrics, SystemHealth, AlertConfig
)

__version__ = "1.0.0"
__author__ = "Card Battle Arena Enhanced Team"

__all__ = [
    # 核心引擎
    "AIEngine",
    "AIEngineConfig",

    # 策略系统
    "AIStrategy",
    "AIAction",
    "ActionType",
    "GameContext",
    "RuleBasedStrategy",
    "LLMEnhancedStrategy",
    "HybridAIStrategy",

    # 代理系统
    "AIAgent",
    "AgentMemory",
    "PersonalityProfile",
    "PersonalityManager",
    "PersonalityTrait",
    "PlayStyle",
    "PERSONALITY_PROFILES",

    # LLM集成
    "LLMManager",
    "BaseLLMClient",
    "LLMMessage",
    "OpenAIClient",

    # 监控系统
    "PerformanceMonitor",
    "PerformanceMetrics",
    "SystemHealth",
    "AlertConfig"
]