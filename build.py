# build.py - 打包脚本
import os
import subprocess
import sys
from pathlib import Path

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),  # 包含assets目录
        ('config', 'config'),  # 包含config目录
        ('src', 'src'),        # 包含src目录
        ('utils', 'utils'),    # 包含utils目录
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LevelingOnly',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False以隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 如果有图标文件可以指定路径
)
'''
    
    with open('LevelingOnly.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Spec文件已创建: LevelingOnly.spec")

def install_dependencies():
    """安装打包所需的依赖"""
    print("正在安装PyInstaller...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    print("PyInstaller安装完成!")

def build_windows():
    """构建Windows版本"""
    print("开始构建Windows版本...")
    
    # 创建spec文件
    create_spec_file()
    
    # 执行打包命令
    subprocess.check_call([
        'pyinstaller', 
        '--onefile',  # 打包成单个可执行文件
        '--windowed', # 无控制台窗口
        '--add-data', 'assets;assets',
        '--add-data', 'config;config',
        '--add-data', 'src;src',
        '--add-data', 'utils;utils',
        '--name', 'LevelingOnly',
        'main.py'
    ])
    
    print("Windows版本构建完成! 可执行文件位于dist/目录下")

def build_linux():
    """构建Linux版本（需要在Linux环境下运行）"""
    print("开始构建Linux版本...")
    
    # 创建spec文件
    create_spec_file()
    
    # 执行打包命令
    subprocess.check_call([
        'pyinstaller', 
        '--onefile',  # 打包成单个可执行文件
        '--windowed', # 无控制台窗口
        '--add-data', 'assets:assets',  # Linux使用冒号分隔
        '--add-data', 'config:config',
        '--add-data', 'src:src',
        '--add-data', 'utils:utils',
        '--name', 'LevelingOnly',
        'main.py'
    ])
    
    print("Linux版本构建完成! 可执行文件位于dist/目录下")

def main():
    """主函数"""
    print("LevelingOnly 游戏打包工具")
    print("="*40)
    
    # 检查是否已安装PyInstaller
    try:
        import PyInstaller
        print("PyInstaller 已安装")
    except ImportError:
        install_dependencies()
    
    # 根据操作系统选择构建目标
    import platform
    os_name = platform.system().lower()
    
    if os_name == 'windows':
        build_windows()
    elif os_name == 'linux':
        build_linux()
    else:
        print(f"不支持的操作系统: {os_name}")
        print("此脚本支持 Windows 和 Linux")
    
    print("\n打包完成!")
    print("可执行文件位于 dist/ 目录下")
    print("将整个 dist/ 目录分发给用户即可")

if __name__ == '__main__':
    main()