# config/characters.py
# 角色配置
import pygame
from math import sin, cos, pi

# ---------- 预计算常量 ----------
_TWO_PI = 2 * pi
_PI_2 = pi / 2
_PI_3 = pi / 3
_PI_4 = pi / 4
_PI_8 = pi / 8
_PI_12 = pi / 12

# 战士：预计算角度常量
_WARRIOR_BLADE_OFFSETS = [0.0, _TWO_PI / 3, 2 * _TWO_PI / 3]      # 3刀间隔
_WARRIOR_LAYER_OFFSETS = [0.0, 0.12, 0.24]                          # 每层偏移
_WARRIOR_PARTICLE_ANGLES = [i * _TWO_PI / 12 for i in range(12)]    # 12粒子角度

# 射手：预计算角度常量
_ARCHER_CROSS_ANGLES = [0.0, _PI_2, pi, _PI_2 * 3]                  # 十字4点
_ARCHER_LINE_ANGLES = [i * _PI_3 for i in range(6)]                 # 6条放射线
_ARCHER_PARTICLE_ANGLES = [i * _PI_4 for i in range(8)]             # 8粒子

# 忍者：预计算角度常量
_NINJA_PARTICLE_ANGLES = [i * _TWO_PI / 8 for i in range(8)]        # 8粒子

# 机器人：预计算角度常量
_ROBOT_HEX_ANGLES = [i * _PI_3 for i in range(6)]                   # 6边


# ---------- 预分配Surface缓存 ----------
_ninja_glow = None
_ninja_shadows = [None, None]
_robot_shield = None


def _get_ninja_glow():
    global _ninja_glow
    if _ninja_glow is None:
        _ninja_glow = pygame.Surface((80, 80), pygame.SRCALPHA)
    _ninja_glow.fill((0, 0, 0, 0))
    return _ninja_glow


def _get_ninja_shadow(idx, w, h):
    global _ninja_shadows
    if _ninja_shadows[idx] is None or _ninja_shadows[idx].get_size() != (w, h):
        _ninja_shadows[idx] = pygame.Surface((w, h), pygame.SRCALPHA)
    _ninja_shadows[idx].fill((0, 0, 0, 0))
    return _ninja_shadows[idx]


def _get_robot_shield():
    global _robot_shield
    if _robot_shield is None:
        _robot_shield = pygame.Surface((54, 54), pygame.SRCALPHA)
    _robot_shield.fill((0, 0, 0, 0))
    return _robot_shield


# ---------- 特效绘制函数 ----------

def render_warrior_effect(screen, player):
    px, py = player.rect.center
    now = pygame.time.get_ticks()
    t = now / 1000.0
    progress = player.ultimate_timer / player.ultimate["duration"]
    base_radius = player.ultimate["radius"]
    current_radius = base_radius * (0.7 + 0.3 * abs(sin(progress * pi * 3)))

    for b_idx, blade_offset in enumerate(_WARRIOR_BLADE_OFFSETS):
        angle = blade_offset - t * 4
        for i, layer_offset in enumerate(_WARRIOR_LAYER_OFFSETS):
            a = angle + layer_offset
            arc_points = []
            for j in range(13):
                frac = j / 12.0
                arc_a = a + frac * 0.9
                r = current_radius * (0.3 + frac * 0.7)
                arc_points.append((px + cos(arc_a) * r, py + sin(arc_a) * r))
            pygame.draw.lines(screen, (255, 160 - i * 30, 20), False, arc_points, 4 - i)

    ring_r = current_radius * 0.85
    pygame.draw.circle(screen, (255, 140, 0), (int(px), int(py)), int(ring_r), 3)
    pygame.draw.circle(screen, (255, 200, 60), (int(px), int(py)), int(ring_r * 0.55), 2)

    sin_t6 = sin(t * 6)
    sin_t4 = sin(t * 4)
    cos_t3 = cos(t * 3)
    sin_t3 = sin(t * 3)
    for i, base_angle in enumerate(_WARRIOR_PARTICLE_ANGLES):
        p_angle = base_angle - t * 3
        p_r = current_radius * (0.4 + 0.4 * abs(sin_t6 * cos(i) + cos(t * 6) * sin(i)))  # sin(t*6 + i)
        p_size = 2 + int(abs(sin_t4 * cos(i) + cos(t * 4) * sin(i)) * 2)               # sin(t*4 + i)
        p_col = (255, 220, 80) if i % 2 == 0 else (255, 180, 40)
        pygame.draw.circle(screen, p_col,
                         (int(px + cos(p_angle) * p_r), int(py + sin(p_angle) * p_r)), p_size)


