# 概念文档（Concepts）

本目录按“身份 → 设计 → 架构 → 环境 → 模型 → 配置 → 评测 → 迁移”组织，建议顺序阅读。

## 阅读路径

| 顺序 | 文档 | 回答的问题 |
|---|---|---|
| 1 | [项目概览](00-project-overview.md) | 它是什么、从哪来、现在什么版本、哪些流行说法是错的 |
| 2 | [设计哲学](01-design-philosophy.md) | 为什么敢减到只剩 bash、线性历史、独立 subprocess |
| 3 | [架构解剖](02-architecture-and-code.md) | 三个 Protocol 与 190 行主循环如何工作 |
| 4 | [执行环境](03-execution-environments.md) | 命令在哪里跑、如何隔离、安全边界在哪 |
| 5 | [模型接入](04-model-integration.md) | 支持哪些模型、toolcall 与 textbased 怎么选 |
| 6 | [配置与扩展](05-configuration-and-extension.md) | YAML 三段、Jinja 模板、子类化怎么改 |
| 7 | [评测与边界](06-benchmarks-and-boundaries.md) | 74% 证明了什么、不擅长什么 |
| 8 | [可迁移经验](07-transferable-lessons.md) | 不做 coding agent 能拿走什么 |
| 9 | [源码地图](08-source-map.md) | 模块/符号/行号、调用链、数据契约、扩展点与测试地图 |

```{toctree}
:hidden:
:maxdepth: 2

00-project-overview
01-design-philosophy
02-architecture-and-code
03-execution-environments
04-model-integration
05-configuration-and-extension
06-benchmarks-and-boundaries
07-transferable-lessons
08-source-map
```
