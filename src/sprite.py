# src/sprite.py
import pygame.sprite

class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, player):
        """
        初始化玩家精灵
        :param player: 玩家对象
        """
        super().__init__()
        self.player = player
        self.image = pygame.Surface((32, 32))
        self.image.fill((0, 255, 0))
        self.rect = self.player.rect

    def update(self):
        """更新精灵"""
        self.rect = self.player.rect

class EnemySprite(pygame.sprite.Sprite):
    def __init__(self, enemy):
        """
        初始化敌人精灵
        :param enemy: 敌人对象
        """
        super().__init__()
        self.enemy = enemy
        self.image = pygame.Surface((enemy.size, enemy.size))
        self.image.fill(enemy.color)
        self.rect = self.enemy.rect

    def update(self):
        """更新精灵"""
        self.rect = self.enemy.rect

class BulletSprite(pygame.sprite.Sprite):
    def __init__(self, bullet):
        """
        初始化子弹精灵
        :param bullet: 子弹对象
        """
        super().__init__()
        self.bullet = bullet
        self.image = pygame.Surface((6, 6))
        self.image.fill((255, 255, 0))
        self.rect = pygame.Rect(bullet[1], bullet[2], 6, 6)

    def update(self):
        """更新精灵"""
        self.rect.x = self.bullet[1]
        self.rect.y = self.bullet[2]