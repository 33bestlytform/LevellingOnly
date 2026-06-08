# src/ability.py
# 升级系统模块

import random
from config.weapons import BASE_WEAPON_CONFIG

# 定义所有升级选项
UPGRADE_POOL = [
    {
        "name": "生命+3",
        "effect": lambda p: (setattr(p, 'max_hp', p.max_hp + 3), setattr(p, 'hp', p.hp + 3)),
        "condition": lambda p: True,  # 总是可用
    },
    {
        "name": "基础伤害+1",
        "effect": lambda p: setattr(p, 'base_damage', p.base_damage + 1),
        "condition": lambda p: True,
    },
    {
        "name": "全武器攻速+",
        "effect": lambda p: [
            BASE_WEAPON_CONFIG[wp].update({'atk_speed': max(0.15, BASE_WEAPON_CONFIG[wp]['atk_speed'] * 0.97)})
            for wp in BASE_WEAPON_CONFIG.keys()
        ],
        "condition": lambda p: True,
    },
    {
        "name": "移速+1",
        "effect": lambda p: setattr(p, 'speed', min(p.speed + 1, 10)),
        "condition": lambda p: True,
    },
    {
        "name": "散弹枪弹丸数量+1",
        "effect": lambda p: BASE_WEAPON_CONFIG["霰弹枪"].update({'pellets': min(8, BASE_WEAPON_CONFIG["霰弹枪"].get('pellets', 3) + 1)}),
        "condition": lambda p: "霰弹枪" in p.unlocked_weapons and BASE_WEAPON_CONFIG["霰弹枪"].get('pellets', 3) < 12,
    },
    # 在这里添加新的升级选项
    {
        "name": "金币+5",
        "effect": lambda p: setattr(p, 'money', p.money + 5),
        "condition": lambda p: True,
    },
    {
        "name": "终极技能冷却-10%",
        "effect": lambda p: setattr(p, 'ultimate', {**p.ultimate, 'cd': max(5, p.ultimate['cd'] * 0.9)}),
        "condition": lambda p: True,
    },
]

def generate_upgrades(player, count=3):
    """
    从升级池中随机选择指定数量的升级选项
    只选择满足条件的升级
    :param player: 玩家对象，用于条件判断
    :param count: 选择的升级数量，默认为3
    :return: 升级选项列表，包含name和effect
    """
    # 过滤出满足条件的升级选项
    available_upgrades = [upgrade for upgrade in UPGRADE_POOL if upgrade['condition'](player)]
    # 随机选择
    return random.sample(available_upgrades, min(count, len(available_upgrades)))

def apply_upgrade(player, upgrade):
    """
    应用升级效果
    :param player: 玩家对象
    :param upgrade: 升级选项字典
    """
    if 'effect' in upgrade:
        upgrade['effect'](player)

def get_all_upgrade_names():
    """
    获取所有可用的升级选项名称
    :return: 升级名称列表
    """
    return [upgrade["name"] for upgrade in UPGRADE_POOL]

def add_upgrade_option(name, effect):
    """
    动态添加新的升级选项
    :param name: 升级名称
    :param effect: 升级效果函数（接收player参数）
    """
    UPGRADE_POOL.append({
        "name": name,
        "effect": effect,
    })