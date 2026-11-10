---
type: Log
title: "生成日志：从三份信源到 19 文件知识包"
description: "mini-SWE-agent 知识包的 R→I→E→V→C 链路记录、CMD-LOG、G1-G4 质量门、19 文件清单、4 条勘误与信源缺口"
tags: [日志, 七概念, R-I-E-V-C, 质量门, mini-swe-agent, 勘误]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T17:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: blog-mini-swe-agent
    resource: https://lukaxiya.github.io/coding-agent-blog/posts/mini-swe-agent/
    title: "博客原文"
  - id: github-mini-swe-agent
    resource: https://github.com/SWE-agent/mini-swe-agent
    title: "官方仓库 v2.4.6"
  - id: spec
    resource: .trae/specs/mini-swe-agent-okf-wiki/spec.md
    title: "本次任务 spec"
---

# 生成日志：从三份信源到 19 文件知识包

## CMD-LOG

```text
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S0 | event=CMD_START
  session=sc-20261110-mini-swe-agent
  msg=方法论编排开始：全面学习 mini-SWE-agent 并生成 OKF wiki
  ctx={"scenario":"knowledge","topic":"mini-swe-agent","depth":"deep"}

[CMD-LOG] | step=S1 | event=SCENARIO_DETECTED
  scenario=knowledge（知识沉淀）
  chain=R→I→E→V→C（V 强制）

[CMD-LOG] | step=S2 | event=SOURCE_CHECK
  blog=ok（5.7 KB）
  zhihu=failed（403/40362/404）
  repo=ok（v2.4.6 / 04d809ce）

[CMD-LOG] | step=S3 | event=CHAIN_SELECTED
  chain=R→I→E→V→C
  target=projects/awesome-okf-xs/doc/bundles/jishu/ai/frameworks/ai-agent/mini-swe-agent/

[CMD-LOG] | step=S4 | event=GATE_PASSED
  G1=事实无因果词（事实表只记录“是什么”，观点单列）
  G2=洞察四元组完整（项目定位/证据/反常识/行动见 00 与 07）
  G3=模式可迁移（七条经验均给迁移动作与检查清单）
  G4=行动项原子化（见 spec/tasks.md）

[CMD-LOG] | step=S5 | event=CHAIN_COMPLETED
  files=19
  facts=90
  errata=4
  source_gap=1（知乎）
```

## R→I→E→V→C 链路

| 阶段 | 动作 | 产出 |
|---|---|---|
| **R（复盘/事实）** | 抓博客、克隆仓库、读源码与 docs、抓 GitHub API 与 arXiv、登记 F-001 ~ F-090 | `references/blog-source.md`、`references/repo-source.md` |
| **I（洞察）** | 识别三条设计原则、三协议、v1/v2 错位、74% 口径边界；判定“源码教程 + 博客核验”混合型 | 8 篇 concepts 的骨架 |
| **E（萃取/执行）** | 先写 references，再写 concepts/examples，最后写各级 index；把七条经验萃取为可迁移模式 | 19 个文件 |
| **V（对抗审查）** | 四视角审查 + 双份 F 编号对账 + 链接/toctree/UTF-8/计数门禁 | `references/verification.md`、spec/review.md |
| **C（原子提交）** | 子模块显式文件提交 → 主仓库 spec 提交 → 子模块指针更新 | 见 git log |

## 质量门

| 门 | 检查 | 结果 |
|---|---|---|
| G1 | 事实表是否混入“因为/导致/所以”等因果判断 | ✅ 事实与观点分列；作者判断标“作者观点” |
| G2 | 洞察是否含“陈述/证据/反常识/行动” | ✅ 00 的项目定位、01 的三原则、07 的七条经验均给证据与行动 |
| G3 | 模式能否迁移到非当前领域 | ✅ 七条经验均配迁移动作与检查表 |
| G4 | 行动项是否单一职责、可验证 | ✅ 见 `spec/tasks.md` 的 R/I/E/V/C 清单 |
| V 门 | 审查意见是否 ≥5 条且有实质修正 | ✅ 4 条硬勘误 + 6 条单源边界 + 3 条结构修正 |

## 文件清单（19）

| # | 文件 | 类型 |
|---|---|---|
| 1 | `index.md` | bundle 根索引 |
| 2 | `log.md` | 本文件 |
| 3 | `concepts/index.md` | 目录索引 |
| 4 | `concepts/00-project-overview.md` | 概念 |
| 5 | `concepts/01-design-philosophy.md` | 概念 |
| 6 | `concepts/02-architecture-and-code.md` | 概念 |
| 7 | `concepts/03-execution-environments.md` | 概念 |
| 8 | `concepts/04-model-integration.md` | 概念 |
| 9 | `concepts/05-configuration-and-extension.md` | 概念 |
| 10 | `concepts/06-benchmarks-and-boundaries.md` | 概念 |
| 11 | `concepts/07-transferable-lessons.md` | 概念 |
| 12 | `examples/index.md` | 目录索引 |
| 13 | `examples/01-install-and-cli.md` | 示例 |
| 14 | `examples/02-python-bindings.md` | 示例 |
| 15 | `examples/03-swebench-batch.md` | 示例 |
| 16 | `references/index.md` | 目录索引 |
| 17 | `references/blog-source.md` | 信源 |
| 18 | `references/repo-source.md` | 信源 |
| 19 | `references/verification.md` | 核验 |

> 计数口径：目录索引不计入“概念/示例/信源”篇数；bundle 表行写 `8+3+3=14`，另有 index 与 log 两篇。

## 勘误与信源缺口

| 编号 | 内容 | 处理 |
|---|---|---|
| E-1 | 博客 26k+ Stars → 实际 9,496 | 正文用实测值 |
| E-2 | 博客 SWE-bench 2024 → 实际 2023-10-10 | 正文改年份 |
| E-3 | 博客 `MiniSWEAgent`/`result.passed`/`result.patch` 不存在 | 示例用真实 `DefaultAgent` |
| E-4 | 博客“无工具/不用 tool-calling” → v2 默认 tool calling | 标注 v1/v2 边界 |
| S-1 | 知乎文章 403/404 | 明示未使用，不虚构观点 |

## 幂等与重跑

- 开工前检查：目标目录不存在，无覆盖风险。
- 索引计数：先读现值（729 束 / 9 域 / 64 组），新增 1 束后改为 730；ai-agent 63→64、frameworks 97→98、ai 296→297、jishu 534→535。
- 重跑策略：若目录已存在，先读 `log.md` 与 `index.md`，判定“补核验”还是“重建”，禁止静默覆盖。

## 未做与边界

- 未在本机 `pip install` 或跑 SWE-bench（缺 API Key / x86 Docker）。
- 未复现 74%；只核对官方声明与博客转述。
- 未使用知乎文章内容。
- 未修改并发会话生成的其它 bundle。
