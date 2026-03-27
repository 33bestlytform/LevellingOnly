import pygame

# 初始化 Pygame
pygame.init()

# 屏幕设置
SW, SH = 1000, 700

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (220, 40, 50)
YELLOW = (255, 220, 0)
ORANGE = (255, 140, 0)
BLUE = (0, 220, 255)
DARK_BLUE = (18, 18, 22)
SHOP_BG = (20, 20, 30)

# 字体设置
try:
    # 尝试使用支持中文的字体
    FONT = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "Arial"], 32)
    BIG_FONT = pygame.font.SysFont(["SimHei", "Microsoft YaHei", "Arial"], 48)
except:
    # 使用默认字体
    FONT = pygame.font.SysFont(None, 32)
    BIG_FONT = pygame.font.SysFont(None, 48)

# 游戏常量
WEAPONS = ["手枪", "霰弹", "激光", "剑"]

# 生存目标时间（10分钟）
SURVIVE_GOAL = 10 * 60 * 1000

# 初始敌人数量
INITIAL_ENEMIES = 6

# 敌人速度范围
ENEMY_SPEED_MIN = 1.2
ENEMY_SPEED_MAX = 2.7

# 敌人掉落金币范围
ENEMY_MONEY_MIN = 1
ENEMY_MONEY_MAX = 3

# 武器伤害系数
WEAPON_DAMAGE = {
    "手枪": 1.0,
    "霰弹": 0.5,
    "激光": 1.5,
    "剑": 2.0
}

# 武器速度
WEAPON_SPEED = {
    "手枪": 8,
    "霰弹": 7,
    "激光": 12
}

# 升级选项
UPGRADE_OPTIONS = [
    ("生命+3", lambda p: setattr(p, 'max_hp', p.max_hp + 3) or setattr(p, 'hp', p.hp + 3)),
    ("伤害+1", lambda p: setattr(p, 'damage', p.damage + 1)),
    ("攻速提升", lambda p: setattr(p, 'atk_speed', max(0.06, p.atk_speed * 0.82))),
    ("移速+1", lambda p: setattr(p, 'speed', p.speed + 1)),
]

# 商店物品
SHOP_ITEMS = [
    ("生命+2  10金币", 10, lambda pl: setattr(pl, 'max_hp', pl.max_hp + 2) or setattr(pl, 'hp', pl.hp + 2)),
    ("伤害+1  15金币", 15, lambda pl: setattr(pl, 'damage', pl.damage + 1)),
    ("攻速提升 12金币", 12, lambda pl: setattr(pl, 'atk_speed', max(0.06, pl.atk_speed * 0.85))),
    ("移速+1  10金币", 10, lambda pl: setattr(pl, 'speed', pl.speed + 1)),
]

# 角色数据
CHARACTERS = [
    {"name": "战士", "hp": 15, "speed": 4, "damage": 2, "atk_speed": 0.3, "desc": "血厚攻高"},
    {"name": "射手", "hp": 8, "speed": 6, "damage": 1, "atk_speed": 0.15, "desc": "攻速飞快"},
    {"name": "忍者", "hp": 10, "speed": 8, "damage": 1, "atk_speed": 0.25, "desc": "极致灵活"},
    {"name": "机器人", "hp": 20, "speed": 3, "damage": 3, "atk_speed": 0.4, "desc": "超级肉盾"}
]