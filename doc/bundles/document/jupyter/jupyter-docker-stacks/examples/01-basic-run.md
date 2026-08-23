---
title: 基础运行示例
id: ex-01-basic-run
version: 0.2.0
okf-spec: v0.2
bundle: jupyter-docker-stacks
category: examples
tags: [docker, getting-started, jupyterlab, scipy-notebook]
sources:
  - references/startup-scripts.md
  - references/dockerfiles.md
prerequisites:
  - concepts/00-introduction.md
  - concepts/01-getting-started.md
difficulty: beginner
estimated-time: 10min
---

# 基础运行示例

本示例展示如何使用 Jupyter Docker Stacks 快速启动一个 Jupyter 环境，涵盖最常用的启动模式。

## 前置条件

- 已安装 Docker Engine（支持 Linux/macOS/WSL2）
- 本地 Docker 守护进程正在运行
- 至少 4GB 可用磁盘空间（用于拉取镜像）

## 示例 1：最简单的启动方式

以下命令拉取 `jupyter/scipy-notebook` 镜像并启动 JupyterLab 服务器：

```bash
docker run -it -p 8888:8888 quay.io/jupyter/scipy-notebook:2026-07-28
```

**参数说明**：

| 参数 | 作用 |
|------|------|
| `-it` | 交互式终端模式，可查看日志并通过 Ctrl+C 停止 |
| `-p 8888:8888` | 将容器内 8888 端口映射到主机 8888 端口 |
| `quay.io/jupyter/scipy-notebook:2026-07-28` | 指定镜像和日期标签（推荐使用固定日期标签保证可复现） |

**预期输出**：

```
Entered start.sh with args: start-notebook.py
...
    To access the server, open this file in a browser:
        file:///home/jovyan/.local/share/jupyter/runtime/jpserver-7-open.html
    Or copy and paste one of these URLs:
        http://127.0.0.1:8888/lab?token=<随机token>
```

打开浏览器访问输出中的 URL（带 token），即可进入 JupyterLab 界面。

**停止与清理**：按两次 `Ctrl+C` 关闭服务器。容器保留在磁盘上，可通过 `docker ps --all` 查看，使用 `docker rm <container_id>` 删除。

## 示例 2：挂载工作目录 + 自动清理

推荐日常使用的方式——挂载当前目录并在退出时自动删除容器：

```bash
docker run -it --rm -p 8888:8888 -v "${PWD}":/home/jovyan/work quay.io/jupyter/scipy-notebook:2026-07-28
```

**关键参数**：

| 参数 | 作用 |
|------|------|
| `--rm` | 容器停止后自动删除（不留残留） |
| `-v "${PWD}":/home/jovyan/work` | 将当前目录挂载到容器内 `/home/jovyan/work`，数据持久化到主机 |

:::{note}
默认的 Jupyter 根目录是 `/home/jovyan`，新建 notebook 默认保存在这里。若要将工作目录设为挂载的目录，添加参数：
`start-notebook.py --ServerApp.root_dir=/home/jovyan/work`
:::

**权限问题**：如果挂载目录出现权限错误，确保主机目录对 UID=1000（jovyan 默认用户）有读写权限，或使用 `-e NB_UID=$(id -u)` 调整容器内 UID：

```bash
docker run -it --rm \
    -p 8888:8888 \
    --user root \
    -e NB_UID=$(id -u) \
    -e NB_GID=$(id -g) \
    -e CHOWN_HOME=yes \
    -v "${PWD}":/home/jovyan/work \
    quay.io/jupyter/scipy-notebook:2026-07-28
```

## 示例 3：后台运行 + 随机端口

适合服务器环境，容器在后台运行：

```bash
# 启动容器（后台模式，随机端口映射）
docker run -d -P --name my-jupyter quay.io/jupyter/scipy-notebook:2026-07-28

# 查看随机分配的主机端口
docker port my-jupyter 8888
# 输出示例: 0.0.0.0:49153

# 查看日志获取 token
docker logs --tail 5 my-jupyter

# 访问地址: http://127.0.0.1:<端口>/lab?token=<token>

# 停止并删除
docker stop my-jupyter && docker rm my-jupyter
```

## 示例 4：使用密码替代 Token

生产或共享环境推荐使用密码认证。首先生成密码哈希：

```bash
# 在容器内生成密码哈希（需要先有一个运行的容器）
docker run --rm quay.io/jupyter/base-notebook:2026-07-28 \
    python -c "from jupyter_server.auth import passwd; print(passwd('your-password'))"
```

然后使用哈希密码启动：

```bash
docker run -it --rm -p 8888:8888 quay.io/jupyter/base-notebook:2026-07-28 \
    start-notebook.py --PasswordIdentityProvider.hashed_password='argon2:$argon2id$v=19$m=10240,t=10,p=8$...'
```

## 示例 5：切换前端界面

默认使用 JupyterLab，可通过环境变量切换：

```bash
# 经典 Jupyter Notebook
docker run -it --rm -p 8888:8888 \
    -e DOCKER_STACKS_JUPYTER_CMD=notebook \
    quay.io/jupyter/base-notebook:2026-07-28

# NBClassic 界面
docker run -it --rm -p 8888:8888 \
    -e DOCKER_STACKS_JUPYTER_CMD=nbclassic \
    quay.io/jupyter/base-notebook:2026-07-28

# 仅启动 Jupyter Server（无前端）
docker run -it --rm -p 8888:8888 \
    -e DOCKER_STACKS_JUPYTER_CMD=server \
    quay.io/jupyter/base-notebook:2026-07-28
```

## 示例 6：无 Token 模式（受信内网环境）

在已隔离的安全环境中，可以禁用 token 认证：

```bash
docker run -it --rm -p 8888:8888 quay.io/jupyter/base-notebook:2026-07-28 \
    start-notebook.py --IdentityProvider.token=''
```

:::{warning}
无 token 模式仅适用于完全隔离的受信环境，绝不要在公网暴露的容器中使用！
:::

## 常见问题排查

| 问题 | 解决方案 |
|------|----------|
| 端口 8888 被占用 | 改用其他端口，如 `-p 8889:8888` |
| 挂载目录 Permission denied | 参考示例 2 的 UID/GID 映射方案 |
| 浏览器无法访问 | 检查防火墙设置，确认使用 `127.0.0.1` 而非容器内部 IP |
| Token 丢失 | 使用 `docker logs <container_id>` 查看日志 |
| 镜像拉取慢 | 配置 Docker 镜像加速器，或使用 `docker pull` 预拉取 |

## 验证步骤

启动容器后，执行以下验证：

1. 浏览器能正常打开 JupyterLab 界面
2. 新建一个 Python 3 notebook，执行 `print("Hello Jupyter!")` 能正常输出
3. 执行 `import numpy, pandas, matplotlib` 确认科学计算包可用（scipy-notebook）
4. 在终端中执行 `whoami` 应输出 `jovyan`
5. 执行 `conda --version` 和 `mamba --version` 确认包管理器可用

## 下一步

- 学习 [自定义镜像构建](02-custom-image.md) 来预装自己的依赖
- 了解 [GPU/CUDA 使用](03-gpu-cuda.md) 进行深度学习加速
- 掌握 [启动生命周期](../concepts/07-startup-lifecycle.md) 理解容器内部机制
