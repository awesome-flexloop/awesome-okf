---
type: Example
title: "Kubernetes部署示例"
description: "使用Helm在Kubernetes集群上完整部署BinderHub和JupyterHub的步骤指南，包含Docker Hub/Harbor/GCR配置、Ingress设置、GitHub OAuth认证、资源配置、健康检查、升级回滚"
tags: [binderhub, kubernetes, helm, deployment, jupyterhub, docker-registry, ingress, oauth]
generated:
  by: "reference_agent/trae-cn"
  at: "2026-08-22T20:45:00Z"
status: stable
stale_after: 2027-08-22
sources:
  - ../../../../../external/libs/jupyter/binderhub/binderhub/
---

# Kubernetes 部署示例

本文档提供在 Kubernetes 集群上使用 Helm 部署 BinderHub 的完整指南，从前置条件准备到生产环境配置，覆盖匿名部署和认证部署两种模式。

## 1. 前置条件

### 1.1 必需组件

| 组件 | 最低版本 | 说明 |
|------|----------|------|
| Kubernetes | 1.24+ | 支持 Helm 3 的集群（GKE、EKS、AKS、自建集群均可） |
| Helm | 3.0+ | Kubernetes 包管理器 |
| kubectl | 与集群版本匹配 | Kubernetes 命令行工具 |
| Docker Registry | Docker Registry v2 API | 存储构建的 Docker 镜像（Docker Hub、GCR、Harbor 等） |
| JupyterHub | 通过 Zero-to-JupyterHub Helm Chart 部署 | 用户会话管理 |

### 1.2 集群资源建议

| 规模 | 节点数 | 每节点资源 | 并发用户 |
|------|--------|-----------|----------|
| 小型测试 | 2 | 2 CPU / 4GB | 10-20 |
| 中型服务 | 3-5 | 4 CPU / 8GB | 50-100 |
| 大型生产 | 5+ | 8 CPU / 16GB+ | 200+ |

### 1.3 工具安装

```bash
# 安装 Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 安装 kubectl（Linux 示例）
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# 验证集群连接
kubectl cluster-info
kubectl get nodes
```

## 2. 第一步：安装 JupyterHub

BinderHub 依赖 JupyterHub 来管理用户 Notebook 服务器。必须先安装 JupyterHub。

### 2.1 添加 Helm 仓库

```bash
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update
```

### 2.2 创建 JupyterHub 配置文件

创建 `jupyterhub-config.yaml`：

```yaml
# jupyterhub-config.yaml - JupyterHub基础配置（供BinderHub使用）
proxy:
  chp:
    resources:
      requests:
        cpu: "0.2"
        memory: 512Mi
      limits:
        cpu: "1"
        memory: 1Gi
  service:
    type: ClusterIP  # 通过BinderHub Ingress统一暴露

hub:
  # BinderSpawnerMixin 配置将由 BinderHub Chart 自动注入
  # 这里只设置基础配置
  db:
    type: sqlite-pvc
    pvc:
      storage: 3Gi
  config:
    JupyterHub:
      admin_access: true
      authenticator_class: "null"  # 匿名模式，认证模式见第9节
    BinderSpawner:
      auth_enabled: false

singleuser:
  # Binder 会话不需要持久存储
  storage:
    type: none
  # 默认资源限制
  cpu:
    limit: 2
    guarantee: 0.1
  memory:
    limit: 2G
    guarantee: 256M
  # 启动 JupyterLab（如果可用）
  cmd:
    - python3
    - "-c"
    - |
      import os, sys
      try:
          import jupyterlab
          exe = "jupyter-lab"
      except Exception:
          exe = "jupyter-notebook"
      os.execvp(exe, sys.argv)
  defaultUrl: "/lab"

# 空闲用户自动清理
cull:
  enabled: true
  users: true
  timeout: 3600        # 1小时无活动则清理
  every: 600           # 每10分钟检查一次
  maxAge: 21600        # 最长运行6小时
```

### 2.3 安装 JupyterHub

```bash
# 创建命名空间
kubectl create namespace jupyterhub

# 安装 JupyterHub（版本号请查阅最新版本）
helm install jupyterhub jupyterhub/jupyterhub \
  --namespace jupyterhub \
  --version 3.3.7 \
  --values jupyterhub-config.yaml \
  --timeout=10m0s

# 等待所有 Pod 就绪
kubectl wait --for=condition=ready pod \
  --all -n jupyterhub \
  --timeout=10m0s

# 验证安装
kubectl get pods -n jupyterhub
```

