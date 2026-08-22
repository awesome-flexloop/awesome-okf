---
type: Reference
title: "ProcessProxy进程代理体系源码"
description: "BaseProcessProxyABC抽象基类、LocalProcessProxy、RemoteProcessProxy及其8种具体实现的源码解析，包括SSH隧道、端口管理、授权检查"
tags: [process-proxy, kernel-launch, remote, kubernetes, yarn, docker, ssh]
sources:
  - id: processproxy
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/processproxy.py"
    title: "processproxy.py"
  - id: container
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/container.py"
    title: "container.py"
  - id: k8s
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/k8s.py"
    title: "k8s.py"
  - id: yarn
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/yarn.py"
    title: "yarn.py"
  - id: distributed
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/distributed.py"
    title: "distributed.py"
  - id: docker-swarm
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/docker_swarm.py"
    title: "docker_swarm.py"
  - id: conductor
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/conductor.py"
    title: "conductor.py"
  - id: crd
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/crd.py"
    title: "crd.py"
  - id: spark-operator
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/processproxies/spark_operator.py"
    title: "spark_operator.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
---

# ProcessProxy进程代理体系源码

ProcessProxy是Enterprise Gateway的核心抽象层，定义了"如何启动和管理内核进程"的统一接口。

## 类继承层次 [F-087]

```
BaseProcessProxyABC (抽象基类)
├── LocalProcessProxy          # 本地进程
└── RemoteProcessProxy (抽象)  # 远程进程基类
    ├── DistributedProcessProxy    # SSH分布式（轮询/最少连接）
    ├── YarnClusterProcessProxy    # Apache Hadoop YARN
    ├── ConductorClusterProcessProxy # IBM Spectrum Conductor
    └── ContainerProcessProxy (抽象) # 容器基类
        ├── KubernetesProcessProxy    # Kubernetes Pod
        │   └── CustomResourceProcessProxy  # K8s CRD
        │       └── SparkOperatorProcessProxy  # Spark Operator CRD
        ├── DockerSwarmProcessProxy   # Docker Swarm
        └── DockerProcessProxy        # Docker Engine
```

## BaseProcessProxyABC 抽象基类 [F-061~F-070]

### 构造函数 [F-062]

```python
def __init__(self, kernel_manager: RemoteKernelManager, proxy_config: dict):
    self.kernel_manager = kernel_manager
    self.proxy_config = proxy_config
    self.local_proc = None
    self.ip = None
    self.pid = None
    self.pgid = None
```

### 抽象方法 [F-063]

```python
@abc.abstractmethod
async def launch_process(self, kernel_cmd, **kwargs):
    pass
```

### 进程生命周期方法 [F-064,F-065]

| 方法 | 行为 |
|------|------|
| `launch_kernel(cmd, **kwargs)` | 调用 `jupyter_client.launch_kernel` 启动本地子进程 |
| `poll()` | 本地：`local_proc.poll()`；远程：`send_signal(0)` 检查进程存活 |
| `wait()` | 本地：`local_proc.wait()`；远程：轮询poll直到进程退出 |
| `send_signal(signum)` | 本地：`local_proc.send_signal()`；远程：SSH发送kill信号 |
| `kill()` | 先SIGTERM，轮询max_poll_attempts次，仍存活则SIGKILL |
| `terminate()` | 发送SIGTERM |
| `cleanup()` | 清理资源（默认空实现，子类覆盖） |

### 授权检查 [F-066]

`_enforce_authorization()` 方法检查KERNEL_USERNAME：
- 在 `unauthorized_users` 集合中 → raise HTTPError(403)
- `authorized_users` 非空且用户不在其中 → raise HTTPError(403)

### 端口管理 [F-067]

`_validate_port_range(port_range)` 解析 "lower..upper" 格式：
- 范围大小 ≥ `min_port_range_size`（默认1000）
- 端口在 1024~65535 范围内

`select_ports(count)` 创建socket绑定随机端口后立即关闭，返回可用端口列表。

### 进程信息持久化 [F-068]

```python
def get_process_info(self):
    return {"pid": self.pid, "pgid": self.pgid, "ip": self.ip}

def load_process_info(self, process_info):
    self.pid = process_info["pid"]
    self.pgid = process_info["pgid"]
    self.ip = process_info["ip"]
```

用于HA模式下恢复内核状态。

### SSH远程执行 [F-069]

| 方法 | 行为 |
|------|------|
| `_get_ssh_client(host)` | 创建paramiko SSHClient，支持密码/密钥/GSS认证 |
| `rsh(host, command)` | 通过SSH执行远程命令，返回stdout行列表 |
| `remote_signal(signum)` | 通过SSH发送 `kill -<signum> <pid>` 命令 |

