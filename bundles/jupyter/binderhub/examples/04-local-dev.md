---
type: Example
title: "本地开发调试"
description: "BinderHub本地开发环境搭建：源码安装、本地Docker构建、连接远程JupyterHub/Registry、Docker-in-Docker、Minikube开发、SSE调试、pytest测试、前端React开发、构建故障排查"
tags: [binderhub, development, local-dev, debugging, docker, minikube, pytest, react, sse]
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T20:45:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# 本地开发调试

本文档介绍如何在本地搭建 BinderHub 开发环境，包括源码安装、本地构建、连接远程服务、测试和调试技巧。根据开发目标（纯前端/后端逻辑/K8s集成），提供多种开发模式。

## 1. 获取源码与安装开发依赖

### 1.1 克隆源码

```bash
git clone https://github.com/jupyterhub/binderhub.git
cd binderhub
```

### 1.2 安装开发依赖

推荐使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 以可编辑模式安装BinderHub及开发依赖
pip install -e ".[dev]"
```

`[dev]` 额外依赖（来自 `dev-requirements.txt`）：

| 包名 | 用途 |
|------|------|
| `pytest` | 单元测试框架 |
| `pytest-asyncio` | 异步测试支持 |
| `pytest-cov` | 测试覆盖率 |
| `pytest-timeout` | 测试超时控制 |
| `pytest_playwright` | 浏览器端到端测试 |
| `jupyter-repo2docker>=2021.08.0` | 镜像构建核心工具 |
| `dockerspawner` | Docker Spawner（本地JupyterHub） |
| `beautifulsoup4[html5lib]` | HTML解析（测试用） |
| `chartpress>=2.1` | Helm Chart构建工具 |
| `nest-asyncio` | 嵌套事件循环支持 |
| `requests` | HTTP客户端（API示例） |

### 1.3 验证安装

```bash
# 验证可执行模块
python -m binderhub --help
python -m binderhub --version

# 生成默认配置文件
python -m binderhub --generate-config
# 会在当前目录生成 binderhub_config.py
```

## 2. 本地运行（无 Kubernetes）

不依赖 Kubernetes 集群，直接在本地 Docker 上构建镜像，适用于后端逻辑开发和快速原型验证。

### 2.1 使用 LocalRepo2dockerBuild

`LocalRepo2dockerBuild` 直接调用本地 `jupyter-repo2docker` 命令构建镜像，连接本地 Docker daemon。

```python
# binderhub_config.py - 纯本地开发配置
import os
import socket

from binderhub.build_local import LocalRepo2dockerBuild
from binderhub.quota import LaunchQuota

# 获取本机IP（用于JupyterHub连接）
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostip = s.getsockname()[0]
s.close()

# ---- 基础配置 ----
c.BinderHub.debug = True
c.BinderHub.use_registry = False       # 本地构建不需要Registry
c.BinderHub.builder_required = False   # 不要求K8s构建基础设施
c.BinderHub.port = 8585

# ---- 使用本地构建器 ----
c.BinderHub.build_class = LocalRepo2dockerBuild
c.BinderHub.launch_quota_class = LaunchQuota  # 不使用K8s配额检查
c.BinderHub.push_secret = ""

# ---- UI自定义 ----
c.BinderHub.about_message = "本地开发环境 - 不使用Kubernetes"
c.BinderHub.banner_message = (
    '<div style="background:#d4edda;color:#155724;padding:8px;text-align:center;">'
    '🔧 本地开发模式 - 构建在本地Docker中执行</div>'
)

# ---- JupyterHub连接 ----
# 方式1：作为JupyterHub Service运行（推荐，见2.3节）
# 此时 c.BinderHub.hub_api_token 和 c.BinderHub.base_url 从环境变量获取

# 方式2：独立运行连接到远程JupyterHub
# c.BinderHub.hub_url = f"http://{hostip}:8000"
# c.BinderHub.hub_api_token = "dummy-binder-secret-token"
# c.BinderHub.base_url = "/"
```

### 2.2 本地 Docker 要求

```bash
# 确保Docker正在运行
docker info

