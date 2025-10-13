"""
大模型增强的AI策略
结合规则AI和LLM分析，实现更智能的决策
"""
import asyncio
import json
import time
import re
from typing import Dict, List, Any, Optional
import logging

from .base import AIStrategy, AIAction, ActionType, GameContext, AIStrategyError
from .rule_based import RuleBasedStrategy
from ..llm_integration.base import LLMManager, LLMMessage


logger = logging.getLogger(__name__)


class LLMEnhancedStrategy(AIStrategy):
    """大模型增强的AI策略"""

    def __init__(self, name: str = "LLM增强AI", config: Dict[str, Any] = None):
        default_config = {
            # LLM配置
            "llm_client": "openai",
            "llm_temperature": 0.3,
            "llm_max_tokens": 1000,

            # 混合决策配置
            "llm_weight": 0.6,  # LLM决策权重
            "rule_weight": 0.4,  # 规则决策权重
            "llm_confidence_threshold": 0.5,  # LLM置信度阈值（降低到0.5，避免过度保守）

            # 性能配置
            "enable_llm_caching": True,
            "cache_ttl": 30,  # 缓存时间(秒)
            "max_analysis_time": 25.0,  # 最大分析时间（增加到25秒）

            # 回退配置
            "fallback_to_rule": True,
            "max_retries": 2
        }

        if config:
            default_config.update(config)

        super().__init__(name, default_config)

        # 初始化规则AI作为基础策略
        rule_config = config.get("rule_config", {}) if config else {}
        self.rule_strategy = RuleBasedStrategy(f"{name}_规则层", rule_config)

        # LLM管理器
        self.llm_manager: Optional[LLMManager] = None
        self.llm_cache: Dict[str, Dict[str, Any]] = {}

        # 统计信息
        self.llm_calls = 0
        self.llm_successes = 0
        self.llm_failures = 0
        self.cache_hits = 0

    def set_llm_manager(self, llm_manager: LLMManager):
        """设置LLM管理器"""
        self.llm_manager = llm_manager

    async def make_decision(self, context: GameContext) -> Optional[AIAction]:
        """
        使用LLM增强的决策过程
        结合规则AI和LLM分析
        """
        logger.info("🤖 LLM增强AI开始决策分析...")

        # 详细显示当前游戏状态
        self._log_game_state(context)

        if not self.llm_manager:
            logger.warning("⚠️ LLM管理器未设置，回退到规则AI")
            return await self.rule_strategy.execute_with_timing(context)

        try:
            # 1. 获取规则AI的决策
            logger.info("📋 步骤1: 获取规则AI决策...")
            rule_action = await self.rule_strategy.execute_with_timing(context)
            if rule_action:
                logger.info(f"✅ 规则AI决策: {rule_action.action_type.value}, "
                          f"置信度: {rule_action.confidence:.2f}, "
                          f"推理: {rule_action.reasoning}")
            else:
                logger.info("❌ 规则AI无法做出决策")

            # 2. 获取LLM分析（带超时控制）
            logger.info(f"🧠 步骤2: 进行LLM分析（超时: {self.config['max_analysis_time']}秒）...")
            llm_action = await asyncio.wait_for(
                self._get_llm_decision(context),
                timeout=self.config["max_analysis_time"]
            )
            if llm_action:
                logger.info(f"✅ LLM决策: {llm_action.action_type.value}, "
                          f"置信度: {llm_action.confidence:.2f}, "
                          f"推理: {llm_action.reasoning}")
            else:
                logger.info("❌ LLM无法做出决策")

            # 3. 混合决策
            logger.info("🔄 步骤3: 混合决策分析...")
            final_action = self._combine_decisions(rule_action, llm_action, context)

            if final_action:
                logger.info(f"🎯 最终决策: {final_action.action_type.value}, "
                          f"置信度: {final_action.confidence:.2f}, "
                          f"推理: {final_action.reasoning}")

                # 如果是出牌决策，显示详细信息
                if final_action.action_type == ActionType.PLAY_CARD and final_action.parameters:
                    card = final_action.parameters.get("card")
                    if card:
                        logger.info(f"🃏 选择卡牌: {card.get('name', 'Unknown')} "
                                  f"({card.get('cost', 0)}费) - {card.get('description', '')}")
            else:
                logger.warning("❌ 无法确定最终决策")

            return final_action

        except asyncio.TimeoutError:
            logger.warning(f"⏰ LLM分析超时（{self.config['max_analysis_time']}秒），使用规则AI决策")
            self.llm_failures += 1
            if rule_action:
                logger.info(f"🔄 回退到规则AI决策: {rule_action.action_type.value}")
            return rule_action
        except Exception as e:
            logger.error(f"💥 LLM增强AI决策失败: {e}")
            self.llm_failures += 1

            if self.config["fallback_to_rule"]:
                logger.info("🔄 回退到规则AI决策")
                return rule_action
            return None

    async def _get_llm_decision(self, context: GameContext) -> Optional[AIAction]:
        """获取LLM决策"""
        # 检查缓存
        cache_key = self._generate_cache_key(context)
        if self._is_cache_valid(cache_key):
            return self._get_cached_decision(cache_key)

        try:
            # 准备LLM分析的prompt
            llm_response = await self._analyze_with_llm(context)
            llm_action = self._parse_llm_response(llm_response, context)

            # 缓存结果
            if self.config["enable_llm_caching"]:
                self._cache_decision(cache_key, llm_action)

            self.llm_calls += 1
            if llm_action:
                self.llm_successes += 1
            else:
                self.llm_failures += 1

            return llm_action

        except Exception as e:
            logger.error(f"LLM决策失败: {e}")
            self.llm_failures += 1
            return None

    async def _analyze_with_llm(self, context: GameContext) -> str:
        """使用LLM分析游戏状态"""
        system_prompt = """你是一个专业的卡牌游戏AI分析师。请基于当前游戏状态进行深度分析并给出精确的决策建议。

分析要求：
1. **局面评估**: 分析双方优劣势，包括血量、场面、手牌质量
2. **机会识别**: 找出当前的最佳战术机会
3. **风险评估**: 识别潜在威胁和不利因素
4. **决策建议**: 提供具体的行动方案和优先级

战术优先级：
1. **出牌** (play_card): 如果有强力随从或法术
2. **攻击** (attack): 如果能做有利交换或直接伤害
3. **英雄技能** (use_hero_power): 如果能带来价值
4. **结束回合** (end_turn): 仅在无更好选择时

请严格按照以下JSON格式回复：
{
    "analysis": "详细局面分析，包括优劣势和关键机会",
    "board_score": 0.8,
    "strategic_goals": ["目标1", "目标2"],
    "recommended_actions": [
        {
            "action_type": "play_card",
            "target": "具体目标描述",
            "confidence": 0.9,
            "reasoning": "详细的战术理由",
            "priority": 1
        }
    ]
}

重要规则：
- 置信度范围：0-1，建议不低于0.3
- priority：1-5，数字越小优先级越高
- 必须提供详细且合理的推理过程
- 优先考虑场面控制和价值交换"""

        user_prompt = f"""请进行深度战术分析：

## 基础信息
- 游戏ID: {context.game_id} | 回合: {context.turn_number} | 阶段: {context.phase}
- 当前玩家: 玩家{context.current_player}

## 我方状态
- **生命值**: {context.player_health} ❤️
- **法力值**: {context.player_mana}/{context.player_mana + context.turn_number - 1} 💰
- **手牌**: {len(context.player_hand)} 张
- **场面随从**: {len(context.player_field)} 个

## 我方详细资源
**手牌详情**:
{self._format_hand_cards_for_llm(context.player_hand)}

**场面随从**:
{self._format_field_cards_for_llm(context.player_field)}

## 对手状态
- **生命值**: {context.opponent_health} 🎯
- **法力值**: {context.opponent_mana} 💰
- **场面随从**: {len(context.opponent_field)} 个

**对手场面**:
{self._format_field_cards_for_llm(context.opponent_field)}

## 分析要求
请重点考虑：
1. 当前法力值下的最优出牌选择
2. 场面交换的可行性
3. 血量压力和节奏控制
4. 手牌质量和曲线规划

请给出具体的战术建议和决策方案。"""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt)
        ]

        # 调用LLM
        response = await self.llm_manager.analyze_with_fallback(
            messages,
            preferred_client=self.config["llm_client"]
        )

        return response.content

    def _parse_llm_response(self, llm_response: str, context: GameContext) -> Optional[AIAction]:
        """解析LLM响应为AIAction"""
        try:
            logger.info("🧠 解析LLM响应...")
            logger.debug(f"LLM原始响应长度: {len(llm_response)} 字符")
            logger.debug(f"LLM原始响应前200字符: {llm_response[:200]}...")

            # 清理LLM响应，移除markdown代码块标记
            cleaned_response = self._clean_llm_response(llm_response)
            logger.debug(f"清理后响应长度: {len(cleaned_response)} 字符")
            logger.debug(f"清理后响应前200字符: {cleaned_response[:200]}...")

            # 记录游戏状态快照用于调试
            self._log_debug_context(context)

            # 尝试解析JSON响应
            response_data = json.loads(cleaned_response)
            logger.info("✅ JSON解析成功")

            # 记录LLM分析结果
            analysis = response_data.get("analysis", "无分析")
            board_score = response_data.get("board_score", 0.5)
            strategic_goals = response_data.get("strategic_goals", [])
            logger.info(f"📊 LLM分析: {analysis}")
            logger.info(f"📈 局面评分: {board_score:.2f}")
            if strategic_goals:
                logger.info(f"🎯 战略目标: {', '.join(strategic_goals)}")

            recommended_actions = response_data.get("recommended_actions", [])
            if not recommended_actions:
                logger.warning("❌ LLM没有提供推荐动作")
                return None

            logger.info(f"📝 LLM推荐了 {len(recommended_actions)} 个动作:")

            # 显示所有推荐动作
            for i, action_data in enumerate(recommended_actions):
                action_type = action_data.get("action_type", "unknown")
                confidence = action_data.get("confidence", 0.0)
                priority = action_data.get("priority", 999)
                reasoning = action_data.get("reasoning", "无推理")
                logger.info(f"   {i+1}. {action_type} (置信度: {confidence:.2f}, 优先级: {priority}) - {reasoning}")

            # 选择最佳动作：优先考虑优先级，然后是置信度
            best_action_data = None
            best_score = -1

            for action_data in recommended_actions:
                action_type = action_data.get("action_type", "end_turn")
                confidence = action_data.get("confidence", 0.5)
                priority = action_data.get("priority", 5)
                reasoning = action_data.get("reasoning", "无推理")

                # 计算综合评分：优先级权重更高
                score = (6 - priority) * 10 + confidence * 10  # 优先级1-5转换为50-10分
                logger.info(f"      评分: {score:.1f} (优先级: {priority}, 置信度: {confidence:.2f})")

                if score > best_score:
                    best_score = score
                    best_action_data = action_data

            if not best_action_data:
                logger.warning("❌ 无法选择最佳动作")
                return None

            action_type_str = best_action_data.get("action_type", "end_turn")
            action_type = self._parse_action_type(action_type_str)
            confidence = best_action_data.get("confidence", 0.5)
            reasoning = best_action_data.get("reasoning", "LLM决策建议")
            priority = best_action_data.get("priority", 5)

            logger.info(f"🎯 选择动作: {action_type_str} (评分: {best_score:.1f}, 优先级: {priority})")

            # 验证置信度阈值
            if confidence < self.config["llm_confidence_threshold"]:
                logger.warning(f"⚠️ LLM置信度 {confidence:.2f} 低于阈值 {self.config['llm_confidence_threshold']}")
                # 不直接返回None，而是记录并继续，让混合策略决定
                logger.info("🔄 混合策略将综合考虑此决策")

            parameters = {}
            if action_type == ActionType.PLAY_CARD:
                logger.info("🃏 构建出牌参数...")
                parameters["card"] = self._find_best_card_to_play(context)
            elif action_type == ActionType.ATTACK:
                logger.info("⚔️ 构建攻击参数...")
                parameters.update(self._find_best_attack(context))
            elif action_type == ActionType.USE_HERO_POWER:
                logger.info("✨ 构建英雄技能参数...")
                parameters = {}

            full_reasoning = f"LLM(P{priority}): {reasoning}"
            if strategic_goals:
                full_reasoning += f" | 目标: {', '.join(strategic_goals[:2])}"

            return AIAction(
                action_type=action_type,
                confidence=confidence,
                reasoning=full_reasoning,
                parameters=parameters
            )

        except json.JSONDecodeError as e:
            logger.error(f"💥 LLM响应JSON解析失败: {e}")
            logger.error(f"响应内容: {llm_response}")
            return None
        except Exception as e:
            logger.error(f"💥 LLM响应解析失败: {e}")
            return None

    def _combine_decisions(self, rule_action: Optional[AIAction],
                          llm_action: Optional[AIAction],
                          context: GameContext) -> Optional[AIAction]:
        """结合规则AI和LLM的决策"""
        if not rule_action and not llm_action:
            return None

        if not rule_action:
            return llm_action

        if not llm_action:
            return rule_action

        # 计算加权置信度
        rule_weight = self.config["rule_weight"]
        llm_weight = self.config["llm_weight"]

        # 根据当前局面调整权重
        board_score = self.evaluate_board_state(context)
        if abs(board_score) > 0.5:  # 局面明显优/劣势时，更依赖规则
            rule_weight *= 1.2
            llm_weight *= 0.8
        else:  # 局面均衡时，更依赖LLM
            rule_weight *= 0.8
            llm_weight *= 1.2

        # 归一化权重
        total_weight = rule_weight + llm_weight
        rule_weight /= total_weight
        llm_weight /= total_weight

        # 选择最优动作
        rule_score = rule_action.confidence * rule_weight
        llm_score = llm_action.confidence * llm_weight

        if llm_score > rule_score:
            # 合并推理信息
            combined_reasoning = f"LLM({llm_score:.2f}): {llm_action.reasoning} | 规则AI({rule_score:.2f}): {rule_action.reasoning}"
            llm_action.reasoning = combined_reasoning
            return llm_action
        else:
            combined_reasoning = f"规则AI({rule_score:.2f}): {rule_action.reasoning} | LLM({llm_score:.2f}): {llm_action.reasoning}"
            rule_action.reasoning = combined_reasoning
            return rule_action

    def evaluate_board_state(self, context: GameContext) -> float:
        """评估局面状态，委托给规则AI"""
        return self.rule_strategy.evaluate_board_state(context)

    # 辅助方法
    def _format_hand_cards(self, hand_cards: List[Dict[str, Any]]) -> str:
        """格式化手牌信息"""
        if not hand_cards:
            return "无手牌"

        result = []
        for i, card in enumerate(hand_cards):
            card_info = f"{i+1}. {card.get('name', 'Unknown')} ({card.get('cost', 0)}费)"
            if 'attack' in card:
                card_info += f" {card['attack']}/{card.get('health', 0)}"
            result.append(card_info)

        return "\n".join(result)

    def _format_hand_cards_for_llm(self, hand_cards: List[Dict[str, Any]]) -> str:
        """为LLM格式化手牌信息，包含更多细节"""
        if not hand_cards:
            return "无手牌"

        result = []
        for i, card in enumerate(hand_cards):
            cost = card.get('cost', 0)
            name = card.get('name', 'Unknown')
            card_type = card.get('type', 'minion')

            card_info = f"- **{i+1}. {name}** ({cost}费, {card_type})"

            if card_type == 'minion':
                attack = card.get('attack', 0)
                health = card.get('health', 0)
                card_info += f" [{attack}/{health}]"
            elif card_type == 'spell':
                spell_type = card.get('spell_type', '')
                if spell_type:
                    card_info += f" [{spell_type}]"

            description = card.get('description', '')
            if description:
                card_info += f" - {description}"

            result.append(card_info)

        return "\n".join(result)

    def _format_field_cards(self, field_cards: List[Dict[str, Any]]) -> str:
        """格式化场面卡牌信息"""
        if not field_cards:
            return "无随从"

        result = []
        for i, card in enumerate(field_cards):
            card_info = f"{i+1}. {card.get('name', 'Unknown')} {card.get('attack', 0)}/{card.get('health', 0)}"
            if not card.get('can_attack', True):
                card_info += " (无法攻击)"
            result.append(card_info)

        return "\n".join(result)

    def _format_field_cards_for_llm(self, field_cards: List[Dict[str, Any]]) -> str:
        """为LLM格式化场面卡牌信息，包含更多细节"""
        if not field_cards:
            return "无随从"

        result = []
        for i, card in enumerate(field_cards):
            name = card.get('name', 'Unknown')
            attack = card.get('attack', 0)
            health = card.get('health', 0)
            can_attack = card.get('can_attack', True)

            status = "可攻击" if can_attack else "无法攻击"
            card_info = f"- **{i+1}. {name}** [{attack}/{health}] ({status})"

            description = card.get('description', '')
            if description:
                card_info += f" - {description}"

            result.append(card_info)

        return "\n".join(result)

    def _clean_llm_response(self, response: str) -> str:
        """清理LLM响应，移除markdown标记和其他格式问题"""
        if not response:
            return response

        original_response = response.strip()
        cleaned = original_response

        # 移除markdown代码块标记
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]  # 移除```json
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]   # 移除```

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]  # 移除结尾的```

        cleaned = cleaned.strip()

        # 移除可能的解释性文本（在JSON之前或之后）
        # 查找第一个{和最后一个}
        first_brace = cleaned.find('{')
        last_brace = cleaned.rfind('}')

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            # 提取JSON部分
            cleaned = cleaned[first_brace:last_brace + 1]

        # 处理常见的JSON格式问题
        # 移除多余的逗号
        cleaned = cleaned.replace(',\n}', '\n}').replace(',\n]', '\n]')
        cleaned = cleaned.replace(',}', '}').replace(',]', ']')

        # 修复引号问题 - 更智能的方法
        # 不再简单地替换所有引号，而是修复常见问题
        if not self._is_valid_json(cleaned):
            # 尝试修复引号问题
            cleaned = self._fix_json_quotes(cleaned)

        return cleaned

    def _is_valid_json(self, text: str) -> bool:
        """检查文本是否为有效的JSON"""
        try:
            json.loads(text)
            return True
        except:
            return False

    def _fix_json_quotes(self, text: str) -> str:
        """尝试修复JSON中的引号问题"""
        # 移除注释
        text = re.sub(r'//.*?\n', '', text)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

        # 尝试不同的引号修复策略
        strategies = [
            # 策略1: 保持原样
            lambda x: x,
            # 策略2: 替换单引号为双引号
            lambda x: x.replace("'", '"'),
            # 策略3: 修复常见的转义问题
            lambda x: x.replace('\\"', '"').replace('\\\'', "'"),
            # 策略4: 移除所有注释和额外文本
            lambda x: re.sub(r'[^{}[\],\d:\.\- "a-zA-Z_]', '', x)
        ]

        for strategy in strategies:
            try:
                fixed = strategy(text)
                json.loads(fixed)  # 验证
                logger.info(f"✅ JSON修复成功，使用策略: {strategy.__name__ if hasattr(strategy, '__name__') else 'unknown'}")
                return fixed
            except:
                continue

        logger.warning("⚠️ 无法修复JSON格式，返回原始清理文本")
        return text

    def _log_debug_context(self, context: GameContext):
        """记录调试用的游戏上下文信息"""
        logger.debug("📋 调试游戏上下文:")
        logger.debug(f"  - 游戏ID: {context.game_id}")
        logger.debug(f"  - 回合: {context.turn_number}")
        logger.debug(f"  - 阶段: {context.phase}")
        logger.debug(f"  - 我方血量: {context.player_health}")
        logger.debug(f"  - 我方法力: {context.player_mana}/{context.player_mana + context.turn_number - 1}")
        logger.debug(f"  - 手牌数量: {len(context.player_hand)}")
        logger.debug(f"  - 场面随从: {len(context.player_field)}")
        logger.debug(f"  - 对手血量: {context.opponent_health}")
        logger.debug(f"  - 对方法力: {context.opponent_mana}")
        logger.debug(f"  - 对手随从: {len(context.opponent_field)}")

        # 详细记录手牌信息
        if context.player_hand:
            logger.debug("🃏 我方手牌详情:")
            for i, card in enumerate(context.player_hand):
                card_name = card.get('name', 'Unknown')
                card_cost = card.get('cost', 0)
                card_type = card.get('type', 'minion')
                logger.debug(f"    {i+1}. {card_name} ({card_cost}费, {card_type})")
        else:
            logger.debug("🃏 我方手牌: 无")

    def _parse_action_type(self, action_type_str: str) -> ActionType:
        """解析动作类型"""
        action_map = {
            "play_card": ActionType.PLAY_CARD,
            "attack": ActionType.ATTACK,
            "use_hero_power": ActionType.USE_HERO_POWER,
            "end_turn": ActionType.END_TURN
        }
        return action_map.get(action_type_str, ActionType.END_TURN)

    def _find_best_card_to_play(self, context: GameContext) -> Optional[Dict[str, Any]]:
        """智能评估最佳出牌"""
        playable_cards = [card for card in context.player_hand if card.get("cost", 0) <= context.player_mana]

        if not playable_cards:
            logger.info("❌ 没有可出的卡牌")
            return None

        logger.info(f"🃏 评估 {len(playable_cards)} 张可出卡牌...")

        # 为每张卡牌计算综合评分
        card_scores = []
        for card in playable_cards:
            score = self._evaluate_card_score(card, context)
            card_scores.append((card, score))
            logger.info(f"   📊 {card.get('name', 'Unknown')}: 评分 {score:.2f}")

        # 选择评分最高的卡牌
        best_card, best_score = max(card_scores, key=lambda x: x[1])
        logger.info(f"🎯 选择最佳卡牌: {best_card.get('name', 'Unknown')} (评分: {best_score:.2f})")

        return best_card

    def _evaluate_card_score(self, card: Dict[str, Any], context: GameContext) -> float:
        """计算卡牌的综合评分"""
        score = 0.0

        # 基础评分
        cost = card.get("cost", 0)
        attack = card.get("attack", 0)
        health = card.get("health", 0)
        card_type = card.get("type", "minion")

        # 费用效率评分（鼓励出高费卡牌，但不是绝对的）
        mana_efficiency = min(cost / max(1, context.player_mana), 1.0)
        score += mana_efficiency * 2.0

        if card_type == "minion":
            # 随从评分
            # 攻击力和血量价值
            score += attack * 0.3 + health * 0.3

            # 场面优势加成
            if len(context.player_field) < len(context.opponent_field):
                score += attack * 0.2  # 落后时优先出高攻击

            # 交换能力评估
            if attack > 0:
                # 计算能否有效交换对手随从
                for enemy in context.opponent_field:
                    enemy_health = enemy.get("health", 0)
                    if attack >= enemy_health and health > enemy.get("attack", 0):
                        score += 0.5  # 能做有利交换

        elif card_type == "spell":
            # 法术评分
            spell_type = card.get("spell_type", "")
            if "damage" in spell_type.lower():
                score += 1.5  # 伤害法术有价值
            elif "draw" in spell_type.lower() or "card" in spell_type.lower():
                score += 1.2  # 抽牌法术有价值
            elif "heal" in spell_type.lower():
                # 根据血量决定治疗法术价值
                if context.player_health <= 20:
                    score += 1.0
                else:
                    score += 0.3

        # 特殊效果加成
        description = card.get("description", "").lower()
        if any(keyword in description for keyword in ["charge", "rush", "windfury"]):
            score += 0.8  # 立即效果加成
        if any(keyword in description for keyword in ["taunt", "protect"]):
            score += 0.6  # 保护效果加成
        if any(keyword in description for keyword in ["battlecry", "combo"]):
            score += 0.4  # 战吼效果加成

        # 情况评分
        # 落后时偏向防守和反制
        health_diff = context.player_health - context.opponent_health
        if health_diff < -10:
            # 大幅落后，优先高价值卡牌
            score += cost * 0.3
        elif health_diff > 10:
            # 大幅领先，可以快速压制
            score += attack * 0.2

        # 法力曲线考虑
        if cost <= context.player_mana - 2:
            # 还有剩余法力，稍微奖励高费卡牌
            score += cost * 0.1

        return score

    def _find_best_attack(self, context: GameContext) -> Dict[str, Any]:
        """智能评估最佳攻击策略"""
        attackers = [card for card in context.player_field if card.get("can_attack", True)]
        if not attackers:
            logger.info("❌ 没有可攻击的随从")
            return {}

        logger.info(f"⚔️ 评估 {len(attackers)} 个可攻击随从...")

        # 评估所有可能的攻击
        attack_options = []

        # 攻击对手英雄的选项
        for attacker in attackers:
            score = self._evaluate_hero_attack_score(attacker, context)
            attack_options.append({
                "attacker": attacker,
                "target": "opponent_hero",
                "score": score,
                "target_type": "hero"
            })

        # 攻击对手随从的选项
        for enemy in context.opponent_field:
            for attacker in attackers:
                score = self._evaluate_trade_attack_score(attacker, enemy, context)
                attack_options.append({
                    "attacker": attacker,
                    "target": enemy,
                    "score": score,
                    "target_type": "minion"
                })

        # 记录评估结果
        for option in attack_options[:5]:  # 只显示前5个最佳选项
            target_name = "对手英雄" if option["target_type"] == "hero" else option["target"].get("name", "Unknown")
            logger.info(f"   ⚔️ {option['attacker'].get('name', 'Unknown')} -> {target_name}: 评分 {option['score']:.2f}")

        # 选择评分最高的攻击
        if attack_options:
            best_attack = max(attack_options, key=lambda x: x["score"])
            target_name = "对手英雄" if best_attack["target_type"] == "hero" else best_attack["target"].get("name", "Unknown")
            logger.info(f"🎯 最佳攻击: {best_attack['attacker'].get('name', 'Unknown')} -> {target_name} (评分: {best_attack['score']:.2f})")

            return {
                "attacker": best_attack["attacker"],
                "target": best_attack["target"]
            }

        return {}

    def _evaluate_hero_attack_score(self, attacker: Dict[str, Any], context: GameContext) -> float:
        """评估攻击对手英雄的评分"""
        score = 0.0
        attack = attacker.get("attack", 0)
        health = attacker.get("health", 0)

        # 基础伤害价值
        score += attack * 0.4

        # 安全性评估 - 如果没有对手随从，攻击英雄更安全
        if not context.opponent_field:
            score += attack * 0.3

        # 血量优势时更积极
        if context.player_health > context.opponent_health + 10:
            score += attack * 0.2

        # 危险时避免冒险
        if context.player_health <= 15:
            score -= health * 0.1  # 血量低时保护随从

        # 高威胁随从优先攻击
        if attack >= 5:
            score += 1.0

        return score

    def _evaluate_trade_attack_score(self, attacker: Dict[str, Any], enemy: Dict[str, Any], context: GameContext) -> float:
        """评估随从交换的评分"""
        score = 0.0
        attack = attacker.get("attack", 0)
        health = attacker.get("health", 0)
        enemy_attack = enemy.get("attack", 0)
        enemy_health = enemy.get("health", 0)

        # 有利交换评估
        if attack >= enemy_health and health > enemy_attack:
            # 能存活的情况下击杀敌人
            score += 3.0  # 基础交换价值
            score += enemy_attack * 0.5  # 消除威胁的价值
            remaining_health = health - enemy_attack
            score += remaining_health * 0.2  # 存活价值
        elif attack >= enemy_health:
            # 同归于尽
            score += 2.0  # 消除威胁的价值
            score -= attack * 0.3  # 失去攻击力的损失
        else:
            # 无法击杀，可能只是消耗
            score += attack * 0.2  # 伤害价值
            score -= health * 0.1  # 风险评估

        # 威胁等级评估
        if enemy_attack >= 5:
            score += 1.5  # 高威胁随从优先处理
        elif enemy_attack >= 3:
            score += 0.8  # 中等威胁

        # 效果随从优先
        enemy_description = enemy.get("description", "").lower()
        if any(keyword in enemy_description for keyword in ["taunt", "protect"]):
            score += 1.2  # 嘲讽随从
        if any(keyword in enemy_description for keyword in ["charge", "rush"]):
            score += 1.0  # 突袭随从

        return score

    def _generate_cache_key(self, context: GameContext) -> str:
        """生成缓存键"""
        # 基于关键游戏状态生成哈希
        key_data = f"{context.game_id}_{context.turn_number}_{len(context.player_hand)}_{len(context.player_field)}_{context.player_mana}"
        return str(hash(key_data))

    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if not self.config["enable_llm_caching"]:
            return False

        if cache_key not in self.llm_cache:
            return False

        cache_time = self.llm_cache[cache_key].get("timestamp", 0)
        return (time.time() - cache_time) < self.config["cache_ttl"]

    def _get_cached_decision(self, cache_key: str) -> Optional[AIAction]:
        """获取缓存的决策"""
        self.cache_hits += 1
        return self.llm_cache[cache_key].get("action")

    def _cache_decision(self, cache_key: str, action: Optional[AIAction]):
        """缓存决策"""
        self.llm_cache[cache_key] = {
            "action": action,
            "timestamp": time.time()
        }

    def _log_game_state(self, context: GameContext):
        """详细记录当前游戏状态"""
        logger.info("📊 当前游戏状态分析:")
        logger.info(f"   🎮 游戏ID: {context.game_id} | 回合: {context.turn_number} | 阶段: {context.phase}")
        logger.info(f"   ❤️  我方血量: {context.player_health} | 💰 法力: {context.player_mana}")
        logger.info(f"   🎯 对手血量: {context.opponent_health} | 💰 法力: {context.opponent_mana}")

        # 详细分析手牌
        if context.player_hand:
            logger.info(f"   🃏 手牌 ({len(context.player_hand)}张):")
            playable_cards = [card for card in context.player_hand if card.get("cost", 0) <= context.player_mana]
            for i, card in enumerate(context.player_hand):
                cost = card.get("cost", 0)
                can_play = "✅可出" if cost <= context.player_mana else "❌费用不足"
                card_info = f"     {i+1}. {card.get('name', 'Unknown')} ({cost}费) {can_play}"

                if "attack" in card:
                    card_info += f" [{card['attack']}/{card.get('health', 0)}]"
                if "description" in card:
                    card_info += f" - {card['description'][:50]}..."
                logger.info(card_info)

            logger.info(f"   📈 可出卡牌: {len(playable_cards)}/{len(context.player_hand)} 张")
        else:
            logger.info("   🃏 手牌: 无")

        # 分析场面
        if context.player_field:
            logger.info(f"   ⚔️  我方场面 ({len(context.player_field)}个随从):")
            for i, card in enumerate(context.player_field):
                can_attack = "🗡️可攻击" if card.get("can_attack", True) else "🛡️无法攻击"
                logger.info(f"     {i+1}. {card.get('name', 'Unknown')} [{card.get('attack', 0)}/{card.get('health', 0)}] {can_attack}")
        else:
            logger.info("   ⚔️  我方场面: 无随从")

        if context.opponent_field:
            logger.info(f"   🛡️  对手场面 ({len(context.opponent_field)}个随从):")
            for i, card in enumerate(context.opponent_field):
                logger.info(f"     {i+1}. {card.get('name', 'Unknown')} [{card.get('attack', 0)}/{card.get('health', 0)}]")
        else:
            logger.info("   🛡️  对手场面: 无随从")

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        base_stats = super().get_performance_stats()

        # 添加LLM相关统计
        llm_stats = {
            "llm_calls": self.llm_calls,
            "llm_successes": self.llm_successes,
            "llm_failures": self.llm_failures,
            "llm_success_rate": self.llm_successes / max(1, self.llm_calls),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / max(1, self.llm_calls),
            "cache_size": len(self.llm_cache)
        }

        base_stats.update(llm_stats)

        # 添加规则AI统计
        if self.rule_strategy:
            base_stats["rule_strategy_stats"] = self.rule_strategy.get_performance_stats()

        return base_stats

    def reset_statistics(self):
        """重置统计信息"""
        super().reset_statistics()
        self.llm_calls = 0
        self.llm_successes = 0
        self.llm_failures = 0
        self.cache_hits = 0
        self.llm_cache.clear()

        if self.rule_strategy:
            self.rule_strategy.reset_statistics()