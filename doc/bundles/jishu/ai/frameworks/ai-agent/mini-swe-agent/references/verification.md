---
type: Reference
title: "P0 核验报告：mini-SWE-agent 博客与仓库对账"
description: "对博客的 Stars、SWE-bench 年份、74% 成绩、代码规模、快速开始 API 与 v2 工具调用方式做权威核验；记录 4 条硬勘误、1 条口径边界与 1 个信源缺口"
tags: [核验, P0, 勘误, mini-swe-agent, SWE-bench, 信源缺口]
generated: { by: "seven-concepts-cmd/V", at: "2026-11-10T17:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: github-api
    resource: https://api.github.com/repos/SWE-agent/mini-swe-agent
    title: "GitHub API 仓库元数据（stars/forks/license/created_at）"
  - id: arxiv-swebench
    resource: https://arxiv.org/abs/2310.06770
    title: "SWE-bench 论文（arXiv 2310.06770，2023-10-10 提交）"
  - id: repo-commit
    resource: https://github.com/SWE-agent/mini-swe-agent/commit/04d809ceab9df28f9adaed044884180159172930
    title: "mini-swe-agent v2.4.6 源码（2026-09-03）"
  - id: official-docs
    resource: https://mini-swe-agent.com/latest/
    title: "mini-SWE-agent 官方文档"
---

# P0 核验报告：博客与仓库对账

> 核验日期：2026-11-10。P0 = 数字、日期、官方表态、产品能力时间线、核心 API。P1 = 能力声明、采用者名单、无量化基准的性能比较。P2 = 背景叙述与作者观点。

## 一、P0 核验结论

| 编号 | 待核验声明 | 权威来源 | 结论 |
|---|---|---|---|
| P0-1 | 博客：项目有 26k+ GitHub Stars（F-004） | GitHub API：`stargazers_count = 9496`（F-036） | ❌ **不成立**，实际 9,496（E-1） |
| P0-2 | 博客：SWE-agent 团队 2024 年发布 SWE-bench（F-007） | arXiv 2310.06770：Submitted on 10 Oct 2023（F-085） | ❌ **不成立**，SWE-bench 为 2023 年（E-2） |
| P0-3 | 博客：74% SWE-bench verified（F-005、F-017） | 官方 docs：`Scores >74%` + News “Gemini 3 Pro reaches 74%”（F-070） | ⚠️ **成立但有口径边界**：官方未公开完整评测配置（F-088） |
| P0-4 | 博客：核心代码约 100 行（F-006） | 源码：`default.py` 172 行，核心方法约 100 行（F-075、F-079） | ⚠️ **概数成立**，但不能按字面理解为整文件 100 行 |
| P0-5 | 博客：快速开始使用 `MiniSWEAgent`、`result.passed`、`result.patch`（F-028） | v2.4.6 源码：真实入口为 `DefaultAgent`，`run()` 返回 exit_status/submission（F-086） | ❌ **API 不存在**（E-3） |
| P0-6 | 博客：没有工具、不需要 tool-calling（F-010） | v2 `LitellmModel` 默认 `tools=[BASH_TOOL]`（F-060） | ❌ **仅 v1/文本模式成立**（E-4） |
| P0-7 | 仓库许可证为 MIT（F-037） | GitHub API `spdx_id = MIT` + LICENSE.md | ✅ 通过 |
| P0-8 | 版本为 v2.4.6、commit `04d809ce`（F-038） | `git log` + `__init__.py` | ✅ 通过 |
| P0-9 | 支持 local/docker/singularity 等环境（F-043、F-057） | 源码 environments/ + docs/advanced/environments.md | ✅ 通过（博客只列 4 类，实际更多） |
| P0-10 | 完成信号为 `COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`（F-055、F-062） | local.py:45-62 + v2_migration.md | ✅ 通过 |
| P0-11 | 知乎文章可作为第二信源（用户提供） | 三次抓取：403 / 40362 / 404（F-090） | ❌ **不可达**，未使用 |

## 二、四条硬勘误

### E-1｜Stars 数量：26k+ → 9,496

- 博客原文（F-004）：`26k+ Stars`。
- 权威值（F-036）：GitHub API 在 2026-11-10 返回 `stargazers_count = 9496`。
- 差异：16,504。即使考虑博客写于 2026-03-22，GitHub 星数也不可能在 8 个月内减少 1.6 万；该数字更可能是与其它项目混淆或凭空放大。
- 处理：正文不引用 26k+；统一写“约 9.5k stars（2026-11-10 快照）”。

### E-2｜SWE-bench 发布年份：2024 → 2023

- 博客原文（F-007）：“SWE-agent 团队在 2024 年发布了 SWE-bench”。
- 权威值（F-085）：SWE-bench 论文 arXiv 2310.06770 于 **2023-10-10** 提交；SWE-agent 论文 arXiv 2405.15793 为 2024 年。
- 处理：正文改为“SWE-bench 于 2023 年提出，SWE-agent 于 2024 年发布”。

### E-3｜快速开始 API 不存在

- 博客原文（F-028）：`from minisweagent import MiniSWEAgent`，`result.passed`，`result.patch`。
- 源码事实（F-086）：v2.4.6 无 `MiniSWEAgent` 类；真实入口为 `minisweagent.agents.default.DefaultAgent`，构造参数为 `(model, env)`，`run(task)` 返回 `{"exit_status": ..., "submission": ...}` 形态的字典。
- 处理：`examples/02-python-bindings.md` 使用官方文档真实代码；正文明确标注博客代码为伪代码。

### E-4｜“没有工具/不需要 tool-calling”是 v1 结论

- 博客原文（F-010、F-020）：mini 没有工具接口，不需要 tool-calling。
- 源码事实（F-060、F-061）：v2 默认 `LitellmModel` 使用 `BASH_TOOL` 原生 tool calling；文本解析模式保留但被官方“强烈建议”替换。README（F-078）与 FAQ 仍保留旧表述，属文档滞后。
- 处理：`concepts/01-design-philosophy.md` 与 `concepts/04-model-integration.md` 同时给出 v1 与 v2 两条路径，不把 v1 结论写成现状。

## 三、口径边界与单源清单

| 项目 | 性质 | 处理 |
|---|---|---|
| 74% 的完整评测配置（F-088） | 官方只给结果，不给模型快照/成本上限/步数/架构 | 正文写“官方声明 + Gemini 3 Pro 单点成绩”，不写“任何模型都能 74%” |
| 65% / 42% / 54% 对比表（F-089） | 博客单源，未在官方 docs 逐项复核 | 只在“博客数据表”语境引用，标注单源 |
| 采用者名单（F-041、F-082） | 机构自述，无授权/案例 | 写“README 自述”，不作为独立事实 |
| “启动快于 Claude Code”（F-042、F-083） | 无量化方法 | 不引用为性能结论 |
| 能力边界表（F-032） | 作者判断，无逐项基准 | 标注“作者判断” |
| 知乎文章（F-090） | 403/404，无法读取 | 明示信源缺口，不虚构其观点 |

## 四、跨信源一致性

| 主题 | 博客 | 仓库/官方 | 判定 |
|---|---|---|---|
| 项目定位 | 100 行极简 coding agent | README 同定位 | ✅ 一致 |
| 设计三原则 | bash-only / 线性历史 / 独立 subprocess | 源码与 FAQ 一致 | ✅ 一致（v1 语义） |
| 74% | Gemini 3 Pro 74% | docs >74% + News 74% | ✅ 一致（口径待补） |
| 代码规模 | 约 100 行 | README 约 100 行；文件 172 行 | ⚠️ 概数 |
| 工具接口 | 无工具、不用 tool-calling | v2 默认 bash tool call | ❌ 版本差异（E-4） |
| Stars | 26k+ | 9,496 | ❌ 硬错误（E-1） |
| SWE-bench 年份 | 2024 | 2023-10-10 | ❌ 硬错误（E-2） |

## 五、核验结论

- 博客的**设计哲学与工程判断**（三原则、模型 > 框架、线性轨迹可复现）与源码结构一致，可作为学习主线。
- 博客的**三个可验证数字/事实**存在硬错误：Stars、SWE-bench 年份、快速开始 API；一个核心表述存在版本错位：tool-calling。
- 74% 成绩有官方背书，但缺少完整评测配置，引用时必须带“官方声明 + 单点成绩”限定。
- 知乎信源不可达，本知识包不声称覆盖其内容。

```{toctree}
:hidden:
:maxdepth: 3

../blog-source
../repo-source
```
