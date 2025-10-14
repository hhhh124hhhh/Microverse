#!/usr/bin/env python3
"""
Card Battle Arena Enhanced - 主程序入口
智能卡牌游戏AI系统
"""
import asyncio
import argparse
import logging
import sys
import random
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from demo import main as demo_main
from ai_engine.engine import AIEngine, AIEngineConfig
from ai_engine.strategies.rule_based import RuleBasedStrategy
from ai_engine.strategies.hybrid import HybridAIStrategy
from ai_engine.agents.agent_personality import PersonalityManager
from ai_engine.agents.ai_agent import AIAgent
from ai_engine.debug_tools import debugger
from game_engine.game_state.game_context import GameContext
from game_engine.card_game import CardGame
from game_ui import GameUI

# Rich库导入
from rich.panel import Panel
from rich import box


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('card_battle_arena.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def safe_get_card_attr(card, attr_name, default=None):
    """安全获取卡牌属性，支持对象和字典格式"""
    try:
        # 尝试直接访问属性（对象格式）
        return getattr(card, attr_name)
    except AttributeError:
        try:
            # 尝试字典访问
            return card[attr_name]
        except (KeyError, TypeError):
            return default

def get_card_name(card):
    """获取卡牌名称"""
    return safe_get_card_attr(card, 'name', '未知卡牌')

def get_card_attack(card):
    """获取卡牌攻击力"""
    return safe_get_card_attr(card, 'attack', 0)

def get_card_health(card):
    """获取卡牌血量"""
    return safe_get_card_attr(card, 'health', 0)

def get_card_type(card):
    """获取卡牌类型，兼容字典和对象格式"""
    # 先尝试对象格式的card_type
    card_type = safe_get_card_attr(card, 'card_type')
    if card_type:
        return card_type
    # 再尝试字典格式的type
    return safe_get_card_attr(card, 'type', 'minion')

def create_ai_context(game: CardGame, ai_player_idx: int = 1, game_id: str = "ai_game") -> GameContext:
    """
    为AI创建正确的游戏上下文

    Args:
        game: 卡牌游戏实例
        ai_player_idx: AI玩家的索引 (0 或 1)
        game_id: 游戏ID

    Returns:
        GameContext: AI的游戏上下文
    """
    state = game.get_game_state()

    # 确定AI和对手的状态
    if game.current_player_idx == ai_player_idx:
        # AI是当前玩家
        ai_state = state["current_player_state"]
        opponent_state = state["opponent_state"]
        current_player_for_context = ai_player_idx
    else:
        # AI是对手（在AI vs AI模式中可能发生）
        ai_state = state["opponent_state"]
        opponent_state = state["current_player_state"]
        current_player_for_context = ai_player_idx

    return GameContext(
        game_id=game_id,
        current_player=current_player_for_context,
        turn_number=game.turn_number,
        phase="main",

        # AI的状态
        player_health=ai_state["health"],
        player_max_health=ai_state["max_health"],
        player_mana=ai_state["mana"],
        player_max_mana=ai_state["max_mana"],
        player_hand=ai_state.get("hand", []),
        player_field=ai_state["field"],
        player_deck_size=0,

        # 对手的状态
        opponent_health=opponent_state["health"],
        opponent_max_health=opponent_state["max_health"],
        opponent_mana=opponent_state["mana"],
        opponent_max_mana=opponent_state["max_mana"],
        opponent_field=opponent_state["field"],
        opponent_hand_size=len(opponent_state.get("hand", [])),
        opponent_deck_size=0
    )

async def execute_ai_action(action, game: CardGame, ai_player_idx: int = 1) -> Dict[str, Any]:
    """
    执行AI决策的动作，与AI分析保持一致

    Args:
        action: AI决策的动作
        game: 卡牌游戏实例
        ai_player_idx: AI玩家的索引

    Returns:
        Dict[str, Any]: 执行结果
    """
    if not action:
        return {"success": False, "message": "AI无决策"}

    action_type = action.action_type.value if hasattr(action.action_type, 'value') else str(action.action_type)

    logger.info(f"🎯 执行AI动作: {action_type}")
    if hasattr(action, 'reasoning') and action.reasoning:
        logger.info(f"💭 AI推理: {action.reasoning[:100]}...")

    result = {"success": False, "message": f"未知动作: {action_type}"}

    if action_type in ["play_minion", "play_card"]:
        # 优先使用AI建议的卡牌
        suggested_card = None
        if hasattr(action, 'parameters') and action.parameters:
            suggested_card = action.parameters.get("card")

        current = game.players[ai_player_idx]
        playable_cards = []

        # 如果AI建议了特定卡牌，优先选择它
        if suggested_card:
            suggested_name = get_card_name(suggested_card)
            for i, card in enumerate(current.hand):
                if get_card_name(card) == suggested_name and current.can_play_card(card):
                    playable_cards.append((i, card, "AI推荐"))
                    break

        # 如果没有找到AI推荐的卡牌，或者AI没有推荐，找出所有可出的牌
        if not playable_cards:
            for i, card in enumerate(current.hand):
                if current.can_play_card(card):
                    playable_cards.append((i, card, "可用"))

        if playable_cards:
            # 选择AI推荐的卡牌，或者第一个可用的卡牌
            card_idx, card, reason = playable_cards[0]
            result = game.play_card(ai_player_idx, card_idx)

            if result["success"]:
                card_name = get_card_name(card)
                card_attack = get_card_attack(card)
                card_health = get_card_health(card)
                result["message"] = f"AI打出 {card_name} ({card_attack}/{card_health}) - {reason} - {result['message']}"
            else:
                result["message"] = f"AI出牌失败: {result['message']}"
        else:
            result = {"success": False, "message": "AI没有可出的牌"}

    elif action_type == "use_spell":
        # 类似逻辑，处理法术牌
        suggested_card = None
        if hasattr(action, 'parameters') and action.parameters:
            suggested_card = action.parameters.get("card")

        current = game.players[ai_player_idx]
        spell_cards = []

        if suggested_card:
            suggested_name = get_card_name(suggested_card)
            for i, card in enumerate(current.hand):
                if get_card_name(card) == suggested_name and get_card_type(card) == "spell" and current.can_play_card(card):
                    spell_cards.append((i, card, "AI推荐"))
                    break

        if not spell_cards:
            for i, card in enumerate(current.hand):
                if get_card_type(card) == "spell" and current.can_play_card(card):
                    spell_cards.append((i, card, "可用"))

        if spell_cards:
            card_idx, card, reason = spell_cards[0]
            result = game.play_card(ai_player_idx, card_idx)

            if result["success"]:
                card_name = get_card_name(card)
                card_attack = get_card_attack(card)
                effect = "造成伤害" if card_attack > 0 else "治疗" if card_attack < 0 else "特殊效果"
                result["message"] = f"AI使用法术 {card_name} ({effect}) - {reason} - {result['message']}"
            else:
                result["message"] = f"AI使用法术失败: {result['message']}"
        else:
            result = {"success": False, "message": "AI没有可用的法术"}

    elif action_type == "use_hero_power":
        result = game.use_hero_power(ai_player_idx)
        if result["success"]:
            result["message"] = f"AI使用英雄技能 - {result['message']}"
        else:
            result["message"] = f"AI使用英雄技能失败: {result['message']}"

    elif action_type == "end_turn":
        result = game.end_turn(ai_player_idx, auto_attack=True)
        if result["success"]:
            result["message"] = f"AI结束回合 - {result['message']}"
        else:
            result["message"] = f"AI结束回合失败: {result['message']}"

    elif action_type == "attack":
        # 处理攻击动作
        if hasattr(action, 'parameters') and action.parameters:
            attacker = action.parameters.get("attacker")
            target = action.parameters.get("target")

            if attacker and target:
                # 需要找到对应的随从索引
                current = game.players[ai_player_idx]
                attacker_idx = None

                for i, minion in enumerate(current.field):
                    if get_card_name(minion) == get_card_name(attacker):
                        attacker_idx = i
                        break

                if attacker_idx is not None:
                    if isinstance(target, str) and "英雄" in target:
                        result = game.attack_with_hero(ai_player_idx)
                    else:
                        target_name = get_card_name(target) if target else "随从0"
                        result = game.attack_with_minion(ai_player_idx, attacker_idx, target_name)

                    if result["success"]:
                        result["message"] = f"AI执行攻击 - {result['message']}"
                    else:
                        result["message"] = f"AI攻击失败: {result['message']}"
                else:
                    result = {"success": False, "message": "AI找不到攻击随从"}
            else:
                result = {"success": False, "message": "AI攻击参数不完整"}
        else:
            result = {"success": False, "message": "AI攻击缺少参数"}

    # 记录执行结果
    if result["success"]:
        logger.info(f"✅ AI动作执行成功: {result['message']}")
    else:
        logger.warning(f"❌ AI动作执行失败: {result['message']}")

    return result


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Card Battle Arena Enhanced - 智能卡牌游戏AI系统",
        epilog="""
🚀 快速开始:
  %(prog)s demo                    # 运行AI功能演示
  %(prog)s play --mode ai-vs-ai --games 5      # AI对战5场
  %(prog)s play --mode human-vs-ai              # 人机对战模式
  %(prog)s test deepseek           # 测试DeepSeek集成
  %(prog)s list strategies          # 列出所有AI策略
  %(prog)s list personalities       # 列出所有AI人格
  %(prog)s benchmark --iterations 100   # 性能基准测试
  %(prog)s status --detailed        # 显示详细系统状态

📋 更多示例:
  %(prog)s play --strategy hybrid --personality aggressive_berserker  # 使用狂战士人格
  %(prog)s play --difficulty expert --games 3   # 专家难度对战3场
  %(prog)s config --show          # 显示当前配置
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 主命令组
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # demo命令 - 演示模式
    demo_parser = subparsers.add_parser("demo", help="运行AI功能演示 (Demo - 演示)")
    demo_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出 (Verbose - 详细)")

    # play命令 - 主游戏命令
    play_parser = subparsers.add_parser("play", help="开始游戏 (Play - 游戏)")
    play_parser.add_argument(
        "--mode", "-m",
        choices=["ai-vs-ai", "human-vs-ai", "ai-vs-human", "interactive", "menu"],
        default="ai-vs-ai",
        help="游戏模式 (Game Mode - 游戏模式): ai-vs-ai(AI对战), human-vs-ai(人机对战), ai-vs-human(AI对人), interactive(交互式模式), menu(炫酷菜单)"
    )
    play_parser.add_argument(
        "--strategy", "-s",
        choices=["rule_based", "hybrid", "llm_enhanced"],
        default="hybrid",
        help="AI策略类型 (AI Strategy - AI策略): rule_based(规则AI), hybrid(混合AI), llm_enhanced(LLM增强AI)"
    )
    play_parser.add_argument(
        "--personality", "-p",
        choices=["aggressive_berserker", "wise_defender", "strategic_mastermind",
                "combo_enthusiast", "adaptive_learner", "fun_seeker"],
        default="adaptive_learner",
        help="AI人格类型 (AI Personality - AI人格): aggressive_berserker(狂战士), wise_defender(守护者), strategic_mastermind(战略大师), combo_enthusiast(连锁爱好者), adaptive_learner(学习者), fun_seeker(娱乐玩家)"
    )
    play_parser.add_argument(
        "--difficulty", "-d",
        choices=["easy", "normal", "hard", "expert"],
        default="normal",
        help="AI难度级别 (Difficulty - 难度): easy(简单), normal(普通), hard(困难), expert(专家)"
    )
    play_parser.add_argument(
        "--games", "-g",
        type=int,
        default=1,
        help="游戏数量 (Game Count - 游戏场次)"
    )
    play_parser.add_argument(
        "--show-thinking",
        action="store_true",
        help="显示AI思考过程 (Show AI Thinking Process - 显示AI思考)"
    )

    # test命令 - 测试模式
    test_parser = subparsers.add_parser("test", help="运行测试 (Test - 测试)")
    test_parser.add_argument(
        "test_type",
        choices=["deepseek", "strategies", "personalities", "all"],
        help="测试类型 (Test Type - 测试类型): deepseek(DeepSeek AI测试), strategies(策略测试), personalities(人格测试), all(全部测试)"
    )
    test_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出 (Verbose - 详细)")

    # config命令 - 配置管理
    config_parser = subparsers.add_parser("config", help="配置管理 (Config - 配置)")
    config_parser.add_argument("--show", action="store_true", help="显示当前配置 (Show Configuration - 显示配置)")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="设置配置项 (Set Configuration - 设置配置)")
    config_parser.add_argument("--reset", action="store_true", help="重置配置 (Reset Configuration - 重置)")

    # list命令 - 列表信息
    list_parser = subparsers.add_parser("list", help="列出信息 (List - 列表)")
    list_parser.add_argument(
        "item",
        choices=["strategies", "personalities", "modes"],
        help="要列出的项目 (Item to List - 列表项目): strategies(策略列表), personalities(人格列表), modes(模式列表)"
    )

    # benchmark命令 - 性能测试
    benchmark_parser = subparsers.add_parser("benchmark", help="性能基准测试 (Benchmark - 基准测试)")
    benchmark_parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=100,
        help="测试迭代次数 (Test Iterations - 测试次数)"
    )
    benchmark_parser.add_argument(
        "--strategy", "-s",
        choices=["rule_based", "hybrid", "llm_enhanced"],
        help="测试指定策略 (Test Specific Strategy - 测试策略)"
    )

    # status命令 - 系统状态
    status_parser = subparsers.add_parser("status", help="显示系统状态 (Status - 状态)")
    status_parser.add_argument("--detailed", action="store_true", help="详细信息 (Detailed Info - 详细)")

    # debug命令 - AI调试工具
    debug_parser = subparsers.add_parser("debug", help="AI决策调试工具 (Debug - 调试)")
    debug_subparsers = debug_parser.add_subparsers(dest="action", help="调试动作")

    # performance子命令
    perf_parser = debug_subparsers.add_parser("performance", help="显示AI性能摘要")

    # export子命令
    export_parser = debug_subparsers.add_parser("export", help="导出调试报告")
    export_parser.add_argument("--output", "-o", help="输出文件路径")

    # analyze子命令
    analyze_parser = debug_subparsers.add_parser("analyze", help="分析决策模式")

    # clear子命令
    clear_parser = debug_subparsers.add_parser("clear", help="清空调试历史")

    # save子命令
    save_parser = debug_subparsers.add_parser("save", help="保存调试会话")
    save_parser.add_argument("filename", nargs="?", help="会话文件名")

    # load子命令
    load_parser = debug_subparsers.add_parser("load", help="加载调试会话")
    load_parser.add_argument("filename", help="会话文件名")

    # 全局选项 (Global Options - 全局选项)
    parser.add_argument("--version", action="version", version="Card Battle Arena Enhanced v1.0.0")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式 (Quiet Mode - 静默)")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细模式 (Verbose Mode - 详细)")

    return parser.parse_args()


def configure_logging(args):
    """配置日志级别"""
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    else:
        logging.getLogger().setLevel(logging.INFO)


def get_difficulty_config(difficulty: str) -> dict:
    """获取难度配置"""
    difficulty_configs = {
        "easy": {
            "thinking_time_range": (0.1, 0.5),
            "error_rate": 0.1,
            "confidence_penalty": 0.2
        },
        "normal": {
            "thinking_time_range": (0.5, 2.0),
            "error_rate": 0.05,
            "confidence_penalty": 0.1
        },
        "hard": {
            "thinking_time_range": (1.0, 3.0),
            "error_rate": 0.02,
            "confidence_penalty": 0.0
        },
        "expert": {
            "thinking_time_range": (2.0, 5.0),
            "error_rate": 0.0,
            "confidence_penalty": 0.0
        }
    }

    return difficulty_configs.get(difficulty, difficulty_configs["normal"])


async def run_ai_vs_ai(args):
    """运行AI对战模式"""
    logger.info(f"🎮 AI对战模式 - {args.strategy} vs {args.strategy}")

    # 获取人格管理器
    personality_manager = PersonalityManager()

    # 创建两个AI代理
    profile1 = personality_manager.get_profile(args.personality)
    profile2 = personality_manager.get_random_profile()

    logger.info(f"玩家1: {profile1.name}")
    logger.info(f"玩家2: {profile2.name}")

    # 创建AI策略
    if args.strategy == "rule_based":
        strategy1 = RuleBasedStrategy("AI_1")
        strategy2 = RuleBasedStrategy("AI_2")
    elif args.strategy == "hybrid":
        hybrid_config = {
            "strategies": [
                {"name": "rule_based", "weight": 0.6, "min_confidence": 0.3},
                {"name": "llm_enhanced", "weight": 0.4, "min_confidence": 0.5}
            ]
        }
        strategy1 = HybridAIStrategy("AI_1", hybrid_config)
        strategy2 = HybridAIStrategy("AI_2", hybrid_config)

        # 尝试设置LLM管理器
        try:
            from ai_engine.llm_integration.base import LLMManager
            from ai_engine.llm_integration.deepseek_client import DeepSeekClient
            from config.settings import get_settings

            settings = get_settings()
            if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                llm_manager = LLMManager()
                deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                llm_manager.register_client("deepseek", deepseek_client, is_default=True)

                strategy1.set_llm_manager(llm_manager)
                strategy2.set_llm_manager(llm_manager)
                logger.info("✅ LLM管理器已配置，混合AI策略完全启用")
            else:
                logger.warning("⚠️ LLM功能未配置或API密钥未设置，混合AI将仅使用规则部分")
        except Exception as e:
            logger.warning(f"⚠️ LLM配置失败: {e}，混合AI将仅使用规则部分")
    elif args.strategy == "llm_enhanced":
        try:
            from ai_engine.strategies.llm_enhanced import LLMEnhancedStrategy
            from ai_engine.llm_integration.base import LLMManager
            from ai_engine.llm_integration.deepseek_client import DeepSeekClient
            from config.settings import get_settings

            settings = get_settings()
            if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                llm_manager = LLMManager()
                deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                llm_manager.register_client("deepseek", deepseek_client, is_default=True)

                strategy1 = LLMEnhancedStrategy("AI_1", {
                    "llm_client": "deepseek",
                    "llm_temperature": 0.3,
                    "llm_weight": 0.8,
                    "rule_weight": 0.2
                })
                strategy2 = LLMEnhancedStrategy("AI_2", {
                    "llm_client": "deepseek",
                    "llm_temperature": 0.4,
                    "llm_weight": 0.7,
                    "rule_weight": 0.3
                })

                strategy1.set_llm_manager(llm_manager)
                strategy2.set_llm_manager(llm_manager)
                logger.info("✅ LLM增强策略已配置")
            else:
                logger.warning("⚠️ LLM功能未配置，回退到规则AI")
                strategy1 = RuleBasedStrategy("AI_1")
                strategy2 = RuleBasedStrategy("AI_2")
        except Exception as e:
            logger.warning(f"⚠️ LLM增强策略配置失败: {e}，回退到规则AI")
            strategy1 = RuleBasedStrategy("AI_1")
            strategy2 = RuleBasedStrategy("AI_2")
    else:
        logger.error(f"不支持的策略类型: {args.strategy}")
        return

    # 创建AI代理
    agent1 = AIAgent("player_1", profile1, strategy1)
    agent2 = AIAgent("player_2", profile2, strategy2)

    # 应用难度配置
    difficulty_config = get_difficulty_config(args.difficulty)

    # 运行指定数量的游戏
    for game_num in range(1, args.games + 1):
        logger.info(f"\n🏁 第 {game_num} 场游戏开始")

        # 模拟游戏（这里只是演示，实际需要完整的游戏逻辑）
        await simulate_game(agent1, agent2, game_num)

        if game_num < args.games:
            logger.info("⏳ 等待下一场游戏...")
            await asyncio.sleep(1)


async def simulate_game(agent1: AIAgent, agent2: AIAgent, game_num: int):
    """模拟一场真实的卡牌游戏"""
    import random

    logger.info(f"🎮 第 {game_num} 场游戏: {agent1.personality.name} vs {agent2.personality.name}")

    # 初始化游戏状态
    player_health = [30, 30]
    player_mana = [1, 1]
    player_max_mana = [1, 1]
    player_field = [[], []]
    player_hand = [[], []]
    player_deck_size = [25, 25]

    # 创建初始手牌
    def create_card(name, cost, attack, health, card_type="minion", mechanics=None):
        return {
            "name": name,
            "cost": cost,
            "attack": attack,
            "health": health,
            "card_type": card_type,
            "mechanics": mechanics or [],
            "instance_id": f"card_{random.randint(1000, 9999)}"
        }

    # 卡牌池
    card_pool = [
        create_card("烈焰元素", 3, 5, 3, "minion", []),
        create_card("霜狼步兵", 2, 2, 3, "minion", ["taunt"]),
        create_card("铁喙猫头鹰", 3, 2, 2, "minion", ["taunt"]),
        create_card("狼人渗透者", 2, 3, 2, "minion", ["stealth"]),
        create_card("石像鬼", 1, 1, 1, "minion", ["divine_shield"]),
        create_card("火球术", 4, 6, 0, "spell", []),
        create_card("闪电箭", 1, 3, 0, "spell", []),
        create_card("治愈术", 2, -5, 0, "spell", []),  # 负攻击表示治疗
        create_card("狂野之怒", 1, 3, 0, "spell", []),
        create_card("奥术智慧", 3, 0, 0, "spell", ["draw_cards"]),
    ]

    # 初始抽牌
    for player_idx in range(2):
        for _ in range(3):
            if player_deck_size[player_idx] > 0:
                card = random.choice(card_pool)
                player_hand[player_idx].append(card)
                player_deck_size[player_idx] -= 1

    # 游戏主循环
    current_player = 0
    turn_number = 1
    max_turns = 10  # 限制回合数

    while turn_number <= max_turns and player_health[0] > 0 and player_health[1] > 0:
        logger.info(f"\n🔄 回合 {turn_number} - {agent1.personality.name if current_player == 0 else agent2.personality.name} 回合")

        # 回合开始：增加法力值
        if player_max_mana[current_player] < 10:
            player_max_mana[current_player] += 1
        player_mana[current_player] = player_max_mana[current_player]

        # 抽一张牌
        if player_deck_size[current_player] > 0 and len(player_hand[current_player]) < 10:
            card = random.choice(card_pool)
            player_hand[current_player].append(card)
            player_deck_size[current_player] -= 1
            logger.info(f"🃏 {'玩家1' if current_player == 0 else '玩家2'} 抽取了 {card['name']}")

        # 显示当前状态
        logger.info(f"💰 法力值: {player_mana[current_player]}/{player_max_mana[current_player]}")
        logger.info(f"❤️ 生命值: {player_health[0]} vs {player_health[1]}")
        logger.info(f"👥 场面随从: {len(player_field[0])} vs {len(player_field[1])}")
        logger.info(f"🃋 手牌数量: {len(player_hand[0])} vs {len(player_hand[1])}")

        # 创建游戏上下文
        opponent_idx = 1 - current_player
        context = GameContext(
            game_id=f"game_{game_num}_turn_{turn_number}",
            current_player=current_player,
            turn_number=turn_number,
            phase="main",

            player_health=player_health[current_player],
            player_max_health=30,
            player_mana=player_mana[current_player],
            player_max_mana=player_max_mana[current_player],
            player_hand=player_hand[current_player],
            player_field=player_field[current_player],
            player_deck_size=player_deck_size[current_player],

            opponent_health=player_health[opponent_idx],
            opponent_max_health=30,
            opponent_mana=player_mana[opponent_idx],
            opponent_max_mana=player_max_mana[opponent_idx],
            opponent_field=player_field[opponent_idx],
            opponent_hand_size=len(player_hand[opponent_idx]),
            opponent_deck_size=player_deck_size[opponent_idx]
        )

        # AI决策
        current_agent = agent1 if current_player == 0 else agent2
        action = await current_agent.make_decision(context)

        if action:
            logger.info(f"🤖 {current_agent.personality.name} 决策: {action.action_type.value}")
            if hasattr(action, 'reasoning') and action.reasoning:
                logger.info(f"💭 推理: {action.reasoning[:100]}...")

            # 执行动作
            await execute_action(action, current_player, player_health, player_mana,
                              player_hand, player_field, current_agent.personality.name)

        # 战斗阶段
        if player_field[current_player]:
            await combat_phase(current_player, player_health, player_field)

        current_player = 1 - current_player
        if current_player == 0:
            turn_number += 1

        await asyncio.sleep(0.5)

    # 游戏结束
    if player_health[0] <= 0 and player_health[1] <= 0:
        winner = "平局"
        player1_wins = None
    elif player_health[0] > 0 and player_health[1] <= 0:
        winner = f"玩家1 ({agent1.personality.name})"
        player1_wins = True
    elif player_health[1] > 0 and player_health[0] <= 0:
        winner = f"玩家2 ({agent2.personality.name})"
        player1_wins = False
    else:
        # 超过回合数，比较血量
        if player_health[0] > player_health[1]:
            winner = f"玩家1 ({agent1.personality.name})"
            player1_wins = True
        elif player_health[1] > player_health[0]:
            winner = f"玩家2 ({agent2.personality.name})"
            player1_wins = False
        else:
            winner = "平局"
            player1_wins = None

    logger.info(f"\n🏁 游戏结束! {winner}")
    logger.info(f"❤️ 最终血量: 玩家1 {player_health[0]} vs 玩家2 {player_health[1]}")

    # 学习反馈
    if player1_wins is not None:
        result1 = {
            "won": player1_wins,
            "opponent_id": agent2.agent_id,
            "opponent_aggression": agent2.personality.aggression_level,
            "final_health_diff": player_health[0] - player_health[1]
        }

        result2 = {
            "won": not player1_wins,
            "opponent_id": agent1.agent_id,
            "opponent_aggression": agent1.personality.aggression_level,
            "final_health_diff": player_health[1] - player_health[0]
        }

        agent1.learn_from_game(result1)
        agent2.learn_from_game(result2)

        # 显示统计
        stats1 = agent1.get_performance_stats()
        stats2 = agent2.get_performance_stats()

        logger.info(f"📊 {agent1.personality.name}: {stats1['games_played']} 场, 胜率 {stats1['win_rate']:.2f}")
        logger.info(f"📊 {agent2.personality.name}: {stats2['games_played']} 场, 胜率 {stats2['win_rate']:.2f}")


async def execute_action(action, player_idx, player_health, player_mana,
                       player_hand, player_field, player_name):
    """执行AI选择的动作"""
    if not player_hand[player_idx]:
        return

    import random

    if action.action_type.value in ["play_minion", "play_card"] and player_mana[player_idx] >= 2:
        # 出一个随从
        affordable_cards = [card for card in player_hand[player_idx]
                           if card["card_type"] == "minion" and card["cost"] <= player_mana[player_idx]]
        if affordable_cards:
            card = random.choice(affordable_cards)
            player_hand[player_idx].remove(card)
            player_mana[player_idx] -= card["cost"]
            player_field[player_idx].append(card)
            logger.info(f"  ⚔️ {player_name} 打出 {card['name']} ({card['attack']}/{card['health']})")

    elif action.action_type.value == "use_spell" and player_mana[player_idx] >= 2:
        # 使用法术
        affordable_spells = [card for card in player_hand[player_idx]
                            if card["card_type"] == "spell" and card["cost"] <= player_mana[player_idx]]
        if affordable_spells:
            spell = random.choice(affordable_spells)
            player_hand[player_idx].remove(spell)
            player_mana[player_idx] -= spell["cost"]

            opponent_idx = 1 - player_idx
            if spell["attack"] < 0:  # 治疗法术
                player_health[player_idx] = min(30, player_health[player_idx] - spell["attack"])
                logger.info(f"  💚 {player_name} 使用 {spell['name']} 治疗 {-spell['attack']} 点生命")
            else:  # 伤害法术
                player_health[opponent_idx] -= spell["attack"]
                logger.info(f"  🔥 {player_name} 使用 {spell['name']} 造成 {spell['attack']} 点伤害")

    elif action.action_type.value == "use_hero_power" and player_mana[player_idx] >= 2:
        # 使用英雄技能
        player_mana[player_idx] -= 2
        opponent_idx = 1 - player_idx
        damage = 2
        player_health[opponent_idx] -= damage
        logger.info(f"  ⚡ {player_name} 使用英雄技能，造成 {damage} 点伤害")

    else:
        logger.info(f"  🤔 {player_name} 想要 {action.action_type.value}，但无法执行")


async def combat_phase(current_player, player_health, player_field):
    """战斗阶段"""
    opponent_idx = 1 - current_player

    # 如果对方没有随从，直接攻击英雄
    if not player_field[opponent_idx] and player_field[current_player]:
        for minion in player_field[current_player]:
            if minion.get("can_attack", True):  # 简化：假设所有随从都能攻击
                player_health[opponent_idx] -= minion["attack"]
                logger.info(f"  ⚔️ 随从攻击英雄，造成 {minion['attack']} 点伤害")

    # 随从对战（简化版）
    elif player_field[current_player] and player_field[opponent_idx]:
        attacker = random.choice(player_field[current_player])
        defender = random.choice(player_field[opponent_idx])

        # 互相攻击
        defender["health"] -= attacker["attack"]

        if defender.get("mechanics") and "taunt" not in defender["mechanics"]:
            # 如果防御者没有嘲讽，可以攻击英雄
            if random.random() > 0.5:  # 50%概率攻击英雄
                player_health[opponent_idx] -= attacker["attack"]
                logger.info(f"  ⚔️ {attacker['name']} 绕过随从直接攻击英雄")
            else:
                logger.info(f"  ⚔️ {attacker['name']} vs {defender['name']} ({attacker['attack']} vs {defender['health']})")
        else:
            logger.info(f"  ⚔️ {attacker['name']} vs {defender['name']} ({attacker['attack']} vs {defender['health']})")

        # 移除死亡的随从
        if defender["health"] <= 0:
            player_field[opponent_idx].remove(defender)
            logger.info(f"  💀 {defender['name']} 被击败")


async def run_human_vs_ai(args):
    """运行人机对战模式"""
    from ai_engine.strategies.rule_based import RuleBasedStrategy
    from ai_engine.strategies.hybrid import HybridAIStrategy
    from ai_engine.strategies.llm_enhanced import LLMEnhancedStrategy
    from ai_engine.agents.ai_agent import AIAgent
    from ai_engine.llm_integration.base import LLMManager
    from ai_engine.llm_integration.deepseek_client import DeepSeekClient
    from config.settings import get_settings

    # 创建AI策略
    personality_manager = PersonalityManager()
    profile = personality_manager.get_profile(args.personality)

    if args.strategy == "rule_based":
        strategy = RuleBasedStrategy("AI对手")
    elif args.strategy == "hybrid":
        hybrid_config = {
            "strategies": [
                {"name": "rule_based", "weight": 0.6, "min_confidence": 0.3},
                {"name": "llm_enhanced", "weight": 0.4, "min_confidence": 0.5}
            ]
        }
        strategy = HybridAIStrategy("AI对手", hybrid_config)

        # 配置LLM管理器
        try:
            settings = get_settings()
            if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                llm_manager = LLMManager()
                deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                llm_manager.register_client("deepseek", deepseek_client, is_default=True)
                strategy.set_llm_manager(llm_manager)
                logger.info("✅ 混合AI策略已配置LLM功能")
            else:
                logger.warning("⚠️ LLM功能未配置，混合AI将仅使用规则部分")
        except Exception as e:
            logger.warning(f"⚠️ LLM配置失败: {e}")

    elif args.strategy == "llm_enhanced":
        try:
            settings = get_settings()
            if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                llm_manager = LLMManager()
                deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                llm_manager.register_client("deepseek", deepseek_client, is_default=True)

                strategy = LLMEnhancedStrategy("AI对手", {
                    "llm_client": "deepseek",
                    "llm_temperature": 0.3,
                    "llm_weight": 0.8,
                    "rule_weight": 0.2
                })
                strategy.set_llm_manager(llm_manager)
                logger.info("✅ LLM增强策略已配置")
            else:
                logger.warning("⚠️ LLM功能未配置，回退到规则AI")
                strategy = RuleBasedStrategy("AI对手")
        except Exception as e:
            logger.warning(f"⚠️ LLM增强策略配置失败: {e}，回退到规则AI")
            strategy = RuleBasedStrategy("AI对手")
    else:
        strategy = RuleBasedStrategy("AI对手")

    ai_agent = AIAgent("ai_opponent", profile, strategy)

    # 创建游戏
    game = CardGame("玩家", profile.name)

    print(f"\n🎮 人机对战开始!")
    print(f"你的对手: {profile.name} ({args.strategy})")
    print(f"难度级别: {args.difficulty}")
    print("=" * 60)

    # 应用难度配置
    difficulty_config = get_difficulty_config(args.difficulty)

    # 主游戏循环 - 与交互式模式相同，但可以指定多场游戏
    games_played = 0
    player_wins = 0

    while games_played < args.games:
        if games_played > 0:
            print(f"\n🎮 第 {games_played + 1} 场游戏开始!")
            print("=" * 30)

        # 重置游戏状态
        if games_played > 0:
            game = CardGame("玩家", profile.name)

        # 游戏循环
        while not game.game_over:
            current_player = game.get_current_player()

            # 如果是玩家回合
            if current_player.name == "玩家":
                game.display_status()

                # 显示可用命令
                commands = game.get_available_commands()
                print(f"\n📋 可用命令: {', '.join(commands)}")

                try:
                    user_input = input("\n> 请输入命令: ").strip().lower()

                    if user_input in ['quit', 'exit', 'q']:
                        logger.info("👋 游戏已退出")
                        return

                    elif user_input == 'help':
                        print("\n📖 游戏帮助:")
                        print("  help        - 显示帮助信息")
                        print("  status      - 显示当前游戏状态")
                        print("  play <数字>  - 打出指定编号的卡牌")
                        print("  power       - 使用英雄技能 (2费)")
                        print("  end         - 结束回合")
                        print("  quit        - 退出游戏")

                    elif user_input == 'status':
                        game.display_status()

                    elif user_input.startswith('play ') or user_input.startswith('出牌 '):
                        try:
                            # 支持英文和中文命令
                            if user_input.startswith('play '):
                                card_idx = int(user_input.split()[1])
                            else:  # 出牌
                                card_idx = int(user_input.split()[1])
                            result = game.play_card(0, card_idx)
                            if result["success"]:
                                print(f"✅ {result['message']}")
                            else:
                                print(f"❌ {result['message']}")
                        except (IndexError, ValueError):
                            print("❌ 无效的卡牌编号，请使用 '出牌 <数字>' 或 'play <数字>' 格式")

                    elif user_input in ['power', '技能', '英雄技能']:
                        result = game.use_hero_power(0)
                        if result["success"]:
                            print(f"✅ {result['message']}")
                        else:
                            print(f"❌ {result['message']}")

                    elif user_input in ['end', 'end_turn', '结束', '结束回合']:
                        result = game.end_turn(0)
                        if result["success"]:
                            print(f"✅ {result['message']}")
                        else:
                            print(f"❌ {result['message']}")

                    else:
                        print(f"❌ 未知命令: {user_input}")
                        print("输入 'help' 或 '帮助' 查看可用命令")

                except KeyboardInterrupt:
                    logger.info("\n👋 游戏被用户中断")
                    return
                except EOFError:
                    logger.info("\n👋 游戏被用户中断")
                    return

            # 如果是AI回合
            else:
                print(f"\n🤖 {current_player.name} 正在思考...")

                # 根据难度调整思考时间
                thinking_time = random.uniform(*difficulty_config["thinking_time_range"])

                # 创建游戏上下文给AI
                state = game.get_game_state()
                ai_state = state["opponent_state"]

                # 转换AI手牌为AI策略能理解的格式
                ai_hand_for_context = []
                for card in current.hand:
                    ai_hand_for_context.append({
                        "name": get_card_name(card),
                        "cost": safe_get_card_attr(card, 'cost', 0),
                        "attack": get_card_attack(card),
                        "health": get_card_health(card),
                        "card_type": get_card_type(card),
                        "mechanics": safe_get_card_attr(card, 'mechanics', []),
                        "description": safe_get_card_attr(card, 'description', '')
                    })

                context = create_ai_context(game, ai_player_idx=1, game_id=f"human_vs_ai_game_{games_played + 1}")

                # 显示AI分析过程
                print(f"  🧠 分析当前局面...")
                ai_hand = current.hand
                playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]
                print(f"  📋 AI手牌状况: {len(ai_hand)}张手牌，{len(playable_cards)}张可出")

                if playable_cards:
                    card_names = []
                    for i in playable_cards[:3]:
                        card = current.hand[i]
                        card_name = get_card_name(card)
                        card_cost = safe_get_card_attr(card, 'cost', 0)
                        card_names.append(f"{card_name}({card_cost}费)")
                    print(f"  🃏 可出的牌: {', '.join(card_names)}")

                # 模拟思考过程
                await asyncio.sleep(thinking_time / 2)
                print(f"  💭 评估策略选择...")

                await asyncio.sleep(thinking_time / 2)
                print(f"  ⚡ 正在制定最优决策...")

                # AI决策 - 增加超时处理和详细显示
                try:
                    action = await asyncio.wait_for(ai_agent.make_decision(context), timeout=15.0)
                    print(f"  ✅ AI决策完成!")
                except asyncio.TimeoutError:
                    print(f"  ⏰ AI思考超时，使用简化策略...")
                    action = None
                except Exception as e:
                    print(f"  ❌ AI决策出现异常: {str(e)[:50]}...")
                    action = None

                # 根据难度添加随机错误
                if random.random() < difficulty_config["error_rate"]:
                    print("🤖 AI出现失误，选择错误策略")
                    action = None

                if action:
                    # 详细分析AI决策原因
                    decision_reason = ""
                    confidence_info = ""
                    if hasattr(action, 'reasoning') and action.reasoning:
                        decision_reason = f"\n  🧠 思考过程: {action.reasoning[:100]}..."
                    if hasattr(action, 'confidence'):
                        confidence_info = f" (置信度: {action.confidence:.2f})"

                    print(f"\n🤖 {profile.name} 最终决策: {action.action_type.value}{confidence_info}{decision_reason}")

                    # 执行AI动作
                    if action.action_type.value in ["play_minion", "play_card"]:
                        ai_hand = current.hand
                        playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]

                        if playable_cards:
                            # 智能选择卡牌而不是随机选择
                            if hasattr(action, 'parameters') and action.parameters:
                                # 尝试使用AI推荐的卡牌
                                target_card = action.parameters.get('card_index')
                                if target_card is not None and target_card in playable_cards:
                                    card_idx = target_card
                                else:
                                    card_idx = playable_cards[0]  # 选择第一张可出的牌
                            else:
                                card_idx = playable_cards[0]  # 选择第一张可出的牌

                            card = ai_hand[card_idx]
                            result = game.play_card(1, card_idx)
                            # 使用安全的卡牌属性访问
                            card_name = get_card_name(card)
                            card_attack = get_card_attack(card)
                            card_health = get_card_health(card)
                            print(f"  ✅ AI打出: {card_name} ({card_attack}/{card_health}) - {result['message']}")
                        else:
                            print(f"  ❌ AI想出牌，但没有可出的牌")

                    elif action.action_type.value == "use_spell":
                        ai_hand = current.hand
                        spell_cards = [i for i, card in enumerate(ai_hand)
                                     if get_card_type(card) == "spell" and current.can_play_card(card)]
                        if spell_cards:
                            # 智能选择法术牌
                            if hasattr(action, 'parameters') and action.parameters:
                                target_spell = action.parameters.get('card_index')
                                if target_spell is not None and target_spell in spell_cards:
                                    card_idx = target_spell
                                else:
                                    card_idx = spell_cards[0]
                            else:
                                card_idx = spell_cards[0]

                            card = ai_hand[card_idx]
                            result = game.play_card(1, card_idx)
                            # 使用安全的卡牌属性访问
                            card_name = get_card_name(card)
                            card_attack = get_card_attack(card)
                            effect = "造成伤害" if card_attack > 0 else "治疗" if card_attack < 0 else "特殊效果"
                            print(f"  ✅ AI使用法术: {card_name} ({effect}) - {result['message']}")
                        else:
                            print(f"  ❌ AI想使用法术，但没有可用的法术")

                    elif action.action_type.value == "use_hero_power":
                        result = game.use_hero_power(1)
                        if result["success"]:
                            print(f"  ✅ AI使用英雄技能 - {result['message']}")
                        else:
                            print(f"  ❌ AI想使用英雄技能，但法力不足")

                    elif action.action_type.value == "end_turn":
                        # 详细分析AI为什么结束回合
                        ai_hand = current.hand
                        playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]
                        if playable_cards:
                            print(f"  🤔 AI策略性结束回合，可出牌 {len(playable_cards)} 张:")
                            for i in playable_cards[:3]:  # 显示前3张可出的牌
                                card = ai_hand[i]
                                card_name = get_card_name(card)
                                card_cost = safe_get_card_attr(card, 'cost', 0)
                                print(f"    - {card_name} ({card_cost}费)")
                            if len(playable_cards) > 3:
                                print(f"    ... 还有 {len(playable_cards) - 3} 张其他牌")
                            print(f"    💭 策略考虑: 保留资源等待更好时机")
                        else:
                            print(f"  😔 AI没有可出的牌，被迫结束回合")
                    else:
                        print(f"  ❓ AI选择了未知动作: {action.action_type.value}")

                else:
                    print("\n🤖 AI无法做出决策，使用默认策略")
                    # 显示AI手牌情况
                    ai_hand = current.hand
                    playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]
                    print(f"  📋 AI当前手牌: {len(ai_hand)}张，可出: {len(playable_cards)}张")

                    if playable_cards:
                        print(f"  🎯 自动选择最优卡牌...")
                        # 选择最优卡牌（简单策略：选择费用最高的）
                        best_card_idx = max(playable_cards, key=lambda i: safe_get_card_attr(ai_hand[i], 'cost', 0))
                        card = ai_hand[best_card_idx]
                        result = game.play_card(1, best_card_idx)
                        card_name = get_card_name(card)
                        card_attack = get_card_attack(card)
                        card_health = get_card_health(card)
                        print(f"  ✅ 自动打出: {card_name} ({card_attack}/{card_health}) - {result['message']}")
                    else:
                        print(f"  ⏭️ 无牌可出，跳过回合")

                # AI结束回合
                await asyncio.sleep(0.5)
                result = game.end_turn(1)
                print(f"✅ {result['message']}")

        # 游戏结束处理
        if game.game_over:
            games_played += 1
            print(f"\n🏁 第 {games_played} 场游戏结束! {game.winner}")
            print("=" * 30)

            # 统计胜负
            if game.winner == "玩家":
                player_wins += 1

            # 显示最终统计
            final_state = game.get_game_state()
            print(f"最终生命值: 玩家 {final_state['current_player_state']['health']} vs AI {final_state['opponent_state']['health']}")
            print(f"总回合数: {game.turn_number}")

            # AI学习
            if game.winner != "平局":
                result = {
                    "won": game.winner == profile.name,
                    "opponent_id": "player",
                    "opponent_aggression": 0.5,
                    "final_health_diff": final_state['opponent_state']['health'] - final_state['current_player_state']['health']
                }
                ai_agent.learn_from_game(result)

            # 显示战绩
            print(f"\n📊 当前战绩: 玩家 {player_wins} - {games_played - player_wins} AI")

            if games_played < args.games:
                print("准备下一场游戏...")
                await asyncio.sleep(2)

    # 显示最终结果
    print(f"\n🏆 比赛结束!")
    print(f"最终战绩: 玩家 {player_wins} - {args.games - player_wins} AI")
    print(f"胜率: {player_wins/args.games*100:.1f}%")
    print("=" * 60)


async def run_interactive_mode(args):
    """运行真正的交互式模式"""
    from ai_engine.strategies.rule_based import RuleBasedStrategy
    from ai_engine.agents.ai_agent import AIAgent

    logger.info("🎯 交互式模式 - 玩家 vs AI")
    logger.info("输入 'help' 查看可用命令")

    # 创建AI对手
    personality_manager = PersonalityManager()
    profile = personality_manager.get_profile(args.personality)
    strategy = RuleBasedStrategy("AI对手")
    ai_agent = AIAgent("ai_opponent", profile, strategy)

    # 创建游戏
    game = CardGame("玩家", profile.name)

    print(f"\n🎮 游戏开始! 你的对手是: {profile.name}")
    print("=" * 50)

    # 主游戏循环
    while not game.game_over:
        current_player = game.get_current_player()

        # 如果是玩家回合
        if current_player.name == "玩家":
            game.display_status()

            # 显示可用命令
            commands = game.get_available_commands()
            print(f"\n📋 可用命令: {', '.join(commands)}")

            try:
                user_input = input("\n> 请输入命令: ").strip().lower()

                if user_input in ['quit', 'exit', 'q']:
                    logger.info("👋 游戏已退出")
                    break

                elif user_input == 'help':
                    print("\n📖 游戏帮助:")
                    print("  help        - 显示帮助信息")
                    print("  status      - 显示当前游戏状态")
                    print("  play <数字>  - 打出指定编号的卡牌")
                    print("  power       - 使用英雄技能 (2费)")
                    print("  end         - 结束回合")
                    print("  quit        - 退出游戏")

                elif user_input == 'status':
                    game.display_status()

                elif user_input.startswith('play '):
                    try:
                        card_idx = int(user_input.split()[1])
                        result = game.play_card(0, card_idx)
                        if result["success"]:
                            print(f"✅ {result['message']}")
                        else:
                            print(f"❌ {result['message']}")
                    except (IndexError, ValueError):
                        print("❌ 无效的卡牌编号，请使用 'play <数字>' 格式")

                elif user_input == 'power':
                    result = game.use_hero_power(0)
                    if result["success"]:
                        print(f"✅ {result['message']}")
                    else:
                        print(f"❌ {result['message']}")

                elif user_input in ['end', 'end_turn']:
                    result = game.end_turn(0)
                    if result["success"]:
                        print(f"✅ {result['message']}")
                    else:
                        print(f"❌ {result['message']}")

                else:
                    print(f"❌ 未知命令: {user_input}")
                    print("输入 'help' 查看可用命令")

            except KeyboardInterrupt:
                logger.info("\n👋 游戏被用户中断")
                break
            except EOFError:
                logger.info("\n👋 游戏被用户中断")
                break

        # 如果是AI回合
        else:
            print(f"\n🤖 {current_player.name} 正在思考...")
            await asyncio.sleep(1)  # 模拟思考时间

            # 创建游戏上下文给AI
            state = game.get_game_state()
            ai_state = state["opponent_state"]  # AI的视角

            context = create_ai_context(game, ai_player_idx=1, game_id="interactive_game")

            # AI决策
            action = await ai_agent.make_decision(context)

            if action:
                # 分析AI决策原因
                decision_reason = ""
                if hasattr(action, 'reasoning') and action.reasoning:
                    decision_reason = f" - {action.reasoning[:80]}..."

                print(f"🤖 {profile.name} 决策: {action.action_type.value}{decision_reason}")

                # 执行AI动作
                if action.action_type.value in ["play_minion", "play_card"]:
                    ai_hand = current.hand
                    playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]

                    if playable_cards:
                        card_idx = random.choice(playable_cards)
                        card = ai_hand[card_idx]
                        result = game.play_card(1, card_idx)
                        # 使用安全的卡牌属性访问
                        card_name = get_card_name(card)
                        card_attack = get_card_attack(card)
                        card_health = get_card_health(card)
                        print(f"  ✅ AI打出: {card_name} ({card_attack}/{card_health}) - {result['message']}")
                    else:
                        print(f"  ❌ AI想出牌，但没有可出的牌")

                elif action.action_type.value == "use_spell":
                    ai_hand = current.hand
                    spell_cards = [i for i, card in enumerate(ai_hand)
                                 if get_card_type(card) == "spell" and current.can_play_card(card)]
                    if spell_cards:
                        card_idx = random.choice(spell_cards)
                        card = ai_hand[card_idx]
                        result = game.play_card(1, card_idx)
                        # 使用安全的卡牌属性访问
                        card_name = get_card_name(card)
                        card_attack = get_card_attack(card)
                        effect = "造成伤害" if card_attack > 0 else "治疗" if card_attack < 0 else "特殊效果"
                        print(f"  ✅ AI使用法术: {card_name} ({effect}) - {result['message']}")
                    else:
                        print(f"  ❌ AI想使用法术，但没有可用的法术")

                elif action.action_type.value == "use_hero_power":
                    result = game.use_hero_power(1)
                    if result["success"]:
                        print(f"  ✅ AI使用英雄技能 - {result['message']}")
                    else:
                        print(f"  ❌ AI想使用英雄技能，但法力不足")

                elif action.action_type.value == "end_turn":
                    # 分析AI为什么结束回合
                    ai_hand = current.hand
                    playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]
                    if playable_cards:
                        print(f"  🤔 AI选择结束回合，虽然有 {len(playable_cards)} 张可出的牌")
                    else:
                        print(f"  😔 AI没有可出的牌，选择结束回合")
                else:
                    print(f"  ❓ AI选择了未知动作: {action.action_type.value}")

            else:
                print("🤖 AI无法做出决策，跳过回合")
                # 显示AI手牌情况
                ai_hand = current.hand
                playable_cards = [i for i, card in enumerate(ai_hand) if current.can_play_card(card)]
                print(f"  📋 AI当前手牌: {len(ai_hand)}张，可出: {len(playable_cards)}张")

            # AI结束回合
            await asyncio.sleep(0.5)
            result = game.end_turn(1)
            print(f"✅ {result['message']}")

    # 游戏结束
    if game.game_over:
        print(f"\n🏁 游戏结束! {game.winner}")
        print("=" * 50)

        # 显示最终统计
        final_state = game.get_game_state()
        print(f"最终生命值: 玩家 {final_state['current_player_state']['health']} vs AI {final_state['opponent_state']['health']}")
        print(f"总回合数: {game.turn_number}")

        # 显示AI统计
        stats = ai_agent.get_performance_stats()
        print(f"AI统计: {stats['games_played']} 场游戏")


async def run_benchmark(args):
    """运行性能基准测试"""
    logger.info("🚀 性能基准测试")

    # 创建测试用的AI引擎
    config = AIEngineConfig(enable_monitoring=True)
    engine = AIEngine(config)

    # 用于存储需要清理的资源
    llm_manager = None
    deepseek_client = None

    try:
        # 测试不同策略的性能
        strategies = ["rule_based", "hybrid"]

        for strategy in strategies:
            logger.info(f"\n📊 测试策略: {strategy}")

            if strategy == "hybrid":
                hybrid_config = {
                    "strategies": [
                        {"name": "rule_based", "weight": 0.6, "min_confidence": 0.3},
                        {"name": "llm_enhanced", "weight": 0.4, "min_confidence": 0.5}
                    ]
                }
                from ai_engine.strategies.hybrid import HybridAIStrategy
                hybrid_strategy = HybridAIStrategy("benchmark_hybrid", hybrid_config)

                # 尝试配置LLM管理器
                try:
                    from ai_engine.llm_integration.base import LLMManager
                    from ai_engine.llm_integration.deepseek_client import DeepSeekClient
                    from config.settings import get_settings

                    settings = get_settings()
                    if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                        llm_manager = LLMManager()
                        deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                        llm_manager.register_client("deepseek", deepseek_client, is_default=True)
                        hybrid_strategy.set_llm_manager(llm_manager)
                        logger.info("✅ Benchmark混合策略已配置LLM功能")
                    else:
                        logger.info("ℹ️ Benchmark混合策略未配置LLM，仅使用规则部分")
                except Exception as e:
                    logger.info(f"ℹ️ Benchmark LLM配置失败: {e}，仅使用规则部分")

                engine.register_strategy("hybrid", hybrid_strategy)

            engine.set_strategy(strategy)

            # 创建测试上下文
            context = GameContext(
                game_id="benchmark",
                current_player=0,
                turn_number=5,
                phase="main",

                player_health=25,
                player_max_health=30,
                player_mana=6,
                player_max_mana=6,
                player_hand=ai_state.get("hand", []),
                player_field=[],
                player_deck_size=15,

                opponent_health=20,
                opponent_max_health=30,
                opponent_mana=4,
                opponent_max_mana=4,
                opponent_field=[],
                opponent_hand_size=4,
                opponent_deck_size=17
            )

            # 执行多次测试
            test_count = 10
            total_time = 0
            success_count = 0

            for i in range(test_count):
                start_time = asyncio.get_event_loop().time()
                action = await engine.make_decision(context)
                end_time = asyncio.get_event_loop().time()

                if action:
                    success_count += 1
                    total_time += end_time - start_time

            # 计算统计结果
            avg_time = total_time / max(1, success_count)
            success_rate = success_count / test_count

            logger.info(f"  成功率: {success_rate:.2f}")
            logger.info(f"  平均响应时间: {avg_time:.3f}秒")
            logger.info(f"  总测试次数: {test_count}")

            # 获取详细统计
            if strategy in ["rule_based", "hybrid"]:
                stats = engine.get_strategy_performance(strategy)
                if stats:
                    logger.info(f"  引擎统计: 成功率 {stats['success_rate']:.2f}, "
                              f"平均时间 {stats['average_decision_time']:.3f}s")

    finally:
        # 清理资源
        if deepseek_client:
            try:
                await deepseek_client.close()
                logger.info("✅ Benchmark DeepSeek客户端已关闭")
            except Exception as e:
                logger.warning(f"⚠️ 关闭DeepSeek客户端时出错: {e}")

        if llm_manager:
            try:
                # 清理LLM管理器中的会话
                if hasattr(llm_manager, 'clients'):
                    for client in llm_manager.clients.values():
                        if hasattr(client, 'close'):
                            await client.close()
                logger.info("✅ Benchmark LLM管理器已清理")
            except Exception as e:
                logger.warning(f"⚠️ 清理LLM管理器时出错: {e}")


async def run_demo_command(args):
    """运行演示命令"""
    logger.info("🎭 运行AI功能演示")
    await demo_main()


async def run_play_command(args):
    """运行游戏命令"""
    if args.mode == "menu":
        await run_menu_mode()
    elif args.mode == "ai-vs-ai":
        logger.info(f"🤖 AI对战模式 - {args.strategy} vs {args.strategy}")
        logger.info(f"🎮 玩家1人格: {args.personality}")
        await run_ai_vs_ai(args)
    elif args.mode == "human-vs-ai":
        logger.info(f"👥 人机对战模式 - 玩家 vs AI ({args.strategy})")
        logger.info(f"🎮 AI对手: {args.personality}")
        await run_human_vs_ai(args)
    elif args.mode == "ai-vs-human":
        logger.info("👥 AI对人模式 (开发中，与human-vs-ai相同)")
        logger.info("当前使用与human-vs-ai相同的实现")
        await run_human_vs_ai(args)
    elif args.mode == "interactive":
        logger.info("🎯 交互式模式")
        logger.info(f"🤖 AI对手: {args.personality}")
        await run_interactive_mode(args)


async def run_menu_mode():
    """运行炫酷菜单模式"""
    ui = GameUI()

    # 显示欢迎动画
    ui.show_welcome_animation()

    while True:
        choice = ui.show_main_menu()

        if choice == "quit":
            break
        elif choice["mode"] == "human_vs_ai":
            await run_menu_human_vs_ai(choice, ui)
        elif choice["mode"] == "ai_vs_ai":
            await run_menu_ai_vs_ai(choice, ui)
        elif choice["mode"] == "interactive":
            await run_menu_interactive(choice, ui)
        elif choice["mode"] == "test":
            await run_menu_test(choice, ui)
        elif choice["mode"] == "benchmark":
            await run_menu_benchmark(choice, ui)


async def run_menu_human_vs_ai(choice: dict, ui: GameUI):
    """菜单模式下的人机对战"""
    # 创建AI策略
    personality_manager = PersonalityManager()
    profile = personality_manager.get_profile("adaptive_learner")

    strategy_type = choice.get("strategy", "hybrid")
    if strategy_type == "rule_based":
        strategy = RuleBasedStrategy("AI对手")
    else:
        hybrid_config = {
            "strategies": [
                {"name": "rule_based", "weight": 0.6, "min_confidence": 0.3},
                {"name": "llm_enhanced", "weight": 0.4, "min_confidence": 0.5}
            ]
        }
        strategy = HybridAIStrategy("AI对手", hybrid_config)

        # 配置LLM管理器
        try:
            from ai_engine.llm_integration.base import LLMManager
            from ai_engine.llm_integration.deepseek_client import DeepSeekClient
            from config.settings import get_settings

            settings = get_settings()
            if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                llm_manager = LLMManager()
                deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                llm_manager.register_client("deepseek", deepseek_client, is_default=True)
                strategy.set_llm_manager(llm_manager)
        except Exception:
            pass

    ai_agent = AIAgent("ai_opponent", profile, strategy)

    # 创建游戏
    game = CardGame("玩家", profile.name)

    # 应用难度配置
    difficulty_config = get_difficulty_config(choice.get("difficulty", "normal"))

    # 主游戏循环
    games_played = 0
    player_wins = 0
    total_games = choice.get("games", 1)

    while games_played < total_games:
        if games_played > 0:
            ui.console.clear()
            ui.console.print(Panel(
                f"[bold cyan]第 {games_played + 1} 场游戏开始！[/bold cyan]",
                box=box.DOUBLE,
                border_style="cyan"
            ))
            await asyncio.sleep(1)

        # 重置游戏状态
        if games_played > 0:
            game = CardGame("玩家", profile.name)

        # 游戏循环
        while not game.game_over:
            current_player = game.get_current_player()

            # 如果是玩家回合
            if current_player.name == "玩家":
                game.display_status(use_rich=True)

                # 显示可用命令
                commands = game.get_available_commands()

                # 使用简化的交互方式
                from rich.prompt import Prompt
                try:
                    user_input = Prompt.ask(
                        "\n[bold green]请输入操作 (数字/命令)[/bold green]",
                        default="",
                        show_default=False
                    ).strip()

                    # 空输入或空格/回车 = 结束回合
                    if not user_input or user_input in ['', ' ', '\n', '\r']:
                        result = game.end_turn(0, auto_attack=True)  # 启用自动攻击
                        ui.console.print(f"✅ {result['message']}", style="green")
                        continue

                    user_input_lower = user_input.lower()

                    # 退出游戏
                    if user_input_lower in ['退出', 'quit', 'exit', 'q']:
                        return

                    # 帮助 - 使用智能上下文帮助
                    elif user_input_lower in ['帮助', '帮', 'help', 'h']:
                        # 使用游戏提供的上下文帮助
                        context_help = game.get_context_help()
                        ui.console.print(context_help)
                        continue

                    # 查看状态
                    elif user_input_lower in ['状态', 'status']:
                        game.display_status(use_rich=True)
                        continue

                    # 简化出牌 - 直接输入数字
                    elif user_input.isdigit():
                        card_idx = int(user_input)
                        if card_idx < len(current_player.hand):
                            result = game.quick_play_card(0, card_idx)
                            ui.console.print(
                                f"✅ {result['message']}" if result["success"]
                                else f"❌ {result['message']}",
                                style="green" if result["success"] else "red"
                            )
                        else:
                            ui.console.print("❌ 无效的卡牌编号", style="red")
                        continue

                    # 完整出牌命令
                    elif user_input_lower.startswith('出牌 ') or user_input_lower.startswith('play '):
                        try:
                            card_idx = int(user_input.split()[1])
                            result = game.quick_play_card(0, card_idx)
                            ui.console.print(
                                f"✅ {result['message']}" if result["success"]
                                else f"❌ {result['message']}",
                                style="green" if result["success"] else "red"
                            )
                        except (IndexError, ValueError):
                            ui.console.print("❌ 无效的卡牌编号，请使用 '出牌 <编号>' 格式", style="red")
                        continue

                    # 英雄技能
                    elif user_input_lower in ['英雄技能', '技能', '技', 'power']:
                        result = game.use_hero_power(0)
                        ui.console.print(
                            f"✅ {result['message']}" if result["success"]
                            else f"❌ {result['message']}",
                            style="green" if result["success"] else "red"
                        )
                        continue

                    # 随从攻击
                    elif user_input_lower.startswith('随从攻击 ') or user_input_lower.startswith('attack '):
                        parts = user_input.split()
                        if len(parts) >= 3:
                            try:
                                minion_idx = int(parts[1])
                                target = parts[2]
                                result = game.attack_with_minion(0, minion_idx, target)
                                ui.console.print(
                                    f"✅ {result['message']}" if result["success"]
                                    else f"❌ {result['message']}",
                                    style="green" if result["success"] else "red"
                                )
                            except (IndexError, ValueError):
                                ui.console.print("❌ 无效的随从编号", style="red")
                        else:
                            # 显示可攻击的随从和目标
                            attackable = []
                            for i, minion in enumerate(current_player.field):
                                if getattr(minion, 'can_attack', False):
                                    targets = game.get_minion_attack_targets(0, i)
                                    if targets:
                                        attackable.append(f"随从{i}: {get_card_name(minion)} -> {', '.join(targets)}")

                            if attackable:
                                ui.console.print("📋 [yellow]可攻击的随从:[/yellow]", style="yellow")
                                for info in attackable:
                                    ui.console.print(f"  • {info}", style="white")
                            else:
                                ui.console.print("❌ 当前没有可以攻击的随从", style="red")
                        continue

                    # 英雄攻击
                    elif user_input_lower in ['英雄攻击', 'hero']:
                        result = game.attack_with_hero(0)
                        ui.console.print(
                            f"✅ {result['message']}" if result["success"]
                            else f"❌ {result['message']}",
                            style="green" if result["success"] else "red"
                        )
                        continue

                    # 手动结束回合
                    elif user_input_lower in ['结束回合', '结束', 'end']:
                        result = game.end_turn(0, auto_attack=False)  # 不自动攻击
                        ui.console.print(f"✅ {result['message']}", style="green")

                    else:
                        ui.console.print(f"❌ 未知命令: {user_input}", style="red")
                        ui.console.print("💡 输入 '帮助' 查看可用操作", style="dim")

                except KeyboardInterrupt:
                    ui.console.print("\n👋 游戏被用户中断", style="yellow")
                    return

            # 如果是AI回合
            else:
                ui.console.print(f"\n🤖 {current_player.name} 正在思考...", style="blue")
                ui.show_ai_thinking(current_player.name, 2)

                # 创建游戏上下文给AI
                state = game.get_game_state()
                ai_state = state["opponent_state"]

                context = create_ai_context(game, ai_player_idx=1, game_id=f"menu_game_{games_played + 1}")

                # AI决策
                action = await ai_agent.make_decision(context)

                # 根据难度添加随机错误
                if random.random() < difficulty_config["error_rate"]:
                    ui.console.print("🤖 AI出现失误，选择错误策略", style="yellow")
                    action = None

                if action:
                    # 分析AI决策原因
                    decision_reason = ""
                    if hasattr(action, 'reasoning') and action.reasoning:
                        decision_reason = f" - {action.reasoning[:80]}..."

                    ui.console.print(f"🤖 {profile.name} 决策: {action.action_type.value}{decision_reason}", style="cyan")

                    # 执行AI动作
                    if action.action_type.value in ["play_minion", "play_card"]:
                        ai_hand = current_player.hand
                        playable_cards = [i for i, card in enumerate(ai_hand) if current_player.can_play_card(card)]

                        if playable_cards:
                            card_idx = random.choice(playable_cards)
                            card = ai_hand[card_idx]
                            result = game.play_card(1, card_idx)
                            # 使用安全的卡牌属性访问
                            card_name = get_card_name(card)
                            card_attack = get_card_attack(card)
                            card_health = get_card_health(card)
                            ui.console.print(f"  ✅ AI打出: {card_name} ({card_attack}/{card_health}) - {result['message']}", style="green")
                        else:
                            ui.console.print("  ❌ AI想出牌，但没有可出的牌", style="red")

                    elif action.action_type.value == "use_spell":
                        ai_hand = current_player.hand
                        spell_cards = [i for i, card in enumerate(ai_hand)
                                     if card.card_type == "spell" and current_player.can_play_card(card)]
                        if spell_cards:
                            card_idx = random.choice(spell_cards)
                            card = ai_hand[card_idx]
                            result = game.play_card(1, card_idx)
                            # 使用安全的卡牌属性访问
                            card_name = get_card_name(card)
                            card_attack = get_card_attack(card)
                            effect = "造成伤害" if card_attack > 0 else "治疗" if card_attack < 0 else "特殊效果"
                            ui.console.print(f"  ✅ AI使用法术: {card_name} ({effect}) - {result['message']}", style="green")
                        else:
                            ui.console.print("  ❌ AI想使用法术，但没有可用的法术", style="red")

                    elif action.action_type.value == "use_hero_power":
                        result = game.use_hero_power(1)
                        if result["success"]:
                            ui.console.print(f"  ✅ AI使用英雄技能 - {result['message']}", style="green")
                        else:
                            ui.console.print("  ❌ AI想使用英雄技能，但法力不足", style="red")

                    elif action.action_type.value == "end_turn":
                        # 分析AI为什么结束回合
                        ai_hand = current_player.hand
                        playable_cards = [i for i, card in enumerate(ai_hand) if current_player.can_play_card(card)]
                        if playable_cards:
                            ui.console.print(f"  🤔 AI选择结束回合，虽然有 {len(playable_cards)} 张可出的牌", style="yellow")
                        else:
                            ui.console.print("  😔 AI没有可出的牌，选择结束回合", style="dim")
                    else:
                        ui.console.print(f"  ❓ AI选择了未知动作: {action.action_type.value}", style="red")

                else:
                    ui.console.print("🤖 AI无法做出决策，跳过回合", style="yellow")
                    # 显示AI手牌情况
                    ai_hand = current_player.hand
                    playable_cards = [i for i, card in enumerate(ai_hand) if current_player.can_play_card(card)]
                    ui.console.print(f"  📋 AI当前手牌: {len(ai_hand)}张，可出: {len(playable_cards)}张", style="dim")

                # AI结束回合
                await asyncio.sleep(0.5)
                result = game.end_turn(1)
                ui.console.print(f"✅ {result['message']}", style="green")

        # 游戏结束处理
        if game.game_over:
            games_played += 1
            ui.show_game_result(game.winner, {
                "游戏局数": games_played,
                "总局数": total_games,
                "最终回合数": game.turn_number
            })

            # 统计胜负
            if game.winner == "玩家":
                player_wins += 1

            # AI学习
            if game.winner != "平局":
                result = {
                    "won": game.winner == profile.name,
                    "opponent_id": "player",
                    "opponent_aggression": 0.5,
                    "final_health_diff": state['opponent_state']['health'] - state['current_player_state']['health']
                }
                ai_agent.learn_from_game(result)

            # 显示战绩
            ui.console.print(f"\n📊 当前战绩: 玩家 {player_wins} - {games_played - player_wins} AI", style="bold cyan")

            if games_played < total_games:
                from rich.prompt import Confirm
                if Confirm.ask("准备下一场游戏？", default=True):
                    await asyncio.sleep(2)
                else:
                    break

    # 显示最终结果
    ui.show_game_result(f"玩家 {player_wins} - {total_games - player_wins} AI", {
        "总游戏局数": total_games,
        "玩家胜利": player_wins,
        "AI胜利": total_games - player_wins,
        "玩家胜率": f"{player_wins/total_games*100:.1f}%"
    })


async def run_menu_ai_vs_ai(choice: dict, ui: GameUI):
    """菜单模式下的AI对战"""
    games = choice.get("games", 3)

    ui.console.print(Panel(
        f"[bold cyan]🤖 AI对战模式[/bold cyan]\n"
        f"[dim]观看智能AI之间的精彩对决！[/dim]\n"
        f"[blue]对战场次: {games}[/blue]",
        box=box.DOUBLE,
        border_style="cyan"
    ))

    # 创建AI代理
    personality_manager = PersonalityManager()

    # 获取两个人格
    profile1 = personality_manager.get_profile("adaptive_learner")
    profile2 = personality_manager.get_random_profile()

    # 创建AI策略
    from ai_engine.strategies.rule_based import RuleBasedStrategy
    from ai_engine.strategies.hybrid import HybridAIStrategy

    hybrid_config = {
        "strategies": [
            {"name": "rule_based", "weight": 0.7, "min_confidence": 0.3},
            {"name": "llm_enhanced", "weight": 0.3, "min_confidence": 0.5}
        ]
    }

    strategy1 = HybridAIStrategy("AI玩家1", hybrid_config)
    strategy2 = RuleBasedStrategy("AI玩家2")  # 简化，使用规则AI避免超时问题

    # 尝试配置LLM
    try:
        from ai_engine.llm_integration.base import LLMManager
        from ai_engine.llm_integration.deepseek_client import DeepSeekClient
        from config.settings import get_settings

        settings = get_settings()
        if settings.ai.enable_llm and settings.ai.deepseek_api_key:
            llm_manager = LLMManager()
            deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
            llm_manager.register_client("deepseek", deepseek_client, is_default=True)
            strategy1.set_llm_manager(llm_manager)
    except Exception:
        pass

    # 创建AI代理
    agent1 = AIAgent("ai_player_1", profile1, strategy1)
    agent2 = AIAgent("ai_player_2", profile2, strategy2)

    ui.console.print(f"\n🎮 [bold green]对战选手[/bold green]:")
    ui.console.print(f"  🔵 {profile1.name} (混合AI)")
    ui.console.print(f"  🟠 {profile2.name} (规则AI)")

    # 运行多场对战
    player1_wins = 0
    player2_wins = 0
    draws = 0

    for game_num in range(1, games + 1):
        ui.console.print(f"\n{'='*60}")
        ui.console.print(Panel(
            f"[bold yellow]第 {game_num} 场对战开始[/bold yellow]",
            box=box.ROUNDED,
            border_style="yellow"
        ))

        # 模拟游戏
        winner = await simulate_ai_vs_ai_game(agent1, agent2, game_num, ui)

        if winner == 1:
            player1_wins += 1
            ui.console.print(f"🏆 [green]{profile1.name} 获胜！[/green]")
        elif winner == 2:
            player2_wins += 1
            ui.console.print(f"🏆 [green]{profile2.name} 获胜！[/green]")
        else:
            draws += 1
            ui.console.print(f"🤝 [yellow]平局！[/yellow]")

        if game_num < games:
            ui.console.print("\n⏳ 准备下一场对战...")
            await asyncio.sleep(2)

    # 显示最终统计
    ui.console.print(f"\n{'='*60}")
    ui.console.print(Panel(
        f"[bold magenta]🏆 对战统计[/bold magenta]\n\n"
        f"🔵 {profile1.name}: {player1_wins} 胜\n"
        f"🟠 {profile2.name}: {player2_wins} 胜\n"
        f"🤝 平局: {draws} 场\n\n"
        f"[bold]总胜率:[/bold] {profile1.name} {player1_wins/games*100:.1f}% vs {profile2.name} {player2_wins/games*100:.1f}%",
        box=box.DOUBLE,
        border_style="magenta"
    ))


async def simulate_ai_vs_ai_game(agent1: AIAgent, agent2: AIAgent, game_num: int, ui: GameUI) -> int:
    """模拟AI对战游戏"""
    import random

    # 初始化游戏状态
    player_health = [30, 30]
    player_mana = [1, 1]
    player_max_mana = [1, 1]
    player_field = [[], []]
    player_hand = [[], []]
    player_deck_size = [20, 20]

    # 创建卡牌池
    def create_card(name, cost, attack, health, card_type="minion", mechanics=None):
        return {
            "name": name,
            "cost": cost,
            "attack": attack,
            "health": health,
            "card_type": card_type,
            "mechanics": mechanics or [],
            "instance_id": f"card_{random.randint(1000, 9999)}"
        }

    card_pool = [
        create_card("烈焰元素", 3, 5, 3, "minion", []),
        create_card("霜狼步兵", 2, 2, 3, "minion", ["taunt"]),
        create_card("铁喙猫头鹰", 3, 2, 2, "minion", ["taunt"]),
        create_card("狼人渗透者", 2, 3, 2, "minion", ["stealth"]),
        create_card("石像鬼", 1, 1, 1, "minion", ["divine_shield"]),
        create_card("火球术", 4, 6, 0, "spell", []),
        create_card("闪电箭", 1, 3, 0, "spell", []),
        create_card("治愈术", 2, -5, 0, "spell", []),
        create_card("狂野之怒", 1, 3, 0, "spell", []),
        create_card("奥术智慧", 3, 0, 0, "spell", ["draw_cards"]),
    ]

    # 初始手牌
    for player_idx in range(2):
        for _ in range(3):
            if player_deck_size[player_idx] > 0:
                card = random.choice(card_pool).copy()
                player_hand[player_idx].append(card)
                player_deck_size[player_idx] -= 1

    # 游戏主循环
    current_player = 0
    turn_number = 1
    max_turns = 8  # 限制回合数，避免游戏过长

    while turn_number <= max_turns and player_health[0] > 0 and player_health[1] > 0:
        # 显示回合信息
        current_agent = agent1 if current_player == 0 else agent2
        opponent_agent = agent2 if current_player == 0 else agent1

        ui.console.print(f"\n[bold blue]回合 {turn_number} - {current_agent.personality.name} 回合[/bold blue]")

        # 回合开始
        if player_max_mana[current_player] < 10:
            player_max_mana[current_player] += 1
        player_mana[current_player] = player_max_mana[current_player]

        # 抽牌
        if player_deck_size[current_player] > 0 and len(player_hand[current_player]) < 10:
            card = random.choice(card_pool).copy()
            player_hand[current_player].append(card)
            player_deck_size[current_player] -= 1
            ui.console.print(f"🃏 {current_agent.personality.name} 抽取了 {card['name']}")

        # 显示状态摘要
        ui.console.print(f"💰 法力: {player_mana[current_player]}/{player_max_mana[current_player]} | "
                         f"❤️ 生命: {player_health[0]} vs {player_health[1]} | "
                         f"⚔️ 场面: {len(player_field[0])} vs {len(player_field[1])} 随从")

        # 创建游戏上下文
        opponent_idx = 1 - current_player
        context = GameContext(
            game_id=f"ai_vs_ai_game_{game_num}_turn_{turn_number}",
            current_player=current_player,
            turn_number=turn_number,
            phase="main",

            player_health=player_health[current_player],
            player_max_health=30,
            player_mana=player_mana[current_player],
            player_max_mana=player_max_mana[current_player],
            player_hand=player_hand[current_player],
            player_field=player_field[current_player],
            player_deck_size=player_deck_size[current_player],

            opponent_health=player_health[opponent_idx],
            opponent_max_health=30,
            opponent_mana=player_mana[opponent_idx],
            opponent_max_mana=player_max_mana[opponent_idx],
            opponent_field=player_field[opponent_idx],
            opponent_hand_size=len(player_hand[opponent_idx]),
            opponent_deck_size=player_deck_size[opponent_idx]
        )

        # AI决策
        ui.console.print(f"🤖 {current_agent.personality.name} 正在思考...")

        try:
            # 为AI对战模式设置更长的超时时间
            action = await asyncio.wait_for(current_agent.make_decision(context), timeout=30.0)
        except asyncio.TimeoutError:
            ui.console.print(f"⏰ {current_agent.personality.name} 思考超时，跳过回合")
            action = None

        if action:
            ui.console.print(f"💭 {current_agent.personality.name} 决策: {action.action_type.value}")

            # 执行AI动作
            await execute_ai_action(action, current_player, player_health, player_mana,
                                  player_hand, player_field, current_agent.personality.name, ui)

            # 战斗阶段
            if player_field[current_player]:
                await ai_combat_phase(current_player, player_health, player_field, ui)
        else:
            ui.console.print(f"😔 {current_agent.personality.name} 无法做出决策")

        current_player = 1 - current_player
        if current_player == 0:
            turn_number += 1

        await asyncio.sleep(1)  # 短暂暂停让用户看清过程

    # 判断胜负
    if player_health[0] <= 0 and player_health[1] <= 0:
        return 0  # 平局
    elif player_health[0] > 0 and player_health[1] <= 0:
        return 1  # 玩家1胜
    elif player_health[1] > 0 and player_health[0] <= 0:
        return 2  # 玩家2胜
    else:
        # 超过回合数，比较血量
        if player_health[0] > player_health[1]:
            return 1
        elif player_health[1] > player_health[0]:
            return 2
        else:
            return 0


# 旧的execute_ai_action函数已被新的版本替换
# 新版本在第131行，使用更现代的参数和游戏对象


async def ai_combat_phase(current_player, player_health, player_field, ui: GameUI):
    """AI战斗阶段"""
    opponent_idx = 1 - current_player

    # 如果对方没有随从，直接攻击英雄
    if not player_field[opponent_idx] and player_field[current_player]:
        for minion in player_field[current_player]:
            if random.random() > 0.3:  # 70%概率攻击
                player_health[opponent_idx] -= minion["attack"]
                ui.console.print(f"  ⚔️ {minion['name']} 攻击英雄，造成 {minion['attack']} 点伤害")

    # 随从对战（简化版）
    elif player_field[current_player] and player_field[opponent_idx]:
        attacker = random.choice(player_field[current_player])
        defender = random.choice(player_field[opponent_idx])

        # 互相攻击
        defender["health"] -= attacker["attack"]
        ui.console.print(f"  ⚔️ {attacker['name']} vs {defender['name']} ({attacker['attack']} vs {defender['health']})")

        # 移除死亡的随从
        if defender["health"] <= 0:
            player_field[opponent_idx].remove(defender)
            ui.console.print(f"  💀 {defender['name']} 被击败")


async def run_menu_interactive(choice: dict, ui: GameUI):
    """菜单模式下的交互模式"""
    ui.console.print(Panel(
        f"[bold cyan]🎯 交互模式[/bold cyan]\n"
        f"[dim]自由探索游戏功能，无压力游戏！[/dim]",
        box=box.DOUBLE,
        border_style="cyan"
    ))

    # 创建AI对手
    personality_manager = PersonalityManager()
    profile = personality_manager.get_profile("adaptive_learner")

    # 创建简单的规则AI
    from ai_engine.strategies.rule_based import RuleBasedStrategy
    strategy = RuleBasedStrategy("AI对手")
    ai_agent = AIAgent("ai_opponent", profile, strategy)

    # 创建游戏
    game = CardGame("玩家", profile.name)

    ui.console.print(f"\n🎮 [bold green]交互模式开始！[/bold green]")
    ui.console.print(f"你的对手是: [bold blue]{profile.name}[/bold blue]")
    ui.console.print("=" * 50)

    # 主游戏循环
    while not game.game_over:
        current_player = game.get_current_player()

        # 如果是玩家回合
        if current_player.name == "玩家":
            game.display_status(use_rich=True)

            # 显示可用命令
            commands = game.get_available_commands()

            # 使用Rich的Prompt获取用户输入
            from rich.prompt import Prompt
            try:
                user_input = Prompt.ask(
                    "\n[bold green]请输入操作 (数字/命令)[/bold green]",
                    default="",
                    show_default=False
                ).strip()

                # 空输入或空格/回车 = 结束回合
                if not user_input or user_input in ['', ' ', '\n', '\r']:
                    result = game.end_turn(0, auto_attack=True)
                    ui.console.print(f"✅ {result['message']}", style="green")
                    continue

                user_input_lower = user_input.lower()

                # 退出游戏
                if user_input_lower in ['退出', 'quit', 'exit', 'q']:
                    ui.console.print("👋 [yellow]游戏已退出[/yellow]")
                    return

                # 帮助 - 使用智能上下文帮助
                elif user_input_lower in ['帮助', '帮', 'help', 'h']:
                    # 使用游戏提供的上下文帮助
                    context_help = game.get_context_help()
                    ui.console.print(context_help)
                    continue

                # 查看状态
                elif user_input_lower in ['状态', 'status']:
                    game.display_status(use_rich=True)
                    continue

                # 简化出牌 - 直接输入数字
                elif user_input.isdigit():
                    card_idx = int(user_input)
                    if card_idx < len(current_player.hand):
                        result = game.quick_play_card(0, card_idx)
                        ui.console.print(
                            f"✅ {result['message']}" if result["success"]
                            else f"❌ {result['message']}",
                            style="green" if result["success"] else "red"
                        )
                    else:
                        ui.console.print("❌ 无效的卡牌编号", style="red")
                    continue

                # 完整出牌命令
                elif user_input_lower.startswith('出牌 ') or user_input_lower.startswith('play '):
                    try:
                        card_idx = int(user_input.split()[1])
                        result = game.quick_play_card(0, card_idx)
                        ui.console.print(
                            f"✅ {result['message']}" if result["success"]
                            else f"❌ {result['message']}",
                            style="green" if result["success"] else "red"
                        )
                    except (IndexError, ValueError):
                        ui.console.print("❌ 无效的卡牌编号，请使用 '出牌 <编号>' 格式", style="red")
                    continue

                # 英雄技能
                elif user_input_lower in ['英雄技能', '技能', '技', 'power']:
                    result = game.use_hero_power(0)
                    ui.console.print(
                        f"✅ {result['message']}" if result["success"]
                        else f"❌ {result['message']}",
                        style="green" if result["success"] else "red"
                    )
                    continue

                # 随从攻击
                elif user_input_lower.startswith('随从攻击 ') or user_input_lower.startswith('attack '):
                    parts = user_input.split()
                    if len(parts) >= 3:
                        try:
                            minion_idx = int(parts[1])
                            target = parts[2]
                            result = game.attack_with_minion(0, minion_idx, target)
                            ui.console.print(
                                f"✅ {result['message']}" if result["success"]
                                else f"❌ {result['message']}",
                                style="green" if result["success"] else "red"
                            )
                        except (IndexError, ValueError):
                            ui.console.print("❌ 无效的随从编号", style="red")
                    else:
                        # 显示可攻击的随从和目标
                        attackable = []
                        for i, minion in enumerate(current_player.field):
                            if getattr(minion, 'can_attack', False):
                                targets = game.get_minion_attack_targets(0, i)
                                if targets:
                                    attackable.append(f"随从{i}: {get_card_name(minion)} -> {', '.join(targets)}")

                        if attackable:
                            ui.console.print("📋 [yellow]可攻击的随从:[/yellow]", style="yellow")
                            for info in attackable:
                                ui.console.print(f"  • {info}", style="white")
                        else:
                            ui.console.print("❌ 当前没有可以攻击的随从", style="red")
                    continue

                # 英雄攻击
                elif user_input_lower in ['英雄攻击', 'hero']:
                    result = game.attack_with_hero(0)
                    ui.console.print(
                        f"✅ {result['message']}" if result["success"]
                        else f"❌ {result['message']}",
                        style="green" if result["success"] else "red"
                    )
                    continue

                # 手动结束回合
                elif user_input_lower in ['结束回合', '结束', 'end']:
                    result = game.end_turn(0, auto_attack=False)
                    ui.console.print(f"✅ {result['message']}", style="green")

                else:
                    ui.console.print(f"❌ 未知命令: {user_input}", style="red")
                    ui.console.print("💡 输入 '帮助' 查看可用操作", style="dim")

            except KeyboardInterrupt:
                ui.console.print("\n👋 游戏被用户中断", style="yellow")
                return

        # 如果是AI回合
        else:
            ui.console.print(f"\n🤖 {current_player.name} 正在思考...", style="blue")
            await asyncio.sleep(1.5)  # 模拟思考时间

            # 创建游戏上下文给AI（AI总是第二个玩家）
            context = create_ai_context(game, ai_player_idx=1, game_id="interactive_game")

            # AI决策
            action = await ai_agent.make_decision(context)

            if action:
                # 分析AI决策原因
                decision_reason = ""
                if hasattr(action, 'reasoning') and action.reasoning:
                    decision_reason = f" - {action.reasoning[:80]}..."

                ui.console.print(f"🤖 {profile.name} 决策: {action.action_type.value}{decision_reason}", style="cyan")

                # 执行AI动作
                if action.action_type.value in ["play_minion", "play_card"]:
                    ai_hand = current_player.hand
                    playable_cards = [i for i, card in enumerate(ai_hand) if current_player.can_play_card(card)]

                    if playable_cards:
                        card_idx = random.choice(playable_cards)
                        card = ai_hand[card_idx]
                        result = game.play_card(1, card_idx)
                        # 使用安全的卡牌属性访问
                        card_name = get_card_name(card)
                        card_attack = get_card_attack(card)
                        card_health = get_card_health(card)
                        ui.console.print(f"  ✅ AI打出: {card_name} ({card_attack}/{card_health}) - {result['message']}", style="green")
                    else:
                        ui.console.print("  ❌ AI想出牌，但没有可出的牌", style="red")

                elif action.action_type.value == "use_spell":
                    ai_hand = current_player.hand
                    spell_cards = [i for i, card in enumerate(ai_hand)
                                 if card.card_type == "spell" and current_player.can_play_card(card)]
                    if spell_cards:
                        card_idx = random.choice(spell_cards)
                        card = ai_hand[card_idx]
                        result = game.play_card(1, card_idx)
                        # 使用安全的卡牌属性访问
                        card_name = get_card_name(card)
                        card_attack = get_card_attack(card)
                        effect = "造成伤害" if card_attack > 0 else "治疗" if card_attack < 0 else "特殊效果"
                        ui.console.print(f"  ✅ AI使用法术: {card_name} ({effect}) - {result['message']}", style="green")
                    else:
                        ui.console.print("  ❌ AI想使用法术，但没有可用的法术", style="red")

                elif action.action_type.value == "use_hero_power":
                    result = game.use_hero_power(1)
                    if result["success"]:
                        ui.console.print(f"  ✅ AI使用英雄技能 - {result['message']}", style="green")
                    else:
                        ui.console.print("  ❌ AI想使用英雄技能，但法力不足", style="red")

                elif action.action_type.value == "end_turn":
                    ai_hand = current_player.hand
                    playable_cards = [i for i, card in enumerate(ai_hand) if current_player.can_play_card(card)]
                    if playable_cards:
                        ui.console.print(f"  🤔 AI选择结束回合，虽然有 {len(playable_cards)} 张可出的牌", style="yellow")
                    else:
                        ui.console.print("  😔 AI没有可出的牌，选择结束回合", style="dim")
                else:
                    ui.console.print(f"  ❓ AI选择了未知动作: {action.action_type.value}", style="red")

            else:
                ui.console.print("🤖 AI无法做出决策，跳过回合", style="yellow")
                ai_hand = current_player.hand
                playable_cards = [i for i, card in enumerate(ai_hand) if current_player.can_play_card(card)]
                ui.console.print(f"  📋 AI当前手牌: {len(ai_hand)}张，可出: {len(playable_cards)}张", style="dim")

            # AI结束回合
            await asyncio.sleep(0.5)
            result = game.end_turn(1)
            ui.console.print(f"✅ {result['message']}", style="green")

    # 游戏结束
    if game.game_over:
        ui.console.print(f"\n🏁 游戏结束! {game.winner}", style="bold yellow")
        ui.console.print("=" * 50)

        # 显示最终统计
        final_state = game.get_game_state()
        ui.console.print(f"最终生命值: 玩家 {final_state['current_player_state']['health']} vs AI {final_state['opponent_state']['health']}")
        ui.console.print(f"总回合数: {game.turn_number}")

        # 显示游戏结果
        if game.winner == "玩家":
            result_text = "[bold green]🎉 恭喜你赢了！[/bold green]"
            border_style = "green"
        elif game.winner == "平局":
            result_text = "[bold yellow]🤝 平局！[/bold yellow]"
            border_style = "yellow"
        else:
            result_text = f"[bold red]😔 {game.winner} 获胜[/bold red]"
            border_style = "red"

        ui.console.print(Panel(
            result_text,
            title="游戏结果",
            box=box.DOUBLE,
            border_style=border_style
        ))

        # AI学习
        result = {
            "won": game.winner == profile.name,
            "opponent_id": "player",
            "opponent_aggression": 0.5,
            "final_health_diff": final_state['opponent_state']['health'] - final_state['current_player_state']['health']
        }
        ai_agent.learn_from_game(result)

        # 询问是否再来一局
        from rich.prompt import Confirm
        if Confirm.ask("再来一局？", default=True):
            # 递归调用，重新开始游戏
            await run_menu_interactive(choice, ui)
        else:
            ui.console.print("👋 [blue]感谢游玩交互模式！[/blue]")


async def run_menu_test(choice: dict, ui: GameUI):
    """菜单模式下的测试"""
    test_type = choice.get("test_type", "all")
    if test_type == "deepseek":
        await test_deepseek()
    elif test_type == "strategies":
        await test_strategies()
    elif test_type == "personalities":
        await test_personalities()
    elif test_type == "all":
        await test_all()


async def run_menu_benchmark(choice: dict, ui: GameUI):
    """菜单模式下的性能基准测试"""
    iterations = choice.get("iterations", 100)
    test_args = type('Args', (), {})()
    test_args.iterations = iterations
    await run_benchmark(test_args)


async def run_test_command(args):
    """运行测试命令"""
    logger.info(f"🧪 运行测试: {args.test_type}")

    if args.test_type == "deepseek":
        await test_deepseek()
    elif args.test_type == "strategies":
        await test_strategies()
    elif args.test_type == "personalities":
        await test_personalities()
    elif args.test_type == "all":
        await test_all()


def run_config_command(args):
    """运行配置命令"""
    from config.settings import get_settings

    if args.show:
        settings = get_settings()
        print("📋 当前配置:")
        print(f"  AI策略: {settings.ai.default_strategy}")
        print(f"  AI人格: {settings.ai.default_personality}")
        print(f"  LLM功能: {'启用' if settings.ai.enable_llm else '禁用'}")
        print(f"  监控功能: {'启用' if settings.monitoring.enable_monitoring else '禁用'}")
        print(f"  DeepSeek模型: {settings.ai.deepseek_model}")

    elif args.set:
        key, value = args.set
        print(f"⚙️ 设置配置: {key} = {value}")
        # 这里可以添加实际的配置设置逻辑

    elif args.reset:
        print("🔄 重置配置")
        # 这里可以添加重置配置的逻辑

    else:
        print("请指定配置操作，使用 --help 查看帮助")


def run_list_command(args):
    """运行列表命令"""
    if args.item == "strategies":
        from ai_engine import __all__ as available
        strategies = [name for name in available if 'Strategy' in name or 'Engine' in name]
        print("🤖 可用AI策略:")
        for strategy in strategies:
            print(f"  • {strategy}")

    elif args.item == "personalities":
        from ai_engine.agents.agent_personality import PERSONALITY_PROFILES
        print("🎭 可用AI人格:")
        for name, profile in PERSONALITY_PROFILES.items():
            print(f"  • {name}: {profile.name} ({profile.description})")

    elif args.item == "modes":
        print("🎮 可用游戏模式:")
        print("  • ai-vs-ai: AI对战模式")
        print("  • human-vs-ai: 人机对战模式")
        print("  • ai-vs-human: AI对人模式")
        print("  • interactive: 交互式模式")


async def run_benchmark_command(args):
    """运行基准测试命令"""
    logger.info(f"🚀 性能基准测试 (迭代次数: {args.iterations})")

    # 创建测试配置
    test_args = type('Args', (), {})()
    test_args.iterations = args.iterations

    if args.strategy:
        test_args.strategy = args.strategy

    await run_benchmark(test_args)


def run_status_command(args):
    """运行状态命令"""
    import os
    from config.settings import get_settings

    try:
        from ai_engine.monitoring import PerformanceMonitor
        monitor = PerformanceMonitor()
        monitor_available = True
    except ImportError:
        monitor = None
        monitor_available = False

    try:
        import psutil
        psutil_available = True
    except ImportError:
        psutil = None
        psutil_available = False

    settings = get_settings()

    print("📊 系统状态:")
    print(f"  Python版本: {sys.version.split()[0]}")
    print(f"  工作目录: {os.getcwd()}")

    if psutil_available:
        print(f"  内存使用: {psutil.virtual_memory().percent:.1f}%")
        print(f"  CPU使用: {psutil.cpu_percent():.1f}%")
    else:
        print("  系统资源信息: 需要安装 psutil 库")

    if args.detailed:
        if monitor_available and monitor:
            try:
                health = monitor.get_system_health()
                print(f"\n🏥 AI引擎状态:")
                print(f"  状态: {health.status}")
                print(f"  活跃策略: {health.active_strategies}")
                print(f"  错误率: {health.error_rate:.2f}")
                print(f"  平均响应时间: {health.avg_response_time:.3f}s")
            except Exception as e:
                print(f"\n🏥 AI引擎状态: 监控模块异常 ({e})")
        else:
            print(f"\n🏥 AI引擎状态: 监控模块不可用")
            print(f"  配置状态: LLM功能 {'启用' if settings.ai.enable_llm else '禁用'}")
            print(f"  默认策略: {settings.ai.default_strategy}")
            print(f"  默认人格: {settings.ai.default_personality}")


async def test_deepseek():
    """测试DeepSeek集成"""
    try:
        from test_deepseek import main as test_main
        await test_main()
    except Exception as e:
        logger.error(f"DeepSeek测试失败: {e}")


async def test_strategies():
    """测试AI策略"""
    from ai_engine.engine import AIEngine, AIEngineConfig
    from game_engine.game_state.game_context import GameContext

    print("🧪 测试AI策略...")

    config = AIEngineConfig()
    engine = AIEngine(config)

    # 用于存储需要清理的资源
    llm_manager = None
    deepseek_client = None

    try:
        context = GameContext(
            game_id="test_game",
            current_player=0,
            turn_number=5,
            phase="main",
            player_health=25,
            player_max_health=30,
            player_mana=6,
            player_max_mana=6,
            player_hand=ai_state.get("hand", []),
            player_field=[],
            player_deck_size=15,
            opponent_health=20,
            opponent_max_health=30,
            opponent_mana=4,
            opponent_max_mana=4,
            opponent_field=[],
            opponent_hand_size=4,
            opponent_deck_size=17
        )

        for strategy_name in engine.get_available_strategies():
            print(f"  测试策略: {strategy_name}")

            # 如果是混合策略，需要配置LLM
            if strategy_name == "hybrid":
                try:
                    from ai_engine.llm_integration.base import LLMManager
                    from ai_engine.llm_integration.deepseek_client import DeepSeekClient
                    from config.settings import get_settings

                    settings = get_settings()
                    if settings.ai.enable_llm and settings.ai.deepseek_api_key:
                        llm_manager = LLMManager()
                        deepseek_client = DeepSeekClient(settings.ai.deepseek_api_key)
                        llm_manager.register_client("deepseek", deepseek_client, is_default=True)

                        # 配置混合策略
                        from ai_engine.strategies.hybrid import HybridAIStrategy
                        hybrid_config = {
                            "strategies": [
                                {"name": "rule_based", "weight": 0.6, "min_confidence": 0.3},
                                {"name": "llm_enhanced", "weight": 0.4, "min_confidence": 0.5}
                            ]
                        }
                        hybrid_strategy = HybridAIStrategy("test_hybrid", hybrid_config)
                        hybrid_strategy.set_llm_manager(llm_manager)
                        engine.register_strategy("hybrid", hybrid_strategy)
                        print("    ✅ 混合策略已配置LLM功能")
                except Exception as e:
                    print(f"    ⚠️ LLM配置失败: {e}，仅使用规则部分")

            action = await engine.make_decision(context)
            if action:
                print(f"    ✅ 决策: {action.action_type.value} (置信度: {action.confidence:.2f})")
            else:
                print(f"    ❌ 无决策")

    finally:
        # 清理资源
        if deepseek_client:
            try:
                await deepseek_client.close()
                print("    ✅ 测试DeepSeek客户端已关闭")
            except Exception as e:
                print(f"    ⚠️ 关闭DeepSeek客户端时出错: {e}")

        if llm_manager:
            try:
                if hasattr(llm_manager, 'clients'):
                    for client in llm_manager.clients.values():
                        if hasattr(client, 'close'):
                            await client.close()
                print("    ✅ 测试LLM管理器已清理")
            except Exception as e:
                print(f"    ⚠️ 清理LLM管理器时出错: {e}")


async def test_personalities():
    """测试AI人格"""
    from ai_engine.agents.agent_personality import PersonalityManager, PERSONALITY_PROFILES
    from ai_engine.strategies.rule_based import RuleBasedStrategy
    from game_engine.game_state.game_context import GameContext

    print("🧪 测试AI人格...")

    manager = PersonalityManager()
    context = GameContext(
        game_id="test_game",
        current_player=0,
        turn_number=5,
        phase="main",
        player_health=25,
        player_max_health=30,
        player_mana=6,
        player_max_mana=6,
        player_hand=ai_state.get("hand", []),
        player_field=[],
        player_deck_size=15,
        opponent_health=20,
        opponent_max_health=30,
        opponent_mana=4,
        opponent_max_mana=4,
        opponent_field=[],
        opponent_hand_size=4,
        opponent_deck_size=17
    )

    for name, profile in PERSONALITY_PROFILES.items():
        print(f"  测试人格: {profile.name}")
        strategy = RuleBasedStrategy(f"test_{name}")

        from ai_engine.agents.ai_agent import AIAgent
        agent = AIAgent(f"test_{name}", profile, strategy)

        action = await agent.make_decision(context)
        if action:
            print(f"    ✅ 决策: {action.action_type.value} (置信度: {action.confidence:.2f})")
        else:
            print(f"    ❌ 无决策")


async def test_all():
    """运行所有测试"""
    print("🧪 运行所有测试...")

    await test_deepseek()
    await test_strategies()
    await test_personalities()

    print("✅ 所有测试完成!")


def show_help():
    """显示帮助信息"""
    help_text = """
🎮 Card Battle Arena Enhanced - 智能卡牌游戏AI系统

🚀 快速开始:
  python main.py demo                          # 运行AI功能演示
  python main.py play --mode ai-vs-ai --games 3     # AI对战3场
  python main.py play --mode interactive            # 交互式模式
  python main.py test deepseek                     # 测试DeepSeek集成
  python main.py list strategies                    # 列出所有AI策略
  python main.py benchmark --iterations 50         # 性能基准测试

📋 可用命令:
  demo         - 运行AI功能演示
  play         - 开始游戏
  test         - 运行测试
  config       - 配置管理
  list         - 列出信息
  benchmark    - 性能基准测试
  status       - 显示系统状态

🎮 游戏模式:
  ai-vs-ai     - AI对战模式
  human-vs-ai  - 人机对战模式
  ai-vs-human  - AI对人模式
  interactive  - 交互式模式

🤖 AI策略:
  rule_based    - 基于规则的AI
  hybrid        - 混合策略AI
  llm_enhanced  - LLM增强AI

🎭 AI人格:
  aggressive_berserker    - 狂战士
  wise_defender           - 智慧守护者
  strategic_mastermind    - 战略大师
  combo_enthusiast       - 连锁爱好者
  adaptive_learner        - 适应性学习者
  fun_seeker              - 娱乐玩家

📊 更多帮助:
  python main.py --help              # 显示详细帮助
  python main.py demo --help          # 演示模式帮助
  python main.py play --help          # 游戏模式帮助
  python main.py test --help          # 测试命令帮助
"""

    print(help_text)


async def run_debug_command(args):
    """运行调试命令"""
    from rich.console import Console
    from rich.table import Table
    console = Console()

    if args.action == "performance":
        # 显示性能摘要
        debugger.print_performance_summary()

    elif args.action == "export":
        # 导出调试报告
        output_file = args.output if hasattr(args, 'output') and args.output else None
        report_path = debugger.export_debug_report(output_file)
        console.print(f"📊 调试报告已导出到: {report_path}")

    elif args.action == "analyze":
        # 分析决策模式
        patterns = debugger.analyze_decision_patterns()

        if "message" in patterns:
            console.print(f"⚠️ {patterns['message']}")
        else:
            console.print("🔍 决策模式分析结果:")

            # 策略分析表格
            if "strategy_analysis" in patterns:
                table = Table(title="策略性能分析")
                table.add_column("策略", style="cyan")
                table.add_column("决策数", justify="right")
                table.add_column("平均置信度", justify="right")
                table.add_column("平均耗时", justify="right")
                table.add_column("最常用动作", style="green")

                for strategy, stats in patterns["strategy_analysis"].items():
                    most_common = max(stats["common_actions"].items(), key=lambda x: x[1])
                    table.add_row(
                        strategy,
                        str(stats["count"]),
                        f"{stats['avg_confidence']:.3f}",
                        f"{stats['avg_time']:.3f}s",
                        f"{most_common[0]} ({most_common[1]}次)"
                    )
                console.print(table)

            # 置信度趋势
            if "confidence_analysis" in patterns:
                conf_analysis = patterns["confidence_analysis"]
                console.print(f"\n📈 置信度趋势: {conf_analysis['confidence_trend']}")
                console.print(f"   平均置信度: {conf_analysis['avg_confidence']:.3f}")
                console.print(f"   高置信度比例: {conf_analysis['high_confidence_ratio']:.1%}")

    elif args.action == "clear":
        # 清空调试历史
        debugger.clear_history()
        console.print("🗑️ 调试历史已清空")

    elif args.action == "save":
        # 保存调试会话
        filename = args.filename if hasattr(args, 'filename') and args.filename else None
        debugger.save_session(filename)
        console.print("💾 调试会话已保存")

    elif args.action == "load":
        # 加载调试会话
        filename = args.filename if hasattr(args, 'filename') and args.filename else None
        if not filename:
            console.print("❌ 请指定要加载的会话文件")
            return
        debugger.load_session(filename)
        console.print(f"📂 调试会话已从 {filename} 加载")

    else:
        console.print(f"❌ 未知的调试动作: {args.action}")
        console.print("可用动作: performance, export, analyze, clear, save, load")


async def cleanup_resources():
    """清理所有资源"""
    try:
        # 清理设置管理器
        try:
            from config.user_preferences import get_settings_manager
            manager = get_settings_manager()
            if hasattr(manager, 'save_all_settings'):
                manager.save_all_settings()
                logger.debug("✅ 设置保存完成")
        except Exception as e:
            logger.debug(f"保存设置时出错: {e}")

        # 强制垃圾回收
        try:
            import gc
            gc.collect()
            logger.debug("✅ 垃圾回收完成")
        except Exception as e:
            logger.debug(f"垃圾回收时出错: {e}")

        logger.info("✅ 资源清理完成")

    except Exception as e:
        logger.debug(f"资源清理过程中出现错误: {e}")
        # 即使清理失败也不抛出异常，确保程序能正常退出


async def main():
    """主函数"""
    try:
        args = parse_arguments()
        configure_logging(args)

        # 如果没有指定命令，显示帮助
        if not hasattr(args, 'command') or args.command is None:
            show_help()
            return

        # 根据命令执行相应功能
        if args.command == "demo":
            await run_demo_command(args)
        elif args.command == "play":
            await run_play_command(args)
        elif args.command == "test":
            await run_test_command(args)
        elif args.command == "config":
            run_config_command(args)
        elif args.command == "list":
            run_list_command(args)
        elif args.command == "benchmark":
            await run_benchmark_command(args)
        elif args.command == "status":
            run_status_command(args)
        elif args.command == "debug":
            await run_debug_command(args)
        else:
            logger.error(f"未知命令: {args.command}")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
        # 优雅退出，清理资源
        await cleanup_resources()
        return
    except Exception as e:
        # 更安全的verbose属性访问
        verbose = getattr(args, 'verbose', False) if 'args' in locals() else False
        if verbose:
            import traceback
            traceback.print_exc()
        else:
            logger.error(f"❌ 程序运行出错: {e}")
        # 即使出错也要清理资源
        try:
            await cleanup_resources()
        except:
            pass
        sys.exit(1)
    finally:
        # 确保资源被清理
        try:
            await cleanup_resources()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())