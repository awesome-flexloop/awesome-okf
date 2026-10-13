---
okf_version: "0.2"
type: Reference
title: "Plane 信源登记簿"
description: "Plane 知识包信源层——博文事实清单（F-001~F-057 双份登记）与 P0 核验报告（含勘误）"
---

# 信源登记簿

| 文档 | 内容 | 何时读 |
|------|------|--------|
| [博文事实登记](article-source.md) | F-001 ~ F-057 逐条登记：博文原话口径、位置、级别、性质标注 | 引用任何数字/结论前 |
| [核验报告](verification.md) | 18 项 P0/P1 核验结果（✅/⚠️/❌）+ 勘误四张清单 + 时效边界 | 判断可信度与复核时点 |

## 信源分层

| 层 | 信源 | 性质 |
|----|------|------|
| L1 一手 | GitHub makeplane/plane README、仓库 LICENSE.txt、docker-compose.yml | 项目方官方 |
| L1 一手 | developers.plane.so（Self-hosting 101 / editions-and-versions / docker-compose / configuration） | 项目方官方部署文档 |
| L1 一手 | docs.plane.so（Native Integrations / organize-and-view-work） | 项目方官方产品文档 |
| L2 二手 | 微信公众号「芋道源码」2026-10-12 推文（本包转化对象） | 自媒体转述 |
| L3 旁证 | plane.so 官方博客对比文、Besthub / zendot / switchtools 等第三方综述 | 交叉参照 |

```{toctree}
:hidden:
:maxdepth: 2

article-source
verification
```
