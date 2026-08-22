---
okf_version: "0.2"
type: "concept"
title: "远程内核管理"
description: "RemoteMappingKernelManager多内核管理、RemoteKernelManager单内核生命周期、内核限额、HA恢复机制"
tags: [kernel-manager, remote-kernel, lifecycle, limits, high-availability, restart]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: kernel-manager
    resource: "/references/kernel-manager-source.md"
    title: "内核管理器源码"
  - id: process-proxy
    resource: "/references/process-proxy-source.md"
    title: "ProcessProxy源码"
---

# 远程内核管理

Enterprise Gateway的内核管理由两个核心类协作完成：
- **RemoteMappingKernelManager**：管理所有内核实例的映射表，负责限额检查、会话管理
- **RemoteKernelManager**：管理单个内核的完整生命周期，负责进程代理集成

## RemoteMappingKernelManager

扩展了Jupyter Server的 `AsyncMappingKernelManager`，添加了EG特有功能。

### 内核启动流程 [F-110]

```
start_kernel(kernel_name, **kwargs)
  │
  ├─ 1. get_kernel_username()         ← 从请求中提取KERNEL_USERNAME
  ├─ 2. _enforce_kernel_limits()      ← 检查全局/每用户限额
  ├─ 3. pending_requests.increment()  ← pending计数+1
  ├─ 4. super().start_kernel()        ← 创建RemoteKernelManager并启动
  │     └─ RemoteKernelManager.start_kernel()
  │           ├─ _get_process_proxy()
  │           ├─ _capture_user_overrides()
  │           └─ process_proxy.launch_process()
  ├─ 5. pending_requests.decrement()  ← pending计数-1（finally保证）
  └─ 6. create_session()              ← 持久化会话记录
```

### 内核限额检查 [F-111]

`_enforce_kernel_limits(username)` 执行两层检查：

1. **全局限额**：`len(self) + pending_all >= max_kernels` → 403
   - `len(self)` 是当前活跃内核数
   - `pending_all` 是正在启动中的内核数（全局）
   
2. **每用户限额**：`user_kernels + pending_user >= max_kernels_per_user` → 403
   - `user_kernels` 是该用户当前活跃内核数
   - `pending_user` 是该用户正在启动的内核数

> **注意**：pending计数很重要——如果只检查活跃内核数，并发请求可能在同一时刻通过检查，导致超出限额。TrackPendingRequests将pending中的请求也计入限额 [F-108,F-109]。

### TrackPendingRequests 并发控制 [F-108,F-109]

```python
class TrackPendingRequests:
    _all = 0
    _per_user = defaultdict(int)
```

类级别的实例（所有RemoteMappingKernelManager共享），通过 `increment(username)` 和 `decrement(username)` 维护计数。这确保即使在并发场景下限额检查也是准确的。

### 内核重启 [F-112]

`restart_kernel(kernel_id)` 处理逻辑：
1. 获取RemoteKernelManager实例
2. 检查 `restarting` 标志，防止重复重启
3. 设置 `restarting = True`
4. 调用父类重启逻辑（kill旧进程→启动新进程）
5. 轮询等待 `restarting = False`
6. 重启后更新会话信息

### 内核关闭 [F-113]

`shutdown_kernel(kernel_id, now=False, restart=False)` 处理逻辑：
1. 获取RemoteKernelManager实例
2. 轮询等待重启完成（如果正在重启中）
3. 调用 `super().shutdown_kernel()`（最终调用process_proxy.kill()或terminate()）
4. 若不是restart场景，删除持久化会话

### HA内核恢复 [F-114,F-115,F-116]

两种恢复模式：

**standalone模式 - 启动时全量恢复** [F-028]：
- EG启动时调用 `kernel_session_manager.start_sessions()`
- 遍历所有持久化session
- 对每个session调用 `start_kernel_from_session()`
- 恢复process_proxy状态（pid/pgid/ip），poll确认进程仍存活
- 重建ZMQ连接（SSH隧道等）

**replication模式 - 访问时懒加载恢复** [F-116]：
- `check_kernel_id(kernel_id)` 发现内核不在内存中时
- 调用 `_refresh_kernel(kernel_id)` 尝试从持久化session恢复
- 恢复成功后继续处理请求
- 适用于多EG实例部署场景

`start_kernel_from_session()` 恢复步骤 [F-114]：
1. 构造RemoteKernelManager实例
2. 加载kernelspec
3. 创建ProcessProxy实例
4. 调用 `process_proxy.load_process_info(process_info)` 恢复pid/pgid/ip
5. 轮询 `process_proxy.poll()` 确认进程存活（None=存活）
6. 设置 `kernel_manager.kernel = process_proxy`（将process_proxy作为kernel属性）
7. 启动kernel restarter和activity watching

