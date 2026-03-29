# config/characters.py
# 角色配置
CHARACTERS = [
    {
        "name": "战士",
        "desc": "高生命值，强大的AOE技能",
        "hp": 15,
        "speed": 5,
        "damage": 2,
        "ultimate": {
            "name": "旋风斩",
            "type": "aoe",
            "radius": 120,
            "dmg": 5,
            "duration": 5,
            "cd": 20
        }
    },
    {
        "name": "射手",
        "desc": "高攻速，技能提升所有武器攻速",
        "hp": 10,
        "speed": 6,
        "damage": 1,
        "ultimate": {
            "name": "极速射击",
            "type": "speedup",
            "multiplier": 0.5,
            "duration": 10,
            "cd": 25
        }
    },
    {
        "name": "忍者",
        "desc": "高移速，技能提供短暂无敌",
        "hp": 8,
        "speed": 8,
        "damage": 3,
        "ultimate": {
            "name": "影遁",
            "type": "invincible",
            "duration": 3,
            "cd": 15
        }
    },
    {
        "name": "机器人",
        "desc": "技能提供护盾，抵挡伤害",
        "hp": 12,
        "speed": 4,
        "damage": 4,
        "ultimate": {
            "name": "能量护盾",
            "type": "shield",
            "hits": 5,
            "cd": 30
        }
    }
]