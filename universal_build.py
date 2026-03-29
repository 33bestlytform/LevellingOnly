# universal_build.py - 跨平台打包脚本
import os
import sys
import subprocess
import platform

def detect_os():
    """检测操作系统"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "linux":
        return "linux"
    elif system == "darwin":  # macOS
        return "macos"
    else:
        return system

def install_requirements():
    """安装项目依赖"""
    print("正在安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成！")
        return True
    except subprocess.CalledProcessError:
        print("安装依赖时出错，尝试使用国内镜像源...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", 
                                 "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/"])
            print("依赖安装完成！")
            return True
        except subprocess.CalledProcessError:
            print("依赖安装失败，请手动安装：pip install -r requirements.txt")
            return False

def build_for_windows():
    """为Windows构建"""
    print("检测到Windows系统，开始构建...")
    
    # Windows使用分号作为数据文件分隔符
    data_separator = ";"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "LevelingOnly",
        f"--add-data=assets{data_separator}assets",
        f"--add-data=config{data_separator}config",
        f"--add-data=src{data_separator}src",
        f"--add-data=utils{data_separator}utils",
        "main.py"
    ]
    
    subprocess.run(cmd, check=True)

def build_for_linux():
    """为Linux构建"""
    print("检测到Linux系统，开始构建...")
    
    # Linux使用冒号作为数据文件分隔符
    data_separator = ":"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "LevelingOnly",
        f"--add-data=assets{data_separator}assets",
        f"--add-data=config{data_separator}config",
        f"--add-data=src{data_separator}src",
        f"--add-data=utils{data_separator}utils",
        "main.py"
    ]
    
    subprocess.run(cmd, check=True)

def build_for_macos():
    """为macOS构建"""
    print("检测到macOS系统，开始构建...")
    
    # macOS使用冒号作为数据文件分隔符
    data_separator = ":"
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "LevelingOnly",
        f"--add-data=assets{data_separator}assets",
        f"--add-data=config{data_separator}config",
        f"--add-data=src{data_separator}src",
        f"--add-data=utils{data_separator}utils",
        "main.py"
    ]
    
    subprocess.run(cmd, check=True)

def main():
    """主函数"""
    print("LevelingOnly 跨平台打包工具")
    print("="*40)
    print(f"当前系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
        print("PyInstaller 已安装 ✓")
    except ImportError:
        print("PyInstaller 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller 安装完成 ✓")
        except subprocess.CalledProcessError:
            print("PyInstaller 安装失败，尝试用户安装...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
                print("PyInstaller 安装完成 ✓")
            except subprocess.CalledProcessError:
                print("PyInstaller 安装失败，请手动安装后再运行此脚本")
                return
    
    # 检查并安装项目依赖
    if not install_requirements():
        print("依赖安装失败，无法继续构建")
        return
    
    # 根据操作系统选择构建方法
    os_type = detect_os()
    print(f"\n开始为 {os_type} 构建...")
    
    try:
        if os_type == "windows":
            build_for_windows()
        elif os_type == "linux":
            build_for_linux()
        elif os_type == "macos":
            build_for_macos()
        else:
            print(f"不支持的操作系统: {os_type}")
            return
        
        print("\n✅ 构建成功完成！")
        print("可执行文件位置:")
        if os_type == "windows":
            print("  dist/LevelingOnly.exe")
        else:
            print("  dist/LevelingOnly")
        
        print("\n文件大小:")
        executable_path = "dist/LevelingOnly.exe" if os_type == "windows" else "dist/LevelingOnly"
        if os.path.exists(executable_path):
            size_mb = os.path.getsize(executable_path) / (1024 * 1024)
            print(f"  {size_mb:.2f} MB")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 构建失败: {e}")
        print("\n请参考以下故障排除文档:")
        if os_type == "windows":
            print("- BUILD_TROUBLESHOOTING.md")
        else:
            print("- LINUX_BUILDING.md")
    except Exception as e:
        print(f"\n❌ 发生未知错误: {e}")

if __name__ == "__main__":
    main()