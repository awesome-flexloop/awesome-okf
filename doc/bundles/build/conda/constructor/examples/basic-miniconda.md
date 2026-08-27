---
type: example
title: "构建基础 Miniconda 风格安装程序"
description: "从零开始构建一个类似 Miniconda 的最小化 Python 安装程序，包含 Python、conda、pip 和基本配置。"
tags: [Miniconda, 基础安装程序, 入门, 最小配置]
status: stable
stale_after: 2027-12-31
level: beginner
prerequisites: ["../concepts/01-getting-started"]
reading_time: 8
generated: { by: "example_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-main
    resource: "constructor/main.py"
---

# 构建基础 Miniconda 风格安装程序

本例演示如何构建一个类似 Miniconda 的最小化 Python 环境安装程序。Miniconda 是 Anaconda 公司发布的最小化 conda + Python 安装程序，也是 constructor 最经典的使用场景。

## 目标

创建一个包含以下内容的安装程序：
- Python 3.14.x
- conda 包管理器
- pip
- 基本的 conda 配置（默认通道、自动激活 base）
- 跨平台支持（Windows .exe、macOS .sh/.pkg、Linux .sh）

## 步骤 1：创建项目

```bash
mkdir my-miniconda
cd my-miniconda
```

## 步骤 2：编写 construct.yaml

创建文件 `construct.yaml`：

```yaml
name: MyMiniconda
version: "2026.08"

channels:
  - https://repo.anaconda.com/pkgs/main
  # Windows 需要 msys2 通道
  - https://repo.anaconda.com/pkgs/msys2  # [win]

specs:
  - python 3.14.*
  - conda
  - pip
  - setuptools
  - wheel
  - menuinst                    # [win]  Windows 开始菜单支持

# conda 初始化配置
initialize_conda: true
initialize_by_default: true    # 默认选中 conda init

# 写入 .condarc
write_condarc: true
conda_default_channels:
  - https://repo.anaconda.com/pkgs/main

# Windows 特定
register_python: true          # [win]
register_python_default: false # [win] 默认不注册

# 安装路径
default_prefix: "%USERPROFILE%\\myminiconda"  # [win]
default_prefix: "$HOME/myminiconda"            # [unix]
default_prefix_all_users: "%ALLUSERSPROFILE%\\myminiconda"  # [win]

# 安装行为
keep_pkgs: false              # 安装后删除包缓存（减小体积）
check_path_spaces: true       # 检查路径空格

# 输出额外产物
build_outputs:
  - hash
  - info.json
```

## 步骤 3：构建

```bash
# 安装 constructor 和 conda-standalone
conda create -n constructor-build -c conda-forge constructor conda-standalone
conda activate constructor-build

# 构建当前平台安装程序
constructor .
```

## 步骤 4：输出文件

构建完成后，当前目录下会生成：

```
MyMiniconda-2026.08-Windows-x86_64.exe        # Windows 安装程序
MyMiniconda-2026.08-Windows-x86_64.exe.sha256 # SHA-256 校验
MyMiniconda-2026.08-Windows-x86_64.exe.info.json  # 构建信息
```

（在 macOS/Linux 上生成对应平台的 .sh/.pkg 文件）

## 步骤 5：测试安装

### Linux/macOS

```bash
# 静默安装到 ~/myminiconda
bash MyMiniconda-2026.08-Linux-x86_64.sh -b -p $HOME/myminiconda

# 验证
$HOME/myminiconda/bin/python --version    # Python 3.14.x
$HOME/myminiconda/bin/conda --version     # conda 24.x.x
```

### Windows

```cmd
:: 静默安装
MyMiniconda-2026.08-Windows-x86_64.exe /S /D=C:\myminiconda

:: 验证
C:\myminiconda\python.exe --version
C:\myminiconda\Scripts\conda.exe --version
```

## 配置说明

### 为什么需要 menuinst（Windows）？

`menuinst` 是 conda 生态中创建 Windows 开始菜单快捷方式的工具。如果不包含 menuinst，即使设置了 `menu_packages`，也无法创建快捷方式。

### 为什么要 write_condarc？

如果不设置 `write_condarc: true`，安装后用户运行 `conda install` 时会因为没有配置通道而报错。Miniconda 默认配置 `pkgs/main` 通道。

### initialize_by_default 的选择

- **个人安装**：设为 `true`，方便用户开箱即用
- **企业部署**：考虑设为 `false`，由管理员统一配置
- **服务器环境**：设为 `false`，避免修改 shell 配置文件

## 扩展：添加常用包

在 `specs` 中追加常用包即可：

```yaml
specs:
  - python 3.14.*
  - conda
  - pip
  # 常用工具
  - ipython
  - jupyter
  - requests
  - numpy
  - pandas
```

## 下一步

- [自定义安装程序](custom-installer.md)：添加许可证、品牌图片、安装脚本
- [多环境安装程序](multi-env-installer.md)：在一个安装程序中创建多个 conda 环境
