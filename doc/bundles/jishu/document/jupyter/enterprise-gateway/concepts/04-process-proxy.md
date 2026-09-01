---
okf_version: "0.2"
type: "concept"
title: "ProcessProxy进程代理体系"
description: "ProcessProxy核心抽象、三层继承体系、9种进程代理实现详解、SSH隧道机制、自定义ProcessProxy扩展方法"
tags: [process-proxy, abstraction, remote-kernel, kubernetes, yarn, docker, ssh, plugin]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: process-proxy
    resource: "/references/process-proxy-source.md"
    title: "ProcessProxy源码"
---

# ProcessProxy进程代理体系

ProcessProxy是Enterprise Gateway**最核心的抽象层**，它将"如何启动和管理内核进程"这一问题从KernelManager中解耦出来，使EG可以支持本地、SSH、YARN、Kubernetes、Docker等多种部署后端。

## 为什么需要ProcessProxy

Jupyter原生的KernelManager直接通过 `subprocess.Popen` 在本地启动内核进程。这种方式无法满足企业级场景：
- 内核需要运行在远程计算节点上（YARN/K8s集群）
- 需要通过SSH启动远程进程
- 需要在容器中运行内核
- 需要在调度器（如YARN、K8s）中申请资源后启动

ProcessProxy抽象了进程的生命周期管理，使得KernelManager不需要关心进程实际运行在哪里。

## 类继承体系 [F-087]

```
BaseProcessProxyABC (抽象基类)          ← 定义统一接口
│
├── LocalProcessProxy                    ← 本地子进程
│
└── RemoteProcessProxy (抽象)            ← 远程进程基础能力
    │                                    （SSH隧道、ResponseManager集成）
    ├── DistributedProcessProxy          ← SSH轮询/最少连接
    ├── YarnClusterProcessProxy          ← Apache Hadoop YARN
    ├── ConductorClusterProcessProxy     ← IBM Spectrum Conductor
    │
    └── ContainerProcessProxy (抽象)     ← 容器通用逻辑
        ├── KubernetesProcessProxy       ← Kubernetes Pod
        │   └── CustomResourceProcessProxy  ← K8s CRD
        │       └── SparkOperatorProcessProxy ← Spark Operator
        ├── DockerSwarmProcessProxy      ← Docker Swarm Service
        └── DockerProcessProxy           ← Docker Container
```

## BaseProcessProxyABC 统一接口 [F-061~F-069]

所有ProcessProxy必须实现/继承以下接口：

### 核心方法

| 方法 | 类型 | 说明 |
|------|------|------|
| `launch_process(kernel_cmd, **kwargs)` | 抽象 | 启动进程，返回self |
| `poll()` | 实现 | 检查进程是否存活（None=存活，int=退出码） |
| `wait()` | 实现 | 阻塞等待进程退出 |
| `send_signal(signum)` | 实现 | 向进程发送信号 |
| `kill()` | 实现 | 强制终止进程（SIGTERM→轮询→SIGKILL） |
| `terminate()` | 实现 | 优雅终止（SIGTERM） |
| `cleanup()` | 空实现 | 清理资源（子类可覆盖） |
| `get_process_info()` | 实现 | 返回进程信息（pid/pgid/ip）用于持久化 |
| `load_process_info(info)` | 实现 | 从持久化数据恢复进程状态 |

### 授权检查 [F-066]

`_enforce_authorization()` 方法在进程启动前检查用户权限：
- KERNEL_USERNAME在unauthorized_users中 → 403 Forbidden
- authorized_users非空且用户不在其中 → 403 Forbidden

### 端口管理 [F-067]

`_validate_port_range(port_range)` 验证端口范围配置：
- 格式为 "lower..upper"（如 "40000..50000"）
- 范围大小至少1000个端口
- 端口值在1024~65535之间

`select_ports(count)` 通过创建socket绑定随机端口然后关闭的方式获取可用端口。

### SSH远程执行 [F-069]

基类提供了SSH远程执行的基础能力：
- `_get_ssh_client(host)`：创建paramiko SSH连接（支持密码/密钥/GSS认证）
- `rsh(host, command)`：通过SSH执行远程命令
- `remote_signal(signum)`：通过SSH发送kill信号

## LocalProcessProxy 本地进程 [F-070]

最简单的ProcessProxy，直接在本地启动子进程：

```python
async def launch_process(self, kernel_cmd, **kwargs):
    self._enforce_authorization()
    self.local_proc = self.launch_kernel(kernel_cmd, **kwargs)
    self.pid = self.local_proc.pid
    self.pgid = os.getpgid(self.pid)
    self.ip = self.kernel_manager.local_ip
    return self
```

`launch_kernel()` 调用 `jupyter_client.launch_kernel`，本质上是 `subprocess.Popen`。

适用于开发调试和单机部署场景。

## RemoteProcessProxy 远程进程基类 [F-071~F-076]

所有远程进程代理的基类，提供远程启动的通用能力。

### 构造函数初始化 [F-072]

```python
def __init__(self, kernel_manager, proxy_config):
    super().__init__(kernel_manager, proxy_config)
    self.response_manager = ResponseManager.instance()
    self.response_manager.register_event(self.kernel_manager.kernel_id)
    self.kernel_manager.response_address = self.response_manager.response_address
    self.kernel_manager.public_key = self.response_manager.public_key
```

关键操作：
1. 获取ResponseManager单例
2. 为当前kernel_id注册响应事件
3. 将response_address和public_key设置到kernel_manager，用于格式化启动命令

