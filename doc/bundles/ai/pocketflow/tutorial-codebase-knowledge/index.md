---
title: Codebase Knowledge Generator
type: index
bundle: tutorial-codebase-knowledge
version: 0.1.0
description: |
  基于 PocketFlow 框架的代码库知识自动生成器。输入 GitHub 仓库 URL 或本地目录，
  通过六节点 LLM 流水线（抓取→识别抽象→分析关系→排序章节→逐章写作→组装输出），
  自动生成结构化、新手友好的代码教程文档，支持多语言输出。
concepts:
  - pipeline-architecture: 六节点线性流水线架构与 Shared 字典通信
  - code-analysis-workflow: LLM驱动的代码分析工作流（识别→关系→排序→写作）
references:
  - fetch-repo: FetchRepo 节点（源码抓取，支持GitHub/本地双源）
  - identify-abstractions: IdentifyAbstractions 节点（LLM识别核心抽象）
  - analyze-relationships: AnalyzeRelationships 节点（LLM分析抽象关系+项目概述）
  - order-chapters: OrderChapters 节点（LLM确定教学顺序）
  - write-chapters: WriteChapters 节点（BatchNode逐章生成教程内容）
  - combine-tutorial: CombineTutorial 节点（组装Mermaid图+输出文件）
  - utility-functions: 工具函数（call_llm、crawl、create_tutorial_flow、main）
examples:
  - basic-usage: 基本用法（命令行参数、Python API、Docker、自定义扩展）
---

# Codebase Knowledge Generator

Codebase Knowledge Generator 是一个基于 [PocketFlow](https://github.com/The-Pocket/PocketFlow) 框架的 AI 工具，输入 GitHub 仓库 URL 或本地目录路径，自动分析代码库结构并生成新手友好的结构化教程文档。它将"理解代码库"这一复杂认知任务分解为六个有序步骤，每个步骤由一个 PocketFlow 节点承载，通过 LLM 完成核心分析工作。

## 核心设计哲学

- **流水线分解**：将复杂的代码→教程转换拆分为六个单一职责节点，线性连接，无分支无循环
- **LLM 驱动分析**：四个核心分析节点全部由 LLM 完成，通过精心设计的 Prompt 和严格的 YAML 输出验证保证质量
- **渐进式理解**：先建立全局概念地图（抽象识别），再分析概念关系，然后确定教学顺序，最后逐章展开
- **Shared 字典通信**：节点间通过共享字典传递数据，遵循 prep（读）→ exec（算）→ post（写）三阶段生命周期
- **BatchNode 逐章生成**：利用 BatchNode 的顺序执行特性实现章节上下文累积，确保教程的叙事连贯性

## 六节点流水线

```
FetchRepo → IdentifyAbstractions → AnalyzeRelationships → OrderChapters → WriteChapters → CombineTutorial
 (抓取源码)   (识别5-10个核心抽象)   (分析抽象间关系+概述)   (排序教学顺序)  (逐章生成Markdown)  (组装输出文件)
```

| 节点 | 类型 | 功能 | LLM |
|------|------|------|-----|
| [FetchRepo](references/fetch-repo.md) | Node | 从 GitHub API 或本地目录爬取源码文件 | ❌ |
| [IdentifyAbstractions](references/identify-abstractions.md) | Node | LLM 分析代码，识别核心抽象概念 | ✅ |
| [AnalyzeRelationships](references/analyze-relationships.md) | Node | LLM 分析抽象间依赖关系，生成项目概述 | ✅ |
| [OrderChapters](references/order-chapters.md) | Node | LLM 确定从基础到深入的最佳教学顺序 | ✅ |
| [WriteChapters](references/write-chapters.md) | BatchNode | LLM 逐章生成 Markdown 教程（含代码示例和Mermaid图） | ✅×N |
| [CombineTutorial](references/combine-tutorial.md) | Node | 生成 Mermaid 关系图，组装首页和章节文件到磁盘 | ❌ |

## 快速导航

### 核心概念
- [流水线架构](concepts/pipeline-architecture.md) — 六节点线性管道、Shared 字典数据流、Node vs BatchNode、重试策略
- [代码分析工作流](concepts/code-analysis-workflow.md) — LLM 四阶段分析过程、YAML 输出协议、多语言支持、缓存机制

### API 参考
- [FetchRepo](references/fetch-repo.md) — 源码抓取节点（GitHub API / SSH克隆 / 本地目录）
- [IdentifyAbstractions](references/identify-abstractions.md) — 核心抽象识别节点
- [AnalyzeRelationships](references/analyze-relationships.md) — 抽象关系分析节点
- [OrderChapters](references/order-chapters.md) — 章节排序节点
- [WriteChapters](references/write-chapters.md) — 批量章节写作节点（BatchNode）
- [CombineTutorial](references/combine-tutorial.md) — 教程组装与文件输出节点
- [工具函数](references/utility-functions.md) — call_llm、crawl_github_files、crawl_local_files、create_tutorial_flow、main

### 示例
- [基本用法](examples/basic-usage.md) — 环境准备、命令行参数、Python API 调用、Docker 运行、自定义节点扩展

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 LLM（.env 文件）
GEMINI_API_KEY=your_key_here

# 生成教程
python main.py --repo https://github.com/pallets/flask --language Chinese
```

输出目录 `output/flask/` 将包含 `index.md`（含 Mermaid 关系图）和多个章节 Markdown 文件。

## 源码

- 核心节点：[nodes.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/nodes.py)
- 流程定义：[flow.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/flow.py)
- 入口程序：[main.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/main.py)
- 工具函数：[utils/](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/)
  - [call_llm.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/call_llm.py)
  - [crawl_github_files.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_github_files.py)
  - [crawl_local_files.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/utils/crawl_local_files.py)

```{toctree}
:hidden:

concepts/code-analysis-workflow
concepts/pipeline-architecture
examples/basic-usage
references/analyze-relationships
references/combine-tutorial
references/fetch-repo
references/identify-abstractions
references/order-chapters
references/utility-functions
references/write-chapters
```