预期输出：

```
NAME                              READY   STATUS    RESTARTS   AGE
hub-xxxxxxxxxx-xxxxx              1/1     Running   0          2m
proxy-xxxxxxxxxx-xxxxx            1/1     Running   0          2m
continuous-image-puller-xxxxx     1/1     Running   0          2m
user-scheduler-xxxxxxxxxx-xxxxx   1/1     Running   0          2m
```

## 3. 第二步：准备 BinderHub 配置

创建 BinderHub 的 `config.yaml`。以下是最小匿名部署配置。

### 3.1 基础 config.yaml 框架

```yaml
# config.yaml - BinderHub 基础配置结构

# ---- 镜像配置 ----
image:
  name: quay.io/jupyterhub/k8s-binderhub
  tag: ""  # 留空使用chart默认版本
  pullPolicy: IfNotPresent

# ---- 副本数 ----
replicas: 1

# ---- 资源配置 ----
resources:
  requests:
    cpu: "0.2"
    memory: 512Mi
  limits:
    cpu: "1"
    memory: 1Gi

# ---- Service ----
service:
  type: ClusterIP

# ---- Registry 凭证（用于创建 docker config.json Secret）----
registry:
  url:
  username:
  password:

# ---- BinderHub 核心配置 ----
config:
  BinderHub:
    use_registry: true
    hub_url:
    hub_url_local: http://proxy-public.jupyterhub.svc.cluster.local
    base_url: /
  KubernetesBuildExecutor: {}

# ---- JupyterHub 集成配置 ----
jupyterhub:
  # JupyterHub 的配置会被 BinderHub Chart 自动合并
  # 见第2步中 jupyterhub-config.yaml 的设置
```

## 4. Docker Hub Registry 配置

使用 Docker Hub 作为镜像仓库的配置：

```yaml
# config.yaml - Docker Hub 配置
registry:
  url: https://index.docker.io/v1/
  username: "your-dockerhub-username"
  password: "your-dockerhub-access-token"  # 建议使用Access Token而非密码

config:
  BinderHub:
    use_registry: true
    image_prefix: "your-dockerhub-username/binder-"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"
    # hub_url 在设置 Ingress 后更新为外部访问地址
    # hub_url: "https://binder.example.com/jupyterhub/"
```

