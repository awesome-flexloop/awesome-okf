---
okf_version: "0.2"
type: bundle
title: "Plane：开源项目管理平台（自托管教程）"
description: "6 万 Star 开源 Jira/Linear 替代——三套自托管版本与 AGPL 边界、Work Items/Cycles/Modules 三层时间尺度、五视图与 Pages/Wiki、部署运维要点与选型边界"
tags: [Plane, 项目管理, 自托管, Jira替代, Linear替代, AGPL, Docker Compose, Kubernetes, Work Items, Cycles, Modules, 博文转化]
generated: { by: "blog-article-to-okf-wiki", at: "2026-10-13T11:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-10-13T11:30:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: https://mp.weixin.qq.com/s/KCjLFr72qwngPyyI1b2ENg
    title: "6.0 万 Star 的开源项目管理工具：任务、迭代、文档全包了（微信公众号「芋道源码」，2026-10-12）"
  - id: official-repo
    url: https://github.com/makeplane/plane
    title: "makeplane/plane 官方仓库（README / LICENSE.txt / docker-compose.yml）"
  - id: official-editions
    url: https://developers.plane.so/self-hosting/editions-and-versions
    title: "Plane 官方：Understanding Plane's editions"
  - id: official-docker
    url: https://developers.plane.so/self-hosting/methods/docker-compose
    title: "Plane 官方：Docker Compose 部署"
  - id: official-selfhosting-101
    url: https://developers.plane.so/self-hosting/self-hosting-101
    title: "Plane 官方：Self-hosting 101（许可与版本分层）"
  - id: official-integrations
    url: https://docs.plane.so/integrations
    title: "Plane 官方：Native Integrations"
  - id: article-source
    resource: /references/article-source.md
    title: "博文事实登记 F-001~F-057（双份登记）"
  - id: verification
    resource: /references/verification.md
    title: "P0/P1 核验报告与勘误（26 项：✅22 / ⚠️4 / ❌0）"
---

# Plane：开源项目管理平台（自托管教程）

> ⚠️ **性质声明**：本包由单篇微信公众号博文（「芋道源码」，2026-10-12）经 **blog-article-to-okf-wiki 七阶段工作流（R→I→E→V→C）** 转化生成，属**第三方自媒体转述官方信息**类信源。全部规格数字已回溯官方仓库与官方部署文档核验（26 项：✅22 / ⚠️4 / ❌0），**无厂商自宣成效数字**。
>
> **两处版本勘误已在正文落实**：① Postgres **15.5 → 当前 15.7**；② Redis 7.2.4 → 官方已改用 **Valkey 7.2**（Redis 兼容替代）。另补充源文遗漏的 **RabbitMQ** 消息队列与 MinIO 镜像切换。引用本包任何数字前请先读 [核验报告](references/verification.md)。
>
> **原作者未实际部署过 Plane**（文末明示），本包亦未实测——操作步骤源自官方部署文档，非实测结论。

## 这是什么

Plane 是 **AGPL-3.0 开源的现代项目管理平台**，官方定位为 Jira、Linear、Monday、ClickUp 的开源替代，2022 年末建库，GitHub 约 **6.0 万 Star**（核验时点 2026-10-13 为 60.7k）。后端 Django、前端 React，前后端同仓，自托管提供 **Docker Compose** 与 **Kubernetes** 两条官方路径，另有托管云版。

它的结构性特点有两条：**自托管被拆成三套各自独立的代码库**（Community / Commercial / Airgapped，换版本等于换库），以及**把项目管理固化成三种时间尺度**（Work Item 管单件事、Cycle 管这两周、Module 管整条线）。

## 结构总览

```text
plane/
├── index.md                 ← 本文件（性质声明 + 分层导航 + 边界）
├── log.md                   ← 生成日志（R→I→E→V 过程与质量门记录）
├── concepts/                ← 三层知识拆分（6 篇）
│   ├── index.md
│   ├── 00-overview-and-positioning.md   ← 发布事实层：定位/规模/技术栈/AGPL
│   ├── 01-editions-and-licensing.md     ← 结构层：三套版本与许可边界
│   ├── 02-work-model-three-scales.md    ← 结构层：三种时间尺度
│   ├── 03-views-pages-analytics.md      ← 结构层：视图/文档/统计/Intake/集成
│   ├── 04-deployment-and-operations.md  ← 架构层：部署与运维（含版本勘误）
│   └── 05-selection-and-boundaries.md   ← 边界层：选型矩阵与可信边界
├── examples/                ← 演练与清单（步骤源自官方文档，已核验）
│   ├── index.md
│   ├── 00-community-docker-compose-install.md
│   └── 01-production-hardening-checklist.md
└── references/              ← 信源登记（信源先行）
    ├── index.md
    ├── article-source.md    ← 博文事实登记 F-001~F-057
    └── verification.md      ← 核验报告与勘误四张清单
```

## 分层导航

- **先确认它是什么**：[00 定位与起源](concepts/00-overview-and-positioning.md)——规模、技术栈、AGPL 四条实务边界
- **再定版本**：[01 三套自托管版本](concepts/01-editions-and-licensing.md)——Community/Commercial/Airgapped、12 座席、发版节奏
- **理解数据模型**：[02 三种时间尺度](concepts/02-work-model-three-scales.md)——Work Item / Cycle / Module
- **看功能面**：[03 视图、文档、统计与入口](concepts/03-views-pages-analytics.md)——五视图、Pages+Wiki、Intake、集成与 AI
- **准备部署**：[04 部署架构与运维](concepts/04-deployment-and-operations.md) → [演练 00](examples/00-community-docker-compose-install.md) → [加固清单 01](examples/01-production-hardening-checklist.md)
- **做决定**：[05 选型矩阵与适用边界](concepts/05-selection-and-boundaries.md)
- **要溯源/质疑时**：[信源登记簿](references/index.md)、[事实登记](references/article-source.md)、[核验报告](references/verification.md)

## 信任与生命周期

| 维度 | 裁决 |
|------|------|
| status | **stable**（核心声明——三套版本边界、12 座席、AGPL 3.0、五视图、2 核 4G、安装流程——均获官方证实；⚠️ 项为运维细节与单源补充，勘误已完整记录） |
| 信源距离 | 第三方自媒体转述官方信息（第四类）；无厂商自宣成效数字 |
| 核验规模 | 26 项关键声明：**22 ✅ + 4 ⚠️ + 0 ❌** |
| stale_after | **2026-12-31**；上游发新版、组件镜像变更、座席条款变动即触发复核 |

## 已知边界

1. **无一手实测**：原作者未部署（F-052），本包亦未实测 —— 资源占用、升级平滑度、故障率均无数据。
2. **组件版本已漂移**：Postgres 15.5→**15.7**；Redis 7.2.4→**Valkey 7.2**；MinIO 镜像 2026-10-08 切至 `pgsty/silo`。博文数字不可直接照用。
3. **源文遗漏 RabbitMQ**：官方 Compose 还含消息队列，后台任务依赖它，排障时不可忽略。
4. **Intake 待审队列**仅获旁证支持，未核到官方一手文档页（V26）。
5. **Kubernetes 三条参数**（Helm / PLANE_VERSION / 勿写 stable）仅博文单源（V27）。
6. **Star 与集成清单是时点快照**（2026-10-13），随时间变化。
7. **座席与最低购买门槛**可能变动：2026-04 曾拟设自托管商用 10 座席、Airgapped 100 座席门槛后延期，采购前须向官方确认。

## 主题关联

- 同组 [opensource/](../opensource/index.md)：开源参与与项目准备，配合本包的「开源项目如何落地为团队工具」
- 同域 [containers/](../../containers/index.md)：容器生态（Podman/Compose），自托管部署的底层依赖
- 同域 [systems/](../../systems/index.md)：WSL 与系统基础设施，Windows 环境下的自托管前置条件

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
