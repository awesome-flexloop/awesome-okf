---
title: IdentifyAbstractions
type: reference
bundle: tutorial-codebase-knowledge
source: nodes.py
---

# IdentifyAbstractions

`IdentifyAbstractions` 是流水线的第二个节点，负责使用 LLM 分析全部源码，识别出 5-10 个核心抽象（abstraction）。它继承自 PocketFlow 的 `Node` 类，重试配置为 `max_retries=5, wait=20`。

## 类定义

```python
class IdentifyAbstractions(Node):
```

源码位置：nodes.py#L84-L237

## 生命周期方法

### prep(shared)

从 `shared` 读取文件列表和配置参数，构建发送给 LLM 的完整代码上下文。

**读取的 shared 键**：
- `files`：`[(path, content), ...]` 文件元组列表（来自 FetchRepo）
- `project_name` (str)：项目名称
- `language` (str)：输出语言，默认 `"english"`
- `use_cache` (bool)：是否启用 LLM 缓存，默认 `True`
- `max_abstraction_num` (int)：最大抽象数量，默认 `10`

**内部逻辑**：
1. 调用内部函数 `create_llm_context(files_data)` 将所有文件拼接为上下文字符串，格式为 `--- File Index {i}: {path} ---\n{content}\n\n`
2. 生成文件索引列表字符串（`- {idx} # {path}` 格式）

**返回值** (tuple)：
- `context`：完整代码上下文字符串
- `file_listing_for_prompt`：文件索引列表
- `file_count`：文件总数
- `project_name`：项目名
- `language`：语言
- `use_cache`：缓存开关
- `max_abstraction_num`：最大抽象数

### exec(prep_res)

向 LLM 发送 prompt，要求识别核心抽象，并严格验证 LLM 返回的 YAML 格式。

**Prompt 核心要求**：
1. 分析代码库，识别 top 5 到 `max_abstraction_num` 个核心抽象
2. 每个抽象包含三个字段：
   - `name`：简洁名称（非英语时为翻译后的名称）
   - `description`：约100字的新手友好描述，含类比
   - `file_indices`：相关文件索引列表
3. 输出 YAML 列表格式

**验证逻辑**：
1. 从 LLM 响应中提取 ` ```yaml ... ``` ` 代码块
2. 使用 `yaml.safe_load()` 解析
3. 验证顶层为列表（list）
4. 逐项验证每个抽象项：
   - 必须包含 `name`、`description`、`file_indices` 三个键
   - `name` 必须是字符串
   - `description` 必须是字符串
   - `file_indices` 必须是列表
5. 验证每个文件索引在有效范围内（0 到 file_count-1）
6. 去重并排序文件索引

**多语言支持**：当 `language` 不为 `"english"` 时，在 prompt 中加入语言指令，要求 LLM 用指定语言生成 name 和 description。

**返回值** (list)：验证后的抽象列表，每项为：
```python
{
    "name": str,        # 抽象名称（可能已翻译）
    "description": str, # 描述（可能已翻译）
    "files": [int, ...] # 去重排序后的文件索引列表
}
```

### post(shared, prep_res, exec_res)

将抽象列表写入 `shared["abstractions"]`。

**写入的 shared 键**：
- `abstractions`：`[{"name": str, "description": str, "files": [int]}]`

## 内部辅助函数

### get_content_for_indices(files_data, indices)

源码位置：nodes.py#L11-L19

根据索引列表从 `files_data` 中提取对应文件内容，返回 `{"{i} # {path}": content}` 字典。被本节点后续的 AnalyzeRelationships 和 WriteChapters 节点复用。

参数：
- `files_data`：`[(path, content), ...]` 文件列表
- `indices`：`[int, ...]` 文件索引列表

返回：`{f"{i} # {path}": content}` 字典

## 源码位置

nodes.py#L84-L237
