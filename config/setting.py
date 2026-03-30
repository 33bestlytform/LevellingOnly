# config/settings.py
import pygame

# 初始化 Pygame
pygame.init()

# 屏幕设置
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

# 颜色定义
COLORS = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GREEN": (0, 255, 0),
    "RED": (220, 40, 50),
    "YELLOW": (255, 220, 0),
    "ORANGE": (255, 140, 0),
    "BLUE": (0, 220, 255),
    "DARK_BLUE": (18, 18, 22),
    "SHOP_BG": (20, 20, 30)
}

# 字体设置
def load_font():
    """安全加载字体函数"""
    font_paths = [
        "assets/fonts/MSYH.TTC",
        "assets/fonts/MSYHBD.TTC",
        "assets/fonts/MSYHL.TTC",
        "C:/Windows/Fonts/msyh.ttc",  # Windows系统字体路径
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/msyhl.ttc"
    ]
    
    # 首先尝试加载本地字体文件
    for font_path in font_paths:
        try:
            return pygame.font.Font(font_path, 32), \
                   pygame.font.Font(font_path, 48), \
                   pygame.font.Font(font_path, 24)
        except (FileNotFoundError, OSError):
            continue
    
    # 如果本地字体都失败，尝试系统字体
    try:
        return pygame.font.SysFont("Microsoft YaHei", 32), \
               pygame.font.SysFont("Microsoft YaHei", 48), \
               pygame.font.SysFont("Microsoft YaHei", 24)
    except:
        # 最后回退到默认字体
        return pygame.font.SysFont(None, 32), \
               pygame.font.SysFont(None, 48), \
               pygame.font.SysFont(None, 24)

FONT, BIG_FONT, SMALL_FONT = load_font()

# 游戏常量
SURVIVE_GOAL = 10 * 60 * 1000  # 10分钟
INITIAL_ENEMIES = 6

# 敌人配置
ENEMY_CONFIG = {
    "speed_min": 1.2,
    "speed_max": 2.7,
    "money_min": 1,
    "money_max": 3
}

# 血包配置
HEALTH_PACK_CONFIG = {
    "drop_chance": 0.03,  # 3%概率掉落
    "heal_amount": 2,     # 恢复2点血
    "size": 20,           # 血包碰撞框大小
    "color": (255, 0, 0)  # 红色血包
}

# 史莱姆配置
SLIME_SIZE = {
    "big": {"size": 40, "hp": 5, "split_to": "mid", "speed": 1.0},
    "mid": {"size": 25, "hp": 2, "split_to": "small", "speed": 1.5},
    "small": {"size": 15, "hp": 1, "split_to": None, "speed": 2.0}
}