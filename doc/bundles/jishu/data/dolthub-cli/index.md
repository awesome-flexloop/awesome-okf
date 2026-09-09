---
okf_version: "0.2"
type: bundle-index
title: "dh — DoltHub 命令行接口"
description: "dh CLI 知识包：DoltHub 官方命令行接口的架构、认证、SQL/表导入、仓库协作与异步操作，基于本地源码（dolthub/cli @ 2ef50ab）逐条溯源"
tags:
  - dh
  - dolthub
  - cli
  - go
  - oauth
  - sql
  - version-control
generated:
  at: "2026-09-09"
verified:
  at: "2026-09-09"
  by: process:seven-concepts-v
  status: stable
  noted: 基于本地源码 dolthub/cli（commit 2ef50ab）采集 F-001~F-060，全部事实可 Grep 溯源
stale_after: "2026-12-31"
sources:
  - url: "https://github.com/dolthub/cli"
    type: source-code
    title: "dolthub/cli — GitHub"
    distance: 1
status: stable
---

# dh — DoltHub 命令行接口

本知识包系统化学习 [dolthub/cli](https://github.com/dolthub/cli)（`dh`）的源码，产出可溯源的 OKF 教程。`dh` 是 DoltHub 云平台的官方 CLI，把"GitHub for Data"体验从 Web 端延伸到终端——认证、SQL 查询、表导入、分支/标签/Release、Pull Request 协作一应俱全。

所有内容溯源至 [F-001 ~ F-060](references/source.md)，基于本地源码 `external/dao/action/DoltHub/cli`（commit `2ef50ab87632b40c08782f43573e2b3c43ebfbd9`，`v0.0.1-2-g2ef50ab`），遵循 [OKF v0.2 规范](https://github.com/awesome-flexloop/awesome-okf)。

## 导航

### 核心概念（concepts/）

* [dh CLI 概述与安装](concepts/00-overview.md) — 产品定位、安装/构建、14 个命令组全貌
* [dh CLI 架构与分层](concepts/01-architecture.md) — 入口、Cobra 命令树、Factory 依赖注入、IOStreams、错误/退出码
* [认证与凭据管理](concepts/02-authentication.md) — OAuth PKCE、keyring/文件双源存储、token 刷新、安全脱敏
* [SQL 查询与表导入](concepts/03-sql-and-import.md) — 读/写 SQL、分片上传、异步导入
* [仓库协作操作](concepts/04-repository-operations.md) — db/branch/pr/release/tag、仓库解析
* [结构化输出与异步操作](concepts/05-output-and-operations.md) — JSON/jq/template、Operation 轮询、分页

### 实操示例（examples/）

* [认证操作示例](examples/00-authentication.md)
* [SQL 查询示例](examples/01-sql-queries.md)
* [表导入示例](examples/02-table-import.md)
* [Pull Request 协作工作流示例](examples/03-pr-workflow.md)

### 信源（references/）

* [dh CLI 源码事实登记](references/source.md) — F-001 ~ F-060 全部事实编号

## 学习路径建议

1. **入门**：[概述](concepts/00-overview.md) → [架构](concepts/01-architecture.md)
2. **进阶**：[认证](concepts/02-authentication.md) → [SQL/导入](concepts/03-sql-and-import.md) → [协作](concepts/04-repository-operations.md) → [输出/异步](concepts/05-output-and-operations.md)
3. **实操**：阅读 [examples/](examples/index.md) 中的命令示例
4. **溯源**：阅读 [references/source.md](references/source.md) 核对全部 F 编号

## 核心洞察

1. **gh 架构范式迁移**：`dh` 高度同构于 GitHub CLI（`gh`），是"Go 现代 CLI 工程化"的精简范本。
2. **凭据安全是重头戏**：OAuth PKCE + 双源存储 + token 轮换 + 敏感脱敏，占据 `internal/` 相当比重。
3. **异步操作统一抽象**：SQL write/fork/merge/import 统一收敛为 `Operation` + 指数退避轮询。
4. **安全边界优先的 HTTP 客户端**：URL 逃逸防护、同源校验、控制字符过滤是防凭据泄露的第一道防线。
5. **可测试性贯穿始终**：IO/网络/时间/浏览器全部可注入，是 CLI 高单测覆盖的根因。

## 信任与生命周期说明

- **status 判定依据**：`stable`。全部 60 条事实基于本地源码（信源距离 ①）逐条 Grep 验证，无虚构 API。
- **stale_after 解释**：设为 `2026-12-31`。`dh` 处于快速迭代期（v0.0.1），命令/API 可能变更，年末重新评估。
- **信源基线**：commit `2ef50ab`（2026-09-08），`git describe` = `v0.0.1-2-g2ef50ab`。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
