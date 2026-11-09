---
type: Reference
title: 参考资料索引
description: tvm-tirx 知识包参考层导航——编号事实、信源核验与洞察模式
tags: [tvm-tirx, 索引, 参考资料]
generated: { by: seven-concepts-cmd/1.1.0, at: 2026-11-09T00:00:00+08:00 }
verified: { by: process:seven-concepts-v, at: 2026-11-09T00:00:00+08:00 }
status: stable
stale_after: 2027-02-09
sources:
  - id: bundle-index
    resource: "/index.md"
---

# 参考资料索引

| 文档 | 内容 | 使用建议 |
|------|------|----------|
| [facts.md](facts.md) | F-001 ~ F-135 编号事实，按仓库/版本/文章/IR/扩展/编程模型/部署/两代/源码分组 | 引用具体声明时先查编号 |
| [sources.md](sources.md) | 信源台账、采集方式、26 项 P0 核验表、两代/文档 vs 源码冲突与覆盖边界 | 评估可信度与时效时优先读 |
| [insights.md](insights.md) | 九条洞察、五条可迁移模式、六视角对抗审查、质量门自检 | 做技术判断或方案设计时读 |

## 引用约定

- 正文中的 `[F-xxx]` 指向 [facts.md](facts.md) 的编号事实；
- 官方一手事实（A 级）可直接引用；
- 作者判断（B 级）需标注「作者认为」；
- 未证实主张（D 级）不得作为结论；
- 核验观察（C 级）只用于说明边界。

```{toctree}
:hidden:
:maxdepth: 7

facts
sources
insights
```
