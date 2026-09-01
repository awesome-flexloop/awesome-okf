---
type: Reference
title: "内核管理器源码"
description: "RemoteMappingKernelManager与RemoteKernelManager源码解析：内核启动/重启/关闭/恢复、用户限额、ProcessProxy集成"
tags: [kernel-manager, remote-kernel, kernel-lifecycle, user-limits, ha]
sources:
  - id: remotemanager
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/kernels/remotemanager.py"
    title: "remotemanager.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
---

# 内核管理器源码

本信源登记 `remotemanager.py` 中的 `RemoteMappingKernelManager` 和 `RemoteKernelManager` 两个核心类。

## RemoteMappingKernelManager 多内核管理器 [F-105~F-117]

管理所有内核实例的映射表，是Jupyter Server `AsyncMappingKernelManager` 的扩展。

### 类定义 [F-105]

```python
class RemoteMappingKernelManager(AsyncMappingKernelManager):
```

### 默认KernelManager类 [F-106]

```python
def _kernel_manager_class_default(self):
    return "enterprise_gateway.services.kernels.remotemanager.RemoteKernelManager"
```

### ZMQ Context配置 [F-107]

覆写 `_context_default()` 方法，支持通过 `EG_ZMQ_MAX_SOCKETS` 和 `EG_ZMQ_IO_THREADS` 环境变量调整ZMQ参数。

### TrackPendingRequests 待启动请求跟踪 [F-108,F-109]

```python
class TrackPendingRequests:
    _all = 0  # 全局pending计数
    _per_user = defaultdict(int)  # 每用户pending计数
```

提供 `increment(username)`、`decrement(username)`、`get_counts(username)` 三个方法。`pending_requests` 是类级别实例，在所有RemoteMappingKernelManager实例间共享。

### start_kernel 内核启动 [F-110,F-111]

```python
async def start_kernel(self, *args, **kwargs):
    username = self.kernel_session_manager.get_kernel_username(**kwargs)
    self._enforce_kernel_limits(username)
    RemoteMappingKernelManager.pending_requests.increment(username)
    try:
        kernel_id = await super().start_kernel(*args, **kwargs)
    finally:
        RemoteMappingKernelManager.pending_requests.decrement(username)
    self.parent.kernel_session_manager.create_session(kernel_id, **kwargs)
    return kernel_id
```

1. 获取当前用户名
2. `_enforce_kernel_limits(username)` 检查内核数限制
3. pending计数+1（finally确保-1）
4. 调用父类启动内核（会创建RemoteKernelManager实例）
5. 创建持久化会话

### _enforce_kernel_limits 限额检查 [F-111]

```python
def _enforce_kernel_limits(self, username):
    # 全局限制：活跃内核数 + pending数 >= max_kernels
    if self.max_kernels and (len(self) + RemoteMappingKernelManager.pending_requests._all >= self.max_kernels):
        raise HTTPError(403, "Kernel limit reached")
    # 每用户限制
    current_kernels = sum(1 for k in self.values() if k.username == username)
    user_pending = RemoteMappingKernelManager.pending_requests._per_user.get(username, 0)
    if self.max_kernels_per_user >= 0 and (current_kernels + user_pending >= self.max_kernels_per_user):
        raise HTTPError(403, "Per-user kernel limit reached")
```

### restart_kernel 内核重启 [F-112]

检查 `restarting` 标志防止重复重启，轮询等待重启完成（通过观察restarting状态变化）。

### shutdown_kernel 内核关闭 [F-113]

```python
async def shutdown_kernel(self, kernel_id, now=False, restart=False):
    km = self.get_kernel(kernel_id)
    # 等待重启完成再关闭
    while km.restarting:
        await asyncio.sleep(0.1)
    await super().shutdown_kernel(kernel_id, now=now, restart=restart)
```

如果kernel_id不存在（KeyError），raise HTTPError(404)。

### start_kernel_from_session HA恢复 [F-114]

用于HA场景从持久化session恢复内核：
1. 构造KernelManager实例
2. 加载连接信息（从response或session）
3. 构造ProcessProxy（根据kernelspec的process_proxy配置）
4. 调用 `process_proxy.load_process_info()` 恢复进程状态
5. 轮询 `process_proxy.poll()` 确认进程仍存活
6. 设置 `kernel_manager.kernel = process_proxy`
7. 启动kernel restarter和activity watching

### check_kernel_id 内核存在性检查 [F-115,F-116]

```python
def check_kernel_id(self, kernel_id):
    if kernel_id not in self:
        if self.parent.availability_mode == AVAILABILITY_REPLICATION:
            self._refresh_kernel(kernel_id)
        else:
            raise KeyError(kernel_id)
```

