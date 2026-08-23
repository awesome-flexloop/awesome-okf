---
type: Example
title: 自定义Conda环境示例
description: 配置包含多个科学计算包的自定义xeus-python环境，包括pip纯Python包、多kernel配置和empack过滤
tags: [custom-environment, conda, packages, pip, configuration]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T20:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T20:10:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: build-system
    resource: /concepts/05-build-system.md
    title: 构建系统详解
  - id: pkg-mgmt
    resource: /concepts/06-package-management.md
    title: 包管理
---

## 目标

创建一个功能丰富的数据分析环境，预装numpy、pandas、matplotlib、scipy、scikit-learn，并添加一个纯Python工具包。同时演示如何添加额外的Notebook文件和数据文件。

## 项目结构

```
my-project/
├── environment.yml          # conda环境配置
├── jupyter_lite_config.json # JupyterLite配置
├── content/                 # 示例Notebook和数据
│   ├── welcome.ipynb
│   └── data/
│       └── sample.csv
└── notebooks/               # JupyterLite files目录
    └── examples/
```

## 步骤

### 步骤1：environment.yml

```yaml
name: xeus-data-science
channels:
  - https://prefix.dev/emscripten-forge-4x
  - https://prefix.dev/conda-forge
dependencies:
  # 内核
  - xeus-python

  # 数据处理
  - numpy
  - pandas
  - pyarrow

  # 可视化
  - matplotlib-base
  - bokeh

  # 科学计算
  - scipy
  - scikit-learn

  # 工具
  - requests
  - pyyaml

  # pip纯Python包（无C扩展）
  - pip:
    - simplejson
    - python-dateutil
```

**关键注意事项**：
- matplotlib使用 `matplotlib-base`（无Qt/GUI依赖），不是 `matplotlib`
- 检查包是否在emscripten-forge中可用：https://prefix.dev/emscripten-forge-4x
- pip部分只能是纯Python包，不能包含C扩展

### 步骤2：jupyter_lite_config.json

```json
{
  "XeusAddon": {
    "log_level": "INFO",
    "environment_file": "environment.yml",
    "default_channels": [
      "https://prefix.dev/emscripten-forge-4x",
      "https://prefix.dev/conda-forge"
    ],
    "mount_jupyterlite_content": true
  },
  "LiteBuildConfig": {
    "contents": [
      "notebooks",
      "content"
    ],
    "output_dir": "_output"
  }
}
```

- `mount_jupyterlite_content: true`：将files目录打包到WASM的`/files`路径
- `contents`：将额外的内容目录复制到输出
- `log_level: "DEBUG"` 可以看到更详细的构建日志

### 步骤3：添加示例Notebook

创建 `content/welcome.ipynb`：

```json
{
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": ["# Welcome to xeus-python\\n", "This is a pre-installed data science environment."]
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "import numpy as np\n",
        "import pandas as pd\n",
        "import matplotlib.pyplot as plt\n",
        "\n",
        "print('numpy:', np.__version__)\n",
        "print('pandas:', pd.__version__)"
      ],
      "outputs": [],
      "execution_count": null
    },
    {
      "cell_type": "code",
      "metadata": {},
      "source": [
        "# 测试数据读取\n",
        "df = pd.read_csv('/files/data/sample.csv')\n",
        "df.head()"
      ],
      "outputs": [],
      "execution_count": null
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python (XPython)",
      "language": "python",
      "name": "xpython"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

### 步骤4：添加示例数据

创建 `content/data/sample.csv`：

```csv
id,name,value,category
1,Alpha,100,A
2,Beta,200,B
3,Gamma,150,A
4,Delta,300,C
5,Epsilon,250,B
```

### 步骤5：构建

```bash
# 安装依赖
pip install jupyterlite-core jupyterlite-xeus

# 构建
jupyter lite build
```

构建时间取决于包数量。数据科学包（numpy/scipy/scikit-learn）较大，首次构建可能需要5-10分钟。

### 步骤6：预览

```bash
jupyter lite serve --port 8080
```

访问 `http://localhost:8080`，验证：
1. 打开 welcome.ipynb
2. 执行所有单元格
3. 检查包版本输出
4. 验证sample.csv数据加载

### 步骤7：验证预装包

在新Notebook中执行：

```python
# 验证所有预装包
import numpy
import pandas
import scipy
import sklearn
import matplotlib
import requests
import yaml
import simplejson

print("All packages imported successfully!")
print(f"numpy: {numpy.__version__}")
print(f"pandas: {pandas.__version__}")
print(f"scipy: {scipy.__version__}")
print(f"sklearn: {sklearn.__version__}")
```

## 包可用性检查

在构建之前，可以检查包是否在emscripten-forge中可用：

```bash
# 使用micromamba搜索
micromamba search -c https://prefix.dev/emscripten-forge-4x --platform emscripten-wasm32 <package-name>
```

常用可用包（基于emscripten-forge）：

| 包 | 可用 | 备注 |
|----|------|------|
| numpy | ✅ | |
| pandas | ✅ | |
| matplotlib-base | ✅ | 无GUI后端，用Agg |
| scipy | ✅ | |
| scikit-learn | ✅ | |
| bokeh | ✅ | |
| plotly | ✅ | |
| sympy | ✅ | |
| networkx | ✅ | |
| pillow | ✅ | |
| opencv | ⚠️ | 可能有功能限制 |
| pytorch | ❌ | WASM支持有限 |
| tensorflow | ❌ | 不可用 |

## 添加内容挂载

如果需要在WASM文件系统中预置数据文件，可以使用mounts配置：

在 `jupyter_lite_config.json` 中添加empack_config：

```json
{
  "XeusAddon": {
    "empack_config": {
      "mounts": [
        {
          "from": "content/data",
          "to": "/home/xeus/data"
        }
      ]
    }
  }
}
```

构建后，内核启动时 `/home/xeus/data/` 会包含 `content/data/` 中的文件（作为只读快照）。

**约束**：
- `to` 必须是绝对路径
- `to` 不能以 `/files` 开头
- 文件在启动时解压到MEMFS，是只读的

## 减少构建产物体积

### 排除不必要的文件

使用empack_config过滤不需要的文件：

```json
{
  "XeusAddon": {
    "empack_config": {
      "exclude_patterns": [
        "*.pyc",
        "__pycache__/*",
        "*/tests/*",
        "*/test_*"
      ]
    }
  }
}
```

### 避免安装大而无用的包

- 不要安装 `matplotlib`（完整GUI版），使用 `matplotlib-base`
- 不需要的包不要放在environment.yml中
- pip包只在确实需要时添加

## 运行时安装额外包

构建后如果临时需要新包，在Notebook中使用：

```python
# conda安装（支持C扩展）
%conda install networkx

# pip安装（仅纯Python）
%pip install some-pure-python-lib

# 注意：这些包在页面刷新后会丢失！
```

## 相关概念

- [构建系统详解](../concepts/05-build-system.md)
- [包管理](../concepts/06-package-management.md)
- [文件系统桥接](../concepts/07-filesystem-bridge.md)
- [快速开始](../concepts/01-getting-started.md)
