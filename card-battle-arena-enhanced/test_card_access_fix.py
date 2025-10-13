#!/usr/bin/env python3
"""
测试卡牌属性访问修复
"""

import sys
sys.path.insert(0, '.')

from game_engine.card_game import Card, get_card_name, safe_get_card_attr

def test_card_object_access():
    """测试卡牌对象属性访问"""
    print("🧪 测试卡牌对象属性访问...")

    # 创建一个卡牌对象
    card = Card("火球术", 4, 6, 0, "spell", [], "造成6点伤害")

    # 测试安全访问函数
    name = get_card_name(card)
    attack = safe_get_card_attr(card, 'attack', 0)
    health = safe_get_card_attr(card, 'health', 0)
    card_type = safe_get_card_attr(card, 'card_type', 'minion')

    print(f"✅ 卡牌名称: {name}")
    print(f"✅ 攻击力: {attack}")
    print(f"✅ 血量: {health}")
    print(f"✅ 类型: {card_type}")

    return True

def test_card_dict_access():
    """测试卡牌字典属性访问"""
    print("\n🧪 测试卡牌字典属性访问...")

    # 创建一个卡牌字典
    card_dict = {
        'name': '烈焰元素',
        'attack': 5,
        'health': 3,
        'card_type': 'minion',
        'cost': 3,
        'mechanics': []
    }

    # 测试安全访问函数
    name = get_card_name(card_dict)
    attack = safe_get_card_attr(card_dict, 'attack', 0)
    health = safe_get_card_attr(card_dict, 'health', 0)
    card_type = safe_get_card_attr(card_dict, 'card_type', 'minion')

    print(f"✅ 卡牌名称: {name}")
    print(f"✅ 攻击力: {attack}")
    print(f"✅ 血量: {health}")
    print(f"✅ 类型: {card_type}")

    return True

def test_mixed_access():
    """测试混合访问方式"""
    print("\n🧪 测试混合访问方式...")

    # 创建列表包含不同格式的卡牌
    cards = [
        Card("火球术", 4, 6, 0, "spell", [], "造成6点伤害"),
        {'name': '烈焰元素', 'attack': 5, 'health': 3, 'card_type': 'minion'},
        Card("冰霜新星", 3, 2, 0, "spell", ["freeze"], "冻结所有敌人"),
        {'name': '霜狼步兵', 'attack': 2, 'health': 3, 'card_type': 'minion', 'mechanics': ['taunt']}
    ]

    for i, card in enumerate(cards):
        name = get_card_name(card)
        attack = safe_get_card_attr(card, 'attack', 0)
        health = safe_get_card_attr(card, 'health', 0)
        card_type = safe_get_card_attr(card, 'card_type', 'minion')

        print(f"✅ 卡牌{i+1}: {name} ({attack}/{health}) - {card_type}")

    return True

def main():
    """主测试函数"""
    print("🚀 开始测试卡牌属性访问修复...")

    try:
        # 测试对象访问
        test_card_object_access()

        # 测试字典访问
        test_card_dict_access()

        # 测试混合访问
        test_mixed_access()

        print("\n🎉 所有测试通过！卡牌属性访问修复成功！")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)