# 示例文档索引

本目录包含 BinderHub 项目的实操示例文档，覆盖配置、开发、部署和调试场景。

| 示例 | 内容 |
|------|------|
| [基本配置示例](01-basic-config.md) | BinderHub常用配置：端口、Registry连接、Hub连接、限流配额、Banner自定义 |
| [自定义RepoProvider开发](02-custom-provider.md) | 从零开发自定义RepoProvider的完整步骤和代码示例 |
| [Kubernetes部署示例](03-kubernetes-deploy.md) | Helm部署BinderHub+JupyterHub到Kubernetes集群的完整配置 |
| [本地开发调试](04-local-dev.md) | 本地运行BinderHub、连接远程JupyterHub、DinD构建配置、调试技巧 |

## 快速参考

### 常用启动命令

```bash
# pip安装并启动
pip install binderhub
python -m binderhub --generate-config
python -m binderhub -f binderhub_config.py --port=8585

# Helm部署
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm install jupyterhub jupyterhub/jupyterhub -f secrets.yaml --version=<version>
helm install binderhub jupyterhub/binderhub -f config.yaml --version=<version>

# Docker运行（开发测试）
docker run -p 8585:8585 -v /var/run/docker.sock:/var/run/docker.sock \
  quay.io/jupyterhub/k8s-binderhub:<tag>
```

### 关键配置速查

```python
# 最小匿名配置
c.BinderHub.hub_url = "http://jupyterhub/hub"
c.BinderHub.use_registry = True
c.BinderHub.image_prefix = "registry.example.com/binder-"
c.BinderHub.auth_enabled = False

# Docker Registry
c.DockerRegistry.url = "https://registry.example.com"
c.DockerRegistry.username = "admin"
c.DockerRegistry.password = "password"

# 构建资源
c.KubernetesBuildExecutor.memory_limit = "2G"
c.KubernetesBuildExecutor.cpu_limit = 2
c.KubernetesBuildExecutor.timeout = 1800

# 限流配额
c.RateLimiter.limit = 100
c.RateLimiter.period_seconds = 3600
c.KubernetesLaunchQuota.total_quota = 100
c.BinderHub.per_repo_quota = 5
```

### 排障命令

```bash
# 检查健康状态
curl http://<binderhub>/health
curl http://<binderhub>/versions
curl http://<binderhub>/metrics
curl http://<binderhub>/config/repoproviders

# Kubernetes排障
kubectl get pods -n <namespace> -l component=binderhub
kubectl logs -n <namespace> -l component=binderhub --tail=100
kubectl get pods -n <build-namespace> -l component=binderhub-build
kubectl logs -n <build-namespace> <build-pod-name>
kubectl describe pod <build-pod-name> -n <build-namespace>

# Helm管理
helm list -n <namespace>
helm history binderhub -n <namespace>
helm rollback binderhub <revision> -n <namespace>
```

```{toctree}
:maxdepth: 7

01-basic-config
02-custom-provider
03-kubernetes-deploy
04-local-dev
```