def render_archer_effect(screen, player):
    ax, ay = player.rect.center
    at = pygame.time.get_ticks() / 1000.0

    for ring in range(2):
        r_angle = at * 3 * (-1 if ring else 1)
        r_size = 22 + ring * 6
        for a in _ARCHER_CROSS_ANGLES:
            ang = r_angle + a
            ex = ax + cos(ang) * r_size
            ey = ay + sin(ang) * r_size
            pygame.draw.circle(screen, (255, 200, 30), (int(ex), int(ey)), 3)

    for i, base_angle in enumerate(_ARCHER_LINE_ANGLES):
        line_angle = base_angle + at * 2
        outer = 28 + sin(at * 8 + i) * 6
        lx1 = ax + cos(line_angle) * 12
        ly1 = ay + sin(line_angle) * 12
        lx2 = ax + cos(line_angle) * outer
        ly2 = ay + sin(line_angle) * outer
        pygame.draw.line(screen, (255, 180, 0), (lx1, ly1), (lx2, ly2), 2)

    sin_at6 = sin(at * 6)
    cos_at6 = cos(at * 6)
    for i, base_angle in enumerate(_ARCHER_PARTICLE_ANGLES):
        p_angle = base_angle - at * 2
        p_r = 18 + (sin_at6 * cos(i) + cos_at6 * sin(i)) * 5  # sin(at*6 + i)
        p_x = ax + cos(p_angle) * p_r
        p_y = ay + sin(p_angle) * p_r
        pygame.draw.circle(screen, (255, 220, 50), (int(p_x), int(p_y)), 2)


def render_ninja_effect(screen, player):
    nx, ny = player.rect.center
    nt = pygame.time.get_ticks() / 1000.0
    progress = player.ultimate_timer / player.ultimate["duration"]

    glow = _get_ninja_glow()
    pygame.draw.circle(glow, (80, 0, 120, int(60 * progress)), (40, 40), 30)
    screen.blit(glow, (nx - 40, ny - 40))

    sin_nt5 = sin(nt * 5)
    cos_nt5 = cos(nt * 5)
    sin_nt3 = sin(nt * 3)
    cos_nt3 = cos(nt * 3)
    sin_nt4 = sin(nt * 4)
    cos_nt4 = cos(nt * 4)
    for i, base_angle in enumerate(_NINJA_PARTICLE_ANGLES):
        p_r = 15 + (sin_nt5 * cos(i) + cos_nt5 * sin(i)) * 8          # sin(nt*5 + i)
        p_x = nx + cos(base_angle) * p_r
        p_y = ny + sin(base_angle) * p_r - (sin_nt3 * cos(i) + cos_nt3 * sin(i)) * 10  # sin(nt*3 + i)
        p_size = 2 + int(abs(sin_nt4 * cos(i) + cos_nt4 * sin(i)) * 2)  # sin(nt*4 + i)
        pygame.draw.circle(screen, (120, 40, 180), (int(p_x), int(p_y)), p_size)

    sin_nt6 = sin(nt * 6)
    cos_nt6 = cos(nt * 6)
    for after in range(2):
        off_x = (sin_nt6 * cos(after * pi) + cos_nt6 * sin(after * pi)) * 12  # sin(nt*6 + after*pi)
        off_y = (cos_nt6 * cos(after * pi) - sin_nt6 * sin(after * pi)) * 8   # cos(nt*6 + after*pi)
        shadow = _get_ninja_shadow(after, player.rect.width, player.rect.height)
        shadow.fill((100, 0, 150, 40))
        screen.blit(shadow, (player.rect.x + off_x, player.rect.y + off_y))


def render_robot_effect(screen, player):
    sx, sy = player.rect.center
    st = pygame.time.get_ticks() / 1000.0
    shield_size = 22

    hex_points = []
    for i, base_angle in enumerate(_ROBOT_HEX_ANGLES):
        angle = base_angle + st * 0.5
        hex_points.append((sx + cos(angle) * shield_size, sy + sin(angle) * shield_size))

    shield = _get_robot_shield()
    hex_offset = [(hx - sx + 27, hy - sy + 27) for hx, hy in hex_points]
    pygame.draw.polygon(shield, (0, 180, 220, 30), hex_offset)
    screen.blit(shield, (sx - 27, sy - 27))

    pygame.draw.polygon(screen, (0, 200, 240), hex_points, 3)

    glow_color = (0, 180, 220) if int(st * 6) % 2 == 0 else (0, 220, 255)
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