### 抽象方法 [F-073]

```python
@abc.abstractmethod
async def confirm_remote_startup(self):
    """等待远程内核启动完成并获取连接信息"""
```

子类必须实现此方法，在其中轮询ResponseManager等待launcher回传连接信息。

### launch_process 远程启动流程 [F-074]

```python
async def launch_process(self, kernel_cmd, **kwargs):
    # 设置端口范围相关环境变量
    kwargs['env']['EG_MIN_PORT_RANGE_SIZE'] = str(min_port_range_size)
    kwargs['env']['EG_MAX_PORT_RANGE_RETRIES'] = str(max_port_range_retries)
    
    await super().launch_process(kernel_cmd, **kwargs)
    self.cleanup_connection_file()  # 清理本地connection file
    await self.confirm_remote_startup()
    return self
```

### SSH隧道 [F-076]

远程内核启动后，ZMQ端口在远程主机上，EG需要通过SSH隧道将远程端口映射到本地：

- `_tunnel_to_kernel(connection_info, server)`：为5个ZMQ通道（shell/iopub/stdin/hb/control）创建SSH隧道
- `_create_ssh_tunnel(channel)`：创建单个SSH隧道
- `_tunnel_to_port(port, server)`：为指定端口创建隧道

隧道建立后，WebSocket代理就可以像连接本地端口一样连接远程内核。

## 具体实现详解

### DistributedProcessProxy SSH分布式 [F-077,F-078]

- **适用场景**：多台Linux服务器通过SSH管理
- **负载均衡**：内部类`TrackKernelOnHost`跟踪每个主机上的内核数
- **算法**：
  - round-robin：循环选择主机
  - least-connection：选择内核数最少的主机
- **启动方式**：通过paramiko SSH连接到选定主机，执行launcher启动脚本
- **进程检测**：通过SSH发送kill -0检查进程存活

### YarnClusterProcessProxy YARN集群 [F-079]

- **适用场景**：Hadoop/YARN大数据集群，Spark on YARN
- **启动方式**：通过YARN Resource Manager REST API提交应用
- **安全支持**：支持Kerberos认证（yarn_endpoint_security_enabled）
- **状态轮询**：轮询YARN应用状态等待Running
- **进程管理**：通过YARN API发送信号、杀死应用

### KubernetesProcessProxy Kubernetes [F-082]

- **适用场景**：Kubernetes容器化部署
- **启动方式**：通过Kubernetes Python API创建Pod
- **模板**：使用Jinja2渲染kernel-pod.yaml.j2模板
- **状态轮询**：轮询Pod状态等待Running
- **连接方式**：通过端口转发或kubectl exec连接内核

### DockerProcessProxy Docker容器 [F-084]

- **适用场景**：单节点Docker部署
- **启动方式**：通过Docker Engine API创建容器
- **网络**：使用bridge或host网络
- **端口映射**：自动映射ZMQ端口

### DockerSwarmProcessProxy Docker Swarm [F-083]

- **适用场景**：Docker Swarm集群
- **启动方式**：通过Docker API创建Service
- **扩缩容**：可利用Swarm的调度能力

### CustomResourceProcessProxy / SparkOperatorProcessProxy K8s CRD [F-085,F-086]

- **CustomResourceProcessProxy**：继承KubernetesProcessProxy，使用K8s CRD管理内核Pod
- **SparkOperatorProcessProxy**：继承CustomResourceProcessProxy，专门用于Spark Operator CRD（sparkoperator.k8s.io/v1beta2），适用于Spark on Kubernetes场景

### ConductorClusterProcessProxy IBM Conductor [F-080]

- **适用场景**：IBM Spectrum Conductor企业级计算平台
- **启动方式**：通过Conductor REST API
- 与YarnClusterProcessProxy逻辑类似

## ProcessProxy的选择与配置 [F-088,F-089,F-090]

ProcessProxy不是全局配置的，而是**per-kernelspec**配置的。在kernelspec的 `kernel.json` 中通过 `metadata.process_proxy` 声明：

```json
{
  "argv": ["python", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "Python on Kubernetes",
  "language": "python",
  "metadata": {
    "process_proxy": {
      "class_name": "enterprise_gateway.services.processproxies.k8s.KubernetesProcessProxy",
      "config": {
        "image_name": "elyra/kernel-py:VERSION",
        "executor_image_name": "..."
      }
    }
  }
}
```

默认无配置时使用 `LocalProcessProxy` [F-090]。

ProcessProxy通过 `traitlets.import_item(class_name)` 动态加载 [F-089]，这意味着：
1. 可以自定义ProcessProxy类，只要安装在Python路径中
2. 不同kernelspec可以使用完全不同的部署方式（例如Python在K8s、R在YARN）
3. config字典中的参数传递给ProcessProxy构造函数

## 自定义ProcessProxy扩展

要自定义ProcessProxy，需继承 `RemoteProcessProxy`（远程场景）或 `BaseProcessProxyABC`（全新场景），实现：

1. `launch_process(kernel_cmd, **kwargs)`：启动进程（调用平台API）
2. `confirm_remote_startup()`：等待进程就绪，从ResponseManager获取连接信息
3. `poll()`/`wait()`/`send_signal()`/`kill()`/`terminate()`：进程生命周期管理
4. `get_process_info()`/`load_process_info()`：HA持久化支持（可选）

具体示例参见 [编写自定义ProcessProxy](../examples/02-custom-process-proxy.md)。
