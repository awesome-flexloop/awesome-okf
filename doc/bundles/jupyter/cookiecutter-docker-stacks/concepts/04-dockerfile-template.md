---
type: Concept
title: "Dockerfile模板与编写指南"
description: "模板Dockerfile结构、非root安全模型、Python包和系统包安装规范、常见模式"
tags: [dockerfile, docker, build, user, permissions, best-practices]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T09:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T09:00:00Z" }
status: stable
stale_after: 2027-08-22
sources:
  - { id: src-files, resource: "/references/template-files.md", title: "模板文件源码索引" }
---

# Dockerfile模板与编写指南

本章详细解析模板生成的 Dockerfile，讲解如何正确地在 Jupyter Docker Stacks 基础镜像上添加自定义内容。

## 模板 Dockerfile 解析

生成的 `image/Dockerfile` 内容极简：

```dockerfile
FROM {{cookiecutter.stack_base_image}}

# Add RUN statements to install packages as the ${NB_USER} defined in the base images.

# Add a "USER root" statement followed by RUN statements
# to install system packages using apt-get, change file permissions, etc.

# If you do switch to root, always be sure to add a "USER ${NB_UID}" command
# at the end of the file to ensure the image runs as a unprivileged user by default.
```

三行注释传达了三个关键规则：

1. **Python包安装**：以默认用户（`${NB_USER}`，即jovyan）身份运行pip/conda/mamba安装
2. **系统包安装**：需要先切换到`USER root`，用apt-get安装系统包或修改权限
3. **安全原则**：如果切换到root，文件末尾必须切回`USER ${NB_UID}`

## Jupyter Docker Stacks 的用户模型

理解基础镜像的用户模型是编写正确 Dockerfile 的前提：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `NB_USER` | `jovyan` | 非特权用户名 |
| `NB_UID` | `1000` | 用户UID |
| `NB_GID` | `100` | 用户GID |
| `HOME` | `/home/jovyan` | 用户主目录 |

关键安全规则：
- 容器默认以 `jovyan`（UID 1000）非特权用户运行
- 如需执行特权操作（apt-get、chmod等），临时切换到 `USER root`
- **必须**在Dockerfile末尾切回 `USER ${NB_UID}`，确保容器启动时是非root状态
- 安装Python包时不需要切换用户，直接以jovyan身份运行

## 安装 Python 包

### 使用 pip（推荐纯Python包）

```dockerfile
FROM quay.io/jupyter/scipy-notebook

# 以默认用户jovyan安装Python包
RUN pip install --no-cache-dir \
    polars \
    duckdb \
    seaborn \
    xgboost
```

### 使用 mamba/conda（推荐含C扩展的包）

```dockerfile
FROM quay.io/jupyter/scipy-notebook

# 使用mamba安装conda包（更快的依赖解析）
RUN mamba install --yes \
    'geopandas' \
    'postgresql' \
    'psycopg2' \
    && mamba clean --all -f -y
```

### 安装特定版本

```dockerfile
RUN pip install --no-cache-dir \
    'polars>=1.0' \
    'duckdb==1.1.0'
```

### 从 requirements.txt 安装

```dockerfile
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt
```

> **最佳实践**：`--no-cache-dir` 减少镜像体积；安装后清理临时文件。

## 安装系统包

```dockerfile
FROM quay.io/jupyter/scipy-notebook

# 切换到root安装系统包
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        vim \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ！！！关键：切回非特权用户！！！
USER ${NB_UID}
```

系统包安装要点：
- 先 `USER root`
- 使用 `--no-install-recommends` 减少不必要的依赖
- 安装后执行 `apt-get clean && rm -rf /var/lib/apt/lists/*` 清理缓存
- **最后必须** `USER ${NB_UID}`

## 复制自定义文件

### 复制Notebook/数据文件

```dockerfile
FROM quay.io/jupyter/scipy-notebook

# 复制notebooks到工作目录
COPY --chown=${NB_UID}:${NB_GID} notebooks/ ${HOME}/work/

# 复制配置文件
COPY --chown=${NB_UID}:${NB_GID} jupyter_server_config.py /etc/jupyter/
```

`--chown` 确保复制的文件属于jovyan用户，避免权限问题。

### 复制自定义脚本到Hook目录

Jupyter Docker Stacks 支持启动Hook脚本：

```dockerfile
COPY --chown=${NB_UID}:${NB_GID} my-startup-script.sh /usr/local/bin/start-notebook.d/
RUN chmod +x /usr/local/bin/start-notebook.d/my-startup-script.sh
```

