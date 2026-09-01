---
type: Concept
title: "Hook 扩展与自定义"
description: "start-notebook.d/before-notebook.d双Hook目录机制、run-hooks.sh执行规则、自定义镜像最佳实践"
tags: [hooks, customization, run-hooks, dockerfile-custom, extension-points]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-hooks, resource: "/references/startup-scripts.md", title: "run-hooks.sh与Hook目录" }
---

# Hook 扩展与自定义

Jupyter Docker Stacks 提供了**运行时Hook机制**，允许在不修改官方镜像启动脚本的前提下扩展容器启动行为。这是自定义镜像和动态配置的推荐方式。

## Hook 目录

有两个Hook目录，分别在启动流程的不同阶段执行：

| 目录 | 创建位置 | 执行时机 | 执行身份 | 典型用途 |
|------|---------|---------|---------|---------|
| `/usr/local/bin/start-notebook.d/` | Foundation层Dockerfile | start.sh早期，用户重映射之前 | 容器启动用户（通常是root） | 系统级初始化、安装包、配置服务 |
| `/usr/local/bin/before-notebook.d/` | Foundation层Dockerfile | 降权前后各执行一次 | root模式：先root后jovyan；非root模式：直接以启动用户 | conda环境激活、用户级配置、环境变量设置 |

### 执行顺序

两个目录中的文件按**文件名排序**依次执行。数字前缀可以控制执行顺序：

```
/usr/local/bin/before-notebook.d/
├── 10activate-conda-env.sh    # 第1个执行（官方默认，激活conda）
├── 20my-custom-setup.sh       # 第2个执行（用户自定义）
└── 99-final-check.sh          # 最后执行
```

官方的`10activate-conda-env.sh`使用`10`前缀，确保它在用户自定义hook之前执行。

## run-hooks.sh 执行规则

run-hooks.sh 是Hook执行器，对目录中的文件按以下规则处理：

### 文件类型处理

| 文件类型 | 处理方式 |
|---------|---------|
| `*.sh` 文件 | 使用`source`在当前shell中执行（可以修改环境变量、定义函数） |
| 可执行文件（非.sh） | 作为子进程直接执行 |
| 非可执行文件（非.sh） | 忽略（打印"Ignoring non-executable"日志） |
| 目录为空 | 跳过（无错误） |

### 错误处理

- Hook脚本失败（非零退出码）**不会中断启动流程**
- 失败时打印错误日志：`"${hook_file} has failed, continuing execution"`
- 这意味着单个Hook失败不会导致容器无法启动

### Errexit处理

run-hooks.sh会智能处理`set -e`（errexit）：
1. 如果调用者设置了`set -e`，在执行hook期间临时禁用
2. 每个hook执行后重新禁用errexit（因为hook本身可能启用了它）
3. 所有hook执行完毕后恢复调用者的errexit设置

这确保了一个hook的失败不会因为`set -e`而意外终止整个启动脚本。

## 使用 Hook 的三种方式

### 方式1：自定义Dockerfile（构建时扩展）

在自定义Dockerfile中将脚本复制到Hook目录：

```dockerfile
FROM quay.io/jupyter/base-notebook:latest

# 复制自定义hook脚本
COPY my-custom-setup.sh /usr/local/bin/before-notebook.d/
# 如果是.sh文件不需要chmod +x（source执行）
# 如果是二进制/其他解释器脚本需要可执行权限：
# COPY my-script.py /usr/local/bin/before-notebook.d/
# RUN chmod +x /usr/local/bin/before-notebook.d/my-script.py
```

### 方式2：Docker挂载（运行时扩展）

通过`docker run -v`挂载脚本到Hook目录，无需构建自定义镜像：

```bash
docker run -it --rm \
    -p 8888:8888 \
    -v ./my-setup.sh:/usr/local/bin/before-notebook.d/20my-setup.sh:ro \
    quay.io/jupyter/base-notebook
```

适合临时配置或开发调试。

### 方式3：目录绑定（批量Hook）

挂载整个目录批量添加Hook：

```bash
docker run -it --rm \
    -p 8888:8888 \
    -v ./my-hooks/:/usr/local/bin/before-notebook.d/:ro \
    quay.io/jupyter/base-notebook
```

## Hook 脚本编写指南

