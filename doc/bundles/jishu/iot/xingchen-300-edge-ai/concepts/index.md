# 概念地图（Concepts）

按三层知识拆分组织：**事件事实层 → 机制原理层 → 生态/边界层**，建议按序阅读。

| 层级 | 文档 | 解决的问题 |
|------|------|-----------|
| 事件事实层 | [00 星辰300平台与四大实测用例](00-platform-and-demos.md) | 平台是什么、由什么构成、何时公开、演示了什么 |
| 机制原理层 | [01 CPU+NPU 异构设计](01-cpu-npu-heterogeneous-design.md) | CPU/NPU 如何分工；Helium 5×/15× 数字勘误；U55 规格区间；Vela 图分区如何让 Conformer 跑通；Corstone 组合与商用先例 |
| 生态/边界层 | [02 五个演示模型档案与可信边界](02-model-zoo-and-trust-boundaries.md) | YOLO-Fastest/wav2letter/Conformer/kws-micronet/SESR 开源档案；软件栈；厂商自述等四条可信边界 |

```{toctree}
:hidden:
:maxdepth: 7

00-platform-and-demos
01-cpu-npu-heterogeneous-design
02-model-zoo-and-trust-boundaries
```
