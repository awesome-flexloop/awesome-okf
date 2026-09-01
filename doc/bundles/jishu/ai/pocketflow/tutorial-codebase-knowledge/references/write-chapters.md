---
title: WriteChapters
type: reference
bundle: tutorial-codebase-knowledge
source: nodes.py
---

# WriteChapters

`WriteChapters` 是流水线的第五个节点，继承自 PocketFlow 的 `BatchNode`（而非普通 Node），负责按顺序逐个生成每个章节的 Markdown 教程内容。它是整个流水线中最复杂的节点，因为它需要在生成过程中维护已写章节的上下文，确保章节间的连贯性和交叉引用。重试配置为 `max_retries=5, wait=20`。

## 类定义

```python
class WriteChapters(BatchNode):
```

源码位置：nodes.py#L537-L750

## 生命周期方法

### prep(shared)

准备批量处理的条目列表。为每个抽象创建一个章节任务项。

**读取的 shared 键**：
- `chapter_order`：有序抽象索引列表（来自 OrderChapters）
- `abstractions`：抽象列表
- `files`：`[(path, content), ...]` 文件列表
- `project_name` (str)：项目名称
- `language` (str)：输出语言，默认 `"english"`
- `use_cache` (bool)：是否启用 LLM 缓存，默认 `True`

**关键逻辑**：
1. **初始化临时存储**：`self.chapters_written_so_far = []`，用于在 batch exec 过程中累积已生成章节的内容摘要
2. **构建完整章节目录**：遍历 chapter_order，为每个章节生成：
   - `chapter_num`：章节号（从1开始）
   - `safe_name`：安全文件名（非字母数字字符替换为下划线，小写）
   - `filename`：文件名格式 `{NN}_{safe_name}.md`（如 `01_query_processing.md`）
   - 章节链接字符串 `{num}. [{chapter_name}]({filename})`
3. **构建 chapter_filenames 映射**：`{abstraction_index: {"num": int, "name": str, "filename": str}}`，用于章节间交叉链接
4. **为每个章节准备任务项**：
   - 调用 [get_content_for_indices()](identify-abstractions.md#get_content_for_indicesfiles_data-indices) 获取相关代码片段
   - 查找前一章和后一章信息（用于过渡段落和链接）
   - 将所有信息打包为字典加入 items_to_process 列表

**返回值** (list)：章节任务项列表（BatchNode 的输入迭代器），每项为：
```python
{
    "chapter_num": int,
    "abstraction_index": int,
    "abstraction_details": {"name": str, "description": str, "files": [int]},
    "related_files_content_map": {"{idx} # {path}": content, ...},
    "project_name": str,
    "full_chapter_listing": str,     # 完整章节目录字符串
    "chapter_filenames": dict,       # 章节文件名映射
    "prev_chapter": dict | None,     # 前一章信息
    "next_chapter": dict | None,     # 后一章信息
    "language": str,
    "use_cache": bool,
}
```

### exec(item)

为单个章节生成 Markdown 教程内容。这是 BatchNode 的批量执行方法，对 prep 返回的每个 item 依次调用。

**核心特性：渐进式上下文累积**

与其他节点不同，WriteChapters 使用实例变量 `self.chapters_written_so_far` 在多次 exec 调用间累积已写章节的内容。每生成一章，就将内容追加到列表中，下一章生成时将之前所有章节的摘要作为上下文传入 LLM，确保连贯性。

**Prompt 核心要求**：
1. 以 `# Chapter {num}: {name}` 标题开头
2. 非首章以对上一章的过渡和链接开头
3. 从高层动机（解决什么问题）开始，以具体用例为引导
4. 将复杂概念分解为关键点逐一讲解
5. 每个代码块**不超过10行**，拆分长代码并逐一讲解
6. 提供内部实现的非代码/轻代码讲解（推荐使用 Mermaid sequenceDiagram，最多5个参与者）
7. 引用其他章节时使用 Markdown 链接 `[Chapter Title](filename.md)`
8. 使用 Mermaid 图表说明复杂概念
9. 大量使用类比和示例
10. 以结论和下一章过渡结尾

**多语言支持**：当 language 非英语时，prompt 中加入全面的语言指令，要求所有生成内容（解释、示例、技术术语、代码注释）均使用目标语言，代码语法和专有名词除外。

**后处理**：
1. 检查生成内容是否以正确标题开头
2. 若标题不正确，替换或补加标题行
3. 将生成的章节内容追加到 `self.chapters_written_so_far`

**返回值** (str)：该章节的 Markdown 内容字符串。

### post(shared, prep_res, exec_res_list)

汇总所有章节内容并清理临时状态。

**写入的 shared 键**：
- `chapters`：`[str, ...]` Markdown 章节内容列表（按章节顺序）

**清理**：删除 `self.chapters_written_so_far` 实例变量。

## BatchNode 工作机制

WriteChapters 继承 BatchNode，其执行流程与普通 Node 不同：

```
prep(shared) → [item1, item2, ..., itemN]
                  │
                  ├─ exec(item1) → chapter1_md
                  ├─ exec(item2) → chapter2_md  (可访问 self.chapters_written_so_far)
                  ├─ ...
                  └─ exec(itemN) → chapterN_md
                                    │
post(shared, prep_res, [chapter1_md, ..., chapterN_md])
```

关键区别：
- prep 返回一个可迭代对象（列表），而非单个 prep_res
- exec 对每个 item 单独调用，返回单个结果
- post 接收 exec_res_list（所有 exec 返回值的列表）
- exec 调用是顺序的（非并行），保证章节上下文的累积

## 文件名生成规则

章节文件名由抽象名称派生：
1. 取抽象的 `name` 字段
2. 将所有非字母数字字符替换为下划线 `_`
3. 转为小写
4. 格式化为 `{两位数章节号}_{safe_name}.md`

例如：抽象名 "Query Processing" → `01_query_processing.md`

## 源码位置

nodes.py#L537-L750
