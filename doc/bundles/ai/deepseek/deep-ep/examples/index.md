# DeepEP 示例

本目录包含 DeepEP 的使用示例，从基础 MoE 通信到高级功能演示。

## 示例列表

| 示例 | 说明 |
|------|------|
| [基础 MoE 通信](basic-moe.md) | ElasticBuffer 进行 dispatch → 专家计算 → combine 的完整流程 |
| [ElasticBuffer 配置与使用](elastic-buffer.md) | 缓冲区大小计算、FP8 通信、缓存 dispatch、Engram、PP、AGRS 等高级功能 |
| [计算-通信重叠](event-overlap.md) | 使用 EventOverlap 实现通信与计算重叠的各种模式和最佳实践 |

```{toctree}
:maxdepth: 7

basic-moe
elastic-buffer
event-overlap
```
