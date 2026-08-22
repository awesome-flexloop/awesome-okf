---
okf_version: "0.2"
type: "concept"
title: "会话管理与持久化"
description: "SessionManager内存会话、KernelSessionManager持久化抽象、File/Webhook后端实现、HA模式下的会话恢复"
tags: [session, persistence, high-availability, file-session, webhook, recovery]
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
sources:
  - id: session-source
    resource: "/references/session-manager-source.md"
    title: "会话管理源码"
---

# 会话管理与持久化

Enterprise Gateway提供两层会话管理：内存中的SessionManager和可持久化的KernelSessionManager。后者是实现高可用（HA）的关键基础。

## 两层会话架构

```
┌─────────────────────────────────────────┐
│         HTTP API (SessionHandler)        │
├─────────────────────────────────────────┤
│         SessionManager (内存)            │  ← Jupyter Server标准
│         _sessions = []                  │
├─────────────────────────────────────────┤
│     KernelSessionManager (持久化)        │  ← EG扩展
│     ┌──────────────┬─────────────────┐  │
│     │FileKernelSess│WebhookKernelSes │  │
│     │ionManager    │sionManager      │  │
│     └──────────────┴─────────────────┘  │
└─────────────────────────────────────────┘
```

## SessionManager 内存会话 [F-147~F-152]

SessionManager是Jupyter Server标准的会话管理器，EG扩展了它以支持持久化。

### 数据结构 [F-148]

```python
_sessions = []  # list of dicts
_columns = ["session_id", "path", "kernel_id"]
```

每个session是一个字典：`{"session_id": uuid, "path": notebook_path, "kernel_id": uuid}`。

### 核心方法

| 方法 | 说明 |
|------|------|
| `create_session(path, kernel_name, kernel_id)` | 创建session：生成session_id→启动kernel→保存→返回model |
| `get_session(**kwargs)` | 按列查找session，找不到返回404 |
| `row_to_model(row)` | 转换为API模型格式，kernel不存在则自动清理失效session |
| `delete_session(session_id)` | 删除session：查找→关闭kernel→从_sessions移除 |
| `save_session(session_id, kernel_id, **kwargs)` | 创建或更新session条目 |

### API模型格式 [F-151]

```python
{
    "id": session_id,
    "notebook": {"path": path},
    "kernel": {
        "id": kernel_id,
        "name": kernel_name,
        "last_activity": "...",
        "connections": 0,
        "execution_state": "idle"
    }
}
```

`row_to_model()`的一个重要特性：如果kernel已不存在（进程崩溃或EG重启），会自动从_sessions中移除该条目并raise KeyError，避免返回无效session。

## KernelSessionManager 持久化会话 [F-153~F-159]

KernelSessionManager是EG新增的持久化层，用于在EG重启或多实例部署时恢复内核状态。

### 配置项 [F-157]

- `enable_persistence`（Bool）：是否启用持久化
- `kernel_session_manager_class`：持久化后端类，默认 `FileKernelSessionManager`

### 接口定义 [F-156]

```python
class KernelSessionManager(LoggingConfigurable):
    def create_session(self, kernel_id, **kwargs): ...    # 创建会话记录
    def delete_session(self, kernel_id): ...              # 删除会话记录
    def load_session(self, kernel_id): ...                # 加载单个会话
    def start_session(self, kwargs): ...                  # 从会话恢复启动内核
    def refresh_session(self, kernel_id): ...             # 刷新会话状态
    def active_sessions(self, username): ...              # 用户活跃会话数
    def start_sessions(self): ...                         # 批量恢复（standalone启动时）
    def get_kernel_username(**kwargs): ...                # 提取用户名（静态方法）
```

### 用户名提取 [F-158]

`get_kernel_username()` 静态方法从以下位置提取用户名：
1. 请求kwargs中的env.KERNEL_USERNAME
2. 环境变量KERNEL_USERNAME
3. 当前系统用户（`pwd.getpwuid(os.getuid())` 或 `getpass.getuser()`）

## FileKernelSessionManager 文件持久化 [F-154]

默认持久化后端，将会话数据存储到本地文件系统。

### 存储位置

存储在Jupyter runtime目录（通常是 `~/.local/share/jupyter/runtime/`）下的session子目录，每个kernel_id对应一个JSON文件。

