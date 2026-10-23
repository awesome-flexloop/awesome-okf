---
type: Concept
title: Zvec Agent 集成：MCP 服务器、Skills 与 zvec-grep
description: 库侧 zvec-mcp-server 17 工具与 Agent Skills 领域知识注入，grep 侧 zg CLI 的单工具检索路由与 SWE-QA 评测收益
tags: [zvec, mcp, agent-skills, zvec-grep, cli, retrieval-routing]
generated: { by: "teleagent/seven-concepts-e", at: 2026-10-22T10:30:00+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-22T10:30:00+08:00 }
status: stable
stale_after: 2027-04-22
sources:
  - id: zvec-docs
    resource: /references/website-docs.md
    title: zvec.org 官方文档站信源
---

# Zvec Agent 集成：MCP 服务器、Skills 与 zvec-grep

Zvec 的 AI-Native 能力分两条产品线：**库侧**把数据库操作交给 Agent（MCP 17 工具）并注入领域知识（Skills）；**grep 侧**（zvec-ai/zvec-grep 独立仓库）面向开发者本人与 Agent 的本地工作区检索，刻意只暴露一个 MCP 工具。

## zvec-mcp-server：17 工具全量操作

经 MCP（Model Context Protocol）将 Zvec 全部功能暴露给 AI 助手，`uvx zvec-mcp-server` 分发（需 uv），环境变量 `OPENAI_API_KEY`（必填）、`OPENAI_BASE_URL`（可接 DashScope 兼容端点）、`OPENAI_EMBEDDING_MODEL`（默认 text-embedding-3-small）。

| 类别 | 工具 |
|---|---|
| Collection 管理（4） | create_and_open_collection / open_collection / get_collection_info / destroy_collection |
| Document 操作（5） | insert_documents / upsert_documents / update_documents / delete_documents / fetch_documents |
| 向量查询（2） | vector_query / multi_vector_query |
| 索引管理（3） | create_index / drop_index / optimize_collection |
| AI Embedding（3） | generate_dense_embedding / embedding_write / embedding_search |

接入示例（Claude Code）：`claude mcp add zvec-mcp uvx zvec-mcp-server -e OPENAI_API_KEY=sk-xxx`；Qoder 提供 `qodercli mcp add` 一键配置。验证方式：让 Agent `List all available MCP tools`，应返回 17 个工具。

## Agent Skills：注入领域经验

MCP 让 Agent 能*操作*数据库，但不理解"哪种场景用哪种索引、如何设计 Schema"这类经验。Skills 补齐认知层：

```bash
npx skills add github:zvec-ai/zvec-agent-skills --skill "zvec"
pip install zvec   # 或 npm install @zvec/zvec
```

安装后直接用自然语言描述业务场景（RAG 知识库、电商搜索），AI 给出 Schema 设计、索引策略与可运行代码。

## zvec-grep（zg）：本地工作区检索

面向开发者与 AI Agent 的 CLI（Node.js 22+，`npm install -g @zvec/zvec-grep`），把源代码、文档与文本数据转化为紧凑、来源可追溯的证据（路径 · 符号 · 行号）。基于 Zvec 检索内核，托管扫描→解析→分块→Embedding→索引全链路。

### 四条检索路径

| 命令 | 路径 |
|---|---|
| `zg query "认证流程"` | 默认混合（词法+向量联合排序） |
| `zg query --fts "AuthService"` | BM25 |
| `zg query --vector "凭证在哪里校验"` | 纯语义 |
| `zg query --rg -n -F "AuthService" src` | 内置 ripgrep 穷举（无需索引） |

组合形态：`zg query --hybrid "authentication flow" --fts "ForbiddenError" --fuse --limit 10`。缩窄范围：`-g` glob、`-t` 类型、`--modified-after/before`；新鲜度：`--refresh background|wait|off`。

### 索引管理

```bash
zg index --embedding local/potion-code-16m-v2   # 默认代码模型
zg index --embedding local/potion-retrieval-32m # 英文文档
zg status --check-ready
zg index --rebuild --embedding local/jina-embeddings-v2-base-code  # 换模型需重建
zg index --drop --yes                            # 显式删除
```

索引存于 `<workspace>/.zvec-grep/`。本地模型矩阵（文档表格 11 个条目）：Potion 三款（code-16m-v2 默认 / retrieval-32m / multilingual-128m）、ONNX 六款（all-minilm-l6-v2 / bge-small-en-v1.5 / multilingual-e5-small / jina-embeddings-v2-base-code / gte-modernbert-base / nomic-embed-text-v1.5）、GGUF 两款（embeddinggemma-300m / qwen3-embedding-0.6b）；设备 auto/cpu/metal/vulkan/cuda。远程模型 3 个（qwen/text-embedding-v4 等）需 `--allow-remote` 或 `zg auth grant --capability embedding --scope workspace` 授权。

### Agent 接入与检索路由

`zg install --target codex|claude|qwen|cursor|opencode|all|auto --yes` 接入 Agent；默认只暴露 **1 个 MCP 工具 `zvec_grep_search`**，调用形态 `{"root":..., "query":..., "fts":[...], "fuse":true}`。索引创建/重建/删除仍由用户 CLI 显式执行。

检索路由决策（Agent 何时用哪个工具）：

| 意图 | 路径 |
|---|---|
| 精确词语、标识符、文件名、路径、正则 | 原生 grep 或 rg |
| 措辞或位置未知、需跨文件/语义理解 | zvec_grep_search |
| 已知精确线索但需更广上下文 | 先 zvec_grep_search 再定向 grep/rg |
| 工作区外的开放知识 | 外部信息源 |

## 评测收益

SWE-QA-Bench（11 仓库 20 任务 × 3 次）：回答质量 **+1.50pp**、输入 Token **−47.3%**、工具调用 **−58.6%**、Agent 耗时 **−37.5%**。BrowseComp-Plus（100,195 篇文档 80 样例 × 2 次）：+0.33pp / −37.56% / −43.52% / −38.58%。评测对象是完整 Agent 任务（同任务/模型/Prompt/环境对照，仅增加 Zvec-Grep 索引与工具），非单次 CLI 延迟对比。

## 相关概念

- [总览](00-overview.md)：产品矩阵全景
- [量化](04-quantization.md)：zg 底层依赖的检索内核
- [zg CLI 实战](/examples/02-zvec-grep-cli.md)
