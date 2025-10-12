"""
AI引擎测试套件
测试各种AI策略和代理的功能
"""
import pytest
import asyncio
import time
from unittest.mock import Mock, patch

# 导入要测试的模块
from ai_engine.engine import AIEngine, AIEngineConfig
from ai_engine.strategies.rule_based import RuleBasedStrategy
from ai_engine.strategies.base import AIAction, ActionType, GameContext
from ai_engine.agents.agent_personality import PersonalityManager, PERSONALITY_PROFILES
from ai_engine.agents.ai_agent import AIAgent
from ai_engine.monitoring import PerformanceMonitor


class TestGameContext:
    """测试用的游戏上下文"""

    @staticmethod
    def create_test_context():
        """创建测试用的游戏上下文"""
        return GameContext(
            game_id="test_game_001",
            current_player=0,
            turn_number=5,
            phase="main",

            player_health=25,
            player_max_health=30,
            player_mana=6,
            player_max_mana=6,
            player_hand=[
                {
                    "name": "测试随从",
                    "cost": 3,
                    "attack": 4,
                    "health": 3,
                    "instance_id": "test_card_001",
                    "card_type": "minion",
                    "mechanics": []
                }
            ],
            player_field=[
                {
                    "name": "测试随从2",
                    "attack": 2,
                    "health": 2,
                    "instance_id": "test_minion_001",
                    "can_attack": True,
                    "mechanics": []
                }
            ],
            player_deck_size=15,

            opponent_health=20,
            opponent_max_health=30,
            opponent_mana=4,
            opponent_max_mana=4,
            opponent_field=[
                {
                    "name": "对手随从",
                    "attack": 1,
                    "health": 3,
                    "instance_id": "opp_minion_001",
                    "can_attack": True,
                    "mechanics": ["taunt"]
                }
            ],
            opponent_hand_size=4,
            opponent_deck_size=17
        )


class TestRuleBasedStrategy:
    """测试基于规则的AI策略"""

    @pytest.fixture
    def strategy(self):
        """创建测试策略"""
        config = {
            "mana_curve_preference": 0.7,
            "board_control_weight": 0.8,
            "face_damage_weight": 0.6
        }
        return RuleBasedStrategy("测试规则AI", config)

    @pytest.fixture
    def context(self):
        """创建测试上下文"""
        return TestGameContext.create_test_context()

    @pytest.mark.asyncio
    async def test_make_decision(self, strategy, context):
        """测试AI决策"""
        action = await strategy.make_decision(context)

        assert action is not None
        assert isinstance(action, AIAction)
        assert action.action_type in [at for at in ActionType]
        assert 0 <= action.confidence <= 1
        assert len(action.reasoning) > 0

    @pytest.mark.asyncio
    async def test_execute_with_timing(self, strategy, context):
        """测试带时间统计的执行"""
        action = await strategy.execute_with_timing(context)

        assert action is not None
        assert action.execution_time >= 0
        assert strategy.total_decisions == 1
        assert strategy.successful_decisions == 1

    def test_evaluate_board_state(self, strategy, context):
        """测试局面评估"""
        score = strategy.evaluate_board_state(context)

        assert isinstance(score, float)
        assert -1 <= score <= 1

    def test_performance_stats(self, strategy):
        """测试性能统计"""
        stats = strategy.get_performance_stats()

        assert "name" in stats
        assert "strategy_id" in stats
        assert "total_decisions" in stats
        assert "success_rate" in stats
        assert "average_decision_time" in stats

    def test_reset_statistics(self, strategy):
        """测试统计重置"""
        # 先添加一些统计数据
        strategy.total_decisions = 10
        strategy.successful_decisions = 8
        strategy.average_decision_time = 1.5

        strategy.reset_statistics()

        assert strategy.total_decisions == 0
        assert strategy.successful_decisions == 0
        assert strategy.average_decision_time == 0.0