### 存储内容

每个session JSON文件包含：
```json
{
  "kernel_id": "<UUID>",
  "kernel_name": "python_kubernetes",
  "path": "/notebooks/test.ipynb",
  "username": "alice",
  "process_info": {
    "pid": 12345,
    "pgid": 12345,
    "ip": "192.168.1.100"
  },
  "connection_info": {
    "shell_port": 40001,
    "iopub_port": 40002,
    "stdin_port": 40003,
    "hb_port": 40004,
    "control_port": 40005,
    "ip": "192.168.1.100",
    "key": "...",
    "transport": "tcp",
    "signature_scheme": "hmac-sha256"
  }
}
```

- `process_info`：进程信息，用于恢复ProcessProxy状态（pid/pgid/ip）
- `connection_info`：ZMQ连接信息，用于重建ZMQ连接

### 工作方式

- **create_session**：内核启动成功后，将session数据写入JSON文件
- **delete_session**：内核关闭时删除对应JSON文件
- **load_session**：读取JSON文件返回session数据
- **start_sessions**：遍历所有session文件，逐个调用start_session恢复内核
- **start_session**：调用RemoteMappingKernelManager.start_kernel_from_session()恢复

## WebhookKernelSessionManager Webhook持久化 [F-155]

通过HTTP webhook回调将会话状态持久化到外部服务。

### 工作方式

- `create_session` → POST到webhook URL
- `delete_session` → DELETE到webhook URL/kernel_id
- `load_session` → GET从webhook URL/kernel_id
- `active_sessions` → GET查询用户活跃会话数

适用于将会话状态存储到Redis、数据库、etcd等外部存储的场景，支持多EG实例共享会话状态（配合replication模式）。

## HA模式与持久化联动 [F-027,F-028,F-044]

EG的HA模式依赖持久化会话，两者自动联动：

```python
# 自动联动逻辑
if self.availability_mode is None and self.enable_persistence:
    # 仅启用持久化→自动设为replication模式
    self.availability_mode = "replication"
elif self.availability_mode is not None and not self.enable_persistence:
    # 启用HA模式→自动启用持久化
    self.enable_persistence = True
```

### standalone模式 [F-028]

- **启动时全量恢复**：EG启动时调用 `start_sessions()` 遍历所有持久化session
- 对每个session：构造KernelManager → 创建ProcessProxy → load_process_info → poll确认存活 → 重建ZMQ连接
- 适用于单实例部署（EG重启后自动恢复所有内核）
- 启动时间取决于持久化内核数量

### replication模式 [F-115,F-116]

- **访问时懒加载恢复**：不主动恢复所有内核
- 当请求到达一个不在内存中的kernel_id时：
  - `check_kernel_id(kernel_id)` 发现内核不存在
  - 调用 `_refresh_kernel(kernel_id)`
  - load_session → start_kernel_from_session恢复内核
  - 恢复成功后继续处理请求
- 适用于多EG实例部署（如K8s多副本）
- 任何一个EG实例都可以处理任何内核的请求，内核在首次被访问时恢复到该实例

### 内核恢复流程 [F-114]

`start_kernel_from_session()` 的恢复步骤：
1. 构造RemoteKernelManager实例（不启动新进程）
2. 加载kernelspec
3. 创建对应类型的ProcessProxy实例
4. 调用 `process_proxy.load_process_info(process_info)` 恢复pid/pgid/ip
5. 轮询 `process_proxy.poll()` 确认进程仍存活（poll返回None=存活）
6. 设置 `kernel_manager.kernel = process_proxy`（将process_proxy作为kernel属性）
7. 恢复connection_info到kernel_manager
8. 重建SSH隧道（如果是远程内核）
9. 启动kernel restarter和activity watching

如果poll发现进程已退出，恢复失败，清理session记录。

## KernelSpecCache 内核规范缓存 [F-160,F-161]

虽然不属于会话管理，但KernelSpecCache与会话管理紧密配合，是EG启动时初始化的核心组件之一。

- 单例模式（SingletonConfigurable），缓存所有kernelspec到内存
- 启动时扫描kernelspec目录加载全部spec
- 使用watchdog库的FileSystemEventHandler监控目录变化
- 文件创建/修改/删除时自动刷新缓存
- 无需重启EG即可加载新内核或更新现有内核配置
