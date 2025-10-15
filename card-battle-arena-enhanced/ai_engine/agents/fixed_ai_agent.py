"""
修复版AI代理实现
专门解决AI卡住的问题
"""
import asyncio
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

from .agent_personality import PersonalityProfile, PersonalityManager, PersonalityTrait
from ..strategies.base import AIStrategy, AIAction, ActionType, GameContext
from ..strategies.rule_based import RuleBasedStrategy
from ..strategies.llm_enhanced import LLMEnhancedStrategy
from ..strategies.hybrid import HybridAIStrategy
from ..llm_integration.base import LLMManager


logger = logging.getLogger(__name__)


@dataclass
class AgentMemory:
    """AI代理记忆系统"""
    # 对手记忆
    opponent_styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    # 卡牌效果记忆
    card_outcomes: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    # 战术记忆
    tactical_patterns: List[Dict[str, Any]] = field(default_factory=list)
    # 成功经验
    successful_moves: List[Dict[str, Any]] = field(default_factory=list)
    # 失败教训
    failed_moves: List[Dict[str, Any]] = field(default_factory=list)

    def add_opponent_impression(self, opponent_id: str, impression: Dict[str, Any]):
        """添加对对手的印象"""
        if opponent_id not in self.opponent_styles:
            self.opponent_styles[opponent_id] = {
                "aggression": 0.5,
                "skill_level": 0.5,
                "preferred_cards": [],
                "game_count": 0
            }

        # 更新印象（指数加权移动平均）
        alpha = 0.3  # 学习率
        current = self.opponent_styles[opponent_id]

        for key, value in impression.items():
            if key == "preferred_cards":
                current[key].extend(value)
                # 保持最近20张牌
                current[key] = current[key][-20:]
            elif isinstance(current.get(key), (int, float)):
                current[key] = current[key] * (1 - alpha) + value * alpha

        current["game_count"] += 1

    def get_opponent_profile(self, opponent_id: str) -> Optional[Dict[str, Any]]:
        """获取对手档案"""
        return self.opponent_styles.get(opponent_id)

    def add_card_experience(self, card_id: str, outcome: Dict[str, Any]):
        """添加卡牌使用经验"""
        if card_id not in self.card_outcomes:
            self.card_outcomes[card_id] = []

        self.card_outcomes[card_id].append(outcome)

        # 限制记忆长度
        if len(self.card_outcomes[card_id]) > 50:
            self.card_outcomes[card_id] = self.card_outcomes[card_id][-30:]

    def get_card_effectiveness(self, card_id: str) -> float:
        """获取卡牌效果评分"""
        if card_id not in self.card_outcomes:
            return 0.5  # 中性评分

        outcomes = self.card_outcomes[card_id]
        if not outcomes:
            return 0.5

        # 计算成功率
        success_rate = sum(1 for o in outcomes if o.get("successful", False)) / len(outcomes)

        # 考虑时间因素（最近的记忆权重更高）
        time_weighted_score = 0
        total_weight = 0

        for i, outcome in enumerate(outcomes):
            recency_weight = (i + 1) / len(outcomes)  # 越近的权重越高
            success = 1 if outcome.get("successful", False) else 0
            time_weighted_score += success * recency_weight
            total_weight += recency_weight

        return time_weighted_score / max(1, total_weight)


