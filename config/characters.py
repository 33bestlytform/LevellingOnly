# config/characters.py
# 角色配置
import pygame
from math import sin, cos, pi


def render_warrior_effect(screen, player):
    px, py = player.rect.center
    now = pygame.time.get_ticks()
    t = now / 1000.0
    progress = player.ultimate_timer / player.ultimate["duration"]
    base_radius = player.ultimate["radius"]
    current_radius = base_radius * (0.7 + 0.3 * abs(sin(progress * pi * 3)))

    for blade in range(3):
        angle = blade * 2 * pi / 3 - t * 4
        for i in range(3):
            a = angle + i * 0.12
            arc_points = []
            steps = 12
            for j in range(steps + 1):
                frac = j / steps
                arc_a = a + frac * 0.9
                r = current_radius * (0.3 + frac * 0.7)
                arc_points.append((px + cos(arc_a) * r, py + sin(arc_a) * r))
            if len(arc_points) >= 2:
                pygame.draw.lines(screen, (255, 160 - i * 30, 20), False, arc_points, 4 - i)

    ring_r = current_radius * 0.85
    pygame.draw.circle(screen, (255, 140, 0), (int(px), int(py)), int(ring_r), 3)
    pygame.draw.circle(screen, (255, 200, 60), (int(px), int(py)), int(ring_r * 0.55), 2)

    for i in range(12):
        p_angle = i * 2 * pi / 12 - t * 3
        p_r = current_radius * (0.4 + 0.4 * abs(sin(t * 6 + i)))
        p_size = 2 + int(abs(sin(t * 4 + i)) * 2)
        p_col = (255, 220, 80) if i % 2 == 0 else (255, 180, 40)
        pygame.draw.circle(screen, p_col,
                         (int(px + cos(p_angle) * p_r), int(py + sin(p_angle) * p_r)), p_size)


def render_archer_effect(screen, player):
    ax, ay = player.rect.center
    archer_t = pygame.time.get_ticks() / 1000.0

    for ring in range(2):
        r_angle = archer_t * 3 * (-1 if ring else 1)
        r_size = 22 + ring * 6
        for j in range(4):
            a = r_angle + j * pi / 2
            ex = ax + cos(a) * r_size
            ey = ay + sin(a) * r_size
            pygame.draw.circle(screen, (255, 200, 30), (int(ex), int(ey)), 3)

    for i in range(6):
        line_angle = i * pi / 3 + archer_t * 2
        inner = 12
        outer = 28 + sin(archer_t * 8 + i) * 6
        lx1 = ax + cos(line_angle) * inner
        ly1 = ay + sin(line_angle) * inner
        lx2 = ax + cos(line_angle) * outer
        ly2 = ay + sin(line_angle) * outer
        pygame.draw.line(screen, (255, 180, 0), (lx1, ly1), (lx2, ly2), 2)

    for i in range(8):
        p_angle = i * pi / 4 - archer_t * 2
        p_r = 18 + sin(archer_t * 6 + i) * 5
        p_x = ax + cos(p_angle) * p_r
        p_y = ay + sin(p_angle) * p_r
        pygame.draw.circle(screen, (255, 220, 50), (int(p_x), int(p_y)), 2)


def render_ninja_effect(screen, player):
    nx, ny = player.rect.center
    ninja_t = pygame.time.get_ticks() / 1000.0
    progress = player.ultimate_timer / player.ultimate["duration"]

    glow_alpha = int(60 * progress)
    glow_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(glow_surf, (80, 0, 120, glow_alpha), (40, 40), 30)
    screen.blit(glow_surf, (nx - 40, ny - 40))

    for i in range(8):
        p_angle = i * 2 * pi / 8
        p_r = 15 + sin(ninja_t * 5 + i) * 8
        p_x = nx + cos(p_angle) * p_r
        p_y = ny + sin(p_angle) * p_r - sin(ninja_t * 3 + i) * 10
        p_size = 2 + int(abs(sin(ninja_t * 3 + i)) * 2)
        pygame.draw.circle(screen, (120, 40, 180), (int(p_x), int(p_y)), p_size)

    for after in range(2):
        off_x = sin(ninja_t * 6 + after * pi) * 12
        off_y = cos(ninja_t * 6 + after * pi) * 8
        shadow_surf = pygame.Surface((player.rect.width, player.rect.height), pygame.SRCALPHA)
        shadow_surf.fill((100, 0, 150, 40))
        screen.blit(shadow_surf, (player.rect.x + off_x, player.rect.y + off_y))


def render_robot_effect(screen, player):
    sx, sy = player.rect.center
    shield_t = pygame.time.get_ticks() / 1000.0
    shield_size = 22

    hex_points = []
    for i in range(6):
        angle = i * pi / 3 + shield_t * 0.5
        hx = sx + cos(angle) * shield_size
        hy = sy + sin(angle) * shield_size
        hex_points.append((hx, hy))

    shield_surf = pygame.Surface((shield_size * 2 + 10, shield_size * 2 + 10), pygame.SRCALPHA)
    hex_offset = [(hx - sx + shield_size + 5, hy - sy + shield_size + 5) for hx, hy in hex_points]
    pygame.draw.polygon(shield_surf, (0, 180, 220, 30), hex_offset)
    screen.blit(shield_surf, (sx - shield_size - 5, sy - shield_size - 5))

    pygame.draw.polygon(screen, (0, 200, 240), hex_points, 3)

    glow_color = (0, 180, 220) if int(shield_t * 6) % 2 == 0 else (0, 220, 255)
    pygame.draw.polygon(screen, glow_color, hex_points, 1)

    for hx, hy in hex_points:
        pygame.draw.circle(screen, (100, 230, 255), (int(hx), int(hy)), 3)


def render_ultimate_effect(screen, player):
    if player.ultimate_active and player.ultimate["type"] == "aoe":
        render_warrior_effect(screen, player)
    if player.ultimate_active and player.ultimate["type"] == "speedup":
        render_archer_effect(screen, player)
    if player.ultimate_active and player.ultimate["type"] == "invincible":
        render_ninja_effect(screen, player)
    if player.shield_active:
        render_robot_effect(screen, player)


CHARACTERS = [
    {
        "name": "战士",
        "desc": "高生命值，强大的AOE技能",
        "hp": 15,
        "speed": 5,
        "damage": 2,
        "ultimate": {
            "name": "旋风斩",
            "type": "aoe",
            "radius": 120,
            "dmg": 5,
            "duration": 5,
            "cd": 20
        }
    },
    {
        "name": "射手",
        "desc": "高攻速，技能提升所有武器攻速",
        "hp": 10,
        "speed": 6,
        "damage": 1,
        "ultimate": {
            "name": "极速射击",
            "type": "speedup",
            "multiplier": 0.5,
            "duration": 10,
            "cd": 25
        }
    },
    {
        "name": "忍者",
        "desc": "高移速，技能提供短暂无敌",
        "hp": 8,
        "speed": 8,
        "damage": 3,
        "ultimate": {
            "name": "影遁",
            "type": "invincible",
            "duration": 3,
            "cd": 15
        }
    },
    {
        "name": "机器人",
        "desc": "技能提供护盾，抵挡伤害",
        "hp": 12,
        "speed": 4,
        "damage": 4,
        "ultimate": {
            "name": "能量护盾",
            "type": "shield",
            "hits": 5,
            "duration": 8,
            "cd": 30
        }
    }
]