#!/usr/bin/env python3
# linux_setup_build.py - Linux专用打包脚本
import os
import sys
import subprocess
import platform

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
    print("PyInstaller安装完成！")

def build_game():
    """构建游戏"""
    print(f"正在为 {platform.system()} 构建游戏...")
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller未找到，正在安装...")
        install_pyinstaller()
        # 重新导入模块路径
        import importlib.util
        spec = importlib.util.find_spec("PyInstaller")
        if spec is None:
            print("PyInstaller安装失败，请手动安装: pip3 install --user pyinstaller")
            sys.exit(1)
    
    # Linux使用冒号作为数据文件分隔符
    data_separator = ":"
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",           # 打包成单个文件
        "--windowed",          # 无控制台窗口
        "--name", "LevelingOnly",  # 输出文件名
        f"--add-data=assets{data_separator}assets",
        f"--add-data=config{data_separator}config", 
        f"--add-data=src{data_separator}src",
        f"--add-data=utils{data_separator}utils",
        "main.py"
    ]
    
    print("执行命令:", " ".join(cmd))
    
    # 执行打包
    subprocess.run(cmd, check=True)
    
    print("\n构建完成！")
    print("可执行文件位于 dist/LevelingOnly 目录中")
    print("用户可以直接运行此文件，无需安装任何依赖")

if __name__ == "__main__":
    build_game()