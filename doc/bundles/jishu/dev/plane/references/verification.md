---
okf_version: "0.2"
type: Reference
title: "Plane 博文 P0/P1 核验报告与勘误"
description: "26 项关键声明核验结果（✅22 / ⚠️4 / ❌0）、勘误四张清单、两项源文遗漏与时效边界"
verified_at: "2026-10-13"
---

# 核验报告

> **结论**：`status: stable`。26 项核验 **22 ✅ / 4 ⚠️ / 0 ❌**；全部 ⚠️ 项为运维细节与单源补充，非博文核心主结论（三套版本边界、12 座席、AGPL、五视图、2 核 4G、安装流程均获官方证实），故不置 `flagged`。
> **信源距离**：第三方自媒体转述官方信息（第四类）。作者已在文末明示未实测（F-052），未发现厂商自宣成效数字，故无「营销数据污染」风险。

## 一、核验明细

### A. 定位与规模

| # | 声明（F） | 博文口径 | 核验来源 | 结果 | 说明 |
|---|----------|---------|---------|------|------|
| V1 | F-002 Star 数 | 6.0 万 / 六万多 | GitHub 仓库页快照（2026-10-13）：**60.7k stars**；另有 59.6k（更早口径） | ✅ | 量级一致；Star 为时点快照，正文统一写「约 6.0 万（核验时点 60.7k）」 |
| V2 | F-004 建库时间 | 2022 年 11 月 | Besthub 综述「open-sourced in **late 2022**」；官方页未精确到月 | ⚠️ | 「2022 年末」获证，**具体 11 月仅博文单源** |

### B. 三套版本与许可

| # | 声明（F） | 博文口径 | 核验来源 | 结果 | 说明 |
|---|----------|---------|---------|------|------|
| V3 | F-005 三套独立代码库 | 三套各自独立、换版本等于换库 | developers.plane.so《editions-and-versions》：「Each of our editions is built on a **distinct codebase**…separate codebases, not feature toggles」 | ✅ | 逐字级一致 |
| V4 | F-006 Community 免费/无上限/对齐免费档 | 免费、人数不封顶、对齐云端免费档 | 同上 +《self-hosting-101》：「Free, no license key…Feature parity with the Free tier of Cloud」；「Community Edition remains free **without a seat limit**」 | ✅ | |
| V5 | F-007 Commercial 内置 12 座席 | 每工作区送 12 个座席 | 官方：「a built-in Free tier of **12 user seats per workspace**」 | ✅ | |
| V6 | F-008 Airgapped 离线版 | 商用版改造、更新从自己的镜像仓库拉 | 官方：「The Airgapped Edition is the Commercial Edition adapted for environments without internet access…**Updates from your own docker registry**」 | ✅ | |
| V7 | F-009 发版节奏云端→商用→社区 | 先云端、再商用、最后社区 | 《self-hosting-101》对照表：「New features ship here first（Cloud）→ Commercial gets them next → Community last」 | ✅ | |
| V8 | F-010 无强制迁移/无隐藏限制 | 无强制迁移、社区版无隐藏限制代码 | 官方：「**no hidden code** that limits modifications on the Community Edition」「**no forced migrations** from one edition to another」 | ✅ | |
| V9 | F-011 离线版仅最高档企业方案 | 只随最高一档企业方案提供 | plane.so 对比文：Air-gapped 对应 **Enterprise Grid**；新购 Airgapped 曾拟设 100 座席门槛（2026-04 公告后延期） | ✅ | 补充：门槛条款 2026-04 提出后延期，以官方当期口径为准 |
| V10 | F-012 社区版 REST API 与 Webhook 开放 | 开放 | 官方 Marketplace 支持 OAuth 2.0 / webhooks / Python+TS SDK；第三方综述确认社区版含 REST API 与 webhooks | ✅ | 官方一手为 Marketplace 平台能力描述，社区版含 API/webhook 由旁证确认 |
| V21 | F-051 许可证 AGPL 3.0 | AGPL 3.0，二开再商用有影响 | 仓库 LICENSE.txt + 官方 editions 页「governed by the AGPL v3.0 license」 | ✅ | |
| V23 | F-050 SSO/审计日志付费 | 商用版付费档、按座席收费 | plane.so 对比文：「SAML and OIDC SSO are available on **Pro and above**」；《self-hosting-101》：「Audit logs, SCIM, advanced auth → **Business Plus**」 | ✅ | |

