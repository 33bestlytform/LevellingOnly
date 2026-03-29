@echo off
REM Windows 自动安装脚本

echo LevelingOnly 游戏安装程序
echo ===========================

REM 检查是否在正确的目录中
if not exist "LevelingOnly.exe" (
    echo 错误：未找到 LevelingOnly.exe
    echo 请确保此脚本与游戏可执行文件在同一目录中
    pause
    exit /b 1
)

echo.
echo 游戏文件检测正常
echo.
echo 正在启动游戏...
echo 提示：首次运行可能需要几秒钟时间，请耐心等待
echo.

REM 启动游戏
start "" "LevelingOnly.exe"

echo 游戏已启动！
echo 如果没有自动打开，请手动双击 LevelingOnly.exe 运行游戏
echo.
echo 按任意键退出...
pause > nul