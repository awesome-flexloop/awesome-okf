---
type: Concept
title: 部署与基础设施
description: OpenCode 的 SST 部署架构、GitHub Action 集成、AWS 数据湖（Lake）和阶段环境管理
tags: [deployment, sst, cloudflare, aws, github-action, data-lake, staging]
generated:
  by: "reference_agent/trae-cn"
  at: 2026-08-23T10:00:00+08:00
verified:
  by: "process:grep-verification"
  at: 2026-08-23T10:00:00+08:00
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# 部署与基础设施

OpenCode 使用 SST（Serverless Stack）4.13.1 作为基础设施即代码框架，统一编排 Cloudflare 和 AWS 两朵云的资源。

## SST 配置入口

`sst.config.ts` 是部署配置入口：

- **应用名称**：`opencode`
- **移除策略**：生产环境 `retain`（保留资源），其他环境 `remove`
- **保护**：生产阶段启用保护（`protect: ["production"]`）
- **Home**：`cloudflare`（默认部署目标）
- **Providers**：
  - AWS 7.30.0，区域 us-east-1，使用 named profile（opencode-production / opencode-dev）
  - Stripe 0.0.28
  - Random 4.19.2
  - PlanetScale 0.4.1
  - Honeycomb 0.49.0

运行时按阶段条件导入基础设施模块：

```ts
async run() {
  const stage = await import("./infra/stage.js")
  await import("./infra/app.js")
  const lake = stage.deployAws ? await import("./infra/lake.js") : undefined
  const stats = stage.deployAws ? await import("./infra/stats.js") : undefined
  const { stat } = await import("./infra/console.js")
  await import("./infra/enterprise.js")
  if ($app.stage === "production" || $app.stage === "vimtor") {
    await import("./infra/monitoring.js")
  }
}
```

## 阶段环境管理

`infra/stage.ts` 定义阶段到域名的映射：

| 阶段 | 主域名 | 短域名 |
|------|--------|--------|
| `production` | `opencode.ai` | `opncd.ai` |
| `dev` | `dev.opencode.ai` | `dev.opncd.ai` |
| 其他（如 vimtor、adam、thdxr） | `${stage}.dev.opencode.ai` | `${stage}.dev.opncd.ai` |

- `deployAws` 标志仅在 production 和 dev 阶段为 true
- Cloudflare Zone ID 硬编码为 `430ba34c138cfb5360826c4909f99be8`
- 配置了 Cloudflare Regional Hostname，区域键为 `us`
- 生产环境额外配置 trust.opencode.ai 的 CNAME 和 TXT 验证记录

## Cloudflare 部署（面向用户）

### API Worker

`infra/app.ts:13-50` 定义了主要 API：

- **类型**：`sst.cloudflare.Worker`
- **域名**：`api.${domain}`
- **处理函数**：`packages/function/src/api.ts`
- **链接资源**：R2 Bucket、GitHub App 凭证、Admin Secret、Discord Bot、飞书凭证
- **Durable Object**：`SyncServer`（个人开发阶段除外）
- **Logpush**：启用

### 文档站

`infra/app.ts:52-60`：

- **类型**：`sst.cloudflare.x.Astro`
- **域名**：`docs.${domain}`
- **路径**：`packages/web`
- **环境变量**：`VITE_API_URL` 指向 API Worker URL

### Web 应用

`infra/app.ts:62-68`：

- **类型**：`sst.cloudflare.StaticSite`
- **域名**：`app.${domain}`
- **路径**：`packages/app`
- **构建命令**：`bun turbo build`，输出 `./dist`

### Console 控制台

`infra/console.ts:248-301`：

- **类型**：`sst.cloudflare.x.SolidStart`
- **域名**：根域名 `${domain}`
- **路径**：`packages/console/app`
- **区域放置**：`aws:us-east-2`（SSR 部分）
- **兼容标志**：`global_fetch_strictly_public`
- **Tail Consumer**：LogProcessor Worker
- **链接资源**：ZenData Bucket、数据库、Upstash Redis、Stripe、Honeycomb、AWS SES、Salesforce、ZEN_MODELS（30 个 Secret）等

### Auth 服务

`infra/console.ts:63-68`：

- **类型**：Cloudflare Worker
- **域名**：`auth.${domain}`
- **处理函数**：`packages/console/function/src/auth.ts`
- **链接**：PlanetScale 数据库、AuthStorage KV、GitHub OAuth、Google OAuth

### Stat Worker

`infra/console.ts:307-311`：

- **处理函数**：`packages/console/function/src/stat.ts`
- **链接**：数据库

## 数据库

### PlanetScale（主数据库）

`infra/console.ts:11-44`：

- **数据库名**：`opencode`
- **组织**：`anomalyco`
- **生产分支**：`production`
- **其他阶段**：以阶段名创建新分支，父分支为 production
- 通过 `sst.Linkable` 暴露 host、database、username、password、port

### PlanetScale（Stats 数据库）

`infra/stats.ts:107-146`：

- **数据库名**：`opencode-stats`
- 独立于主数据库
- 暴露完整的 `url` 连接字符串

## Stripe 集成

`infra/console.ts:106-185` 定义了两个产品层级：

- **OpenCode Go**（ZenLite）：$10/月
- **OpenCode Black**（ZenBlack）：$20/月、$100/月、$200/月三档