`_refresh_kernel(kernel_id)` 在replication模式下尝试load_session+start_session恢复内核。

### remove_kernel 内核移除 [F-117]

调用 `super().remove_kernel(kernel_id)` 后删除持久化session。

## RemoteKernelManager 单个内核管理器 [F-118~F-130]

管理单个内核的生命周期，是 `AsyncIOLoopKernelManager` 的扩展，混入了 `EnterpriseGatewayConfigMixin`。

### 构造函数初始化 [F-119]

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.process_proxy = None
    self.response_address = None
    self.public_key = None
    self.sigint_value = None
    self.kernel_id = None
    self.user_overrides = {}
    self.kernel_launch_timeout = 30
    self.restarting = False
    self._activity_stream = None
    self.cache_ports = False  # 禁用端口缓存
```

### _link_dependent_props 配置联动 [F-120]

使用 `traitlets.directional_link` 将父app的14个配置属性单向同步到自身：
- authorized_users, unauthorized_users
- port_range, max_port_range_retries
- impersonation_enabled, authorized_origin
- trust_xheaders, client_envs, inherited_envs, kernel_headers
- response_address, public_key
- socket_timeout, kernel_launch_timeout

### start_kernel 启动流程 [F-121]

```python
async def start_kernel(self, **kwargs):
    self.kernel_id = kwargs.get("kernel_id") or new_kernel_id()
    self.process_proxy = self._get_process_proxy()
    self._capture_user_overrides(**kwargs)
    self._enforce_authorization()
    await super().start_kernel(**kwargs)
```

### _capture_user_overrides 环境变量捕获 [F-122]

捕获三类环境变量存入 `self.user_overrides`：
1. 以 `KERNEL_` 开头的变量
2. 在 `inherited_envs` 列表中的变量
3. 在 `client_envs` 列表中的变量

特别处理 `KERNEL_LAUNCH_TIMEOUT`，设置 `kernel_launch_timeout`。

### format_kernel_cmd 命令模板替换 [F-123]

替换kernel命令模板中的四个占位符：
- `{response_address}` — ResponseManager监听地址
- `{public_key}` — RSA公钥
- `{port_range}` — 端口范围
- `{kernel_id}` — 内核ID

### _launch_kernel 进程启动 [F-124]

```python
async def _launch_kernel(self, kernel_cmd, **kwargs):
    env = kwargs.get("env", os.environ).copy()
    env["KERNEL_GATEWAY"] = "1"
    env.pop("EG_AUTH_TOKEN", None)
    env.pop("KG_AUTH_TOKEN", None)
    kwargs["env"] = env
    return await self.process_proxy.launch_process(kernel_cmd, **kwargs)
```

关键动作：
1. 设置 `KERNEL_GATEWAY=1` 标记（供Notebook前端识别EG环境）
2. 移除认证Token环境变量（防止泄露给内核进程）
3. 委托给process_proxy.launch_process()

### write_connection_file 条件写入 [F-125]

```python
def write_connection_file(self, *args, **kwargs):
    if self.is_remote() or not self.response_address:
        return  # 远程内核由launcher返回连接信息，跳过本地文件写入
    super().write_connection_file(*args, **kwargs)
```

远程内核场景下跳过本地connection file写入，连接信息由launcher通过ResponseManager回传。

### _get_process_proxy ProcessProxy工厂 [F-126]

```python
def _get_process_proxy(self):
    kernelspec = self.kernel_spec
    proxy_config = get_process_proxy_config(kernelspec)
    class_name = proxy_config.get("class_name")
    proxy_class = import_item(class_name)
    return proxy_class(self, proxy_config.get("config", {}))
```

### signal_kernel 信号发送 [F-127]

特殊处理SIGINT信号：
1. 若设置了 `EG_ALTERNATE_SIGINT` 环境变量，使用替代信号
2. SIGINT通过ZMQ interrupt模式发送（而非OS信号）
3. 其他信号直接调用 `process_proxy.send_signal(signum)`

### cleanup 资源清理 [F-128]

关闭时调用 `process_proxy.cleanup()`。注意使用process_proxy而非kernel属性，因为 `_kill_kernel` 会置 `self.kernel = None`。

### request_shutdown 关闭通知 [F-129]

对RemoteProcessProxy调用 `shutdown_listener()` 通知launcher退出监听线程。

## new_kernel_id 函数 [F-130]

```python
def new_kernel_id(**kwargs):
    # 支持客户端通过KERNEL_ID环境变量指定kernel_id
    # 必须为合法的UUID v4格式
```

允许客户端在启动内核时指定自定义的kernel_id。
