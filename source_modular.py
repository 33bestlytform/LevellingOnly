import pygame
import random
import sys
from settings import (
    SW, SH, WEAPONS, WEAPON_SPEED
)

pygame.init()
screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("我独自升级")
clock = pygame.time.Clock()
# 字体设置 - 使用微软雅黑
font = pygame.font.SysFont("Microsoft YaHei", 32)
big_font = pygame.font.SysFont("Microsoft YaHei", 48)
small_font = pygame.font.SysFont("Microsoft YaHei", 24)

# 武器基础配置（用于重新开始时重置）
BASE_WEAPON_CONFIG = {
    "普通手枪": {"base_dmg": 0, "upgrade": 1, "max_level": 10, "atk_speed": 0.25, "type": "click"},
    "霰弹枪": {"base_dmg": 1, "upgrade": 1, "max_level": 8, "atk_speed": 1.2, "type": "auto"},
    "激光枪": {"base_dmg": 2, "upgrade": 1, "max_level": 6, "atk_speed": 1.5, "type": "auto"},
    "圣剑": {"base_dmg": 3, "upgrade": 2, "max_level": 5, "atk_speed": 1.2, "type": "auto"}
}

# 角色属性（新增终极技能配置，不改动原有属性）
CHARACTERS = [
    {"name":"战士","hp":15,"speed":4,"damage":2,"desc":"血厚攻高",
     "ultimate": {"name": "烈焰光圈", "type": "aoe", "cd": 20, "duration": 1.5, "radius": 180, "dmg": 15}},
    {"name":"射手","hp":8,"speed":6,"damage":1,"desc":"攻速飞快",
     "ultimate": {"name": "极速射击", "type": "speedup", "cd": 20, "duration": 5, "multiplier": 0.5}},
    {"name":"忍者","hp":10,"speed":8,"damage":1,"desc":"极致灵活",
     "ultimate": {"name": "暗影无敌", "type": "invincible", "cd": 20, "duration": 3}},
    {"name":"机器人","hp":20,"speed":3,"damage":3,"desc":"超级肉盾",
     "ultimate": {"name": "能量护盾", "type": "shield", "cd": 20, "duration": 10, "hits": 3}}
]

# 全局变量
mouse_clicked = False
weapon_drop_rect = None
dropped_weapon = None
# 新增：血包列表（存储掉落的血包信息）
health_packs = []
# 血包配置：掉落概率、恢复血量、大小、颜色
HEALTH_PACK_CONFIG = {
    "drop_chance": 0.03,  # 3%概率掉落
    "heal_amount": 3,     # 恢复3点血
    "size": 20,           # 血包碰撞框大小
    "color": (255, 0, 0)  # 红色血包
}

# 怪物类型枚举：新增boss类型
MONSTER_TYPES = ["normal", "archer", "slime", "special", "boss"]

# 史莱姆分裂配置：保持不变
SLIME_SIZE = {
    "big": {"size": 40, "hp": 5, "split_to": "mid", "speed": 1.0},
    "mid": {"size": 25, "hp": 2, "split_to": "small", "speed": 1.5},
    "small": {"size": 15, "hp": 1, "split_to": None, "speed": 2.0}
}

