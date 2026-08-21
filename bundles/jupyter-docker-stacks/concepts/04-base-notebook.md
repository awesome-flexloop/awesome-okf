---
type: Concept
title: "Base Notebook 层详解"
description: "base-notebook 镜像的 Dockerfile 解析、Jupyter组件安装、服务器配置、HEALTHCHECK机制"
tags: [base-notebook, jupyterlab, jupyter-server, healthcheck, pandoc]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:00:00Z" }
status: stable
stale_after: 2027-08-21
sources:
  - { id: src-dockerfile, resource: "/references/dockerfiles.md", title: "Base Notebook Dockerfile" }
  - { id: src-startup, resource: "/references/startup-scripts.md", title: "启动脚本与配置" }
---

# Base Notebook 层详解

base-notebook 是 L2 层镜像，基于 docker-stacks-foundation 构建，安装核心 Jupyter 组件并配置服务器。这是**最常直接使用的镜像之一**，适合不需要额外科学计算包、但需要完整Jupyter功能的场景。

## Dockerfile 解析

### OS包安装

```dockerfile
USER root
RUN apt-get update --yes && \
    apt-get install --yes --no-install-recommends \
    fonts-liberation \
    pandoc \
    run-one && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
```

| 包 | 作用 |
|----|------|
| fonts-liberation | Liberation字体（Arial/Times/Courier替代），matplotlib/seaborn绘图需要 |
| pandoc | 文档转换工具，nbconvert依赖它将notebook转换为HTML/Markdown/PDF等格式 |
| run-one | 确保同一命令只有一个实例运行；`run-one-constantly`用于RESTARTABLE自动重启功能 |

### Conda安装Jupyter组件

```dockerfile
USER ${NB_UID}
WORKDIR /tmp
RUN mamba install --yes \
    'jupyterhub-singleuser' \
    'jupyterlab' \
    'nbclassic' \
    'notebook>=7.2.2' && \
    jupyter server --generate-config && \
    mamba clean --all -f -y && \
    jupyter lab clean && \
    rm -rf "/home/${NB_USER}/.cache/yarn" && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
```

安装的Jupyter组件：

| 包 | 说明 |
|----|------|
| jupyterhub-singleuser | JupyterHub单用户服务器（JupyterHub集成必需） |
| jupyterlab | JupyterLab前端（默认UI） |
| nbclassic | Jupyter Notebook v7的经典界面扩展 |
| notebook>=7.2.2 | Jupyter Notebook v7+（最低版本固定以兼容新版JupyterLab） |

> **为什么固定 notebook>=7.2.2？** JupyterLab发布新版本时，旧版notebook(<v7)可能不兼容，但conda解析可能安装旧版notebook。最低版本约束确保JupyterLab和Notebook兼容性。

安装后操作：
- `jupyter server --generate-config`：生成默认服务器配置文件
- `mamba clean --all -f -y`：清理conda缓存
- `jupyter lab clean`：清理JupyterLab扩展缓存
- `rm -rf .cache/yarn`：清理JupyterLab扩展安装时的yarn缓存

### 端口与启动命令

```dockerfile
ENV JUPYTER_PORT=8888
EXPOSE $JUPYTER_PORT
CMD ["start-notebook.py"]
```

- 默认Jupyter端口8888
- CMD设为`start-notebook.py`（注意：ENTRYPOINT是foundation层的`tini → start.sh`）

### 文件复制与权限

```dockerfile
COPY start-notebook.py start-notebook.sh start-singleuser.py start-singleuser.sh /usr/local/bin/
COPY jupyter_server_config.py docker_healthcheck.py /etc/jupyter/

USER root
RUN fix-permissions /etc/jupyter/
```

- 启动脚本复制到`/usr/local/bin/`
- 配置文件和健康检查脚本复制到`/etc/jupyter/`
- 以root身份运行fix-permissions确保配置文件可被jovyan用户读取

### HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=3s --timeout=1s --start-period=3s --retries=3 \
    CMD ["/etc/jupyter/docker_healthcheck.py"]
```

健康检查参数：

| 参数 | 值 | 说明 |
|------|----|------|
| --interval | 3s | 每3秒检查一次 |
| --timeout | 1s | 单次检查超时1秒 |
| --start-period | 3s | 容器启动后3秒开始检查（给Jupyter Server启动时间） |
| --retries | 3 | 连续3次失败才标记为unhealthy |

## Jupyter Server 配置

jupyter_server_config.py 配置了服务器默认行为：

```python
c = get_config()
c.ServerApp.ip = ""                    # 监听所有接口（IPv4+IPv6）
c.ServerApp.open_browser = False      # 不在容器内打开浏览器
c.InlineBackend.figure_formats = {"png", "jpeg", "svg", "pdf"}  # 内联图形多格式
c.FileContentsManager.delete_to_trash = False  # 删除文件直接删除（不移到回收站）
```

关键配置项说明：

1. **监听所有接口**：`c.ServerApp.ip = ""` 确保容器外部可以访问Jupyter Server（不能只绑定127.0.0.1）
2. **不自动打开浏览器**：容器内无桌面环境，不需要
3. **多格式内联图**：notebook中的matplotlib图同时生成PNG/JPEG/SVG/PDF格式，兼顾显示质量和导出需求
4. **删除到回收站关闭**：容器内回收站机制可能导致磁盘空间不可见地增长

### 自签名证书（GEN_CERT）

当设置`GEN_CERT`环境变量时，自动生成自签名SSL证书：

```python
if "GEN_CERT" in os.environ:
    # 生成openssl配置
    # 生成2048位RSA密钥和自签名证书（365天有效期）
    # 证书存放在jupyter_data_dir()/notebook.pem
    # 设置c.ServerApp.certfile
```

这对HTTPS部署很有用，避免手动配置证书。

### NB_UMASK

```python
if "NB_UMASK" in os.environ:
    os.umask(int(os.environ["NB_UMASK"], 8))
```

允许通过`NB_UMASK`环境变量设置Jupyter Server子进程的umask，控制新建文件的默认权限。

## start-notebook.py 启动逻辑

start-notebook.py 是CMD的入口点，负责决定启动哪个Jupyter命令：

1. **JupyterHub检测**：如果存在`JUPYTERHUB_API_TOKEN`环境变量，自动切换到`start-singleuser.py`
2. **重启模式**：如果`RESTARTABLE=yes`，使用`run-one-constantly`包装jupyter命令实现崩溃自动重启
3. **命令选择**：读取`DOCKER_STACKS_JUPYTER_CMD`环境变量（默认`lab`），决定jupyter子命令
4. **参数传递**：解析`NOTEBOOK_ARGS`环境变量（shlex分割）和命令行参数，附加到jupyter命令
5. **执行**：使用`os.execvp`替换当前进程

```
执行链路：
start.sh → sudo降权 → before-notebook.d hooks → start-notebook.py
  ├─ JupyterHub? → start-singleuser.py
  └─ 普通启动 → jupyter lab（默认）
```

## start-notebook.sh / start-singleuser.sh

这两个`.sh`文件只是**兼容shim**：

```bash
#!/bin/bash
echo "WARNING: Use start-notebook.py instead"
exec /usr/local/bin/start-notebook.py "$@"
```

它们存在是为了向后兼容旧版Dockerfile或用户脚本中直接调用`.sh`的情况。新代码应该直接使用`.py`版本。

## 相关概念

- [Foundation层详解](03-foundation-layer.md)
- [Minimal到SciPy层](05-minimal-scipy.md)
- [启动生命周期](07-startup-lifecycle.md)
- [用户与权限模型](09-user-permissions.md)