# 确保repo2docker可用
jupyter-repo2docker --help

# 测试本地构建（不通过BinderHub）
jupyter-repo2docker --no-run --ref=HEAD \
  --image=test-build:latest \
  https://github.com/binder-examples/requirements
```

> **注意**：`LocalRepo2dockerBuild` 在构建时会直接调用 `jupyter-repo2docker` 命令，构建日志以 JSON 格式输出并通过 SSE 推送到前端。

### 2.3 本地 JupyterHub + BinderHub 完整环境

使用 DockerSpawner 在本地 Docker 中启动用户 Notebook 服务器，这是最接近生产环境的本地开发模式。

**目录结构：**

```
local-dev/
├── binderhub_config.py     # BinderHub配置
├── jupyterhub_config.py    # JupyterHub配置
└── requirements.txt        # 额外依赖
```

**requirements.txt：**

```
dockerspawner
jupyterhub
notebook
binderhub
```

**jupyterhub_config.py：**

```python
"""本地JupyterHub配置 - 使用DockerSpawner"""
import os
import socket

from dockerspawner import DockerSpawner
from binderhub.binderspawner_mixin import BinderSpawnerMixin


def random_port():
    """获取随机可用端口"""
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostip = s.getsockname()[0]
s.close()


# BinderSpawner：BinderSpawnerMixin + DockerSpawner
class LocalContainerSpawner(BinderSpawnerMixin, DockerSpawner):
    pass


c.JupyterHub.spawner_class = LocalContainerSpawner
c.DockerSpawner.remove = True               # 容器停止后自动删除
c.DockerSpawner.allowed_images = "*"        # 允许启动任意镜像
c.DockerSpawner.network_name = "bridge"     # 使用默认bridge网络
c.DockerSpawner.extra_host_config = {
    "network_mode": "host",  # 本地开发使用host网络简化连接
}

c.Application.log_level = "DEBUG"
c.Spawner.debug = True
c.JupyterHub.authenticator_class = "null"   # 匿名模式
c.LocalContainerSpawner.cmd = "jupyter-notebook"
c.LocalContainerSpawner.auth_enabled = False

c.JupyterHub.hub_ip = "0.0.0.0"
c.JupyterHub.hub_connect_ip = hostip

# 将BinderHub注册为JupyterHub Service
binderhub_config = os.path.join(os.path.dirname(__file__), "binderhub_config.py")
binderhub_port = random_port()

c.JupyterHub.services = [
    {
        "name": "binder",
        "admin": True,
        "command": [
            "python", "-m", "binderhub",
            f"--config={binderhub_config}",
            f"--port={binderhub_port}",
        ],
        "url": f"http://localhost:{binderhub_port}",
        "environment": {
            "JUPYTERHUB_EXTERNAL_URL": f"http://{hostip}:8000",
        },
    }
]
c.JupyterHub.default_url = f"/services/binder/"
```

**binderhub_config.py（对应上面的jupyterhub_config.py）：**

```python
import os
import socket
from binderhub.build_local import LocalRepo2dockerBuild
from binderhub.quota import LaunchQuota

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostip = s.getsockname()[0]
s.close()

c.BinderHub.debug = True
c.BinderHub.use_registry = False
c.BinderHub.builder_required = False
c.BinderHub.build_class = LocalRepo2dockerBuild
c.BinderHub.launch_quota_class = LaunchQuota
c.BinderHub.push_secret = ""

# 作为JupyterHub Service运行时，这些由JupyterHub自动注入
assert os.getenv("JUPYTERHUB_API_TOKEN"), "必须在JupyterHub Service中运行"
c.BinderHub.base_url = os.getenv("JUPYTERHUB_SERVICE_PREFIX", "/")
c.BinderHub.hub_url = os.getenv("JUPYTERHUB_EXTERNAL_URL") or f"http://{hostip}:8000"

c.BinderHub.about_message = "本地开发环境"
```

**启动本地环境：**

```bash
cd local-dev
pip install -r requirements.txt
jupyterhub -f jupyterhub_config.py
```

访问 `http://localhost:8000/services/binder/` 即可使用。

