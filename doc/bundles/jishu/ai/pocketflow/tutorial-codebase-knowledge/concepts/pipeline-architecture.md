---
title: 流水线架构
type: concept
bundle: tutorial-codebase-knowledge
related:
  - tutorial-codebase-knowledge/references/fetch-repo
  - tutorial-codebase-knowledge/references/identify-abstractions
  - tutorial-codebase-knowledge/references/analyze-relationships
  - tutorial-codebase-knowledge/references/order-chapters
  - tutorial-codebase-knowledge/references/write-chapters
  - tutorial-codebase-knowledge/references/combine-tutorial
  - tutorial-codebase-knowledge/references/utility-functions
---

# 流水线架构

Codebase Knowledge Generator 采用**六节点线性流水线**架构，基于 PocketFlow 框架实现。每个节点是一个独立的处理单元，负责流水线中的一个阶段，节点之间通过 `shared` 字典传递数据，通过运算符 `>>` 线性连接。

## 整体架构

```
┌─────────────┐    ┌─────────────────────┐    ┌───────────────────────┐
│  FetchRepo  │───→│ IdentifyAbstractions│───→│ AnalyzeRelationships  │
│  抓取源码    │    │  识别核心抽象        │    │  分析抽象间关系        │
└─────────────┘    └─────────────────────┘    └───────────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│ CombineTutorial │←───│  WriteChapters   │←───│   OrderChapters     │
│  组装输出文件   │    │  逐章生成教程(Batch)│   │  排序教学顺序       │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

六个节点严格按顺序执行，无分支、无循环、无并行。这是一个经典的**管道-过滤器（Pipe and Filter）**架构。

## 节点职责一览

| 序号 | 节点 | 类型 | 输入 | 输出 | LLM调用 |
|------|------|------|------|------|---------|
| 1 | [FetchRepo](../references/fetch-repo.md) | Node | repo_url 或 local_dir | files[] | ❌ |
| 2 | [IdentifyAbstractions](../references/identify-abstractions.md) | Node | files[] | abstractions[] | ✅ |
| 3 | [AnalyzeRelationships](../references/analyze-relationships.md) | Node | abstractions[], files[] | relationships{} | ✅ |
| 4 | [OrderChapters](../references/order-chapters.md) | Node | abstractions, relationships | chapter_order[] | ✅ |
| 5 | [WriteChapters](../references/write-chapters.md) | **BatchNode** | chapter_order, abstractions, files[] | chapters[] | ✅（多次） |
| 6 | [CombineTutorial](../references/combine-tutorial.md) | Node | 全部数据 | 文件系统输出 | ❌ |

## Shared 字典数据流

所有节点通过同一个 `shared` 字典通信。每个节点遵循 PocketFlow 的 **prep→exec→post** 三阶段生命周期：
- **prep**：从 shared 读取所需数据
- **exec**：执行核心逻辑（调用LLM、爬取文件等）
- **post**：将结果写回 shared

```
shared 字典演化过程：

初始状态（main.py设置）:
  {
    repo_url, local_dir, project_name, github_token,
    output_dir, include_patterns, exclude_patterns,
    max_file_size, language, use_cache, max_abstraction_num,
    files: [], abstractions: [], relationships: {},
    chapter_order: [], chapters: [], final_output_dir: None
  }

FetchRepo 后:     files: [(path, content), ...]
                    project_name: "..."

IdentifyAbstractions后: abstractions: [{name, description, files}, ...]

AnalyzeRelationships后: relationships: {summary: str, details: [{from,to,label}]}

OrderChapters后:   chapter_order: [2, 0, 1, ...]

WriteChapters后:   chapters: ["# Chapter 1...", "# Chapter 2...", ...]

CombineTutorial后: final_output_dir: "output/ProjectName"
                    （文件已写入磁盘）
```

## Node 与 BatchNode 的区别

流水线中五个节点继承 `Node`，唯独 [WriteChapters](../references/write-chapters.md) 继承 `BatchNode`：

```
Node 执行模式：              BatchNode 执行模式：
prep → prep_res             prep → [item1, item2, ..., itemN]
exec(prep_res) → result      ├─ exec(item1) → result1
post(..., result)            ├─ exec(item2) → result2
                              ├─ ...
                              └─ exec(itemN) → resultN
                            post(..., [result1, ..., resultN])
```

WriteChapters 使用 BatchNode 是因为需要**逐章生成**教程，每章是一个独立的处理单元。更重要的是，它利用顺序执行特性实现**上下文累积**——每写完一章，将内容追加到 `self.chapters_written_so_far`，下一章生成时将之前所有章节的摘要作为上下文传给 LLM，保证章节间的连贯性和交叉引用的准确性。

## 重试策略

四个调用 LLM 的节点（2-5）配置了重试机制：
- `max_retries=5`：最多尝试5次
- `wait=20`：重试间隔20秒

这是因为 LLM 输出格式不稳定（YAML 解析失败是常见问题），重试给 LLM 自我纠正的机会。[FetchRepo](../references/fetch-repo.md) 和 [CombineTutorial](../references/combine-tutorial.md) 不需要重试：前者调用 GitHub API 有自己的错误处理（速率限制等待），后者是纯本地文件写入操作。

缓存策略：`use_cache=True` 时，仅在首次尝试（`self.cur_retry == 0`）使用 LLM 缓存；重试时跳过缓存，确保获取新的响应。

## 流程创建

流程在 [create_tutorial_flow()](../references/utility-functions.md#create_tutorial_flow) 中创建（flow.py）：

```python
from pocketflow import Flow

def create_tutorial_flow():
    fetch_repo = FetchRepo()
    identify_abstractions = IdentifyAbstractions(max_retries=5, wait=20)
    analyze_relationships = AnalyzeRelationships(max_retries=5, wait=20)
    order_chapters = OrderChapters(max_retries=5, wait=20)
    write_chapters = WriteChapters(max_retries=5, wait=20)
    combine_tutorial = CombineTutorial()

    # 线性连接
    fetch_repo >> identify_abstractions
    identify_abstractions >> analyze_relationships
    analyze_relationships >> order_chapters
    order_chapters >> write_chapters
    write_chapters >> combine_tutorial

    return Flow(start=fetch_repo)
```

运行流程只需：
```python
shared = { ... }  # 初始化参数
flow = create_tutorial_flow()
flow.run(shared)
```

## 设计特点

1. **单一职责**：每个节点只做一件事——抓取、识别、分析关系、排序、写作、组装
2. **无状态节点**：节点本身不持有跨节点状态（WriteChapters 的 `chapters_written_so_far` 仅用于单次 batch 执行内的上下文传递），所有持久状态在 shared 中
3. **可替换性**：节点间通过 shared 字典松耦合，可以独立替换任何节点的实现（例如用不同的 LLM 提示词策略替换 IdentifyAbstractions）
4. **错误隔离**：每个节点的重试和错误处理独立，单个节点失败不会影响其他节点的定义

## 相关概念

- [代码分析工作流](code-analysis-workflow.md) — LLM 如何驱动从代码到教程的分析过程
