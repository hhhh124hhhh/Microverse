#!/usr/bin/env python3
"""
DeepSeek AI集成测试脚本
测试DeepSeek API是否正常工作
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ai_engine.llm_integration.deepseek_client import DeepSeekClient
from config.settings import get_settings


async def test_deepseek_client():
    """测试DeepSeek客户端"""
    settings = get_settings()
    api_key = settings.ai.deepseek_api_key

    if not api_key or api_key == "your_deepseek_api_key_here":
        print("❌ 未配置DeepSeek API密钥")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return False

    print("🔧 测试DeepSeek API连接...")

    try:
        # 创建DeepSeek客户端
        client = DeepSeekClient(api_key=api_key)

        # 测试简单对话
        from ai_engine.llm_integration.base import LLMMessage
        messages = [
            LLMMessage(role="user", content="你好，请简单介绍一下你自己。")
        ]

        response = await client.chat_completion(messages, max_tokens=100)

        print("✅ DeepSeek API连接成功!")
        print(f"📝 响应: {response.content[:100]}...")
        print(f"⏱️  响应时间: {response.response_time:.2f}秒")
        print(f"📊 Token使用: {response.usage}")

        # 关闭客户端
        await client.close()

        return True

    except Exception as e:
        print(f"❌ DeepSeek API测试失败: {e}")
        return False


async def test_game_analysis():
    """测试游戏状态分析"""
    settings = get_settings()
    api_key = settings.ai.deepseek_api_key

    if not api_key or api_key == "your_deepseek_api_key_here":
        print("❌ 未配置DeepSeek API密钥，跳过游戏分析测试")
        return False

    print("\n🎮 测试游戏状态分析...")

    try:
        # 创建DeepSeek客户端
        client = DeepSeekClient(api_key=api_key)

        # 模拟游戏状态
        game_state = {
            "player_health": 20,
            "opponent_health": 15,
            "player_mana": 6,
            "opponent_mana": 4,
            "player_field": [
                {"name": "烈焰元素", "attack": 5, "health": 3}
            ],
            "opponent_field": [
                {"name": "霜狼步兵", "attack": 2, "health": 3, "mechanics": ["taunt"]}
            ]
        }

        player_info = {
            "personality": "aggressive",
            "hand_size": 3
        }

        # 分析游戏状态
        analysis = await client.analyze_game_state(game_state, player_info)

        print("✅ 游戏状态分析成功!")
        print(f"📊 分析结果: {analysis[:200]}...")

        # 关闭客户端
        await client.close()

        return True

    except Exception as e:
        print(f"❌ 游戏状态分析失败: {e}")
        return False


async def test_llm_enhanced_strategy():
    """测试LLM增强策略"""
    try:
        from ai_engine.strategies.llm_enhanced import LLMEnhancedStrategy
        from ai_engine.llm_integration.base import LLMManager
        from ai_engine.llm_integration.deepseek_client import DeepSeekClient
        from game_engine.game_state.game_context import GameContext

        settings = get_settings()
        api_key = settings.ai.deepseek_api_key

        if not api_key or api_key == "your_deepseek_api_key_here":
            print("❌ 未配置DeepSeek API密钥，跳过LLM策略测试")
            return False

        print("\n🤖 测试LLM增强策略...")

        # 创建LLM管理器
        llm_manager = LLMManager()
        deepseek_client = DeepSeekClient(api_key=api_key)
        llm_manager.register_client("deepseek", deepseek_client, is_default=True)

        # 创建LLM增强策略
        llm_strategy = LLMEnhancedStrategy("DeepSeek增强AI", {
            "llm_client": "deepseek",
            "llm_temperature": 0.3,
            "llm_weight": 0.7,
            "rule_weight": 0.3
        })
        llm_strategy.set_llm_manager(llm_manager)

        # 创建测试游戏上下文
        context = GameContext(
            game_id="test_llm_game",
            current_player=0,
            turn_number=5,
            phase="main",

            player_health=20,
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

            opponent_health=15,
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
                }
            ],
            opponent_hand_size=4,
            opponent_deck_size=18
        )

        # 测试LLM决策
        action = await llm_strategy.make_decision(context)

        if action:
            print("✅ LLM增强策略决策成功!")
            print(f"🎲 决策: {action.action_type.value}")
            print(f"📊 置信度: {action.confidence:.2f}")
            print(f"💭 推理: {action.reasoning[:100]}...")
        else:
            print("❌ LLM增强策略未能做出决策")
            return False

        # 关闭客户端
        await deepseek_client.close()

        return True

    except Exception as e:
        print(f"❌ LLM增强策略测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🧪 DeepSeek AI集成测试")
    print("=" * 50)

    # 显示配置信息
    settings = get_settings()
    print(f"🔧 DeepSeek模型: {settings.ai.deepseek_model}")
    print(f"🤖 默认策略: {settings.ai.default_strategy}")
    print(f"👥 默认人格: {settings.ai.default_personality}")

    if not settings.ai.deepseek_api_key or settings.ai.deepseek_api_key == "your_deepseek_api_key_here":
        print("\n⚠️  未配置DeepSeek API密钥")
        print("请按以下步骤配置:")
        print("1. 访问 https://platform.deepseek.com/")
        print("2. 注册账号并获取API密钥")
        print("3. 编辑 .env 文件")
        print("4. 设置 DEEPSEEK_API_KEY=你的API密钥")
        return

    # 运行测试
    tests = [
        ("API连接测试", test_deepseek_client),
        ("游戏分析测试", test_game_analysis),
        ("LLM策略测试", test_llm_enhanced_strategy)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name}通过")
            else:
                print(f"❌ {test_name}失败")
        except Exception as e:
            print(f"❌ {test_name}异常: {e}")

    # 显示测试结果
    print(f"\n📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！DeepSeek AI集成配置成功！")
    else:
        print("⚠️  部分测试失败，请检查配置")


if __name__ == "__main__":
    asyncio.run(main())