---
okf_version: "0.2"
type: index
title: "API 参考索引"
description: "Maple Mono v8 构建入口、ResolvedConfig 模型与特征生成 API 的速查"
---

# API 参考索引

三篇参考文档聚焦“可以直接调用的接口与数据模型”，不重复概念文档中的设计讨论。

| 文档 | 覆盖范围 | 适用场景 |
|------|----------|----------|
| [构建入口](build-entrypoint.md) | `build.py`、`scripts.pipeline.main()`、`task.py` 子命令、`MapleBuildPipeline` | 写脚本、CI、排查入口行为 |
| [ResolvedConfig](resolved-config.md) | `ResolvedConfig` 六组子配置、`BuildRuntimeContext`、`BuildPlan`、解析器接口 | 读取/构造配置模型、扩展配置字段 |
| [特征生成 API](feature-generator-api.md) | `ast.py` 节点与辅助函数、`compiler.py` 生成入口、`apply.py` 应用接口 | 编写或调试特征规则 |

## 阅读约定

- 代码位置以 v8 `variable` 分支为准；
- 签名只列关键参数，完整定义请对照源码；
- 标注“内部”的接口不保证跨版本稳定。

```{toctree}
:hidden:
:maxdepth: 7

build-entrypoint
resolved-config
feature-generator-api
```
