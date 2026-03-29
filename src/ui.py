# src/ui.py
import pygame

def draw_text(screen, text, x, y, color=(255, 255, 255), font=None):
    """
    绘制文本
    :param screen: 屏幕表面
    :param text: 文本内容
    :param x: x坐标
    :param y: y坐标
    :param color: 文本颜色
    :param font: 字体
    """
    if font:
        surf = font.render(text, True, color)
    else:
        surf = pygame.font.SysFont("Microsoft YaHei", 32).render(text, True, color)
    screen.blit(surf, (x, y))

def draw_big(screen, text, x, y, color=(255, 220, 0)):
    """
    绘制大文本
    :param screen: 屏幕表面
    :param text: 文本内容
    :param x: x坐标
    :param y: y坐标
    :param color: 文本颜色
    """
    font = pygame.font.SysFont("Microsoft YaHei", 48)
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def draw_small(screen, text, x, y, color=(255, 255, 255)):
    """
    绘制小文本
    :param screen: 屏幕表面
    :param text: 文本内容
    :param x: x坐标
    :param y: y坐标
    :param color: 文本颜色
    """
    font = pygame.font.SysFont("Microsoft YaHei", 24)
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))

def draw_weapon_drop(screen, weapon_drop_rect, dropped_weapon, font):
    """
    绘制武器掉落
    :param screen: 屏幕表面
    :param weapon_drop_rect: 武器掉落矩形
    :param dropped_weapon: 掉落的武器
    :param font: 字体
    """
    if weapon_drop_rect and dropped_weapon:
        pygame.draw.rect(screen, (150, 0, 200), weapon_drop_rect.inflate(10, 10), 3)
        pygame.draw.rect(screen, (120, 0, 180), weapon_drop_rect)
        draw_text(screen, f"拾取{dropped_weapon}", weapon_drop_rect.x+10, weapon_drop_rect.y+5, (255, 255, 255), font)

def draw_boss_hp(screen, boss, font):
    """
    绘制BOSS血量条
    :param screen: 屏幕表面
    :param boss: BOSS对象
    :param font: 字体
    """
    if boss:
        bar_width = 300
        bar_height = 20
        x = 1000//2 - bar_width//2
        y = 20
        # 血量条背景
        pygame.draw.rect(screen, (100, 100, 100), (x-2, y-2, bar_width+4, bar_height+4))
        # 当前血量条（红色）
        hp_ratio = boss.hp / boss.boss_max_hp
        pygame.draw.rect(screen, (255, 0, 0), (x, y, int(bar_width * hp_ratio), bar_height))
        # 血量文字
        draw_text(screen, f"BOSS HP: {int(boss.hp)}/{int(boss.boss_max_hp)}", x, y+25, (255, 255, 0), font)

def draw_ultimate_ui(screen, player, font):
    """
    绘制终极技能UI
    :param screen: 屏幕表面
    :param player: 玩家对象
    :param font: 字体
    """
    cd_ratio = player.ultimate_cd / player.ultimate["cd"]
    cd_color = (0, 255, 0) if cd_ratio <= 0 else (255, 0, 0)
    # 技能框背景
    pygame.draw.rect(screen, (50, 50, 50), (1000-120, 700-80, 100, 60))
    pygame.draw.rect(screen, cd_color, (1000-115, 700-75, 90, 50), 3)
    # CD文字或技能名称
    if player.ultimate_cd > 0:
        draw_text(screen, f"CD: {int(player.ultimate_cd)}s", 1000-105, 700-65, (255, 255, 255), font)
    else:
        draw_text(screen, f"Q: {player.ultimate['name']}", 1000-110, 700-65, (255, 255, 255), font)
    # 机器人护盾剩余次数提示
    if player.shield_active:
        draw_text(screen, f"护盾: {player.shield_hits}次", 1000-200, 700-40, (0, 255, 255), font)

def draw_health_packs(screen, health_packs):
    """
    绘制血包
    :param screen: 屏幕表面
    :param health_packs: 血包列表
    """
    for hp in health_packs:
        # 血包主体（红色圆形）
        pygame.draw.circle(screen, (255, 0, 0), (hp["x"], hp["y"]), 10)
        # 十字标记（白色）
        x, y = hp["x"], hp["y"]
        size = 7
        pygame.draw.line(screen, (255, 255, 255), (x-size, y), (x+size, y), 2)
        pygame.draw.line(screen, (255, 255, 255), (x, y-size), (x, y+size), 2)