class Player:
    def __init__(self, char):
        self.rect = pygame.Rect(SW//2, SH//2, 32,32)
        self.max_hp = char["hp"]
        self.hp = self.max_hp
        self.speed = char["speed"]
        self.base_damage = char["damage"]
        self.level = 1
        self.upgrade_wait = False
        self.char_name = char["name"]
        self.money = 0
        self.shop_open = False
        self.last_shot = 0
        # 武器核心（使用基础配置初始化）
        self.unlocked_weapons = {list(BASE_WEAPON_CONFIG.keys())[0]: 1}
        self.weapon_timers = {wp: 0 for wp in BASE_WEAPON_CONFIG.keys()}
        # 受击无敌配置
        self.invincible = False
        self.invincible_time = 1500  # 无敌1.5秒
        self.invincible_timer = 0
        self.flash_frequency = 100  # 闪烁间隔
        self.last_flash = 0
        # 终极技能配置（新增，不影响原有逻辑）
        self.ultimate = char["ultimate"]
        self.ultimate_cd = 0  # 当前CD（秒）
        self.ultimate_active = False  # 技能是否激活
        self.ultimate_timer = 0  # 技能持续时间计时器
        # 射手攻速加成缓存（用于技能结束后恢复）
        self.original_atk_speeds = {wp: BASE_WEAPON_CONFIG[wp]["atk_speed"] for wp in BASE_WEAPON_CONFIG.keys()}
        # 机器人护盾（新增）
        self.shield_hits = 0
        self.shield_active = False

    def move(self):
        k = pygame.key.get_pressed()
        if k[pygame.K_a] and self.rect.x > 0: self.rect.x -= self.speed
        if k[pygame.K_d] and self.rect.x < SW-32: self.rect.x += self.speed
        if k[pygame.K_w] and self.rect.y > 0: self.rect.y -= self.speed
        if k[pygame.K_s] and self.rect.y < SH-32: self.rect.y += self.speed

    def get_weapon_dmg(self, weapon_name):
        lvl = self.unlocked_weapons.get(weapon_name, 0)
        cfg = BASE_WEAPON_CONFIG[weapon_name]
        return cfg["base_dmg"] + (lvl - 1) * cfg["upgrade"]

    def unlock_or_upgrade_weapon(self, weapon_name):
        if weapon_name not in self.unlocked_weapons:
            self.unlocked_weapons[weapon_name] = 1
            return f"获得{weapon_name}！"
        else:
            max_lvl = BASE_WEAPON_CONFIG[weapon_name]["max_level"]
            if self.unlocked_weapons[weapon_name] < max_lvl:
                self.unlocked_weapons[weapon_name] += 1
                return f"{weapon_name}升级到Lv{self.unlocked_weapons[weapon_name]}！"
            else:
                return f"{weapon_name}已达满级Lv{max_lvl}！"

    def update_invincible(self):
        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincible_timer >= self.invincible_time:
                self.invincible = False
            self.last_flash = now if now - self.last_flash >= self.flash_frequency else self.last_flash

    # 重写take_damage：机器人护盾闪烁时保持无敌，抵挡次数不减少
    def take_damage(self):
        # 机器人护盾+无敌闪烁时：仅保持无敌，不消耗护盾次数
        if self.shield_active and self.invincible:
            return True
        # 机器人护盾优先抵挡伤害（未闪烁时）
        if self.shield_active and self.shield_hits > 0:
            self.shield_hits -= 1
            if self.shield_hits <= 0:
                self.shield_active = False
            # 触发无敌闪烁
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            self.last_flash = self.invincible_timer
            return True
        # 原有受击逻辑不变
        if not self.invincible:
            self.hp -= 1
            self.invincible = True
            self.invincible_timer = pygame.time.get_ticks()
            self.last_flash = self.invincible_timer
            return True
        return False

    # 新增：血包拾取恢复血量（不超过上限）
    def pick_health_pack(self, heal_amount):
        if self.hp < self.max_hp:
            self.hp = min(self.hp + heal_amount, self.max_hp)
            return f"拾取血包！HP+{heal_amount}！"
        return "HP已满，无法拾取血包！"

    # 新增：终极技能更新逻辑
    def update_ultimate(self, dt, enemies, bullets):
        # 更新CD（升级页面dt为0，不计算CD）
        if self.ultimate_cd > 0:
            self.ultimate_cd -= dt
        # 更新技能状态
        if self.ultimate_active:
            self.ultimate_timer -= dt
            # 战士AOE伤害（仅对小怪生效）
            if self.ultimate["type"] == "aoe" and self.ultimate_timer > 0:
                px, py = self.rect.center
                for e in enemies:
                    if e.type != "boss":
                        dist = ((e.rect.centerx - px)**2 + (e.rect.centery - py)**2)**0.5
                        if dist < self.ultimate["radius"]:
                            e.hp -= self.ultimate["dmg"] * dt * 2  # 持续伤害
            # 技能结束重置
            if self.ultimate_timer <= 0:
                self.ultimate_active = False
                # 射手恢复原攻速（使用基础配置）
                if self.ultimate["type"] == "speedup":
                    for wp in BASE_WEAPON_CONFIG.keys():
                        BASE_WEAPON_CONFIG[wp]["atk_speed"] = self.original_atk_speeds[wp]
                # 忍者取消无敌（避免与原有无敌冲突）
                elif self.ultimate["type"] == "invincible" and self.invincible:
                    self.invincible_timer = pygame.time.get_ticks() - self.invincible_time  # 强制结束无敌

    # 新增：释放终极技能（Q键触发）
    def cast_ultimate(self):
        if self.ultimate_cd <= 0 and not self.ultimate_active:
            self.ultimate_active = True
            self.ultimate_timer = self.ultimate["duration"]
            self.ultimate_cd = self.ultimate["cd"]
            # 不同角色技能效果
            if self.ultimate["type"] == "aoe":
                return f"发动{self.ultimate['name']}！"
            elif self.ultimate["type"] == "speedup":
                # 临时降低攻击间隔（攻速翻倍）
                for wp in BASE_WEAPON_CONFIG.keys():
                    BASE_WEAPON_CONFIG[wp]["atk_speed"] *= self.ultimate["multiplier"]
                return f"发动{self.ultimate['name']}！攻速翻倍！"
            elif self.ultimate["type"] == "invincible":
                self.invincible = True
                self.invincible_timer = pygame.time.get_ticks() + self.ultimate["duration"] * 1000
                return f"发动{self.ultimate['name']}！免疫伤害！"
            elif self.ultimate["type"] == "shield":
                self.shield_active = True
                self.shield_hits = self.ultimate["hits"]
                return f"发动{self.ultimate['name']}！抵挡{self.ultimate['hits']}次伤害！"
        return "终极技能冷却中！"

    # 原有方法保持不变（改用BASE_WEAPON_CONFIG）
    def fire_all_weapons(self, enemies, bullets, monster_bullets, dt):
        global mouse_clicked
        current_time = pygame.time.get_ticks()
        self.update_invincible()
        for weapon_name in self.unlocked_weapons:
            cfg = BASE_WEAPON_CONFIG[weapon_name]
            weapon_dmg = self.get_weapon_dmg(weapon_name)
            total_dmg = self.base_damage + weapon_dmg
            if weapon_name == "普通手枪":
                if mouse_clicked and current_time - self.last_shot > 100:
                    mx, my = pygame.mouse.get_pos()
                    px, py = self.rect.center
                    dx, dy = mx - px, my - py
                    d = (dx**2 + dy**2)**0.5 + 0.01
                    dx, dy = dx/d, dy/d
                    bullets.append(["pistol", px, py, dx*10, dy*10, total_dmg, 0])
                    self.last_shot = current_time
                    mouse_clicked = False
                continue
            if not enemies or self.upgrade_wait:
                self.weapon_timers[weapon_name] = 0
                continue
            self.weapon_timers[weapon_name] += dt
            if self.weapon_timers[weapon_name] < cfg["atk_speed"]:
                continue
            self.weapon_timers[weapon_name] = 0
            target = min(enemies, key=lambda e: (e.rect.centerx - self.rect.centerx)**2 + (e.rect.centery - self.rect.centery)**2)
            tx, ty = target.rect.center
            px, py = self.rect.center
            dx, dy = tx - px, ty - py
            d = (dx**2 + dy**2)**0.5 + 0.01
            dx, dy = dx/d, dy/d
            if weapon_name == "霰弹枪":
                for off in [-0.2, -0.1, 0, 0.1, 0.2]:
                    c = pygame.math.Vector2(dx, dy).rotate(off * 80)
                    bullets.append(["shotgun", px, py, c.x*8, c.y*8, total_dmg//2 +1, 0])
            elif weapon_name == "激光枪":
                bullets.append(["laser", px, py, dx*12, dy*12, total_dmg, 5])
            elif weapon_name == "圣剑":
                for e in enemies:
                    dist = ((e.rect.centerx - px)**2 + (e.rect.centery - py)**2)**0.5
                    if dist < 120:
                        e.hp -= total_dmg
                        bullets.append(["sword", e.rect.centerx, e.rect.centery, 0, 0, 0, 15])

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
        # 初始生成位置（BOSS体型更大，调整生成范围）
        if self.is_boss:
            side = random.choice([-100, SW + 100])
            y = random.randint(100, SH - 100)
        else:
            side = random.choice([-50, SW + 50])
            y = random.randint(0, SH)
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
            self.speed = random.uniform(1.2, 2.7)
            self.color = (220, 50, 50)
            self.drop_money = random.randint(1, 3) + self.wave // 5
            self.drop_weapon = None
        elif self.type == "archer":
            self.size = 26
            self.base_hp = 1 + self.hp_grow
            self.speed = random.uniform(1.0, 2.0)
            self.color = (50, 100, 220)
            self.drop_money = random.randint(2, 4) + self.wave // 5
            self.drop_weapon = None
        elif self.type == "slime":
            self.slime_grade = "big"
            slime_cfg = SLIME_SIZE[self.slime_grade]
            self.size = slime_cfg["size"]
            self.base_hp = slime_cfg["hp"] + self.hp_grow
            self.speed = slime_cfg["speed"]
            self.color = (50, 220, 100)
            self.drop_money = random.randint(3, 5) + self.wave // 5
            self.drop_weapon = None
        elif self.type == "special":
            self.size = 32
            self.base_hp = 3 + self.hp_grow * 1.2
            self.speed = random.uniform(1.8, 2.5)
            self.color = (150, 0, 200)
            self.drop_money = random.randint(5, 10) + self.wave // 3
            self.drop_weapon = random.choice(list(BASE_WEAPON_CONFIG.keys())[1:]) if self.is_special else None
        # 新增BOSS属性（血量厚、体型大、伤害高）
        elif self.type == "boss":
            self.size = 80
            self.base_hp = 50 + self.hp_grow * 5  # BOSS血量是普通怪的5倍+
            self.boss_max_hp = self.base_hp  # 记录最大血量
            self.speed = random.uniform(0.8, 1.2)  # BOSS移速较慢
            self.color = (255, 0, 100)  # 专属红色外观
            self.drop_money = random.randint(50, 100)  # 掉落大量金币
            self.drop_weapon = random.choice(list(BASE_WEAPON_CONFIG.keys())[1:]) if random.random() > 0.3 else None  # 高概率掉武器
        # 修正血量为整数
        self.hp = max(1, int(self.base_hp))
        self.rect = pygame.Rect(x, y, self.size, self.size)

    # 原有方法保持不变，新增BOSS射击逻辑
    def move_to(self, p):
        dx = p.rect.centerx - self.rect.centerx
        dy = p.rect.centery - self.rect.centery
        d = (dx**2 + dy**2)**0.5 + 0.01
        self.rect.x += dx / d * self.speed
        self.rect.y += dy / d * self.speed
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
        # BOSS发射3颗散射子弹，伤害更高
        if self.is_boss:
            for off in [-0.1, 0, 0.1]:
                c = pygame.math.Vector2(dx, dy).rotate(off * 30)
                monster_bullets.append(["boss", tx, ty, c.x*9, c.y*9, 2])  # BOSS子弹伤害2点
        else:
            monster_bullets.append(["archer", tx, ty, dx*7, dy*7, 1])

    # 原有方法保持不变
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

# 重写wave_spawn，每5波生成BOSS
def wave_spawn(n, wave):
    enemies = []
    # 每5波生成1个BOSS，减少小怪数量
    if wave % 5 == 0:
        enemies.append(Enemy("boss", wave))
        n = n // 2  # BOSS战小怪数量减半
    else:
        enemies.append(Enemy("special", wave, is_special=True))
    # 原有怪物占比逻辑不变
    archer_rate = min(0.4, wave * 0.07)
    slime_rate = min(0.35, wave * 0.08)
    normal_rate = 1 - archer_rate - slime_rate
    monster_pool = []
    monster_pool += ["archer"] * int((n-1)*archer_rate)
    monster_pool += ["slime"] * int((n-1)*slime_rate)
    monster_pool += ["normal"] * ((n-1) - len(monster_pool))
    random.shuffle(monster_pool)
    for m_type in monster_pool:
        enemies.append(Enemy(m_type, wave))
    random.shuffle(enemies)
    return enemies

# 原有工具函数保持不变
def draw_text(s, x, y, color=(255,255,255)):
    surf = font.render(s, True, color)
    screen.blit(surf, (x, y))

def draw_big(s, x, y, color=(255,220,0)):
    surf = big_font.render(s, True, color)
    screen.blit(surf, (x, y))

def draw_small(s, x, y, color=(255,255,255)):
    surf = small_font.render(s, True, color)
    screen.blit(surf, (x, y))

def generate_upgrades():
    pool = [
        ("生命+3", lambda p: setattr(p, 'max_hp', p.max_hp+3) or setattr(p, 'hp', p.hp+3)),
        ("基础伤害+1", lambda p: setattr(p, 'base_damage', p.base_damage+1)),
        ("全武器攻速+", lambda p: [BASE_WEAPON_CONFIG[wp].update({'atk_speed': max(0.15, BASE_WEAPON_CONFIG[wp]['atk_speed']*0.97)}) for wp in BASE_WEAPON_CONFIG.keys()]),
        ("移速+1", lambda p: setattr(p, 'speed', min(p.speed + 1, 10))),
    ]
    return random.sample(pool, 3)

# 新增：绘制武器掉落
def draw_weapon_drop():
    global weapon_drop_rect, dropped_weapon
    if weapon_drop_rect and dropped_weapon:
        pygame.draw.rect(screen, (150, 0, 200), weapon_drop_rect.inflate(10,10), 3)
        pygame.draw.rect(screen, (120, 0, 180), weapon_drop_rect)
        draw_text(f"拾取{dropped_weapon}", weapon_drop_rect.x+10, weapon_drop_rect.y+5, (255,255,255))

# 新增：绘制BOSS血量条
def draw_boss_hp(boss):
    if boss:
        bar_width = 300
        bar_height = 20
        x = SW//2 - bar_width//2
        y = 20
        # 血量条背景
        pygame.draw.rect(screen, (100,100,100), (x-2, y-2, bar_width+4, bar_height+4))
        # 当前血量条（红色）
        hp_ratio = boss.hp / boss.boss_max_hp
        pygame.draw.rect(screen, (255,0,0), (x, y, int(bar_width * hp_ratio), bar_height))
        # 血量文字
        draw_small(f"BOSS HP: {int(boss.hp)}/{int(boss.boss_max_hp)}", x, y+25, (255,255,0))

# 新增：绘制终极技能UI（右下角）
def draw_ultimate_ui(p):
    cd_ratio = p.ultimate_cd / p.ultimate["cd"]
    cd_color = (0,255,0) if cd_ratio <= 0 else (255,0,0)
    # 技能框背景
    pygame.draw.rect(screen, (50,50,50), (SW-120, SH-80, 100, 60))
    pygame.draw.rect(screen, cd_color, (SW-115, SH-75, 90, 50), 3)
    # CD文字或技能名称
    if p.ultimate_cd > 0:
        draw_small(f"CD: {int(p.ultimate_cd)}s", SW-105, SH-65)
    else:
        draw_small(f"Q: {p.ultimate['name']}", SW-110, SH-65)
    # 机器人护盾剩余次数提示
    if p.shield_active:
        draw_small(f"护盾: {p.shield_hits}次", SW-200, SH-40, (0,255,255))

# 新增：绘制血包（红色圆形，带十字标记）
def draw_health_packs():
    for hp in health_packs:
        # 血包主体（红色圆形）
        pygame.draw.circle(screen, HEALTH_PACK_CONFIG["color"], (hp["x"], hp["y"]), HEALTH_PACK_CONFIG["size"]//2)
        # 十字标记（白色）
        x, y = hp["x"], hp["y"]
        size = HEALTH_PACK_CONFIG["size"]//3
        pygame.draw.line(screen, (255,255,255), (x-size, y), (x+size, y), 2)
        pygame.draw.line(screen, (255,255,255), (x, y-size), (x, y+size), 2)

def character_select():
    selected = 0
    while True:
        screen.fill((0,0,0))
        draw_big("我独自升级", SW//2 - 100, 100)
        for i, c in enumerate(CHARACTERS):
            y = 200 + i * 60
            col = (0,255,0) if i == selected else (200,200,200)
            draw_text(f"{i+1}.{c['name']} | {c['desc']}", SW//2 - 150, y, col)
            # 显示终极技能名称
            draw_text(f"HP:{c['hp']} 移速:{c['speed']} 终极:{c['ultimate']['name']}", SW//2 - 150, y+30, (180,180,180))
        draw_text("1/2/3/4选择 ↑↓选择 回车确认", SW//2 - 180, SH - 60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            selected = (selected + 1) % 4
            pygame.time.delay(150)
        if keys[pygame.K_UP]:
            selected = (selected - 1) % 4
            pygame.time.delay(150)
        if keys[pygame.K_1]: selected = 0
        if keys[pygame.K_2]: selected = 1
        if keys[pygame.K_3]: selected = 2
        if keys[pygame.K_4]: selected = 3
        if keys[pygame.K_RETURN]:
            return CHARACTERS[selected]
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(result, wave, char_name):
    while True:
        screen.fill((0,0,0))
        if result == "win":
            draw_big("挑战成功!", SW//2 - 100, SH//2 - 80)
        else:
            draw_big("挑战失败", SW//2 - 80, SH//2 - 80)
        draw_text(f"角色: {char_name}", SW//2 - 50, SH//2)
        draw_text(f"坚持到第 {wave} 波", SW//2 - 70, SH//2 + 40)
        draw_text("按 ENTER 返回主页", SW//2 - 110, SH//2 + 120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # 重置攻速配置（关键：重新开始时恢复基础攻速）
                for wp in BASE_WEAPON_CONFIG.keys():
                    BASE_WEAPON_CONFIG[wp]["atk_speed"] = {
                        "普通手枪": 0.25,
                        "霰弹枪": 1.2,
                        "激光枪": 1.5,
                        "圣剑": 1.2
                    }[wp]
                pygame.time.delay(200)
                return
        pygame.display.flip()
        clock.tick(60)

def main():
    global mouse_clicked, weapon_drop_rect, dropped_weapon, health_packs
    while True:
        # 每次重新开始前重置全局状态
        health_packs = []
        mouse_clicked = False
        weapon_drop_rect = None
        dropped_weapon = None
        # 重置攻速配置（关键：避免重复叠加）
        for wp in BASE_WEAPON_CONFIG.keys():
            BASE_WEAPON_CONFIG[wp]["atk_speed"] = {
                "普通手枪": 0.25,
                "霰弹枪": 1.2,
                "激光枪": 1.5,
                "圣剑": 1.2
            }[wp]
        
        char = character_select()
        p = Player(char)
        bullets = []
        monster_bullets = []
        wave = 1
        enemies = wave_spawn(6 + wave * 2, wave)
        run = True
        upgrades = []
        start_time = pygame.time.get_ticks()
        survive_goal = 10 * 60 * 1000
        shop_notice = ""
        shop_notice_time = 0
        # 新增：血包拾取提示
        health_notice = ""
        health_notice_time = 0
        # 商店物品修改：新增购买次数记录（用于1.2倍涨价）
        shop_items = [
            ("生命+2", 10, 0, lambda pl: setattr(pl, 'max_hp', pl.max_hp+2) or setattr(pl, 'hp', pl.hp+2)),
            ("基础伤害+1", 15, 0, lambda pl: setattr(pl, 'base_damage', pl.base_damage+1)),
            ("全武器攻速提升", 20, 0, lambda pl: [BASE_WEAPON_CONFIG[wp].update({'atk_speed': max(0.15, BASE_WEAPON_CONFIG[wp]['atk_speed']*0.97)}) for wp in BASE_WEAPON_CONFIG.keys()]),
            ("移速+1", 10, 0, lambda pl: setattr(pl, 'speed', min(pl.speed+1, 10))),
        ]
        # 终极技能提示文字
        ultimate_notice = ""
        ultimate_notice_time = 0
        while run:
            # 升级页面暂停计时：dt设为0，不更新CD、生存时间
            if not p.upgrade_wait:
                dt = clock.tick(60) / 1000
                now = pygame.time.get_ticks()
                elapsed = now - start_time
                if elapsed >= survive_goal:
                    game_over_screen("win", wave, p.char_name)
                    break
            else:
                dt = 0  # 暂停时不计算时间
                clock.tick(60)
            
            screen.fill((18, 18, 22))
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True
                    if weapon_drop_rect and weapon_drop_rect.collidepoint(pygame.mouse.get_pos()):
                        shop_notice = p.unlock_or_upgrade_weapon(dropped_weapon)
                        shop_notice_time = pygame.time.get_ticks()
                        weapon_drop_rect = None
                        dropped_weapon = None
                if event.type == pygame.KEYDOWN:
                    # 新增：Q键释放终极技能（仅非升级页面生效）
                    if event.key == pygame.K_q and not p.upgrade_wait:
                        ultimate_notice = p.cast_ultimate()
                        ultimate_notice_time = pygame.time.get_ticks()
                    # 升级页面按键逻辑不变
                    if p.upgrade_wait:
                        if event.key == pygame.K_1 and len(upgrades)>=1:
                            upgrades[0][1](p)
                            p.upgrade_wait = False
                            enemies = wave_spawn(6 + wave * 2, wave)
                        if event.key == pygame.K_2 and len(upgrades)>=2:
                            upgrades[1][1](p)
                            p.upgrade_wait = False
                            enemies = wave_spawn(6 + wave * 2, wave)
                        if event.key == pygame.K_3 and len(upgrades)>=3:
                            upgrades[2][1](p)
                            p.upgrade_wait = False
                            enemies = wave_spawn(6 + wave * 2, wave)
                    else:
                        # 商店开关逻辑不变
                        if event.key == pygame.K_b:
                            p.shop_open = not p.shop_open
                            shop_notice = ""
                        # 商店购买逻辑修改：1.2倍涨价（四舍五入取整）
                        if p.shop_open:
                            idx = -1
                            if event.key == pygame.K_1: idx = 0
                            if event.key == pygame.K_2: idx = 1
                            if event.key == pygame.K_3: idx = 2
                            if event.key == pygame.K_4: idx = 3
                            if 0 <= idx < len(shop_items):
                                name, base_price, count, effect = shop_items[idx]
                                # 核心修改：1.2倍涨价，round()取整
                                current_price = round(base_price * (1.2 ** count))
                                if p.money >= current_price:
                                    p.money -= current_price
                                    effect(p)
                                    # 更新购买次数
                                    shop_items[idx] = (name, base_price, count + 1, effect)
                                    # 计算下次价格并提示
                                    next_price = round(base_price * (1.2 ** (count + 1)))
                                    shop_notice = f"购买{name}成功！下次{next_price}金币"
                                    shop_notice_time = pygame.time.get_ticks()
                                else:
                                    shop_notice = f"金币不足！需要{current_price}金币"
                                    shop_notice_time = pygame.time.get_ticks()
            # 非升级页面才更新游戏逻辑
            if not p.upgrade_wait:
                # 新增：血包碰撞拾取检测
                new_health_packs = []
                for hp in health_packs:
                    # 创建血包碰撞框
                    hp_rect = pygame.Rect(
                        hp["x"] - HEALTH_PACK_CONFIG["size"]//2,
                        hp["y"] - HEALTH_PACK_CONFIG["size"]//2,
                        HEALTH_PACK_CONFIG["size"],
                        HEALTH_PACK_CONFIG["size"]
                    )
                    # 检测玩家与血包碰撞
                    if p.rect.colliderect(hp_rect):
                        # 拾取血包，显示提示
                        health_notice = p.pick_health_pack(HEALTH_PACK_CONFIG["heal_amount"])
                        health_notice_time = pygame.time.get_ticks()
                    else:
                        # 未拾取的血包保留
                        new_health_packs.append(hp)
                health_packs = new_health_packs

                # 新增：更新终极技能
                p.update_ultimate(dt, enemies, bullets)
                # 原有逻辑不变
                p.fire_all_weapons(enemies, bullets, monster_bullets, dt)
                p.move()
                # 怪物逻辑：记录当前BOSS
                boss = None
                for e in enemies:
                    if e.is_boss:
                        boss = e
                    e.move_to(p)
                    e.shoot(p, monster_bullets, dt)
                    if e.rect.colliderect(p.rect):
                        if p.take_damage() and p.hp <= 0:
                            game_over_screen("lose", wave, p.char_name)
                            run = False
                            break
                if not run:
                    break
                # 玩家子弹处理不变
                new_bullets = []
                for b in bullets:
                    t, x, y, vx, vy, dmg, pierce = b
                    x += vx
                    y += vy
                    bullet_rect = pygame.Rect(x, y, 6, 6) if t!="sword" else None
                    hit_enemies = []
                    if t == "laser" and pierce > 0:
                        for e in enemies:
                            if e.rect.colliderect(bullet_rect) and e not in hit_enemies:
                                e.hp -= dmg
                                hit_enemies.append(e)
                                pierce -= 1
                                if pierce <= 0:
                                    break
                    elif t in ["pistol", "shotgun"]:
                        hit = False
                        for e in enemies:
                            if e.rect.colliderect(bullet_rect) and not hit:
                                e.hp -= dmg
                                hit = True
                                break
                        if hit:
                            continue
                    elif t == "sword":
                        new_bullets.append([t, x, y, vx, vy, dmg, pierce-1])
                        continue
                    if 0 < x < SW and 0 < y < SH and (pierce > 0 or t in ["pistol", "shotgun"]):
                        new_bullets.append([t, x, y, vx, vy, dmg, pierce])
                bullets = new_bullets
                # 怪物子弹处理不变（BOSS子弹伤害更高）
                new_monster_bullets = []
                for b in monster_bullets:
                    t, x, y, vx, vy, dmg = b
                    x += vx
                    y += vy
                    bullet_rect = pygame.Rect(x, y, 5, 5)
                    if bullet_rect.colliderect(p.rect):
                        if p.take_damage() and p.hp <= 0:
                            game_over_screen("lose", wave, p.char_name)
                            run = False
                            break
                    if 0 < x < SW and 0 < y < SH:
                        new_monster_bullets.append([t, x, y, vx, vy, dmg])
                monster_bullets = new_monster_bullets
                if not run:
                    break
                # 敌人死亡判定不变（BOSS掉落更丰厚）
                alive = []
                for e in enemies:
                    if e.hp > 0:
                        alive.append(e)
                    else:
                        p.money += e.drop_money
                        if e.type == "slime":
                            alive += e.split_slime()
                        if (e.is_special or e.is_boss) and e.drop_weapon:
                            weapon_drop_rect = pygame.Rect(e.rect.x, e.rect.y, 120, 40)
                            dropped_weapon = e.drop_weapon
                        # 新增：怪物死亡时3%概率掉落血包
                        if random.random() <= HEALTH_PACK_CONFIG["drop_chance"]:
                            health_packs.append({
                                "x": e.rect.centerx,
                                "y": e.rect.centery
                            })
                enemies = alive
                # 清完敌人升级逻辑不变
                if not enemies:
                    wave += 1
                    upgrades = generate_upgrades()
                    p.upgrade_wait = True
                    weapon_drop_rect = None
                    dropped_weapon = None
            # 绘制层：新增BOSS血量条、终极技能UI、战士技能特效、血包
            # 1. 绘制玩家（战士技能特效）
            if not p.invincible or (pygame.time.get_ticks() - p.last_flash) < p.flash_frequency // 2:
                pygame.draw.rect(screen, (0,200,0), p.rect)
            # 战士AOE光圈特效（修复self→p的致命错误）
            if p.ultimate_active and p.ultimate["type"] == "aoe":
                px, py = p.rect.center
                # 核心修复：self.ultimate→p.ultimate
                radius = p.ultimate["radius"] - (p.ultimate_timer / p.ultimate["duration"]) * 50
                pygame.draw.circle(screen, (255,100,0), (int(px), int(py)), int(radius), 3)
            # 2. 绘制敌人（BOSS专属标记）
            for e in enemies:
                pygame.draw.ellipse(screen, e.color, e.rect)
                if e.is_special:
                    draw_text("★", e.rect.x+10, e.rect.y-5, (255,255,0))
                elif e.type == "archer":
                    draw_text("-A", e.rect.x+5, e.rect.y-5, (255,255,255))
                elif e.type == "slime":
                    draw_text("O", e.rect.x+5, e.rect.y-5, (0,0,0))
                elif e.is_boss:
                    draw_big("BOSS", e.rect.x+10, e.rect.y-30, (255,0,0))  # BOSS专属文字
            # 3. 绘制子弹（BOSS子弹更大）
            for b in bullets:
                t, x, y, vx, vy, dmg, pierce = b
                if t == "pistol":
                    pygame.draw.circle(screen, (255,255,0), (int(x), int(y)), 3)
                elif t == "shotgun":
                    pygame.draw.circle(screen, (255,165,0), (int(x), int(y)), 2)
                elif t == "laser":
                    pygame.draw.line(screen, (0,255,255), (int(x-vx*2), int(y-vy*2)), (int(x), int(y)), 2)
                    pygame.draw.circle(screen, (0,255,255), (int(x), int(y)), 4)
                elif t == "sword":
                    radius = 120 - (15 - pierce)*8
                    pygame.draw.circle(screen, (255,200,0), (int(x), int(y)), int(radius), 2)
            # 怪物子弹：BOSS子弹红色更大
            for b in monster_bullets:
                t, x, y, vx, vy, dmg = b
                if t == "boss":
                    pygame.draw.circle(screen, (255, 0, 0), (int(x), int(y)), 5)
                else:
                    pygame.draw.circle(screen, (255, 50, 50), (int(x), int(y)), 3)
            # 4. 原有绘制逻辑不变
            draw_weapon_drop()
            # 新增：绘制血包
            draw_health_packs()
            # 新增：绘制BOSS血量条
            if boss:
                draw_boss_hp(boss)
            # 基础信息显示（新增Q键提示）
            draw_text(f"波数: {wave}", 10, 10)
            draw_text(f"HP: {p.hp}/{p.max_hp}", 10, 50)
            draw_text(f"金币: {p.money}", 10, 90)
            draw_text(f"已解锁武器: {len(p.unlocked_weapons)}/{len(BASE_WEAPON_CONFIG)}", 10, 130)
            draw_text("B=商店  Q=终极技能  鼠标左键=射击/拾取", 10, SH - 40)
            # 已解锁武器绘制不变
            draw_text("已解锁武器：", SW - 200, 10, (255,220,0))
            y_offset = 50
            for wp, lvl in p.unlocked_weapons.items():
                draw_text(f"{wp} Lv{lvl}", SW - 200, y_offset)
                y_offset += 40
            # 商店绘制：显示1.2倍涨价后的当前价格
            if p.shop_open and not p.upgrade_wait:
                pygame.draw.rect(screen, (20,20,40), (SW//2 - 220, 100, 440, 300))
                draw_text("商店（按1-4购买）", SW//2 - 100, 120)
                for i, (name, base_price, count, _) in enumerate(shop_items):
                    current_price = round(base_price * (1.2 ** count))
                    draw_text(f"{i+1}. {name} {current_price}金币", SW//2 - 160, 180 + i * 40)
            # 升级界面绘制不变
            if p.upgrade_wait:
                pygame.draw.rect(screen, (40,20,40), (SW//2 - 200, SH//2 - 100, 400, 300))
                draw_big("选择升级！", SW//2 - 80, SH//2 - 80)
                for i, (name, _) in enumerate(upgrades):
                    draw_text(f"{i+1}. {name}", SW//2 - 100, SH//2 + 20 + i*40, (255,200,100))
            # 提示文字（新增血包拾取提示）
            now_tick = pygame.time.get_ticks()
            if shop_notice and now_tick - shop_notice_time < 2000:
                color = (0,255,0) if "成功" in shop_notice or "获得" in shop_notice else (255,60,60)
                draw_text(shop_notice, SW//2 - 120, SH//2, color)
            if ultimate_notice and now_tick - ultimate_notice_time < 1500:
                draw_text(ultimate_notice, SW//2 - 100, SH//2 - 40, (255,255,0))
            if health_notice and now_tick - health_notice_time < 1500:
                draw_text(health_notice, SW//2 - 100, SH//2 + 40, (0,255,0))
            # 新增：绘制终极技能UI
            draw_ultimate_ui(p)
            pygame.display.flip()

if __name__ == "__main__":
    while True:
        main()