---
okf_version: "0.2"
type: index
title: "概念文档索引"
description: "Maple Mono v8 构建系统概念文档——从总体介绍到流水线、配置、特征、Nerd Font、CJK 与并行缓存"
---

# 概念文档索引

本目录按“先全局、再子系统、最后工程约束”的顺序组织 9 篇概念文档。建议首次阅读按编号顺序进行。

| 编号 | 文档 | 核心问题 | 关键对象 |
|------|------|----------|----------|
| 00 | [总体介绍](00-introduction.md) | Maple Mono 是什么？v8 与 v7 有何不同？ | 版本线、构建方式、仓库布局 |
| 01 | [构建流水线](01-build-pipeline.md) | 一次构建经历哪些阶段？各阶段由谁负责？ | `main()`、`BuildPlan`、`MapleBuildPipeline` |
| 02 | [配置系统](02-config-system.md) | 配置如何从 JSON/CLI 归一化为可执行模型？ | `ResolvedConfig`、`BuildConfigResolver`、`BuildRuntimeContext` |
| 03 | [特征系统](03-feature-system.md) | 特征规则如何组织、生成与应用？ | `feature/` 包、双轨应用路径 |
| 04 | [特征 AST 生成器](04-feature-ast-generator.md) | 如何用 Python 对象生成 `.fea` 源码？ | `Clazz`、`Lookup`、`Feature`、`generate_fea_string` |
| 05 | [特征冻结机制](05-freeze-mechanism.md) | 三种冻结模式在什么时机生效？ | `feature_freeze`、源准备期冻结、`calt` 承载 |
| 06 | [Nerd Font 补丁](06-nerd-font-patching.md) | 预构建基座与动态修补如何取舍？ | `NerdFontVariant`、三份 NF 基座、`font-patcher` |
| 07 | [CJK 字体合并](07-cjk-font-merge.md) | 四语种 CJK 如何生成、缓存与合并？ | `CJKBuilder`、`CJKBaseResolver`、2:1 对齐 |
| 08 | [并行构建与缓存](08-parallel-build.md) | 并行执行与阶段缓存如何保证正确性？ | `Executor`、阶段身份、`build-cache.json` |

## 学习路径

```{toctree}
:hidden:
:maxdepth: 7

00-introduction
01-build-pipeline
02-config-system
03-feature-system
04-feature-ast-generator
05-freeze-mechanism
06-nerd-font-patching
07-cjk-font-merge
08-parallel-build
```

- **只读使用者**：00 → 01 → 对应示例
- **构建配置定制**：00 → 02 → 05 → 06 → 07
- **修改特征规则**：00 → 03 → 04 → 05
- **维护流水线或 CI**：00 → 01 → 08
