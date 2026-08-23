---
type: concept
title: "生成与重排"
bundle: /datawhale/all-in-rag
description: "格式化生成（Pydantic结构化输出、Function Calling函数调用）、检索结果重排与精炼，将检索上下文转化为可控、可靠的最终回答"
sources: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter5/
related:
  - /datawhale/all-in-rag/concepts/retrieval-advanced
  - /datawhale/all-in-rag/concepts/evaluation-system
  - /datawhale/all-in-rag/concepts/rag-overview
tags: [generation, pydantic, function-calling, structured-output, rerank, prompt]
status: stable
---

# 生成与重排

## 核心理解

生成是 RAG 链路的最后一环——将检索到的文档片段转化为用户可读的回答。第五章聚焦**格式化生成**，解决 LLM 输出不可控的问题。检索阶段的重排技术（见[检索进阶技术](retrieval-advanced.md)）与生成阶段紧密配合：重排确保最相关的内容排在前面，生成模块则基于排序后的上下文产出结构化、忠实的回答。

## 格式化生成

LLM 原生输出是自由文本，在生产环境中往往需要结构化格式（如 JSON、表格、列表）以便下游程序处理。第五章介绍两种主流方案：

### Pydantic 结构化输出

Pydantic 是 Python 的数据验证库，可定义结构化数据模型：

```python
from pydantic import BaseModel, Field
from typing import List

class DishRecommendation(BaseModel):
    dish_name: str = Field(description="菜品名称")
    ingredients: List[str] = Field(description="所需食材")
    difficulty: str = Field(description="难度等级")
    steps: List[str] = Field(description="制作步骤")
```

结合 LangChain/LlamaIndex 的结构化输出能力，LLM 会被约束为按指定 Schema 输出，可直接解析为 Python 对象。优势包括：
- 输出格式可预测，便于程序处理
- 自动数据验证和类型检查
- 减少格式解析错误

### Function Calling（函数调用）

Function Calling 是 LLM 的原生能力，允许模型根据用户意图选择调用预定义函数并生成参数：

1. 开发者注册函数描述（名称、参数、用途）
2. LLM 判断是否需要调用函数，生成结构化调用参数
3. 应用执行函数，将结果返回 LLM
4. LLM 基于结果生成自然语言回答

在 RAG 中，Function Calling 可用于：
- 触发不同检索策略（如"搜索菜谱"vs"查询营养数据"）
- 调用外部工具（计算器、单位换算）
- 多步推理中的工具编排

代码示例位于 `code/C5/02_function_calling_example.py`。

## 生成策略

### 查询路由驱动的差异化生成

第八章实战展示了根据查询类型选择不同生成模式的策略：

- **列表查询（list）**：用户询问"有哪些菜"，直接返回菜品名称列表，不做过度展开
- **详细查询（detail）**：用户询问"怎么做"，使用分步指导模式（step-by-step），结构化展示食材和步骤
- **一般查询（general）**：使用基础回答模式

这种差异化生成避免了"杀鸡用牛刀"——简单问题给简洁答案，复杂问题给详细指导。

### 查询重写

在生成前，系统可通过 LLM 对原始查询进行智能重写：
- 补全省略的上下文
- 扩展相关关键词
- 将口语化表达转为规范表述

第八章中，列表查询保持原样（避免过度扩展导致检索偏差），详细和一般查询使用重写优化检索。

### 流式输出

支持 Streaming 输出，逐 token 返回生成结果，提升用户体验（首字延迟降低）。第八章和第九章均实现了流式生成接口。

## 重排与生成的协同

重排发生在检索之后、生成之前，是连接两个阶段的关键：

1. **初筛检索**：混合检索召回 Top-K（如 20 个）候选文档
2. **重排精炼**：Cross-Encoder 等重排模型对候选重新评分，取 Top-N（如 5 个）
3. **上下文组装**：按重排分数排序，截断到 LLM 上下文窗口
4. **Prompt 构建**：将精炼后的文档注入 Prompt，附带格式指令
5. **LLM 生成**：基于高质量上下文生成结构化回答

重排的价值在于"去粗取精"——初筛追求召回率（宁可多检不可漏检），重排追求精确率（只把最相关的送给 LLM），既提升答案质量又节省 Token 成本。

## 代码实践

第五章代码位于 `code/C5/`：
- `01_pydantic.py`——Pydantic 结构化输出示例
- `02_function_calling_example.py`——Function Calling 示例

第八章的生成模块位于 `code/C8/rag_modules/generation_integration.py`，整合了 Kimi API 调用、查询路由、查询重写和多种生成模式。

## 延伸阅读

- [检索进阶技术](retrieval-advanced.md)——重排技术的详细解析
- [评估体系](evaluation-system.md)——忠实度与答案相关性评估
- [项目实战](project-practice.md)——生成模块的完整工程实现
