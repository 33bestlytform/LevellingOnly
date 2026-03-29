# config/enemies.py
import random
from src.enemy import Enemy
from config.setting import SCREEN_WIDTH, SCREEN_HEIGHT

def wave_spawn(count, wave):
    """
    生成敌人
    :param count: 敌人数量
    :param wave: 波数
    :return: 敌人列表
    """
    enemies = []
    is_boss_wave = wave % 5 == 0
    
    if is_boss_wave:
        # 每5波生成一个BOSS
        enemies.append(Enemy("boss", wave))
    else:
        # 普通波次
        for _ in range(count):
            if random.random() < 0.2:  # 20%概率生成弓箭手
                enemy = Enemy("archer", wave)
            elif random.random() < 0.3:  # 30%概率生成史莱姆
                enemy = Enemy("slime", wave)
            else:  # 50%概率生成普通敌人
                enemy = Enemy("normal", wave)
            
            # 每个敌人都有5%概率转化为特殊敌人
            if random.random() < 0.05:
                enemy.type = "special"
                enemy.is_special = True
                enemy._init_attrs(enemy.rect.x, enemy.rect.y)  # 重新初始化特殊敌人的属性
            
            enemies.append(enemy)
    
    return enemies