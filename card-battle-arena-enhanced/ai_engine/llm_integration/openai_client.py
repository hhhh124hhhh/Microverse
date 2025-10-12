"""
OpenAI API客户端实现
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
import openai
from .base import BaseLLMClient, LLMMessage, LLMResponse, LLMIntegrationError, LLMQuotaExceededError, LLMTimeoutError


class OpenAIClient(BaseLLMClient):
    """OpenAI API客户端"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def chat_completion(self, messages: List[LLMMessage],
                            max_tokens: int = 1000,
                            temperature: float = 0.7) -> LLMResponse:
        """
        OpenAI聊天补全接口

        Args:
            messages: 消息列表
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            LLMResponse: 模型响应
        """
        try:
            start_time = time.time()

            # 转换消息格式
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # 调用OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30.0
            )

            response_time = time.time() - start_time

            # 解析响应
            content = response.choices[0].message.content
            finish_reason = response.choices[0].finish_reason
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }

            return LLMResponse(
                content=content,
                model=self.model,
                usage=usage,
                response_time=response_time,
                finish_reason=finish_reason,
                provider="openai"
            )

        except openai.RateLimitError as e:
            raise LLMQuotaExceededError(f"OpenAI API配额超限: {e}")
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"OpenAI API请求超时: {e}")
        except Exception as e:
            raise LLMIntegrationError(f"OpenAI API请求失败: {e}")

    async def analyze_game_state(self, game_state: Dict[str, Any],
                               player_info: Dict[str, Any]) -> str:
        """
        使用OpenAI分析游戏状态

        Args:
            game_state: 游戏状态
            player_info: 玩家信息

        Returns:
            str: 分析结果
        """
        # 构建分析prompt
        system_prompt = """你是一个专业的卡牌游戏AI分析师。请分析当前游戏状态，提供战略建议。

分析要求：
1. 评估当前局面优劣
2. 识别关键机会和威胁
3. 提供具体的战术建议
4. 给出置信度评分(0-1)

请以JSON格式回复，包含以下字段：
{
    "analysis": "局面分析描述",
    "advantage_score": 0.8,  // 0-1，1表示完全优势
    "key_opportunities": ["机会1", "机会2"],
    "key_threats": ["威胁1", "威胁2"],
    "recommended_actions": ["动作1", "动作2"],
    "confidence": 0.85
}"""

        user_prompt = f"""请分析以下游戏状态：

游戏状态：
{json.dumps(game_state, indent=2, ensure_ascii=False)}

玩家信息：
{json.dumps(player_info, indent=2, ensure_ascii=False)}

请提供详细分析。"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

        try:
            response = await self.execute_with_retry(messages, max_tokens=1500, temperature=0.3)
            return response.content
        except Exception as e:
            # 如果LLM分析失败，返回基础分析
            return self._generate_basic_analysis(game_state, player_info)

    def _generate_basic_analysis(self, game_state: Dict[str, Any], player_info: Dict[str, Any]) -> str:
        """生成基础分析（LLM失败时的回退方案）"""
        player_health = game_state.get("player_health", 30)
        opponent_health = game_state.get("opponent_health", 30)
        player_field = game_state.get("player_field", [])
        opponent_field = game_state.get("opponent_field", [])
        hand_size = game_state.get("hand_size", 0)

        # 简单的优势评估
        health_advantage = (player_health - opponent_health) / 30.0
        board_advantage = (len(player_field) - len(opponent_field)) / 7.0
        hand_advantage = min(hand_size / 10.0, 0.2)

        advantage_score = max(0, min(1, 0.5 + health_advantage * 0.3 + board_advantage * 0.4 + hand_advantage))

        analysis = {
            "analysis": f"血量差距: {player_health - opponent_health}, 场面随从: {len(player_field)} vs {len(opponent_field)}",
            "advantage_score": advantage_score,
            "key_opportunities": self._identify_opportunities(game_state),
            "key_threats": self._identify_threats(game_state),
            "recommended_actions": ["考虑出牌", "评估攻击机会"],
            "confidence": 0.6
        }

        return json.dumps(analysis, ensure_ascii=False)

    def _identify_opportunities(self, game_state: Dict[str, Any]) -> List[str]:
        """识别机会"""
        opportunities = []
        player_field = game_state.get("player_field", [])
        opponent_field = game_state.get("opponent_field", [])

        # 检查是否有攻击机会
        if player_field and not opponent_field:
            opportunities.append("直接攻击对手英雄")

        # 检查场面优势
        if len(player_field) > len(opponent_field):
            opportunities.append("场面数量优势")

        return opportunities

    def _identify_threats(self, game_state: Dict[str, Any]) -> List[str]:
        """识别威胁"""
        threats = []
        opponent_field = game_state.get("opponent_field", [])

        # 检查强力随从
        for minion in opponent_field:
            if minion.get("attack", 0) >= 5:
                threats.append(f"高攻击力随从: {minion.get('name', 'Unknown')}")

        return threats


# 导入json用于序列化
import json