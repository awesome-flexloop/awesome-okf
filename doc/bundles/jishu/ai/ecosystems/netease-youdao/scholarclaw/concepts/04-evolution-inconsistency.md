---
type: concept
title: 源码不一致与防御性兼容模式
description: "引擎清单、博客状态枚举、命令清单三处源码间不一致的登记与解读：实现层是类型层的超集，集成时应以运行时行为为准、不以类型枚举为准。"
tags: [scholarclaw, inconsistency, defensive-compatibility, runtime-behavior]
generated: { by: "reference_agent/trae-cn", at: 2026-09-09T10:00:00+08:00 }
verified: { by: "process:facts-cross-check", at: 2026-09-09T10:00:00+08:00 }
status: stable
stale_after: 2027-09-09
sources:
  - id: facts
    resource: /references/facts.md
    title: ScholarClaw 源码事实清单
  - id: insights
    resource: /references/insights.md
    title: ScholarClaw 架构洞察
---

# 源码不一致与防御性兼容模式

基线 commit（`97bdb5e`）中存在三处源码间不一致。直觉上"代码与文档不一致 = 质量缺陷"，但此处的不一致呈现**方向性规律**：实现层的匹配集合是类型层的超集。这是 SaaS 服务端先行、客户端分层跟进的快速迭代痕迹，解读与应对方式直接影响集成的健壮性。

## 三处不一致登记

### 1. 引擎清单（F-sc-062、F-sc-005）

README.md 引擎表列出 9 个引擎且**含 `openalex`、不含 `cache`**；而 `config.ts` 的 `SEARCH_ENGINES` 含 `CACHE`、**不含 `openalex`**（OpenAlex 实际由独立 `/openalex/*` 路由承载，见 F-sc-014）。两处清单不一致。

### 2. 博客状态枚举（F-sc-063、F-sc-007、F-sc-037）

`types.ts`/`config.ts` 的状态枚举为 `pending/running/completed/failed` 四值（F-sc-007）；而 `blog.sh` 的状态匹配分支与 SKILL.md 状态示例中出现 `processing`、`queued`、`success` 取值（F-sc-037）。状态取值集合在不同文件中不一致。

### 3. 命令清单（F-sc-064）

`package.json` 的 14 个 supportedCommands **不含 `blog.sh` 同步封装脚本**；而 `install.sh` 生成的 `sc-blog` 别名却指向 `blog.sh`。

## 解读：实现层做了超集兼容

三处差异的共同模式是**类型层（文档/枚举/元数据）滞后或超前于实现层，而实现层做了超集兼容**：

- `blog.sh` 的状态匹配分支是 `BLOG_STATUSES` 的**超集**（`completed|success`、`failed|error`、`pending|running|processing|queued` 三组并集），说明服务端实际返回的状态值超出客户端类型声明，实现者选择以运行时行为为准、枚举仅作参考（F-sc-037、F-sc-007）；
- README 面向用户宣传最新能力（openalex），`config.ts` 常量残留旧引擎（CACHE）（F-sc-062、F-sc-005）；
- `sc-blog` 别名指向未被 supportedCommands 收录的 `blog.sh`，说明安装层跟进了脚本层的实际能力（F-sc-064）。

若按"枚举即全部合法值"的静态思维编程，会在 `processing`/`queued` 状态上误判任务失败。

## 防御性集成实践

1. **状态轮询用分组/前缀匹配，禁止精确等值比较**：完成组、失败组、进行中组三分；新增服务端状态时只需扩展分组，不影响主流程。
2. **引擎参数入参白名单以服务端报错为准回退**，不要硬编码 `SEARCH_ENGINES` 作为唯一合法集（F-sc-005）。
3. **功能存在性判断以 shell 脚本集为准**：`blog.sh` 同步封装与 `health.sh` 简易模式不在 supportedCommands 中，但真实可用（F-sc-064、F-sc-040）。
4. **升级版本时重点 diff 三处易漂移面**：`config.ts` 常量表、SKILL.md 时序参数、`package.json` 的 lobsterai 元数据。
5. **撰写下游文档引用引擎/状态清单时**，交叉核对 README 与 `config.ts` 两处并标注差异，以事实清单存疑节（F-sc-062~F-sc-064）为准。

## 相关概念

- [/concepts/01-server-client.md](/concepts/01-server-client.md)
- [/concepts/02-shell-toolchain.md](/concepts/02-shell-toolchain.md)
- [/concepts/03-skill-contract.md](/concepts/03-skill-contract.md)
