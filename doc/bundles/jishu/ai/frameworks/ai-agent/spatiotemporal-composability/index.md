---
okf_version: "0.2"
type: bundle
title: "时空可组合性编程范式 · 论文精读"
description: "arXiv:2608.25512v1《A Programming Paradigm for Spatiotemporal Composability》系统化中文教程——可逆效应、响应式协同效应、统一上下文、动态组合演算与元理论"
tags: [spatiotemporal-composability, cordis, formal-methods, plugin-architecture, arxiv-2608-25512]
sources:
  - id: arxiv-abs
    resource: https://arxiv.org/abs/2608.25512
    title: arXiv 元数据页
  - id: arxiv-pdf
    resource: https://arxiv.org/pdf/2608.25512v1
    title: 论文 v1 全文 PDF（92 页）
generated: { by: "process:seven-concepts-cmd/knowledge", at: "2026-11-21T09:10:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-21T09:10:00+08:00" }
status: stable
stale_after: 2027-02-28
---

# 时空可组合性编程范式 · 论文精读

> ⚠️ **版本提示**：本包依据 **arXiv:2608.25512v1**（2026-08-26 提交，92 页 / 1 图 / 2 表）。论文为活跃修订中的预印本，后续版本可能改动证明细节与实现描述；全包到期复核日 **2027-02-28**。既有 [cordis 背景理论章节](../cordis/references/background-paper.md) 记录的是更早的草稿（2026-08-13、约 88 页），属版本差异 E-04，本包不改写它。

## 这个包讲什么

论文把插件系统的两个老大难问题形式化：**卸载时怎么把共享环境的修改干净退回**（时间可组合性）、**依赖变化时谁该跟着动**（空间可组合性）。答案是三层结构：把每次副作用与它的逆绑定在同一处产生（可逆效应），把依赖登记为带类型的键并随变化通知（响应式协同效应），再把两者装进同一个递归上下文并写出可证的装卸规则（动态组合演算）。

本包是**论文精读教程**，不是框架源码教程：

| 需要什么 | 去哪里 |
|---|---|
| 定义、定理、演算规则逐条讲 | 本包 [概念教程](concepts/index.md)（12 篇） |
| 理论符号 → API 的对照 | [理论符号 ↔ Cordis API 映射全表](references/theory-api-mapping.md) |
| TypeScript 源码机制（`ctx.effect`、`@Inject`、`disposable`） | [cordis/concepts/effects-coeffects.md](../cordis/concepts/effects-coeffects.md) |
| 框架总览与可运行示例 | [cordis](../cordis/index.md) |
| Agent 框架落地 | [deepseek-harness](../deepseek-harness/index.md) |

## 骨架说明

- `concepts/` 12 篇原子化教程；`references/` 6 份信源与核验文档；`log.md` 记录生成与复核动作。
- **不设 `examples/`**：论文提供的是形式模型与伪代码，没有可复现的安装、配置、调用或实测流程。按「操作可复现性两问」判据，宁可明确说明「不含可运行示例与部署实测」，也不放占位目录。表 2 与 Algorithm 1–10 是**论文给出的伪代码索引**，不是可执行代码。
- 全部事实以 `F-xxx` 编号标注，双份登记机械比对一致（F-001…F-072，72 条，无重复无跳号）。

## 信任声明

- **信源**：全部 F 编号事实的唯一权威依据是 arXiv v1 PDF 与 abs 元数据页；Pith、BestHub 等二手材料仅用于交叉核验转述口径，不作事实依据。检出并登记四处口径差异（E-01 数据百分比化、E-02 九个规则被写成五个原语、E-03 小节名与定理名混用、E-04 草稿/v1 版本差异），见 [P0 核验报告](references/verification.md)。
- **证据等级**：Koishi 案例（四年、4000+ 插件）是**单生态、单宿主语言、观察性**证据，论文 Threats to validity 明确其**非对照实验**；论文把自我演化 Agent Harness 列为 §8 **未来验证方向**，不是已完成的实证。本包不宣称跨项目已验证，萃取模式标 `maturity: L1`。
- **保证边界**：运行时**不校验 witness**（逆是否有效、键上操作是否可交换均为组件作者义务）；恢复只到观测等价，不覆盖已越界的 emission；Theorem 73 / 80 均带前提。详见 [08 · 元理论](concepts/08-metatheory.md) 与 [11 · 常见误读](concepts/11-learning-path.md)。
- **生成流程**：七概念方法论场景 4「知识沉淀」，链路 R→I→E→V→A→C，`depth=deep`，四视角对抗审查 8 条意见全部采纳并落到文件。

## 快速入口

- 只想判断相关性 → [00 · 总览](concepts/00-overview.md)
- 想看可迁移模式 → [回程同源](references/pattern-return-ticket-with-effect.md)
- 想查某条事实的原文页码 → [论文事实台账](references/facts.md)
- 选阅读路线 → [11 · 学习路径](concepts/11-learning-path.md)

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
references/index
log
```
