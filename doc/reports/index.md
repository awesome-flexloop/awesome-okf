---
type: index
title: "报告索引"
description: "doc/reports 下任务级分析与复盘报告的索引、命名规范与导出约定"
generated: { by: "main-agent/lobsterai", at: "2026-11-24T13:42:16+08:00" }
status: stable
---

# 报告索引

本目录存放任务级报告（分析、对比、复盘），已接入站点导航：根目录 `index.md` 的「报告」toctree 指向本页，`conf.py` 的 `include_patterns` 已将 `reports/**` 纳入构建（全量与分片模式均生效）。

## 报告清单

| 日期 | 报告 | 类型 | 输入规模 | 格式 |
|---|---|---|---|---|
| 2026-11-24 | [pydata-sphinx-theme vs sphinx-book-theme 七概念对比报告](2026-11-24-pydata-vs-sbt-comparison.md) | 学习 + 洞察 + 对比 | 2 个知识包 / 53 篇 / 8,173 行 | Markdown |
| 2026-11-24 | [里程碑复盘：七概念对比报告任务](2026-11-24-seven-concepts-retro.md) | 里程碑复盘（R/I/E/V/A） | 单次任务 / 28 条事实 | Markdown |
| 2026-11-24 | [里程碑复盘：mystx 主题 P0–P4 与发布前收尾](2026-11-24-mystx-milestone-retro.md) | 里程碑复盘（R/I/V/E/A） | 主题仓 36 提交 / 23 篇文档 / 70 格视口矩阵 | Markdown |

## 各报告要点

### 2026-11-24 · 两主题对比报告

- 结论：PST 与 SBT 是同一技术栈的上下游，不是竞品；SBT 薄继承但高耦合，精确锁定 `pydata-sphinx-theme==0.23.0`。
- 结构：摘要 → 方法与证据 → 全景解剖 → 十二维对比 → 6 条洞察 → 3 个模式 → 对抗审查 → 选型与迁移 → 学习路径 → 附录。
- 核验：两包 0 断链；28 张表列数一致；未修改上游知识包。

### 2026-11-24 · mystx 主题里程碑复盘

- 结论：能力层一次成型，6 处事后修正里 4 处属「布局判定 + 可达性」类，而非组件实现或样式调优。
- 产出：3 条洞察（含四元组）、2 个可迁移模式、5 条原子行动项（A-01/A-02/A-04/A-05 待执行，A-03 待人工拍板）。
- 核验：`sphinx -W` 0 warning、`pytest` 46 passed、70 格视口矩阵横向溢出 0。

### 2026-11-24 · 里程碑复盘（对比报告任务）

- 结论：6 处返工中 4 处发生在 Markdown→Word 的格式契约，内容层 2 处；导出检查需脚本化。
- 产出：4 条洞察、2 个模式、4 条原子行动项（A-01/A-04 待执行，A-02/A-03 待确认）。
- 质量门：G1–G4 与 V 门通过。

## 命名与归档规范

1. 文件名：`YYYY-MM-DD-<主题>.md`，日期取交付日。
2. 每篇报告带 frontmatter：`type`、`title`、`description`、`generated`、`status`、`sources`。
3. 默认只交付 Markdown；`.docx` / `.pdf` 仅在明确要求时生成。
4. 新增报告后在本索引的「报告清单」追加一行，并补一节「要点」。

## 相关

- [知识库首页](../index.md)
- [Sphinx 文档工程生态](../bundles/jishu/document/sphinx/index.md)

```{toctree}
:hidden:
:maxdepth: 1

2026-11-24-pydata-vs-sbt-comparison
2026-11-24-seven-concepts-retro
2026-11-24-mystx-milestone-retro
```
