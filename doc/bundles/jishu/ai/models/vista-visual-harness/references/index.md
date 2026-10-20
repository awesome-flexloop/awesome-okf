---
type: reference
title: "信源参考"
description: "VISTA 知识包的信源参考目录——博文事实清单、P0 核验报告与勘误、知识地图、信源登记与采集边界。"
tags: [vista, references, provenance]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: knowledge-map
    resource: /references/knowledge-map.md
  - id: source-manifest
    resource: /references/source-manifest.md
---

# 信源参考

本目录承载 VISTA 知识包的**可溯源层**：所有具体声明都能沿 F 编号回溯到博文原文或权威源，并附带核验结论与勘误。

| 文档 | 内容 |
|------|------|
| [article-source.md](article-source.md) | **事实登记**：F-001~F-044 博文事实 + F-045~F-076 权威核验补充事实，逐条标注类别、声明、来源与核验状态 |
| [verification.md](verification.md) | **核验报告**：18 项 P0 声明的逐条对照结论、8 项勘误（E-1~E-8）、RHAE 官方计分口径、"不可省略的限定"三件套、未覆盖边界 |
| [knowledge-map.md](knowledge-map.md) | **知识地图**：事实层 / 机制层（M1~M5 执行者洞察，标注假设）/ 迁移层（T1~T5 中立可逆实践）三层拆分 |
| [source-manifest.md](source-manifest.md) | **信源登记**：公众号所有权信号、发布与访问时点、全部权威源坐标与角色、采集停止规则与未采集项 |

## 阅读顺序

1. 先读 [source-manifest.md](source-manifest.md) 确认信源可信度与边界；
2. 再读 [article-source.md](article-source.md) 查具体数字与机制的事实出处；
3. 涉及争议结论时读 [verification.md](verification.md) 看核验结论与勘误；
4. 想看推论与可迁移做法时读 [knowledge-map.md](knowledge-map.md)。

```{toctree}
:hidden:
:maxdepth: 2

article-source
verification
knowledge-map
source-manifest
```
