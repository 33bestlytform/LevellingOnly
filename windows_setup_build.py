# windows_setup_build.py - Windows专用打包脚本
import os
import sys
import subprocess
import platform

def check_python():
    """检查Python安装"""
    print("检查Python安装...")
    try:
        import sys
        print(f"Python版本: {sys.version}")
        return True
    except:
        print("错误: 未找到Python或Python配置不正确")
        print("请访问 https://www.python.org/downloads/ 下载并安装Python")
        return False

def check_pip():
    """检查pip安装"""
    print("检查pip安装...")
    try:
        import pip
        print(f"pip版本: {pip.__version__}")
        return True
    except ImportError:
        print("错误: 未找到pip")
        print("请运行: python -m ensurepip --upgrade")
        return False

def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller安装完成！")
        return True
    except subprocess.CalledProcessError:
        print("通过pip安装失败，尝试直接运行安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--user"])
            print("PyInstaller安装完成！")
            return True
        except subprocess.CalledProcessError:
            print("PyInstaller安装失败，请手动安装:")
            print("  方法1: python -m pip install pyinstaller")
            print("  方法2: python -m pip install pyinstaller --user")
            return False

def build_game():
    """构建游戏"""
    print(f"正在为 {platform.system()} 构建游戏...")
    
    # 检查Python和pip
    if not check_python():
        return False
    
    if not check_pip():
        return False
    
    # 检查PyInstaller是否已安装
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller未找到，正在安装...")
        if not install_pyinstaller():
            return False
    
    # Windows使用分号作为数据文件分隔符
    data_separator = ";"
    
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
    
    try:
        # 执行打包
        subprocess.run(cmd, check=True)
        
        print("\n构建完成！")
        print("可执行文件位于 dist/LevelingOnly.exe")
        print("用户可以直接运行此文件，无需安装任何依赖")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n构建失败: {e}")
        print("可能的解决方案:")
        print("1. 确保所有必需的源文件存在")
        print("2. 检查Python环境是否完整")
        print("3. 尝试以管理员身份运行此脚本")
        return False

def main():
    """主函数"""
    print("LevelingOnly 游戏打包工具 (Windows版)")
    print("="*50)
    
    success = build_game()
    
    if success:
        print("\n✅ 打包成功完成！")
        print("文件位置: dist/LevelingOnly.exe")
    else:
        print("\n❌ 打包失败，请检查错误信息并重试")
        print("如需帮助，请参阅 BUILD_TROUBLESHOOTING.md")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()