### 2.4 Docker Compose 开发环境

使用 `docker-compose.yml` 一键启动包含 BinderHub 和 JupyterHub 的完整本地环境：

```yaml
# docker-compose.yml - 本地开发环境
version: "3.8"

services:
  jupyterhub:
    build:
      context: .
      dockerfile: Dockerfile.jupyterhub
    ports:
      - "8000:8000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./binderhub_config.py:/etc/binderhub/binderhub_config.py
      - ./jupyterhub_config.py:/etc/jupyterhub/jupyterhub_config.py
      - ..:/src/binderhub  # 挂载源码用于热重载
    environment:
      - JUPYTERHUB_API_TOKEN=dummy-binder-secret-token
      - DOCKER_NETWORK_NAME=binderhub-dev
    networks:
      - binderhub-dev
    container_name: jupyterhub-dev

  binderhub:
    build:
      context: .
      dockerfile: Dockerfile.binderhub
    ports:
      - "8585:8585"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./binderhub_config.py:/etc/binderhub/binderhub_config.py
      - ..:/src/binderhub
    command: >
      python -m binderhub
      -f /etc/binderhub/binderhub_config.py
      --debug --port=8585
    environment:
      - JUPYTERHUB_API_TOKEN=dummy-binder-secret-token
      - JUPYTERHUB_SERVICE_PREFIX=/
    networks:
      - binderhub-dev
    depends_on:
      - jupyterhub
    container_name: binderhub-dev

networks:
  binderhub-dev:
    name: binderhub-dev
```

**Dockerfile.binderhub：**

```dockerfile
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git docker.io && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /src/binderhub
COPY . .
RUN pip install -e ".[dev]"

EXPOSE 8585
CMD ["python", "-m", "binderhub", "--debug", "--port=8585"]
```

```bash
# 启动开发环境
docker-compose up --build

# 查看日志
docker-compose logs -f binderhub
```

## 3. 连接远程 JupyterHub

本地运行 BinderHub 但连接到远程 Kubernetes 集群上的 JupyterHub（如 Minikube 或远程开发集群）。

### 3.1 连接 Minikube JupyterHub

```python
# binderhub_config.py - 连接Minikube上的JupyterHub
import os

c.BinderHub.debug = True
c.BinderHub.use_registry = False  # 或True，根据配置

# 端口转发：将Minikube中的JupyterHub proxy转发到本地
# kubectl port-forward svc/proxy-public -n jupyterhub 30902:80 &
c.BinderHub.hub_url = "http://localhost:30902"
c.BinderHub.hub_url_local = "http://localhost:30902"
c.BinderHub.hub_api_token = "dummy-binder-secret-token"

# 如果使用K8s构建（需要kubeconfig）
from binderhub.build import KubernetesBuildExecutor
c.BinderHub.build_class = KubernetesBuildExecutor
c.KubernetesBuildExecutor.namespace = "binder-builds"

# 如果使用本地构建
# from binderhub.build_local import LocalRepo2dockerBuild
# c.BinderHub.build_class = LocalRepo2dockerBuild

c.BinderHub.builder_required = True
c.BinderHub.port = 8585
c.BinderHub.base_url = "/"
```

```bash
# 设置端口转发
minikube start
kubectl proxy --port=8080 &

# 转发JupyterHub proxy
kubectl port-forward svc/proxy-public -n jupyterhub 30902:80 &

# 启动本地BinderHub
python -m binderhub -f binderhub_config.py
```

### 3.2 连接远程开发集群

```python
# binderhub_config.py - 连接远程开发集群
c.BinderHub.hub_url = "https://dev-binder.example.com/"
c.BinderHub.hub_url_local = "http://proxy-public.jupyterhub.svc.cluster.local"
c.BinderHub.hub_api_token = "your-api-token-from-k8s-secret"

# 使用远程K8s构建
c.KubernetesBuildExecutor.namespace = "binder-builds"
c.KubernetesBuildExecutor.build_image = "quay.io/jupyterhub/repo2docker:2024.07.0"
```

## 4. 连接远程 Docker Registry

