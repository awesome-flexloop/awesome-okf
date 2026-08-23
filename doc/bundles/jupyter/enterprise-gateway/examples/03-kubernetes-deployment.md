---
okf_version: "0.2"
type: "example"
title: "Kubernetes部署EG"
description: "在Kubernetes集群上部署Enterprise Gateway，使用KubernetesProcessProxy创建远程内核Pod，包含RBAC配置、Helm部署、kernelspec配置"
tags: [example, kubernetes, deployment, k8s, helm, rbac, pod]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: process-proxy
    resource: "/references/process-proxy-source.md"
    title: "ProcessProxy源码"
  - id: deployment
    resource: "/concepts/10-deployment-modes.md"
    title: "部署模式与Kernel Launcher"
  - id: security
    resource: "/concepts/11-security-and-ha.md"
    title: "安全认证与高可用"
---

# Kubernetes部署EG

本示例演示在 Kubernetes 集群上部署 Enterprise Gateway，使用 `KubernetesProcessProxy` 在集群中创建内核Pod。

## 前置条件

- 可用的 Kubernetes 集群（minikube、kind、EKS、GKE等）
- kubectl 已配置好集群访问权限
- Helm 3.x（推荐使用Helm Chart部署）
- 内核Docker镜像已构建或可访问

## 架构概览

```
┌─────────────────────────────────────────────────┐
│  Kubernetes Cluster                              │
│                                                   │
│  ┌─────────────┐    ┌──────────────────────────┐ │
│  │   Notebook  │    │  Enterprise Gateway       │ │
│  │   (JupyterLab│◄──►│  Service (ClusterIP)     │ │
│  │   /Lab)     │WS  │  Deployment (1+ replicas) │ │
│  └─────────────┘    └──────────┬───────────────┘ │
│                                 │ K8s API          │
│                                 ▼                  │
│  ┌─────────────────────────────────────────────┐  │
│  │  Kernel Pods (dynamically created)           │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐                 │  │
│  │  │Python│ │  R   │ │Scala │  (per user/nb)  │  │
│  │  │Kernel│ │Kernel│ │Kernel│                 │  │
│  │  └──────┘ └──────┘ └──────┘                 │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

EG Pod内运行Enterprise Gateway服务，收到创建内核请求时，通过Kubernetes API动态创建内核Pod。内核Pod运行launcher+ipykernel，启动后通过ResponseManager回传连接信息，EG通过端口转发或Pod网络直接连接ZMQ端口。

## 方式1：使用Helm部署（推荐）

### 步骤1：获取EG Helm Chart

```bash
# EG源码中包含Helm Chart
# 从源码目录
cd external/libs/jupyter/enterprise_gateway/etc/kubernetes/helm
```

Helm Chart目录结构 [F-170]：
```
enterprise-gateway/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── clusterrole.yaml
│   ├── clusterrolebinding.yaml
│   ├── serviceaccount.yaml
│   └── configmap.yaml
```

### 步骤2：配置values.yaml

关键配置项：

```yaml
# values.yaml
replicaCount: 1  # 多副本需配合replication HA模式

image:
  repository: elyra/enterprise-gateway
  tag: "3.4.0"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8888

ingress:
  enabled: true
  hosts:
    - host: eg.example.com
      paths: ["/"]

# EG特有配置
enterpriseGateway:
  # 内核镜像配置
  kernelImage: elyra/kernel-py:VERSION
  kernelRImage: elyra/kernel-r:VERSION
  kernelScalaImage: elyra/kernel-scala:VERSION
  
  # 网络配置
  portRange: "40000..50000"
  responsePort: 8877
  
  # 资源限制
  maxKernels: 100
  maxKernelsPerUser: 10
  
  # 认证（生产环境必须设置）
  authToken: "change-me-in-production"
  
  # CORS
  corsAllowOrigin: "https://notebook.example.com"
