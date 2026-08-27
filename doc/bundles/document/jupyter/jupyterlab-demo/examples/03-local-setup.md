---
type: Example
title: "本地搭建 JupyterLab 演示环境"
description: "在自己的机器上克隆仓库、配置 Conda 环境、构建演示文件并启动 JupyterLab，实现离线可运行的本地演示环境"
tags: [local-setup, conda, installation, build, offline, development]
generated: { by: "source-code-to-okf-wiki/trae", at: "2026-08-22T13:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T13:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: readme, resource: "/references/repo-readme.md", title: "README信源" }
  - { id: binder, resource: "/references/binder-config-source.md", title: "Binder配置信源" }
---

# 本地搭建 JupyterLab 演示环境

虽然 Binder 提供了零安装体验，但本地搭建演示环境可以获得更好的性能、更快的启动速度，以及离线演示能力。本示例指导你在自己的机器上完整搭建 jupyterlab-demo 环境。

## 前置条件

| 依赖 | 版本要求 | 说明 |
|------|---------|------|
| Conda | Miniconda 或 Anaconda | 环境管理 |
| Python | 3.6+ | build.py 需要 |
| Git | 任意 | 克隆仓库 |
| 磁盘空间 | ~5GB | Conda环境 + 外部仓库克隆 |
| 内存 | 4GB+ | 运行 JupyterLab |

### Conda 安装

如果你还没有 Conda，推荐安装 Miniconda（轻量级）：
- 下载地址：https://docs.conda.io/en/latest/miniconda.html
- 选择对应操作系统的安装包
- 安装时建议勾选"Add Conda to PATH"

## 步骤一：克隆仓库

```bash
git clone https://github.com/jupyterlab/jupyterlab-demo.git
cd jupyterlab-demo
```

## 步骤二：创建 Conda 环境

仓库使用 `.binder/environment.yml` 定义环境依赖：

```bash
conda env create -f .binder/environment.yml
```

这会创建一个名为 `notebook` 的 Conda 环境，安装所有必要的包（jupyterlab、ipykernel、r-irkernel、bqplot 等）。

> ⏱️ 环境创建可能需要 10-20 分钟，取决于网络速度。如果某些包下载慢，可以配置国内 Conda 镜像源。

### 配置国内镜像（可选，加速下载）

```bash
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes
```

## 步骤三：激活环境

```bash
conda activate notebook
```

激活后，命令行提示符会显示 `(notebook)` 前缀。

## 步骤四：运行构建脚本

```bash
python build.py
```

build.py 执行两件事：

1. **克隆外部仓库**（首次运行）：将7个外部仓库克隆到 `demofiles/` 目录
   - PythonDataScienceHandbook、Urban-Data-Challenge、Altair、TCGA Notebooks、QuantStack、C++ Notebooks、Julia Notebooks
2. **组装演示目录**：根据 `talks.yml` 的4个配置（test_talk/scipy2017/jupytercon2017/demo），将文件组装到对应的输出目录

> ⏱️ 首次构建需要克隆外部仓库，可能需要几分钟。后续构建会跳过已克隆的仓库。

## 步骤五：配置工作区（可选）

workspace.json 定义了 Binder 环境的预设布局。本地环境也可以导入：

```bash
jupyter lab workspaces import .binder/workspace.json
```

> ⚠️ workspace.json 中的路径基于 Binder 环境，本地导入后路径可能需要调整。如果导入后打开文件出错，可以跳过此步骤，手动排列布局即可。

## 步骤六：启动 JupyterLab

以 `demo/` 目录为工作目录启动：

```bash
jupyter lab --notebook-dir=demo/
```

或者如果你想使用其他演讲配置目录：

```bash
# SciPy 2017 教程
jupyter lab --notebook-dir=scipy2017-tutorial/

# JupyterCon 2017 教程
jupyter lab --notebook-dir=jupytercon2017/
```

启动后，终端会显示类似以下信息：

```
    To access the notebook, open this file in a browser:
        ...
    Or copy and paste one of these URLs:
        http://localhost:8888/lab?token=xxxxxxxxxxxx
```

浏览器会自动打开 JupyterLab。如果没有自动打开，复制显示的 URL 到浏览器中。

## 验证环境

启动后，验证以下功能是否正常：

### 1. Python 内核

1. 打开 `notebooks/Data.ipynb`
2. 运行所有单元格（Run → Run All Cells）
3. 确认没有报错，图表正确显示

### 2. 文件查看器

1. 双击 `data/iris.csv` → 应在 DataGrid 中打开
2. 双击 `hubble.jpg` → 应在图片查看器中打开
3. 双击 `data/Museums_in_DC.geojson` → 应在地图中打开

### 3. R 内核

1. 新建 Console：File → New → Console
2. 选择 R 内核
3. 输入 `1 + 1` 并运行，应返回 `[1] 2`

### 4. 终端

1. File → New → Terminal
2. 输入 `ls`（Linux/Mac）或 `dir`（Windows）验证终端可用

## 环境管理

### 更新环境

如果环境配置（environment.yml）有更新：

```bash
conda activate notebook
conda env update -f .binder/environment.yml
```

### 重建环境

如果环境损坏：

```bash
conda deactivate
conda env remove -n notebook
conda env create -f .binder/environment.yml
```

### 查看已安装的包

```bash
conda list           # 所有包
conda list jupyter   # 仅 jupyter 相关包
pip list             # pip 安装的包
```

## 离线演示准备

如果你需要在没有网络的场合演示：

### 1. 提前克隆所有仓库

```bash
python build.py  # 确保 demofiles/ 完整
```

### 2. 预下载所有 Conda 包缓存

```bash
# 在有网络时安装，conda会自动缓存包
conda env create -f .binder/environment.yml
```

Conda 包缓存通常在：
- Windows: `C:\Users\<用户名>\miniconda3\pkgs\`
- Mac/Linux: `~/miniconda3/pkgs/`

### 3. 测试离线运行

断开网络后验证 JupyterLab 启动正常，Notebook 可以运行。

> ⚠️ 注意：Notebook 中可能包含从网络下载数据的代码（如 pandas.read_csv(url)），这些在离线时会失败。建议预先下载数据到本地并修改 Notebook 引用本地路径。

## 性能优化建议

### 增加内存分配

如果运行大数据 Notebook（如 big.csv）时卡顿：
- 确保系统有足够内存（建议8GB+）
- 关闭其他占用内存的应用

### 使用 JupyterLab 最新版本

本仓库基于较旧的 JupyterLab 版本（JupyterCon 2017 时代）。如需使用最新特性，可以创建新环境：

```bash
conda create -n jupyterlab-latest -c conda-forge jupyterlab python=3.11
conda activate jupyterlab-latest
```

## 常见问题

### Q: `conda env create` 报网络错误？
A: 配置国内镜像源（见步骤二备注），或使用 Mamba（更快的 conda 替代）：
```bash
conda install mamba -n base -c conda-forge
mamba env create -f .binder/environment.yml
```

### Q: build.py 报错找不到某个文件？
A: 检查 `demofiles/` 目录是否完整。如果克隆中断，删除对应子目录重新运行 build.py。

### Q: R 内核不显示？
A: 确保 environment.yml 中包含 `r-irkernel`，并且环境激活后安装：
```bash
conda activate notebook
R -e "IRkernel::installspec(name = 'ir', displayname = 'R')"
```

### Q: 端口被占用？
A: JupyterLab 默认使用 8888 端口。如果被占用，指定其他端口：
```bash
jupyter lab --port=8889
```

### Q: Windows 上路径问题？
A: Windows 下路径分隔符使用 `\` 或在 PowerShell 中使用 `/`。build.py 使用 os.path 处理路径，应该兼容。

## 相关概念

- [Binder 环境配置三要素](../concepts/02-binder-config.md)
- [build.py 与 talks.yml 配置化组装系统](../concepts/03-build-system.md)
- [在 Binder 启动 JupyterLab 演示环境](01-launch-binder.md)
