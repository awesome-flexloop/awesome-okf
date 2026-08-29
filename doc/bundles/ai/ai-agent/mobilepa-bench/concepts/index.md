# 概念文档（Concepts）

本目录包含 mobilepa-bench 知识包的核心概念文档：前四篇按"基准性质 → 能力维度 → 判分机制 → 榜单解读"递进覆盖 MobilePA-Bench 本体；第五篇为并入的 Qwen-UI-Agent 网站技术栈简析，与基准本体无依赖、可独立跳读。

## 学习路径

| 序号 | 文档 | 核心问题 |
|------|------|---------|
| 00 | [基准概览](00-benchmark-overview.md) | MobilePA-Bench 是什么？为什么仓库里没有评测代码？如何参与评测？ |
| 01 | [四能力维度与任务分布](01-capability-dimensions.md) | 四个维度考什么？1,705 个任务怎么分布？有哪些代表案例？ |
| 02 | [固定验证策略与六类 checker](02-verification-policy.md) | 每个任务怎么判分？六类 checker 如何分布？哪些是公开样例？ |
| 03 | [榜单解读](03-leaderboard-analysis.md) | 总分公式是什么？13 个模型表现如何？引用分数要注意什么口径？ |
| 04 | [Qwen-UI-Agent 网站技术栈简析](04-qwenuiagent-website.md) | 该网站仓是什么性质？用了什么技术栈？与实现代码仓什么关系？ |

### 路径建议

```
线性主线：00（性质与定位）→ 01（四维与任务分布）→ 02（判分机制）→ 03（榜单解读）
独立支线：04（网站工程，与基准本体无依赖，可随时跳读）
依赖关系：03 依赖 01/02 建立的维度与 checker 概念
```

```{toctree}
:hidden:
:maxdepth: 7

00-benchmark-overview
01-capability-dimensions
02-verification-policy
03-leaderboard-analysis
04-qwenuiagent-website
```
