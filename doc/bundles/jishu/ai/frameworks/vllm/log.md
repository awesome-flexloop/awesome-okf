---
type: Log
title: "更新日志"
description: "vLLM 知识包更新日志"
tags: [vllm, changelog, log]
status: stable
---

# 更新日志

## 2026-10-22

**Created**: vLLM v0.32 OKF 知识包（七概念方法论 R→I→E→V，源码 + 官网双信源）

- 基于本地源码检出 `v0.32.1rc0-283`（2026-10-22）与 vllm.ai 官网/文档站（stable 0.32.0）整理
- 结构：index + concepts/（00–13，入门 3 篇 / 核心 5 篇 / 场景 3 篇 / 进阶 2 篇）+ examples/（4 类典型场景）+ references/（facts 155 条 / source-map / verification）+ log
- 编号事实 F-001~F-155 全部标注来源；三处双源口径差异（版本号、Python 要求、模型计数）已在 verification.md 解释
- 关联包：llama-cpp-local-inference（同门本地推理）、tiktoken（分词基础）、langchain-ai（上层应用框架）
