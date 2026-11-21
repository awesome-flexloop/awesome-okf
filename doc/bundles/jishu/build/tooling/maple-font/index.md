---
okf_version: "0.2"
type: bundle-index
title: "Maple Mono Font Builder"
description: "Maple Mono v7.9 等宽编程字体构建系统源码中文教程——配置驱动流水线、OpenType Feature AST 生成器、特征冻结、Nerd Font 补丁、中英文字体合并"
tags: ["maple-mono", "font", "opentype", "fonttools", "variable-font", "typography", "python"]
total_concepts: 9
total_examples: 4
total_references: 3
source_repository: "https://github.com/subframe7536/maple-font"
source_version: "v7.9"
source_path: "notebook/libs/maple-font/"
generated: { by: reference_agent/deepseek-v4.1-flash, at: "2026-11-21" }
status: draft
---

# Maple Mono Font Builder

> Maple Mono 是一款专为编程体验优化的开源等宽字体，支持变量字重、智能连字、Nerd Font 图标补丁与中英文字符集嵌入。本知识包基于 Maple Mono **v7.9** 构建系统源码阅读撰写，覆盖从构建流水线到特征系统的完整架构。

本知识包基于 **Maple Mono v7.9** 源码阅读撰写，按七概念方法论的 R→I→E→C 链路交付：先采集客观事实（22+ 条），再形成四元组洞察（现象+根因+影响+建议），最后原子化为概念文档、实战示例与 API 参考三层结构。

## 快速导航

| 类别 | 数量 | 索引 |
|------|------|------|
| 📖 概念文档 | 9 | [概念文档索引](concepts/index.md) |
| 🧪 实战示例 | 4 | [实战示例索引](examples/index.md) |
| 📚 API 参考 | 3 | [API 参考索引](references/index.md) |

## 三分钟理解 Maple Mono 构建流水线

```
┌──────────────────────────────────────────────────────────────────┐
│                 原始源字体（source/）                              │
│  MapleMono[wght]-VF.ttf  MapleMono-Italic[wght]-VF.ttf          │
│  MapleMono-NF-Base.ttf（预构建 Nerd Font 基座）                    │
└──────────────────────────┬───────────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────┐           ┌──────────┐          ┌──────────┐
│ build.py│           │ Python AST│          │ config.json│
│ FontConfig│         │ 特征生成器│          │ 声明式配置  │
│ BuildOption│        │ generate_ │          │ CLI 覆盖层 │
│ parse_args│         │ fea_string│          └──────────┘
└────┬────┘           └─────┬────┘
     │                       │
     ▼                       │
┌────────────────────────────▼──────┐
│        并行构建核心逻辑             │
│  run_build(PoolExecutor)          │
│    ├─ build_mono() → TTF/OTF/WOFF2 │
│    ├─ build_mono_autohint()       │
│    ├─ build_nf()    → Nerd Font 版 │
│    └─ build_cn()    → 中英合并版   │
└────────────────────────────┬──────┘
                             │
                             ▼
┌──────────────────────────────────────┐
│  OpenType Feature 注入 + 特征冻结     │
│  patch_font_feature()                │
│  freeze_feature() → 动态规则固化      │
└────────────────────────────┬─────────┘
                             │
                             ▼
┌──────────────────────────────────────┐
│  多格式输出：                       │
│  Variable / TTF / TTF-AutoHint /     │
│  OTF / WOFF2 / NF / CN / NF-CN       │
└──────────────────────────────────────┘
```

## 核心洞察

1. **声明式配置 + 命令覆盖双层架构**：`config.json` 承载默认值（可版本化、可共享），CLI 参数在运行时覆盖（快速实验、CI 流水线）。双层合并顺序固定：Config 默认 → CLI 参数覆写。这避免了"全靠命令行"的复杂度爆炸和"全靠配置文件"的灵活性缺失。

2. **OpenType Feature 的 Python AST 生成器**：不手写 `.fea` 文件，而是用 Python 对象（`ast.FeatureWithDocs`、`ast.Lookup`、`ast.ClassDef`）组合生成特征字符串。这让特征规则可以根据构建参数（italic / cn / normal / calt / infinite / tag 等）动态重组，且每个特征自带文档描述。

3. **特征冻结（Feature Freeze）机制**：对静态字体，可将 `cvXX` / `ssXX` / `zero` 等动态特征固化到字形表。三种模式（`enable` / `disable` / `ignore`）让最终用户拿到的字体就是自己想要的样子——不需要字体渲染器支持 OpenType 特性切换。变量字体则将特征规则移入 `calt` 查找表。

4. **中英文字体的组合策略**：不重绘中文字形，而是下载预构建的中文基字体（Resource Han Rounded 变体），用 `merge_ttfonts()` 将等宽拉丁基字体与中文基字体合并。合并后再调整中文字形宽度比例，保持 2:1 对齐。

5. **预构建 vs 动态生成的权衡**：Nerd Font 默认使用预构建的 NF Base 字体（`MapleMono-NF-Base.ttf`），只有在用户需要自定义 glyph 或 extra_args 时才回退到 `font-patcher` 运行时修补。这避免了每次构建都要调用 FontForge，显著加快构建速度。

## 文档结构

```
maple-font/
├── index.md              ← 本文件（Bundle 首页）
├── log.md                ← 生成日志
├── concepts/             ← 8 篇概念文档
│   ├── index.md
│   ├── 00-introduction.md
│   ├── 01-build-pipeline.md
│   ├── 02-config-system.md
│   ├── 03-feature-system.md
│   ├── 04-feature-ast-generator.md
│   ├── 05-freeze-mechanism.md
│   ├── 06-nerd-font-patching.md
│   ├── 07-cn-font-merge.md
│   └── 08-parallel-build.md
├── examples/             ← 4 个实战示例
│   ├── index.md
│   ├── basic-build.md
│   ├── custom-feature-build.md
│   ├── nerd-font-build.md
│   └── cn-font-build.md
└── references/           ← 3 篇 API 参考
    ├── index.md
    ├── build-entrypoint.md
    ├── font-config-class.md
    └── feature-generator-api.md
```

## 快速开始

如果你是 Maple Mono 构建系统的新用户，从 [基本构建示例](examples/basic-build.md) 开始。

如果你想理解架构，从 [构建流水线](concepts/01-build-pipeline.md) 开始按学习路径阅读。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
