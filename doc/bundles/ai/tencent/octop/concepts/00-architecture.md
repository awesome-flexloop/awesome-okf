---
type: Concept
title: "Octop 四层架构与依赖禁令"
description: "Octop 的 dashboard→api→infra→utils 四层架构、依赖方向禁令、launch.py 独占组合根、单进程 asyncio 模型。"
tags: [octop, architecture, layers, dependency-injection, composition-root]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/harness-stack.md
    title: Harness 技术栈与模块边界
  - id: launch
    resource: /references/server-launch.md
    title: 服务器启动与组合根
---

# Octop 四层架构与依赖禁令

Octop 是一个自托管的多用户、多 Agent AI 助手平台，以单个 Python wheel 分发，包含 FastAPI 后端、React Dashboard 和 Click CLI（F-015）。其架构遵循严格的分层依赖规则。

## 四层架构

```
┌─────────────────────────────────────────────┐
│  dashboard/  (React 18 + TS + Vite + AntD)  │  ← 浏览器
└──────────────────┬──────────────────────────┘
                   │ HTTP / WebSocket
┌──────────────────▼──────────────────────────┐
│  api/  (FastAPI routers, middleware, auth)  │  ← 传输适配层
└──────────────────┬──────────────────────────┘
                   │ 函数调用
┌──────────────────▼──────────────────────────┐
│  infra/  (agents, gateway, db, cron, ...)   │  ← 领域核心
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  infra/utils/  (paths, ulid, env, locale)   │  ← 纯工具
│  octop.config  (OctopConfig frozen dataclass)│
└─────────────────────────────────────────────┘
```

| 层 | 目录 | 职责 | 可导入 |
|----|------|------|--------|
| Dashboard | `dashboard/` | React SPA | 仅通过 `/api` HTTP |
| API | `src/octop/api/` | HTTP 路由、JWT 认证、SSE、OpenAPI | `infra/`、`octop.config`、同级 `api/*` |
| 领域 | `src/octop/infra/` | 业务逻辑与编排 | `infra/utils/`、`infra/db/`、`octop.config`、同级 `infra/*` |
| 工具 | `src/octop/infra/utils/` | 纯辅助函数 | stdlib、第三方库 |

CLI 层（`src/octop/cli/`）位于侧路，通过 `launch.py` 启动服务器或直接操作 `infra/`，不得导入 `api/`（F-129）。

## 依赖方向硬禁令

架构通过以下硬禁令保证领域层不感知传输层（F-129）：

1. **`infra/` 不得导入 `api/`、`cli/`、`launch.py`** — 领域代码不能知道 HTTP 或 CLI 的存在
2. **`api/` 不得导入 `cli/`、`launch.py`** — HTTP 层不能反向引用 CLI
3. **`cli/` 不得导入 `api/`** — CLI 通过 `launch.py` 启动服务器，不直接引用 FastAPI
4. **`infra/db/repos/` 不得导入非 DB `infra` 包** — Repository 只做 SQL，不编排
5. **`infra/utils/` 不得导入非 utils `infra` 包** — 工具函数保持纯净无副作用
6. **Routers 必须保持薄**：校验 HTTP → 调用 `infra/` → 映射错误，不包含领域规则

这些禁令使同一领域核心可以被 HTTP、CLI、ACP stdio 三种传输层复用。

## 组合根：launch.py 独占

`launch.py` 是整个系统中**唯一**同时导入 `infra/server` 和 `api/app` 的模块（F-029、F-130）：

```python
# launch.py
from octop.infra.server import OctopServer
from octop.api.app import build_app

async def run_foreground(...):
    srv = OctopServer()
    await srv.start()
    app = build_app(srv)
    # uvicorn serve(app)
    await srv.stop()
```

这种独占设计意味着：
- `build_app(server)` 接收已构造的 `OctopServer`，自身不初始化任何领域服务
- CLI embedded 模式（`octop acp`、`chats repl`）可以独立构造 `OctopServer` 而不经过 FastAPI
- 测试可以直接构造 `OctopServer` 或 FastAPI app，无需完整启动

## 单进程 asyncio 模型

Octop 采用单进程、单 asyncio 事件循环模型承载所有用户和 Agent（I-05）：

- 无外部队列、无 Redis、无强制微服务（F-015）
- 所有 Agent 实例在同一进程内由 `HarnessAgentManager` 管理
- 所有 IM 通道在同一进程内由 `ChannelManager` 管理
- 定时任务由 `CronManager` 在同一事件循环中调度
- 阻塞 I/O 通过 `run_in_executor` 卸载到线程池（F-131 禁止在 async 函数中做阻塞 I/O）

这种设计降低了部署复杂度（`pip install octop && octop run` 即可），但要求 Agent 间通过 SecurityPolicy 和 guardrails 逻辑隔离而非 OS 级隔离。

## 配置即数据

所有配置通过 frozen dataclass 表达（F-016~F-019）：

- `OctopConfig` 是不可变值对象，从 `config.json` + 环境变量合并加载
- 配置变更需要重启或通过 setup wizard 热绑定
- `DatabaseConfig` 支持 SQLite 和 PostgreSQL 两种驱动，通过同一 Protocol 抽象

## DI 容器：SharedServices

依赖注入通过 `SharedServices` frozen dataclass 手动组装，无 IoC 框架（参见 [/concepts/04-db-di.md](04-db-di.md)）。Routers 通过 `Depends(get_server)` 获取 `OctopServer`，再访问 `server.services`。

## 相关概念

- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)
- [/concepts/04-db-di.md](04-db-di.md)
- [/concepts/06-cli-commands.md](06-cli-commands.md)
