---
type: Concept
title: 快速开始
description: BinderHub安装方式、pip安装、Helm部署、Docker本地运行和配置文件入门
tags:
  - jupyter
  - binderhub
  - getting-started
  - installation
  - helm
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T20:45:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/
---

# 快速开始

## 前置条件

BinderHub运行需要以下组件配合：

| 组件 | 用途 | 最低版本 |
|------|------|---------|
| Kubernetes | 容器编排，运行构建Pod和用户Pod | 1.19+ |
| JupyterHub | 用户会话管理（推荐Zero-to-JupyterHub部署） | 2.0+ |
| Docker Registry | 存储构建好的镜像（Docker Hub/GCR/私有Registry） | v2 |
| repo2docker | 构建引擎（BinderHub自动在Pod中调用） | 随BinderHub版本 |
| Python | 运行BinderHub服务 | 3.8+ |

## 方式一：Helm 部署（推荐生产使用）

这是最推荐的部署方式，BinderHub与JupyterHub一起通过Helm安装到Kubernetes集群。

### 1. 安装 Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 2. 添加 JupyterHub Helm 仓库

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
```

### 3. 创建配置文件

创建 `config.yaml`：

```yaml
# config.yaml
config:
  BinderHub:
    use_registry: true
    hub_url: "http://jupyterhub-hub"  # JupyterHub Hub服务URL
    image_prefix: "gcr.io/<project-id>/binder-"  # 镜像前缀

# JupyterHub配置（BinderHub自动管理）
jupyterhub:
  hub:
    config:
      JupyterHub:
        authenticator_class: "null"  # 匿名访问模式
```

### 4. 安装（先安装JupyterHub，再安装BinderHub）

```bash
# 安装 JupyterHub
helm install jupyterhub jupyterhub/jupyterhub \
  --namespace=binderhub --create-namespace \
  --version=<jupyterhub-version>

# 安装 BinderHub
helm install binderhub jupyterhub/binderhub \
  --namespace=binderhub \
  -f config.yaml \
  --version=<binderhub-version>
```

### 5. 验证

```bash
kubectl get pods -n binderhub
kubectl get service binderhub -n binderhub
```

## 方式二：pip 安装（开发/本地运行）

### 1. 安装 BinderHub

```bash
pip install binderhub
```

### 2. 生成配置文件

```bash
python -m binderhub --generate-config
# 生成 binderhub_config.py
```

### 3. 编辑配置文件

编辑 `binderhub_config.py`，至少配置：

```python
# binderhub_config.py
c.BinderHub.hub_url = "http://localhost:8000"  # JupyterHub URL
c.BinderHub.use_registry = False  # 本地开发可关闭Registry
# 或配置Docker Registry
# c.BinderHub.use_registry = True
# c.BinderHub.image_prefix = "my-registry/binder-"
# c.DockerRegistry.url = "https://registry.example.com"
# c.DockerRegistry.username = "username"
# c.DockerRegistry.password = "password"
```

### 4. 启动服务

```bash
python -m binderhub -f binderhub_config.py --port=8585
```

### 5. 访问服务

打开浏览器访问 `http://localhost:8585`，输入一个GitHub仓库URL即可开始构建。

## 方式三：Docker 本地运行（用于测试）

BinderHub提供Docker镜像用于快速测试，但需要Docker socket挂载和JupyterHub配合。

```bash
docker run -p 8585:8585 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  quay.io/jupyterhub/k8s-binderhub:<tag>
```

## 命令行参数

| 参数 | 配置路径 | 默认值 | 说明 |
|------|---------|--------|------|
| `--port` | `BinderHub.port` | 8585 | 监听端口 |
| `--config` / `-f` | `BinderHub.config_file` | binderhub_config.py | 配置文件路径 |
| `--log-level` | `Application.log_level` | INFO | 日志级别 |
| `--debug` | `BinderHub.debug` | False | 启用debug模式 |

```bash
# 示例
python -m binderhub -f my_config.py --port=8080 --debug
```

## 最小配置示例

### 匿名模式（无认证，类似mybinder.org）

```python
# binderhub_config.py - 最小匿名配置
c.BinderHub.hub_url = "http://jupyterhub:8000"
c.BinderHub.use_registry = True
c.BinderHub.base_url = "/"
c.BinderHub.image_prefix = "my-registry.example.com/binder-"
c.BinderHub.auth_enabled = False

# Registry配置
c.DockerRegistry.url = "https://my-registry.example.com"
c.DockerRegistry.username = "admin"
c.DockerRegistry.password = "password"

# Kubernetes构建配置
c.KubernetesBuildExecutor.memory_limit = "2G"
c.KubernetesBuildExecutor.cpu_limit = 2
c.KubernetesBuildExecutor.timeout = 1800  # 30分钟构建超时

# 限流（每小时每IP最多10次构建）
c.RateLimiter.limit = 10
c.RateLimiter.period_seconds = 3600
```

### 认证模式（用户需登录JupyterHub）

```python
# binderhub_config.py - 认证模式
c.BinderHub.auth_enabled = True
c.BinderHub.hub_url = "https://hub.example.com"
c.BinderHub.base_url = "/binder/"
c.HubOAuth.hub_api_token = "<api-token>"  # JupyterHub API token
c.HubOAuth.hub_host = "https://hub.example.com"
```

## 验证安装

安装完成后，通过以下端点验证：

```bash
# 健康检查
curl http://localhost:8585/health
# 预期: {"ok": true, "checks": [...]}

# 版本信息
curl http://localhost:8585/versions
# 预期: {"binderhub": "...", "builder": "..."}

# Prometheus指标
curl http://localhost:8585/metrics
# 预期: Prometheus格式指标数据

# RepoProvider列表
curl http://localhost:8585/config/repoproviders
# 预期: JSON数组，包含所有支持的Provider配置
```

## 常见问题

### Q: 构建一直卡在 "Waiting for build to start"
检查构建Namespace的Pod是否能被调度：
```bash
kubectl get pods -n <build-namespace>
kubectl describe pod <build-pod-name> -n <build-namespace>
```

### Q: 镜像push失败
检查Registry凭据和网络连通性：
```bash
# 测试Registry连接
curl -k https://<registry>/v2/_catalog
```

### Q: JupyterHub启动用户server失败
检查Hub API连通性和BinderSpawner配置：
```bash
kubectl logs -n <namespace> -l component=hub
```
