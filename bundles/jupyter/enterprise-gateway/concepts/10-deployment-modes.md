---
okf_version: "0.2"
type: "concept"
title: "部署模式与Kernel Launcher"
description: "Python/R/Scala Kernel Launcher职责与实现、Docker/Kubernetes/YARN部署模式详解、内核规范配置"
tags: [deployment, launcher, docker, kubernetes, yarn, kernelspec, kernel-launcher]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: process-proxy
    resource: "/references/process-proxy-source.md"
    title: "ProcessProxy源码"
---

# 部署模式与Kernel Launcher

Enterprise Gateway支持多种部署模式，每种模式由对应的ProcessProxy和Kernel Launcher协作完成。Kernel Launcher是运行在远端（或容器内）的启动脚本，负责实际启动内核进程并回传连接信息。

## Kernel Launcher 的职责

无论哪种部署模式，Launcher都承担以下核心职责 [F-167]：

1. **启动内核进程**：在远端/容器内启动ipykernel/IRkernel/Apache Toree
2. **端口分配**：在指定port-range内选择5个可用ZMQ端口
3. **连接信息回传**：使用RSA+AES加密将连接信息发送回EG的ResponseManager
4. **生命周期管理**：监控内核进程状态，处理EG的中断通知
5. **监听循环**：启动后进入等待循环，接收EG_COMM通道的控制消息

### Launcher与EG的通信协议

所有Launcher都遵循统一的通信协议：
- **命令行参数**：`--response-address`, `--public-key`, `--port-range`, `--kernel-id`, `--spark-context-init-mode`（Spark相关）
- **回传端口**：通过TCP连接response-address发送加密payload
- **回传格式**：v1格式的RSA+AES加密JSON（参见 [加密通信机制](06-response-manager.md)）

## Python Launcher (launch_ipykernel.py) [F-166]

位置：`etc/kernel-launchers/python/scripts/launch_ipykernel.py`

启动Python内核（ipykernel）的Launcher，是最常用的Launcher。

### 工作流程

```
1. 解析命令行参数
2. 等待spark context初始化（如果是Spark内核）
3. 在port-range内找到5个可用端口
4. 准备connection_info字典（含kernel_id）
5. 调用ipykernel启动函数，绑定端口
6. 加密connection_info并回传EG
7. 进入监听循环等待中断信号
```

Python Launcher支持在本地、YARN容器、K8s Pod、Docker容器中运行——它不关心自己在哪里运行，只负责启动ipykernel并回传端口信息。远程调度由对应的ProcessProxy负责（如YarnClusterProcessProxy提交YARN应用，KubernetesProcessProxy创建Pod）。

## R Launcher [F-166]

位置：`etc/kernel-launchers/R/scripts/`

包含两个文件：
- `launch_IRkernel.R`：R脚本，启动IRkernel
- `server_listener.py`：Python脚本，负责端口监听和连接信息回传

R Launcher使用Python的server_listener处理通信，R脚本专注于内核启动。这种混合设计是因为R的网络/加密库不如Python成熟。

## Scala Launcher (Toree) [F-166]

位置：`etc/kernel-launchers/scala/toree-launcher/`

Scala语言的Launcher，基于Apache Toree（Spark的Scala内核）。以Scala/JVM实现，通过bootstrap-kernel.sh启动。

## Docker Launcher [F-166]

位置：`etc/kernel-launchers/docker/scripts/launch_docker.py`

Docker模式下的Launcher辅助脚本。在Docker场景中，ProcessProxy通过Docker API创建容器，容器内部运行的是标准Python/R/Scala Launcher。launch_docker.py负责处理Docker特有的配置：
- 容器镜像选择
- 环境变量传递
- 卷挂载
- 网络模式

## Kubernetes Launcher [F-166]

位置：`etc/kernel-launchers/kubernetes/scripts/launch_kubernetes.py`

K8s模式下的Launcher辅助脚本，配合Jinja2模板 `kernel-pod.yaml.j2`：
- 渲染Pod模板（镜像、资源限制、环境变量、卷）
- 创建Pod
- 等待Pod就绪
- 端口转发或直接连接Pod IP

## Spark Operator Launcher [F-166]

位置：`etc/kernel-launchers/operators/scripts/launch_custom_resource.py`

K8s CRD模式下的Launcher，配合Spark Operator YAML模板 `sparkoperator.k8s.io-v1beta2.yaml.j2`：
- 创建SparkApplication CRD资源
- 等待Spark Application运行
- 获取Driver Pod信息

## Bootstrap脚本 [F-166]

位置：`etc/kernel-launchers/bootstrap/bootstrap-kernel.sh`

