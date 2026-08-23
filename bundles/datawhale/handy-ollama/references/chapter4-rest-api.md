---
okf_version: "0.2"
type: reference
title: "第四章 Ollama REST API"
bundle: /datawhale/handy-ollama
sources:
  - https://github.com/datawhalechina/handy-ollama/blob/main/docs/C4/
tags: [chapter4, api, rest, sdk, python, java, javascript, cpp, golang]
status: stable
---

# 第四章 Ollama REST API

## 信源定位

- **源码路径**：`docs/C4/`（6 节）+ `notebook/C4/`（多语言代码示例）
- **在线阅读**：[第四章](https://datawhalechina.github.io/handy-ollama/#/C4/)
- **内容性质**：API 参考，端点说明和多语言调用实践

## 章节结构

| 节 | 文件 | 核心内容 |
|----|------|----------|
| 4.1 | `1. Ollama API 使用指南.md` | /api/generate、/api/chat、/api/embed、模型管理端点、流式/非流式、JSON 模式、多模态、工具调用 |
| 4.2 | `2. 在 Python 中使用 Ollama API.md` | ollama Python 库、requests 调用、流式响应处理 |
| 4.3 | `3. 在 Java 中使用 Ollama API.md` | OkHttp 调用、Spring AI 集成 |
| 4.4 | `4. 在 JavaScript 中使用 Ollama API.md` | Node.js fetch、流式处理 |
| 4.5 | `5. 在 C++ 中使用 Ollama API.md` | libcurl/cpr 库调用、nlohmann/json 解析 |
| 4.6 | `6. 在 Golang 中使用 Ollama API.md` | ollama-go 客户端、chat/generate-streaming/structured output |

## 关键事实

- 默认 API 地址：`http://localhost:11434`
- 核心推理端点：`POST /api/generate`（生成补全）、`POST /api/chat`（对话补全）、`POST /api/embed`（嵌入）
- /api/generate 参数：model、prompt、system、context、stream、format(json)、images(base64)、options(temperature/seed)、keep_alive
- /api/chat 支持 messages 数组（role: system/user/assistant/tool）和 tools 工具调用
- 流式响应返回 JSON 对象流，最终对象含 total_duration/eval_count/eval_duration 等统计
- format=json 强制 JSON 输出（需在 prompt 中指示模型）
- 多模态通过 images 参数传入 base64 编码图片（llava 等模型）
- 模型管理端点：/api/create、/api/copy、/api/delete、/api/pull、/api/push、/api/tags、/api/ps、/api/show
- keep_alive 默认 5m，控制模型在内存中保留时间

## 代码资产

- `notebook/C4/在 Python 中使用 Ollama API.ipynb`
- `notebook/C4/C++_API_example/`：simple_example.cpp + call_ollama.py
- `notebook/C4/Golang_API_example/`：chat/generate-streaming/structured_output 三个示例
- `notebook/C4/Java_API_example/`：simple_example + springai_demo

## 关联概念

- [API 与 OpenAI 兼容接口](../concepts/api-openai-compatibility.md) — API 端点和 OpenAI 兼容层的系统整理
- [快速启动第一个本地模型](../examples/quickstart-first-model.md) — curl/Python 调用实战
