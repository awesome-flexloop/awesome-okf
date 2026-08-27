---
okf_version: "0.2"
type: index
title: "Claude Cookbooks Wiki"
description: "Anthropic官方Claude Cookbook示例集中文文档——工具调用、多模态、RAG、子Agent、Extended Thinking、提示缓存、Agent SDK等核心模式与食谱索引。"
tags: [cookbook, examples, tool-use, multimodal, rag, agents, prompt-caching, extended-thinking]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# Claude Cookbooks Wiki

**Claude Cookbooks** 是 Anthropic 官方维护的代码示例集，包含可直接运行的 Jupyter Notebook 和 Python 脚本。与抽象的 API 文档不同，Cookbooks 提供"拿来即用"的实践配方——每个示例都是一个完整的端到端解决方案，覆盖从基础文本分类到企业级 Agent SDK 部署的全场景。

如果把 [Python SDK Wiki](/python-sdk/index.md) 比作"食材清单和烹饪原理"，那么本 Cookbooks Wiki 就是"已经写好的菜谱"——精确的步骤、可运行的代码、经过验证的最佳实践模式。

## 快速开始

```bash
# 1. 克隆官方仓库
git clone https://github.com/anthropics/anthropic-cookbook.git
cd anthropic-cookbook

# 2. 使用 uv 同步依赖（推荐）
uv sync

# 3. 配置 API Key
cp .env.example .env
# 编辑 .env 填入 ANTHROPIC_API_KEY

# 4. 运行你的第一个 Cookbook
cd skills/classification
jupyter notebook classification.ipynb
```

最小可运行示例（无需克隆仓库）：

```python
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def classify(text: str, categories: list[str]) -> str:
    """Cookbook 中最简单的文本分类模式"""
    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": f"将这段文本分类到以下类别之一：{', '.join(categories)}\n文本：{text}\n只返回类别名称。"
        }]
    )
    return response.content[0].text.strip()

print(classify("我的订单怎么还没发货？", ["咨询", "投诉", "建议"]))
```

## 文档导航

### 📚 概念文档（Cookbook 模式提炼）

概念文档从官方 Cookbook 示例中提炼出**可复用的通用模式**——不只是某个具体示例的代码，而是解决一类问题的方法论：

| 序号 | 主题 | 内容覆盖 |
|------|------|---------|
| 00 | [Cookbook 导览](/cookbooks/concepts/00-overview.md) | Cookbooks 定位、前置条件、快速开始、六大能力域地图、如何选择 Cookbook、与 SDK Wiki 的关系 |
| 01 | [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md) | Function Calling 基础流程、客服 Agent 多轮模式、计算器确定性函数、Text-to-SQL 模式、工具错误处理、并行调用 |
| 02 | [多模态模式](/cookbooks/concepts/02-multimodal-patterns.md) | Vision 最佳实践、图表/PPT 解读、OCR 表单提取、PDF 处理、图片生成配合 Stable Diffusion、提示词技巧 |
| 03 | [RAG 与知识检索模式](/cookbooks/concepts/03-rag-patterns.md) | 基础 RAG 流程、文档切分策略、Pinecone 等向量数据库集成、上下文嵌入优化、知识图谱增强、Evals 评估 |
| 04 | [高级技巧](/cookbooks/concepts/04-advanced-techniques.md) | Sub-agents 多模型协作、Extended Thinking、Prompt Caching（降本90%）、JSON 模式、自动化 Evals、成本优化、微调 |

### 📖 参考索引（食谱速查表）

| 参考文档 | 内容覆盖 |
|---------|---------|
| [食谱完整索引](/cookbooks/references/recipe-index.md) | 六大能力域、30+ 个 Cookbook recipe 的完整表格索引：名称、源路径、核心技术、一句话说明、按难度分级 |

## 六大能力域一览

```
┌─────────────────────────────────────────────────────────────────┐
│  核心能力 Capabilities    │  文本分类、RAG、摘要、Text-to-SQL、知识图谱、嵌入、内容审核
├─────────────────────────────────────────────────────────────────┤
│  工具使用 Tool Use        │  客服 Agent、计算器、SQL 查询
├─────────────────────────────────────────────────────────────────┤
│  多模态 Multimodal        │  Vision 入门、图表解读、OCR、PDF、图片生成
├─────────────────────────────────────────────────────────────────┤
│  高级技巧 Advanced        │  Sub-agents、Extended Thinking、Prompt Caching、JSON、Evals
├─────────────────────────────────────────────────────────────────┤
│  Agent SDK                │  幕僚长/SRE/研究/安全 Agent、Docker/K8s 部署
├─────────────────────────────────────────────────────────────────┤
│  第三方集成 Integrations  │  Pinecone、Wikipedia、Voyage AI、Web 抓取
└─────────────────────────────────────────────────────────────────┘
```

## 与 Python SDK Wiki 的关系

本 Cookbooks Wiki 与 [Python SDK Wiki](/python-sdk/index.md) 是互补关系：

| 维度 | Python SDK Wiki | Claude Cookbooks Wiki |
|------|----------------|----------------------|
| **回答的问题** | "这个 API/参数是什么意思？" | "这个场景用 Claude 怎么做？" |
| **内容形式** | 系统化概念文档 + API 参考 | 实践模式提炼 + 可运行食谱索引 |
| **代码示例** | 片段化（说明概念用） | 完整可运行端到端方案 |
| **阅读方式** | 从头到尾系统学习 | 按需查阅、复制即用 |
| **适合阶段** | 入门打基础 | 上手做项目、解决具体问题 |

### 推荐学习路径

```
第一步：SDK Wiki 打基础
  └─ /python-sdk/concepts/00-overview → 理解 SDK 架构
  └─ /python-sdk/concepts/02-messages-basics → Messages API
  └─ /python-sdk/concepts/04-tool-use.md → 工具调用原理
  └─ /python-sdk/concepts/05-vision-files.md → 多模态基础
          ↓
第二步：Cookbooks Wiki 做项目
  └─ /cookbooks/concepts/00-overview.md → 选择对应能力域
  └─ /cookbooks/concepts/XX-xxx-patterns.md → 理解该类问题的模式
  └─ /cookbooks/references/recipe-index.md → 找到具体 recipe
  └─ 克隆仓库 → 复制代码 → 修改适配 → 集成上线
```

## 链接索引

- [概念文档索引](/cookbooks/concepts/index.md)
- [参考索引](/cookbooks/references/index.md)
- [Python SDK Wiki](/python-sdk/index.md)
- 官方仓库：https://github.com/anthropics/anthropic-cookbook

```{toctree}
:maxdepth: 2

concepts/index
references/index
log
```