通用的bootstrap脚本，在kernel-launcher之前执行，负责：
- 环境初始化
- Spark配置处理
- 调用对应语言的launcher

## 内核规范（kernelspec）配置 [F-168]

EG在 `etc/kernelspecs/` 下提供了25+种预配置kernelspec，每种对应一个语言+部署平台组合。

### kernelspec目录结构

每个kernelspec是一个目录，包含：
- `kernel.json`：内核定义（启动命令、显示名、语言、metadata）
- 可能包含logo图片、kernel.js等资源文件

### kernel.json 示例

**Python on Kubernetes**：
```json
{
  "argv": [
    "python",
    "/usr/local/share/jupyter/kernels/python_kubernetes/scripts/launch_ipykernel.py",
    "--kernel-id", "{kernel_id}",
    "--port-range", "{port_range}",
    "--response-address", "{response_address}",
    "--public-key", "{public_key}",
    "--spark-context-init-mode", "lazy"
  ],
  "display_name": "Python on Kubernetes",
  "language": "python",
  "metadata": {
    "process_proxy": {
      "class_name": "enterprise_gateway.services.processproxies.k8s.KubernetesProcessProxy",
      "config": {
        "image_name": "elyra/kernel-py:VERSION",
        "executor_image_name": "elyra/kernel-py:VERSION"
      }
    }
  }
}
```

**Python本地模式**：
```json
{
  "argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "Python 3",
  "language": "python",
  "metadata": {
    "process_proxy": {
      "class_name": "enterprise_gateway.services.processproxies.processproxy.LocalProcessProxy"
    }
  }
}
```

关键区别：
- 远程kernelspec的argv使用launch_ipykernel.py等launcher脚本，接收{response_address}/{public_key}/{port_range}/{kernel_id}参数
- 本地kernelspec使用标准的ipykernel_launcher，接收{connection_file}参数
- metadata.process_proxy.class_name决定了使用哪种ProcessProxy

### 支持的kernelspec组合

| 语言 | 本地 | SSH分布式 | YARN | K8s | Docker | Spark Operator |
|------|------|---------|------|-----|--------|---------------|
| Python | python3 | python_distributed | python_yarn | python_kubernetes | python_docker | python_tf_kubernetes/spark_python_yarn |
| R | ir | r_distributed | r_yarn | r_kubernetes | r_docker | spark_r_yarn |
| Scala | - | scala_distributed | spark_scala_yarn | spark_scala_kubernetes | - | spark_scala_kubernetes |
| TensorFlow | - | - | - | tf_kubernetes/tf_gpu_kubernetes | - | - |

## Docker镜像 [F-169]

`etc/docker/` 提供了完整的Docker镜像构建文件：

| 镜像 | 用途 |
|------|------|
| enterprise-gateway | EG服务器镜像 |
| demo-base | 基础演示镜像 |
| enterprise-gateway-demo | 演示环境镜像 |
| kernel-image-puller | K8s环境下预拉取内核镜像 |
| kernel-py | Python内核镜像 |
| kernel-r | R内核镜像 |
| kernel-scala | Scala/Spark内核镜像 |
| kernel-spark-py | Spark Python内核镜像 |
| kernel-spark-r | Spark R内核镜像 |
| kernel-tf-py | TensorFlow CPU内核镜像 |
| kernel-tf-gpu-py | TensorFlow GPU内核镜像 |

## Kubernetes Helm部署 [F-170]

`etc/kubernetes/helm/enterprise-gateway/` 提供Helm Chart用于K8s部署：
- `deployment.yaml`：EG Deployment
- `service.yaml`：EG Service
- `ingress.yaml`：Ingress路由
- `clusterrole.yaml`/`clusterrolebinding.yaml`：RBAC权限（EG需要创建/管理Pod）
- `serviceaccount.yaml`：ServiceAccount
- `configmap.yaml`：内核配置和kernelspec

部署示例参见 [K8s部署示例](/examples/03-kubernetes-deployment.md)。

## 部署模式选择指南

| 场景 | 推荐模式 | ProcessProxy |
|------|---------|-------------|
| 本地开发调试 | 本地模式 | LocalProcessProxy |
| 多服务器集群 | SSH分布式 | DistributedProcessProxy |
| Hadoop/Spark大数据 | YARN | YarnClusterProcessProxy |
| Kubernetes容器化 | Kubernetes | KubernetesProcessProxy |
| Docker单机容器 | Docker | DockerProcessProxy |
| Spark on K8s | Spark Operator | SparkOperatorProcessProxy |
| IBM企业平台 | Conductor | ConductorClusterProcessProxy |
