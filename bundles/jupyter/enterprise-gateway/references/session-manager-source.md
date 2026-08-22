---
type: Reference
title: "会话管理与KernelSpec缓存源码"
description: "SessionManager内存会话、KernelSessionManager持久化会话（File/Webhook后端）、KernelSpecCache带文件监控的缓存"
tags: [session, persistence, file-session, webhook, kernelspec-cache, watchdog]
sources:
  - id: sessionmanager
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/sessionmanager.py"
    title: "services/sessions/sessionmanager.py"
  - id: kernelsession
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/kernelsessionmanager.py"
    title: "services/sessions/kernelsessionmanager.py"
  - id: session-handlers
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/sessions/handlers.py"
    title: "services/sessions/handlers.py"
  - id: kernelspec-cache
    resource: "../../../../../external/libs/jupyter/enterprise_gateway/enterprise_gateway/services/kernelspecs/kernelspec_cache.py"
    title: "services/kernelspecs/kernelspec_cache.py"
generated: { by: "reference_agent/trae-cn", at: "2026-08-22T14:40:00Z" }
status: stable
stale_after: 2027-12-31
---

# 会话管理与KernelSpec缓存源码

本信源登记会话管理体系和KernelSpec缓存的源码。

## SessionManager 内存会话 [F-147~F-152]

继承 `LoggingConfigurable`，管理内存中的session记录。

### 数据结构 [F-148]

```python
class SessionManager(LoggingConfigurable):
    _sessions = []  # list of dicts
    _columns = ["session_id", "path", "kernel_id"]
```

每个session条目为字典：`{"session_id": uuid, "path": str, "kernel_id": str}`。

### 核心方法

| 方法 | 行为 |
|------|------|
| `create_session(path, kernel_name, kernel_id)` | 生成session_id→启动kernel→save→返回model |
| `get_session(**kwargs)` | 按列查询，找不到则raise HTTPError(404) |
| `row_to_model(row)` | 转换为API模型格式，kernel不存在则从_sessions移除并raise KeyError |
| `delete_session(session_id)` | 查找session→shutdown_kernel→从_sessions移除 |
| `save_session(session_id, kernel_id, **kwargs)` | 创建或更新session条目 |

row_to_model返回的模型格式 [F-151]：
```python
{
    "id": session_id,
    "notebook": {"path": path},
    "kernel": kernel_model  # 通过kernel_manager.kernel_model获取
}
```

## KernelSessionManager 持久化会话基类 [F-153,F-156,F-157,F-158]

继承 `LoggingConfigurable`，定义持久化会话的抽象接口。

### 配置项 [F-157]

- `enable_persistence`（Bool）：是否启用会话持久化

### 抽象/可覆写接口 [F-156]

| 方法 | 行为 |
|------|------|
| `create_session(kernel_id, **kwargs)` | 创建持久化会话记录 |
| `delete_session(kernel_id)` | 删除会话记录 |
| `load_session(kernel_id)` | 加载单个会话数据 |
| `start_session(kwargs)` | 从会话数据恢复启动内核 |
| `refresh_session(kernel_id)` | 刷新会话状态（replication模式） |
| `active_sessions(username)` | 返回用户活跃会话数 |
| `start_sessions()` | 批量恢复所有会话（standalone模式启动时调用） |

### get_kernel_username 用户名提取 [F-158]

静态方法，从环境变量和kwargs中提取KERNEL_USERNAME，默认返回当前系统用户（通过 `pwd.getpwuid(os.getuid())` 或Windows `getpass.getuser()`）。

## FileKernelSessionManager 文件持久化 [F-154]

继承 `KernelSessionManager`，使用文件系统存储会话数据。

会话文件存储在 `runtime_dir` 下的session目录，每个kernel_id对应一个JSON文件，包含：
- kernel_id
- kernel_name
- path
- username
- process_info（pid/pgid/ip，用于进程恢复）
- connection_info（ZMQ连接信息）

## WebhookKernelSessionManager Webhook持久化 [F-155]

继承 `KernelSessionManager`，通过HTTP webhook回调实现会话持久化：
- create_session → POST webhook
- delete_session → DELETE webhook
- load_session → GET webhook
- active_sessions → GET webhook查询

适用于将会话状态存储到外部服务（如Redis、数据库等）的场景。

## SessionRootHandler [F-142]

Session handlers采用与kernel handlers相同的动态Mixin替换机制，遍历Jupyter Server的default_handlers动态创建混入三个Mixin的Handler类。

| 路径 | 方法 | 说明 |
|------|------|------|
| `/api/sessions` | GET | 列出所有session |
| `/api/sessions` | POST | 创建新session（创建内核） |
| `/api/sessions/{session_id}` | GET | 查询session |
| `/api/sessions/{session_id}` | PATCH | 更新session（如重连） |
| `/api/sessions/{session_id}` | DELETE | 删除session（关闭内核） |

## KernelSpecCache 内核规范缓存 [F-160,F-161]

继承 `SingletonConfigurable`，提供kernelspec缓存及自动刷新。

### 缓存机制

- 启动时扫描所有kernelspec目录，加载全部kernelspec到内存缓存
- 缓存结构：`{name: kernelspec_dict}`
- 提供 `get_all_specs()` 和 `get_kernel_spec(name)` 方法

### 文件监控自动刷新 [F-161]

内部类 `KernelSpecChangeHandler` 继承 `FileSystemEventHandler`（watchdog库）：
- 监听kernelspec目录的文件系统事件（创建/修改/删除）
- 检测到变化时自动刷新缓存
- 无需重启即可加载新的kernelspec或更新现有kernelspec