```

### 步骤3：安装RBAC资源

EG需要Kubernetes API权限来创建/管理Pod：

```bash
# 创建ServiceAccount和RBAC
kubectl create namespace enterprise-gateway

# ClusterRole权限：创建/删除/list/watch Pods
# templates/clusterrole.yaml 定义了所需权限
helm install enterprise-gateway ./enterprise-gateway \
  --namespace enterprise-gateway \
  -f values.yaml
```

RBAC关键权限（在clusterrole.yaml中定义）：
- pods: create, delete, get, list, watch
- pods/exec: create（端口转发和exec）
- pods/log: get（日志查看）
- events: list, watch

### 步骤4：验证部署

```bash
# 检查Pod状态
kubectl -n enterprise-gateway get pods

# 检查Service
kubectl -n enterprise-gateway get svc

# 端口转发测试
kubectl -n enterprise-gateway port-forward svc/enterprise-gateway 8888:8888

# 验证API
curl http://localhost:8888/api
```

## 方式2：手动部署

### 步骤1：创建Namespace和ServiceAccount

```yaml
# eg-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: enterprise-gateway
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: enterprise-gateway-sa
  namespace: enterprise-gateway
```

### 步骤2：创建ClusterRole和ClusterRoleBinding

```yaml
# eg-rbac.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: enterprise-gateway-kernel-manager
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["create", "delete", "get", "list", "watch"]
  - apiGroups: [""]
    resources: ["pods/exec", "pods/log"]
    verbs: ["create", "get"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: enterprise-gateway-kernel-manager
subjects:
  - kind: ServiceAccount
    name: enterprise-gateway-sa
    namespace: enterprise-gateway
roleRef:
  kind: ClusterRole
  name: enterprise-gateway-kernel-manager
  apiGroup: rbac.authorization.k8s.io
```

```bash
kubectl apply -f eg-namespace.yaml
kubectl apply -f eg-rbac.yaml
```

### 步骤3：创建ConfigMap（kernelspec配置）

```yaml
# eg-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: enterprise-gateway-config
  namespace: enterprise-gateway
data:
  # Python on Kubernetes kernelspec
  python_kubernetes_kernel.json: |
    {
      "argv": [
        "python",
        "/usr/local/share/jupyter/kernels/python_kubernetes/scripts/launch_kubernetes.py",
        "--kernel-id", "{kernel_id}",
        "--port-range", "{port_range}",
        "--response-address", "{response_address}",
        "--public-key", "{public_key}"
      ],
      "display_name": "Python on Kubernetes",
      "language": "python",
      "metadata": {
        "process_proxy": {
          "class_name": "enterprise_gateway.services.processproxies.k8s.KubernetesProcessProxy",
          "config": {
            "image_name": "elyra/kernel-py:3.4.0",
            "executor_image_name": "elyra/kernel-py:3.4.0"
          }
        }
      }
    }
```

### 步骤4：创建Deployment

```yaml
# eg-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: enterprise-gateway
  namespace: enterprise-gateway
  labels:
    app: enterprise-gateway
spec:
  replicas: 1
  selector:
    matchLabels:
      app: enterprise-gateway
  template:
    metadata:
      labels:
        app: enterprise-gateway
    spec:
      serviceAccountName: enterprise-gateway-sa
      containers:
        - name: enterprise-gateway
          image: elyra/enterprise-gateway:3.4.0
          ports:
            - containerPort: 8888
              name: http
            - containerPort: 8877
              name: response
          env:
            - name: EG_IP
              value: "0.0.0.0"
            - name: EG_PORT
              value: "8888"
            - name: EG_PORT_RANGE
              value: "40000..50000"
            - name: EG_RESPONSE_PORT
              value: "8877"
            - name: EG_MAX_KERNELS
              value: "100"
            - name: EG_MAX_KERNELS_PER_USER
              value: "10"
            - name: EG_LIST_KERNELS
              value: "false"
            - name: EG_AUTH_TOKEN
              valueFrom:
                secretKeyRef:
                  name: eg-secrets
                  key: auth-token
            - name: EG_ALLOW_ORIGIN
              value: "*"
            - name: KUBERNETES_SERVICE_HOST
              valueFrom:
                fieldRef:
                  fieldPath: status.hostIP
          readinessProbe:
            httpGet:
              path: /api
              port: 8888
            initialDelaySeconds: 10
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /api
              port: 8888
            initialDelaySeconds: 30
            periodSeconds: 15
```

### 步骤5：创建Service

```yaml
# eg-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: enterprise-gateway
  namespace: enterprise-gateway
spec:
  selector:
    app: enterprise-gateway
  ports:
    - name: http
      port: 8888
      targetPort: 8888
    - name: response
      port: 8877
      targetPort: 8877
  type: ClusterIP
```

### 步骤6：部署

```bash
# 创建Secret（存储认证Token）
kubectl -n enterprise-gateway create secret generic eg-secrets \
  --from-literal=auth-token=$(openssl rand -hex 32)

# 部署所有资源
kubectl apply -f eg-configmap.yaml
kubectl apply -f eg-deployment.yaml
kubectl apply -f eg-service.yaml
```

## 创建内核测试

部署成功后，创建一个Python内核：

```bash
# 端口转发
kubectl -n enterprise-gateway port-forward svc/enterprise-gateway 8888:8888

# 创建内核
TOKEN=$(kubectl -n enterprise-gateway get secret eg-secrets -o jsonpath='{.data.auth-token}' | base64 -d)

curl -X POST http://localhost:8888/api/kernels \
  -H "Content-Type: application/json" \
  -H "Authorization: token $TOKEN" \
  -d '{"name": "python_kubernetes", "env": {"KERNEL_USERNAME": "testuser"}}'
```

观察内核Pod创建：

```bash
# 应该看到一个新的kernel Pod
kubectl -n enterprise-gateway get pods

# 查看内核Pod日志
kubectl -n enterprise-gateway logs <kernel-pod-name>
```

## 内核Pod规格

KubernetesProcessProxy使用kernel-pod.yaml.j2模板创建内核Pod，默认包含：
- 镜像：kernelspec config中指定的image_name
- 环境变量：包含KERNEL_GATEWAY=1、加密密钥、端口范围等
- 资源限制：可通过config配置CPU/内存限制
- 网络：使用集群网络，内核ZMQ端口直接暴露在Pod IP上

## 生产环境配置建议

1. **启用TLS**：配置certfile/keyfile或使用Ingress TLS终结
2. **设置auth_token**：生产环境必须使用强Token
3. **配置CORS**：allow_origin设为Notebook服务器实际域名
4. **资源限制**：为内核Pod设置合理的CPU/内存requests和limits
5. **HA模式**：多副本部署时使用 `EG_AVAILABILITY_MODE=replication` + WebhookKernelSessionManager
6. **网络策略**：限制内核Pod间的网络访问
7. **内核镜像拉取**：使用私有镜像仓库时配置imagePullSecrets
8. **命名空间隔离**：考虑在独立namespace中创建内核Pod

## 清理

```bash
# Helm卸载
helm uninstall enterprise-gateway -n enterprise-gateway

# 或手动清理
kubectl delete namespace enterprise-gateway
```

## 常见问题

**Q: 创建内核时返回403 Forbidden？**
A: 检查RBAC配置是否正确，EG ServiceAccount是否有Pod创建权限。查看EG日志确认错误。

**Q: 内核Pod创建后一直starting？**
A: 检查EG日志和内核Pod日志。常见原因：内核镜像拉取失败、ResponseManager端口不可达、内核启动命令错误。

**Q: WebSocket连接到内核失败？**
A: 确认EG到内核Pod的网络可达。K8s模式下EG通常通过Pod IP直接连接ZMQ端口，检查网络策略和CNI配置。