class TestAIEngine:
    """测试AI引擎"""

    @pytest.fixture
    def engine_config(self):
        """创建引擎配置"""
        return AIEngineConfig(
            default_strategy="rule_based",
            max_decision_time=5.0,
            enable_monitoring=True
        )

    @pytest.fixture
    def engine(self, engine_config):
        """创建AI引擎"""
        return AIEngine(engine_config)

    @pytest.fixture
    def context(self):
        """创建测试上下文"""
        return TestGameContext.create_test_context()

    def test_engine_initialization(self, engine):
        """测试引擎初始化"""
        assert engine.config.default_strategy == "rule_based"
        assert "rule_based" in engine.strategies
        assert engine.current_strategy == "rule_based"

    def test_strategy_registration(self, engine):
        """测试策略注册"""
        # 注册新策略
        new_strategy = RuleBasedStrategy("测试策略")
        engine.register_strategy("test_strategy", new_strategy)

        assert "test_strategy" in engine.strategies
        assert engine.get_available_strategies() == ["rule_based", "test_strategy"]

    def test_strategy_selection(self, engine):
        """测试策略选择"""
        # 设置策略
        success = engine.set_strategy("rule_based")
        assert success is True
        assert engine.current_strategy == "rule_based"

        # 设置不存在的策略
        success = engine.set_strategy("nonexistent")
        assert success is False

    @pytest.mark.asyncio
    async def test_make_decision(self, engine, context):
        """测试AI决策"""
        action = await engine.make_decision(context)

        assert action is not None
        assert isinstance(action, AIAction)
        assert engine.total_decisions_made == 1

    def test_engine_stats(self, engine):
        """测试引擎统计"""
        stats = engine.get_engine_stats()

        assert "total_games_played" in stats
        assert "total_decisions_made" in stats
        assert "available_strategies" in stats
        assert "current_strategy" in stats

    def test_start_new_game(self, engine):
        """测试开始新游戏"""
        engine.start_new_game("test_game")
        assert engine.total_games_played == 1


class TestPersonalitySystem:
    """测试人格系统"""

    @pytest.fixture
    def personality_manager(self):
        """创建人格管理器"""
        return PersonalityManager()

    def test_predefined_profiles(self, personality_manager):
        """测试预定义人格"""
        profiles = list(PERSONALITY_PROFILES.keys())
        assert len(profiles) > 0
        assert "aggressive_berserker" in profiles
        assert "wise_defender" in profiles

    def test_get_profile(self, personality_manager):
        """测试获取人格配置"""
        profile = personality_manager.get_profile("aggressive_berserker")
        assert profile is not None
        assert profile.name == "狂战士"
        assert profile.aggression_level > 0.8

    def test_get_random_profile(self, personality_manager):
        """测试获取随机人格"""
        profile = personality_manager.get_random_profile()
        assert profile is not None
        assert profile.name in PERSONALITY_PROFILES

    def test_create_hybrid_profile(self, personality_manager):
        """测试创建混合人格"""
        hybrid = personality_manager.create_hybrid_profile(
            "测试混合",
            ["aggressive_berserker", "wise_defender"],
            [0.6, 0.4]
        )

        assert hybrid.name == "测试混合"
        assert 0 < hybrid.aggression_level < 1
        assert 0 < hybrid.patience_level < 1


class TestAIAgent:
    """测试AI代理"""

    @pytest.fixture
    def agent(self):
        """创建AI代理"""
        personality = PERSONALITY_PROFILES["adaptive_learner"]
        strategy = RuleBasedStrategy("代理策略")
        return AIAgent("test_agent", personality, strategy)

    @pytest.fixture
    def context(self):
        """创建测试上下文"""
        return TestGameContext.create_test_context()

    @pytest.mark.asyncio
    async def test_make_decision(self, agent, context):
        """测试代理决策"""
        action = await agent.make_decision(context)

        assert action is not None
        assert isinstance(action, AIAction)
        assert agent.total_decisions == 1

    def test_personality_application(self, agent):
        """测试人格应用"""
        assert agent.personality.name == "适应性学习者"
        assert agent.current_emotion == "neutral"
        assert 0 <= agent.emotion_intensity <= 1

    def test_learning_system(self, agent):
        """测试学习系统"""
        # 模拟游戏结果
        game_result = {
            "won": True,
            "opponent_id": "test_opponent",
            "opponent_aggression": 0.6
        }

        initial_games = agent.games_played
        agent.learn_from_game(game_result)

        assert agent.games_played == initial_games + 1
        assert agent.wins == 1

    def test_performance_stats(self, agent):
        """测试代理性能统计"""
        stats = agent.get_performance_stats()

        assert "agent_id" in stats
        assert "personality" in stats
        assert "games_played" in stats
        assert "win_rate" in stats
        assert "total_decisions" in stats