本地开发时连接远程 Registry 进行构建镜像的推送和查询：

```python
# binderhub_config.py - 远程Registry配置
c.BinderHub.use_registry = True
c.BinderHub.image_prefix = "registry.example.com/dev-binder-"

# Docker Hub
c.DockerRegistry.url = "https://registry-1.docker.io"
c.DockerRegistry.username = "your-username"
c.DockerRegistry.password = "your-access-token"
c.DockerRegistry.not_found_401 = True

# 或使用 ~/.docker/config.json 中的凭证（不设置username/password时自动读取）
# c.DockerRegistry.docker_config_path = os.path.expanduser("~/.docker/config.json")
```

验证 Registry 连接：

```bash
# 手动测试Registry API
curl -s -H "Authorization: Bearer $(curl -s -u 'user:pass' \
  'https://auth.docker.io/token?service=registry.docker.io&scope=repository:user/binder-xxx:pull' \
  | jq -r .token)" \
  https://registry-1.docker.io/v2/user/binder-xxx/tags/list
```

## 5. Docker-in-Docker 本地开发

在本地模拟 Kubernetes DinD 模式，适合测试 Docker 层缓存和 sticky_builds 功能。

```bash
# 启动一个本地DinD容器
docker run --privileged --name dind-dev \
  -p 2375:2375 \
  -d docker:28.3.3-dind \
  dockerd --host=tcp://0.0.0.0:2375 --host=unix:///var/run/docker.sock

# 验证DinD可用
DOCKER_HOST=tcp://localhost:2375 docker info
```

```python
# binderhub_config.py - DinD本地开发配置
c.BinderHub.build_docker_host = "tcp://localhost:2375"
c.KubernetesBuildExecutor.docker_host = "tcp://localhost:2375"
c.KubernetesBuildExecutor.sticky_builds = True
```

## 6. Minikube 开发环境

使用 Minikube 搭建完整的 Kubernetes 开发环境。

### 6.1 启动 Minikube

```bash
# 启动Minikube（建议分配足够资源）
minikube start --cpus=4 --memory=8192 --disk-size=40g

# 启用Ingress
minikube addons enable ingress

# 配置kubectl
kubectl cluster-info

# 使用Minikube的Docker daemon（构建镜像直接在Minikube中可用）
eval $(minikube docker-env)
# Windows: minikube docker-env | Invoke-Expression
```

### 6.2 使用 Minikube Docker Daemon 构建

将本地 Docker 客户端指向 Minikube 内部的 Docker daemon，这样本地构建的镜像可以直接在 Minikube 中使用：

```bash
# 设置Docker环境变量
eval $(minikube docker-env)

# 在Minikube中构建BinderHub镜像（可选）
eval $(minikube docker-env)
docker build -t binderhub-dev:latest -f helm-chart/images/binderhub/Dockerfile .
```

### 6.3 Helm 部署开发版本

```bash
# 添加JupyterHub Helm仓库
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# 创建命名空间
kubectl create namespace jupyterhub
kubectl create namespace binderhub

# 安装JupyterHub
helm install jupyterhub jupyterhub/jupyterhub \
  --namespace jupyterhub \
  --version 3.3.7 \
  -f testing/local-binder-k8s-hub/jupyterhub-chart-config.yaml \
  --timeout=10m0s

# 安装BinderHub（开发配置）
helm install binderhub jupyterhub/binderhub \
  --namespace binderhub \
  --version <dev-version> \
  -f testing/k8s-binder-k8s-hub/binderhub-chart-config.yaml \
  --timeout=10m0s

# 端口转发访问
kubectl port-forward svc/binderhub -n binderhub 8585:8585 &
kubectl port-forward svc/proxy-public -n jupyterhub 30902:80 &
```

### 6.4 开发模式热重载

使用 Skaffold 或 Tilt 实现代码修改自动同步到 Pod：

```yaml
# tiltfile 示例（可选）
k8s_yaml(kustomize('k8s/'))
docker_build('binderhub-dev', '.', dockerfile='helm-chart/images/binderhub/Dockerfile')
```

## 7. 使用命令行触发构建测试

