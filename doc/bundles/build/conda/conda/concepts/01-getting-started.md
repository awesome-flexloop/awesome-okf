---
okf_version: "0.2"
type: "concept"
title: "5分钟快速上手"
sources:
  - "conda/cli/main.py"
  - "conda/activate.py"
  - "conda/api.py"
---

# 5分钟快速上手

本教程将带你从零开始，在5分钟内掌握 conda 的核心操作流程：安装 conda、创建环境、安装包、导出环境、删除环境。

## 步骤 1：安装 conda

conda 的 CLI 入口点定义为 `conda = "conda.cli.main_pip:main"` [F-012]。要使用 conda，首先需要安装一个 conda 发行版。推荐以下两种方式：

**Miniforge**（社区驱动，默认使用 conda-forge 通道）：

```bash
# 访问 https://github.com/conda-forge/miniforge 下载对应平台的安装脚本
# Linux/macOS 示例：
wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh
```

**Miniconda**（Anaconda 官方，默认使用 defaults 通道）：

```bash
# 访问 https://docs.anaconda.com/free/miniconda/ 下载安装程序
```

安装完成后，初始化 shell（让 `conda activate` 命令可用）：

```bash
conda init bash    # 或 zsh / fish / powershell
```

> **为什么需要 `conda init`？** conda 的激活命令（activate/deactivate）采用"shell 源调用"（sourced）模式执行 [F-018]。与普通子命令不同，`conda activate` 并不在子进程中直接修改环境变量，而是输出 shell 脚本代码（如 bash 的 `export PATH=...`），由 shell hook 通过 `eval` 在当前 shell 进程中执行 [F-079]。`conda init` 的作用就是将这个 hook 写入你的 shell 配置文件（`.bashrc` 等）。

验证安装：

```bash
conda --version
# 输出示例：conda 26.7.1
```

`--version` 参数有快速路径优化，不加载解析器和插件系统，直接输出当前版本号 [F-016]。

## 步骤 2：创建环境

conda 的默认环境名为 `base`，这是 conda 自身安装所在的环境 [F-029]。日常使用应创建独立环境：

```bash
# 创建名为 myenv 的环境，指定 Python 3.11
conda create -n myenv python=3.11
```

创建过程中 conda 会自动求解依赖（通过 SAT 求解器），列出将要安装的包并请求确认。也可以加上 `-y` 参数自动确认：

```bash
conda create -n myenv python=3.11 -y
```

创建环境时可以同时指定多个包：

```bash
conda create -n ml-project python=3.11 numpy pandas scikit-learn -y
```

> **底层原理**：`conda create` 属于"子 shell 命令"（subshell command），走 `main_subshell()` 入口 [F-015][F-017]。执行流程为：预解析参数 → 初始化全局上下文 `context` → 加载插件 → 完整解析命令行参数 → 初始化日志 → 调用对应命令的 action 函数 [F-017]。

## 步骤 3：激活环境

创建环境后需要激活才能使用：

```bash
conda activate myenv
```

激活后，shell 提示符前会出现环境名标识（如 `(myenv)`），表示当前环境已生效。激活操作由 `_Activator` 抽象类完成，它处理三项任务：①设置/取消环境变量 ②执行 activate.d/deactivate.d 脚本 ③更新 PATH 和命令提示符 [F-079]。

查看当前环境中已安装的包：

```bash
conda list
```

## 步骤 4：安装包

在已激活的环境中安装包：

```bash
# 安装 numpy
conda install numpy

# 安装指定版本
conda install numpy=1.26

# 安装多个包
conda install numpy pandas matplotlib requests

# 从指定通道安装
conda install -c conda-forge numpy
```

也可以不激活环境，直接通过 `-n` 指定环境名：

```bash
conda install -n myenv scipy
```

搜索可用的包：

```bash
conda search numpy
```

> **求解器后端**：安装包时，conda 会通过 `context.plugin_manager.get_cached_solver_backend()` 获取求解器后端 [F-065]，默认使用 classic 求解器（SAT 算法），也可以通过插件切换到 libmamba 等更快的求解器。

更新包：

```bash
conda update numpy          # 更新指定包
conda update --all          # 更新环境中所有包
conda update -n base conda  # 更新 conda 自身
```

## 步骤 5：导出与复现环境

导出当前环境的配置到 YAML 文件：

```bash
conda env export > environment.yml
```

`environment.yml` 文件记录了环境名称、通道、所有包及其精确版本，可用于在另一台机器上复现完全相同的环境：

```bash
conda env create -f environment.yml
```

也可以通过 `conda list --explicit` 生成精确的包 URL 列表（平台相关，跨平台不可用）：

```bash
conda list --explicit > spec-file.txt
conda create -n myenv2 --file spec-file.txt
```

查看所有已创建的环境：

```bash
conda env list
# 或
conda info --envs
```

## 步骤 6：删除环境

当不再需要某个环境时，可以删除它：

```bash
# 先确保不在要删除的环境中
conda deactivate

# 删除环境
conda env remove -n myenv

# 或使用 remove 命令
conda remove -n myenv --all
```

## Python API 快速体验

除了命令行，conda 也提供了 Python 高层 API [F-064]。`conda.api` 模块暴露四个核心类：

- `Solver`：依赖求解 API
- `SubdirData`：通道 repodata 管理
- `PackageCacheData`：本地包缓存管理
- `PrefixData`：环境前缀包管理

```python
from conda.api import Solver, PrefixData
from conda.models.channel import Channel

# 查询已安装包
prefix_data = PrefixData("/path/to/env")
for record in prefix_data.query("numpy"):
    print(record.name, record.version)

# 使用求解器（Beta API）
solver = Solver(
    prefix="/path/to/env",
    channels=[Channel("conda-forge")],
    specs_to_add=["numpy>=1.26"],
)
final_state = solver.solve_final_state()
```

每个 API 类都提供 `reload()` 方法强制刷新数据 [F-067]。

## 常用命令速查表

| 操作 | 命令 |
|------|------|
| 查看版本 | `conda --version` |
| 创建环境 | `conda create -n <name> python=<ver>` |
| 激活环境 | `conda activate <name>` |
| 退出环境 | `conda deactivate` |
| 安装包 | `conda install <pkg>` |
| 更新包 | `conda update <pkg>` |
| 删除包 | `conda remove <pkg>` |
| 列出包 | `conda list` |
| 搜索包 | `conda search <pkg>` |
| 导出环境 | `conda env export > env.yml` |
| 复现环境 | `conda env create -f env.yml` |
| 列出环境 | `conda env list` |
| 删除环境 | `conda env remove -n <name>` |
| 查看信息 | `conda info` |

## 关键要点总结

1. **环境优先**：永远在非 base 环境中工作，用 `conda create -n` 创建独立环境
2. **shell hook 机制**：`conda activate` 通过输出 shell 脚本修改当前 shell 的环境变量，必须先运行 `conda init`
3. **两种命令入口**：普通命令（install/create/list）走子进程模式，激活命令（activate/deactivate）走 shell 源调用模式 [F-015][F-016]
4. **内置24个命令**：activate、clean、create、install、list、remove、search、update 等 [F-019]
5. **环境可复现**：通过 `environment.yml` 实现环境的完整导出与复现

## 相关概念

- [conda 简介](00-introduction.md)
- [七层架构总览](02-architecture-overview.md)