class TestPerformanceMonitor:
    """测试性能监控"""

    @pytest.fixture
    def monitor(self):
        """创建性能监控器"""
        return PerformanceMonitor(max_history=100)

    def test_monitor_initialization(self, monitor):
        """测试监控器初始化"""
        assert monitor.max_history == 100
        assert monitor.is_monitoring is False
        assert len(monitor.metrics_history) == 0

    def test_record_decision(self, monitor):
        """测试记录决策"""
        monitor.record_decision(
            strategy_name="test_strategy",
            game_id="test_game",
            decision_time=0.5,
            confidence=0.8,
            success=True
        )

        assert len(monitor.metrics_history) == 1
        assert "test_strategy" in monitor.strategy_stats

    def test_system_health(self, monitor):
        """测试系统健康检查"""
        health = monitor.get_system_health()

        assert health.status in ["healthy", "warning", "critical"]
        assert 0 <= health.cpu_usage <= 100
        assert 0 <= health.memory_usage <= 100

    def test_performance_summary(self, monitor):
        """测试性能摘要"""
        # 添加一些测试数据
        for i in range(10):
            monitor.record_decision(
                strategy_name="test_strategy",
                game_id=f"game_{i}",
                decision_time=0.1 + i * 0.1,
                confidence=0.5 + i * 0.05,
                success=i % 2 == 0
            )

        summary = monitor.get_performance_summary()

        assert "total_decisions" in summary
        assert "success_rate" in summary
        assert "avg_response_time" in summary
        assert "strategies_used" in summary

    def test_alert_system(self, monitor):
        """测试告警系统"""
        alert_called = False

        def test_callback(alert):
            nonlocal alert_called
            alert_called = True

        monitor.add_alert_callback(test_callback)

        # 手动触发告警
        alert = {
            "type": "test_alert",
            "message": "测试告警",
            "severity": "warning",
            "timestamp": time.time()
        }

        monitor._trigger_alert(alert)
        assert alert_called is True


# 集成测试
class TestIntegration:
    """集成测试"""

    @pytest.mark.asyncio
    async def test_full_ai_pipeline(self):
        """测试完整的AI流程"""
        # 创建组件
        config = AIEngineConfig()
        engine = AIEngine(config)
        context = TestGameContext.create_test_context()

        # 创建多个AI代理
        personalities = ["aggressive_berserker", "wise_defender", "strategic_mastermind"]
        agents = []

        for personality_name in personalities:
            personality = PERSONALITY_PROFILES[personality_name]
            strategy = RuleBasedStrategy(f"{personality_name}_策略")
            agent = AIAgent(f"agent_{personality_name}", personality, strategy)
            agents.append(agent)

        # 测试多个代理的决策
        decisions = []
        for agent in agents:
            action = await agent.make_decision(context)
            if action:
                decisions.append((agent.personality.name, action))

        # 验证结果
        assert len(decisions) > 0
        assert all(isinstance(action, AIAction) for _, action in decisions)

        # 测试学习
        for agent in agents:
            game_result = {"won": True, "opponent_id": "test"}
            agent.learn_from_game(game_result)
            assert agent.games_played == 1

    def test_monitoring_integration(self):
        """测试监控集成"""
        config = AIEngineConfig(enable_monitoring=True)
        engine = AIEngine(config)
        monitor = PerformanceMonitor()

        # 模拟一些决策
        context = TestGameContext.create_test_context()

        # 记录性能数据
        for i in range(5):
            monitor.record_decision(
                strategy_name="rule_based",
                game_id=f"test_game_{i}",
                decision_time=0.1,
                confidence=0.8,
                success=True
            )

        # 获取性能数据
        summary = monitor.get_performance_summary()
        health = monitor.get_system_health()

        assert summary["total_decisions"] == 5
        assert health.status in ["healthy", "warning", "critical"]


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])