### 7.1 使用 Python API 脚本

参考项目中的 `examples/binder-api.py`：

```python
#!/usr/bin/env python3
"""命令行触发Binder构建"""
import argparse
import json
import sys
import webbrowser
import requests


def build_binder(repo, ref, binder_url="http://localhost:8585", build_only=False, provider="gh"):
    """触发Binder构建，逐事件打印SSE消息"""
    url = f"{binder_url}/build/{provider}/{repo}/{ref}"
    params = {"build_only": "true"} if build_only else {}

    print(f"构建: {repo}@{ref}")
    print(f"API端点: {url}")
    print("-" * 60)

    r = requests.get(
        url, stream=True, params=params,
        headers={"Accept": "text/event-stream"},
        timeout=None,
    )
    r.raise_for_status()

    for line in r.iter_lines():
        line = line.decode("utf8", "replace")
        if line.startswith("data:"):
            evt = json.loads(line.split(":", 1)[1])
            phase = evt.get("phase", "")
            msg = evt.get("message", "")
            if msg:
                print(f"[{phase}] {msg.rstrip()}")
            else:
                print(f"[{phase}]")

            if evt.get("phase") == "ready":
                if build_only:
                    print("构建完成（仅构建模式）")
                    break
                server_url = f"{evt['url']}?token={evt['token']}"
                print(f"\n✅ 就绪! URL: {server_url}")
                webbrowser.open(server_url)
                break

    else:
        sys.exit("❌ 构建失败或超时")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Binder API 构建测试")
    parser.add_argument("repo", help="仓库路径，如 binder-examples/requirements")
    parser.add_argument("--ref", default="HEAD", help="Git引用（分支/tag/commit）")
    parser.add_argument("--binder", default="http://localhost:8585", help="BinderHub URL")
    parser.add_argument("--provider", default="gh", help="Provider前缀")
    parser.add_argument("--build-only", action="store_true", help="仅构建不启动")
    args = parser.parse_args()

    build_binder(args.repo, args.ref, args.binder, args.build_only, args.provider)
```

```bash
# 测试GitHub仓库构建
python build_cli.py binder-examples/requirements --ref=HEAD

# 仅构建不启动
python build_cli.py binder-examples/requirements --build-only

# 指定Provider
python build_cli.py myorg/myrepo --provider=gitea --binder=http://localhost:8585
```

### 7.2 使用 curl 测试 SSE 流

```bash
# SSE事件流调试（最直接的调试方式）
curl -N \
  -H "Accept: text/event-stream" \
  "http://localhost:8585/build/gh/binder-examples/requirements/HEAD"
```

SSE 事件格式说明：

```
event: message
data: {"phase": "waiting", "message": "Waiting for build to start..."}

event: message
data: {"phase": "running", "message": "Running..."}

event: message
data: {"phase": "log", "message": "{\"phase\":\"building\",\"message\":\"Step 1/20 : FROM ...\"}"}

event: message
data: {"phase": "built", "imageName": "user/binder-xxx:sha256"}

event: message
data: {"phase": "ready", "url": "http://localhost:8000/user/jovyan/", "token": "secret-token", "image": "..."}

event: message
data: {"phase": "failed", "message": "Build failed: ..."}
```

**关键 phase 说明：**

| phase | 含义 |
|-------|------|
| `waiting` | 等待构建开始（排队中） |
| `running` | 构建Pod已启动 |
| `log` | 构建日志消息（JSON嵌套） |
| `built` | 镜像构建完成 |
| `launching` | 正在启动Jupyter服务器 |
| `ready` | 服务器就绪，包含url和token |
| `failed` | 构建或启动失败 |
| `unknown` | 未知状态 |

### 7.3 测试其他 API 端点

```bash
# 健康检查
curl http://localhost:8585/health | python -m json.tool

# 版本信息
curl http://localhost:8585/versions | python -m json.tool

# RepoProvider列表（验证自定义Provider注册）
curl http://localhost:8585/api/repoproviders | python -m json.tool

# Prometheus指标
curl http://localhost:8585/metrics | grep binderhub

# Badge SVG
curl http://localhost:8585/badge.svg
```

