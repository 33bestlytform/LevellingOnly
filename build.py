#!/usr/bin/env python
"""
游戏打包脚本
用于创建Windows和Linux的独立可执行文件
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def build_game():
    """根据操作系统构建游戏"""
    system = platform.system().lower()
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
    except ImportError:
        print("正在安装PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    project_root = Path(__file__).parent
    main_script = project_root / "main.py"
    
    if system == "windows":
        # Windows构建命令
        build_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name=LevelUpGame",
            "--add-data=assets;assets",
            "--add-data=config;config",
            "--add-data=src;src",
            "--add-data=utils;utils",
            "--clean",
            str(main_script)
        ]
    else:
        # Linux构建命令
        build_cmd = [
            "pyinstaller",
            "--onefile",
            "--name=levelup-game",
            "--add-data=assets:assets",
            "--add-data=config:config",
            "--add-data=src:src",
            "--add-data=utils:utils",
            "--clean",
            str(main_script)
        ]
    
    print(f"正在为{system}构建游戏...")
    subprocess.run(build_cmd)

if __name__ == "__main__":
    build_game()