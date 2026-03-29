# Linux 平台打包说明

## 问题诊断
您在运行打包脚本时遇到的问题是因为Linux系统上缺少必要的组件。

## 解决步骤

### 1. 安装pip（如果未安装）
```bash
# Ubuntu/Debian系统
sudo apt update
sudo apt install python3-pip

# CentOS/RHEL/Fedora系统
sudo yum install python3-pip
# 或者
sudo dnf install python3-pip

# Arch Linux系统
sudo pacman -S python-pip
```

### 2. 安装游戏依赖
```bash
pip3 install -r requirements.txt
```

### 3. 安装PyInstaller
```bash
pip3 install --user pyinstaller
```

### 4. 运行打包脚本
```bash
python3 linux_setup_build.py
```

## 替代方案

如果上述方法仍有问题，您可以使用以下替代方案：

### 方案A：使用虚拟环境
```bash
# 安装venv（如果未安装）
sudo apt install python3-venv  # Ubuntu/Debian
# 或
sudo yum install python3-venv  # CentOS/RHEL

# 创建虚拟环境
python3 -m venv game_env
source game_env/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行打包脚本
python setup_build.py

# 完成后退出虚拟环境
deactivate
```

### 方案B：使用conda（如果已安装）
```bash
# 创建新环境
conda create -n leveling-game python=3.8
conda activate leveling-game

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行打包脚本
python setup_build.py
```

## 常见错误及解决方案

### 错误："No module named pip"
- 运行 `sudo apt install python3-pip` (Ubuntu/Debian)

### 错误："Permission denied"
- 使用 `--user` 标志：`pip3 install --user pyinstaller`

### 错误："Command not found"
- 确保PATH包含用户本地bin目录：
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

## 验证安装
打包完成后，可以运行以下命令验证：
```bash
ls -la dist/
./dist/LevelingOnly
```

注意：生成的可执行文件只能在相同架构的Linux系统上运行（如x86_64）。