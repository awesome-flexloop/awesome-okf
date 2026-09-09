---
type: bundle
title: LobsterAI Electron 桌面 AI Agent 应用
okf_version: "0.2"
---

# LobsterAI 知识库

本知识包是网易有道开源的 Electron 桌面 AI Agent 应用 [LobsterAI](https://github.com/netease-youdao/LobsterAI)（MIT 许可证）的系统化中文源码教程，基于 vendor 源码（`vendor/netease-youdao/LobsterAI`，信源基线 commit `7592cd034a7cb458a8650df0325b4980dd1bc162`，恰为 tag 2026.9.4 指向 commit）深度阅读生成。LobsterAI 以「IM 网关 + MCP 运行时 + 技能系统」为核心：产品/会话层（Cowork）把一切 Agent 执行能力委托给唯一的 Agent 运行时/网关（OpenClaw），全部状态本地优先存储于单一 SQLite 数据库，并可将同一套人机协作协议扩展到九个 IM 平台。覆盖从主进程窗口安全基线到 IPC 通道契约、从 SQLite 存储层到会话消息数据管理、从人机协作协议到 Agent 预设、MCP 桥接、技能系统与定时任务的完整知识体系。所有内容均溯源至 LobsterAI TypeScript 源码，遵循 OKF v0.2 规范，经 R→I→E→V→C 五阶段链路生成。

## 架构基础篇（concepts/）

* [全景与分层架构](concepts/00-overall-architecture.md) — Cowork（产品/会话层）与 OpenClaw（唯一 Agent 运行时/网关）的职责切分、Electron 40 + React 18 技术栈、主进程/渲染进程/共享协议层/定时任务四区布局总览。
* [主进程窗口模型与安全基线](concepts/01-main-window-security.md) — 跨平台无边框窗口外观策略、webPreferences 十项安全基线、webview 挂载时的强制偏好重写，三者构成桌面壳安全边界。
* [IPC 通道契约体系](concepts/02-ipc-channel-contracts.md) — preload 白名单式门面、按命名空间分组的 30+ IPC 通道、`as const` 常量对象契约、`cowork:stream` 流式推送事件族与 IM 平台参数化通道模式。

## 核心机制篇（concepts/）

* [SQLite 本地优先存储层](concepts/03-sqlite-local-storage.md) — SqliteStore 工厂建库、better-sqlite3 同步驱动、13 张表的五域划分、`PRAGMA table_info()` 列存在性迁移、消息级联删除与索引设计。
* [会话与消息数据管理](concepts/04-session-message-store.md) — CoworkStore 四组 40+ 方法的数据访问模式、会话 fork（含 worktree 模式）元数据、分页与搜索计数成对策略、连续性胶囊用途。
* [人机协作四类协议](concepts/05-human-collab-protocols.md) — btw（打断提问）/goal（持续目标）/rail（轨道索引）/steer（流内纠偏）四类协作协议的状态枚举、限长常量、多模态请求负载与 AskUser 权限通道。

## 高级功能篇（concepts/）

* [Agent 与预设体系](concepts/06-agent-preset-system.md) — AgentManager 对 CoworkStore 的委托模式、agents 表 20 列（含 JSON 存储的 skill_ids）、内置预设 Agent 的查询与添加流程。
* [MCP 集成与桥接运行时](concepts/07-mcp-integration-runtime.md) — McpStore → mcpLaunchResolution → McpRuntime + McpBridgeServer 三级结构、launch resolution（来源指纹/npx 判定）、AskUser/媒体生成/浏览器工具三类桥接工具协议。
* [多平台 IM 网关](concepts/08-im-gateway.md) — IMGatewayManager 九平台实例管理与连通性测试、NimGateway 消息方法族、QQ 媒体下载限额与清理策略、扫码登录与配对审批通道。
* [技能系统与注册机制](concepts/09-skill-system.md) — SKILL.md 单文件技能约定、skills.config.json 注册表（order/enabled）、SkillManager 同步/下载/升级/自动路由全生命周期、目录计数与注册表计数互相校验的一致性机制。
* [定时任务子系统](concepts/10-scheduled-tasks.md) — Renderer → Main → OpenClaw Gateway 三层架构、15 秒轮询对账模型、Schedule/Payload 判别联合、投递/会话/唤醒三组正交旋钮与四组网关映射函数。

## 实战示例（examples/）

* [开发一个自定义 SKILL](examples/custom-skill-development.md) — 按 SKILL.md 单文件约定创建技能、注册到 skills.config.json 式注册表、经 SkillManager 同步与自动路由接入 Agent 的完整演练。
* [通过 IPC 通道查询会话消息](examples/query-session-messages-ipc.md) — 渲染层经 `cowork:session:*` 通道分页拉取会话列表与消息历史、订阅 `cowork:stream:*` 流式事件、以 CoworkStore 方法面理解主进程侧数据出口。
* [定时任务配置与投递流程](examples/scheduled-task-delivery.md) — 创建 cron 定时 Agent turn 任务、配置投递/会话/唤醒三组旋钮、经 CronJobService 轮询对账并把结果投递到 IM 会话的完整链路。

## 信源登记簿（references/）

* [LobsterAI 源码事实清单](references/facts.md) — R 阶段产物：74 条编号事实（F-la-001~074）按子系统组织，全部陈述直接来自 vendor 源码阅读，证据位置逐条标注。
* [LobsterAI 架构洞察](references/insights.md) — I 阶段产物：基于 F-la-001~074 提炼的 5 条架构核心洞察，采用「陈述+证据+反常识+行动」四元组结构，证据全部锚定编号事实。
* [LobsterAI 信源登记](references/sources.md) — 上游信源、固定基线（2026.9.4 @ 7592cd0）、许可证与关键信源文件清单，供事实回溯与基线复验使用。

## 信任与生命周期说明

* **status 判定依据**：全部 14 个内容文档（11 个概念 + 3 个示例）均 `status: stable`，内容基于对 LobsterAI 源码（`src/main/`、`src/shared/cowork/`、`src/scheduledTask/` 等目录）的逐文件阅读与事实提取（74 条源码事实 F-la-001~074），经 R→I→E→V→C 五阶段流程生成，`verified.by` 为 `process:vendor-grep`。
* **stale_after 解释**：14 个内容文档统一设置为 `2027-09-09`。LobsterAI 2026.9.4 基线的核心架构（Cowork/OpenClaw 分工、IPC 契约、SQLite 本地优先存储、四类人机协作协议）在 tag 2026.9.4 内自洽稳定；该日期作为针对上游大版本升级的保守重新评估节点。
* **references/ 三篇 spec 文档**（facts.md、insights.md、sources.md）为 R/I 阶段过程产物，frontmatter 未设 status/stale_after 字段，其有效性以固定基线 `7592cd034a7cb458a8650df0325b4980dd1bc162` 与 sources.md 的复验流程为准。
* **核验链路**：`generated.at` 记录各文档原始生成时刻（2026-09-09T10:00:00+08:00）；`verified.at` 记录 V 阶段 vendor-grep 对抗验证事件，两者分离、可追溯。

本知识包共收录 14 个内容文档（11 个概念 + 3 个示例），另含 3 个子目录 index.md、3 个 spec 文档（facts/insights/sources）与根 index.md、log.md。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
