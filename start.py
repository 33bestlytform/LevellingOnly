#!/usr/bin/env python3
"""
游戏启动脚本
"""

import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from source_modular import main

if __name__ == "__main__":
    print("正在启动游戏...")
    print("控制方式:")
    print("- WASD: 移动")
    print("- Q + 1-4: 切换武器")
    print("- B: 打开商店")
    print("- 1-4: 在商店中购买物品")
    print("- 1-3: 选择升级选项")
    print("\n游戏目标: 坚持10分钟获得胜利！")
    print("\n开始游戏...\n")
    main()