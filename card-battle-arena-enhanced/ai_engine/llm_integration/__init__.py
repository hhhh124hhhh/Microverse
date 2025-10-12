"""
LLM集成模块
支持多种大语言模型的集成，包括OpenAI、Claude和DeepSeek
"""

from .base import LLMManager, BaseLLMClient, LLMMessage, LLMProvider
from .deepseek_client import DeepSeekClient

# 可选导入
try:
    from .openai_client import OpenAIClient
except ImportError:
    OpenAIClient = None

__all__ = [
    "LLMManager",
    "BaseLLMClient",
    "LLMMessage",
    "LLMProvider",
    "DeepSeekClient",
    "OpenAIClient"
]