class FixedAIAgent:
    """修复版AI代理，解决卡住问题"""

    def __init__(self, agent_id: str, personality: PersonalityProfile,
                 ai_strategy: AIStrategy, llm_manager: Optional[LLMManager] = None):
        self.agent_id = agent_id
        self.personality = personality
        self.base_strategy = ai_strategy
        self.llm_manager = llm_manager

        # 记忆系统
        self.memory = AgentMemory()

        # 统计信息
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.total_decisions = 0
        self.decision_history: List[Dict[str, Any]] = []

        # 情感状态
        self.current_emotion = "neutral"  # neutral, happy, frustrated, excited
        self.emotion_intensity = 0.5

        # 学习状态
        self.is_learning = True
        self.adaptation_rate = personality.learning_rate

        # 设置LLM管理器（如果策略需要）
        if self.llm_manager and hasattr(self.base_strategy, 'set_llm_manager'):
            try:
                # 使用 getattr 安全地调用方法
                set_llm_manager_method = getattr(self.base_strategy, 'set_llm_manager')
                if callable(set_llm_manager_method):
                    set_llm_manager_method(self.llm_manager)
            except (AttributeError, Exception):
                # 如果策略没有set_llm_manager方法或调用失败，则忽略
                pass

        logger.info(f"修复版AI代理 {agent_id} ({personality.name}) 初始化完成")

    def decide_action(self, player, game_engine):
        """
        决策动作（兼容旧接口）
        修复版本，解决卡住问题
        
        Args:
            player: 当前玩家对象
            game_engine: 游戏引擎对象
            
        Returns:
            AIAction: AI决策的动作
        """
        # 创建游戏上下文
        context = self._create_context_from_game(player, game_engine)
        
        # 检查是否已经在异步事件循环中
        try:
            # 尝试获取当前事件循环
            current_loop = asyncio.get_running_loop()
            # 如果能获取到，说明已经在异步环境中
            import warnings
            warnings.warn("检测到已在异步环境中运行，使用create_task")
            # 在已有事件循环中运行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._sync_make_decision, context)
                return future.result(timeout=5.0)
        except RuntimeError:
            # 没有运行的事件循环，可以安全创建新的
            try:
                # 设置5秒超时
                result = asyncio.run(
                    asyncio.wait_for(self.make_decision(context), timeout=5.0)
                )
                return result
            except asyncio.TimeoutError:
                logger.warning("AI决策超时，使用回退策略")
                # 超时时使用规则AI作为回退
                rule_strategy = RuleBasedStrategy("回退规则AI")
                return asyncio.run(
                    asyncio.wait_for(rule_strategy.execute_with_timing(context), timeout=2.0)
                )
                
        except Exception as e:
            logger.error(f"AI决策失败: {e}")
            # 出现任何错误时，返回结束回合动作
            return AIAction(
                action_type=ActionType.END_TURN,
                confidence=0.3,
                reasoning=f"决策失败: {str(e)}",
                parameters={}
            )

    def _sync_make_decision(self, context: GameContext) -> Optional[AIAction]:
        """同步版本的决策方法，用于在线程池中运行"""
        # 创建新的事件循环来运行异步决策
        try:
            result = asyncio.run(self.make_decision(context))
            return result
        except Exception as e:
            logger.error(f"同步AI决策失败: {e}")
            return AIAction(
                action_type=ActionType.END_TURN,
                confidence=0.3,
                reasoning=f"同步决策失败: {str(e)}",
                parameters={}
            )

    async def make_decision(self, context: GameContext) -> Optional[AIAction]:
        """
        基于人格和记忆做出决策
        """
        start_time = time.time()
        self.total_decisions += 1

        try:
            # 1. 分析当前情感状态
            self._update_emotional_state(context)

            # 2. 应用人格调整
            adjusted_context = self._apply_personality_filters(context)

            # 3. 基础AI决策
            base_action = await self.base_strategy.execute_with_timing(adjusted_context)

            # 4. 应用人格修饰
            final_action = self._apply_personality_modifiers(base_action, context)

            # 5. 记录决策
            self._record_decision(context, final_action, time.time() - start_time)

            # 6. 模拟思考时间（限制在1秒内）
            await self._simulate_thinking()

            if final_action:
                logger.debug(f"代理 {self.agent_id} 决策: {final_action.action_type.value} "
                           f"({final_action.confidence:.2f}) - {self.personality.name}")

            return final_action

        except Exception as e:
            logger.error(f"代理 {self.agent_id} 决策失败: {e}")
            return self._get_emergency_action(context)

    def _update_emotional_state(self, context: GameContext):
        """更新情感状态"""
        # 使用 getattr 安全地访问属性
        danger_level = 0.0
        
        # 手动计算危险等级
        player_health = getattr(context, 'player_health', 30)
        player_max_health = getattr(context, 'player_max_health', 30) if hasattr(context, 'player_max_health') else 30
        if player_max_health > 0:
            health_ratio = player_health / player_max_health
            if health_ratio < 0.2:
                danger_level += 0.4
            elif health_ratio < 0.4:
                danger_level += 0.2

        # 基于危险程度更新情感
        if danger_level > 0.7:
            if self.personality.emotion_factor > 0.7:
                self.current_emotion = "frustrated"
                self.emotion_intensity = 0.8
            else:
                self.current_emotion = "concerned"
                self.emotion_intensity = 0.6
        elif danger_level < 0.2:
            player_health = getattr(context, 'player_health', 30)
            opponent_health = getattr(context, 'opponent_health', 30)
            if player_health > opponent_health:
                self.current_emotion = "excited"
                self.emotion_intensity = 0.7
            else:
                self.current_emotion = "neutral"
                self.emotion_intensity = 0.4
        else:
            self.current_emotion = "neutral"
            self.emotion_intensity = 0.5

    def _apply_personality_filters(self, context: GameContext) -> GameContext:
        """应用人格过滤器调整上下文"""
        # 根据人格特征调整对局势的感知
        adjusted_context = context

        # 激进人格更关注进攻机会
        if PersonalityTrait.AGGRESSIVE in self.personality.traits:
            # 这里可以调整上下文以反映激进倾向
            pass

        # 防御人格更关注威胁
        elif PersonalityTrait.DEFENSIVE in self.personality.traits:
            # 这里可以调整上下文以反映防御倾向
            pass

        return adjusted_context

    def _apply_personality_modifiers(self, action: Optional[AIAction],
                                   context: GameContext) -> Optional[AIAction]:
        """应用人格修饰调整决策"""
        if not action:
            return None

        modified_action = AIAction(
            action_type=action.action_type,
            confidence=action.confidence,
            reasoning=action.reasoning,
            parameters=action.parameters.copy()
        )

        # 根据人格调整置信度
        if self.personality.emotion_factor > 0.7:
            # 高情感因素：情感影响决策
            if self.current_emotion == "excited":
                modified_action.confidence *= 1.2
            elif self.current_emotion == "frustrated":
                modified_action.confidence *= 0.9

        # 根据激进程度调整
        if action.action_type == ActionType.ATTACK:
            aggression_bonus = (self.personality.aggression_level - 0.5) * 0.3
            modified_action.confidence = max(0, min(1, modified_action.confidence + aggression_bonus))

        # 根据风险容忍度调整
        if self.personality.risk_tolerance < 0.3:
            # 低风险容忍：降低不确定决策的置信度
            if modified_action.confidence < 0.7:
                modified_action.confidence *= 0.8

        # 确保置信度在合理范围内
        modified_action.confidence = max(0.1, min(1.0, modified_action.confidence))

        # 添加人格化推理
        personality_reasoning = self._generate_personality_reasoning(action, context)
        modified_action.reasoning = f"{personality_reasoning} | {action.reasoning}"

        return modified_action

    def _generate_personality_reasoning(self, action: AIAction, context: GameContext) -> str:
        """生成人格化推理"""
        if self.personality.name == "狂战士":
            if action.action_type == ActionType.ATTACK:
                return "狂战士本能：进攻是最好的防御！"
            elif action.action_type == ActionType.PLAY_CARD:
                return "狂战策略：压制造胜！"

        elif self.personality.name == "智慧守护者":
            if action.action_type == ActionType.ATTACK:
                return "谨慎评估：计算最佳交换"
            elif action.action_type == ActionType.END_TURN:
                return "耐心等待：寻找更好的时机"

        elif self.personality.name == "战略大师":
            return "战略思考：长远规划"

        elif self.personality.name == "连锁爱好者":
            return "寻找配合：创造连锁机会"

        return "战术决策"

    async def _simulate_thinking(self):
        """模拟思考时间（限制在1秒内）"""
        min_time, max_time = self.personality.thinking_time_range

        # 限制最大思考时间为1秒，防止卡住
        max_time = min(max_time, 1.0)

        # 根据当前情感状态调整思考时间
        if self.current_emotion == "excited":
            thinking_time = random.uniform(min_time, (min_time + max_time) / 2)
        elif self.current_emotion == "frustrated":
            thinking_time = random.uniform((min_time + max_time) / 2, max_time)
        else:
            thinking_time = random.uniform(min_time, max_time)

        await asyncio.sleep(thinking_time)

    def _record_decision(self, context: GameContext, action: Optional[AIAction],
                        execution_time: float):
        """记录决策历史"""
        record = {
            "timestamp": time.time(),
            "game_id": context.game_id,
            "turn": context.turn_number,
            "action": action.action_type.value if action else None,
            "confidence": action.confidence if action else None,
            "reasoning": action.reasoning if action else None,
            "execution_time": execution_time,
            "emotion": self.current_emotion,
            "personality": self.personality.name
        }

        self.decision_history.append(record)

        # 限制历史记录长度
        if len(self.decision_history) > 1000:
            self.decision_history = self.decision_history[-500:]

    def _get_emergency_action(self, context: GameContext) -> AIAction:
        """紧急情况下的默认动作"""
        return AIAction(
            action_type=ActionType.END_TURN,
            confidence=0.3,
            reasoning="紧急情况下的安全决策",
            parameters={}
        )

    def _create_context_from_game(self, player, game_engine):
        """
        从游戏对象创建上下文
        
        Args:
            player: 当前玩家对象
            game_engine: 游戏引擎对象
            
        Returns:
            GameContext: 游戏上下文
        """
        from ..strategies.base import GameContext
        
        # 获取对手信息
        opponent_idx = 1 - game_engine.current_player_idx
        opponent = game_engine.players[opponent_idx]
        
        # 转换手牌为字典格式
        player_hand = []
        for card in player.hand:
            player_hand.append({
                "name": getattr(card, 'name', 'Unknown'),
                "cost": getattr(card, 'cost', 0),
                "attack": getattr(card, 'attack', 0),
                "health": getattr(card, 'health', 0),
                "card_type": getattr(card, 'card_type', 'minion'),
                "mechanics": getattr(card, 'mechanics', [])
            })
        
        # 转换场上随从为字典格式
        player_field = []
        for card in player.field:  # 修复：使用 field 而不是 battlefield
            player_field.append({
                "name": getattr(card, 'name', 'Unknown'),
                "cost": getattr(card, 'cost', 0),
                "attack": getattr(card, 'attack', 0),
                "health": getattr(card, 'health', 0),
                "card_type": getattr(card, 'card_type', 'minion'),
                "mechanics": getattr(card, 'mechanics', []),
                "can_attack": getattr(card, 'can_attack', False)
            })
            
        opponent_field = []
        for card in opponent.field:  # 修复：使用 field 而不是 battlefield
            opponent_field.append({
                "name": getattr(card, 'name', 'Unknown'),
                "cost": getattr(card, 'cost', 0),
                "attack": getattr(card, 'attack', 0),
                "health": getattr(card, 'health', 0),
                "card_type": getattr(card, 'card_type', 'minion'),
                "mechanics": getattr(card, 'mechanics', []),
                "can_attack": getattr(card, 'can_attack', False)
            })
        
        # 使用字典方式创建GameContext以避免类型检查错误
        context_data = {
            "game_id": f"game_{id(game_engine)}",
            "current_player": game_engine.current_player_idx,
            "turn_number": game_engine.turn_number,
            "phase": "main",  # 简化处理
            "player_health": player.health,
            "player_mana": player.mana,  # 修复：使用 mana 而不是 current_mana
            "player_hand": player_hand,
            "player_field": player_field,
            "player_deck_size": len(player.hand),  # 简化处理
            "opponent_health": opponent.health,
            "opponent_mana": opponent.mana,  # 修复：使用 mana 而不是 current_mana
            "opponent_field": opponent_field,
            "opponent_hand_size": len(opponent.hand),  # 简化处理
            "opponent_deck_size": len(opponent.hand)  # 简化处理
        }
        
        # 移除 GameContext 不接受的参数
        game_context_params = {
            "game_id": context_data["game_id"],
            "current_player": context_data["current_player"],
            "turn_number": context_data["turn_number"],
            "phase": context_data["phase"],
            "player_hand": context_data["player_hand"],
            "player_field": context_data["player_field"],
            "opponent_field": context_data["opponent_field"],
            "player_mana": context_data["player_mana"],
            "opponent_mana": context_data["opponent_mana"],
            "player_health": context_data["player_health"],
            "opponent_health": context_data["opponent_health"]
        }
        
        # 使用**kwargs方式创建GameContext
        return GameContext(**game_context_params)

    def _learn_from_victory(self, game_result: Dict[str, Any]):
        """从胜利中学习"""
        # 记录成功的决策模式
        successful_decisions = [
            record for record in self.decision_history[-20:]  # 最近20个决策
            if record.get("action") and record.get("confidence", 0) > 0.7
        ]

        for decision in successful_decisions:
            self.memory.successful_moves.append(decision)

        # 限制记忆长度
        if len(self.memory.successful_moves) > 100:
            self.memory.successful_moves = self.memory.successful_moves[-50:]

    def _learn_from_defeat(self, game_result: Dict[str, Any]):
        """从失败中学习"""
        # 记录失败的决策模式
        failed_decisions = [
            record for record in self.decision_history[-20:]
            if record.get("action") and record.get("confidence", 0) < 0.5
        ]

        for decision in failed_decisions:
            self.memory.failed_moves.append(decision)

        # 限制记忆长度
        if len(self.memory.failed_moves) > 100:
            self.memory.failed_moves = self.memory.failed_moves[-50:]

    def _evolve_personality(self):
        """进化人格配置"""
        recent_games = 10  # 最近10场游戏

        if len(self.decision_history) < recent_games:
            return

        # 计算最近的胜率
        recent_wins = sum(1 for i in range(min(recent_games, self.games_played))
                         if self.games_played - 1 - i < len(self.decision_history))

        recent_win_rate = recent_wins / min(recent_games, self.games_played)

        # 根据表现调整人格
        personality_manager = PersonalityManager()
        game_outcomes = [{"won": i < recent_wins} for i in range(recent_games)]

        evolved_profile = personality_manager.evolve_personality(
            self.personality, game_outcomes
        )

        if evolved_profile != self.personality:
            self.personality = evolved_profile
            logger.info(f"代理 {self.agent_id} 人格已进化: {self.personality.name}")

    def learn_from_game(self, game_result: Dict[str, Any]):
        """从游戏结果中学习"""
        self.games_played += 1

        if game_result.get("won", False):
            self.wins += 1
            self._learn_from_victory(game_result)
        else:
            self.losses += 1
            self._learn_from_defeat(game_result)

        # 更新对手印象
        opponent_id = game_result.get("opponent_id")
        if opponent_id:
            impression = {
                "aggression": game_result.get("opponent_aggression", 0.5),
                "skill_level": game_result.get("opponent_skill", 0.5),
                "preferred_cards": game_result.get("opponent_cards", [])
            }
            self.memory.add_opponent_impression(opponent_id, impression)

        # 进化人格（如果启用学习）
        if self.is_learning and self.games_played % 5 == 0:
            self._evolve_personality()

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        win_rate = self.wins / max(1, self.games_played)

        avg_confidence = 0
        if self.decision_history:
            confidences = [d.get("confidence", 0) for d in self.decision_history if d.get("confidence")]
            avg_confidence = sum(confidences) / max(1, len(confidences))

        return {
            "agent_id": self.agent_id,
            "personality": self.personality.name,
            "games_played": self.games_played,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": win_rate,
            "total_decisions": self.total_decisions,
            "average_confidence": avg_confidence,
            "current_emotion": self.current_emotion,
            "opponents_known": len(self.memory.opponent_styles),
            "strategy_performance": self.base_strategy.get_performance_stats() if hasattr(self.base_strategy, 'get_performance_stats') else {}
        }

    def reset_statistics(self):
        """重置统计信息"""
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.total_decisions = 0
        self.decision_history.clear()
        self.current_emotion = "neutral"
        self.emotion_intensity = 0.5

        if hasattr(self.base_strategy, 'reset_statistics'):
            self.base_strategy.reset_statistics()