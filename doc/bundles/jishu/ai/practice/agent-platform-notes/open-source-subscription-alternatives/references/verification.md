---
type: Reference
title: "五个开源项目核验报告"
description: "按日期版本、成效数字、统计口径和引文归属四类清单记录证据与缺口"
tags: [核验, P0, 开源工具, 成本边界]
generated: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-11-30
sources:
  - { id: article, resource: "https://mp.weixin.qq.com/s/RLsYjpbzUxdQU4U6ylTkTw" }
  - { id: orca, resource: "https://github.com/stablyai/orca" }
  - { id: gev, resource: "https://github.com/bilawalsidhu/gods-eye-view" }
  - { id: hyperframes, resource: "https://github.com/heygen-com/hyperframes" }
  - { id: scrapling, resource: "https://scrapling.readthedocs.io/en/latest/" }
  - { id: openseo, resource: "https://github.com/every-app/open-seo" }
---

# 五个开源项目核验报告

> **状态：flagged。** 文章的星标、订阅价格、替代效果和节省金额没有在本次任务中全部通过同条件独立复现；这不表示项目功能或文章结论已被证伪。

## 日期与版本

| 对象 | 已读证据 | 结论 |
| --- | --- | --- |
| 微信发布时间 | 文章页面元信息 | 2026-09-20 11:30；仅确认文章发布时间 |
| Orca | GitHub 仓库 | 版本与星标随时间变化，文章 72.6k 不作为当前值 |
| God's Eye View | GitHub README/仓库 | 数据图层和密钥要求会随提交变化 |
| HyperFrames | GitHub README/发布页 | 文章称 0.8.x；命令需以当前 CLI 为准 |
| Scrapling | 官方文档/PyPI | Python >=3.10；发行版本持续变化 |
| OpenSEO | GitHub/官方站点 | 仍需 DataForSEO，托管计划和加价需复核 |

## 成效数字溯源

| 主张 | 来源 | 核验结论 |
| --- | --- | --- |
| 五个项目“替掉每月订阅” | 文章标题与总结 | 作者 framing，不能当作等价替换 |
| 爬虫 API 约 49 美元/月起 | 文章 | 单源价格对照，缺产品、地区和周期 |
| SEO 套件约 129–139 美元/月 | 文章 | 单源价格对照，缺统一套餐 |
| 视频工具 54.99 美元/月 | 文章 | 未指定产品，不作为市场基准 |
| OpenSEO 10 美元/月、28%加价 | 文章/第三方 | 需查官方现行计划与 DataForSEO 账单 |
| Scrapling 2.46 ms 自适应查找等基准 | 文章/官方材料 | 需按硬件、页面和版本复跑 |

## 统计口径

- 星标是 GitHub 时间点快照，不是采用量或生产稳定性。
- “免费”只描述软件许可证或基础路径，不覆盖地图、数据 API、云渲染、代理、带宽和运维。
- “替代”应拆成软件层、数据层、执行层与治理层；OpenSEO 和 God's Eye View 的数据层依赖尤其明显。
- 本地渲染和自托管把固定月费换成机器成本与维护责任，不能直接比较单价。

## 引文与归属

- Orca 的功能可由官方仓库交叉支持，但多 Agent 的实际并行收益取决于底层 Agent 账号、任务质量和审查能力。
- God's Eye View 的“实时”必须按图层解释；交通、摄像头位姿和发射回放存在模拟、估计或重建状态。
- HyperFrames 的确定性渲染是框架设计目标，不等于每个外部媒体输入都具备可复现字节输出。
- Scrapling 的反检测能力受目标站点、代理、法律与 robots.txt 约束；不应理解为无限制绕过。
- OpenSEO 的软件开源不代表 DataForSEO 数据免费，也不代表与 Semrush/Ahrefs 的覆盖和历史深度等价。

## 复核计划

在 `stale_after` 前复核五个官方仓库的版本、许可证、安装命令、星标和价格；对 OpenSEO 的数据费、God's Eye View 的地图配额、HyperFrames 云渲染和 Scrapling 反爬边界优先复查。没有创建自动定时任务。
