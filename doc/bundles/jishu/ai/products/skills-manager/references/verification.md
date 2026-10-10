---
okf_version: "0.2"
type: reference
title: P0 核验报告
description: Skills Manager 文章 P0 声明核验——官方来源快照、数量口径对照、版本视口与勘误登记（2026-10-10）
tags: [skills-manager, verification, p0, snapshot]
generated:
  by: process:seven-concepts
  at: "2026-10-10T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-10T00:00:00+08:00"
status: flagged
stale_after: "2026-12-31"
sources:
  - id: wechat-article
    url: "https://mp.weixin.qq.com/s/G4jm1Y2wAJUWSSnazAGdxg"
  - id: github-repo
    url: "https://github.com/xingkongliang/skills-manager"
  - id: github-readme
    url: "https://raw.githubusercontent.com/xingkongliang/skills-manager/9e03d833829bc5e004263f61dec75f3bc8e39062/README.md"
  - id: github-release-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager/releases/latest"
  - id: github-api
    url: "https://api.github.com/repos/xingkongliang/skills-manager"
---

# P0 核验报告

> **核验日期**：2026-10-10
> **核验方式**：读取官方 GitHub 仓库 API、主分支 README（固定 commit SHA）、`releases/latest` API、Release 列表 API 与网页 `/releases/latest`，并交叉对照文章页面。源码结论仅作实现分支描述，不构成实机测试或安全审计。

## P0 声明核验总览

| P0 事实 | 文章 | 官方证据 | 核验状态 |
|---|---|---|---|
| 支持 54 个工具/Agent（F-007） | 54 个 | README“54 agents ... out of the box” + API“50+ coding tools” | ✅ 口径支持，但术语不同（详见数量专题） |
| 发布时间（F-004） | 2026-10-04 15:14 | 页面元信息 | ✅ 文章单源记录 |
| 三平台可用（F-009） | macOS/Windows/Linux | README Installation（P0: F-029） | ✅ 官方支持 |
| Windows junction / WSL 复制（F-010） | 有 | 源码 + README（P0: F-027/F-028） | ✅ 部分支持（详见链接专题） |
| Git 备份同步（F-012） | 有 | 源码 `commands/git_backup.rs`（F-032） | ✅ 机制存在 |
| 设备授权（F-013） | 有 | 源码 oauth 路径（F-026） | ✅ 分支存在 |
| 同步冲突+快照（F-014） | 有 | README 同快照 + 源码（F-032/F-041） | ✅ 选项与快照机制一致 |
| 100 MB 限制（F-015） | 默认不备份 | 源码 100 MiB 阈值（F-025） | ✅ 有阈值，但适用范围见边界 |
| 钥匙串存凭证（F-016） | 是 | 源码多入口分支（F-026） | ⚠️ 分支差异，非统一保证 |
| 默认库 `~/.skills-manager`（F-034） | 是 | README 同快照记载默认路径 | ✅ 官方一致 |
| 安装资产格式（F-039） | 多种格式 | 随版本变化 | ⚠️ 动态，以当时 Release 为准 |
| WSL 用 Linux 软链接（F-038） | 是 | 文章单源 | ⚠️ 仅文章陈述，待官方资料核验 |
| 当前版本 v1.40.3 | 文章未标版本 | 三视图均 v1.40.3 | ✅ 动态快照（F-030） |

## 数量口径专题

截至 2026-10-10：
- 文章（F-007）：支持 54 个 AI 编程工具/Agent。
- 官方 README `Supported Tools`（F-023，commit `9e03d833…`）：支持 **54 agents ... out of the box**。
- 官方仓库 API 描述（F-021）：**50+ coding tools**。

`agents` 与 `coding tools` 术语不同，统计对象未必相同；三处数量在字面上相互支持，但不能据此断言三者的统计集合完全一致。引用时保留来源字段与快照日期。

## 版本视口专题

| 视图 | 2026-10-10 新快照 | 历史记录 |
|---|---|---|
| `releases/latest` API | `v1.40.3`（2026-10-01T23:49:29Z） | — |
| Release 列表首项 | `v1.40.3` | — |
| 网页 `/releases/latest` | 重定向至 `v1.40.3` | — |
| 旧 Spec/bundle 记录 | — | `v1.22.1` / `v1.28.3` / `v1.17.0`：无原始响应，不可复现，按未验证历史处理（F-030） |

新快照三视图一致；旧差异值因无原始响应保留为审计历史，不作为当前版本结论。

## 链接与备份边界

- **Windows 链接**（F-027）：实现优先目录符号链接，本地 NTFS 上可回退 junction；远程/UNC（含 `\\wsl.localhost`）走复制回退。README 对 WSL 建议复制而非依赖 junction（F-028）。
- **100 MiB 阈值**（F-025）：针对尚未纳入 Git 跟踪的超限技能；已跟踪技能不会仅因超阈值被自动取消跟踪。仅描述源码分支。
- **凭证**（F-026）：PAT/Device Flow 路径要求令牌写入钥匙串，失败返回错误；旧式含凭证 URL 净化路径在钥匙串不可用时保留原 URL。不同入口分支行为不同，单一定性会超出代码证据。

## 勘误登记

| # | 说明 | 处置 |
|---|---|---|
| 1 | 旧版本口径（v1.22.1/v1.28.3/v1.17.0）与最新 v1.40.3 冲突 | 保留并列历史，标注不可复现，以 2026-10-10 新快照为准（F-030） |
| 2 | 数量口径在文章/README/API 间用词不同 | 并列保留来源字段与口径差异，不强求拼合（F-024） |
| 3 | 作者履历与体验无独立验证材料 | 标为单源主张（F-042/F-043/F-044），不升级为已核实事实 |
| 4 | 文章未标具体产品版本 | 正文引用一律带观察日期与 README commit SHA（F-019/F-031） |

## 门禁说明

- 本包内 toctree、相对链接、frontmatter 与 UTF-8 均通过本地检查。
- 全库 toctree 门禁被无关并行目录 `deepseek-harness/concepts` 缺少 `index.md` 拦截；`invoke gates.*` 因缺少 `invocations` 依赖无法启动。均与本包无关，已在 log 如实记录，不作虚报通过。