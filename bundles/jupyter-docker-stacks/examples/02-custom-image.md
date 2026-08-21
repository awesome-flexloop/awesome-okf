---
title: 自定义镜像构建
id: ex-02-custom-image
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
category: examples
tags: [dockerfile, custom-image, mamba, pip, conda]
sources:
  - references/dockerfiles.md
  - references/startup-scripts.md
prerequisites:
  - concepts/03-foundation-layer.md
  - concepts/04-base-notebook.md
  - examples/01-basic-run.md
difficulty: intermediate
estimated-time: 20min
---

# 自定义镜像构建

本示例展示如何基于 Jupyter Docker Stacks 构建自定义镜像，包括安装额外包、添加自定义环境、配置扩展等常见场景。

## 构建原则

在开始之前，请理解以下关键原则：

1. **选择合适的基础镜像**：从最接近你需求的镜像继承（如 scipy-notebook 而非 base-notebook）
2. **以 jovyan 用户安装包**：避免以 root 安装 Python 包导致权限问题
3. **清理缓存减小镜像体积**：安装后执行 `mamba clean --all -f -y` 和 `fix-permissions`
4. **使用 mamba 优先**：mamba 比 conda 更快地解析依赖
5. **切换用户用 USER 指令**：不要在 Dockerfile 中使用 `sudo`

## 模式 1：使用 mamba 安装额外包（推荐）

创建 `Dockerfile`：

```dockerfile
# 选择基础镜像——选择最接近你需求的镜像以减小层大小
FROM quay.io/jupyter/scipy-notebook:2026-07-28

# 切换到 root 仅用于安装系统包
USER root

# 安装系统级依赖（如需要）
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    # 系统包列表
    graphviz \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 切换回 jovyan 用户安装 Python 包
USER ${NB_UID}

# 使用 mamba 安装 conda-forge 包（推荐）
RUN mamba install --yes \
    # Python 包列表
    'xgboost' \
    'lightgbm' \
    'graphviz' \
    'python-graphviz' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

**构建与运行**：

```bash
# 构建镜像
docker build --rm -t my-custom-scipy .

# 运行
docker run -it --rm -p 8888:8888 my-custom-scipy
```

## 模式 2：使用 pip 安装包

对于 conda-forge 中没有的包，使用 pip：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER ${NB_UID}

# 使用 pip 安装（--no-cache-dir 减小镜像体积）
RUN pip install --no-cache-dir \
    'some-pypi-only-package' \
    'another-package>=1.0' && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

:::{note}
混合使用 mamba/conda 和 pip 时，**先安装 conda 包，再安装 pip 包**，避免依赖冲突。
:::

## 模式 3：使用 requirements.txt

创建 `requirements.txt`：

```text
# requirements.txt
numpy>=1.26
pandas>=2.0
scikit-learn>=1.3
matplotlib>=3.8
```

创建 `Dockerfile`：

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

# 复制 requirements 文件
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/

USER ${NB_UID}

# 从 requirements.txt 安装
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}" && \
    rm /tmp/requirements.txt
```

## 模式 4：添加自定义 Conda 环境和 Jupyter 内核

当需要不同 Python 版本或隔离环境时：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

USER root

# 如需安装系统依赖
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# 创建 Python 3.11 的自定义环境（以 py311 为例）
RUN mamba create --yes -p "${CONDA_DIR}/envs/python311" python=3.11 ipykernel && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# 将自定义环境注册为 Jupyter 内核
RUN "${CONDA_DIR}/envs/python311/bin/python" -m ipykernel install \
    --user --name python311 --display-name "Python 3.11" && \
    fix-permissions "/home/${NB_USER}"

# 安装包到自定义环境
RUN "${CONDA_DIR}/envs/python311/bin/pip" install --no-cache-dir \
    'tensorflow==2.15' \
    'torch==2.1' && \
    fix-permissions "${CONDA_DIR}"
```

## 模式 5：启用 JupyterLab 扩展

```dockerfile
FROM quay.io/jupyter/scipy-notebook:2026-07-28

USER ${NB_UID}

# 安装 JupyterLab 扩展（pip 方式）
RUN pip install --no-cache-dir \
    'jupyterlab-git' \
    'jupyterlab-lsp' \
    'python-lsp-server' \
    'jupyter-dash' && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# 如需启用 server extension
RUN jupyter server extension enable jupyterlab_git && \
    fix-permissions "/home/${NB_USER}"
```

## 模式 6：安装 R 包（基于 r-notebook）

```dockerfile
FROM quay.io/jupyter/r-notebook:2026-07-28

USER root

# 安装系统依赖
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}

# 安装 R 包
RUN mamba install --yes \
    'r-arrow' \
    'r-duckdb' \
    'r-tidymodels' && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}"
```

## 模式 7：配置 Jupyter Server

创建自定义配置文件 `jupyter_server_config.py`：

```python
# jupyter_server_config.py
c = get_config()  # noqa

# 设置默认内核
c.MultiKernelManager.default_kernel_name = "python3"

# 禁用退出按钮（共享环境）
c.ServerApp.quit_button = False

# 设置 iFrame 允许来源
c.ServerApp.allow_origin_pat = ".*"

