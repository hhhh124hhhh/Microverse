#!/usr/bin/env python3
"""
测试AI攻击修复 - 验证攻击目标格式问题
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_attack_fix():
    """测试AI攻击修复"""
    from rich.console import Console
    console = Console()

    console.print("🎯 [bold blue]AI攻击目标格式修复测试[/bold blue]")
    console.print("=" * 50)

    # 模拟AI决策返回的攻击动作
    console.print("📋 [bold cyan]模拟AI攻击决策[/bold cyan]")
    console.print("-" * 30)

    # 模拟AI决策对象
    class MockAction:
        def __init__(self, action_type, parameters=None, reasoning=""):
            self.action_type = action_type
            self.parameters = parameters or {}
            self.reasoning = reasoning

    # 模拟卡牌对象
    class MockCard:
        def __init__(self, name, attack, health):
            self.name = name
            self.attack = attack
            self.health = health

    # 模拟AI决策：石像鬼攻击狼人渗透者
    ai_attacker = MockCard("石像鬼", 1, 1)
    ai_target = MockCard("狼人渗透者", 3, 2)

    ai_action = MockAction(
        action_type="attack",
        parameters={
            "attacker": ai_attacker,
            "target": ai_target
        },
        reasoning="石像鬼攻击敌方随从狼人渗透者"
    )

    console.print(f"AI攻击决策:")
    console.print(f"  攻击者: {ai_action.parameters['attacker'].name}")
    console.print(f"  目标: {ai_action.parameters['target'].name}")
    console.print(f"  推理: {ai_action.reasoning}")

    # 模拟游戏状态
    console.print(f"\n📋 [bold cyan]模拟游戏状态[/bold cyan]")
    console.print("-" * 30)

    # 模拟玩家手牌和场上随从
    player_field = [ai_target]  # 玩家场上有狼人渗透者
    ai_field = [ai_attacker]    # AI场上有石像鬼

    console.print(f"玩家场上随从:")
    for i, minion in enumerate(player_field):
        console.print(f"  随从{i}: {minion.name} ({minion.attack}/{minion.health})")

    console.print(f"AI场上随从:")
    for i, minion in enumerate(ai_field):
        console.print(f"  随从{i}: {minion.name} ({minion.attack}/{minion.health})")

    # 测试当前有问题的攻击执行逻辑
    console.print(f"\n📋 [bold cyan]当前有问题的攻击逻辑[/bold cyan]")
    console.print("-" * 30)

    def get_card_name(card):
        """获取卡牌名称的辅助函数"""
        if isinstance(card, str):
            return card
        elif hasattr(card, 'name'):
            return card.name
        elif isinstance(card, dict):
            return card.get('name', '未知')
        else:
            return str(card)

    # 模拟当前execute_ai_action中的逻辑
    attacker = ai_action.parameters.get("attacker")
    target = ai_action.parameters.get("target")

    console.print(f"攻击者: {get_card_name(attacker)}")
    console.print(f"目标: {get_card_name(target)}")

    # 找到攻击者索引
    attacker_idx = None
    for i, minion in enumerate(ai_field):
        if get_card_name(minion) == get_card_name(attacker):
            attacker_idx = i
            console.print(f"✅ 找到攻击者索引: {i}")
            break

    if attacker_idx is not None:
        if isinstance(target, str) and "英雄" in target:
            # 攻击英雄
            target_for_attack = "英雄"
            console.print(f"目标: 英雄")
        else:
            # 这里是问题所在！
            target_name = get_card_name(target) if target else "随从0"
            target_for_attack = target_name
            console.print(f"❌ 问题: 目标名称是 '{target_name}'")
            console.print(f"   游戏引擎期望格式: '随从_X'")
            console.print(f"   实际传递格式: '{target_name}'")

    # 测试修复后的逻辑
    console.print(f"\n📋 [bold cyan]修复后的攻击逻辑[/bold cyan]")
    console.print("-" * 30)

    def execute_ai_attack_fixed(action, player_field, ai_field):
        """修复后的AI攻击执行逻辑"""
        if hasattr(action, 'parameters') and action.parameters:
            attacker = action.parameters.get("attacker")
            target = action.parameters.get("target")

            if attacker and target:
                # 找到攻击者索引
                attacker_idx = None
                for i, minion in enumerate(ai_field):
                    if get_card_name(minion) == get_card_name(attacker):
                        attacker_idx = i
                        break

                if attacker_idx is not None:
                    if isinstance(target, str) and "英雄" in target:
                        # 攻击英雄
                        return {"success": True, "target": "英雄", "attacker_idx": attacker_idx}
                    else:
                        # 修复：找到目标随从的索引
                        target_idx = None
                        for i, minion in enumerate(player_field):
                            if get_card_name(minion) == get_card_name(target):
                                target_idx = i
                                break

                        if target_idx is not None:
                            # 使用正确的格式 "随从_X"
                            target_for_attack = f"随从_{target_idx}"
                            return {"success": True, "target": target_for_attack, "attacker_idx": attacker_idx, "target_idx": target_idx}
                        else:
                            return {"success": False, "message": f"找不到目标随从: {get_card_name(target)}"}
                else:
                    return {"success": False, "message": f"找不到攻击随从: {get_card_name(attacker)}"}
            else:
                return {"success": False, "message": "攻击参数不完整"}
        else:
            return {"success": False, "message": "攻击缺少参数"}

    # 测试修复后的逻辑
    result = execute_ai_attack_fixed(ai_action, player_field, ai_field)
    console.print(f"修复后执行结果:")
    console.print(f"  成功: {result['success']}")
    if result['success']:
        console.print(f"  攻击者索引: {result['attacker_idx']}")
        console.print(f"  目标格式: '{result['target']}'")
        if 'target_idx' in result:
            console.print(f"  目标索引: {result['target_idx']}")
        console.print("✅ 修复成功！现在目标格式正确")
    else:
        console.print(f"  错误: {result['message']}")

    # 测试多个目标的情况
    console.print(f"\n📋 [bold cyan]测试多目标情况[/bold cyan]")
    console.print("-" * 30)

    # 添加更多随从
    player_field.extend([
        MockCard("鹰身女妖", 2, 1),
        MockCard("石像鬼", 1, 1)
    ])

    console.print("扩展后的玩家场上随从:")
    for i, minion in enumerate(player_field):
        console.print(f"  随从{i}: {minion.name} ({minion.attack}/{minion.health})")

    # 测试攻击不同目标
    test_targets = ["狼人渗透者", "鹰身女妖", "石像鬼"]

    for target_name in test_targets:
        target_card = MockCard(target_name, 0, 0)
        test_action = MockAction("attack", {
            "attacker": ai_attacker,
            "target": target_card
        })

        result = execute_ai_attack_fixed(test_action, player_field, ai_field)
        if result['success']:
            console.print(f"✅ {target_name} -> {result['target']} (索引: {result.get('target_idx', 'N/A')})")
        else:
            console.print(f"❌ {target_name} -> {result['message']}")

    console.print(f"\n🎯 [bold green]修复总结：[/bold green]")
    console.print("1. 原问题：AI攻击随从时传递卡牌名称而不是随从索引格式")
    console.print("2. 修复方案：在攻击执行前查找目标随从的索引，转换为'随从_X'格式")
    console.print("3. 修复位置：main.py中的execute_ai_action函数第273行")
    console.print("4. 修复效果：AI攻击目标格式现在与游戏引擎期望一致")

if __name__ == "__main__":
    test_ai_attack_fix()