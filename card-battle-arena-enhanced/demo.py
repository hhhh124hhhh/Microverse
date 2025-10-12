"""
Card Battle Arena Enhanced 演示程序
展示AI系统的各种功能
"""
import asyncio
import time
from typing import Dict, List, Any

from ai_engine.engine import AIEngine, AIEngineConfig
from ai_engine.strategies.rule_based import RuleBasedStrategy
from ai_engine.strategies.hybrid import HybridAIStrategy
from ai_engine.agents.agent_personality import PersonalityManager, PERSONALITY_PROFILES
from ai_engine.agents.ai_agent import AIAgent
from game_engine.game_state.game_context import GameContext
from ai_engine.llm_integration.openai_client import OpenAIClient
from ai_engine.llm_integration.base import LLMManager, LLMMessage


def create_demo_game_context() -> GameContext:
    """创建演示用的游戏上下文"""
    return GameContext(
        game_id="demo_game_001",
        current_player=0,
        turn_number=5,
        phase="main",

        # 玩家状态
        player_health=25,
        player_max_health=30,
        player_mana=6,
        player_max_mana=6,
        player_hand=[
            {
                "name": "烈焰元素",
                "cost": 3,
                "attack": 5,
                "health": 3,
                "instance_id": "card_001",
                "card_type": "minion",
                "mechanics": []
            },
            {
                "name": "铁喙猫头鹰",
                "cost": 3,
                "attack": 2,
                "health": 2,
                "instance_id": "card_002",
                "card_type": "minion",
                "mechanics": ["taunt"]
            },
            {
                "name": "火球术",
                "cost": 4,
                "instance_id": "card_003",
                "card_type": "spell",
                "mechanics": []
            }
        ],
        player_field=[
            {
                "name": "狼人渗透者",
                "attack": 3,
                "health": 2,
                "instance_id": "minion_001",
                "can_attack": True,
                "mechanics": ["stealth"]
            }
        ],
        player_deck_size=20,

        # 对手状态
        opponent_health=20,
        opponent_max_health=30,
        opponent_mana=4,
        opponent_max_mana=4,
        opponent_field=[
            {
                "name": "霜狼步兵",
                "attack": 2,
                "health": 3,
                "instance_id": "opp_minion_001",
                "can_attack": True,
                "mechanics": ["taunt"]
            },
            {
                "name": "石像鬼",
                "attack": 1,
                "health": 1,
                "instance_id": "opp_minion_002",
                "can_attack": False,
                "mechanics": ["divine_shield"]
            }
        ],
        opponent_hand_size=4,
        opponent_deck_size=18
    )


async def demo_rule_based_ai():
    """演示基于规则的AI"""
    print("=" * 50)
    print("🤖 规则AI演示")
    print("=" * 50)

    # 创建AI引擎
    config = AIEngineConfig()
    engine = AIEngine(config)

    # 设置策略
    engine.set_strategy("rule_based")

    # 创建游戏上下文
    context = create_demo_game_context()

    print(f"游戏状态:")
    print(f"  我方血量: {context.player_health}/{context.player_max_health}")
    print(f"  我方法力: {context.player_mana}/{context.player_max_mana}")
    print(f"  手牌数量: {len(context.player_hand)}")
    print(f"  场面随从: {len(context.player_field)}")
    print(f"  对手血量: {context.opponent_health}/{context.opponent_max_health}")
    print(f"  对手场面: {len(context.opponent_field)}")
    print()

    # AI决策
    print("AI正在思考...")
    action = await engine.make_decision(context)

    if action:
        print(f"✅ AI决策: {action.action_type.value}")
        print(f"   置信度: {action.confidence:.2f}")
        print(f"   推理: {action.reasoning}")
        print(f"   执行时间: {action.execution_time:.3f}秒")
    else:
        print("❌ AI无法做出决策")

    # 显示性能统计
    stats = engine.get_engine_stats()
    print(f"\n📊 引擎统计:")
    print(f"   总决策数: {stats['total_decisions_made']}")
    print(f"   当前策略: {stats['current_strategy']}")


async def demo_personality_agents():
    """演示不同人格的AI代理"""
    print("\n" + "=" * 50)
    print("🎭 AI人格代理演示")
    print("=" * 50)

    personality_manager = PersonalityManager()
    context = create_demo_game_context()

    # 选择几种不同的人格进行演示
    demo_personalities = ["aggressive_berserker", "wise_defender", "strategic_mastermind"]

    for personality_name in demo_personalities:
        profile = personality_manager.get_profile(personality_name)
        print(f"\n🎯 {profile.name} ({profile.description})")
        print(f"   风格: {profile.play_style.value}")
        print(f"   激进程度: {profile.aggression_level:.2f}")
        print(f"   风险容忍: {profile.risk_tolerance:.2f}")

        # 创建AI代理
        strategy = RuleBasedStrategy(f"{profile.name}_策略")
        agent = AIAgent(
            agent_id=f"agent_{personality_name}",
            personality=profile,
            ai_strategy=strategy
        )

        # 做决策
        action = await agent.make_decision(context)

        if action:
            print(f"   🎲 决策: {action.action_type.value} (置信度: {action.confidence:.2f})")
            print(f"   💭 推理: {action.reasoning}")
            print(f"   😊 情感: {agent.current_emotion}")