## 8. 日志与调试模式

### 8.1 启用 Debug 日志

```python
# binderhub_config.py - 详细日志配置
import logging

c.BinderHub.debug = True
c.Application.log_level = logging.DEBUG

# Tornado自动重载（代码修改后自动重启）
c.BinderHub.tornado_settings = {
    "autoreload": True,
}

# 启用pycurl（推荐高并发/调试场景）
# pip install pycurl
```

命令行启动 debug 模式：

```bash
# --debug 标志同时启用debug日志和Tornado autoreload
python -m binderhub -f binderhub_config.py --debug

# 或指定日志级别
python -m binderhub -f binderhub_config.py --log-level=DEBUG
```

### 8.2 构建日志调试

Kubernetes 模式下查看构建 Pod 日志：

```bash
# 查看运行中的构建Pod
kubectl get pods -n binder-builds -l component=binderhub-build

# 实时跟踪构建日志
kubectl logs -f -n binder-builds <build-pod-name>

# 查看Pod详情（调度失败、挂载错误等）
kubectl describe pod <build-pod-name> -n binder-builds

# 查看Pod事件
kubectl get events -n binder-builds --sort-by=.metadata.creationTimestamp
```

### 8.3 请求日志格式

BinderHub 使用自定义请求日志格式，输出到 stderr：

```
[I 260822 20:45:00 log:123] 200 GET /build/gh/binder-examples/requirements/HEAD (127.0.0.1) 12345.67ms
```

### 8.4 事件日志（EventLog）

启用结构化事件日志记录：

```python
# binderhub_config.py - 事件日志配置
c.EventLog.handlers = [
    # 输出到控制台
    {"cls": "logging.StreamHandler"},
]
```

事件遵循 JSON Schema（见 `binderhub/event-schemas/launch.json`），包含：
- `timestamp`: ISO 8601 时间戳
- `provider`: Provider ID
- `spec`: 仓库spec
- `ref`: 解析后的commit SHA
- `status`: success/failure
- `phase`: 事件阶段

## 9. 运行测试

### 9.1 测试目录结构

```
binderhub/
├── conftest.py              # 顶层pytest配置（--helm选项）
└── binderhub/tests/
    ├── conftest.py          # 测试fixtures
    ├── test_app.py          # 应用配置测试
    ├── test_auth.py         # 认证测试
    ├── test_build.py        # 构建流程测试
    ├── test_builder.py      # Builder测试
    ├── test_eventlog.py     # 事件日志测试
    ├── test_health.py       # 健康检查测试
    ├── test_launcher.py     # Launcher测试
    ├── test_main.py         # 主页面测试
    ├── test_quota.py        # 配额测试
    ├── test_ratelimit.py    # 限流测试
    ├── test_registry.py     # Registry测试
    ├── test_repoproviders.py # RepoProvider测试
    ├── test_utils.py        # 工具函数测试
    ├── test_version.py      # 版本端点测试
    ├── utils.py             # 测试工具函数
    └── http-record.*.json   # HTTP录制回放数据
├── js/
│   └── packages/
│       ├── binderhub-client/
│       │   └── tests/       # JS客户端测试
│       └── binderhub-react-components/
└── integration-tests/       # 集成测试（需要K8s集群）
    ├── conftest.py
    └── test_ui.py           # Playwright端到端测试
```

### 9.2 运行 Python 单元测试

```bash
# 运行所有测试
pytest binderhub/tests/

# 运行特定测试文件
pytest binderhub/tests/test_repoproviders.py -v

# 运行单个测试函数
pytest binderhub/tests/test_build.py::test_build -v

# 带覆盖率报告
pytest binderhub/tests/ --cov=binderhub --cov-report=term-missing

# 运行需要Helm/K8s的集成测试（需要集群）
pytest --helm binderhub/tests/ -v

# 不跳过慢速测试
pytest --run-slow binderhub/tests/

# 测试超时设置
pytest --timeout=30 binderhub/tests/
```

### 9.3 测试 HTTP 录制回放

