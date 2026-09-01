---
type: reference
title: "第五章 生成集成"
bundle: /datawhale/all-in-rag
description: "格式化生成技术——Pydantic结构化输出与Function Calling函数调用，解决LLM输出格式不可控问题"
source: https://github.com/datawhalechina/all-in-rag/blob/main/docs/chapter5/
path: docs/chapter5/
code:
  - code/C5/
tags: [generation, pydantic, function-calling, structured-output, formatting]
status: stable
---

# 第五章 生成集成

## 信源信息

- **章节路径**：`docs/chapter5/`
- **代码路径**：`code/C5/`
- **小节列表**：
  - 第一节 格式化生成（`16_formatted_generation.md`）

## 内容概要

### 第一节 格式化生成

LLM 原生输出为自由文本，生产环境需要结构化格式以便程序处理。本章介绍两种方案：

- **Pydantic 结构化输出**：定义数据模型 Schema，约束 LLM 按指定 JSON 结构输出，自动类型验证
- **Function Calling（函数调用）**：LLM 原生能力，根据用户意图选择预定义函数并生成参数，支持工具编排和多步推理

## 代码资产

| 文件 | 职责 |
|------|------|
| `code/C5/01_pydantic.py` | Pydantic 结构化输出示例 |
| `code/C5/02_function_calling_example.py` | Function Calling 示例 |

## 对应概念

- [生成与重排](../concepts/generation-rerank.md)
