# main.py
import os
import sys
import pygame

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.abspath('.'))

from src.game import Game

def main():
    """游戏主函数"""
    try:
        # 创建游戏实例
        game = Game()
        
        # 运行游戏
        game.run()
        
    except Exception as e:
        print(f"游戏崩溃: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 退出Pygame
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()