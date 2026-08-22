---
type: Reference
title: JupyterHub Spawner 源码参考
description: Spawner 基类及 LocalProcessSpawner 的 API 参考——服务器生命周期、配置项和状态管理
tags: [spawner, server, lifecycle, process, spawn]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T21:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T21:00:00+08:00" }
status: stable
stale_after: "2027-08-22"
sources:
  - id: spawner-source
    resource: https://github.com/jupyterhub/jupyterhub/blob/main/jupyterhub/spawner.py
    title: jupyterhub/spawner.py
---

# Spawner 源码参考

## Spawner 基类

继承自 `traitlets.config.LoggingConfigurable`。

### 核心配置 Traitlets

| Traitlet | 类型 | 默认值 | 说明 |
|----------|------|--------|------|
| `cmd` | Command | `['jupyterhub-singleuser']` | 启动单用户服务器的命令 |
| `args` | List(Unicode) | `[]` | 传递给单用户服务器的参数 |
| `env` | Dict | `{}` | 额外环境变量 |
| `env_keep` | List | `['PATH','PYTHONPATH','CONDA_ROOT','VIRTUAL_ENV','LANG','LC_ALL']` | 保留的父进程环境变量 |
| `notebook_dir` | Unicode | `''` | 笔记本目录（已迁移为 `notebook_dir`） |
| `default_url` | Unicode | `''` | 服务器启动后的默认 URL |
| `api_token` | Unicode | 自动生成 | Hub API 访问 token |
| `oauth_client_id` | Unicode | 自动生成 | OAuth 客户端 ID |
| `start_timeout` | Integer | `60` | 启动超时（秒） |
| `http_timeout` | Integer | `30` | HTTP 请求超时（秒） |
| `poll_interval` | Integer | `30` | 服务器状态轮询间隔（秒） |
| `pid` | Integer | `0` | 单用户服务器进程 ID |
| `options_form` | Unicode | `''` | Spawn 选项表单（HTML） |
| `c.I*` | | | 配置文件中使用 `c.Spawner.xxx` 设置 |

### 生命周期状态

```
  (stopped)
      │ start()
      ▼
  (starting) ──start_timeout──→ (failed)
      │
      ▼
  (running) ──poll()──→ (stopped)
      │ stop()
      ▼
  (stopping)
```

### 核心方法

| 方法 | 签名 | 说明 |
|------|------|------|
| `start` | `async () → (ip, port)` | 启动单用户服务器，返回 (ip, port) |
| `stop` | `async (now=False)` | 停止单用户服务器 |
| `poll` | `async () → int/None` | 检查进程状态，返回退出码或 None（运行中） |
| `get_state` | `async () → dict` | 获取可序列化状态（用于 DB 持久化） |
| `load_state` | `(state)` | 从持久化状态恢复 |
| `clear_state` | `()` | 清除状态 |
| `get_env` | `() → dict` | 获取环境变量 |
| `get_args` | `() → list` | 获取命令行参数 |
| `progress` | `async () → dict` | SSE 启动进度事件生成器 |
| `options_from_form` | `(form_data) → dict` | 解析 options 表单数据 |
| `run_pre_spawn_hook` | `async ()` | 执行 pre_spawn_hook |
| `run_post_stop_hook` | `async ()` | 执行 post_stop_hook |

### SpawnException

v6.0 新增的异常类，用于策略性阻止 spawn：

```python
raise SpawnException(
    "Server is full",
    reason="capacity",           # 短标签，用于 metrics
    log_message="详细日志",       # 仅记录日志，不展示用户
    message_html="<b>...</b>",   # HTML 格式消息
    status_code=503              # HTTP 状态码
)
```

## LocalProcessSpawner

继承自 `Spawner`，默认 Spawner 实现。

- 在本地系统上以子进程方式启动单用户服务器
- 使用 `subprocess.Popen` 创建进程
- 通过 PID 管理进程生命周期
- `make_preexec_fn()` 创建用户切换函数（setuid/setgid）
- 适用于单机部署场景

## SimpleLocalProcessSpawner

继承自 `LocalProcessSpawner`，简化版本地进程 Spawner。

- 不做用户切换，直接以 Hub 进程的用户身份运行
- 适用于测试和简单部署
