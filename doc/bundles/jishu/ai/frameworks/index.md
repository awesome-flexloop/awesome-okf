---
okf_version: "0.2"
type: category
title: "🧩 Agent 与 LLM 应用框架"
description: "Agent 与 LLM 应用的开发框架、运行时与代码库源码教程——以 ai-agent（58 束）与 langchain-ai（19 束）两大仓库集群为核心，辅以极简框架、分词、推理、决策模型、AI 原生搜索引擎（XERJ）、嵌入式向量检索库（Zvec）与 JIT 编译量化 GEMM 内核库（Humming）等基础库。"
---

# 🧩 Agent 与 LLM 应用框架

Agent 与 LLM 应用的开发框架、运行时与代码库源码教程——以 ai-agent（58 束）与 langchain-ai（19 束）两大仓库集群为核心，辅以极简框架、分词、推理、决策模型、AI 原生搜索引擎（XERJ）、嵌入式向量检索库（Zvec）与 JIT 编译量化 GEMM 内核库（Humming）等基础库。

本类共 **91 个知识包**，分布于 **12 个生态/项目目录**。

## 束导航

| 知识包 | 束数 | 一句话简介 |
|--------|------|-----------|
| [🤖 AI Agent 框架](ai-agent/index.md) | 58 | AI Agent 运行时框架与架构模式——工具调用循环、多代理编排、记忆系统、Coding Agent 源码解读、知乎开放平台官方文档全集精读、Hypit 视频复刻工作流与 Tongyi-MAI GUI Agent 生态源码精读 |
| [🦜🔗 LangChain-AI LLM 应用框架](langchain-ai/index.md) | 19 | LangChain/LangGraph 核心框架（Python+JS）、深度研究 Agent、可观测性、评测与基础设施 |
| [⚡ PocketFlow 极简 LLM 应用框架](pocketflow/index.md) | 5 | 100 行代码的极简 LLM Agent 框架——节点+流程抽象、6 大设计模式、实战教程 |
| [🕷️ Firecrawl 网页数据 API](firecrawl/index.md) | 1 | 微信博文经 OKF v0.2 七阶段转化（技术综述非操作教程）——18 万 Star 开源 web context API：七端点、Agent 与 /extract、spark-1 弃用→spark-2、九 SDK/CLI/MCP、开源 vs 云分界与 AGPL 边界（两轮 26 簇核验 20✅/5⚠️/2❌） |
| [🔢 tiktoken BPE 分词库](tiktoken/index.md) | 1 | OpenAI 官方 BPE 分词库源码教程——薄 Python 门面 + 重型 Rust 核心（PyO3）双层架构 |
| [🦙 llama.cpp 本地 LLM 推理](llama-cpp-local-inference/index.md) | 1 | 微信博文经 OKF v0.2 七阶段转化——C/C++ 本地推理、GGUF/Q4 与内存预算、CPU/Metal 后端、llama-server 与 OpenAI 兼容迁移（技术体验综述非操作教程，6✅/4⚠️/1❌，含 4GB/7B 勘误） |
| [Jev 决策模型与十类应用](jev/index.md) | 1 | TypeSafe System One模型概念教程：Noul/Choice/Score、十案例的状态与执行分工、工程评测；flagged保留原帖和成效证据缺口，非操作教程 |
| [Jev 自动化决策引擎](jev-automation-decision/index.md) | 1 | 当前微信文章的 Jev 自动化场景解读——System One、客服/游戏/浏览器/安全四类模式与端到端评测边界；flagged，非操作教程 |
| [🔎 XERJ AI 原生搜索引擎](xerj/index.md) | 1 | Rust 从零实现的 AI 原生搜索引擎——18 crate 架构、autoindex 零配置摄取流水线、17 个 MCP 工具、向量与混合检索、第二大脑与参考编码，附诚实的边界与基准 |
| [🦎 vLLM 高性能推理引擎](vllm/index.md) | 1 | vLLM 高性能大模型推理引擎源码教程——PagedAttention 显存管理、连续批处理调度、KV Cache 分块、量化与推测解码、分布式并行与 OpenAI 兼容服务 |
| [🐦 Humming 量化 GEMM 内核库](humming/index.md) | 1 | JIT 编译的量化推理 GEMM 内核库源码教程——统一量化表示与支持矩阵、三层配置架构、三条 CUDA 流水线、MoE grouped 路径与 vLLM 集成 |
| [⚡ Zvec 嵌入式向量数据库](zvec/index.md) | 1 | Alibaba 开源进程内向量检索库源码教程——四层 C++ 架构（ailego/turbo/core/db）、六种索引、RaBitQ 量化双轨、FTS/ANTLR 过滤引擎、混合检索与 MCP/zvec-grep Agent 集成 |

```{toctree}
:hidden:
:maxdepth: 7

ai-agent/index
langchain-ai/index
pocketflow/index
firecrawl/index
tiktoken/index
llama-cpp-local-inference/index
jev/index
jev-automation-decision/index
xerj/index
vllm/index
humming/index
zvec/index
```
