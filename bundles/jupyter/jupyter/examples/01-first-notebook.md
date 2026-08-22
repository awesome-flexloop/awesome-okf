---
type: example
title: 创建你的第一个 Jupyter Notebook
description: 从零开始启动 JupyterLab、创建 Notebook、执行代码单元格、使用 Markdown 和魔法命令，快速上手 Jupyter 交互计算
tags: [example, getting-started, hello-world, notebook, jupyterlab]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T11:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T11:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: jupyter-metasource
    resource: /references/jupyter-metasource.md
---

# 创建你的第一个 Jupyter Notebook

本示例将引导你从零开始使用 JupyterLab，创建第一个 Notebook，执行代码，并体验 Jupyter 的核心交互计算能力。

## 前置条件

- 已安装 Python 3.9+
- 已安装 JupyterLab（`pip install jupyterlab` 或 `conda install jupyterlab`）
- 已阅读 [Jupyter 元包与核心组件](../concepts/00-introduction.md)

## 步骤 1：启动 JupyterLab

打开终端（命令行），进入你想存放 Notebook 的目录，然后启动 JupyterLab：

```bash
cd ~/projects  # 或你喜欢的任何目录
jupyter lab
```

启动成功后，终端会显示类似输出：

```
[I 2026-08-22 10:00:00.123 ServerApp] Jupyter Server 2.x.x is running at:
[I 2026-08-22 10:00:00.123 ServerApp] http://localhost:8888/lab?token=abc123...
[I 2026-08-22 10:00:00.124 ServerApp] Use Control-C to stop this server
```

浏览器应该会自动打开 JupyterLab 界面。如果没有，手动复制终端中显示的 URL（含 token）到浏览器。

> **提示**：如果不想自动打开浏览器，使用 `jupyter lab --no-browser`。

## 步骤 2：创建新 Notebook

在 JupyterLab 的 Launcher 页面（首次打开时显示）：

1. 在 "Notebook" 部分，点击你想用的 Kernel（例如 "Python 3"）
2. 一个新的空白 Notebook 会打开，包含一个空的代码单元格

界面结构：
- **左侧边栏**：文件浏览器、运行中的 Kernel、扩展管理器等
- **主区域**：Notebook 编辑区
- **顶部菜单栏**：File、Edit、View、Run、Kernel 等
- **工具栏**：常用操作（运行、停止、单元格类型切换等）

## 步骤 3：执行第一个代码单元格

在代码单元格中输入：

```python
print("Hello, Jupyter!")
```

然后执行单元格，可以通过以下任一方式：
- 点击工具栏的 ▶️（Run）按钮
- 按 `Shift+Enter`（运行并移动到下一个单元格）
- 按 `Ctrl+Enter`（运行并保持在当前单元格）

你会看到输出：

```
Hello, Jupyter!
```

单元格左侧的 `In [ ]:` 会变成 `In [1]:`，表示这是第 1 个执行的单元格。

## 步骤 4：体验有状态执行

在新单元格中输入：

```python
x = 42
name = "Jupyter"
print(f"x = {x}")
```

执行（`Shift+Enter`）。然后在下一个单元格输入：

```python
print(f"x squared = {x ** 2}")
print(f"Hello, {name}!")
```

执行。注意：第二个单元格可以访问第一个单元格中定义的变量 `x` 和 `name`——这是因为 Kernel 保持了状态。

## 步骤 5：添加 Markdown 单元格

点击工具栏中的单元格类型下拉菜单（默认显示 "Code"），选择 "Markdown"，或按 `M` 键（在命令模式下，按 `Esc` 进入命令模式）。

输入以下 Markdown 内容：

```markdown
# 我的第一个 Notebook

这是一个 **Markdown 单元格**，支持：

- 列表项
- *斜体* 和 **粗体**
- 数学公式：$E = mc^2$
- [链接](https://jupyter.org)
```

按 `Shift+Enter` 渲染 Markdown。双击 Markdown 单元格可以重新编辑。

## 步骤 6：使用魔法命令

创建一个代码单元格，尝试 IPython 魔法命令：

```python
# 测量代码执行时间
%timeit sum(range(1000))
```

```python
# 列出当前命名空间中的所有变量
%who
```

```python
# 运行外部 Python 脚本
# 先创建一个脚本，然后运行
%%writefile hello_script.py
def greet(name):
    return f"Hello, {name}!"

print(greet("World"))

%run hello_script.py
```

```python
# 查看对象帮助信息
import math
math.sqrt?
```

```python
# 在 Notebook 中显示 Matplotlib 图表
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2*np.pi, 100)
plt.plot(x, np.sin(x), label='sin(x)')
plt.plot(x, np.cos(x), label='cos(x)')
plt.legend()
plt.title("Trigonometric Functions")
plt.show()
```

## 步骤 7：保存 Notebook

- 按 `Ctrl+S`（Windows/Linux）或 `Cmd+S`（macOS）保存
- 或点击 File → Save Notebook
- 文件会保存为 `.ipynb` 格式

## 步骤 8：关闭 JupyterLab

使用完毕后：

1. 保存所有 Notebook（`Ctrl+S`）
2. File → Shut Down（关闭所有 Kernel）
3. 在终端按 `Ctrl+C` 停止 Jupyter Server，确认关闭

> **注意**：直接关闭浏览器不会停止 Server 或 Kernel，它们会继续运行。务必正确关闭。

## 常用快捷键速查

在命令模式下（按 `Esc` 进入，单元格边框变蓝）：

| 快捷键 | 功能 |
|--------|------|
| `Shift+Enter` | 运行单元格，移到下一个 |
| `Ctrl+Enter` | 运行单元格，保持在当前 |
| `A` | 在上方插入单元格 |
| `B` | 在下方插入单元格 |
| `D,D`（按两次D） | 删除当前单元格 |
| `M` | 将单元格转为 Markdown |
| `Y` | 将单元格转为 Code |
| `C` / `V` | 复制 / 粘贴单元格 |
| `Z` | 撤销删除 |
| `0,0`（按两次0） | 重启 Kernel |
| `I,I`（按两次I） | 中断 Kernel |

在编辑模式下（按 `Enter` 进入，单元格边框变绿）：

| 快捷键 | 功能 |
|--------|------|
| `Tab` | 代码补全 |
| `Shift+Tab` | 显示函数签名/帮助 |
| `Ctrl+Shift+-` | 拆分单元格 |

## 验证结果

完成本示例后，你应该能够：

- ✅ 启动 JupyterLab 并创建 Notebook
- ✅ 执行代码单元格，理解 Kernel 状态保持
- ✅ 使用 Markdown 单元格添加叙述
- ✅ 使用常用魔法命令
- ✅ 正确保存和关闭 Notebook

## 下一步

- 学习 [配置基础操作](02-config-basics.md) 自定义 Jupyter 行为
- 探索 [多环境 Kernel 管理](03-multi-env-kernels.md) 在不同项目间切换
- 阅读 [什么是计算笔记本与 Jupyter 核心架构](../concepts/01-what-is-jupyter.md) 深入理解架构
- 尝试 [交互式控件](04-widgets-interact.md) 构建交互式 Notebook
