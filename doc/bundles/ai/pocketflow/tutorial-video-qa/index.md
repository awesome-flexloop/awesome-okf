---
title: AI Tutor 极简问答应用
type: index
bundle: tutorial-video-qa
version: 0.1.0
source: d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/
description: |
  基于 PocketFlow 框架的问答(QA)生成应用教程。本教程演示了如何使用 PocketFlow 构建
  一个最简的线性问答流水线：获取用户问题 → 调用 LLM 生成回答。包含2个核心节点、
  1个流程编排函数和1个 LLM 调用工具函数。
concepts:
  - linear-qa-pipeline: 线性问答流水线（GetQuestion→Answer 两阶段模式）
  - llm-integration-pattern: LLM 集成模式（在 Node 中封装 LLM 调用）
references:
  - get-question-node: GetQuestionNode — 获取用户问题节点
  - answer-node: AnswerNode — LLM 回答生成节点
  - create-qa-flow: create_qa_flow() — 创建问答流程工厂函数
  - call-llm: call_llm() — OpenAI LLM 调用工具函数
examples:
  - basic-qa-chat: 基础问答聊天完整示例
---

# Video Generator QA 教程

本教程是 [PocketFlow](https://github.com/The-Pocket/PocketFlow) 框架的入门级示例项目，演示了如何使用 PocketFlow 的节点（Node）和流程（Flow）抽象构建一个最简的问答应用。项目名为 "AI Tutor for Learning"，旨在通过 AI 辅助学习场景展示 PocketFlow 的核心用法。

## 架构概览

项目采用经典的**线性管道（Linear Pipeline）**模式，包含两个节点：

```
用户输入 → [GetQuestionNode] → shared["question"] → [AnswerNode] → shared["answer"] → 输出结果
```

1. **GetQuestionNode** — 从用户终端获取问题输入
2. **AnswerNode** — 调用 LLM（gpt-4o）生成回答

两个节点通过 `>>` 运算符顺序连接，通过 `shared` 字典传递数据。

## 文件结构

```
PocketFlow-Tutorial-Video-Generator/
├── nodes.py          # 节点定义（GetQuestionNode、AnswerNode）
├── flow.py           # 流程编排（create_qa_flow 工厂函数）
├── main.py           # 程序入口与示例运行
├── utils/
│   ├── __init__.py
│   └── call_llm.py   # LLM 调用工具函数
├── requirements.txt  # 依赖声明（pocketflow>=0.0.1）
└── README.md
```

## 快速导航

### 核心概念

- [线性问答流水线](concepts/linear-qa-pipeline.md) — prep→exec→post 三阶段在问答场景中的应用，线性管道模式
- [LLM 集成模式](concepts/llm-integration-pattern.md) — 如何在 PocketFlow 节点中封装外部 LLM API 调用

### API 参考

- [GetQuestionNode](references/get-question-node.md) — 获取用户问题的输入节点
- [AnswerNode](references/answer-node.md) — 调用 LLM 生成回答的处理节点
- [create_qa_flow()](references/create-qa-flow.md) — 创建并返回问答流程的工厂函数
- [call_llm()](references/call-llm.md) — 基于 OpenAI API 的 LLM 调用工具函数

### 示例

- [基础问答聊天](examples/basic-qa-chat.md) — 完整的问答聊天程序，包含环境配置和运行方法

## 运行前置条件

- Python 3.7+
- OpenAI API Key（设置环境变量 `OPENAI_API_KEY`）
- 安装依赖：`pip install pocketflow openai`

## 源码位置

- 项目根目录：[PocketFlow-Tutorial-Video-Generator/](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/)
- 节点定义：[nodes.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/nodes.py)
- 流程编排：[flow.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/flow.py)
- 程序入口：[main.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/main.py)
- 工具函数：[utils/call_llm.py](file:///d:/spaces/SpecWeave/external/libs/ai/ThePocket/PocketFlow-Tutorial-Video-Generator/utils/call_llm.py)

```{toctree}
:maxdepth: 7

concepts/linear-qa-pipeline
concepts/llm-integration-pattern
examples/basic-qa-chat
references/answer-node
references/call-llm
references/create-qa-flow
references/get-question-node
```
