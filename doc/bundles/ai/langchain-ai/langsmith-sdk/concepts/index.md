# 核心概念

- [SDK 总览](overview.md) — Client、RunTree、traceable、evaluation、anonymizer 的整体结构
- [traceable 自动追踪装饰器](traceable-decorator.md) — 上下文解析、输入输出归一、Promise 与流式返回值包装
- [RunTree 追踪模型](run-tree-tracing.md) — run 字段、trace_id、dotted_order、postRun/patchRun 生命周期
- [评测运行器](evaluation.md) — evaluate、_ExperimentManager、RunEvaluator、StringEvaluator 与 feedback 写入

```{toctree}
:hidden:
:maxdepth: 7

evaluation
overview
run-tree-tracing
traceable-decorator
```
