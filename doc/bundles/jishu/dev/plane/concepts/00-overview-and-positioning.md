---
okf_version: "0.2"
type: Concept
title: "Plane 是什么：定位、起源与技术栈"
description: "Plane 的开源定位、仓库规模与建库时间、Django+React 技术栈、AGPL 3.0 许可，以及它在 Jira/Linear 之外的第三选项位置"
sources:
  - id: blog
    resource: https://mp.weixin.qq.com/s/KCjLFr72qwngPyyI1b2ENg
  - id: official-repo
    resource: https://github.com/makeplane/plane
---

# 00 · Plane 是什么

## 1. 一句话定位

Plane 是**开源的项目管理平台**，官方自我描述为「Open-source Jira, Linear, Monday, and ClickUp alternative」，覆盖任务跟踪、周期（Sprint）运转、产品路线图与需求分诊（F-001、F-003）。它同时提供托管云版（Plane Cloud）与自托管部署，本包聚焦**自托管**路径。

## 2. 规模与起源

| 维度 | 值 | 出处 |
|------|-----|------|
| GitHub 仓库 | `makeplane/plane` | F-003 |
| Star 数 | 约 **6.0 万**（核验时点 2026-10-13 快照为 **60.7k**） | F-002 / V1 |
| 建库时间 | **2022 年末**（博文记为 2022 年 11 月，权威源仅到季度粒度） | F-004 / V2 |
| 提交规模 | 7,200+ commits（2026-10 快照） | 补充核验 |

> ⚠️ **口径提醒**：Star 是**时点快照**，不同日期的二手文章会给出 58k / 59.6k / 60.7k 等差异值，差异来自抓取时间而非事实冲突（见 [verification.md §③](../references/verification.md)）。

## 3. 技术栈

| 层 | 选型 | 出处 |
|----|------|------|
| 后端 | **Django**（Python） | F-013 / V11 |
| 前端 | **React**（TypeScript） | F-013 / V11 |
| 数据库 | PostgreSQL | 核验补充 |
| 缓存/消息 | Valkey（Redis 兼容）+ RabbitMQ | V24 / F-056 |
| 对象存储 | S3 兼容（容器内置 MinIO） | F-041 / F-056 |
| 代码组织 | 前后端**同仓**（monorepo，`apps/` + `packages/` + `deployments/`） | F-013 |

官方 Compose 的实际服务拓扑为：web / admin / space / api / worker / beat-worker / migrator / live / proxy 九个应用服务，外加 plane-db、plane-redis、plane-mq、plane-minio 四个有状态服务（F-056）。

## 4. 许可证：AGPL 3.0 的真实边界

License 为 **GNU AGPL v3.0**（F-051 / V21）。官方在《Self-hosting 101》中给出四条实务边界：

| 场景 | 官方口径 |
|------|---------|
| 团队内部自用 Community | 无附加义务 |
| 内部使用并修改 Community | AGPL 明确允许 |
| 把 Community 作为服务提供给**外部客户** | 须公开你所做的修改（含源码） |
| 把 Community **嵌入商业产品** | 触发 AGPL 传染条款，需合规或向官方购买商业许可 |

博文的判断「对打算二次开发再商用的团队有影响，团队内部自用不受限制」（F-051）与官方口径一致。

## 5. 它站在什么位置

博文给出的对照（属**作者观点**，非官方结论）：

| 工具 | 博文口径 | 性质 |
|------|---------|------|
| Jira | 功能齐，但配置成本高，建项目/加字段/改流程都费时间 | F-054 [作者观点] |
| Linear | 顺手，但闭源、数据在别人机器上、按人头计费 | F-054 [作者观点] |
| Redmine / OpenProject | 老项目活了十几年、功能不缺，界面停留在上一个时代 | F-053 [作者观点] |

作者的核心判断是：Plane 同时占住「**体验达到商业产品水平**」与「**数据所有权留在用户手上**」两点（F-055）。这一判断与官方自我定位方向一致，但「界面代际优于老牌开源项目」属于主观评价，采信前建议自行试用。

## 6. 本包的可信边界

博文作者在文末明示：**「我没有实际部署过 Plane，文中功能与部署描述来自官方 README、开发者文档与来源正文」**（F-052）。因此本包所有规格数字均已回溯官方源核验（见 [verification.md](../references/verification.md)），但**不包含任何一手实测结论**（如实际资源占用、升级平滑度、故障率）。

下一篇 → [01 三套自托管版本与许可边界](01-editions-and-licensing.md)