配置了多种优惠券（首月 50% off、首月免费、3 个月免费、6 个月免费、12 个月免费）。

Webhook 端点处理 25+ 事件类型，包括 checkout、invoice、customer、subscription 事件。

## AWS 数据湖（Lake）

`infra/lake.ts` 定义了完整的 Iceberg 数据湖架构，仅在 production/dev 阶段部署。

### 存储层

- **S3 Tables Bucket**：`opencode-${stage}-lake`，使用 Iceberg 格式
- **Glue Catalog**：联邦目录，连接 S3 Tables
- **Athena Results Bucket**：查询结果存储
- **Firehose Errors Bucket**：摄入失败数据备份
- 非生产环境 `forceDestroy: true`

### 摄入层

- **Kinesis Firehose Delivery Stream**：`opencode-${stage}-lake-ingest`
  - 目标：Iceberg
  - 追加模式（appendOnly）
  - 缓冲间隔 60 秒，大小 1 MB
  - 使用 JQ 1.6 进行元数据提取
  - 从 `_lake_database`、`_lake_table`、`_lake_operation` 字段路由
- **ECS/Fargate Ingest Service**：
  - ARM64 架构，1 vCPU，4 GB 内存
  - 生产环境最小 2 副本，最大 32 副本
  - CPU 利用率目标 60%，内存 70%
  - 域名 `lake.${domain}`
  - 健康检查路径 `/ready` 和 `/health`

### 查询层

- **Athena Workgroup**：`opencode-${stage}-lake-workgroup`
  - 单次查询扫描上限 2 TB（防止成本失控）
  - 发布 CloudWatch 指标
- **Lake VPC**：`sst.aws.Vpc`
- **Lake Cluster**：`sst.aws.Cluster`（ECS）

### 推理事件表

`infra/stats.ts:14-90` 定义了 `inference.event` Iceberg 表，包含 50+ 字段：

- 事件元数据（timestamp、date、type、dataset）
- Cloudflare 地理位置（continent、country、city、region、lat/long、timezone）
- 请求指标（duration、request_length、status、is_stream）
- 模型信息（model、model_tier、model_variant、provider、provider_model）
- 错误信息（llm_error_code、error_type、error_message、error_cause）
- Token 统计（input、output、reasoning、cache_read、cache_write）
- 成本（input、output、cache_read/write、total，单位 microcents）
- 用户信息（session、user_id、workspace、subscription）

### Stats 同步服务

`infra/stats.ts:194-219`：

- ECS/Fargate 服务，ARM64，0.25 vCPU，2 GB 内存（0.5 GB 曾导致 OOM 崩溃循环）
- 单副本固定（min 1, max 1）
- 命令：`bun src/stat-sync.ts`
- 同时链接 Athena 和 R2 SQL 以支持回滚

## GitHub Action

`github/` 目录包含 OpenCode 的 GitHub Action 实现。

### Action 元数据

`github/action.yml`：

- **名称**：opencode GitHub Action
- **类型**：composite
- **输入**：
  - `model`（必填）：模型选择，格式 `provider/model`
  - `agent`（可选）：主 agent 名称
  - `share`（可选）：是否共享会话
  - `prompt`（可选）：自定义 prompt
  - `use_github_token`（可选）：直接使用 GITHUB_TOKEN
  - `mentions`（可选）：触发短语，默认 `/opencode,/oc`
  - `variant`（可选）：模型变体
  - `oidc_base_url`（可选）：OIDC token 交换 API

### 执行流程

`github/index.ts` 实现了完整的 Action 逻辑：

1. 验证事件类型（issue_comment 或 pull_request_review_comment）
2. 验证评论包含 `/opencode` 或 `/oc`
3. 启动本地 opencode 服务器（`127.0.0.1:4096`）
4. 通过 OIDC 或 PAT 获取 GitHub App token
5. 创建工作评论
6. 创建 opencode 会话
7. 订阅会话事件流（SSE）
8. 根据场景处理：
   - **Issue**：创建新分支 → 调用 agent → 如有改动则提交并创建 PR
   - **本地 PR**：检出 PR 分支 → 调用 agent → 推送改动
   - **Fork PR**：添加 fork 远程 → 检出分支 → 调用 agent → 推送到 fork
9. 更新评论为最终结果
10. 清理：关闭服务器、恢复 git 配置、撤销 token

### 权限控制

- 检查用户对仓库的权限级别（admin 或 write）
- 使用 `GITHUB_TOKEN` 时跳过权限检查
- Git 提交使用 actor 的 noreply 邮箱作为 co-author

## 密钥管理

`infra/secret.ts` 和各 infra 模块使用 `sst.Secret` 管理敏感信息：

- 云凭证：R2 Access Key/Secret、AWS SES
- 第三方 API：GitHub App、Stripe、Discord、飞书、Salesforce、Honeycomb
- 模型配置：ZEN_MODELS1-30（30 个 Secret 存储模型配置）
- 其他：Admin Secret、Upstash Redis、Support API Key

## 相关概念

- [OpenCode 简介](/concepts/00-introduction.md)
- [架构概览](/concepts/01-architecture.md)
- [配置系统](/concepts/02-config-system.md)
- [会话与工具](/concepts/03-session-tools.md)