### C. 技术与功能

| # | 声明（F） | 博文口径 | 核验来源 | 结果 | 说明 |
|---|----------|---------|---------|------|------|
| V11 | F-013 技术栈 Django + React | 后端 Django、前端 React、前后端同仓 | 仓库 topics（django/python/react/redis/postgresql）+ 第三方综述「frontend TypeScript and React, backend Django」 | ✅ | |
| V12 | F-014 Docker Compose 与 K8s 双路径 | 两条 | 仓库 README「Installation methods：**Docker** / **Kubernetes**」 | ✅ | |
| V13 | F-022 五种视图 | 看板/列表/日历/甘特图/表格 | plane.so 官方博客：「Plane ships **five layouts** on every plan, including Free: Board (Kanban), List, Timeline (Gantt), Calendar, and Spreadsheet」；docs 教程列 List/Board/Calendar/Table/Timeline | ✅ | 命名口径：官方 Timeline=甘特、Spreadsheet=表格 |
| V14 | F-024 五种版式免费档全开放 | 免费档全部开放 | 同上「five layouts on every plan, **including Free**」 | ✅ | |
| V15 | F-026 官方集成四项 | GitHub、GitLab、Slack、Sentry | docs.plane.so《Native Integrations》原生集成页逐项列出 GitHub / GitHub Enterprise / Draw.io / GitLab / Slack / Sentry | ✅ | 官方集成多于博文所列（另有 GitHub Enterprise、Draw.io） |
| V16 | F-031 Pages + Wiki 双层 | 项目级 Pages、工作区级 Wiki | plane.so 官方博客多次并列「Pages and Wiki」；仓库 README 仅列 Pages | ✅ | Wiki 由官方博客证实，README 未列 |
| V22 | F-047 God mode | 管理员专属实例管理路径 | 仓库 README：「**Instance admins** can configure instance settings with **God mode**」 | ✅ | |
| V26 | F-025 Intake 待审队列 | 外部免注册表单 → 待审队列 | 未取到官方 Intake 独立文档页；Besthub 综述同样描述 Intake 机制 | ⚠️ | 机制获旁证支持，**官方一手页未核到**，正文标「博文 + 旁证」 |

### D. 部署与运维

| # | 声明（F） | 博文口径 | 核验来源 | 结果 | 说明 |
|---|----------|---------|---------|------|------|
| V17 | F-033/F-034 一键脚本与八项菜单 | 五步命令 + 八项菜单 | 官方《Docker Compose》页：步骤 01–05 与菜单 1–8 **逐项一致** | ✅ | 官方示例目录名为 `plane-selfhost`，博文用 `plane-deploy`（自由命名差异，注记） |
| V18 | F-036 端口与环境键默认值 | HTTP/HTTPS 默认 80/443，WEB_URL 与 CORS 默认本机 | 官方：`LISTEN_HTTP_PORT=80`、`LISTEN_HTTPS_PORT=443`、`WEB_URL="http://localhost"`、`CORS_ALLOWED_ORIGINS="http://localhost"` | ✅ | 补充官方键名（博文未给键名）；官方要求 WEB_URL 与 CORS **必须完全一致**（含协议与端口），否则认证与 API 失败 |
| V19 | F-038 机器门槛 2 核 4G | 2 核 4G 能跑 | 官方 Prerequisites：「**CPU: 2 cores**」「**RAM: 4GB**（**8GB recommended for production**）」 | ✅ | 补充：生产官方推荐 8GB |
| V20 | F-040 生产外置数据库/存储 | 建议挪到容器外 | 官方 WARNING：「**strongly recommended** to configure external database and storage」 | ✅ | |
| V24 | F-041 容器内置组件版本 | Postgres 15.5、Redis 7.2.4、MinIO | 官方 docker-compose：`postgres:15.7-alpine`、`valkey/valkey:7.2.x-alpine`；官方配置文档：「Plane uses **Valkey 7.2** by default, a Redis-compatible alternative」 | ⚠️ | **勘误①**：Postgres 15.5 → 当前 15.7；**勘误②**：Redis 7.2.4 → 官方已改用 **Valkey 7.2**（Redis 兼容替代） |
| V25 | F-042 上传上限默认 5 MB | 默认 5 MB | 官方环境变量表：`FILE_SIZE_LIMIT` 默认 **5242880** 字节 = 5 MB | ✅ | |
| V27 | F-044/F-045 Helm 与 PLANE_VERSION | 官方 Helm Chart，勿写 stable | 未取到 K8s 部署文档页原文 | ⚠️ | **仅博文单源**，正文标注 |

