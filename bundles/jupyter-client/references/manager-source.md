---
okf_version: "0.2"
type: reference
title: "内核管理器 (manager.py)"
description: "KernelManager/AsyncKernelManager 源码——内核生命周期管理（启动/关闭/重启/中断）、client 工厂方法、Provisioner 委托模式"
tags: ["manager", "kernel-manager", "lifecycle", "provisioner", "kernel-startup"]
generated: { by: "reference_agent/trae-cn", at: "2026-08-21T15:57:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-21T15:57:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: manager-py
    resource: jupyter_client/manager.py
    title: jupyter_client/manager.py
---

# 内核管理器 (manager.py)

`KernelManager` 负责内核进程的完整生命周期管理，继承自 `ConnectionFileMixin` 和 `KernelClientFactory`。实际的进程启动/信号发送委托给 `KernelProvisioner`。

```python
class _ShutdownStatus(enum.Enum):
    """内核关闭状态机"""
    Unset = 0
    WaitForShutdown = 1
    WaitForKill = 2
    Finished = 3

def in_pending_state(method):
    """装饰器：检查内核是否处于 pending 状态（启动/关闭中）"""
    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        if self._pending_shutdown or self._pending_start:
            msg = f"Kernel is in a pending state..."
            raise RuntimeError(msg)
        return method(self, *args, **kwargs)
    return wrapped

class KernelManager(ConnectionFileMixin, KernelClientFactory):
    """Manages a single kernel's lifecycle."""

    kernel_name = Unicode("python3")
    provisioner = Instance("jupyter_client.provisioning.KernelProvisionerBase", allow_none=True)
    _pending_start = Bool(False)
    _pending_shutdown = Bool(False)

    # 生命周期方法
    @in_pending_state
    def start_kernel(self, **kw):
        """启动内核进程"""
        self._pending_start = True
        try:
            # 1. 创建/选择 provisioner
            self.provisioner = KernelProvisionerFactory.instance().create_provisioner_instance(...)
            # 2. pre_launch → launch → post_launch
            connection_info = self.provisioner.launch_kernel(kernel_cmd, **kw)
            self._reconcile_connection_info(connection_info)
        finally:
            self._pending_start = False

    @in_pending_state
    def shutdown_kernel(self, now=False, restart=False):
        """关闭内核"""
        self._pending_shutdown = True
        try:
            self.provisioner.shutdown_kernel(restart=restart)
            self.cleanup_connection_file()
        finally:
            self._pending_shutdown = False

    def restart_kernel(self, now=False, **kw): ...
    def interrupt_kernel(self): ...
    def signal_kernel(self, signum): ...

    # 状态检查
    def is_alive(self) -> bool: ...
    def has_kernel(self) -> bool: ...

    # Client 工厂
    def client(self, **kwargs) -> KernelClient:
        """创建连接到此内核的 client"""
        return self.blocking_client(**kwargs)  # 默认返回 BlockingKernelClient

class AsyncKernelManager(KernelManager):
    """异步版本的 KernelManager"""
    context = Instance(zmq.asyncio.Context)
    # 所有生命周期方法均为 async
    async def start_kernel(self, **kw): ...
    async def shutdown_kernel(self, now=False, restart=False): ...
    async def _async_is_alive(self) -> bool: ...

# 便捷函数
def start_new_kernel(startup_timeout=60, kernel_name="python3", **kwargs):
    """启动一个新内核，返回 (km, kc) 元组"""
    km = KernelManager(kernel_name=kernel_name)
    km.start_kernel(**kwargs)
    kc = km.client()
    kc.start_channels()
    kc.wait_for_ready(timeout=startup_timeout)
    return km, kc

async def start_new_async_kernel(...): ...  # 异步版本
def run_kernel(**kwargs): ...  # 运行内核的便捷入口
```

**关键设计点**：
- **Provisioner 委托模式**：KernelManager 不直接启动进程，而是通过 `KernelProvisionerFactory` 创建 provisioner，将进程管理委托出去
- **pending 状态保护**：`@in_pending_state` 装饰器防止在内核启动/关闭过程中执行冲突操作
- **连接信息调和**：`_reconcile_connection_info()` 确保 provisioner 返回的连接信息与本地连接文件一致，解决竞争条件
- **同步/异步双实现**：`AsyncKernelManager` 使用 `zmq.asyncio.Context`，所有生命周期方法为 async
