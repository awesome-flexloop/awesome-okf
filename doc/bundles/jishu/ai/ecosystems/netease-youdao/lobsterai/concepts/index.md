# 概念文档

LobsterAI 核心架构概念，共 11 篇，按依赖顺序组织：先建立产品层与运行时分工、IPC 契约与存储基座，再展开人机协作协议与 Agent/MCP/IM/技能/定时任务五大高级子系统。

## 架构基础

* [00 全景与分层架构](00-overall-architecture.md) — Cowork 与 OpenClaw 的职责切分、Electron 40 + React 18 技术栈、主进程/渲染进程/共享协议层/定时任务四区布局。
* [01 主进程窗口模型与安全基线](01-main-window-security.md) — 跨平台无边框窗口外观、webPreferences 十项安全基线、webview 强制偏好重写的桌面壳安全边界。
* [02 IPC 通道契约体系](02-ipc-channel-contracts.md) — preload 白名单门面、30+ 命名空间分组通道、`as const` 契约、cowork:stream 流式事件族、IM 参数化通道。

## 核心机制

* [03 SQLite 本地优先存储层](03-sqlite-local-storage.md) — SqliteStore 工厂建库、better-sqlite3 同步驱动、13 张表五域划分、PRAGMA 列存在性迁移、级联删除与索引。
* [04 会话与消息数据管理](04-session-message-store.md) — CoworkStore 四组 40+ 方法、会话 fork（含 worktree）元数据、分页搜索计数成对、resetRunningSessions 运行态恢复。
* [05 人机协作四类协议](05-human-collab-protocols.md) — btw/goal/rail/steer 四类协作协议的状态枚举、限长常量、多模态请求负载与 AskUser 权限通道。

## 高级功能

* [06 Agent 与预设体系](06-agent-preset-system.md) — AgentManager 委托模式、agents 表 20 列、JSON 存储 skill_ids、内置预设 Agent 查询与添加流程。
* [07 MCP 集成与桥接运行时](07-mcp-integration-runtime.md) — 存储/解析/运行时三级结构、launch resolution、AskUser/媒体生成/浏览器工具三类桥接协议。
* [08 多平台 IM 网关](08-im-gateway.md) — 九平台实例管理与连通性测试、NimGateway 消息方法族、QQ 媒体限额清理、扫码登录与配对审批。
* [09 技能系统与注册机制](09-skill-system.md) — SKILL.md 单文件技能约定、skills.config.json 注册表、SkillManager 全生命周期、目录与注册表计数互相校验。
* [10 定时任务子系统](10-scheduled-tasks.md) — 三层架构、15 秒轮询对账、Schedule/Payload 判别联合、投递/会话/唤醒三组旋钮与网关映射函数。

```{toctree}
:hidden:
:maxdepth: 7

00-overall-architecture
01-main-window-security
02-ipc-channel-contracts
03-sqlite-local-storage
04-session-message-store
05-human-collab-protocols
06-agent-preset-system
07-mcp-integration-runtime
08-im-gateway
09-skill-system
10-scheduled-tasks
```