Hook脚本会在Jupyter启动前自动执行。

## 完整示例 Dockerfile

以下是一个比较完整的自定义镜像Dockerfile示例：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:latest

LABEL maintainer="Your Name <your@email.com>"
LABEL description="Custom Jupyter image for data science with additional tools"

# ---- 以jovyan安装Python包 ----
RUN pip install --no-cache-dir \
    'polars>=1.0' \
    'duckdb>=1.0' \
    'seaborn' \
    'xgboost' \
    'lightgbm' \
    'optuna' \
    'shap'

# ---- 切换root安装系统包 ----
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        vim \
        htop \
        tree \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ---- 复制自定义配置 ----
COPY --chown=${NB_UID}:${NB_GID} jupyter_server_config.py /etc/jupyter/
COPY --chown=${NB_UID}:${NB_GID} notebooks/ ${HOME}/work/

# ---- 确保容器以非特权用户运行 ----
USER ${NB_UID}
```

## 常见错误与反模式

### ❌ 错误1：忘记切回非root用户

```dockerfile
# 错误！容器以root运行，存在安全风险
USER root
RUN apt-get update && apt-get install -y some-package
# 缺少 USER ${NB_UID}
```

**后果**：容器以root运行，Jupyter进程有root权限，挂载主机目录时可能修改主机文件权限。

### ❌ 错误2：不清理apt缓存

```dockerfile
# 错误！镜像体积膨胀
USER root
RUN apt-get update && apt-get install -y some-package
# 缺少清理命令
```

**后果**：apt缓存留在镜像中，可能增加几十到几百MB体积。

### ❌ 错误3：以root安装Python包

```dockerfile
# 不推荐：以root安装的包可能导致权限问题
USER root
RUN pip install some-package
USER ${NB_UID}
```

**后果**：pip安装的文件属于root，jovyan用户无法更新或卸载，且可能导致权限冲突。

**正确做法**：Python包直接以jovyan用户（默认）安装，不需要切换root。

### ❌ 错误4：复制文件不设置所有者

```dockerfile
# 不推荐：复制的文件属于root
COPY my-file.txt ${HOME}/
```

**后果**：jovyan用户无法修改这些文件。

**正确做法**：使用 `--chown=${NB_UID}:${NB_GID}`。

### ❌ 错误5：每层一个RUN（镜像膨胀）

```dockerfile
# 不推荐：多个RUN层创建不必要的镜像层
RUN pip install package1
RUN pip install package2
RUN pip install package3
```

**正确做法**：将相关命令合并到单个RUN层：

```dockerfile
RUN pip install --no-cache-dir \
    package1 \
    package2 \
    package3
```

## 构建最佳实践

### 利用构建缓存

将变化频率低的指令放在前面，变化频率高的（如复制代码）放在后面：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:latest

# 1. 先安装依赖（变化少，可缓存）
RUN pip install --no-cache-dir \
    polars duckdb seaborn

# 2. 安装系统包（变化少）
USER root
RUN apt-get update && ... && rm -rf /var/lib/apt/lists/*
USER ${NB_UID}

# 3. 最后复制代码（变化频繁，缓存命中率低）
COPY --chown=${NB_UID}:${NB_GID} notebooks/ ${HOME}/work/
```

### 固定基础镜像版本

生产环境建议固定基础镜像的日期标签，保证可复现性：

```dockerfile
# 推荐：使用日期标签固定版本
FROM quay.io/jupyter/scipy-notebook:2026-07-28

# 不推荐（生产环境）：使用latest标签
FROM quay.io/jupyter/scipy-notebook:latest
```

### 启用 BuildKit

```bash
DOCKER_BUILDKIT=1 docker build -t my-image image/
```

BuildKit 提供：
- 并行构建独立阶段
- 更好的缓存机制
- 更清晰的构建输出

## 验证 Dockerfile 正确性

构建后运行测试：

```bash
# 构建镜像
docker build -t my-project/my-jupyter-stack image/

# 运行测试
TEST_IMAGE=my-project/my-jupyter-stack pytest tests/ -v

# 手动验证
docker run --rm my-project/my-jupyter-stack id
# 应输出：uid=1000(jovyan) gid=100(users) groups=100(users)
```

`id` 命令验证容器以 jovyan（UID 1000）而非 root 运行。

## 相关概念

- [项目介绍](00-introduction.md)
- [快速上手](01-getting-started.md)
- [模板变量详解](03-cookiecutter-variables.md)
- [测试框架详解](05-testing-framework.md)
- [最佳实践](09-best-practices.md)
