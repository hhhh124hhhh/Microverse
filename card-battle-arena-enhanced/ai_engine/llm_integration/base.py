"""
大语言模型集成基础模块
支持OpenAI、Claude等多种LLM服务
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import asyncio
import time
import json
from enum import Enum


class LLMProvider(Enum):
    """LLM服务提供商"""
    OPENAI = "openai"
    CLAUDE = "claude"
    DEEPSEEK = "deepseek"
    LOCAL = "local"


@dataclass
class LLMMessage:
    """LLM消息格式"""
    role: str  # system, user, assistant
    content: str
    timestamp: float = 0.0

    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class LLMResponse:
    """LLM响应格式"""
    content: str
    model: str
    usage: Dict[str, int]  # tokens used
    response_time: float
    finish_reason: str
    provider: LLMProvider


class LLMIntegrationError(Exception):
    """LLM集成异常基类"""
    pass


class LLMQuotaExceededError(LLMIntegrationError):
    """配额超限异常"""
    pass


class LLMTimeoutError(LLMIntegrationError):
    """请求超时异常"""
    pass


class BaseLLMClient(ABC):
    """LLM客户端基础接口"""

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self.total_requests = 0
        self.total_tokens = 0
        self.total_response_time = 0.0

    @abstractmethod
    async def chat_completion(self, messages: List[LLMMessage],
                            max_tokens: int = 1000,
                            temperature: float = 0.7) -> LLMResponse:
        """
        聊天补全接口

        Args:
            messages: 消息列表
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            LLMResponse: 模型响应
        """
        pass

    @abstractmethod
    async def analyze_game_state(self, game_state: Dict[str, Any],
                               player_info: Dict[str, Any]) -> str:
        """
        分析游戏状态

        Args:
            game_state: 游戏状态
            player_info: 玩家信息

        Returns:
            str: 分析结果
        """
        pass

    async def execute_with_retry(self, messages: List[LLMMessage],
                               max_retries: int = 3,
                               **kwargs) -> LLMResponse:
        """
        带重试机制的执行

        Args:
            messages: 消息列表
            max_retries: 最大重试次数
            **kwargs: 其他参数

        Returns:
            LLMResponse: 模型响应
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                response = await self.chat_completion(messages, **kwargs)
                self._update_statistics(response)
                return response

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    wait_time = (2 ** attempt) * 1.0  # 指数退避
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise LLMIntegrationError(f"LLM请求失败，重试{max_retries}次后仍失败: {e}")

        raise last_error

    def _update_statistics(self, response: LLMResponse):
        """更新统计信息"""
        self.total_requests += 1
        self.total_tokens += sum(response.usage.values())
        self.total_response_time += response.response_time

    def get_statistics(self) -> Dict[str, Any]:
        """获取使用统计"""
        avg_response_time = (self.total_response_time / max(1, self.total_requests))
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "average_response_time": avg_response_time,
            "model": self.model,
            "provider": self.__class__.__name__
        }

    def reset_statistics(self):
        """重置统计信息"""
        self.total_requests = 0
        self.total_tokens = 0
        self.total_response_time = 0.0


class LLMManager:
    """LLM管理器，支持多个LLM客户端"""

    def __init__(self):
        self.clients: Dict[str, BaseLLMClient] = {}
        self.default_client: Optional[str] = None

    def register_client(self, name: str, client: BaseLLMClient, is_default: bool = False):
        """注册LLM客户端"""
        self.clients[name] = client
        if is_default or self.default_client is None:
            self.default_client = name

    def get_client(self, name: Optional[str] = None) -> BaseLLMClient:
        """获取LLM客户端"""
        client_name = name or self.default_client
        if client_name not in self.clients:
            raise LLMIntegrationError(f"LLM客户端 {client_name} 不存在")
        return self.clients[client_name]

    async def analyze_with_fallback(self, messages: List[LLMMessage],
                                  preferred_client: Optional[str] = None,
                                  fallback_clients: List[str] = None) -> LLMResponse:
        """
        带回退机制的分析

        Args:
            messages: 消息列表
            preferred_client: 首选客户端
            fallback_clients: 回退客户端列表

        Returns:
            LLMResponse: 模型响应
        """
        clients_to_try = []

        if preferred_client and preferred_client in self.clients:
            clients_to_try.append(preferred_client)

        if fallback_clients:
            for client_name in fallback_clients:
                if client_name in self.clients and client_name not in clients_to_try:
                    clients_to_try.append(client_name)

        # 如果没有指定客户端，使用默认客户端
        if not clients_to_try and self.default_client:
            clients_to_try.append(self.default_client)

        last_error = None
        for client_name in clients_to_try:
            try:
                client = self.clients[client_name]
                response = await client.execute_with_retry(messages)
                return response
            except Exception as e:
                last_error = e
                continue

        raise LLMIntegrationError(f"所有LLM客户端都不可用: {last_error}")

    def get_all_statistics(self) -> Dict[str, Any]:
        """获取所有客户端的统计信息"""
        return {
            name: client.get_statistics()
            for name, client in self.clients.items()
        }