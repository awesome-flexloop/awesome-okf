---
type: spec
title: web-compile 架构洞察
description: web-compile 源码洞察记录
tags:
- web-compile
- spec
- insights
generated:
  by: reference_agent/trae-cn
  at: '2026-08-23'
status: stable
stale_after: '2027-08-23'
sources:
- id: web-compile-source
  resource: /references/compile-source.md
  title: web-compile compile-source
---

# web-compile 架构洞察

> I 阶段产出：基于事实清单提炼的核心洞察四元组。

## 洞察 I-001：[hash]文件名——零配置缓存失效

- **陈述**：web-compile 支持在输出文件名中使用 `[hash]` 占位符，编译时自动替换为输出内容的MD5哈希值前8位。重新编译时自动删除旧哈希版本文件。这实现了静态资源的内容哈希缓存失效（cache busting）。
- **证据**：F-019~F-022（哈希替换逻辑）、F-021（旧文件清理）
- **反常识**：很多前端构建工具（webpack/vite）的文件名哈希需要插件配置、构建系统集成。web-compile用`[hash]`占位符+文件系统glob删除旧版本的极简方案，无需额外配置即可获得内容哈希缓存失效能力——这对Python生态的文档/Sphinx主题开发者尤为重要，他们通常没有Node.js构建链。
- **行动**：为静态资源工具内置内容哈希命名支持；旧版本清理使用glob模式匹配；无需引入复杂构建系统即可获得生产级缓存策略。

## 洞察 I-002：非零退出码——CI友好的设计

- **陈述**：web-compile 在文件有变更时以非零退出码（默认3）退出，无变更时退出码0。这使得它可以直接集成到CI流水线中：检测到文件变更时CI任务失败，提醒开发者提交编译后的文件。`--test-run`模式支持dry-run不修改文件。
- **证据**：F-034~F-036（exit_code/test_run选项）、F-042（变更退出逻辑）
- **反常识**：CLI工具通常成功就退出0，失败退出非零。但编译类工具（prettier/eslint --fix/black）在CI中的语义是"检查是否有未提交的变更"——退出非零表示"文件被修改了/需要提交"。这是一个CI原生设计模式，不是错误，而是"需要人工确认"信号。
- **行动**：面向CI的编译/格式化工具应提供"变更检测"模式，通过退出码区分"无变更（0）"和"有变更（N）"，支持可配置退出码避免与真正的错误码（1）冲突。

## 洞察 I-003：声明式文件映射——配置驱动而非命令驱动

- **陈述**：所有文件映射（sass_files/js_files/jinja_files）只能通过配置文件设置，CLI命令行参数只控制编译选项（格式、编码、sourcemap等），不接受文件列表参数。这确保编译配置是可重复、可版本控制的。
- **证据**：F-028~F-031（配置文件）、F-037（文件映射为"config only"）
- **反常识**：很多CLI工具允许命令行直接传入文件列表做一次性编译（如`sass input.scss output.css`）。但对于需要反复执行的文档构建流水线，命令行参数容易遗漏和不一致。配置文件驱动确保团队所有人执行相同的编译配置，配置本身纳入版本控制。
- **行动**：需要重复执行的编译/构建工具应优先使用配置文件声明输入输出映射，命令行参数用于控制行为选项（format/verbosity等）而非文件映射。

## 洞察 I-004：三编译管线独立执行——原子化错误收集

- **陈述**：SASS编译、JS压缩、Jinja渲染三个管线独立执行，各自收集错误到compilation_errors字典。默认遇到第一个错误即停止，但`--continue-on-error`可继续处理其他文件，最后汇总报告所有错误。
- **证据**：F-038~F-041（三管线顺序执行+错误收集）、F-035（continue-on-error选项）
- **反常识**：简单CLI工具通常遇到错误立即退出。但多文件编译场景下，开发者希望一次看到所有错误（类似编译器的error list），而不是修一个重跑一次再遇到下一个。原子化错误收集+可选continue-on-error是更好的开发体验。
- **行动**：批处理工具应收集所有错误后统一报告；提供continue-on-error选项用于一次性发现所有问题；错误信息用结构化格式（YAML/JSON）输出便于解析。

## 知识地图

```
web-compile/
├── 入门层
│   ├── 00-introduction.md     → I-001,I-002,I-003 功能概览
│   └── 01-getting-started.md  → 安装与基本用法
├── 核心层
│   ├── 02-compilation-types.md → I-004 三种编译类型
│   ├── 03-configuration.md    → I-003 配置文件详解
│   └── 04-ci-integration.md   → I-002 CI集成
└── 实践层
    └── examples/
        └── asset-pipeline.md → 完整资产编译流水线示例
```
