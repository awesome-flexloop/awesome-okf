---
type: concepts-index
title: "Maple Mono 概念文档索引"
description: "Maple Mono v7.9 构建系统核心概念——按学习路径从入门到高级排列"
---

# Maple Mono 概念文档索引

本索引列出 Maple Mono 构建系统核心概念的 9 篇文档，按学习路径从入门到高级排列。

## 入门篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 00 | [Maple Mono 简介](00-introduction.md) | Maple Mono 是什么、构建系统全貌、与 JetBrains Mono/Fira Code 的定位区别 |
| 01 | [构建流水线](01-build-pipeline.md) | 从源字体到多格式输出的四阶段流水线：源字体加载→配置解析→并行构建→后处理 |
| 02 | [配置系统](02-config-system.md) | config.json 声明式配置 + CLI 参数双层覆盖的合并顺序与优先级 |

## 核心篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 03 | [OpenType Feature 系统](03-feature-system.md) | calt 连字查找表、cv 变体、ss 样式集三层结构与触发机制 |
| 04 | [Feature AST 生成器](04-feature-ast-generator.md) | Python 对象组合生成 .fea 字符串的 DSL 设计——FeatureWithDocs/Lookup/ClassDef |
| 05 | [特征冻结机制](05-freeze-mechanism.md) | enable/disable/ignore 三模式——把动态 OpenType 规则固化到字形表 |

## 高级篇

| 序号 | 文档 | 说明 |
|------|------|------|
| 06 | [Nerd Font 补丁策略](06-nerd-font-patching.md) | 预构建 NF Base 字体 vs font-patcher 运行时修补的权衡 |
| 07 | [中英文字体合并](07-cn-font-merge.md) | Resource Han Rounded 基字体下载 + merge_ttfonts 合并 + 2:1 宽度对齐 |
| 08 | [并行构建与性能](08-parallel-build.md) | ProcessPoolExecutor 并行流水线 + pool_size 配置 + 缓存策略 |

## 学习路径

```
00-introduction → 01-build-pipeline → 02-config-system
  → 03-feature-system → 04-feature-ast-generator
    → 05-freeze-mechanism → 06-nerd-font-patching
      → 07-cn-font-merge → 08-parallel-build
```

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
07-cn-font-merge
08-parallel-build
```