部分测试使用录制的 HTTP 响应（`http-record.*.json` 文件），避免测试时频繁调用外部 API：

```bash
# 重新录制HTTP响应（需要网络）
pytest --record binderhub/tests/test_repoproviders.py -v
```

### 9.4 运行前端测试

```bash
# 安装前端依赖
npm install

# 运行JS单元测试（Jest）
npm test

# 运行ESLint检查
npm run lint

# 带覆盖率
npm test -- --coverage
```

### 9.5 端到端测试（Playwright）

```bash
# 安装Playwright浏览器
playwright install

# 运行E2E测试（需要运行中的BinderHub+JupyterHub）
pytest integration-tests/ -v
```

## 10. 前端开发

### 10.1 前端技术栈

| 组件 | 技术 |
|------|------|
| 框架 | React 19 |
| 路由 | Wouter |
| 终端 | xterm.js |
| 样式 | Bootstrap 5 + SCSS |
| 构建 | Webpack 5 + ts-loader |
| 测试 | Jest + Testing Library |

源码位于 `binderhub/static/js/`：

```
static/js/
├── index.jsx           # React入口
├── App.jsx             # 主应用组件
├── App.test.jsx        # 应用测试
├── index.scss          # 全局样式
├── pages/              # 页面组件
│   ├── HomePage.jsx    # 首页（仓库输入）
│   ├── LoadingPage.jsx # 加载/构建页
│   ├── AboutPage.jsx   # 关于页
│   └── NotFoundPage.jsx # 404页
└── index.d.ts          # TypeScript类型定义
```

### 10.2 开发模式构建

```bash
# 安装依赖
npm install

# 开发模式（监听文件变更自动重新构建）
npm run webpack:watch
```

构建产物输出到 `binderhub/static/dist/`：
- `bundle.js` - JavaScript bundle
- `styles.css` - 编译后的CSS
- `*.map` - Source maps（开发模式）

### 10.3 纯前端开发模式（Mocked Backend）

不需要实际构建基础设施，使用 FakeBuild/FakeRegistry/FakeProvider 进行纯 UI 开发：

```python
# binderhub_config.py - 纯前端Mock开发
from binderhub.build import FakeBuild
from binderhub.registry import FakeRegistry
from binderhub.repoproviders import FakeProvider

c.BinderHub.debug = True
c.BinderHub.use_registry = True
c.BinderHub.registry_class = FakeRegistry
c.BinderHub.builder_required = False
c.BinderHub.build_class = FakeBuild
c.BinderHub.repo_providers = {"fake": FakeProvider}

c.BinderHub.about_message = "前端开发模式 - Mock数据"
c.BinderHub.banner_message = "UI开发模式"
c.BinderHub.port = 8585
```

启动后访问 `http://localhost:8585`，输入 `fake/spec/HEAD` 即可看到模拟的构建流程。

### 10.4 API Only 模式

仅暴露 API 端点（无 UI），适用于前端独立开发：

```python
c.BinderHub.enable_api_only_mode = True
```

此模式下仅注册以下端点：
- `/metrics`
- `/versions`
- `/build/([^/]+)/(.+)`
- `/health`

### 10.5 自定义模板

```python
# 使用自定义Jinja2模板目录
c.BinderHub.template_path = "./custom-templates"

# 模板变量
c.BinderHub.template_variables = {
    "custom_var": "value",
}

# 额外静态文件
c.BinderHub.extra_static_path = "./custom-static"
c.BinderHub.extra_static_url_prefix = "/extra_static/"
```

## 11. 构建失败调试

### 11.1 常见构建失败原因及排查

| 症状 | 可能原因 | 排查命令 |
|------|----------|----------|
| 构建Pod一直Pending | 资源不足/节点选择器不匹配/secret不存在 | `kubectl describe pod <pod> -n binder-builds` |
| 构建失败无日志 | push_secret配置错误/Registry不可达 | 检查Pod环境变量和secret挂载 |
| repo2docker报错 | 仓库配置错误/requirements.txt语法错误/网络超时 | 查看构建Pod完整日志 |
| 镜像推送失败 | Registry凭证错误/网络策略阻止 | 手动在构建容器中 `docker push` 测试 |
| 构建超时 | 仓库过大/网络慢/依赖安装超时 | 增大 `KubernetesCleaner.max_age` |
| Git克隆失败 | 私有仓库凭证缺失/网络问题 | 检查 `git_credentials` 配置 |

