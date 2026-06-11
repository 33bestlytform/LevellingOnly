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
        # 生成三个随机生成区域（左侧或右侧边缘）
        spawn_zones = []
        for _ in range(3):
            # 随机选择在左边缘或右边缘生成
            side = random.choice([-50, SCREEN_WIDTH + 50])
            # Y坐标随机分布在整个屏幕高度
            y = random.randint(0, SCREEN_HEIGHT)
            spawn_zones.append((side, y))
        
        # 将敌人分配到三个区域，每个区域随机数量
        remaining = count
        for i in range(3):
            if i == 2:
                # 最后一个区域拿剩余所有敌人
                zone_count = remaining
            else:
                # 前两个区域随机分配，保证至少每个区域有一个敌人
                min_count = max(1, remaining - (count // 2))
                max_count = remaining - 2
                if min_count > max_count:
                    zone_count = remaining // 2
                else:
                    zone_count = random.randint(min_count, max_count)
            remaining -= zone_count
            
            # 在当前区域生成敌人
            side, base_y = spawn_zones[i]
            for _ in range(zone_count):
                if random.random() < 0.2:  # 20%概率生成弓箭手
                    enemy = Enemy("archer", wave)
                elif random.random() < 0.3:  # 30%概率生成史莱姆
                    enemy = Enemy("slime", wave)
                else:  # 50%概率生成普通敌人
                    enemy = Enemy("normal", wave)
                
                # 在区域内随机分散，允许重叠
                random_y = base_y + random.randint(-100, 100)
                random_y = max(0, min(SCREEN_HEIGHT, random_y))
                enemy._init_attrs(side, random_y)
                
                # 每个敌人都有5%概率转化为特殊敌人
                if random.random() < 0.05:
                    enemy.type = "special"
                    enemy.is_special = True
                    enemy._init_attrs(side, random_y)  # 重新初始化特殊敌人的属性
                
                enemies.append(enemy)
    
    return enemies