## LocalProcessProxy 本地进程代理 [F-070]

```python
class LocalProcessProxy(BaseProcessProxyABC):
    async def launch_process(self, kernel_cmd, **kwargs):
        self._enforce_authorization()
        self.local_proc = self.launch_kernel(kernel_cmd, **kwargs)
        self.pid = self.local_proc.pid
        self.pgid = os.getpgid(self.pid)
        self.ip = self.kernel_manager.local_ip
        return self
```

直接在本地启动内核子进程，记录pid/pgid/ip。

## RemoteProcessProxy 远程进程代理基类 [F-071~F-076]

### 构造函数初始化 [F-072]

1. 获取 `ResponseManager.instance()` 单例
2. 为当前 `kernel_id` 注册响应事件
3. 设置 `kernel_manager.response_address` 和 `public_key`

### 抽象方法 [F-073]

```python
@abc.abstractmethod
async def confirm_remote_startup(self):
    pass
```

子类必须实现此方法等待远程内核启动完成。

### launch_process 启动流程 [F-074]

1. 设置环境变量 `EG_MIN_PORT_RANGE_SIZE`、`EG_MAX_PORT_RANGE_RETRIES`
2. 调用 `super().launch_process()` 启动本地launcher进程
3. 调用 `cleanup_connection_file()` 清理本地connection file

### 失败检测 [F-075]

`detect_launch_failure()` 检查 `local_proc.poll()` 是否返回非0值，是则raise HTTPError(500)。

### SSH隧道 [F-076]

| 方法 | 行为 |
|------|------|
| `_tunnel_to_kernel(connection_info, server)` | 为5个ZMQ通道创建SSH隧道（SHELL/iopub/stdin/hb/control） |
| `_create_ssh_tunnel(channel)` | 创建单个SSH隧道 |
| `_tunnel_to_port(port, server)` | 为单个端口创建SSH隧道 |

SSH隧道将远程主机的ZMQ端口映射到本地，使WebSocket代理可以连接。

## 具体实现类

### DistributedProcessProxy SSH分布式 [F-077,F-078]

- 内部类 `TrackKernelOnHost` 跟踪每个主机上的内核计数
- 支持两种负载均衡算法：round-robin（轮询）和least-connection（最少连接数优先）
- 从 `remote_hosts` 列表中选择目标主机
- 通过SSH远程启动launcher进程

### YarnClusterProcessProxy YARN集群 [F-079]

- 通过YARN Resource Manager REST API提交内核进程
- 支持kerberos安全认证（yarn_endpoint_security_enabled）
- 轮询YARN应用状态确认启动完成

### ConductorClusterProcessProxy IBM Conductor [F-080]

- 对接IBM Spectrum Conductor REST API
- 通过Conductor Spark实例管理内核生命周期

### ContainerProcessProxy 容器基类 [F-081]

- 定义容器化进程代理的通用接口
- 处理容器镜像、资源限制、网络配置等通用容器逻辑

### KubernetesProcessProxy Kubernetes [F-082]

- 通过Kubernetes Python API创建Pod
- 支持kernel-pod.yaml.j2模板渲染
- 轮询Pod状态等待Running
- 通过exec或端口转发连接内核

### DockerSwarmProcessProxy / DockerProcessProxy [F-083,F-084]

- DockerSwarm：通过Docker Swarm API创建Service
- DockerProcessProxy：通过Docker Engine API创建Container

### CustomResourceProcessProxy K8s CRD [F-085]

- 继承KubernetesProcessProxy，使用K8s CustomResourceDefinition管理内核
- 支持自定义CRD类型

### SparkOperatorProcessProxy Spark Operator [F-086]

- 继承CustomResourceProcessProxy
- 使用Spark Operator CRD（sparkoperator.k8s.io）管理Spark应用内核

## 工厂函数

### get_process_proxy_config [F-088,F-090]

```python
def get_process_proxy_config(kernelspec):
    if 'process_proxy' in kernelspec.metadata:
        return kernelspec.metadata['process_proxy']
    return {
        "class_name": "enterprise_gateway.services.processproxies.processproxy.LocalProcessProxy",
        "config": {}
    }
```

从kernelspec的metadata中读取process_proxy配置，无配置则默认使用LocalProcessProxy。

ProcessProxy实例化通过 `traitlets.import_item(class_name)` 动态导入类，class_name从kernelspec配置中获取 [F-089]。
