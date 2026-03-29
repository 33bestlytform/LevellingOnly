# src/game.py
import pygame
import random
import os
from config.setting import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS, FONT, BIG_FONT, SMALL_FONT
from src.player import Player
from src.enemy import Enemy
from src.ui import draw_text, draw_big, draw_small, draw_weapon_drop, draw_boss_hp, draw_ultimate_ui, draw_health_packs
from config.characters import CHARACTERS
from config.weapons import BASE_WEAPON_CONFIG
from config.enemies import wave_spawn
from utils.logger import Logger

class Game:
    def __init__(self):
        """初始化游戏"""
        # 初始化Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("我独自升级")
        self.clock = pygame.time.Clock()
        
        # 初始化日志
        self.logger = Logger()
        
        # 初始化音乐
        self.music_files = self._load_music_files()
        self.current_music_index = -1
        self.last_played = []
        
        # 全局变量
        self.mouse_clicked = False
        self.weapon_drop_rect = None
        self.dropped_weapon = None
        self.health_packs = []
        
    def _load_music_files(self):
        """
        加载音乐文件
        :return: 音乐文件列表
        """
        music_dir = "assets/music"
        if not os.path.exists(music_dir):
            self.logger.warning(f"Music directory {music_dir} not found")
            return []
        
        music_files = []
        for file in os.listdir(music_dir):
            if file.endswith((".mp3", ".wav", ".ogg")):
                music_files.append(os.path.join(music_dir, file))
        
        self.logger.info(f"Loaded {len(music_files)} music files")
        return music_files
    
    def play_next_music(self):
        """播放下一首音乐"""
        if not self.music_files:
            return
        
        # 确保三首内不重复
        available = [i for i in range(len(self.music_files)) if i not in self.last_played]
        if not available:
            self.last_played = []
            available = list(range(len(self.music_files)))
        
        # 随机选择
        self.current_music_index = random.choice(available)
        self.last_played.append(self.current_music_index)
        if len(self.last_played) > 3:
            self.last_played.pop(0)
        
        # 播放音乐
        music_file = self.music_files[self.current_music_index]
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.play(-1)  # 循环播放
            self.logger.info(f"Playing music: {os.path.basename(music_file)}")
        except Exception as e:
            self.logger.error(f"Error playing music: {e}")
    
    def run(self):
        """运行游戏"""
        # 开始播放音乐
        self.play_next_music()
        
        while True:
            # 每次重新开始前重置全局状态
            self.health_packs = []
            self.mouse_clicked = False
            self.weapon_drop_rect = None
            self.dropped_weapon = None
            
            # 重置攻速配置
            for wp in BASE_WEAPON_CONFIG.keys():
                BASE_WEAPON_CONFIG[wp]["atk_speed"] = {
                    "普通手枪": 0.25,
                    "霰弹枪": 1.2,
                    "激光枪": 1.5,
                    "圣剑": 1.2
                }[wp]
            
            # 选择角色
            char = self.character_select()
            if not char:
                break
            
            # 初始化游戏
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
            health_notice = ""
            health_notice_time = 0
            
            # 商店物品
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
                # 检查音乐是否结束
                if not pygame.mixer.music.get_busy():
                    self.play_next_music()
                
                # 升级页面暂停计时
                if not p.upgrade_wait:
                    dt = self.clock.tick(60) / 1000
                    now = pygame.time.get_ticks()
                    elapsed = now - start_time
                    if elapsed >= survive_goal:
                        self.game_over_screen("win", wave, p.char_name)
                        break
                else:
                    dt = 0  # 暂停时不计算时间
                    self.clock.tick(60)
                
                # 填充背景
                self.screen.fill(COLORS["DARK_BLUE"])
                
                # 事件处理
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                        break
                    
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.mouse_clicked = True
                        if self.weapon_drop_rect and self.weapon_drop_rect.collidepoint(pygame.mouse.get_pos()):
                            shop_notice = p.unlock_or_upgrade_weapon(self.dropped_weapon)
                            shop_notice_time = pygame.time.get_ticks()
                            self.weapon_drop_rect = None
                            self.dropped_weapon = None
                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.mouse_clicked = False
                    
                    if event.type == pygame.KEYDOWN:
                        # Q键释放终极技能
                        if event.key == pygame.K_q and not p.upgrade_wait:
                            ultimate_notice = p.cast_ultimate()
                            ultimate_notice_time = pygame.time.get_ticks()
                        
                        # 升级页面按键逻辑
                        if p.upgrade_wait:
                            if event.key == pygame.K_1 and len(upgrades) >= 1:
                                upgrades[0][1](p)
                                p.upgrade_wait = False
                                enemies = wave_spawn(6 + wave * 2, wave)
                            if event.key == pygame.K_2 and len(upgrades) >= 2:
                                upgrades[1][1](p)
                                p.upgrade_wait = False
                                enemies = wave_spawn(6 + wave * 2, wave)
                            if event.key == pygame.K_3 and len(upgrades) >= 3:
                                upgrades[2][1](p)
                                p.upgrade_wait = False
                                enemies = wave_spawn(6 + wave * 2, wave)
                        else:
                            # 商店开关逻辑
                            if event.key == pygame.K_b:
                                p.shop_open = not p.shop_open
                                shop_notice = ""
                            
                            # 商店购买逻辑
                            if p.shop_open:
                                idx = -1
                                if event.key == pygame.K_1: idx = 0
                                if event.key == pygame.K_2: idx = 1
                                if event.key == pygame.K_3: idx = 2
                                if event.key == pygame.K_4: idx = 3
                                if 0 <= idx < len(shop_items):
                                    name, base_price, count, effect = shop_items[idx]
                                    # 1.2倍涨价，round()取整
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
                
                if not run:
                    break
                
                # 非升级页面才更新游戏逻辑
                if not p.upgrade_wait:
                    # 血包碰撞拾取检测
                    new_health_packs = []
                    for hp in self.health_packs:
                        # 创建血包碰撞框
                        hp_rect = pygame.Rect(
                            hp["x"] - 10,
                            hp["y"] - 10,
                            20,
                            20
                        )
                        # 检测玩家与血包碰撞
                        if p.rect.colliderect(hp_rect):
                            # 拾取血包，显示提示
                            health_notice = p.pick_health_pack(3)
                            health_notice_time = pygame.time.get_ticks()
                        else:
                            # 未拾取的血包保留
                            new_health_packs.append(hp)
                    self.health_packs = new_health_packs

                    # 更新终极技能
                    p.update_ultimate(dt, enemies, bullets)
                    
                    # 武器开火
                    p.fire_all_weapons(enemies, bullets, monster_bullets, dt, self.mouse_clicked)
                    
                    # 玩家移动
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
                                self.game_over_screen("lose", wave, p.char_name)
                                run = False
                                break
                    if not run:
                        break
                    
                    # 玩家子弹处理
                    new_bullets = []
                    for b in bullets:
                        t, x, y, vx, vy, dmg, pierce = b
                        x += vx
                        y += vy
                        bullet_rect = pygame.Rect(x, y, 6, 6) if t != "sword" else None
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
                        
                        if 0 < x < SCREEN_WIDTH and 0 < y < SCREEN_HEIGHT and (pierce > 0 or t in ["pistol", "shotgun"]):
                            new_bullets.append([t, x, y, vx, vy, dmg, pierce])
                    bullets = new_bullets
                    
                    # 怪物子弹处理
                    new_monster_bullets = []
                    for b in monster_bullets:
                        t, x, y, vx, vy, dmg = b
                        x += vx
                        y += vy
                        bullet_rect = pygame.Rect(x, y, 5, 5)
                        if bullet_rect.colliderect(p.rect):
                            if p.take_damage() and p.hp <= 0:
                                self.game_over_screen("lose", wave, p.char_name)
                                run = False
                                break
                        if 0 < x < SCREEN_WIDTH and 0 < y < SCREEN_HEIGHT:
                            new_monster_bullets.append([t, x, y, vx, vy, dmg])
                    monster_bullets = new_monster_bullets
                    
                    if not run:
                        break
                    
                    # 敌人死亡判定
                    alive = []
                    for e in enemies:
                        if e.hp > 0:
                            alive.append(e)
                        else:
                            p.money += e.drop_money
                            if e.type == "slime":
                                alive += e.split_slime()
                            if (e.is_special or e.is_boss) and e.drop_weapon:
                                self.weapon_drop_rect = pygame.Rect(e.rect.x, e.rect.y, 120, 40)
                                self.dropped_weapon = e.drop_weapon
                            # 怪物死亡时3%概率掉落血包
                            if random.random() <= 0.03:
                                self.health_packs.append({
                                    "x": e.rect.centerx,
                                    "y": e.rect.centery
                                })
                    enemies = alive
                    
                    # 清完敌人升级逻辑
                    if not enemies:
                        wave += 1
                        upgrades = self.generate_upgrades()
                        p.upgrade_wait = True
                        self.weapon_drop_rect = None
                        self.dropped_weapon = None
                
                # 绘制层
                # 1. 绘制玩家（战士技能特效）
                if not p.invincible or (pygame.time.get_ticks() - p.last_flash) < p.flash_frequency // 2:
                    pygame.draw.rect(self.screen, COLORS["GREEN"], p.rect)
                
                # 战士AOE光圈特效
                if p.ultimate_active and p.ultimate["type"] == "aoe":
                    px, py = p.rect.center
                    radius = p.ultimate["radius"] - (p.ultimate_timer / p.ultimate["duration"]) * 50
                    pygame.draw.circle(self.screen, (255, 100, 0), (int(px), int(py)), int(radius), 3)
                
                # 2. 绘制敌人
                for e in enemies:
                    pygame.draw.ellipse(self.screen, e.color, e.rect)
                    if e.is_special:
                        draw_text(self.screen, "★", e.rect.x+10, e.rect.y-5, (255, 255, 0), SMALL_FONT)
                    elif e.type == "archer":
                        draw_text(self.screen, "-A", e.rect.x+5, e.rect.y-5, (255, 255, 255), SMALL_FONT)
                    elif e.type == "slime":
                        draw_text(self.screen, "O", e.rect.x+5, e.rect.y-5, (0, 0, 0), SMALL_FONT)
                    elif e.is_boss:
                        draw_big(self.screen, "BOSS", e.rect.x+10, e.rect.y-30, (255, 0, 0))
                
                # 3. 绘制子弹
                for b in bullets:
                    t, x, y, vx, vy, dmg, pierce = b
                    if t == "pistol":
                        pygame.draw.circle(self.screen, (255, 255, 0), (int(x), int(y)), 3)
                    elif t == "shotgun":
                        pygame.draw.circle(self.screen, (255, 165, 0), (int(x), int(y)), 2)
                    elif t == "laser":
                        pygame.draw.line(self.screen, (0, 255, 255), (int(x-vx*2), int(y-vy*2)), (int(x), int(y)), 2)
                        pygame.draw.circle(self.screen, (0, 255, 255), (int(x), int(y)), 4)
                    elif t == "sword":
                        radius = 120 - (15 - pierce)*8
                        pygame.draw.circle(self.screen, (255, 200, 0), (int(x), int(y)), int(radius), 2)
                
                # 怪物子弹
                for b in monster_bullets:
                    t, x, y, vx, vy, dmg = b
                    if t == "boss":
                        pygame.draw.circle(self.screen, (255, 0, 0), (int(x), int(y)), 5)
                    else:
                        pygame.draw.circle(self.screen, (255, 50, 50), (int(x), int(y)), 3)
                
                # 4. 绘制武器掉落
                draw_weapon_drop(self.screen, self.weapon_drop_rect, self.dropped_weapon, FONT)
                
                # 5. 绘制血包
                draw_health_packs(self.screen, self.health_packs)
                
                # 6. 绘制BOSS血量条
                if boss:
                    draw_boss_hp(self.screen, boss, SMALL_FONT)
                
                # 7. 基础信息显示
                draw_text(self.screen, f"波数: {wave}", 10, 10, COLORS["WHITE"], FONT)
                draw_text(self.screen, f"HP: {p.hp}/{p.max_hp}", 10, 50, COLORS["WHITE"], FONT)
                draw_text(self.screen, f"金币: {p.money}", 10, 90, COLORS["WHITE"], FONT)
                draw_text(self.screen, f"已解锁武器: {len(p.unlocked_weapons)}/{len(BASE_WEAPON_CONFIG)}", 10, 130, COLORS["WHITE"], FONT)
                draw_text(self.screen, "B=商店  Q=终极技能  鼠标左键=射击/拾取", 10, SCREEN_HEIGHT - 40, COLORS["WHITE"], FONT)
                
                # 8. 已解锁武器绘制
                draw_text(self.screen, "已解锁武器：", SCREEN_WIDTH - 200, 10, (255, 220, 0), FONT)
                y_offset = 50
                for wp, lvl in p.unlocked_weapons.items():
                    draw_text(self.screen, f"{wp} Lv{lvl}", SCREEN_WIDTH - 200, y_offset, COLORS["WHITE"], FONT)
                    y_offset += 40
                
                # 9. 商店绘制
                if p.shop_open and not p.upgrade_wait:
                    pygame.draw.rect(self.screen, COLORS["SHOP_BG"], (SCREEN_WIDTH//2 - 220, 100, 440, 300))
                    draw_text(self.screen, "商店（按1-4购买）", SCREEN_WIDTH//2 - 100, 120, COLORS["WHITE"], FONT)
                    for i, (name, base_price, count, _) in enumerate(shop_items):
                        current_price = round(base_price * (1.2 ** count))
                        draw_text(self.screen, f"{i+1}. {name} {current_price}金币", SCREEN_WIDTH//2 - 160, 180 + i * 40, COLORS["WHITE"], FONT)
                
                # 10. 升级界面绘制
                if p.upgrade_wait:
                    pygame.draw.rect(self.screen, (40, 20, 40), (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100, 400, 300))
                    draw_big(self.screen, "选择升级！", SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 80, (255, 220, 0))
                    for i, (name, _) in enumerate(upgrades):
                        draw_text(self.screen, f"{i+1}. {name}", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20 + i*40, (255, 200, 100), FONT)
                
                # 11. 提示文字
                now_tick = pygame.time.get_ticks()
                if shop_notice and now_tick - shop_notice_time < 2000:
                    color = (0, 255, 0) if "成功" in shop_notice or "获得" in shop_notice else (255, 60, 60)
                    draw_text(self.screen, shop_notice, SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2, color, FONT)
                if ultimate_notice and now_tick - ultimate_notice_time < 1500:
                    draw_text(self.screen, ultimate_notice, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 40, (255, 255, 0), FONT)
                if health_notice and now_tick - health_notice_time < 1500:
                    draw_text(self.screen, health_notice, SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 40, (0, 255, 0), FONT)
                
                # 12. 绘制终极技能UI
                draw_ultimate_ui(self.screen, p, SMALL_FONT)
                
                # 更新显示
                pygame.display.flip()
            
            # 游戏结束后停止音乐
            pygame.mixer.music.stop()
    
    def character_select(self):
        """
        角色选择界面
        :return: 选择的角色
        """
        selected = 0
        while True:
            self.screen.fill(COLORS["BLACK"])
            draw_big(self.screen, "我独自升级", SCREEN_WIDTH//2 - 100, 100, (255, 220, 0))
            
            for i, c in enumerate(CHARACTERS):
                y = 200 + i * 60
                col = COLORS["GREEN"] if i == selected else (200, 200, 200)
                draw_text(self.screen, f"{i+1}.{c['name']} | {c['desc']}", SCREEN_WIDTH//2 - 150, y, col, FONT)
                # 显示终极技能名称
                draw_text(self.screen, f"HP:{c['hp']} 移速:{c['speed']} 终极:{c['ultimate']['name']}", SCREEN_WIDTH//2 - 150, y+30, (180, 180, 180), SMALL_FONT)
            
            draw_text(self.screen, "1/2/3/4选择 ↑↓选择 回车确认", SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT - 60, COLORS["WHITE"], FONT)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % 4
                        pygame.time.delay(150)
                    elif event.key == pygame.K_UP:
                        selected = (selected - 1) % 4
                        pygame.time.delay(150)
                    elif event.key == pygame.K_1:
                        selected = 0
                    elif event.key == pygame.K_2:
                        selected = 1
                    elif event.key == pygame.K_3:
                        selected = 2
                    elif event.key == pygame.K_4:
                        selected = 3
                    elif event.key == pygame.K_RETURN:
                        return CHARACTERS[selected]
            
            pygame.display.flip()
            self.clock.tick(60)
    
    def game_over_screen(self, result, wave, char_name):
        """
        游戏结束界面
        :param result: 游戏结果（win或lose）
        :param wave: 波数
        :param char_name: 角色名称
        """
        while True:
            self.screen.fill(COLORS["BLACK"])
            if result == "win":
                draw_big(self.screen, "挑战成功!", SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 80, (255, 220, 0))
            else:
                draw_big(self.screen, "挑战失败", SCREEN_WIDTH//2 - 80, SCREEN_HEIGHT//2 - 80, (255, 220, 0))
            
            draw_text(self.screen, f"角色: {char_name}", SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT//2, COLORS["WHITE"], FONT)
            draw_text(self.screen, f"坚持到第 {wave} 波", SCREEN_WIDTH//2 - 70, SCREEN_HEIGHT//2 + 40, COLORS["WHITE"], FONT)
            draw_text(self.screen, "按 ENTER 返回主页", SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2 + 120, COLORS["WHITE"], FONT)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # 重置攻速配置
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
            self.clock.tick(60)
    
    def generate_upgrades(self):
        """
        生成升级选项
        :return: 升级选项列表
        """
        pool = [
            ("生命+3", lambda p: setattr(p, 'max_hp', p.max_hp+3) or setattr(p, 'hp', p.hp+3)),
            ("基础伤害+1", lambda p: setattr(p, 'base_damage', p.base_damage+1)),
            ("全武器攻速+", lambda p: [BASE_WEAPON_CONFIG[wp].update({'atk_speed': max(0.15, BASE_WEAPON_CONFIG[wp]['atk_speed']*0.97)}) for wp in BASE_WEAPON_CONFIG.keys()]),
            ("移速+1", lambda p: setattr(p, 'speed', min(p.speed + 1, 10))),
        ]
        return random.sample(pool, 3)