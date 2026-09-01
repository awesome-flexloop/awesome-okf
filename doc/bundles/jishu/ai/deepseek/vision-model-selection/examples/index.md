# 实战示例（Examples）

本目录包含视觉模型选型的实战示例，从成本意识、落地结构到决策树，均基于知识包事实（F-001 ~ F-036）推导。

| 示例 | 难度 | 核心内容 |
|------|------|---------|
| [成本-场景选型演练](cost-scenario-walkthrough.md) | ⭐入门 | 以"识别报错弹窗"为例演示任务档位匹配模型档位，附各场景价格对比表（F-013/F-015/F-019） |
| [视觉模型输出结构设计示例](pipeline-output-structure.md) | ⭐⭐基础 | 五字段结构化返回（OCR 文本/物体/位置关系/表格/不确定项）的 JSON Schema 与 Python 伪代码（基于 F-028 推导） |
| [选型决策树](selection-decision-tree.md) | ⭐⭐基础 | 按 F-033 口诀展开的 Mermaid 决策树，叶节点标注对应事实编号 |

> 注意：示例中的伪代码与 JSON 均为设计示意，非官方 API 文档；示例引用的价格为 2026-08 时点信息。

```{toctree}
:hidden:
:maxdepth: 7

cost-scenario-walkthrough
pipeline-output-structure
selection-decision-tree
```
