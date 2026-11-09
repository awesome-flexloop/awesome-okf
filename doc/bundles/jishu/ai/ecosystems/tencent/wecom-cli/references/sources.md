---
type: reference
title: wecom-cli 信源登记
description: 登记 wecom-cli 知识包的上游仓库、固定版本基线、许可证与复核边界。
tags: [wecom, wecom-cli, sources]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: R（信源）
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-cli/
  - resource: /references/facts.md
---

# wecom-cli 信源登记

## 固定基线

| 项目 | 登记值 | 依据 |
|---|---|---|
| 上游路径 | `vendor/WecomTeam/wecom-cli/` | F-001、F-162 |
| 上游仓库 | `https://github.com/WecomTeam/wecom-cli` | F-003 |
| 基线 commit | `1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde` | facts.md frontmatter、F-009 |
| npm 包 | `@wecom/cli` `1.3.4` | F-009 |
| 许可证 | MIT | F-003、F-032、F-163 |
| Rust MSRV | `1.85.0` | F-005 |
| Node 要求 | `>=18` | F-014、F-162 |

## 证据边界

本包只描述固定基线中的仓库文件、代码结构、命令行为、测试结构与文档登记。数字、路径、版本和行为不以推测补足，均回指 `facts.md` 的 F 编号。事实登记明确覆盖 F-001 至 F-172，连续无跳号、无重复（见 `facts.md` 统计节）。

## 复核方法

升级基线时，应先重新固定 commit，再按 `facts.md` 各条的证据位置和取证命令复测。对 Skills 数量与 crate 数量，应保留现有并置口径：前者由 F-151/F-152 登记 14 与 15 的差异，后者由 F-164/F-165 登记 3 与 5 的差异。
