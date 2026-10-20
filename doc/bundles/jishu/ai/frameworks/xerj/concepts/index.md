# Concepts 索引

本目录是 XERJ 知识包的概念文档，按「入门 → 核心 → 进阶」三段组织。

## 入门：建立心智模型

| 文档 | 一句话简介 |
|---|---|
| [00 整体架构](00-overview.md) | 18 个 crate 的职责分层、三条并发端口、搜索与摄取路径、「ES 兼容是传输层」这一架构主轴 |
| [01 安装与快速上手](01-getting-started.md) | 安装与校验策略、`--insecure` 信任边界、admin.key 认证模型、14 个顶层子命令全景、首次索引闭环 |
| [02 autoindex 零配置流水线](02-autoindex-pipeline.md) | 内容驱动的格式识别（28 个 Family / 25 个抽取器）、字段来源标记决定的数据集划分、阶段序列、10 分钟决策门、退出码语义 |

## 核心：主要接口面

| 文档 | 一句话简介 |
|---|---|
| [03 MCP 智能体接口](03-mcp-agent-surface.md) | 17 个工具的分工、代理与非代理之别、回环 admin.key 认证回退、`max_tokens` 硬预算、工具计数漂移 |
| [04 检索路径与响应裁剪](04-search-query-path.md) | 查询执行链路、memtable 与 segment 双路合并、`_passage` 伪字段与 `_xerj.hints`、未知字段严格模式 |
| [05 向量、嵌入与混合检索](05-vector-and-hybrid.md) | 四类嵌入后端与「嵌入在摄入时绑定」、HNSW 与 flat-slab 重构、精确扫描与 ANN 的判定规则、`rerank` 外呼边界 |

## 进阶：边界与替代路径

| 文档 | 一句话简介 |
|---|---|
| [06 智能体记忆与第二大脑](06-agent-memory-and-brain.md) | `/_memory` 命名空间记忆、`/_graph` 关系层（9 个确定性检测器）、`/_ask` 确定性规划器、`/_decide` 类型化判断 |
| [07 ES 兼容与基准诚实性](07-es-compat-and-benchmarks.md) | ES 8.x 线协议兼容面、零失败一致性门禁、记分卡 55/26/4 与四处败因、能力边界与未实现清单 |
| [08 参考编码与语料库](08-reference-coding.md) | `corpus add/index/code` 闭环、返回定义而非字节窗口、退出码契约、许可证分档、MEATL、收益的记忆门控 |

```{toctree}
:maxdepth: 2

00-overview
01-getting-started
02-autoindex-pipeline
03-mcp-agent-surface
04-search-query-path
05-vector-and-hybrid
06-agent-memory-and-brain
07-es-compat-and-benchmarks
08-reference-coding
```