> **安全提示**：Docker Hub Access Token 在 [Docker Hub Account Settings > Security](https://hub.docker.com/settings/security) 生成，权限选择 `Read & Write`。不要使用账户密码。

## 5. 私有 Registry 配置（Harbor 示例）

使用自建 Harbor 作为镜像仓库：

```yaml
# config.yaml - Harbor 私有Registry配置
registry:
  url: https://harbor.example.com
  username: "admin"
  password: "Harbor12345"

config:
  BinderHub:
    use_registry: true
    image_prefix: "harbor.example.com/binder/binder-"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"

  DockerRegistry:
    not_found_401: false
    token_url: ""  # Harbor使用Basic Auth，留空即可
```

如果 Harbor 使用自签名证书，需要在构建 Pod 中配置 CA 证书：

```yaml
# 添加额外Volume挂载自定义CA
extraVolumes:
  - name: harbor-ca
    secret:
      secretName: harbor-ca-cert

extraVolumeMounts:
  - name: harbor-ca
    mountPath: /etc/ssl/certs/harbor-ca.crt
    subPath: ca.crt

extraConfig:
  10-harbor-ca: |
    import os
    os.environ["REQUESTS_CA_BUNDLE"] = "/etc/ssl/certs/ca-certificates.crt"
```

## 6. Google GCR/GAR 配置

### 6.1 Google Container Registry (GCR)

```yaml
# config.yaml - Google GCR配置
config:
  BinderHub:
    use_registry: true
    image_prefix: "gcr.io/your-gcp-project/binder-"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"

  # GCR 使用 Workload Identity 或节点服务账号认证
  # 不需要在registry段设置username/password
  # 确保GKE节点/服务账号具有Storage Admin权限
  DockerRegistry:
    url: "https://gcr.io"
    token_url: "https://gcr.io/v2/token?service=gcr.io"
```

### 6.2 Google Artifact Registry (GAR)

```yaml
# config.yaml - Google Artifact Registry配置
config:
  BinderHub:
    use_registry: true
    image_prefix: "us-central1-docker.pkg.dev/your-gcp-project/binder-images/binder-"
    registry_class: "binderhub.registry.GoogleArtifactRegistry"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"

  GoogleArtifactRegistry:
    url: "https://us-central1-docker.pkg.dev"
```

GKE Workload Identity 设置：

```bash
# 创建GCP服务账号
gcloud iam service-accounts create binderhub-sa \
  --project=your-gcp-project

# 绑定Artifact Registry权限
gcloud projects add-iam-policy-binding your-gcp-project \
  --member="serviceAccount:binderhub-sa@your-gcp-project.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# 绑定Kubernetes服务账号
gcloud iam service-accounts add-iam-policy-binding \
  binderhub-sa@your-gcp-project.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:your-gcp-project.svc.id.goog[binderhub/binderhub]"
```

## 7. 安装 BinderHub

### 7.1 使用 Helm 安装

```bash
# 创建 BinderHub 命名空间
kubectl create namespace binderhub

# 添加 JupyterHub Helm 仓库（如未添加）
helm repo add jupyterhub https://jupyterhub.github.io/helm-chart/
helm repo update

# 安装 BinderHub（版本号请查阅最新版本）
helm install binderhub jupyterhub/binderhub \
  --namespace binderhub \
  --version 1.0.0-0.dev.git.0000.h0000000 \
  --values config.yaml \
  --timeout=10m0s
```

> **注意**：请将 `--version` 替换为实际最新版本号。可通过 `helm search repo jupyterhub/binderhub --versions` 查看可用版本。

### 7.2 等待部署就绪

```bash
# 查看 Pod 状态
kubectl get pods -n binderhub

# 等待就绪
kubectl wait --for=condition=ready pod \
  -l app=binderhub -n binderhub \
  --timeout=10m0s

# 查看 Service
kubectl get svc -n binderhub
```

### 7.3 初始化时设置 hub_url

安装完成后，BinderHub 需要知道 JupyterHub 的外部访问地址。如果使用 LoadBalancer 或 NodePort 测试：

```bash
# 临时使用端口转发测试
kubectl port-forward svc/proxy-public -n jupyterhub 8000:80 &
kubectl port-forward svc/binderhub -n binderhub 8585:8585 &
```

## 8. 配置 Ingress

### 8.1 Ingress Nginx 配置示例

首先确保集群中已安装 Ingress Controller（如 nginx-ingress）：

```yaml
# config.yaml - Ingress配置
ingress:
  enabled: true
  hosts:
    - binder.example.com
  ingressClassName: nginx
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-body-size: "64m"
    nginx.ingress.kubernetes.io/websocket-services: "proxy-public"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  tls:
    - secretName: binder-tls
      hosts:
        - binder.example.com

config:
  BinderHub:
    hub_url: "https://binder.example.com/"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"
    base_url: /
```

### 8.2 JupyterHub Ingress 配置

BinderHub 和 JupyterHub 通常通过同一个 Ingress 暴露。在 BinderHub 的 `config.yaml` 中配置 JupyterHub 的 Ingress：

```yaml
# config.yaml - 包含JupyterHub Ingress
jupyterhub:
  proxy:
    service:
      type: ClusterIP
  ingress:
    enabled: true
    hosts:
      - binder.example.com
    ingressClassName: nginx
    annotations:
      nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
      nginx.ingress.kubernetes.io/websocket-services: "proxy-public"
      cert-manager.io/cluster-issuer: "letsencrypt-prod"
    tls:
      - secretName: binder-tls
        hosts:
          - binder.example.com
```

### 8.3 HTTPRoute（Gateway API）配置

如果集群支持 Gateway API（如使用 GKE Gateway、Envoy Gateway）：

```yaml
# config.yaml - Gateway API HTTPRoute
httpRoute:
  enabled: true
  hostnames:
    - binder.example.com
  parentRefs:
    - name: gw
      namespace: ingress-gateway
      sectionName: https
  filters:
    - type: ResponseHeaderModifier
      responseHeaderModifier:
        add:
          - name: Access-Control-Allow-Origin
            value: "*"
```

## 9. 认证模式部署（GitHub OAuth）

启用认证后，用户需要登录 GitHub 才能启动 Binder 会话。

### 9.1 创建 GitHub OAuth App

1. 访问 [GitHub Developer Settings > OAuth Apps](https://github.com/settings/developers)
2. 点击 "New OAuth App"
3. 填写：
   - **Application name**: My BinderHub
   - **Homepage URL**: `https://binder.example.com`
   - **Authorization callback URL**: `https://binder.example.com/hub/oauth_callback`
4. 记录 `Client ID` 和 `Client Secret`

### 9.2 认证模式 config.yaml

```yaml
# config.yaml - 认证模式（GitHub OAuth）
registry:
  url: https://index.docker.io/v1/
  username: "your-dockerhub-username"
  password: "your-dockerhub-access-token"

config:
  BinderHub:
    use_registry: true
    image_prefix: "your-dockerhub-username/binder-"
    hub_url: "https://binder.example.com/"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"
    auth_enabled: true
    base_url: /

jupyterhub:
  hub:
    config:
      JupyterHub:
        authenticator_class: github
      GitHubOAuthenticator:
        client_id: "your-github-client-id"
        client_secret: "your-github-client-secret"
        oauth_callback_url: "https://binder.example.com/hub/oauth_callback"
        allowed_organizations:
          - "your-github-org"  # 限制特定组织成员
      BinderSpawner:
        auth_enabled: true
    services:
      binder:
        oauth_client_id: "binder-oauth-client-id"
        oauth_client_secret: "binder-oauth-client-secret"
        oauth_redirect_uri: "https://binder.example.com/oauth_callback"
```

> **安全提示**：敏感信息（client_secret、password）建议使用 Kubernetes Secret + Helm `--set` 或 Sealed Secrets/External Secrets 管理，不要明文提交到版本控制。

### 9.3 使用 Secret 管理敏感信息

```bash
# 创建 Secret 存储敏感配置
kubectl create secret generic binderhub-secrets -n binderhub \
  --from-literal=registry-password='your-dockerhub-token' \
  --from-literal=github-client-secret='your-github-secret' \
  --from-literal=binder-oauth-secret='random-secret-string'
```

然后在 `config.yaml` 中使用环境变量引用：

```yaml
extraEnv:
  DOCKER_REGISTRY_PASSWORD:
    valueFrom:
      secretKeyRef:
        name: binderhub-secrets
        key: registry-password
```

## 10. 构建资源配置

### 10.1 构建 Pod 资源限制

```yaml
# config.yaml - 构建资源配置
config:
  KubernetesBuildExecutor:
    namespace: binder-builds  # 建议使用独立命名空间
    resources:
      requests:
        memory: "2G"
        cpu: "1"
      limits:
        memory: "4G"
        cpu: "2"
    node_selector:
      node-role.kubernetes.io/builder: "true"
    build_image: "quay.io/jupyterhub/repo2docker:2024.07.0"
    push_secret: binder-build-docker-config
    sticky_builds: false
    log_tail_lines: 100
    extra_envs:
      DOCKER_BUILDKIT: "1"
```

### 10.2 创建构建命名空间和 RBAC

```bash
# 创建构建命名空间
kubectl create namespace binder-builds

# BinderHub需要在binder-builds命名空间创建Pod的权限
# Helm Chart会自动创建必要的RBAC，但需要指定构建命名空间
```

```yaml
# config.yaml - 构建命名空间配置
config:
  KubernetesBuildExecutor:
    namespace: binder-builds

# RBAC配置（Helm Chart自动处理，通常不需要手动设置）
rbac:
  enabled: true
```

### 10.3 Docker-in-Docker (DinD) 模式

DinD 模式在每个节点上运行一个 Docker-in-Docker DaemonSet，构建 Pod 连接到节点上的 DinD socket，可利用 Docker 层缓存加速重复构建。

```yaml
# config.yaml - Docker-in-Docker配置
imageBuilderType: dind  # 可选: host (默认), dind, pink (Podman)

dind:
  daemonset:
    image:
      name: docker.io/library/docker
      tag: "28.3.3-dind"
      pullPolicy: IfNotPresent
    extraArgs:
      - "--registry-mirror=https://mirror.gcr.io"
  storageDriver: overlay2
  resources:
    requests:
      cpu: "0.5"
      memory: "512Mi"
    limits:
      cpu: "2"
      memory: "4G"
  hostSocketDir: /var/run/dind
  hostLibDir: /var/lib/dind

config:
  KubernetesBuildExecutor:
    docker_host: "unix:///var/run/dind/docker.sock"
    sticky_builds: true  # DinD模式下建议开启，利用层缓存
```

### 10.4 Podman-in-Kubernetes (Pink) 模式

使用 Podman 替代 Docker 进行构建：

```yaml
# config.yaml - Podman配置
imageBuilderType: pink

pink:
  daemonset:
    image:
      name: quay.io/podman/stable
      tag: "v5.8.2"
  resources: {}
  hostSocketDir: /var/run/pink
  hostSocketName: podman.sock
```

### 10.5 BinderHub 自身资源

```yaml
# config.yaml - BinderHub Pod资源
resources:
  requests:
    cpu: "0.2"
    memory: 512Mi
  limits:
    cpu: "1"
    memory: 1Gi

replicas: 2  # 生产环境建议多副本
pdb:
  enabled: true
  maxUnavailable: 1
```

## 11. 镜像清理配置

构建镜像会占用节点磁盘空间，Image Cleaner 自动清理旧镜像：

```yaml
# config.yaml - 镜像清理
imageCleaner:
  enabled: true
  image:
    name: quay.io/jupyterhub/docker-image-cleaner
    tag: "1.0.0-beta.3"
    pullPolicy: IfNotPresent
  cordon: true                    # 清理时cordon节点
  delay: 5                        # 每5秒最多删除一个镜像
  imageGCThresholdType: "relative"
  imageGCThresholdHigh: 80        # 磁盘使用率达80%时开始清理
  imageGCThresholdLow: 60         # 清理到60%停止
  host:
    dockerSocketDir: /var/run
    dockerSocketName: docker.sock
    dockerLibDir: /var/lib/docker
```

## 12. 验证部署

### 12.1 基础健康检查

```bash
# 端口转发到本地测试
kubectl port-forward svc/binderhub -n binderhub 8585:8585 &

# 健康检查
curl http://localhost:8585/health
# 预期: {"ok": true} 或包含各组件健康状态

# 版本信息
curl http://localhost:8585/versions
# 预期: {"binderhub": "...", "builder_info": {...}}

# 已注册的RepoProvider
curl http://localhost:8585/api/repoproviders

# Prometheus指标
curl http://localhost:8585/metrics
```

### 12.2 触发测试构建

```bash
# 方法1: 使用curl测试SSE构建流
curl -N -H "Accept: text/event-stream" \
  "http://localhost:8585/build/gh/binder-examples/requirements/HEAD"

# 方法2: 浏览器访问
# 打开 http://localhost:8585 在输入框中输入:
# https://github.com/binder-examples/requirements
# 点击 "launch" 开始构建
```

SSE 事件流预期输出：

```
data: {"phase": "waiting", "message": "Waiting for build to start..."}

data: {"phase": "running", "message": "Running..."}

data: {"phase": "log", "message": "{\"phase\": \"pulling\", \"message\": \"Pulling image...\"}"}
...
data: {"phase": "built", "imageName": "your-user/binder-xxx:sha"}

data: {"phase": "ready", "url": "http://...", "token": "..."}
```

### 12.3 检查构建 Pod

```bash
# 查看运行中的构建Pod
kubectl get pods -n binder-builds

# 查看构建日志
kubectl logs -n binder-builds <build-pod-name>

# 查看Pod详情（排查调度/资源问题）
kubectl describe pod <build-pod-name> -n binder-builds
```

## 13. 升级和回滚

### 13.1 升级部署

```bash
# 更新Helm仓库
helm repo update

# 查看可用版本
helm search repo jupyterhub/binderhub --versions

# 升级配置
helm upgrade binderhub jupyterhub/binderhub \
  --namespace binderhub \
  --version <new-version> \
  --values config.yaml \
  --timeout=10m0s

# 查看升级状态
helm status binderhub -n binderhub
helm history binderhub -n binderhub
```

### 13.2 回滚

```bash
# 查看部署历史
helm history binderhub -n binderhub

# 回滚到上一个版本
helm rollback binderhub -n binderhub

# 回滚到指定版本
helm rollback binderhub <revision-number> -n binderhub
```

### 13.3 删除部署

```bash
# 删除BinderHub（不删除JupyterHub）
helm uninstall binderhub -n binderhub

# 删除命名空间
kubectl delete namespace binderhub
kubectl delete namespace binder-builds
```

## 14. 完整匿名部署 config.yaml 示例

以下是一个整合所有配置的完整匿名部署 `config.yaml`：

```yaml
# config.yaml - 完整匿名部署示例
replicas: 2

resources:
  requests:
    cpu: "0.2"
    memory: 512Mi
  limits:
    cpu: "1"
    memory: 1Gi

pdb:
  enabled: true
  maxUnavailable: 1

image:
  name: quay.io/jupyterhub/k8s-binderhub
  tag: ""
  pullPolicy: IfNotPresent

imageBuilderType: dind

dind:
  daemonset:
    image:
      name: docker.io/library/docker
      tag: "28.3.3-dind"
      pullPolicy: IfNotPresent
  storageDriver: overlay2
  resources:
    requests:
      cpu: "0.5"
      memory: "512Mi"
    limits:
      cpu: "2"
      memory: "4G"
  hostSocketDir: /var/run/dind
  hostLibDir: /var/lib/dind

imageCleaner:
  enabled: true
  cordon: true
  delay: 5
  imageGCThresholdHigh: 80
  imageGCThresholdLow: 60
  host:
    dockerSocketDir: /var/run/dind
    dockerSocketName: docker.sock
    dockerLibDir: /var/lib/dind

registry:
  url: https://index.docker.io/v1/
  username: "your-username"
  password: "your-access-token"

service:
  type: ClusterIP
  annotations:
    prometheus.io/scrape: "true"

ingress:
  enabled: true
  hosts:
    - binder.example.com
  ingressClassName: nginx
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
    nginx.ingress.kubernetes.io/websocket-services: "proxy-public"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  tls:
    - secretName: binder-tls
      hosts:
        - binder.example.com

config:
  BinderHub:
    use_registry: true
    image_prefix: "your-username/binder-"
    hub_url: "https://binder.example.com/"
    hub_url_local: "http://proxy-public.jupyterhub.svc.cluster.local"
    auth_enabled: false
    base_url: /
    banner_message: ""
    about_message: "<p>Welcome to our BinderHub instance.</p>"
    cors_allow_origin: ""
    per_repo_quota: 5
    concurrent_build_limit: 32
    build_token_expires_seconds: 300

  KubernetesBuildExecutor:
    namespace: binder-builds
    resources:
      requests:
        memory: "2G"
        cpu: "1"
      limits:
        memory: "4G"
        cpu: "2"
    build_image: "quay.io/jupyterhub/repo2docker:2024.07.0"
    push_secret: binder-build-docker-config
    sticky_builds: true
    docker_host: "unix:///var/run/dind/docker.sock"
    log_tail_lines: 100
    extra_envs:
      DOCKER_BUILDKIT: "1"

  KubernetesLaunchQuota:
    total_quota: 100
    namespace: jupyterhub

  RateLimiter:
    limit: 100
    period_seconds: 3600

  BuildExecutor:
    appendix: |
      USER root
      RUN pip install --no-cache-dir nbgitpuller
      USER $NB_UID

jupyterhub:
  cull:
    enabled: true
    users: true
    timeout: 3600
    every: 600
    maxAge: 21600
  hub:
    config:
      JupyterHub:
        authenticator_class: "null"
      BinderSpawner:
        auth_enabled: false
    db:
      type: sqlite-pvc
      pvc:
        storage: 3Gi
    loadRoles:
      binder:
        services:
          - binder
        scopes:
          - servers
          - admin:users
  singleuser:
    storage:
      type: none
    cpu:
      limit: 2
      guarantee: 0.1
    memory:
      limit: 2G
      guarantee: 256M
    cmd:
      - python3
      - "-c"
      - |
        import os, sys
        try:
            import jupyterlab
            exe = "jupyter-lab"
        except Exception:
            exe = "jupyter-notebook"
        os.execvp(exe, sys.argv)
    defaultUrl: "/lab"
  proxy:
    service:
      type: ClusterIP
    chp:
      resources:
        requests:
          cpu: "0.2"
          memory: 512Mi
        limits:
          cpu: "1"
          memory: 1Gi
```

## 15. Helm Values 常用配置参考表

| 配置路径 | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `replicas` | int | `1` | BinderHub Pod 副本数 |
| `resources.requests.cpu` | string | `"0.2"` | CPU 请求 |
| `resources.requests.memory` | string | `"512Mi"` | 内存请求 |
| `image.name` | string | `quay.io/jupyterhub/k8s-binderhub` | BinderHub 镜像 |
| `image.tag` | string | Chart 设置 | 镜像标签 |
| `image.pullSecrets` | list | `[]` | 镜像拉取 Secret |
| `service.type` | string | `LoadBalancer` | Service 类型 |
| `registry.url` | string | `nil` | Registry URL（用于创建 docker config.json） |
| `registry.username` | string | `nil` | Registry 用户名 |
| `registry.password` | string | `nil` | Registry 密码/Token |
| `config.BinderHub.hub_url` | string | `nil` | JupyterHub 外部 URL（必填） |
| `config.BinderHub.hub_url_local` | string | `nil` | JupyterHub 集群内 URL |
| `config.BinderHub.image_prefix` | string | `""` | 构建镜像名称前缀（必填） |
| `config.BinderHub.auth_enabled` | bool | `false` | 是否启用认证 |
| `config.BinderHub.base_url` | string | `/` | 应用基础路径 |
| `config.KubernetesBuildExecutor.namespace` | string | `default` | 构建 Pod 命名空间 |
| `config.KubernetesBuildExecutor.build_image` | string | repo2docker 镜像 | 构建镜像 |
| `config.KubernetesBuildExecutor.resources` | dict | `{}` | 构建 Pod 资源 |
| `imageBuilderType` | string | `"host"` | 构建方式：host/dind/pink |
| `ingress.enabled` | bool | `false` | 是否启用 Ingress |
| `ingress.hosts` | list | `[]` | Ingress 主机名 |
| `ingress.tls` | list | `[]` | TLS 配置 |
| `rbac.enabled` | bool | `true` | 是否创建 RBAC 资源 |
| `imageCleaner.enabled` | bool | `true` | 是否启用镜像清理 |
| `extraConfig` | dict | `{}` | 额外 Python 配置片段 |
| `extraFiles` | dict | `{}` | 额外挂载文件 |
| `extraEnv` | dict | `{}` | 额外环境变量 |
| `extraVolumes` | list | `[]` | 额外 Volume |
| `extraVolumeMounts` | list | `[]` | 额外 VolumeMount |
| `nodeSelector` | dict | `{}` | BinderHub Pod 节点选择器 |
| `tolerations` | list | `[]` | BinderHub Pod 容忍度 |
| `jupyterhub.*` | dict | - | 传递给 JupyterHub Chart 的配置 |

## 16. 常见部署问题排查

### 16.1 BinderHub Pod 无法启动

```bash
# 查看Pod事件
kubectl describe pod -l app=binderhub -n binderhub

# 查看日志
kubectl logs -l app=binderhub -n binderhub --tail=100
```

常见原因：
- `hub_url` 未配置或 JupyterHub 不可达
- Registry 凭证错误
- RBAC 权限不足

### 16.2 构建 Pod 一直 Pending

```bash
kubectl describe pod <build-pod-name> -n binder-builds
# 查看 Events 部分
```

常见原因：
- 节点资源不足（检查 `resources` 配置）
- `node_selector` 未匹配到节点
- Docker socket 挂载失败
- push_secret 不存在

### 16.3 构建成功但启动失败

```bash
# 查看JupyterHub Hub日志
kubectl logs -l component=hub -n jupyterhub --tail=100

# 检查BinderHub是否能访问JupyterHub API
kubectl exec -it <binderhub-pod> -n binderhub -- \
  curl -H "Authorization: token <api-token>" \
  http://proxy-public.jupyterhub.svc.cluster.local/hub/api/
```

常见原因：
- `hub_api_token` 不匹配
- JupyterHub 中未注册 binder service
- CORS 配置不正确

### 16.4 SSE 连接中断

Ingress 代理超时过短，需调整：

```yaml
ingress:
  annotations:
    nginx.ingress.kubernetes.io/proxy-read-timeout: "600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "600"
```
