# 示例与工具

本目录四篇均为**编者构造的学习工具**，不是对原文操作的复现。主文是会议后多人访谈加记者述评，没有输入输出样例、没有版本、没有实测步骤；按「操作可复现性两问」不生成操作型示例，也不含创业、择业、投资或裁撤建议（对抗审查·编者视角采纳项，见 [P0 核验报告 §四](../references/verification.md)）。

| 工具 | 用途 | 对应概念 |
|---|---|---|
| [01 · 单位经济算例](01-unit-economics-worksheet.md) | 用主文数字练习口径分离：成本结构、产量×平均单价、两种人效、假设题敏感性 | [01 成本结构](../concepts/01-cost-structure-collapse.md)、[03 第一性原理](../concepts/03-attention-economics-first-principles.md) |
| [02 · 判据清单：读行业预测的四问](02-decision-checklist.md) | 引用行业断言前的四步核对：陈述分层、口径分母、可证伪性、总量/分配层 | [00 证据边界](../concepts/00-reading-map-and-evidence-boundary.md)、[02 内容判断力](../concepts/02-content-judgement-as-scarce-asset.md)、[05 预测边界](../concepts/05-historical-analogy-and-prediction-boundary.md) |
| [03 · 进阶：两层单位经济](03-two-layer-unit-economics.md) | 把总量/分配两层模型写成可复算方程组：分配恒等式、成本率阈值、盈亏平衡、证伪清单与跨领域参数替换模板 | [03 第一性原理](../concepts/03-attention-economics-first-principles.md)、[01 成本结构](../concepts/01-cost-structure-collapse.md) |
| [04 · 补篇：把「内容判断力」写进方程](04-judgement-as-parameter.md) | 替换 H3 均匀分配假设：注意力份额 `φ`、判断力失效条件、广撒网不等式与归一化例题 | [02 内容判断力](../concepts/02-content-judgement-as-scarce-asset.md)、[03 第一性原理](../concepts/03-attention-economics-first-principles.md) |

> **阅读顺序**：01 先建立「哪些口径不能混」，03 再问「口径固定后结构如何决定方向」，04 追问「差异化何时把这个方向改写」，02 用于在引用前收口。**三条参数化路径**（01 口径分离 / 03 结构法·阈值法 / 04 份额法）各自参数化隔离，**禁止互相代入数值**。

```{toctree}
:hidden:
:maxdepth: 2

01-unit-economics-worksheet
02-decision-checklist
03-two-layer-unit-economics
04-judgement-as-parameter
```

## 使用边界（总声明）

- **算术自洽 ≠ 数据真实**：`01` 的输入全部是受访者自述单源（⭕）或假设计算（E-08），任何输出结果都不是行业规模、均价或收益的估计。
- **符号 ≠ 实测**：`03` 的 `A/k/n/s/F/α` 与 `04` 的 `θ/γ/φ` 均为编者符号或读者自填，原文一个都没给；其输出是条件性恒等式与判定条件，不是预测，也不是对任何公司、岗位或个人能力的测量。`04` 的 `θ` 尤其不是能力测评分数，权重函数形式只是登记在案的假设。
- **不判定真伪、不产出结论**：`02` 只做分层与登记，不输出「可信/不可信」，参数由使用者自行固定并公开。
- **不跨口径**：总量流水/单部爆款、批量剧/精品剧、部·人月/营收·人、实测/预估、结构法/阈值法五组口径各自独立（E-02、E-03、E-04、E-07、E-11、E-12）；01 / 03 / 04 三条参数化路径的数值同样不得串联，04 只改 03 的 H3、沿用其 H2。
- **不构成建议**：本目录不含任何行动项、评分、排序或决策阈值；不构成创业、择业、投资或裁撤组织的依据。
- **理论归概念层**：事实、论证与引用规则见 [concepts/](../concepts/index.md) 与 [references/](../references/index.md)。
