---
type: spec
scope: opencode
name: insights
version: "0.1.0"
source: local
description: "OpenCode 源码架构洞察，基于事实清单的深度分析"
---

# OpenCode 架构洞察

## 洞察一：V2 会话核心采用"持久化录入与执行分离"架构

**陈述**：OpenCode V2 会话引擎将用户输入的持久化录入（durable admission）与模型执行（model execution）严格解耦。`SessionV2.prompt()` 先写入一条持久化的 `session_input` 行，再通过 `SessionExecution.wake(sessionID)` 发起建议性执行唤醒。执行器在安全边界（safe provider-turn boundary）将已录入输入提升为可见的用户消息。

**证据**：
- `specs/v2/session.md:5-20` 定义了 `sessions.prompt` 的录入语义和 `resume` 参数
- `AGENTS.md:153` 明确"Keep durable prompt admission separate from model execution"
- `specs/v2/session.md:35` 描述 `session_input` 作为持久化录入收件箱，`PromptAdmitted` 事件在 `Prompted` 事件前发布
- `specs/v2/session.md:155-164` 区分了 `steer`（立即提升）和 `queue`（空闲时提升）两种投递模式

**反常识**：传统 AI agent 框架通常将用户输入直接送入模型调用循环。OpenCode 反向而行——输入先落库为"待处理"状态，再由独立的协调器异步调度。这意味着即使进程崩溃，已录入的 prompt 也不会丢失（但崩溃后的自动续跑尚未实现，见 `specs/v2/session.md:104`）。

**行动**：理解 OpenCode 会话行为时，应区分"已录入"（admitted）和"已提升"（promoted）两个状态。调试会话无响应时，先检查输入是否停留在 inbox 中未被提升。

## 洞察二：多运行时条件导入与严格的包依赖方向

**陈述**：OpenCode 通过 Bun 的条件导入（conditional imports）机制在 Bun 和 Node 双运行时间切换 SQLite、PTY、文件系统等底层实现，同时强制执行严格的包间依赖方向：Schema → Core/Protocol → Server，Client 永不依赖 Core/Server。

**证据**：
- `packages/core/package.json:25-40` 定义了 `#sqlite`、`#pty`、`#fff` 三个条件导入，各有 bun/node 实现
- `packages/opencode/package.json:24-29` 定义了 `#db` 条件导入
- `AGENTS.md:3` 明确依赖方向规则
- `AGENTS.md:2` 要求修改 HttpApi 后必须从 `packages/client` 重新生成，不可手编 generated 代码
- `package.json:7` 固定包管理器为 `bun@1.3.14`

**反常识**：项目虽以 Bun 为主要运行时（CLI、TUI、构建工具），但 Core 包仍保留完整的 Node.js 条件导入路径。这表明 OpenCode 的嵌入式 SDK（`sdk-next`）需要在纯 Node 环境中运行，不能假设 Bun API 可用。

**行动**：在 Core 层编写代码时，不可直接使用 `Bun.file()` 等 Bun 专有 API（AGENTS.md 风格指南中的 Bun API 建议主要针对 opencode 主包）。跨运行时代码应通过 `#sqlite`/`#pty`/`#fff` 条件导入抽象。

## 洞察三：V2 配置系统正在进行大规模重命名与结构重组

**陈述**：V2 配置规范对旧版配置进行了系统性重命名——几乎所有集合类型字段从单数改为复数（`provider`→`providers`、`agent`→`agents`、`plugin`→`plugins`、`permission`→`permissions`、`snapshot`→`snapshots`、`attachment`→`attachments`），且不提供兼容别名。多个旧字段被直接移除（`logLevel`、`server`、`command`、`small_model`、`tools`、`default_agent`、`mode`）。

**证据**：
- `specs/v2/config.md:92` plugin → plugins
- `specs/v2/config.md:175,206` provider → providers，无兼容别名
- `specs/v2/config.md:248` agent → agents
- `specs/v2/config.md:294` permission → permissions
- `specs/v2/config.md:33-34` logLevel 和 server 被标记为 remove
- `specs/v2/config.md:43` command 被移除，功能由 skills 替代
- `specs/v2/config.md:16` V2 仅发现 `opencode.json`/`opencode.jsonc`，不支持旧版 `config.json`

**反常识**：与多数项目追求向后兼容不同，OpenCode V2 明确拒绝为旧版配置键提供别名或迁移垫片（`specs/v2/config.md:206`："v2 does not add a compatibility alias while its configuration surface is still being defined"）。这是因为 V2 尚未稳定，团队选择在定型前清除技术债。

**行动**：编写 V2 配置文件时，直接使用复数字段名。参考 `specs/v2/config.md` 中的 jsonc 示例。旧版配置文档和教程不适用于 V2。当前 `.opencode/opencode.jsonc` 仍使用旧版单数格式（`provider`、`permission`），说明 V2 配置迁移尚未在项目自身完成。

## 洞察四：混合云部署——Cloudflare 为主，AWS 为数据湖

**陈述**：OpenCode 的生产基础设施采用混合云架构：面向用户的 API、Web、Console、Auth 全部部署在 Cloudflare（Workers、KV、R2/Bucket、StaticSite），而数据分析湖（Lake）使用 AWS S3 Tables + Iceberg + Kinesis Firehose + Athena + ECS。SST 作为统一 IaC 层同时编排两个云厂商。

**证据**：
- `infra/app.ts:13` API 为 `sst.cloudflare.Worker`
- `infra/app.ts:52` 文档站为 `sst.cloudflare.x.Astro`
- `infra/app.ts:62` Web 应用为 `sst.cloudflare.StaticSite`
- `infra/console.ts:63` Auth 为 Cloudflare Worker
- `infra/console.ts:248` Console 为 `sst.cloudflare.x.SolidStart`
- `infra/lake.ts:16` 数据湖为 `aws.s3tables.TableBucket`（Iceberg 格式）
- `infra/lake.ts:160` Firehose 摄入流目标为 Iceberg
- `infra/lake.ts:218` 摄入服务为 `sst.aws.Service`（ECS/Fargate）
- `sst.config.ts:10-27` 同时配置 Cloudflare home 和 AWS/Stripe/PlanetScale provider
- `infra/stage.ts:9` `deployAws` 仅在 production 和 dev 阶段为 true

**反常识**：Cloudflare Workers 本身已具备 Durable Objects 和 SQLite 能力，但 OpenCode 选择将数据分析负载放在 AWS，原因在于 AWS S3 Tables + Athena 提供了成熟的 Iceberg 表格式和 SQL 查询能力，而 Cloudflare 在此领域尚无等价服务。此外，AWS 部署仅限 production/dev 阶段，个人开发者阶段不部署数据湖。

**行动**：本地开发时关注 Cloudflare 资源即可。数据湖相关功能（stats sync、lake ingest）需要 AWS 凭证且仅在 production/dev 阶段激活。Athena 查询设置了 2TB 扫描上限以控制成本（`infra/lake.ts:73`）。
