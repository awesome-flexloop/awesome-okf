---
type: Concept
title: "最佳实践"
description: "使用Jupyter Docker Stacks的推荐模式：镜像选择、自定义构建、安全配置、性能优化、常见陷阱"
tags: [best-practices, recipes, customization, security, performance, pitfalls]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-docs, resource: "/references/makefile-ci-source.md", title: "官方文档与CI/CD" }
---

# 最佳实践

本章总结使用 Jupyter Docker Stacks 的推荐模式、安全配置、性能优化技巧和常见陷阱。

## 镜像选择最佳实践

### 1. 选择满足需求的最小镜像

不要默认使用`datascience-notebook`或`all-spark-notebook`。镜像越大：
- 拉取时间越长
- 安全攻击面越大
- 启动越慢
- 磁盘占用越大

| 需求 | 推荐镜像 |
|------|---------|
| 纯Python教学/基础数据分析 | base-notebook + 自己装包 |
| Python科学计算 | scipy-notebook |
| R统计分析 | r-notebook（比datascience轻量） |
| 多语言数据科学 | datascience-notebook |
| GPU深度学习 | pytorch-notebook:cuda12 或 tensorflow-notebook:cuda |
| 大数据处理 | pyspark-notebook |

### 2. 固定版本标签

始终使用日期标签（如`2026-07-28`）而非`latest`，确保环境可复现：

```bash
# ✅ 好：固定版本
docker run -p 8888:8888 quay.io/jupyter/scipy-notebook:2026-07-28

# ❌ 不好：latest会变，结果不可复现
docker run -p 8888:8888 quay.io/jupyter/scipy-notebook:latest
```

## 自定义镜像最佳实践

### 1. 基于官方镜像构建

```dockerfile
FROM quay.io/jupyter/base-notebook:2026-07-28

# 以root安装系统包
USER root
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends some-package && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 以jovyan安装Python包
USER ${NB_UID}
RUN mamba install --yes some-conda-package && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# 恢复jovyan用户
USER ${NB_UID}
```

### 2. 始终在安装包后运行 fix-permissions

每次`mamba install`或`pip install`后都运行`fix-permissions`，确保文件对users组可写。否则容器内不同用户可能无法访问安装的包。

### 3. 同层清理（P7原则）

apt-get update/install/clean必须在**同一个RUN层**，mamba install/clean同理。跨层清理无效，会增加镜像体积。

```dockerfile
# ✅ 好：同层安装+清理
RUN apt-get update --yes && \
    apt-get install --yes package && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ❌ 不好：跨层清理
RUN apt-get update --yes && apt-get install --yes package
RUN apt-get clean && rm -rf /var/lib/apt/lists/*  # 不减小体积！
```

### 4. 使用Hook而非修改启动脚本

不要直接修改start.sh或start-notebook.py。使用Hook目录扩展启动行为：

```dockerfile
# ✅ 好：使用Hook
COPY my-setup.sh /usr/local/bin/before-notebook.d/

# ❌ 不好：覆盖启动脚本
COPY my-start.sh /usr/local/bin/start.sh  # 会与官方更新冲突
```

### 5. 使用pip --no-cache-dir

pip安装时使用`--no-cache-dir`避免缓存文件进入镜像层：

```dockerfile
RUN pip install --no-cache-dir some-package
```

### 6. conda-forge优先

mamba默认从conda-forge安装包（initial-condarc配置）。conda-forge包通常更新更快、更全面。

## 运行时最佳实践

### 1. 挂载工作目录

始终将工作目录挂载到`/home/jovyan/work`：

```bash
docker run -it --rm \
    -p 8888:8888 \
    -v "${PWD}":/home/jovyan/work \
    quay.io/jupyter/scipy-notebook:2026-07-28
```

### 2. 使用 --rm 自动清理

临时开发使用`--rm`，容器退出后自动删除：

```bash
docker run -it --rm -p 8888:8888 quay.io/jupyter/base-notebook
```

### 3. 设置Token

生产环境设置固定token或禁用token（配合其他认证方式）：

```bash
# 固定token
docker run -p 8888:8888 quay.io/jupyter/base-notebook \
    start-notebook.py --IdentityProvider.token=my-secret-token

# 禁用token（仅在可信网络/反向代理后使用！）
docker run -p 8888:8888 quay.io/jupyter/base-notebook \
    start-notebook.py --IdentityProvider.token=''
```

### 4. 容器重启策略

需要长期运行的服务使用Docker restart policy：

```bash
docker run -d --restart unless-stopped \
    -p 8888:8888 \
    --name jupyter \
    quay.io/jupyter/scipy-notebook:2026-07-28
```

或者使用内置的RESTARTABLE：
```bash
docker run -d -p 8888:8888 -e RESTARTABLE=yes quay.io/jupyter/scipy-notebook
```

## 安全最佳实践

### 1. 不以root运行Jupyter

默认配置已经以jovyan（UID 1000）运行Jupyter。不要使用`--user root`启动然后直接运行notebook。

如果需要sudo权限（安装系统包），使用GRANT_SUDO但理解安全风险：