## 二、勘误四张清单

### ① 日期/版本表

| 项 | 博文口径 | 核验值 | 处置 |
|----|---------|--------|------|
| 建库时间（F-004） | 2022 年 11 月 | 2022 年末（权威仅到季度粒度） | 正文写「2022 年末（博文记 11 月）」 |
| Postgres 版本（F-041） | 15.5 | **15.7**（`postgres:15.7-alpine`） | 正文采用 15.7，标注源文 15.5 为历史值 |
| Redis 版本（F-041） | Redis 7.2.4 | **Valkey 7.2**（Redis 兼容替代，官方默认） | 正文采用 Valkey 7.2，说明镜像已由 Redis 换成 Valkey |
| MinIO（F-041/F-057） | MinIO（未注镜像） | 2026-10-08 上游 commit `bab49bb` 将 MinIO 镜像切至 `pgsty/silo` | 正文标注镜像来源近期变更，离线部署需确认 |

### ② 成效数字溯源表

**N/A**。本博文为工具盘点类，全文无「提效 N 倍 / 节省 N 工时 / 成本下降 N%」类厂商自宣成效数字，故无溯源失败项。文中出现的数字均为**规格数字**（座席数、端口、内存、文件大小、Star 数），已逐项归入 ① 与 ③。

### ③ 口径对照表

| 项 | 博文口径 | 核验口径 | 处置 |
|----|---------|---------|------|
| Star 数（F-002） | 6.0 万（标题）/ 六万多（正文） | 2026-10-13 快照 **60.7k**；另见 59.6k、58k 等更早口径 | 正文统一「约 6.0 万（核验时点 60.7k）」，并声明 Star 为时点快照 |
| 内存（F-038） | 2 核 4G 能跑 | 官方最低 2C/4G，**生产推荐 8GB** | 正文补「生产推荐 8GB」，避免读者按最低值上生产 |
| 集成清单（F-026） | 四项 | 官方原生集成 **六项**（另含 GitHub Enterprise、Draw.io） | 正文补两项，说明官方集成面大于博文 |

### ④ 引文逐字核对表

| 项 | 核对结果 |
|----|---------|
| 八项菜单（F-034） | 逐字一致 ✅ |
| 「换版本等于换库」（F-005） | 与官方「separate codebases, not feature toggles」语义一致 ✅ |
| S3 兼容 / 地址不能填本机 / 密码特殊字符（F-043） | 官方页未直接载此表述 → 标「仅博文单源」，正文保留但不作强断言 |
| prime-cli configure 可改项（F-042） | 上传上限已核（V25 ✅）；其余项未逐项核到官方原文 → 标注 |

## 三、源文遗漏（核验补充）

| 补充 | 内容 | 影响 |
|------|------|------|
| **F-056 RabbitMQ** | 官方 Compose 另含 `rabbitmq:3.13.6-management-alpine`，承担邮件、通知、导入等后台任务 | 博文 07 节只列三件组件；排障时若 worker/beat 反复重启，多为 RabbitMQ 或 Postgres 不可达 |
| **F-057 MinIO 镜像切换** | 2026-10-08 commit 切至 `pgsty/silo` | 影响私有镜像仓库同步与离线部署拉取策略 |

## 四、时效边界

| 项 | 时点/状态 | 复核触发 |
|----|----------|---------|
| Star 数、组件版本、集成清单 | 2026-10-13 快照 | `stale_after: 2026-12-31`；上游发新版 / 镜像再切换即复核 |
| Commercial 座席与最低购买门槛 | 12 座席（免费档）；2026-04 曾拟设自托管商用 10 座席、Airgapped 100 座席门槛后延期 | 采购决策前须向官方确认当期条款 |
| 部署步骤 | 官方 Docker Compose 页（2026-10 版） | 官方安装脚本改版即复核 |
