---
type: Example
title: Xeus 内核完整配置示例
description: Xeus Python 内核站点配置，重点展示 environment.yml 包管理、micromamba 构建需求和与 Pyodide 的配置差异
tags: [xeus, emscripten-forge, environment.yml, micromamba, configuration]
difficulty: intermediate
estimated_time: 20min
prerequisites:
  - Python 3.10+
  - micromamba（本地构建需要）
  - 了解 Pyodide 配置示例
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: xeus-example
    resource: /references/conf-py-source.md
    title: xeus-kernel-example 完整源码
---

## 目标

配置一个使用 Xeus Python 内核的 JupyterLite Sphinx 站点。与 Pyodide 示例相比，关键差异在于：
1. 使用 `jupyterlite-xeus` 替代 `jupyterlite-pyodide-kernel`
2. 需要 `environment.yml` 定义预装包
3. `defaultKernelName` 设为 `"XPython"` 而非 `"python"`
4. 构建需要 micromamba

## 与 Pyodide 配置的差异

| 配置项 | Pyodide | Xeus |
|--------|---------|------|
| pip 包 | `jupyterlite-pyodide-kernel` | `jupyterlite-xeus` |
| 额外文件 | 无 | `environment.yml` |
| defaultKernelName | `"python"` | `"XPython"` |
| appName 后缀 | `(Pyodide)` | `(Xeus)` |
| 包安装方式 | 运行时 piplite | 构建时 environment.yml |
| 本地构建工具 | 仅 pip | pip + micromamba |

## requirements.txt

```txt
sphinx>=7.0
jupyterlite-sphinx
jupyterlite-xeus
pydata-sphinx-theme
myst-nb
numpydoc
sphinx-design
```

> 注意：用 `jupyterlite-xeus` 替换了 `jupyterlite-pyodide-kernel`。

## environment.yml（Xeus 特有）

这是 Xeus 配置的核心文件，定义了浏览器环境中预装的所有包：

```yaml
name: xeus-python-kernel
channels:
  - https://repo.mamba.pm/emscripten-forge
  - conda-forge
dependencies:
  - numpy
  - matplotlib-base
  - scipy
  - sympy
  - ipycanvas
```

### channels 说明

- **`https://repo.mamba.pm/emscripten-forge`**：emscripten-forge 频道，提供编译为 WebAssembly 的 conda 包。这是 Xeus 内核的核心频道。
- **`conda-forge`**：标准 conda-forge 频道，提供构建工具和依赖。

### 常用 emscripten-forge 包

| 包名 | 功能 |
|------|------|
| `numpy` | 数值计算 |
| `matplotlib-base` | 绘图（使用 -base 变体避免 GUI 依赖） |
| `scipy` | 科学计算 |
| `pandas` | 数据分析 |
| `sympy` | 符号数学 |
| `scikit-learn` | 机器学习 |
| `ipycanvas` | Canvas 绘图（Pyodide 中不直接支持） |
| `ipywidgets` | 交互式控件 |

> **重要**：不是所有 conda-forge 包都有 WASM 版本。可用包列表见 [emscripten-forge packages](https://beta.mamba.pm/channels/emscripten-forge)。

## conf.py 差异部分

Xeus 的 conf.py 与 Pyodide 几乎相同，只有几处差异：

```python
# ── 项目标识 ──
project = "jupyterlite-sphinx-demo (Xeus)"  # 注意 (Xeus)

# ── JupyterLite 配置 ──
jupyterlite_contents = ["custom_contents/*"]
jupyterlite_silence = True
strip_tagged_cells = True
# 不需要额外配置，jupyterlite-xeus 会自动处理内核注册
```

> **关键差异**：Xeus 内核**不需要**在 conf.py 中显式配置 defaultKernelName——这个配置在 jupyter-lite.json 中。

## jupyter-lite.json 差异

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "jupyterlite-sphinx-demo (Xeus)",
    "defaultKernelName": "XPython",
    "faviconUrl": "./lab/favicon.ico"
  }
}
```

注意 `defaultKernelName` 是 `"XPython"`（大写 XP），不是 `"python"` 或 `"xeus-python"`。

## 其他配置文件

以下配置文件与 Pyodide 完全相同，直接复用即可：

- `jupyter_lite_config.json`：`no_sourcemaps: true`
- `overrides.json`：Download 按钮配置
- `try_examples.json`：iframe 高度和页面忽略规则
- `button_styling.css`：按钮样式
- `example.py`：示例代码模块（Xeus 预装 numpy/matplotlib，示例更丰富）

## 本地构建前提

Xeus 内核的本地构建需要 micromamba（conda 包管理器）：

### 安装 micromamba

**Windows (PowerShell)**：
```powershell
Invoke-WebRequest -Uri https://micro.mamba.pm/api/micromamba/win-64/latest -OutFile micromamba.tar.bz2
# 解压并添加到 PATH
```

**macOS/Linux**：
```bash
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
sudo mv bin/micromamba /usr/local/bin/
```

或使用 conda-forge 安装：
```bash
conda install -c conda-forge micromamba
```

### 构建命令

```bash
pip install -r requirements.txt
cd docs
make html
```

`jupyterlite-xeus` 在构建时会自动调用 micromamba 解析 `environment.yml` 中的依赖，下载预编译的 WASM 包。首次构建需要下载包文件，时间较长。

## CI 构建（GitHub Actions）

Xeus 的 CI 构建需要额外安装 micromamba。参考 [/concepts/09-ci-deployment.md](../concepts/09-ci-deployment.md) 中的完整工作流，关键差异是 Xeus 构建步骤前需要：

```yaml
- name: Install micromamba
  if: matrix.site[0] == 'xeus-kernel-example'
  uses: mamba-org/setup-micromamba@v2
  with:
    environment-name: xeus-build
```

## Xeus 中的包使用

由于包通过 environment.yml 预装，Xeus Notebook 中**不需要** piplite 安装，直接 import 即可：

```python
# Xeus 中：包已预装，直接使用
import numpy as np
import matplotlib.pyplot as plt
from ipycanvas import Canvas  # ipycanvas 在 Pyodide 中不可用

x = np.linspace(0, 2*np.pi, 100)
plt.plot(x, np.sin(x))
plt.show()
```

对比 Pyodide：

```python
# Pyodide 中：需要 piplite 安装非预置包
import piplite
await piplite.install("sympy")
import sympy
```

## 验证清单

- [ ] 构建成功无错误（检查 micromamba 是否可用）
- [ ] JupyterLite 中内核显示为 "XPython"
- [ ] `import numpy` 直接可用（无需 piplite）
- [ ] `import ipycanvas` 可用（验证 emscripten-forge 包正确加载）
- [ ] TryExamples 按钮正常工作

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 构建失败：micromamba not found | 未安装 micromamba | 安装 micromamba 并添加到 PATH |
| 内核启动失败：No kernel named XPython | defaultKernelName 错误 | 确认为 `"XPython"`（大小写敏感） |
| 包导入失败 | 包不在 emscripten-forge | 检查可用包列表或使用 Pyodide |
| 构建时间极长 | 首次下载 WASM 包 | 后续构建使用缓存 |

## 相关内容

- [/concepts/04-kernel-comparison.md](../concepts/04-kernel-comparison.md)：内核选型指南
- [/examples/02-pyodide-setup.md](02-pyodide-setup.md)：Pyodide 配置对比
- [/concepts/09-ci-deployment.md](../concepts/09-ci-deployment.md)：CI/CD 配置
