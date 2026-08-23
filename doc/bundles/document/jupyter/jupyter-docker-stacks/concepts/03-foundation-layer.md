---
type: Concept
title: "Foundation 层详解"
description: "docker-stacks-foundation 镜像的 Dockerfile 逐层解析、Micromamba BuildKit 注入模式、用户创建与权限模型"
tags: [foundation, dockerfile, micromamba, buildkit, user-model, permissions]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-dockerfile, resource: "/references/dockerfiles.md", title: "Foundation Dockerfile" }
  - { id: src-startup, resource: "/references/startup-scripts.md", title: "启动脚本" }
---

# Foundation 层详解

docker-stacks-foundation 是所有 Jupyter Docker Stacks 镜像的**最底层**（L1），基于 Ubuntu 24.04 构建，负责操作系统配置、用户模型、Conda/Python 环境和启动框架。

## Dockerfile 逐层解析

### Stage 0: 参数定义与多阶段构建

```dockerfile
ARG ROOT_IMAGE=default_root_image
FROM ubuntu:24.04@sha256:5616... AS default_root_image
FROM mambaorg/micromamba:2.8.1@sha256:fb18... AS micromamba
FROM $ROOT_IMAGE
```

关键设计：
- **ROOT_IMAGE 可替换**：通过 build arg 允许完全替换基础镜像（用于自定义场景）
- **Micromamba 多阶段**：将 mambaorg/micromamba 镜像作为 build stage，通过 BuildKit bind mount 注入二进制
- **Digest 固定**：所有基础镜像使用 sha256 digest 固定版本，确保可复现构建，由 Dependabot 自动更新

### Stage 1: OS系统包安装（root用户）

```dockerfile
USER root
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    ca-certificates locales netbase sudo tini wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen
```

每个包的作用：

| 包 | 作用 |
|----|------|
| ca-certificates | SSL/TLS证书验证 |
| locales | 本地化支持（配置en_US.UTF-8和C.UTF-8） |
| netbase | 提供/etc/protocols、/etc/rpc、/etc/services（POSIX必需） |
| sudo | 可选的提权支持（通过GRANT_SUDO控制） |
| tini | PID 1 init进程，回收僵尸进程 |
| wget | HTTP下载工具 |

- `apt-get upgrade` 修复基础镜像的已知漏洞
- `--no-install-recommends` 最小化安装
- `apt-get clean && rm -rf /var/lib/apt/lists/*` 清理缓存减小镜像体积

### Stage 2: 环境变量配置

```dockerfile
ENV CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    NB_USER="jovyan" \
    NB_UID=1000 \
    NB_GID=100 \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    LANGUAGE=C.UTF-8
ENV PATH="${CONDA_DIR}/bin:${PATH}" \
    HOME="/home/${NB_USER}"
```

关键环境变量：
- `CONDA_DIR=/opt/conda`：Conda安装到系统级目录（非用户home）
- `NB_USER=jovyan`：默认用户名（jovyan是Jupyter社区传统用户名，意为"木星居民"）
- `NB_UID=1000`/`NB_GID=100`：默认UID/GID，GID 100是Ubuntu的`users`组
- `LC_ALL=C.UTF-8`：强制UTF-8编码，避免容器内locale问题

### Stage 3: Bash配置与用户创建

```dockerfile
RUN sed -i 's/^#force_color_prompt=yes/force_color_prompt=yes/' /etc/skel/.bashrc && \
    echo 'eval "$(conda shell.bash hook)"' >> /etc/skel/.bashrc
```

在 `/etc/skel/.bashrc`（新用户的模板）中：
- 启用bash提示符颜色
- 自动激活conda base环境（这样每次shell启动都能直接使用conda/mamba）