# 配置终端
c.ServerApp.terminals_enabled = True
```

Dockerfile 中复制配置：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

COPY --chown=${NB_UID}:${NB_GID} jupyter_server_config.py /etc/jupyter/
```

## 模式 8：使用启动 Hooks 进行运行时配置

如需在容器启动时执行自定义脚本（而非构建时），使用 hooks：

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

# 在标准选项处理之前执行的 hooks
COPY --chown=${NB_UID}:${NB_GID} my-startup-hook.sh /usr/local/bin/start-notebook.d/
RUN chmod +x /usr/local/bin/start-notebook.d/my-startup-hook.sh

# 在 Server 启动前执行的 hooks
COPY --chown=${NB_UID}:${NB_GID} my-pre-server-hook.sh /usr/local/bin/before-notebook.d/
RUN chmod +x /usr/local/bin/before-notebook.d/my-pre-server-hook.sh
```

示例 hook 脚本 `my-startup-hook.sh`：

```bash
#!/bin/bash
# 示例：启动时设置环境变量
export MY_CUSTOM_VAR="hello from hook"
echo "Custom hook executed: MY_CUSTOM_VAR=${MY_CUSTOM_VAR}"
```

## 模式 9：Docker Bake 构建（多镜像定制）

对于复杂场景，使用 Docker Bake 统一管理构建参数。创建 `docker-bake.hcl`：

```hcl
// docker-bake.hcl
group "default" {
    targets = ["custom-jupyter"]
}

target "docker-stacks-foundation" {
    context = "https://github.com/jupyter/docker-stacks.git#main"
    dockerfile = "images/docker-stacks-foundation/Dockerfile"
    args = {
        PYTHON_VERSION = "3.12"
    }
}

target "base-notebook" {
    context = "https://github.com/jupyter/docker-stacks.git#main"
    dockerfile = "images/base-notebook/Dockerfile"
    contexts = {
        docker-stacks-foundation = "target:docker-stacks-foundation"
    }
}

target "custom-jupyter" {
    context = "."
    dockerfile = "Dockerfile"
    contexts = {
        base-notebook = "target:base-notebook"
    }
    tags = ["custom-jupyter:latest"]
}
```

构建：

```bash
docker buildx bake
```

## 最佳实践清单

构建自定义镜像时，遵循以下检查清单：

- [ ] 选择了最具体的基础镜像（避免从 docker-stacks-foundation 开始）
- [ ] 系统包使用 `USER root` 安装，Python 包使用 `USER ${NB_UID}` 安装
- [ ] mamba/pip 安装后执行了 `clean` 和 `fix-permissions`
- [ ] 使用 `--no-cache-dir`（pip）或 `--all -f -y`（mamba）清理缓存
- [ ] `COPY` 指令使用 `--chown=${NB_UID}:${NB_GID}` 设置正确权限
- [ ] 没有在 Dockerfile 中使用 `sudo`
- [ ] 没有以 root 用户运行最终命令
- [ ] 固定了基础镜像版本标签（使用日期标签而非 `latest`）
- [ ] 构建后验证镜像能正常启动且包可导入

## 镜像体积优化技巧

1. **合并 RUN 指令**：将相关命令合并到一个 RUN 层，减少镜像层数
2. **同层清理**：安装和清理在同一个 RUN 指令中（P7 同层修改原则）
3. **使用 mamba 替代 conda**：更快且产生更少的缓存
4. **避免 `--no-install-recommends` 之外的冗余包**：系统包安装始终使用 `--no-install-recommends`
5. **多阶段构建**：如需编译 C 扩展，使用多阶段构建只保留最终产物

```dockerfile
# 多阶段构建示例（编译阶段）
FROM quay.io/jupyter/scipy-notebook:2026-07-28 AS builder

USER root
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER ${NB_UID}
RUN pip install --no-cache-dir --prefix=/install some-package-with-extensions

# 最终镜像
FROM quay.io/jupyter/scipy-notebook:2026-07-28
COPY --from=install /opt/conda/lib/python3.*/site-packages/ /opt/conda/lib/python3.*/site-packages/
```

## 验证自定义镜像

```bash
# 构建镜像
docker build --rm -t my-custom-image .

# 启动测试
docker run -it --rm -p 8888:8888 my-custom-image

# 在 JupyterLab 中验证包已安装
# 1. 打开 notebook 执行 import 测试
# 2. 在终端执行: conda list | grep <package-name>
# 3. 执行: pip list | grep <package-name>
```

## 常见错误与修复

| 错误 | 原因 | 修复 |
|------|------|------|
| Permission denied 安装包 | 以 root 用户执行 pip/mamba | 切换到 `USER ${NB_UID}` |
| 镜像体积过大 | 未清理缓存 | 添加 `mamba clean`/`pip --no-cache-dir` |
| 包找不到 | 安装到了错误的环境 | 确认使用默认环境 `/opt/conda` |
| Kernel 不显示 | 未注册 ipykernel | 执行 `python -m ipykernel install --user` |
| 启动 hooks 不执行 | 没有执行权限 | 添加 `RUN chmod +x` |

## 下一步

- 学习 [GPU/CUDA 加速](03-gpu-cuda.md) 配置深度学习环境
- 了解 [CI/CD 集成](04-ci-integration.md) 实现镜像自动构建
- 参考 [常用配方集锦](05-recipes.md) 获取更多实用 Dockerfile 模板
