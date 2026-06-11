# src/enemy.py
import pygame
import random
from config.setting import SCREEN_WIDTH, SCREEN_HEIGHT, SLIME_SIZE

# 群聚行为参数
SEPARATION_RADIUS = 60    # 分离检测半径
ALIGNMENT_RADIUS = 150    # 对齐检测半径
SEPARATION_WEIGHT = 0.4   # 分离力度权重
ALIGNMENT_WEIGHT = 0.25   # 对齐力度权重

class Enemy:
    def __init__(self, monster_type, wave, is_special=False):
        self.type = monster_type
        self.is_special = is_special
        self.wave = wave
        self.shoot_timer = 0
        self.shoot_interval = random.uniform(1.5, 2.5)
        # BOSS专属标识
        self.is_boss = monster_type == "boss"
        self.boss_max_hp = 0  # BOSS最大血量（用于绘制血量条）
        # 记录上一帧速度，用于对齐行为
        self.vx = 0
        self.vy = 0
        # 初始生成位置（BOSS体型更大，调整生成范围）
        if self.is_boss:
            side = random.choice([-100, SCREEN_WIDTH + 100])
            y = random.randint(100, SCREEN_HEIGHT - 100)
        else:
            side = random.choice([-50, SCREEN_WIDTH + 50])
            y = random.randint(0, SCREEN_HEIGHT)
        # 血量成长保持原有逻辑
        if wave <= 5:
            self.hp_grow = 0.8 * (wave - 1)
        else:
            self.hp_grow = 0.8 * 4 + (wave - 5) * 1.5
        self._init_attrs(side, y)

    def _init_attrs(self, x, y):
        if self.type == "normal":
            self.size = 28
            self.base_hp = 1 + self.hp_grow
            self.speed = 5
            self.color = (220, 50, 50)
            self.drop_money = random.randint(1, 3) + self.wave // 5
            self.drop_weapon = None
        elif self.type == "archer":
            self.size = 26
            self.base_hp = 1 + self.hp_grow
            self.speed = 5
            self.color = (50, 100, 220)
            self.drop_money = random.randint(2, 4) + self.wave // 5
            self.drop_weapon = None
        elif self.type == "slime":
            self.slime_grade = "big"
            slime_cfg = SLIME_SIZE[self.slime_grade]
            self.size = slime_cfg["size"]
            self.base_hp = slime_cfg["hp"] + self.hp_grow
            self.speed = 5
            self.color = (50, 220, 100)
            self.drop_money = random.randint(3, 5) + self.wave // 5
            self.drop_weapon = None
        elif self.type == "special":
            self.size = 32
            self.base_hp = 3 + self.hp_grow * 1.2
            self.speed = 5
            self.color = (150, 0, 200)
            self.drop_money = random.randint(5, 10) + self.wave // 3
            self.drop_weapon = random.choice(list(["霰弹枪", "激光枪", "圣剑"])) if self.is_special else None
        # 新增BOSS属性（血量厚、体型大、伤害高）
        elif self.type == "boss":
            self.size = 80
            self.base_hp = 50 + self.hp_grow * 5  # BOSS血量是普通怪的5倍+
            self.boss_max_hp = self.base_hp
            self.speed = 5
            self.color = (255, 0, 100)  # 专属红色外观
            self.drop_money = random.randint(50, 100)  # 掉落大量金币
            self.drop_weapon = random.choice(list(["霰弹枪", "激光枪", "圣剑"])) if random.random() > 0.3 else None  # 高概率掉武器
        # 修正血量为整数
        self.hp = max(1, int(self.base_hp))
        self.rect = pygame.Rect(x, y, self.size, self.size)

    def move_to(self, p, enemies):
        # 计算朝向玩家的基础方向
        dx = p.rect.centerx - self.rect.centerx
        dy = p.rect.centery - self.rect.centery
        d = (dx**2 + dy**2)**0.5 + 0.01
        seek_x = dx / d
        seek_y = dy / d

        # 分离：远离附近敌人
        sep_x, sep_y = 0, 0
        sep_count = 0
        for other in enemies:
            if other is self:
                continue
            dist_x = self.rect.centerx - other.rect.centerx
            dist_y = self.rect.centery - other.rect.centery
            dist = (dist_x**2 + dist_y**2)**0.5 + 0.01
            if dist < SEPARATION_RADIUS:
                # 距离越近排斥力越大
                force = (SEPARATION_RADIUS - dist) / SEPARATION_RADIUS
                sep_x += (dist_x / dist) * force
                sep_y += (dist_y / dist) * force
                sep_count += 1

        # 对齐：参考附近敌人的移动方向
        align_x, align_y = 0, 0
        align_count = 0
        for other in enemies:
            if other is self:
                continue
            dist_x = self.rect.centerx - other.rect.centerx
            dist_y = self.rect.centery - other.rect.centery
            dist = (dist_x**2 + dist_y**2)**0.5 + 0.01
            if dist < ALIGNMENT_RADIUS:
                align_x += other.vx
                align_y += other.vy
                align_count += 1

        # 混合三种力：朝向玩家 + 分离 + 对齐
        move_x = seek_x
        move_y = seek_y

        if sep_count > 0:
            move_x += sep_x * SEPARATION_WEIGHT
            move_y += sep_y * SEPARATION_WEIGHT

        if align_count > 0:
            avg_align_x = align_x / align_count
            avg_align_y = align_y / align_count
            move_x += avg_align_x * ALIGNMENT_WEIGHT
            move_y += avg_align_y * ALIGNMENT_WEIGHT

        # 归一化并应用速度
        move_d = (move_x**2 + move_y**2)**0.5 + 0.01
        self.vx = (move_x / move_d) * self.speed
        self.vy = (move_y / move_d) * self.speed

        self.rect.x += self.vx
        self.rect.y += self.vy

        # 弓箭手保持距离逻辑
        if self.type == "archer":
            dist = ((p.rect.centerx - self.rect.centerx)**2 + (p.rect.centery - self.rect.centery)**2)**0.5
            if dist > 300:
                return
            self.rect.x -= dx / d * self.speed
            self.rect.y -= dy / d * self.speed

    # 重写shoot，增加BOSS射击逻辑
    def shoot(self, p, monster_bullets, dt):
        if self.type != "archer" and not self.is_boss:
            return
        # BOSS射击间隔缩短（更快发射）
        if self.is_boss:
            self.shoot_interval = 0.8
        self.shoot_timer += dt
        if self.shoot_timer < self.shoot_interval:
            return
        self.shoot_timer = 0
        px, py = p.rect.center
        tx, ty = self.rect.center
        dx, dy = px - tx, py - ty
        d = (dx**2 + dy**2)**0.5 + 0.01
        dx, dy = dx/d, dy/d
        
        # 对于 archer 类型，添加预判
        if self.type == "archer":
            # 计算距离和预判偏移
            distance = d
            # 根据距离和玩家移动方向计算预判偏移
            # 偏移量与距离成正比，与玩家移动速度相关
            lead_factor = distance * 0.02  # 调整这个值来控制预判程度
            lead_x = p.last_move_x * lead_factor
            lead_y = p.last_move_y * lead_factor
            # 应用预判偏移
            px += lead_x
            py += lead_y
            # 重新计算方向向量
            dx, dy = px - tx, py - ty
            d = (dx**2 + dy**2)**0.5 + 0.01
            dx, dy = dx/d, dy/d
        
        # BOSS发射3颗散射子弹，伤害更高
        if self.is_boss:
            for off in [-0.1, 0, 0.1]:
                c = pygame.math.Vector2(dx, dy).rotate(off * 30)
                monster_bullets.append(["boss", tx, ty, c.x*9, c.y*9, 2])  # BOSS子弹伤害2点
        else:
            monster_bullets.append(["archer", tx, ty, dx*7, dy*7, 1])

    # 史莱姆分裂方法
    def split_slime(self):
        slime_cfg = SLIME_SIZE[self.slime_grade]
        if slime_cfg["split_to"] is None:
            return []
        new_slimes = []
        for i in [-1, 1]:
            offset_x = random.randint(20, 40) * i
            offset_y = random.randint(20, 40) * i
            new_slime = Enemy("slime", self.wave)
            new_slime.slime_grade = slime_cfg["split_to"]
            slime_new_cfg = SLIME_SIZE[new_slime.slime_grade]
            new_slime.size = slime_new_cfg["size"]
            new_slime.hp = max(1, int(slime_new_cfg["hp"] + self.hp_grow))
            new_slime.speed = slime_new_cfg["speed"]
            new_slime.rect = pygame.Rect(self.rect.x + offset_x, self.rect.y + offset_y, new_slime.size, new_slime.size)
            new_slimes.append(new_slime)
        return new_slimes