```dockerfile
RUN if id -un "${NB_UID}" >/dev/null 2>&1; then \
        userdel --remove "$(id -un "${NB_UID}")"; \
    fi
RUN echo "auth requisite pam_deny.so" >> /etc/pam.d/su && \
    sed -i.bak -e 's/^%admin/#%admin/' /etc/sudoers && \
    sed -i.bak -e 's/^%sudo/#%sudo/' /etc/sudoers && \
    useradd --no-log-init --create-home --shell /bin/bash --uid "${NB_UID}" --no-user-group "${NB_USER}" && \
    mkdir -p "${CONDA_DIR}" && \
    chown "${NB_USER}:${NB_GID}" "${CONDA_DIR}" && \
    chmod g+w /etc/passwd && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

用户创建逻辑：
1. 先删除UID=1000的已有用户（处理基础镜像中可能存在的冲突）
2. **禁用su**：通过PAM配置禁止`su`命令（所有用户切换通过sudo）
3. **注释掉默认sudo组**：禁用admin和sudo组的默认sudo权限（精确控制通过GRANT_SUDO）
4. 创建jovyan用户，使用`--no-user-group`（不创建同名用户组，加入users组GID 100）
5. `/etc/passwd`设为组可写（start.sh需要能修改passwd来重映射UID）
6. 运行fix-permissions设置组写权限和setgid位

### Stage 4: Micromamba安装Conda环境（BuildKit bind mount模式）

```dockerfile
COPY --chown="${NB_UID}:${NB_GID}" initial-condarc "${CONDA_DIR}/.condarc"
WORKDIR /tmp
RUN --mount=type=bind,from=micromamba,source=/bin/micromamba,target=/usr/local/bin/micromamba \
    set -x && \
    PYTHON_SPECIFIER="python=${PYTHON_VERSION}" && \
    if [ "${PYTHON_VERSION}" = "default" ]; then PYTHON_SPECIFIER="python"; fi && \
    micromamba install \
        --root-prefix="${CONDA_DIR}" \
        --prefix="${CONDA_DIR}" \
        --yes \
        'jupyter_core' \
        'conda' \
        "mamba==$(micromamba --version)" \
        "${PYTHON_SPECIFIER}" && \
    mamba list --full-name 'python' | awk 'END{sub("[^.]*$", "*", $2); print $1 " " $2}' >> "${CONDA_DIR}/conda-meta/pinned" && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

这是最精巧的设计之一——**Micromamba BuildKit注入模式**：

1. **不将micromamba留在镜像中**：通过`--mount=type=bind,from=micromamba,...`将micromamba二进制从另一个build stage挂载到当前构建上下文，安装完成后挂载自动消失，不增加镜像体积
2. **安装版本匹配的mamba**：`"mamba==$(micromamba --version)"`确保安装的mamba版本与micromamba二进制版本一致（它们一起发布）
3. **版本固定**：通过conda-meta/pinned文件固定Python的major.minor版本，防止意外升级
4. **同层清理**：mamba clean和fix-permissions在同一个RUN层执行，避免产生额外的镜像层

### Stage 5: 启动脚本与Hook目录

```dockerfile
COPY _docker_stacks_log.sh run-hooks.sh start.sh /usr/local/bin/
ENTRYPOINT ["tini", "-g", "--", "start.sh"]

USER root
RUN mkdir /usr/local/bin/start-notebook.d && \
    mkdir /usr/local/bin/before-notebook.d
COPY 10activate-conda-env.sh /usr/local/bin/before-notebook.d/
```

- ENTRYPOINT使用tini作为init，然后调用start.sh
- 创建两个Hook目录供下游镜像和用户自定义扩展
- 10activate-conda-env.sh是before-notebook.d中的第一个hook，负责激活conda环境

## fix-permissions 脚本

fix-permissions是一个关键工具脚本，用于在安装软件包后修复目录权限：

```bash
for d in "$@"; do
    find "${d}" \
        ! \( -group "${NB_GID}" -a -perm -g+rwX \) \
        -exec chgrp "${NB_GID}" -- {} \+ \
        -exec chmod g+rwX -- {} \+
    find "${d}" \
        -type d \
        ! -perm -g+s \
        -exec chmod g+s -- {} \+
done
```

核心逻辑：
1. **只修改不符合权限的文件**：使用find的否定条件，跳过已经正确设置权限的文件——这对避免Docker镜像膨胀至关重要（修改文件会触发OverlayFS Copy-on-Write复制整个文件到上层）
2. **组权限**：将文件组设为`${NB_GID}`（users组），授予组读写和目录执行权限
3. **SetGID位**：对目录设置setgid位，确保新创建的文件/子目录自动继承users组

> 这是Docker镜像优化的一个重要技巧：盲目`chmod -R`会导致所有文件被复制到可写层，显著增大镜像体积。fix-permissions的"只修改不满足条件的文件"策略避免了这个问题。

## Rosetta缓存清理

Dockerfile中反复出现：
```dockerfile
RUN rm -rf "/home/${NB_USER}/.cache/rosetta"
```

这是为了清理macOS上Rosetta 2转译x86_64二进制时产生的缓存垃圾。该缓存在ARM Mac上运行x86_64容器时自动产生，没有实际用处但会增加镜像体积。

## 相关概念

- [镜像层级架构](02-image-hierarchy.md)
- [Base Notebook层详解](04-base-notebook.md)
- [启动生命周期](07-startup-lifecycle.md)
- [Hook扩展与自定义](08-hooks-and-customization.md)
- [用户与权限模型](09-user-permissions.md)