## RemoteKernelManager

管理单个内核的完整生命周期，混入了 `EnterpriseGatewayConfigMixin` 获取配置 [F-118]。

### 初始化 [F-119]

```python
def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.process_proxy = None       # 进程代理实例
    self.response_address = None    # ResponseManager地址
    self.public_key = None          # RSA公钥
    self.sigint_value = None        # SIGINT信号值
    self.kernel_id = None           # 内核ID
    self.user_overrides = {}        # 用户覆盖的环境变量
    self.kernel_launch_timeout = 30 # 启动超时（秒）
    self.restarting = False         # 重启标志
    self.cache_ports = False        # 禁用端口缓存
```

注意 `cache_ports = False`——远程内核的端口由远端launcher分配，不能缓存。

### 配置联动 [F-120]

`_link_dependent_props()` 使用 `traitlets.directional_link` 将父app的配置单向同步到自身，共14个属性：
- 用户授权：authorized_users, unauthorized_users, impersonation_enabled
- 端口管理：port_range, max_port_range_retries
- 环境传递：client_envs, inherited_envs, kernel_headers
- 通信：response_address, public_key, socket_timeout, kernel_launch_timeout
- 其他：authorized_origin, trust_xheaders

这种单向联动确保kernel_manager始终使用最新配置。

### 启动流程 [F-121,F-126]

```
start_kernel(**kwargs)
  ├─ 获取/生成kernel_id
  ├─ _get_process_proxy()         ← 从kernelspec创建ProcessProxy实例
  ├─ _capture_user_overrides()    ← 捕获用户环境变量
  ├─ _enforce_authorization()     ← 用户授权检查
  └─ super().start_kernel()       ← AsyncIOLoopKernelManager
       ├─ format_kernel_cmd()     ← 替换命令模板占位符
       └─ _launch_kernel()
            └─ process_proxy.launch_process()
```

### _get_process_proxy 工厂方法 [F-126]

```python
def _get_process_proxy(self):
    kernelspec = self.kernel_spec
    proxy_config = get_process_proxy_config(kernelspec)
    class_name = proxy_config.get("class_name")
    proxy_class = import_item(class_name)  # 动态导入类
    return proxy_class(self, proxy_config.get("config", {}))
```

通过kernelspec的metadata.process_proxy配置确定使用哪种ProcessProxy，支持动态导入自定义类。

### 命令模板替换 [F-123]

`format_kernel_cmd(extra_arguments)` 替换kernel命令中的四个占位符：

| 占位符 | 替换为 | 说明 |
|--------|-------|------|
| `{response_address}` | `ip:port` | ResponseManager监听地址 |
| `{public_key}` | Base64 RSA公钥 | 供launcher加密连接信息 |
| `{port_range}` | `lower..upper` | 内核ZMQ端口范围 |
| `{kernel_id}` | UUID | 内核ID，用于ResponseManager路由 |

### _launch_kernel 进程启动 [F-124]

```python
async def _launch_kernel(self, kernel_cmd, **kwargs):
    env = kwargs.get("env", os.environ).copy()
    env["KERNEL_GATEWAY"] = "1"           # 标记EG环境
    env.pop("EG_AUTH_TOKEN", None)        # 防止Token泄露
    env.pop("KG_AUTH_TOKEN", None)
    kwargs["env"] = env
    return await self.process_proxy.launch_process(kernel_cmd, **kwargs)
```

关键安全措施：移除auth token环境变量，防止泄露到内核进程。

### write_connection_file 条件写入 [F-125]

本地内核场景下写connection file；远程内核场景下跳过（连接信息由launcher通过ResponseManager回传）。

### 信号处理 [F-127]

`signal_kernel(signum)` 的特殊逻辑：
- **SIGINT**（中断）：通过ZMQ interrupt模式发送（不是OS信号），支持 `EG_ALTERNATE_SIGINT` 替代信号
- **其他信号**：直接调用 `process_proxy.send_signal(signum)`

### 资源清理 [F-128,F-129]

- `cleanup()`/`cleanup_resources()`：调用 `process_proxy.cleanup()` 清理资源
- `request_shutdown(restart)`：对RemoteProcessProxy调用 `shutdown_listener()` 通知launcher退出监听线程

## new_kernel_id 自定义内核ID [F-130]

支持客户端通过 `KERNEL_ID` 环境变量指定自定义kernel_id，必须为合法UUID v4格式。这在HA场景下很有用——恢复内核时可以使用原有的kernel_id。
