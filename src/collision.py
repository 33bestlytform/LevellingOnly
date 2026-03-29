# src/collision.py
import pygame

class SpatialGrid:
    def __init__(self, cell_size=50):
        """
        初始化空间网格
        :param cell_size: 单元格大小
        """
        self.cell_size = cell_size
        self.grid = {}
    
    def clear(self):
        """清空网格"""
        self.grid = {}
    
    def add_object(self, obj):
        """
        添加对象到网格
        :param obj: 游戏对象
        """
        cells = self._get_cells(obj.rect)
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = []
            self.grid[cell].append(obj)
    
    def get_neighbors(self, rect):
        """
        获取矩形周围的对象
        :param rect: 矩形
        :return: 邻居对象列表
        """
        neighbors = []
        cells = self._get_cells(rect)
        for cell in cells:
            if cell in self.grid:
                neighbors.extend(self.grid[cell])
        return neighbors
    
    def _get_cells(self, rect):
        """
        获取矩形覆盖的单元格
        :param rect: 矩形
        :return: 单元格坐标列表
        """
        cells = []
        left = int(rect.left // self.cell_size)
        right = int(rect.right // self.cell_size)
        top = int(rect.top // self.cell_size)
        bottom = int(rect.bottom // self.cell_size)
        
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                cells.append((x, y))
        
        return cells