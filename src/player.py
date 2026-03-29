# src/player.py
# src/player.py
import pygame
from config.setting import SCREEN_WIDTH, SCREEN_HEIGHT
from config.weapons import BASE_WEAPON_CONFIG

class Player:
    def __init__(self, char):
        """
        初始化玩家
        :param char: 角色配置字典
        """
        self.rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 32, 32)
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
        
        # 鼠标状态跟踪
        self.mouse_pressed_last_frame = False
        self.last_pistol_shot = 0  # 用于限制按住鼠标时的射速
        
        # 受击无敌配置
        self.invincible = False
        self.invincible_time = 1500  # 无敌1.5秒
        self.invincible_timer = 0
        self.flash_frequency = 100  # 闪烁间隔
        self.last_flash = 0
        
        # 终极技能配置
        self.ultimate = char["ultimate"]
        self.ultimate_cd = 0  # 当前CD（秒）
        self.ultimate_active = False  # 技能是否激活
        self.ultimate_timer = 0  # 技能持续时间计时器
        
        # 射手攻速加成缓存（用于技能结束后恢复）
        self.original_atk_speeds = {wp: BASE_WEAPON_CONFIG[wp]["atk_speed"] for wp in BASE_WEAPON_CONFIG.keys()}
        
        # 机器人护盾
        self.shield_hits = 0
        self.shield_active = False
        
        # 移动方向记录
        self.last_move_x = 0
        self.last_move_y = 0

    def move(self):
        """处理玩家移动"""
        k = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        
        if k[pygame.K_a] and self.rect.x > 0: 
            move_x -= self.speed
        if k[pygame.K_d] and self.rect.x < SCREEN_WIDTH - 32: 
            move_x += self.speed
        if k[pygame.K_w] and self.rect.y > 0: 
            move_y -= self.speed
        if k[pygame.K_s] and self.rect.y < SCREEN_HEIGHT - 32: 
            move_y += self.speed
        
        # 更新位置
        self.rect.x += move_x
        self.rect.y += move_y
        
        # 更新移动方向
        if move_x != 0 or move_y != 0:
            # 归一化移动向量
            magnitude = (move_x**2 + move_y**2)**0.5
            if magnitude > 0:
                self.last_move_x = move_x / magnitude
                self.last_move_y = move_y / magnitude

    def get_weapon_dmg(self, weapon_name):
        """
        获取武器伤害
        :param weapon_name: 武器名称
        :return: 武器伤害值
        """
        lvl = self.unlocked_weapons.get(weapon_name, 0)
        cfg = BASE_WEAPON_CONFIG[weapon_name]
        return cfg["base_dmg"] + (lvl - 1) * cfg["upgrade"]

    def unlock_or_upgrade_weapon(self, weapon_name):
        """
        解锁或升级武器
        :param weapon_name: 武器名称
        :return: 操作结果提示
        """
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
        """更新无敌状态"""
        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincible_timer >= self.invincible_time:
                self.invincible = False
            self.last_flash = now if now - self.last_flash >= self.flash_frequency else self.last_flash

    def take_damage(self):
        """
        处理玩家受到伤害
        :return: 是否成功处理伤害
        """
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

    def pick_health_pack(self, heal_amount):
        """
        拾取血包
        :param heal_amount: 恢复血量
        :return: 操作结果提示
        """
        if self.hp < self.max_hp:
            self.hp = min(self.hp + heal_amount, self.max_hp)
            return f"拾取血包！HP+{heal_amount}！"
        return "HP已满，无法拾取血包！"

    def update_ultimate(self, dt, enemies, bullets):
        """
        更新终极技能状态
        :param dt: 时间增量
        :param enemies: 敌人列表
        :param bullets: 子弹列表
        """
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

    def cast_ultimate(self):
        """
        释放终极技能
        :return: 技能释放结果提示
        """
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

    def fire_all_weapons(self, enemies, bullets, monster_bullets, dt, mouse_clicked):
        """
        所有武器开火
        :param enemies: 敌人列表
        :param bullets: 子弹列表
        :param monster_bullets: 怪物子弹列表
        :param dt: 时间增量
        :param mouse_clicked: 鼠标是否点击
        """
        current_time = pygame.time.get_ticks()
        self.update_invincible()
        
        for weapon_name in self.unlocked_weapons:
            cfg = BASE_WEAPON_CONFIG[weapon_name]
            weapon_dmg = self.get_weapon_dmg(weapon_name)
            total_dmg = self.base_damage + weapon_dmg
            
            if weapon_name == "普通手枪":
                # 获取当前鼠标状态
                mouse_pressed = pygame.mouse.get_pressed()[0]  # 获取鼠标左键状态
                
                # 检测鼠标是否刚被按下（从释放变为按下）
                mouse_just_pressed = mouse_pressed and not self.mouse_pressed_last_frame
                
                # 更新鼠标状态
                self.mouse_pressed_last_frame = mouse_pressed
                
                # 单击模式：鼠标刚按下且不在冷却期内
                if mouse_just_pressed and current_time - self.last_shot > 50:  # 单击模式：更快的射速（每0.05秒）
                    mx, my = pygame.mouse.get_pos()
                    px, py = self.rect.center
                    dx, dy = mx - px, my - py
                    d = (dx**2 + dy**2)**0.5 + 0.01
                    dx, dy = dx/d, dy/d
                    bullets.append(["pistol", px, py, dx*10, dy*10, total_dmg, 0])
                    self.last_shot = current_time
                # 按住模式：鼠标持续按下但不在单击冷却期内
                elif mouse_pressed and not mouse_just_pressed and current_time - self.last_shot > 500:  # 按住模式：限制射速（每0.5秒）
                    mx, my = pygame.mouse.get_pos()
                    px, py = self.rect.center
                    dx, dy = mx - px, my - py
                    d = (dx**2 + dy**2)**0.5 + 0.01
                    dx, dy = dx/d, dy/d
                    bullets.append(["pistol", px, py, dx*10, dy*10, total_dmg, 0])
                    self.last_shot = current_time
                self.weapon_timers[weapon_name] = 0
                continue
            
            self.weapon_timers[weapon_name] += dt
            if self.weapon_timers[weapon_name] < cfg["atk_speed"]:
                continue
            
            self.weapon_timers[weapon_name] = 0
            
            # 找到最近的敌人
            target = min(enemies, key=lambda e: (e.rect.centerx - self.rect.centerx)**2 + (e.rect.centery - self.rect.centery)**2)
            tx, ty = target.rect.center
            px, py = self.rect.center
            dx, dy = tx - px, ty - py
            d = (dx**2 + dy**2)**0.5 + 0.01
            dx, dy = dx/d, dy/d
            
            if weapon_name == "霰弹枪":
                for off in [-0.2, -0.1, 0, 0.1, 0.2]:
                    c = pygame.math.Vector2(dx, dy).rotate(off * 80)
                    bullets.append(["shotgun", px, py, c.x*8, c.y*8, total_dmg//2 + 1, 0])
            elif weapon_name == "激光枪":
                bullets.append(["laser", px, py, dx*12, dy*12, total_dmg, 5])
            elif weapon_name == "圣剑":
                for e in enemies:
                    dist = ((e.rect.centerx - px)**2 + (e.rect.centery - py)**2)**0.5
                    if dist < 150:
                        e.hp -= total_dmg
                        bullets.append(["sword", e.rect.centerx, e.rect.centery, 0, 0, 0, 15])