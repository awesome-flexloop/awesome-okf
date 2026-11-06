# 概念解析（Concepts）

本束为**概念骨架**（操作可复现性两问皆「否」，不设 `examples/`）。十篇分两轮：00~05 为首轮（信源为微信博文 + GitHub API + 官方 README 快照），06~09 为源码轮增量（信源为固定 commit `fb6a42c` 的本地源码），按「是什么 → 怎么架构 → 产出什么 → 能查什么 → 怎么走到真实数据 → 能迁移什么 → 源码里到底是什么」排列。

| 文档 | 内容 |
|------|------|
| [00 · 项目身份、热度时点与信源距离](00-what-is-wechat-intelligence-hub.md) | 官方身份核验数据、1976/2000/2764 三星标口径、「5 天」不可写成「创建后 5 天」、四层信源距离地图 |
| [01 · 本地优先只读架构与两个 Skill](01-local-first-readonly-architecture.md) | 四层目录、Reader + 情报产品分层、双 Skill、Profile 排序、⚠️「不重签名」范围勘误 |
| [02 · 旗舰交互式日报、双格式报告与四种视图](02-flagship-daily-report-and-four-views.md) | 四个入口、商单信号雷达、Markdown/HTML 双产物、四种视图与移动端；图注单源分层；🔬 源码轮修订：四入口名/移动端/回复草稿坐实，「四种视图风格」改判为设计期候选，见 [07-flagship-renderer-and-view-model.md](07-flagship-renderer-and-view-model.md)、[../references/verification.md](../references/verification.md) 源码轮追记 |
| [03 · 定向检索、重点联系人与行动项](03-search-contacts-and-actions.md) | 消息→状态→行动项三段链、五维检索、承诺/待回复、三条官方 Codex 示例 |
| [04 · 官方命令路径与全虚构 Demo 的差距](04-official-workflow-and-demo-gap.md) | install/demo/profile-init/Codex/产物五步逐字登记、骨架判定、Demo 能证明与不能证明 |
| [05 · 洞察、可迁移模式与采用边界](05-insights-and-adoption-boundaries.md) | I 阶段三条洞察、E 阶段 M1~M3 模式、AGPL-3.0-only 商业授权与四类采用边界 |
| [06 · 只读契约的代码级实现](06-readonly-contract-and-code-evidence.md) | 🔬 源码轮：`read_only` 统一置位、`mode=ro` 快照、零写入型函数、接入助手例外边界、模式 M4 |
| [07 · 旗舰渲染器与视图模型的源码实现](07-flagship-renderer-and-view-model.md) | 🔬 源码轮：`PAGE_SPECS` 四路由、移动端响应式分支、`theme-button` 机制、⚠️ 修正「四种视图风格」、模式 M5 |
| [08 · 源码架构分层与计数口径](08-source-code-architecture-and-counts.md) | 🔬 源码轮：双 CLI 分层、30/36/37/73 四个口径、29 vs 30 工具数差、tag 落后 13 提交、模式 M6 |
| [09 · 报告安全模型与源码级采用边界](09-safety-and-adoption-boundaries-from-source.md) | 🔬 源码轮：nh3 白名单 + 哈希 CSP 失败关闭、回复草稿确定性模板、语气学习边界、模式 M7 |

> **轮次标记**：🔬 = 2026-11-06 源码轮增量，事实编号 F-058~F-101，见 [../references/source-code-map.md](../references/source-code-map.md)。

```{toctree}
:maxdepth: 1
:caption: 概念文档

00-what-is-wechat-intelligence-hub
01-local-first-readonly-architecture
02-flagship-daily-report-and-four-views
03-search-contacts-and-actions
04-official-workflow-and-demo-gap
05-insights-and-adoption-boundaries
06-readonly-contract-and-code-evidence
07-flagship-renderer-and-view-model
08-source-code-architecture-and-counts
09-safety-and-adoption-boundaries-from-source
```
