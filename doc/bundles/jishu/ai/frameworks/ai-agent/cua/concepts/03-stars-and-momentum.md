---
type: Concept
title: Stars 趋势与社区活跃度
description: Cua 的 GitHub Stars 趋势（2026-09-20 博文快照 vs 2026-10-10 官方时点）、Forks/Issues 快照、发布节奏、语言构成、增长态势解读
tags: [Cua, GitHub, Stars, Trending, 社区, 发布节奏]
generated: { by: "blog-article-to-okf-bundle", at: "2026-10-10T10:50:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: wechat-article-finops-cua
    resource: https://mp.weixin.qq.com/s/6FaVJOhGomsSn43RdFMRlg
    title: 《开源精选 | Cua》（FinOps实战，2026-09-26）
  - id: github-api-cua
    resource: https://api.github.com/repos/trycua/cua
    title: GitHub API：trycua/cua 仓库元数据
---

# Stars 趋势与社区活跃度

> **事实基础**：本文所有具体数据与声明均带 F 编号，完整事实清单见 [references/article-source.md](../references/article-source.md)，核验结论见 [references/verification.md](../references/verification.md)。

## 1. 硬数据快照

博文给出的数据采集于 **2026-09-20**，来源为 GitHub API 与 Trending 页面（F-016~F-020）：

| 指标 | 博文快照（2026-09-20） | 官方时点（2026-10-10） |
|------|------------------------|------------------------|
| 总 Stars | 24,432 | **29,189** |
| Forks | 1,681 | **2,061** |
| 今日新增 | +859（Trending 日榜第 2） | —（时点数据） |
| 创建时间 | 2025-01-31 | 2025-01-31T15:02:49Z（✅ 一致） |
| 开放 Issues | 1,032 | **1,149** |

> ⚠️ **时点差异（F-055）**：Stars/Forks/Issues 为动态数字，博文快照与 2026-10-10 GitHub API 实测值存在自然增长差异，非事实错误。引用时须带时点。日增 +859 / Trending 第 2 为当日快照，无法事后精确复核；多方 2026-09-19~21 报道（如 9 月 21 日 +1018、25.2k 星）佐证博文快照合理（F-018）。

## 2. 增长态势解读

博文对数据的解读（作者观点，F-021~F-022）：

- **单日 +859 star 约占总量的 3.5%**——在 AI 基础设施类项目中属于高位，说明"让 Agent 用电脑"这个方向正在被开发者社区快速认可（F-021）。
- **一年半攒下 2.4 万 star，平均每月超过 1,300**——属于稳步爬升后借势爆发的典型曲线（F-022）。

这些是作者基于快照的推算，反映的是社区情绪，而非项目质量本身的可验证指标。

## 3. 社区活跃度

### 发布节奏

Cua 的 Release 节奏相当惊人（F-023）：

- **cua-driver-rs 保持每日 nightly 发布**——2026-09-14 到 09-19 一天不落；
- 最近的正式版是 **2026-09-15 发布的 sandbox v0.8.0**（F-024）。

> ✅ **核验（F-058、F-060）**：newreleases.io 确认 `sandbox-v0.8.0` 于 2026-09-15 发布，piwheels 记录 cua-sandbox 0.8.0 于同日 16:49:04 UTC 发布；nightly-cua-driver-rs-v0.28.3 连续 20260917/20260918/20260919 发布，与博文描述一致。

每日构建 + 高频正式版，说明核心团队全职投入、迭代飞快（F-023）。

### 工程化生态

项目还拿到了 **Trendshift 趋势徽章**，Discord 社区、官方博客、文档站一应俱全（F-025）。2026-10-10 GitHub API 显示项目仍有 **94 个 subscribers**，最近 push 时间为 2026-10-10T00:58Z，维护高度活跃（F-055）。

### 语言构成

仓库主语言与核心组件横跨 **HTML/Rust/Swift/Python**（F-026）：

- 博文 2026-09-20 快照：主语言标记为 HTML（文档站与演示页）；
- 官方 2026-10-10 API：主语言为 Rust（F-057，时点差异）。

核心组件构成不变：Rust（cua-driver-rs 驱动）、Swift（Lume 虚拟化）、Python（Sandbox SDK、CUA-S1、Bench）——这种"多语言各取所长"的架构选择，侧面印证团队对性能与生态的平衡考量（F-026）。

---

## 参考

- 完整事实清单：[references/article-source.md](../references/article-source.md)
- 核验报告：[references/verification.md](../references/verification.md)
- 生态与许可证：[02-ecosystem-and-licensing.md](02-ecosystem-and-licensing.md)
- 快速上手：[04-getting-started.md](04-getting-started.md)