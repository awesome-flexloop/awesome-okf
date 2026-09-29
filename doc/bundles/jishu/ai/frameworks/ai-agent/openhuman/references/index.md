# 信源登记簿（References）

本目录收录 OpenHuman 知识包的博文事实清单与 P0 核验报告。

## 信源清单

| 编号 | 信源 | 类型 | 覆盖事实 |
|------|------|------|---------|
| R1 | [博文原文](article-source.md) | 开源先驱微信公众号，2026-07-28 | F-001 ~ F-064（64 条：博文 42 + 核验补充 22） |
| R2 | [核验报告](verification.md) | GitHub 仓库实测 + 官方 GitBook + openhuman.dev | 12 项 P0（6✅ 6⚠️ 0❌，勘误六条） |

## 事实编号索引

| 事实编号 | 简述 | 文档 |
|---------|------|------|
| F-001~F-003 | 博文元信息与性质 | article-source |
| F-004~F-007 | 热度与许可证（博文口径） | 00-what-is-openhuman |
| F-008~F-013 | 产品定位与三大能力 | 00/01/02 |
| F-014~F-021 | 四痛点、Memory Tree、TokenJuice | 01-memory-tree-and-tokenjuice |
| F-022, F-061 | 竞品对照（博文/官方两套表） | 03-landscape-and-tradeoffs |
| F-023~F-029 | 特色设计与技术栈 | 02-runtime-and-agent-design |
| F-030~F-032 | 安装与上手 | 00-what-is-openhuman |
| F-033~F-037 | 短板与风险 | 03-landscape-and-tradeoffs |
| F-038~F-041 | 作者观点（显式分层） | 03-landscape-and-tradeoffs |
| F-043~F-064 | 核验补充事实（2026-09-16） | verification + 各概念篇 |

## 可信度说明

| 等级 | 事实编号 | 说明 |
|------|---------|------|
| ✅ 已核验 | F-007/F-045, F-043, F-048, F-051, F-053, F-054, F-058, F-060, F-061 | GitHub/官方文档直接证实 |
| ⚠️ 口径漂移/单源 | F-004~F-006, F-011, F-015, F-022, F-028, F-029, F-035, F-052, F-056, F-057, F-062, F-064 | 数字老化、弱源单源或官方未见 |
| 📝 作者观点 | F-010, F-036, F-038~F-041 | 开源先驱/豆芽菜小萌的归纳与建议 |
| 📊 博文测算 | F-020, F-021 | 美元金额与细分省幅为博文假设推算 |

```{toctree}
:hidden:
:maxdepth: 2

article-source
verification
```
