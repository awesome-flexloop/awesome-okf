---
title: MapReduce 分治模式
type: concept
bundle: pocketflow-patterns
source: cookbook/pocketflow-map-reduce
related:
  - /pocketflow/pocketflow-core/concepts/batch-processing
  - /pocketflow/pocketflow-core/references/batch-node
  - /pocketflow/pocketflow-core/references/batch-flow
---

# MapReduce 分治模式

MapReduce 模式将大规模数据处理拆分为"分而治之"：Map阶段并行/批量处理每个分片，Reduce阶段汇总所有分片结果。PocketFlow通过BatchNode/BatchFlow天然支持此模式。

## 流程图

```
┌──────────────┐
│  Read/Chunk   │  准备阶段：读取数据、分片
│  (prep返回列表)│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  BatchNode   │  Map阶段：对每个分片独立处理
│  exec×N     │  （LLM摘要/评分/转换）
└──────┬───────┘
       │ 结果列表
       ▼
┌──────────────┐
│  ReduceNode  │  Reduce阶段：汇总所有结果
│  (聚合/排序)  │
└──────────────┘
```

## 核心实现

```python
class MapChunks(BatchNode):
    """Map: 对每个文档块做处理（如摘要）"""
    def prep(self, shared):
        return split_into_chunks(shared["documents"])

    def exec(self, chunk):
        return llm_summarize(chunk)  # 每个块独立处理

    def post(self, shared, prep_res, exec_res):
        shared["chunk_summaries"] = exec_res

class ReduceResults(Node):
    """Reduce: 汇总所有块的结果"""
    def prep(self, shared):
        return shared["chunk_summaries"]

    def exec(self, summaries):
        return llm_combine(summaries)  # 合并为最终结果

    def post(self, shared, prep_res, exec_res):
        shared["final_result"] = exec_res

map_node >> reduce_node
flow = Flow(start=map_node)
```

## 嵌套MapReduce

处理分层数据时（如学校→班级→学生），使用嵌套BatchFlow：

```
OuterBatchFlow (遍历学校)
  └→ InnerBatchFlow (遍历班级)
       └→ ProcessNode (处理学生)
```

## AsyncParallelBatchNode 并行版

异步并行Map阶段，大幅加速I/O密集型处理：

```python
class ParallelMap(AsyncParallelBatchNode):
    async def exec_async(self, chunk):
        return await llm_summarize_async(chunk)
# 所有chunk同时发起LLM调用
```

## Cookbook 对应示例

- `pocketflow-map-reduce` — 简历批量评估
- `pocketflow-batch-node` — CSV数据批量处理
- `pocketflow-nested-batch` — 嵌套批量（学校-班级-学生）
- `pocketflow-parallel-batch` — 并行翻译
- `pocketflow-parallel-batch-flow` — 并行图片处理
