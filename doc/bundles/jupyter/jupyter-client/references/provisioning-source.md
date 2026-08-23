---
okf_version: "0.2"
type: reference
title: "内核供给器框架 (provisioning/)"
description: "KernelProvisionerBase/LocalProvisioner/KernelProvisionerFactory 源码——可插拔内核生命周期抽象、Popen本地进程管理、entry_points插件发现"
tags: ["provisioner", "kernel-provisioner", "plugin", "entry-points", "local-provisioner"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: provisioning-init
    resource: jupyter_client/provisioning/__init__.py
    title: jupyter_client/provisioning/__init__.py
  - id: provisioning-base
    resource: jupyter_client/provisioning/provisioner_base.py
    title: jupyter_client/provisioning/provisioner_base.py
  - id: provisioning-local
    resource: jupyter_client/provisioning/local_provisioner.py
    title: jupyter_client/provisioning/local_provisioner.py
  - id: provisioning-factory
    resource: jupyter_client/provisioning/factory.py
    title: jupyter_client/provisioning/factory.py
---

# 内核供给器框架 (provisioning/)

Provisioner 是 jupyter_client 的可插拔内核生命周期抽象层，允许将内核运行在本地进程、远程服务器、Docker 容器或 Kubernetes Pod 中。

```python
# provisioning/__init__.py 导出
from .provisioner_base import KernelProvisionerBase
from .local_provisioner import LocalProvisioner
from .factory import KernelProvisionerFactory

# provisioning/provisioner_base.py
class KernelProvisionerBase(Configurable, metaclass=abc.ABCMeta):
    """供给器抽象基类"""

    kernel_id = Unicode()
    kernel_spec: KernelSpec = Instance(KernelSpec, allow_none=True)
    connection_info = Dict()
    process = Any(allow_none=True)  # Popen 或远程进程句柄
    log = Instance(logging.Logger, allow_none=True)

    # 生命周期方法（抽象）
    @abc.abstractmethod
    async def pre_launch(self, **kwargs) -> dict:
        """启动前准备（端口分配、环境变量等）"""

    @abc.abstractmethod
    async def launch_kernel(self, cmd, **kwargs) -> KernelConnectionInfo:
        """启动内核进程，返回连接信息"""

    @abc.abstractmethod
    async def post_launch(self, **kwargs) -> None:
        """启动后操作（连接验证等）"""

    @abc.abstractmethod
    async def poll(self) -> int | None:
        """检查进程是否结束，返回退出码或None"""

    @abc.abstractmethod
    async def wait(self) -> int | None:
        """等待进程结束"""

    @abc.abstractmethod
    async def send_signal(self, signum: int) -> None:
        """发送信号到内核进程"""

    @abc.abstractmethod
    async def kill(self, restart: bool = False) -> None:
        """强制杀死内核"""

    @abc.abstractmethod
    async def terminate(self, restart: bool = False) -> None:
        """优雅终止内核"""

    @abc.abstractmethod
    async def cleanup(self, restart: bool = False) -> None:
        """清理资源"""

    # 可选方法（非抽象）
    async def shutdown_requested(self, restart=False) -> None:
        """内核请求关闭时的钩子"""
    def get_shutdown_wait_time(self, recommended=5.0) -> float: ...
    def get_stable_start_time(self, recommended=10.0) -> float: ...
    def has_process(self) -> bool: ...

# provisioning/local_provisioner.py
class LocalProvisioner(KernelProvisionerBase):
    """本地进程供给器——使用 subprocess.Popen"""

    proc: Popen | None = None
    _exit_future = None

    async def launch_kernel(self, cmd, **kwargs):
        # 1. 写入连接文件（write_connection_file）
        # 2. Popen 启动进程（处理 Windows/Unix 差异）
        # 3. 返回 connection_info
        ...

    async def poll(self): return self.proc.poll() if self.proc else None
    async def wait(self): ...
    async def send_signal(self, signum): os.kill(self.pid, signum)
    async def kill(self, restart=False): self.proc.kill()
    async def terminate(self, restart=False): self.proc.terminate()
    async def cleanup(self, restart=False):
        self.cleanup_connection_file()
        if restart:
            self.cleanup_random_ports()

# provisioning/factory.py
class KernelProvisionerFactory(SingletonConfigurable):
    """供给器工厂——通过 entry_points 发现可用供给器"""

    GROUP_NAME = "jupyter_client.kernel_provisioners"
    default_provisioner_name = "local-provisioner"

    def create_provisioner_instance(self, kernel_id, kernel_spec, parent):
        """根据 kernelspec 的 metadata.provisioner_name 创建供给器实例"""
        # 通过 importlib.metadata.entry_points 发现注册的 provisioner
        # 默认使用 LocalProvisioner
```

**关键设计点**：
- **ABC 抽象强制**：`KernelProvisionerBase` 定义了8个抽象方法（pre_launch/launch_kernel/post_launch/poll/wait/send_signal/kill/terminate/cleanup），子类必须全部实现
- **entry_points 插件发现**：通过 `jupyter_client.kernel_provisioners` entry point group 注册自定义供给器，LocalProvisioner 注册为 `local-provisioner`
- **Singleton 工厂**：`KernelProvisionerFactory` 是单例，全局共享供给器注册表
- **LocalProvisioner 平台差异**：Windows 上使用 `CREATE_NEW_PROCESS_GROUP` 和中断事件（win_interrupt.py），Unix 使用进程组和 `os.killpg`
- **CurveZMQ 支持**：LocalProvisioner 在 pre_launch 阶段可生成 CurveZMQ 密钥对
- **端口缓存**：通过 `LocalPortCache` 单例防止多内核端口竞争