### Shell脚本（.sh文件）

.sh文件通过`source`执行，可以**修改当前shell环境**：

```bash
#!/bin/bash
# 示例：设置额外的环境变量
export MY_CUSTOM_VAR="hello"

# 示例：安装额外的pip包（在root身份执行时）
if [ "$(id -u)" == 0 ]; then
    pip install --no-cache-dir my-package
fi

# 示例：以jovyan身份安装JupyterLab扩展
if [ "$(id -u)" == "${NB_UID}" ]; then
    jupyter labextension install my-extension
fi
```

**注意**：.sh文件不需要可执行权限（因为是source的），但必须是有效的bash脚本。

### Python脚本（可执行文件）

Python脚本需要shebang行和可执行权限：

```python
#!/usr/bin/env python3
"""示例：在启动前进行配置检查"""
import os
import sys

if "REQUIRED_VAR" not in os.environ:
    print("WARNING: REQUIRED_VAR is not set", file=sys.stderr)
    # 非零退出码会被记录但不会终止启动
    sys.exit(1)
```

在Dockerfile中：
```dockerfile
COPY my-check.py /usr/local/bin/start-notebook.d/
RUN chmod +x /usr/local/bin/start-notebook.d/my-check.py
```

## 常见Hook用例

### 用例1：安装额外包

```bash
#!/bin/bash
# /usr/local/bin/before-notebook.d/install-deps.sh
# 以root身份运行时安装系统包
if [ "$(id -u)" == 0 ]; then
    apt-get update --yes
    apt-get install --yes --no-install-recommends some-package
    apt-get clean && rm -rf /var/lib/apt/lists/*
fi
```

### 用例2：配置Jupyter Server

```bash
#!/bin/bash
# /usr/local/bin/before-notebook.d/config-jupyter.sh
# 设置Jupyter配置选项
mkdir -p /home/${NB_USER}/.jupyter
cat >> /home/${NB_USER}/.jupyter/jupyter_server_config.py << 'EOF'
c.ServerApp.max_buffer_size = 536870912
c.NotebookApp.allow_origin = '*'
EOF
```

### 用例3：conda环境激活

```bash
#!/bin/bash
# /usr/local/bin/before-notebook.d/activate-custom-env.sh
# 激活自定义conda环境（而非base）
if [ -d "${CONDA_DIR}/envs/myenv" ]; then
    eval "$(conda shell.bash hook)"
    conda activate myenv
fi
```

## Hook执行身份判断

由于before-notebook.d在root模式下执行**两次**（一次root，一次jovyan），脚本需要判断当前执行身份：

```bash
#!/bin/bash
if [ "$(id -u)" == 0 ]; then
    echo "Running as root, doing system setup..."
    # root级操作：apt安装、系统配置
elif [ "$(id -u)" == "${NB_UID}" ]; then
    echo "Running as ${NB_USER}, doing user setup..."
    # 用户级操作：pip安装、Jupyter配置
else
    echo "Running as unknown user $(id -u), skipping..."
fi
```

## 内置Hook：10activate-conda-env.sh

这是官方唯一内置的before-notebook.d hook，负责激活conda base环境。它的存在确保了在Jupyter Server启动前，conda/mamba/python等命令在PATH中可用。

如果你需要替换或扩展conda环境激活行为，可以创建一个数字前缀更小或更大的脚本来覆盖或补充它。

## 常见错误

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| Hook脚本不执行 | 文件没有放在正确目录 | 检查路径是否为`/usr/local/bin/start-notebook.d/`或`/usr/local/bin/before-notebook.d/` |
| Python脚本不执行 | 缺少shebang或没有可执行权限 | 添加`#!/usr/bin/env python3`并chmod +x |
| 环境变量不生效 | 使用了子进程执行而非source | .sh文件通过source执行才能修改父shell环境 |
| Hook在错误身份下执行 | 没有判断id -u | 在脚本中添加root/jovyan身份判断 |
| 自定义镜像Hook被覆盖 | 多个COPY指令覆盖目录 | 每个Hook文件单独COPY，或确保COPY整个目录 |

## 相关概念

- [启动生命周期](07-startup-lifecycle.md)
- [用户与权限模型](09-user-permissions.md)
- [自定义镜像示例](../examples/02-custom-image.md)
