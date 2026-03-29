# setup_build.py - 简化打包脚本
import os
import sys
import subprocess
import platform

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    print("PyInstaller安装完成！")

def build_game():
    """构建游戏"""
    print(f"正在为 {platform.system()} 构建游戏...")
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
    except ImportError:
        install_pyinstaller()
    
    # 根据操作系统确定数据文件分隔符
    if platform.system() == "Windows":
        data_separator = ";"
    else:
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