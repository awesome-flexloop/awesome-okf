# 变更日志

## 2026-08-23

- 基于 `external/libs/ai/langchain-ai/langsmith-sdk/js/src/` 的 `client.ts`、`traceable.ts`、`run_trees.ts`、`schemas.ts`、`evaluation/evaluator.ts`、`evaluation/_runner.ts`、`evaluation/string_evaluator.ts`、`singletons/traceable.ts`、`anonymizer/index.ts` 生成 OKF v0.2 bundle。
- 写入 100 条源码事实，覆盖项目导出、schemas、Client、RunTree、traceable、singleton context、evaluation 与 anonymizer。
- 提炼 4 个架构洞察：RunTree 顺序模型、traceable 包装机制、Client 异步批处理、evaluate 复用 tracing/feedback 流水线。
- 生成 1 篇 reference、4 篇 concept、1 篇 example、根索引、子目录索引和本日志。
- 验证范围：关键导出类名/函数名存在性、frontmatter 必填字段、bundle 内交叉链接。