### 11.2 手动执行 repo2docker 复现问题

```bash
# 在本地手动执行repo2docker复现构建问题
jupyter-repo2docker --no-run \
  --ref=HEAD \
  --image=test-debug:latest \
  --json-logs \
  --user-name=jovyan \
  --user-id=1000 \
  --verbose \
  https://github.com/binder-examples/requirements

# 交互式调试（进入容器）
jupyter-repo2docker --no-build --debug https://github.com/user/repo
```

### 11.3 进入构建 Pod 调试

```bash
# 找到构建Pod
kubectl get pods -n binder-builds

# 进入构建容器调试
kubectl exec -it -n binder-builds <build-pod-name> -- /bin/bash

# 在容器内手动尝试git clone
git clone https://github.com/user/repo /tmp/repo

# 手动尝试docker push
docker push your-registry/binder-test:latest
```

### 11.4 本地复现线上构建

```bash
# 获取线上构建的镜像名和参数
# 从SSE日志中获取 imageName

# 本地拉取并运行该镜像
docker run -it --rm -p 8888:8888 <image-name> jupyter notebook --ip=0.0.0.0
```

## 12. 开发工作流速查

### 12.1 快速启动命令汇总

```bash
# 1. 安装开发环境
git clone https://github.com/jupyterhub/binderhub.git && cd binderhub
pip install -e ".[dev]"
npm install

# 2. 前端监听构建
npm run webpack:watch &

# 3. 纯UI Mock开发
python -m binderhub -f testing/local-binder-mocked-hub/binderhub_config.py --debug --port=8585

# 4. 本地Docker构建 + Mock Hub
python -m binderhub -f testing/local-binder-local-hub/binderhub_config.py --debug

# 5. 本地连接Minikube JupyterHub
python -m binderhub -f testing/local-binder-k8s-hub/binderhub_config.py --debug

# 6. 运行测试
pytest binderhub/tests/ -v
npm test
```

### 12.2 开发模式配置文件对照

| 配置文件 | 构建方式 | Hub方式 | Registry | 用途 |
|----------|----------|---------|----------|------|
| `testing/local-binder-mocked-hub/` | FakeBuild | Mock | FakeRegistry | 纯UI开发 |
| `testing/local-binder-local-hub/` | LocalRepo2dockerBuild | 本地DockerSpawner | 无 | 本地完整功能 |
| `testing/local-binder-k8s-hub/` | KubernetesBuildExecutor | K8s JupyterHub | 可选 | K8s集成开发 |
| `testing/k8s-binder-k8s-hub/` | K8s (Helm部署) | K8s JupyterHub | 可选 | Helm Chart测试 |

### 12.3 环境变量参考

| 环境变量 | 说明 |
|----------|------|
| `JUPYTERHUB_API_TOKEN` | JupyterHub API Token（Service模式自动注入） |
| `JUPYTERHUB_SERVICE_PREFIX` | Service URL前缀（Service模式自动注入） |
| `JUPYTERHUB_EXTERNAL_URL` | JupyterHub外部访问URL |
| `BUILD_NAMESPACE` | 构建Pod命名空间（默认default） |
| `BINDERHUB_BUILD_TOKEN_SECRET` | Build Token签名密钥（hex编码） |
| `GITHUB_ACCESS_TOKEN` | GitHub API Token（增加速率限制） |
| `GITLAB_ACCESS_TOKEN` | GitLab API Token |
| `GITLAB_PRIVATE_TOKEN` | GitLab Private Token |
| `GITEA_ACCESS_TOKEN` | Gitea API Token（自定义Provider） |
| `DOCKER_CONFIG` | Docker配置目录（默认~/.docker） |
| `BINDERHUB_CONTAINER_REGISTRY_HELPER_AUTH_TOKEN` | ExternalRegistryHelper认证Token |
