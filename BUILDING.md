# LevelingOnly 游戏打包指南

## 简介
本项目包含一个自动生成的可执行文件打包脚本，可以将游戏打包成独立的可运行程序。

## 打包步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 运行打包脚本
```bash
python build.py
```

这将在 `dist/` 目录下生成一个名为 `LevelingOnly.exe` 的可执行文件（Windows）或 `LevelingOnly` （Linux）。

## 平台支持

### Windows
- 打包后生成 `LevelingOnly.exe`
- 可以直接双击运行，无需安装Python或其他依赖

### Linux
- 打包后生成 `LevelingOnly` 可执行文件
- 需要在终端中运行 `./LevelingOnly` 或右键设置为可执行后双击运行

## 注意事项
- 打包过程可能需要几分钟时间
- 生成的可执行文件包含了Python解释器和所有必要的依赖库
- 可执行文件较大（通常几十MB），因为它包含了整个Python环境
- 游戏资源文件（如图片、音频）会自动包含在可执行文件中

## 分发
打包完成后，您可以直接将生成的可执行文件发送给用户，他们无需安装任何额外软件即可运行游戏。