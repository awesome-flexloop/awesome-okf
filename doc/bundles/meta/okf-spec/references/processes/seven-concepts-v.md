---
type: Reference
title: 进程登记：seven-concepts-v（对抗审查）
description: process:seven-concepts-v 的登记文档。定义该进程的语义、运行方式与复核路径，使本 bundle 的 verified.by 指向的自动化进程可被独立第三方复现核验，从而确立 machine-confirmed 信任层级。
tags: [okf, process, registry, review]
generated: { by: reference_agent/trae-glm, at: 2026-08-21T00:00:00Z }
verified: { by: process:seven-concepts-v, at: 2026-08-21T00:00:00Z }
status: stable
sources:
  - id: okf-spec
    resource: /references/okf-spec.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 进程登记：凡七对抗审查（seven-concepts-v）

本文件登记本 bundle 中 `verified.by` 值为 `process:seven-concepts-v` 所用的自动化进程，使其满足 §7 actor 约定中 `process:<id>` 要求的"可由独立第三方复核"语义。

## 进程标识

- **标识**：`process:seven-concepts-v`
- **类型**：自动化分析进程（非一次性会话）
- **定义**：以"方法论编排 · 七概念"之 **V（Adversarial Review，对抗审查）** 阶段对目标文档执行多视角证伪的进程。视角覆盖：魔鬼代言人、新人、老板、未来。
- **运行方式**：通过 SpecWeave 的 `seven-concepts-cmd` 技能加载，执行 V 阶段 4 视角对抗审查，输出 P0-P3 分级问题清单与采纳/拒绝交契约。

## 复核路径（如何复现）

任意第三方可按以下路径复现本进程对任一文档的核验结论：

1. 加载 `seven-concepts-cmd` 技能（SpecWeave `.agents/skills/seven-concepts-cmd`）。
2. 对目标文档执行 V 阶段对抗审查，覆盖魔鬼代言人／新人／老板／未来四视角。
3. 检查产物是否符合 V 质量门：≥5 条具体建议、≥2 条可采纳修正、覆盖 ≥3 视角。
4. 比对结论与本文档 `verified.at` 所指核验事件记录（见 `log.md`）。

## 核验记录

| 日期 | 范围 | 结论 |
|------|------|------|
| 2026-08-21 | `bundles/okf-spec` 全 bundle（19 个含 status 文档） | 对抗审查通过；P1（信任元数据真实化）与 P2（溯源自包含）修正已落地，见 `log.md` |

> **说明**：`verified` 表征"文档经本进程确认"这一事件（machine-confirmed）。内容本身的语义正确性仍以其 `sources` 指向的 [references/okf-spec.md](okf-spec.md) 为权威信源。

## 相关概念

- [可认证计算之 verification 与 attestation 之别](../concepts/attested-computations.md)

[^okf-spec]: OKF SPEC v0.2 规范，见本 bundle 信源登记 [references/okf-spec.md](/references/okf-spec.md)。