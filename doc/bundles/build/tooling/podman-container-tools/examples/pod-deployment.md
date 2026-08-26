---
type: Example
title: Pod与Kubernetes YAML实战
description: 学习Podman Pod的创建与管理，生成和部署Kubernetes兼容YAML，实现nginx+redis多容器sidecar模式编排。
tags: [podman, pod, kubernetes, yaml, sidecar, kube-play]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## 创建Pod与运行容器

Pod是Podman的一等公民，Pod内的容器共享网络命名空间、IPC命名空间和UTS命名空间，可以通过localhost互相通信。

```bash
# 创建一个名为mypod的Pod，映射主机8080端口到Pod网络
podman pod create --name mypod -p 8080:80

# 在Pod中运行nginx容器（无需额外端口映射，使用Pod的网络）
podman run -d --pod mypod --name web nginx:alpine

# 查看Pod列表
podman pod ps

# 查看Pod内的容器
podman ps -a --pod
```

参数说明：
- `--pod mypod`：将容器加入指定Pod
- Pod创建时的端口映射对Pod内所有容器生效

此时访问 `http://localhost:8080` 即可看到nginx默认页面。

## 生成Kubernetes YAML

Podman可以将运行中的Pod导出为Kubernetes兼容的YAML清单：

```bash
# 生成Pod的Kubernetes YAML并保存到文件
podman kube generate mypod > pod.yaml

# 查看生成的YAML内容
cat pod.yaml
```

生成的YAML是标准的Kubernetes Pod清单，包含容器定义、端口映射、重启策略等字段。

## 使用kube play部署YAML

通过 `podman kube play` 可以直接基于YAML清单创建Pod和容器：

```bash
# 先停止并删除之前的Pod，避免冲突
podman pod stop mypod
podman pod rm mypod

# 从YAML文件创建Pod和容器
podman kube play pod.yaml

# 验证Pod已启动
podman pod ps
podman ps --pod
```

`podman kube play` 会解析YAML中的Pod定义，自动创建对应的Pod和容器，与Kubernetes行为一致。

## 多容器Pod示例：Nginx + Redis Sidecar

以下是一个完整的多容器Pod YAML示例，包含nginx主容器和redis sidecar容器：

```yaml
# nginx-redis-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: webapp-pod
  labels:
    app: webapp
spec:
  containers:
    - name: nginx
      image: nginx:alpine
      ports:
        - containerPort: 80
          hostPort: 8080
      resources:
        limits:
          memory: "128Mi"
          cpu: "500m"
    - name: redis
      image: redis:alpine
      resources:
        limits:
          memory: "64Mi"
          cpu: "250m"
  restartPolicy: Always
```

部署这个多容器Pod：

```bash
# 使用kube play部署多容器Pod
podman kube play nginx-redis-pod.yaml

# 验证两个容器都在运行
podman ps --pod

# 在nginx容器内通过localhost访问redis（共享网络命名空间）
podman exec -it webapp-pod-nginx sh
# 在容器内执行（alpine需先安装redis-tools）
apk add --no-cache redis
redis-cli -h localhost ping
# 应返回 PONG
```

在多容器Pod中，容器之间通过 `localhost` 直接通信，无需显式创建网络或服务发现。

## 管理Pod生命周期

```bash
# 停止Pod（停止Pod内所有容器）
podman pod stop webapp-pod

# 启动已停止的Pod
podman pod start webapp-pod

# 重启Pod
podman pod restart webapp-pod

# 查看Pod详细信息
podman pod inspect webapp-pod

# 查看Pod内进程
podman pod top webapp-pod
```

## 使用kube down清理资源

与 `kube play` 对应，`podman kube down` 可以清理YAML定义的所有资源：

```bash
# 停止并删除YAML中定义的Pod和容器
podman kube down nginx-redis-pod.yaml

# 也可以直接删除Pod（会自动删除Pod内所有容器）
podman pod rm -f webapp-pod

# 验证清理完成
podman pod ps
podman ps
```

`podman kube down` 会读取YAML并删除对应的Pod、容器和相关资源，是推荐的清理方式。

## 完整工作流速查

```bash
# 方式一：命令行创建Pod再导出YAML
podman pod create --name mypod -p 8080:80
podman run -d --pod mypod --name web nginx:alpine
podman kube generate mypod > pod.yaml

# 方式二：直接编写YAML再用kube play部署
cat > nginx-redis-pod.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: webapp-pod
spec:
  containers:
    - name: nginx
      image: nginx:alpine
      ports:
        - containerPort: 80
          hostPort: 8080
    - name: redis
      image: redis:alpine
  restartPolicy: Always
EOF

podman kube play nginx-redis-pod.yaml

# 验证部署
curl http://localhost:8080
podman pod ps

# 清理
podman kube down nginx-redis-pod.yaml
```

## 相关概念

- [Pod一等公民](/concepts/05-pod-first-class.md)
- [Kubernetes集成](/concepts/13-kubernetes-integration.md)
- [容器基础](/concepts/04-container-basics.md)
- [网络与数据卷](/concepts/09-network-volume.md)
