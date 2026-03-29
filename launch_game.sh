#!/bin/bash
# Linux 自动启动脚本

echo "LevelingOnly 游戏启动脚本"
echo "========================="

# 检查可执行文件是否存在
if [ ! -f "./LevelingOnly" ]; then
    echo "错误：未找到 LevelingOnly 可执行文件"
    echo "请确保此脚本与游戏可执行文件在同一目录中"
    exit 1
fi

echo
echo "游戏文件检测正常"
echo
echo "正在启动游戏..."
echo "提示：首次运行可能需要几秒钟时间，请耐心等待"
echo

# 使游戏文件可执行
chmod +x ./LevelingOnly

# 启动游戏
./LevelingOnly &

echo "游戏已启动！"
echo "如果游戏没有自动打开，请检查是否有图形界面支持"
echo