---
title: AnalyzeRelationships
type: reference
bundle: tutorial-codebase-knowledge
source: nodes.py
---

# AnalyzeRelationships

`AnalyzeRelationships` 是流水线的第三个节点，负责使用 LLM 分析已识别的抽象之间的关系，生成项目概述和抽象间关系图。它继承自 PocketFlow 的 `Node` 类，重试配置为 `max_retries=5, wait=20`。

## 类定义

```python
class AnalyzeRelationships(Node):
```

源码位置：[nodes.py#L240-L408](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/nodes.py#L240-L408)

## 生命周期方法

### prep(shared)

从 `shared` 读取抽象列表和文件数据，构建包含抽象信息和相关代码片段的上下文。

**读取的 shared 键**：
- `abstractions`：抽象列表（来自 IdentifyAbstractions）
- `files`：`[(path, content), ...]` 文件列表
- `project_name` (str)：项目名称
- `language` (str)：输出语言，默认 `"english"`
- `use_cache` (bool)：是否启用 LLM 缓存，默认 `True`

**内部逻辑**：
1. 遍历所有抽象，格式化抽象信息行（`- Index {i}: {name} (Relevant file indices: [{files}])\n  Description: {description}`）
2. 收集所有抽象引用的文件索引（取并集）
3. 调用 [get_content_for_indices()](identify-abstractions.md#get_content_for_indicesfiles_data-indices) 提取相关文件内容
4. 拼接上下文字符串

**返回值** (tuple)：
- `context`：包含抽象描述和相关代码片段的上下文
- `abstraction_listing`：抽象索引列表字符串（`{i} # {name}` 格式）
- `num_abstractions`：抽象总数
- `project_name`：项目名
- `language`：语言
- `use_cache`：缓存开关

### exec(prep_res)

向 LLM 发送 prompt，要求分析抽象间关系并生成项目概述。

**Prompt 核心要求**：
1. `summary`：用新手友好的语言概述项目主要功能，支持 Markdown 加粗和斜体
2. `relationships`：抽象间关键交互关系列表，每项包含：
   - `from_abstraction`：源抽象索引（如 `0 # AbstractionName`）
   - `to_abstraction`：目标抽象索引
   - `label`：简洁的关系标签（如 "Manages"、"Inherits"、"Uses"）
3. **关键约束**：每个抽象必须至少参与一个关系（作为源或目标）

**验证逻辑**：
1. 从 LLM 响应提取 YAML 代码块
2. 验证顶层为字典，且包含 `summary` 和 `relationships` 键
3. 验证 `summary` 为字符串
4. 验证 `relationships` 为列表
5. 逐项验证关系：
   - 必须包含 `from_abstraction`、`to_abstraction`、`label` 三个键
   - `label` 必须是字符串
   - 索引必须在有效范围内（0 到 num_abstractions-1）
6. 解析索引（支持 `int` 和 `"idx # name"` 字符串格式）

**多语言支持**：当 `language` 不为 `"english"` 时，要求 LLM 用指定语言生成 `summary` 和 `label`。

**返回值** (dict)：
```python
{
    "summary": str,       # 项目概述（可能已翻译）
    "details": [          # 验证后的关系列表
        {
            "from": int,  # 源抽象索引
            "to": int,    # 目标抽象索引
            "label": str  # 关系标签（可能已翻译）
        },
        ...
    ]
}
```

### post(shared, prep_res, exec_res)

将关系数据写入 `shared["relationships"]`。

**写入的 shared 键**：
- `relationships`：`{"summary": str, "details": [{"from": int, "to": int, "label": str}]}`

## 源码位置

[nodes.py#L240-L408](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Codebase-Knowledge/nodes.py#L240-L408)
