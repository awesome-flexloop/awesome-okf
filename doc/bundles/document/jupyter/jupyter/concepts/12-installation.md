---
type: Concept
title: 安装与环境管理
description: Jupyter 生态安装方法总览（pip/conda/uv/mamba/pixi）、虚拟环境最佳实践、Jupyter 与环境内核的关系、Kernel 管理、Jupyter Console 与多语言 Kernel 安装
tags: [jupyter, installation, pip, conda, uv, mamba, pixi, venv, virtual-environment, kernel, ipykernel, jupyter-console, kernels]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T15:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T16:00:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
    title: Jupyter 元包源码信源登记
  - id: jupyter-install-docs
    resource: https://docs.jupyter.org/en/latest/install.html
    title: Jupyter 官方安装文档
  - id: jupyter-docs
    resource: https://docs.jupyter.org/
    title: Jupyter 官方文档
---

# 安装与环境管理

正确安装和配置 Jupyter 环境是高效使用 Jupyter 的第一步。Jupyter 生态包含多个组件——Notebook 界面、Jupyter Console 终端、多语言 Kernel 等，不同组件有不同的安装方式。

## Jupyter 生态组件概览

根据 [Jupyter 官方安装文档](https://docs.jupyter.org/en/latest/install.html)，Jupyter 生态主要包含三类可安装组件：

| 组件 | 说明 | 安装入口 |
|---|---|---|
| **Jupyter Notebook Interface** | 基于 Web 的交互式笔记本界面，融合代码、叙述文本、公式和可视化 | `pip install notebook` 或 `pip install jupyterlab` |
| **Jupyter Console** | 基于终端的交互式计算控制台 | `pip install jupyter-console` |
| **Jupyter Kernels** | 为不同编程语言和代码执行行为提供支持的内核 | 各语言独立安装（见下文） |

> **提示**：各工具的最佳实践安装方式请参考对应工具的官方文档。本页提供通用安装指南和常见问题排查。

## 安装方式

### 使用 pip 安装

```bash
# 安装完整 Jupyter 元包（包含 notebook, jupyterlab, nbconvert, ipykernel, ipywidgets）
pip install jupyter

# 仅安装 JupyterLab（推荐，更现代的界面）
pip install jupyterlab

# 仅安装经典 Notebook（v7+）
pip install notebook

# 安装 Jupyter Console（终端交互）
pip install jupyter-console
```

> **注意**：`jupyter` 是元包（metapackage），安装它会自动安装 notebook、nbconvert、ipykernel、ipywidgets、jupyterlab 五个依赖包。它本身不包含任何代码。

### 使用 uv 安装（推荐，新一代 Python 包管理器）

[uv](https://docs.astral.sh/uv/) 是用 Rust 编写的高速 Python 包管理器，兼容 pip 接口：

```bash
# 使用 uv 安装
uv pip install jupyterlab

# 创建环境并安装
uv venv myproject
source myproject/bin/activate  # Windows: myproject\Scripts\activate
uv pip install jupyterlab pandas numpy
```

### 使用 conda/mamba/micromamba 安装

[Anaconda](https://www.anaconda.com/) 或 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 是数据科学社区广泛使用的 Python 发行版，自带 conda 包管理器：

```bash
# 使用 conda 安装
conda install jupyter

# 使用 mamba（更快的 conda 替代品，C++ 实现）
mamba install jupyter

# 使用 micromamba（更轻量的 mamba）
micromamba install -c conda-forge jupyterlab

# conda-forge 频道通常有更新版本
conda install -c conda-forge jupyterlab
```

Conda 的优势：

- 自带 Python 和常用科学计算包（Anaconda 完整版）
- 管理非 Python 依赖（如 CUDA、C 库）更方便
- 环境隔离内置
- mamba/micromamba 用 C++ 重写了解析器，速度比 conda 快很多

### 使用 pixi 安装

[pixi](https://pixi.sh/) 是基于 conda 生态的跨语言包管理器，使用 `pixi.toml` 管理项目依赖：

```bash
# 在现有 pixi 项目中添加
pixi add jupyterlab

# 初始化新项目
pixi init myproject
cd myproject
pixi add jupyterlab pandas numpy
pixi run jupyter lab
```

### 使用 Homebrew（macOS）

```bash
brew install jupyter
```

## 启动 Jupyter

安装后，使用以下命令启动：

```bash
# 启动 JupyterLab（推荐）
jupyter lab

# 启动经典 Notebook
jupyter notebook

# 启动 Jupyter Console（终端交互）
jupyter console

# 指定端口
jupyter lab --port 8889

# 指定工作目录
jupyter lab --notebook-dir ~/projects

# 不自动打开浏览器
jupyter lab --no-browser

# 监听所有网络接口（允许远程访问）
jupyter lab --ip 0.0.0.0
```

启动后终端会显示 URL（含 token），复制到浏览器打开即可：

```
http://localhost:8888/?token=abc123def456...
```

### Jupyter Console 使用

Jupyter Console 是终端中的交互式环境，适合快速测试代码：

```bash
# 启动 Python Console
jupyter console

# 启动指定 Kernel
jupyter console --kernel=python3

# 启动时执行初始化代码
jupyter console --existing=<kernel-id>
```

## 虚拟环境与 Jupyter 的关系

这是初学者最容易困惑的问题之一。核心原则：

> **Jupyter 本身安装在哪个环境不重要，重要的是 Kernel 运行在哪个环境。**

Jupyter 包含前端（Lab/Notebook UI）和后端 Server，它们运行在某个 Python 环境中。但你可以将其他 Python 环境注册为 Kernel，在 Notebook 中切换使用。

### 常见的两种工作流

#### 工作流 1：每个环境安装 Jupyter（简单）

在每个虚拟环境中都安装 jupyterlab/notebook，激活环境后启动：

```bash
# 创建环境并安装 Jupyter
python -m venv myproject
source myproject/bin/activate  # Windows: myproject\Scripts\activate
pip install jupyterlab pandas numpy
jupyter lab
```

优点：简单直接，Jupyter 和 Kernel 在同一环境。
缺点：每个环境都要安装一次 Jupyter（几百 MB）。

#### 工作流 2：一个 Jupyter + 多个 Kernel（推荐）

在一个"核心"环境中安装 JupyterLab，为每个项目环境注册为 Kernel：

```bash
# 步骤 1：在基础环境安装 JupyterLab
pip install jupyterlab  # 或 conda install jupyterlab / uv pip install jupyterlab

# 步骤 2：为每个项目创建虚拟环境
python -m venv project1-env
source project1-env/bin/activate
pip install ipykernel pandas scikit-learn
python -m ipykernel install --user --name project1 --display-name "Python (project1)"
deactivate

python -m venv project2-env
source project2-env/bin/activate
pip install ipykernel tensorflow
python -m ipykernel install --user --name project2 --display-name "Python (project2)"
deactivate

# 步骤 3：在基础环境启动 JupyterLab，然后在 UI 中选择 Kernel
jupyter lab
```

优点：
- JupyterLab 只需安装一次
- 每个项目环境保持干净，只装项目需要的包
- 可以同时打开不同环境的 Notebook
- 在 JupyterLab 中可以随时切换 Kernel（Kernel → Change Kernel）

### ipykernel install 命令详解

```bash
python -m ipykernel install [选项]
```

| 选项 | 说明 |
|------|------|
| `--user` | 安装到用户目录（不需要管理员权限） |
| `--name <name>` | Kernel 内部名称（用于命令行引用） |
| `--display-name <name>` | 在 Jupyter UI 中显示的名称 |
| `--prefix <prefix>` | 安装到指定 prefix（如 conda 环境） |
| `--sys-prefix` | 安装到当前 Python 环境的 sys.prefix |

这个命令做了什么？它在 Jupyter 数据目录的 `kernels/<name>/kernel.json` 创建一个 kernelspec 文件：

```json
{
  "argv": ["/path/to/project1-env/bin/python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "Python (project1)",
  "language": "python"
}
```

`argv` 中的 Python 路径指向项目环境的 Python 解释器，这就是为什么 Kernel 运行在项目环境中——它使用该环境的 Python 执行代码。

### 管理已注册的 Kernel

```bash
# 列出所有已注册的 Kernel
jupyter kernelspec list

# 输出示例：
# Available kernels:
#   python3       /home/user/.local/share/jupyter/kernels/python3
#   project1      /home/user/.local/share/jupyter/kernels/project1
#   project2      /home/user/.local/share/jupyter/kernels/project2

# 删除不需要的 Kernel
jupyter kernelspec remove project1
```

> **重要**：`jupyter kernelspec remove` 只是删除了 kernelspec 文件，不会卸载环境或包。

## Conda 环境与 Kernel

使用 conda 环境时，流程类似：

```bash
# 创建 conda 环境
conda create -n myenv python=3.12 pandas numpy
conda activate myenv
pip install ipykernel  # 或 conda install ipykernel
python -m ipykernel install --user --name myenv --display-name "Python (myenv)"
```

如果使用 conda-forge 频道的 `nb_conda_kernels` 包，可以自动发现所有 conda 环境中的 Kernel，无需手动注册：

```bash
conda install nb_conda_kernels
```

安装后，所有包含 ipykernel 的 conda 环境会自动出现在 Kernel 列表中。

## 安装多语言 Kernel

Jupyter 不仅支持 Python，还可以通过安装不同 Kernel 支持多种编程语言：

| 语言 | Kernel 包 | 安装命令 |
|---|---|---|
| Python | ipykernel | `pip install ipykernel`（通常已随 Jupyter 安装） |
| R | IRkernel | 在 R 中执行 `install.packages('IRkernel')` 然后 `IRkernel::installspec()` |
| Julia | IJulia | 在 Julia 中执行 `using Pkg; Pkg.add("IJulia")` |
| Bash/Shell | bash_kernel | `pip install bash_kernel && python -m bash_kernel.install` |
| C++ | xeus-cling | `conda install -c conda-forge xeus-cling` |
| TypeScript/JavaScript | itypescript | `npm install -g itypescript && its --install=global` |
| SQL | JupySQL | `pip install jupysql` |

更多 Kernel 请参考 [Jupyter Kernels 列表](https://github.com/jupyter/jupyter/wiki/Jupyter-kernels)。

## 验证安装

安装后运行以下命令验证：

```bash
# 检查 Jupyter 版本
jupyter --version

# 检查可发现的 Jupyter 目录
jupyter --paths

# 检查已注册的 Kernel
jupyter kernelspec list

# 检查扩展（JupyterLab）
jupyter labextension list

# 快速启动并验证（创建一个简单 Notebook 并执行）
jupyter lab --no-browser --port=8888 &
# 浏览器打开后创建 Notebook，执行 print("Hello, Jupyter!")
```

## 常见安装问题

### 问题 1："jupyter 不是内部或外部命令"

**原因**：Python Scripts 目录不在 PATH 中。

**解决**：
- 确认 Python 和 pip 安装正确：`python --version`、`pip --version`
- 使用 `python -m jupyter lab` 代替 `jupyter lab`
- 找到 Python 的 Scripts 目录加入 PATH：
  - Windows: `%APPDATA%\Python\Python3x\Scripts` 或 `C:\Python3x\Scripts`
  - Unix: `~/.local/bin` 或虚拟环境的 `bin/`

### 问题 2：Kernel 启动失败 / Kernel 一直显示 "Starting"

**原因**：通常是 kernelspec 中的 Python 路径指向了不存在或损坏的环境。

**解决**：
```bash
# 检查 kernelspec 路径
jupyter kernelspec list
# 查看 kernel.json 中的 argv 路径
cat ~/.local/share/jupyter/kernels/myenv/kernel.json
# 确认该路径的 Python 存在
/path/to/env/bin/python --version
# 如果环境已删除，移除无效 kernelspec
jupyter kernelspec remove myenv
```

### 问题 3：安装包后 Notebook 中 import 失败

**原因**：在一个环境中 pip install 了包，但 Jupyter 的 Kernel 运行在另一个环境中。

**诊断**：在 Notebook 中执行以下代码确认当前 Kernel 环境：

```python
import sys
print(sys.executable)  # 应该是你期望的环境 Python 路径
print(sys.version)
```

**解决**：
1. 在 Notebook 中切换到正确的 Kernel（Kernel → Change Kernel）
2. 或者在 Notebook 中直接安装：`%pip install <package>`（`%pip` 魔法命令会安装到当前 Kernel 对应的环境）

### 问题 4：多个 Python 安装冲突

系统 Python、conda Python、pyenv Python、uv Python 等可能冲突。使用以下命令确认使用的是哪个 Python：

```bash
which python    # Unix
where python    # Windows
which jupyter
```

建议使用虚拟环境（venv/conda/uv）隔离项目，避免污染系统 Python。

### 问题 5：端口被占用

```bash
# 指定其他端口
jupyter lab --port 8889

# 或查看并终止占用端口的进程
# Unix:
lsof -i :8888
kill <pid>
# Windows:
netstat -ano | findstr :8888
taskkill /PID <pid> /F
```

### 问题 6：JupyterLab 扩展安装后不显示

JupyterLab 3.x+ 支持预构建扩展（prebuilt extensions），大多数扩展通过 pip/conda 安装后即可使用，无需 `jupyter labextension install`：

```bash
# 预构建扩展（推荐）
pip install jupyterlab-git
# 重启 JupyterLab 即可使用

# 检查已安装扩展
jupyter labextension list
```

## 升级 Jupyter

```bash
# pip
pip install --upgrade jupyterlab
pip install --upgrade notebook

# uv
uv pip install --upgrade jupyterlab

# conda
conda update jupyterlab
# 或使用 conda-forge
conda update -c conda-forge jupyterlab

# micromamba
micromamba update -c conda-forge jupyterlab
```

## 相关概念

- [Jupyter 元包与核心组件](00-introduction.md) — jupyter 元包安装的依赖关系
- [目录结构与文件位置](05-directories.md) — kernelspec 存放位置
- [Kernel 架构](06-kernel-architecture.md) — Kernel 启动机制与 kernelspec
- [jupyter 命令与子命令发现](03-jupyter-command.md) — jupyter --version/--paths 命令
- [配置系统](04-config-system.md) — Jupyter 配置文件与环境变量
