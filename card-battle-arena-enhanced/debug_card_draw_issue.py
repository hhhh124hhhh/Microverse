#!/usr/bin/env python3
"""
调试后期抽不到手牌的问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def debug_card_draw_issue():
    """调试后期抽不到手牌的问题"""
    from rich.console import Console
    from game_engine.card_game import CardGame, Card, Player
    console = Console()

    console.print("🎯 [bold blue]后期抽牌问题调试[/bold blue]")
    console.print("=" * 50)

    # 创建游戏实例
    game = CardGame("测试玩家", "测试AI")
    player = game.players[0]
    ai_player = game.players[1]

    # 场景1: 检查初始状态
    console.print("📋 [bold cyan]场景1: 检查初始游戏状态[/bold cyan]")
    console.print("-" * 30)

    console.print(f"玩家初始状态:")
    console.print(f"  手牌数量: {len(player.hand)}")
    console.print(f"  牌组大小: {player.deck_size}")
    console.print(f"  手牌内容:")
    for i, card in enumerate(player.hand):
        console.print(f"    {i}. {card.name} ({card.cost}费)")

    console.print(f"\nAI初始状态:")
    console.print(f"  手牌数量: {len(ai_player.hand)}")
    console.print(f"  牌组大小: {ai_player.deck_size}")

    # 场景2: 模拟多回合，观察抽牌情况
    console.print(f"\n📋 [bold cyan]场景2: 模拟多回合抽牌[/bold cyan]")
    console.print("-" * 30)

    turn_count = 0
    max_turns_to_test = 30  # 测试30回合

    while turn_count < max_turns_to_test and not game.game_over:
        turn_count += 1
        current_player = game.get_current_player()

        console.print(f"\n🔄 回合 {turn_count} - {current_player.name} 的回合")
        console.print(f"  抽牌前状态:")
        console.print(f"    手牌数量: {len(current_player.hand)}")
        console.print(f"    牌组大小: {current_player.deck_size}")
        console.print(f"    法力值: {current_player.mana}/{current_player.max_mana}")

        # 记录抽牌前的手牌数量
        hand_before = len(current_player.hand)
        deck_before = current_player.deck_size

        # 手动执行抽牌逻辑（模拟start_turn中的抽牌）
        if current_player.deck_size > 0:
            card = game._smart_draw_card(current_player)
            draw_success = current_player.draw_card(card)

            console.print(f"  抽牌结果:")
            console.print(f"    抽牌成功: {draw_success}")
            if draw_success:
                console.print(f"    抽到: {card.name} ({card.cost}费)")
            console.print(f"    抽牌后状态:")
            console.print(f"      手牌数量: {len(current_player.hand)} (变化: {len(current_player.hand) - hand_before})")
            console.print(f"      牌组大小: {current_player.deck_size} (变化: {deck_before - current_player.deck_size})")
        else:
            console.print(f"  ❌ 牌组已空，无法抽牌")

        # 检查手牌是否已满
        if len(current_player.hand) >= 10:
            console.print(f"  ⚠️ 手牌已满 (10张)，无法继续抽牌")

        # 显示当前手牌
        if len(current_player.hand) > 0:
            console.print(f"  当前手牌:")
            for i, card in enumerate(current_player.hand):
                console.print(f"    {i}. {card.name} ({card.cost}费)")

        # 结束当前回合
        game.end_turn(current_player == game.players[0])

        # 如果进行了足够的回合，提前退出
        if turn_count >= 20:
            console.print(f"\n⚠️ 已测试{turn_count}回合，停止测试")
            break

    # 场景3: 分析抽牌逻辑
    console.print(f"\n📋 [bold cyan]场景3: 分析抽牌逻辑[/bold cyan]")
    console.print("-" * 30)

    console.print("抽牌逻辑分析:")
    console.print("1. 玩家初始牌组: 25张")
    console.print("2. 初始抽牌: 3张 (剩余22张)")
    console.print("3. 每回合抽牌: 1张 (理论上可以抽22回合)")
    console.print("4. 手牌上限: 10张")
    console.print("5. 手牌已满时: 抽牌失败但牌组数量会减少")

    # 测试手牌上限逻辑
    console.print(f"\n🔍 测试手牌上限逻辑:")

    # 创建一个测试玩家
    test_player = Player("测试玩家")
    test_player.deck_size = 10

    console.print(f"  测试玩家初始状态:")
    console.print(f"    手牌: {len(test_player.hand)}张")
    console.print(f"    牌组: {test_player.deck_size}张")

    # 添加9张手牌
    for i in range(9):
        test_card = Card(f"测试卡{i}", 1, 1, 1, "minion", [])
        test_player.draw_card(test_card)

    console.print(f"  添加9张手牌后:")
    console.print(f"    手牌: {len(test_player.hand)}张")
    console.print(f"    牌组: {test_player.deck_size}张")

    # 尝试添加第10张手牌
    test_card_10 = Card("第10张卡", 1, 1, 1, "minion", [])
    result_10 = test_player.draw_card(test_card_10)

    console.print(f"  尝试添加第10张手牌:")
    console.print(f"    抽牌结果: {result_10}")
    console.print(f"    手牌: {len(test_player.hand)}张")
    console.print(f"    牌组: {test_player.deck_size}张")

    # 尝试添加第11张手牌（应该失败）
    test_card_11 = Card("第11张卡", 1, 1, 1, "minion", [])
    result_11 = test_player.draw_card(test_card_11)

    console.print(f"  尝试添加第11张手牌:")
    console.print(f"    抽牌结果: {result_11}")
    console.print(f"    手牌: {len(test_player.hand)}张")
    console.print(f"    牌组: {test_player.deck_size}张")

    console.print(f"\n🎯 [bold green]问题诊断结果：[/bold green]")
    console.print("1. 如果牌组25张牌被抽完，确实会无法抽牌")
    console.print("2. 如果手牌达到10张上限，也会无法抽牌")
    console.print("3. 需要检查实际游戏中是哪种情况导致无法抽牌")
    console.print("4. 可能的解决方案:")
    console.print("   - 增加初始牌组大小")
    console.print("   - 实现牌组重洗机制")
    console.print("   - 调整手牌上限")
    console.print("   - 添加疲劳伤害机制")

if __name__ == "__main__":
    debug_card_draw_issue()