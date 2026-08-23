---
type: concept
title: "快速上手"
description: "从安装 constructor 到构建第一个安装程序的完整入门指南，包括 construct.yaml 编写、命令行参数和输出产物。"
tags: [入门, 安装, construct.yaml, 构建, CLI]
status: stable
stale_after: 2027-12-31
level: beginner
prerequisites: ["00-introduction"]
reading_time: 10
generated: { by: "concept_agent/trae-cn", at: "2026-08-21T00:00:00Z" }
sources:
  - id: constructor-main
    resource: "constructor/main.py"
  - id: constructor-pyproject
    resource: "pyproject.toml"
---

# 快速上手

本文将指导你完成 constructor 的安装、编写第一个配置文件、构建安装程序的完整流程。

## 1. 安装 constructor

constructor 作为 conda 包分发，建议在一个独立的 conda 环境中安装：

```bash
conda create -n constructor -c conda-forge constructor conda-standalone
conda activate constructor
```

> **重要**：`conda-standalone` 是构建安装程序所必需的，它提供了一个独立的 conda 二进制（不需要预装 conda 环境即可运行）。constructor 在构建时会自动查找 `sys.prefix/standalone_conda/conda.exe`（Windows）或对应路径。

也可以使用 micromamba 替代 conda-standalone（通过 `--conda-exe` 指定），但 Windows 平台目前不支持 micromamba。

验证安装：

```bash
constructor --version
constructor --help
```

## 2. 创建项目目录

constructor 需要一个包含 `construct.yaml` 的目录作为输入：

```bash
mkdir my-installer
cd my-installer
```

## 3. 编写 construct.yaml

`construct.yaml` 是 constructor 的唯一配置文件，用于指定安装程序的名称、版本、包含的包、通道等信息。

### 最简配置

```yaml
name: mypython          # 安装程序名称（字母数字开头，允许 -._）
version: "1.0.0"        # 版本号（将强制转为字符串）

channels:               # conda 通道列表（顺序重要，优先级从高到低）
  - https://repo.anaconda.com/pkgs/main
  - https://repo.anaconda.com/pkgs/msys2  # [win]

specs:                  # 要包含的包列表
  - python 3.14.*
  - pip
```

将以上内容保存为 `construct.yaml`。

### 关键必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 安装程序名称，正则 `^[a-zA-Z0-9_][\w.-]*$` |
| `version` | string | 版本号 |
| `channels` | list\<string\> | conda 通道 URL 列表 |
| `specs` | list\<string\> | 包规格（支持 conda matchspec 语法） |

> `specs` 和 `environment`/`environment_file` 三选一，不能同时为空。

## 4. 构建安装程序

在包含 `construct.yaml` 的目录中运行：

```bash
constructor .
```

constructor 将执行以下步骤：

1. **解析** construct.yaml（处理 selectors、Jinja2 模板）
2. **校验** JSON Schema 合规性
3. **求解**依赖（调用 conda Solver API）
4. **下载**包到缓存目录
5. **生成**安装程序（平台相关的 .sh/.exe/.pkg）
6. **输出**构建产物到当前目录

构建完成后，你会看到类似这样的输出文件：

```
mypython-1.0.0-Windows-x86_64.exe     # Windows 安装程序
# 或
mypython-1.0.0-Linux-x86_64.sh        # Linux 安装程序
# 或
mypython-1.0.0-MacOSX-x86_64.pkg      # macOS 安装程序
mypython-1.0.0-MacOSX-arm64.sh
```

## 5. 常用命令行参数

```bash
# 指定输出目录
constructor . --output-dir ./dist

# 交叉构建（在 Linux 上构建 Windows 安装程序，需提供 conda-standalone）
constructor . --platform win-64 --conda-exe /path/to/conda.exe

# 指定安装程序类型
constructor . --installer-type exe     # Windows 仅生成 exe
constructor . --installer-type pkg     # macOS 仅生成 pkg
constructor . --installer-type all     # 生成所有平台支持的类型

# 仅预览（不生成安装程序，仅求解依赖）
constructor . --dry-run

# 渲染并输出 construct.yaml（查看 selectors/Jinja2 处理结果）
constructor . --render

# 输出所有可用配置键（参考）
constructor . --help-construct

# 清理下载缓存
constructor . --clean
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `CONSTRUCTOR_CACHE` | 包下载缓存目录，默认 `~/.conda/constructor` |
| `CONDA_CHANNEL_URLS` | 可在 Jinja2 模板中引用的通道 URL |
| `CONDA_CHANNEL_ALIASES` | 通道别名映射 |

## 6. 使用 Selectors（平台条件）

constructor 支持 conda-build 风格的 selector 语法，使用 `# [condition]` 行尾注释：

```yaml
name: mypython
version: "1.0.0"
channels:
  - conda-forge
specs:
  - python
  - pywin32  # [win]
  - appscript  # [osx]

installer_type: exe  # [win]
installer_type: pkg  # [osx]
installer_type: sh   # [linux]
```

支持的 selector 布尔变量：`linux`, `linux64`, `win`, `win64`, `osx`, `arm64`, `unix`, `x86_64`, `aarch64` 等，也支持逻辑运算如 `# [linux64 or osx]`。

## 7. 安装生成的安装程序

### Linux/macOS (.sh)

```bash
# 批处理模式（无交互）
bash mypython-1.0.0-Linux-x86_64.sh -b -p ~/mypython

# 交互模式
bash mypython-1.0.0-Linux-x86_64.sh
```

常用选项：
- `-b`：批处理模式，不弹出交互提示
- `-p <prefix>`：指定安装路径
- `-k`：保留 pkgs 缓存（默认安装后删除）
- `-u`：更新现有安装

### Windows (.exe)

双击 `.exe` 文件启动 NSIS GUI 安装向导，或命令行静默安装：

```cmd
mypython-1.0.0-Windows-x86_64.exe /S /D=C:\mypython
```

- `/S`：静默安装
- `/D=<path>`：指定安装路径（必须是最后一个参数，不能加引号）
- `/AddToPath=1`：添加到 PATH
- `/RegisterPython=1`：注册为系统 Python
- `/KeepPkgCache=1`：保留包缓存

## 8. 下一步

- [02-架构总览](./02-architecture-overview.md)：理解 constructor 的模块划分和执行流程
- [03-construct.yaml 配置规范](./03-construct-yaml-schema.md)：完整了解所有配置字段
- [示例：基础 Miniconda 风格安装程序](../examples/basic-miniconda.md)：查看更完整的配置示例
