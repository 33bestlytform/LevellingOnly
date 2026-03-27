import pygame
import random
import sys
from settings import (
    SW, SH, BLACK, WHITE, GREEN, RED, YELLOW, ORANGE, BLUE, DARK_BLUE, SHOP_BG,
    FONT, BIG_FONT, WEAPONS, SURVIVE_GOAL, INITIAL_ENEMIES, ENEMY_SPEED_MIN, ENEMY_SPEED_MAX,
    ENEMY_MONEY_MIN, ENEMY_MONEY_MAX, WEAPON_DAMAGE, WEAPON_SPEED, UPGRADE_OPTIONS, SHOP_ITEMS, CHARACTERS
)

class Player:
    def __init__(self, char):
        self.rect = pygame.Rect(SW // 2, SH // 2, 32, 32)
        self.max_hp = char["hp"]
        self.hp = self.max_hp
        self.speed = char["speed"]
        self.damage = char["damage"]
        self.atk_speed = char["atk_speed"]
        self.timer = 0
        self.level = 1
        self.upgrade_wait = False
        self.weapon = "手枪"
        self.char_name = char["name"]
        self.money = 0
        self.shop_open = False

    def move(self):
        k = pygame.key.get_pressed()
        if k[pygame.K_a]:
            self.rect.x -= self.speed
        if k[pygame.K_d]:
            self.rect.x += self.speed
        if k[pygame.K_w]:
            self.rect.y -= self.speed
        if k[pygame.K_s]:
            self.rect.y += self.speed

    def fire(self, enemies, bullets, clock):
        if not enemies:
            return
        self.timer += clock.tick() / 1000
        if self.timer < self.atk_speed:
            return
        self.timer = 0
        target = min(enemies, key=lambda e: (e.rect.centerx - self.rect.centerx) ** 2 + (e.rect.centery - self.rect.centery) ** 2)
        tx, ty = target.rect.center
        px, py = self.rect.center
        dx, dy = tx - px, ty - py
        d = (dx ** 2 + dy ** 2) ** 0.5 + 0.01
        dx, dy = dx / d, dy / d
        
        if self.weapon == "手枪":
            bullets.append(["bullet", px, py, dx * WEAPON_SPEED["手枪"], dy * WEAPON_SPEED["手枪"], self.damage])
        elif self.weapon == "霰弹":
            for off in [-0.18, -0.09, 0, 0.09, 0.18]:
                c = pygame.math.Vector2(dx, dy).rotate(off * 100)
                bullets.append(["shot", px, py, c.x * WEAPON_SPEED["霰弹"], c.y * WEAPON_SPEED["霰弹"], self.damage // 2 + 1])
        elif self.weapon == "激光":
            bullets.append(["laser", px, py, dx * WEAPON_SPEED["激光"], dy * WEAPON_SPEED["激光"], self.damage + 1])
        elif self.weapon == "剑":
            for e in enemies:
                if e.rect.collidepoint(self.rect.center) or d < 60:
                    e.hp -= self.damage + 2

    def switch_weapon(self, key):
        idx = int(key) - 1
        if 0 <= idx < len(WEAPONS):
            self.weapon = WEAPONS[idx]

    def level_up(self):
        self.level += 1
        self.upgrade_wait = True

class Enemy:
    def __init__(self):
        side = random.choice([-30, SW + 30])
        y = random.randint(0, SH)
        self.rect = pygame.Rect(side, y, 28, 28)
        self.speed = random.uniform(ENEMY_SPEED_MIN, ENEMY_SPEED_MAX)
        self.hp = 1
        self.drop_money = random.randint(ENEMY_MONEY_MIN, ENEMY_MONEY_MAX)

    def move_to(self, p):
        dx = p.rect.centerx - self.rect.centerx
        dy = p.rect.centery - self.rect.centery
        d = (dx ** 2 + dy ** 2) ** 0.5 + 0.01
        self.rect.x += dx / d * self.speed
        self.rect.y += dy / d * self.speed

def wave_spawn(n):
    return [Enemy() for _ in range(n)]

def draw_text(s, x, y, screen, color=WHITE):
    screen.blit(FONT.render(s, True, color), (x, y))

def draw_big(s, x, y, screen, color=YELLOW):
    screen.blit(BIG_FONT.render(s, True, color), (x, y))

def generate_upgrades():
    return random.sample(UPGRADE_OPTIONS, 3)

def character_select(screen, clock):
    selected = 0
    while True:
        screen.fill(BLACK)
        draw_big("我独自升级", SW // 2 - 100, 100, screen)
        for i, c in enumerate(CHARACTERS):
            y = 200 + i * 60
            col = GREEN if i == selected else (200, 200, 200)
            draw_text(f"{i+1}.{c['name']}", SW // 2 - 120, y, screen, col)
            draw_text(c['desc'], SW // 2 + 20, y, screen, (200, 200, 200))
        draw_text("1/2/3/4选择 ↑↓选择", SW // 2 - 140, SH - 60, screen)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DOWN]:
            selected = (selected + 1) % 4
            pygame.time.delay(150)
        if keys[pygame.K_UP]:
            selected = (selected - 1) % 4
            pygame.time.delay(150)
        if keys[pygame.K_1]:
            selected = 0
        if keys[pygame.K_2]:
            selected = 1
        if keys[pygame.K_3]:
            selected = 2
        if keys[pygame.K_4]:
            selected = 3
        if keys[pygame.K_RETURN]:
            return CHARACTERS[selected]
        
        pygame.display.flip()
        clock.tick(60)

def game_over_screen(result, wave, char_name, screen, clock):
    while True:
        screen.fill(BLACK)
        if result == "win":
            draw_big("挑战成功!", SW // 2 - 100, SH // 2 - 80, screen)
        else:
            draw_big("挑战失败", SW // 2 - 80, SH // 2 - 80, screen)
        draw_text(f"角色: {char_name}", SW // 2 - 50, SH // 2, screen)
        draw_text(f"坚持到第 {wave} 波", SW // 2 - 70, SH // 2 + 40, screen)
        draw_text("按 ENTER 返回主页", SW // 2 - 110, SH // 2 + 120, screen)
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            pygame.time.delay(200)
            return
        
        pygame.display.flip()
        clock.tick(60)

def main():
    # 初始化游戏
    screen = pygame.display.set_mode((SW, SH))
    pygame.display.set_caption("我独自升级")
    clock = pygame.time.Clock()
    
    char = character_select(screen, clock)
    p = Player(char)
    bullets = []
    wave = 1
    enemies = wave_spawn(INITIAL_ENEMIES + wave * 2)
    run = True
    upgrades = []
    start_time = pygame.time.get_ticks()

    while run:
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        
        # 检查是否达到胜利条件
        if elapsed >= SURVIVE_GOAL:
            game_over_screen("win", wave, p.char_name, screen, clock)
            return

        screen.fill(DARK_BLUE)
        
        # 事件处理
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        
        # 打开商店
        if keys[pygame.K_b]:
            p.shop_open = True
            pygame.time.delay(150)

        # 商店界面
        if p.shop_open:
            screen.fill(SHOP_BG)
            draw_big("商店", SW // 2 - 40, 100, screen)
            draw_text(f"金币:{p.money}", SW // 2 - 50, 160, screen)
            
            for i, (itm, cost, _) in enumerate(SHOP_ITEMS):
                draw_text(f"{i+1}. {itm}", SW // 2 - 120, 220 + i * 50, screen)
            
            draw_text("1-4购买 | B关闭", SW // 2 - 100, SH - 80, screen)
            
            k = pygame.key.get_pressed()
            if k[pygame.K_1] and p.money >= SHOP_ITEMS[0][1]:
                p.money -= SHOP_ITEMS[0][1]
                SHOP_ITEMS[0][2](p)
            if k[pygame.K_2] and p.money >= SHOP_ITEMS[1][1]:
                p.money -= SHOP_ITEMS[1][1]
                SHOP_ITEMS[1][2](p)
            if k[pygame.K_3] and p.money >= SHOP_ITEMS[2][1]:
                p.money -= SHOP_ITEMS[2][1]
                SHOP_ITEMS[2][2](p)
            if k[pygame.K_4] and p.money >= SHOP_ITEMS[3][1]:
                p.money -= SHOP_ITEMS[3][1]
                SHOP_ITEMS[3][2](p)
            if k[pygame.K_b]:
                p.shop_open = False
                pygame.time.delay(150)
            
            pygame.display.flip()
            continue

        # 升级界面
        if p.upgrade_wait:
            draw_big("等级提升!", SW // 2 - 100, SH // 2 - 100, screen)
            draw_text(f"1:{upgrades[0][0]}", SW // 2 - 70, SH // 2 - 30, screen)
            draw_text(f"2:{upgrades[1][0]}", SW // 2 - 70, SH // 2, screen)
            draw_text(f"3:{upgrades[2][0]}", SW // 2 - 70, SH // 2 + 30, screen)
            draw_text("按1/2/3选择", SW // 2 - 100, SH // 2 + 100, screen)
            
            k = pygame.key.get_pressed()
            if k[pygame.K_1]:
                upgrades[0][1](p)
                p.upgrade_wait = False
            if k[pygame.K_2]:
                upgrades[1][1](p)
                p.upgrade_wait = False
            if k[pygame.K_3]:
                upgrades[2][1](p)
                p.upgrade_wait = False
            
            pygame.display.flip()
            continue

        # 切换武器
        if keys[pygame.K_q]:
            if keys[pygame.K_1]:
                p.switch_weapon('1')
            if keys[pygame.K_2]:
                p.switch_weapon('2')
            if keys[pygame.K_3]:
                p.switch_weapon('3')
            if keys[pygame.K_4]:
                p.switch_weapon('4')
            pygame.time.delay(150)

        # 玩家移动和攻击
        p.move()
        p.fire(enemies, bullets, clock)

        # 处理子弹
        for b in bullets[:]:
            t, x, y, vx, vy, dmg = b
            b[1] += vx
            b[2] += vy
            
            if t == "bullet":
                pygame.draw.circle(screen, YELLOW, (int(x), int(y)), 4)
            if t == "shot":
                pygame.draw.circle(screen, ORANGE, (int(x), int(y)), 3)
            if t == "laser":
                pygame.draw.rect(screen, BLUE, (x - 2, y - 2, 5, 5))
            
            if x < -30 or x > SW + 30 or y < -30 or y > SH + 30:
                bullets.remove(b)

        # 处理敌人
        for en in enemies[:]:
            en.move_to(p)
            pygame.draw.rect(screen, RED, en.rect)
            
            for b in bullets[:]:
                bx, by = b[1], b[2]
                if en.rect.collidepoint(bx, by):
                    en.hp -= b[5]
                    if b[0] != "laser":
                        bullets.remove(b)
                    if en.hp <= 0:
                        p.money += en.drop_money
                        enemies.remove(en)

        # 波次结束，生成新敌人和升级选项
        if not enemies:
            wave += 1
            p.level_up()
            upgrades = generate_upgrades()
            enemies = wave_spawn(INITIAL_ENEMIES + wave * 2)

        # 检查玩家是否被敌人击中
        if p.rect.collidelist([e.rect for e in enemies]) != -1:
            p.hp -= 1
            pygame.time.delay(100)
            if p.hp <= 0:
                game_over_screen("lose", wave, p.char_name, screen, clock)
                run = False

        # 计算并显示时间
        sec = elapsed // 1000
        minute = sec // 60
        sec %= 60

        # 绘制玩家和UI
        pygame.draw.ellipse(screen, (40, 220, 60), p.rect)
        draw_text(f"角色:{p.char_name}", 10, 10, screen)
        draw_text(f"生命:{p.hp}/{p.max_hp}", 10, 40, screen)
        draw_text(f"波次:{wave}", 10, 70, screen)
        draw_text(f"金币:{p.money}", 10, 100, screen)
        draw_text(f"武器:{p.weapon}", 10, 130, screen)
        draw_text(f"时间:{minute:02d}:{sec:02d}", 10, 160, screen)
        draw_text("Q切武器 B商店", 10, 200, screen)
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    # 初始化 Pygame
    pygame.init()
    
    try:
        while True:
            main()
    finally:
        pygame.quit()
        sys.exit()