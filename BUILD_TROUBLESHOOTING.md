# Windows 平台打包故障排除

## 常见问题及解决方案

### 1. "pip 不是内部或外部命令"
**问题**: 系统找不到pip命令
**解决方案**:
```cmd
# 方法1: 使用python -m pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

# 方法2: 检查Python安装路径并添加到PATH
# 通常在: C:\Users\[用户名]\AppData\Local\Programs\Python\Python[版本]\
# 或: C:\Python[版本]\
```

### 2. "No module named pip"
**问题**: Python安装时未包含pip
**解决方案**:
```cmd
# 下载get-pip.py并运行
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

### 3. 权限错误 (Permission Denied)
**解决方案**:
```cmd
# 以管理员身份运行命令提示符或PowerShell
# 或使用 --user 参数
pip install --user pyinstaller
```

### 4. "ModuleNotFoundError" 错误
**问题**: 缺少游戏依赖
**解决方案**:
```cmd
# 确保在项目根目录下运行
pip install -r requirements.txt
```

### 5. PyInstaller 安装失败
**解决方案**:
```cmd
# 方法1: 升级pip
python -m pip install --upgrade pip

# 方法2: 使用国内镜像源
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 方法3: 使用用户安装
pip install --user pyinstaller
```

### 6. 游戏无法启动
**问题**: 打包后的可执行文件无法运行
**解决方案**:
```cmd
# 检查是否有缺失的资源文件
# 确保assets, config, src, utils目录包含在打包中
```

## 完整的Windows安装步骤

### 步骤1: 检查Python安装
```cmd
python --version
pip --version
```

### 步骤2: 安装依赖
```cmd
# 在项目根目录下
pip install -r requirements.txt
pip install pyinstaller
```

### 步骤3: 运行打包脚本
```cmd
python windows_setup_build.py
```

## 使用虚拟环境（推荐）

如果遇到环境问题，建议使用虚拟环境：

```cmd
# 创建虚拟环境
python -m venv game_env

# 激活虚拟环境
game_env\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 运行打包
python windows_setup_build.py

# 完成后退出虚拟环境
deactivate
```

## 验证安装
打包完成后，可以运行以下命令验证：
```cmd
dir dist\
dist\LevelingOnly.exe
```

## 高级故障排除

### 查看详细错误信息
```cmd
# 以详细模式运行PyInstaller
pyinstaller --debug=all main.py
```

### 检查依赖关系
```cmd
pip list
pip show pygame
```

### 清理缓存
```cmd
pip cache purge
# 删除build目录
rmdir /s build
rmdir /s dist
```

## 联系支持

如果以上方法都无法解决问题，请检查：
- Python版本是否为3.7或更高
- 是否有足够的磁盘空间（至少1GB可用）
- 防病毒软件是否阻止了PyInstaller运行
- 确保以管理员身份运行命令提示符