async def demo_hybrid_ai():
    """演示混合AI系统"""
    print("\n" + "=" * 50)
    print("🧠 混合AI系统演示")
    print("=" * 50)

    # 创建混合策略配置
    hybrid_config = {
        "strategies": [
            {"name": "rule_based", "weight": 0.6, "min_confidence": 0.3},
            {"name": "llm_enhanced", "weight": 0.4, "min_confidence": 0.5}
        ],
        "consensus_method": "weighted_voting",
        "enable_adaptive_weights": True
    }

    # 创建混合策略
    hybrid_strategy = HybridAIStrategy("混合智能AI", hybrid_config)

    # 创建AI引擎
    config = AIEngineConfig(default_strategy="hybrid")
    engine = AIEngine(config)
    engine.register_strategy("hybrid", hybrid_strategy)
    engine.set_strategy("hybrid")

    context = create_demo_game_context()

    print("混合AI正在综合分析...")
    action = await engine.make_decision(context, "hybrid")

    if action:
        print(f"✅ 混合AI决策: {action.action_type.value}")
        print(f"   置信度: {action.confidence:.2f}")
        print(f"   推理: {action.reasoning}")

        # 获取详细的性能统计
        hybrid_stats = hybrid_strategy.get_performance_stats()
        print(f"\n📈 混合AI统计:")
        print(f"   总决策数: {hybrid_stats['decisions_made']}")
        print(f"   平均共识分数: {hybrid_stats['average_consensus_score']:.2f}")
        print(f"   策略权重: {hybrid_stats['strategy_weights']}")
    else:
        print("❌ 混合AI无法做出决策")


async def demo_learning_system():
    """演示学习系统"""
    print("\n" + "=" * 50)
    print("📚 AI学习系统演示")
    print("=" * 50)

    # 创建一个学习型代理
    personality = PERSONALITY_PROFILES["adaptive_learner"]
    strategy = RuleBasedStrategy("学习策略")
    agent = AIAgent(
        agent_id="learning_agent",
        personality=personality,
        ai_strategy=strategy
    )

    context = create_demo_game_context()

    print(f"🎓 {personality.name} 学习演示")
    print(f"   学习率: {personality.learning_rate:.2f}")

    # 模拟多轮决策
    for round_num in range(1, 4):
        print(f"\n--- 第 {round_num} 轮决策 ---")
        action = await agent.make_decision(context)

        if action:
            print(f"决策: {action.action_type.value} (置信度: {action.confidence:.2f})")

        # 模拟游戏结果
        game_result = {
            "won": round_num % 2 == 1,  # 交替胜负
            "opponent_id": "demo_opponent",
            "opponent_aggression": 0.6,
            "opponent_skill": 0.7
        }

        agent.learn_from_game(game_result)
        stats = agent.get_performance_stats()

        print(f"学习进度: {stats['games_played']} 场, "
              f"胜率: {stats['win_rate']:.2f}, "
              f"情感: {stats['current_emotion']}")


async def demo_performance_monitoring():
    """演示性能监控"""
    print("\n" + "=" * 50)
    print("📊 性能监控系统演示")
    print("=" * 50)

    # 创建AI引擎
    config = AIEngineConfig(enable_monitoring=True)
    engine = AIEngine(config)

    context = create_demo_game_context()

    # 执行多次决策以收集数据
    print("执行多次决策以收集性能数据...")
    for i in range(5):
        engine.start_new_game(f"test_game_{i}")
        action = await engine.make_decision(context)
        if action:
            print(f"  决策 {i+1}: {action.action_type.value} "
                  f"(置信度: {action.confidence:.2f}, "
                  f"耗时: {action.execution_time:.3f}s)")

    # 获取详细的性能报告
    stats = engine.get_engine_stats()
    print(f"\n📈 性能报告:")
    print(f"   总游戏数: {stats['total_games_played']}")
    print(f"   总决策数: {stats['total_decisions_made']}")
    print(f"   可用策略: {', '.join(stats['available_strategies'])}")
    print(f"   性能记录数: {stats['total_performance_records']}")

    # 获取策略性能
    for strategy_name in stats['available_strategies']:
        strategy_stats = engine.get_strategy_performance(strategy_name)
        if strategy_stats:
            print(f"\n🎯 {strategy_name} 策略性能:")
            print(f"   成功率: {strategy_stats['success_rate']:.2f}")
            print(f"   平均决策时间: {strategy_stats['average_decision_time']:.3f}s")
            print(f"   总决策数: {strategy_stats['total_decisions']}")


async def main():
    """主演示函数"""
    print("🎮 Card Battle Arena Enhanced - AI系统演示")
    print("🚀 展示智能AI代理、混合决策系统和学习能力")

    try:
        # 1. 规则AI演示
        await demo_rule_based_ai()

        # 2. 人格代理演示
        await demo_personality_agents()

        # 3. 混合AI演示
        await demo_hybrid_ai()

        # 4. 学习系统演示
        await demo_learning_system()

        # 5. 性能监控演示
        await demo_performance_monitoring()

        print("\n" + "=" * 50)
        print("✨ 演示完成！")
        print("💡 这个系统展示了:")
        print("   • 多种AI策略的结合")
        print("   • 个性化AI代理")
        print("   • 混合决策机制")
        print("   • 自适应学习能力")
        print("   • 完整的性能监控")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())