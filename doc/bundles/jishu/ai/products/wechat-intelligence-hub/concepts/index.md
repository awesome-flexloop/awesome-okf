# 概念解析（Concepts）

本束为**概念骨架**（操作可复现性两问皆「否」，不设 `examples/`）。六篇按「是什么 → 怎么架构 → 产出什么 → 能查什么 → 怎么走到真实数据 → 能迁移什么」排列。

| 文档 | 内容 |
|------|------|
| [00 · 项目身份、热度时点与信源距离](00-what-is-wechat-intelligence-hub.md) | 官方身份核验数据、1976/2000/2764 三星标口径、「5 天」不可写成「创建后 5 天」、四层信源距离地图 |
| [01 · 本地优先只读架构与两个 Skill](01-local-first-readonly-architecture.md) | 四层目录、Reader + 情报产品分层、双 Skill、Profile 排序、⚠️「不重签名」范围勘误 |
| [02 · 旗舰交互式日报、双格式报告与四种视图](02-flagship-daily-report-and-four-views.md) | 四个入口、商单信号雷达、Markdown/HTML 双产物、四种视图与移动端；图注单源分层 |
| [03 · 定向检索、重点联系人与行动项](03-search-contacts-and-actions.md) | 消息→状态→行动项三段链、五维检索、承诺/待回复、三条官方 Codex 示例 |
| [04 · 官方命令路径与全虚构 Demo 的差距](04-official-workflow-and-demo-gap.md) | install/demo/profile-init/Codex/产物五步逐字登记、骨架判定、Demo 能证明与不能证明 |
| [05 · 洞察、可迁移模式与采用边界](05-insights-and-adoption-boundaries.md) | I 阶段三条洞察、E 阶段 M1~M3 模式、AGPL-3.0-only 商业授权与四类采用边界 |

```{toctree}
:maxdepth: 1
:caption: 概念文档

00-what-is-wechat-intelligence-hub
01-local-first-readonly-architecture
02-flagship-daily-report-and-four-views
03-search-contacts-and-actions
04-official-workflow-and-demo-gap
05-insights-and-adoption-boundaries
```
