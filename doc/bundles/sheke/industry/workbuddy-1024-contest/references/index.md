---
okf_version: "0.2"
type: index
title: "信源参考"
description: "事实底账与核验报告——本知识包的事实唯一来源与证据等级依据。"
tags: ["workbuddy-1024-contest", "信源参考"]
generated: { by: "seven-concepts-cmd", at: "2026-10-24T00:00:00Z" }
verified: [{ by: "process:seven-concepts-v", at: "2026-10-24T00:00:00Z" }]
status: flagged
stale_after: "2026-11-10"
sources:
  - id: facts
    resource: "/references/facts.md"
---

# 信源参考

本目录是本知识包的证据层，共 2 篇：

| 文档 | 作用 |
|---|---|
| [事实底账 F-001~F-117](facts.md) | **本包唯一事实来源**。**121 条编号事实**（F-001~F-117 + 补录 F-056b / F-076b / F-093b / F-093c）+ **19 条口径缺口**（G-01~G-19）+ **10 条采集元数据**（M-01~M-10），逐条标注信源定位 |
| [核验报告](verification.md) | **42 项核验结论**（C-01~C-42）、勘误清单、证据四层分级、单源清单、缺口影响评估、**复核触发检测表 T-1~T-9** 与 flagged 判定依据 |

## 引用纪律

1. **正文事实一律挂 F 编号**——F 编号只能从[事实底账](facts.md)取，正文中出现的任何数字若未在底账登记，即为编造。
2. **推断必须显式标注**——机制洞察与方案设计部分标注「洞察/推断」，不与事实混排。
3. **缺口必须显式引用**——官方未给出的信息登记为 G 编号，正文不得据缺口推演结论。
4. **单源必须随附**——引用本包任何事实时，须一并转述"活动页单源"这一证据等级与 `stale_after: 2026-11-10` 的时效边界。

```{toctree}
:hidden:
:maxdepth: 1

facts
verification
```