```bash
# 仅在可信环境中使用
docker run -it --rm -p 8888:8888 \
    -e GRANT_SUDO=yes --user root \
    quay.io/jupyter/base-notebook
```

### 2. 不要在镜像中硬编码密钥

使用Docker secrets或运行时环境变量传递敏感信息：

```bash
# ✅ 好：运行时传入
docker run -e AWS_ACCESS_KEY_ID=xxx -e AWS_SECRET_ACCESS_KEY=yyy ...

# ❌ 不好：在Dockerfile中写死
ENV AWS_SECRET_ACCESS_KEY=yyy  # 会进入镜像层！
```

### 3. 使用HTTPS

生产环境启用SSL/TLS：

```bash
# 自动生成自签名证书
docker run -p 8888:8888 -e GEN_CERT=yes quay.io/jupyter/base-notebook

# 或挂载自己的证书
docker run -p 8888:8888 \
    -v ./mycert.pem:/etc/jupyter/mycert.pem:ro \
    quay.io/jupyter/base-notebook \
    start-notebook.py --ServerApp.certfile=/etc/jupyter/mycert.pem
```

### 4. 网络隔离

JupyterHub部署时，将用户容器放在内部网络中，通过反向代理暴露。

## 性能优化

### 1. 预构建matplotlib缓存

scipy-notebook已经在构建时执行`import matplotlib`预热字体缓存。自定义镜像如果安装额外字体，也应执行类似操作。

### 2. 使用mamba而非conda安装包

mamba使用libsolv求解器，比conda快得多。官方镜像默认安装mamba。

### 3. 清理所有缓存

```dockerfile
RUN mamba install --yes packages && \
    mamba clean --all -f -y && \
    jupyter lab clean && \
    npm cache clean --force || true && \
    rm -rf /home/${NB_USER}/.cache/yarn && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

### 4. 挂载pip/conda缓存（开发时）

开发时可以挂载缓存目录加速包安装：

```bash
docker run -it --rm -p 8888:8888 \
    -v pip-cache:/home/jovyan/.cache/pip \
    -v conda-pkgs:/opt/conda/pkgs \
    quay.io/jupyter/base-notebook
```

## 常见陷阱

### 1. 忘记设置--user root就想GRANT_SUDO

GRANT_SUDO必须配合`--user root`启动，否则sudo配置无法写入。非root启动时GRANT_SUDO被忽略并打印警告。

### 2. chown挂载目录

CHOWN_HOME=yes对挂载的宿主机目录执行chown -R会修改宿主机文件的所有者！仅在必要时使用，且理解后果。

```bash
# ⚠️ 警告：这会修改宿主机当前目录的文件所有者！
docker run --user root -e CHOWN_HOME=yes -v "${PWD}":/home/jovyan/work ...
```

推荐做法是启动时通过NB_UID匹配宿主机UID，而非chown。

### 3. 修改/etc/sudoers直接

不要直接编辑`/etc/sudoers`，使用`/etc/sudoers.d/`目录下的文件。官方镜像已经禁用了默认的sudo组权限。

### 4. 在.bashrc中写复杂逻辑

`start-notebook.py`通过`os.execvp`启动jupyter，不经过交互式bash shell，因此.bashrc中的配置不会被Jupyter Server进程继承。使用before-notebook.d hooks来设置环境变量。

### 5. 使用conda activate而非mamba activate

在容器内，使用`conda activate`或`mamba activate`都可以，但在非交互式shell（如hook脚本）中需要先初始化conda。before-notebook.d/10activate-conda-env.sh已经处理了这个问题。

### 6. 镜像版本不兼容CUDA驱动

CUDA变体镜像要求宿主机NVIDIA驱动版本与CUDA版本兼容。使用nvidia-smi检查驱动版本，选择匹配的CUDA变体。

### 7. Rosetta缓存（Apple Silicon）

在Apple Silicon Mac上运行x86_64镜像时，Rosetta 2转译器会在.cache/rosetta目录生成缓存。Dockerfile中反复`rm -rf .cache/rosetta`就是为了防止这个缓存增大镜像体积。如果自定义镜像安装了大量二进制文件，也应加入这个清理步骤。

### 8. pip与conda混用

尽量避免在同一个环境中混用pip和conda安装包，可能导致依赖冲突。如果必须混用，先conda安装所有能装的，再pip安装剩余的，并且使用`--no-deps`谨慎处理依赖。

## JupyterHub 部署

JupyterHub部署时使用`start-singleuser.py`（start-notebook.py自动检测JUPYTERHUB_API_TOKEN）。关键配置：

1. 使用JupyterHub的DockerSpawner或KubeSpawner
2. 镜像选择base-notebook或更高层
3. 设置容器安全上下文（非root、只读根文件系统等）
4. 配置资源限制（CPU/内存/GPU）
5. 使用持久卷挂载用户home目录

## 相关概念

- [Hook扩展与自定义](08-hooks-and-customization.md)
- [用户与权限模型](09-user-permissions.md)
- [启动生命周期](07-startup-lifecycle.md)
- [自定义镜像示例](../examples/02-custom-image.md)
- [常用配方示例](../examples/05-common-recipes.md)
