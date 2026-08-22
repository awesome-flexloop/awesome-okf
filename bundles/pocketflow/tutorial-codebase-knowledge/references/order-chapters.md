---
title: OrderChapters
type: reference
bundle: tutorial-codebase-knowledge
source: nodes.py
---

# OrderChapters

`OrderChapters` 是流水线的第四个节点，负责使用 LLM 确定教程章节的最佳学习顺序。它根据抽象的重要性、基础性和用户面向程度，将抽象排列为从入门到深入的教学顺序。它继承自 PocketFlow 的 `Node` 类，重试配置为 `max_retries=5, wait=20`。

## 类定义

```python
class OrderChapters(Node):
```

源码位置：[nodes.py#L410-L534](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/nodes.py#L410-L534)

## 生命周期方法

### prep(shared)

从 `shared` 读取抽象列表和关系数据，构建包含项目摘要和关系图的上下文。

**读取的 shared 键**：
- `abstractions`：抽象列表
- `relationships`：关系数据（包含 `summary` 和 `details`）
- `project_name` (str)：项目名称
- `language` (str)：输出语言，默认 `"english"`
- `use_cache` (bool)：是否启用 LLM 缓存，默认 `True`

**内部逻辑**：
1. 生成抽象索引列表字符串（`- {i} # {name}` 格式）
2. 将项目摘要拼入上下文
3. 遍历关系详情，将每个关系格式化为 `- From {from_idx} ({from_name}) to {to_idx} ({to_name}): {label}`

**返回值** (tuple)：
- `abstraction_listing`：抽象列表字符串
- `context`：包含摘要和关系的上下文
- `num_abstractions`：抽象总数
- `project_name`：项目名
- `list_lang_note`：语言备注字符串（非英语时提示名称可能已翻译）
- `use_cache`：缓存开关

### exec(prep_res)

向 LLM 发送 prompt，要求确定章节最佳教学顺序。

**Prompt 核心要求**：
1. 从最重要/最基础的概念开始（用户面向概念或入口点）
2. 逐步深入到更底层的实现细节或支撑概念
3. 输出有序的抽象索引列表，包含名称注释

**输出格式**（YAML 列表）：
```yaml
- 2 # FoundationalConcept
- 0 # CoreClassA
- 1 # CoreClassB (uses CoreClassA)
```

**验证逻辑**：
1. 从 LLM 响应提取 YAML 代码块
2. 验证顶层为列表
3. 逐项解析索引（支持 `int` 和 `"idx # name"` 字符串格式）
4. 验证每个索引在有效范围内
5. **验证无重复索引**
6. **验证所有抽象都被包含**（列表长度必须等于抽象总数），否则报错并列出缺失索引

**返回值** (list)：有序的抽象索引列表 `[int, ...]`，按教学顺序排列。

### post(shared, prep_res, exec_res)

将章节顺序写入 `shared["chapter_order"]`。

**写入的 shared 键**：
- `chapter_order`：`[int, ...]` 有序索引列表

## 排序设计原则

OrderChapters 的 prompt 明确指示 LLM 按以下原则排序：
- **先基础后深入**：先解释最重要、最基础的概念（如用户面向的入口点）
- **依赖前置**：被依赖的概念应在依赖它的概念之前出现
- **教学递进**：从高层概览到低层实现细节

## 源码位置

[nodes.py#L410-L534](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/nodes.py#L410-L534)
