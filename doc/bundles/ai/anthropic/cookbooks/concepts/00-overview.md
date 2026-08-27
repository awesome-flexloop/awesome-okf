---
type: concept
title: "Cookbook 导览"
description: "Claude Cookbooks 是什么、前置条件、快速开始、六大能力域地图、如何选择适合的 Cookbook，以及与 Python SDK Wiki 的关系。"
tags: [cookbook, overview, getting-started, capabilities, examples]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# Cookbook 导览

**Claude Cookbooks** 是 Anthropic 官方维护的代码示例集，包含可直接运行的 Jupyter Notebook 和 Python 脚本，覆盖从基础能力到高级技巧的完整场景。与抽象的 API 文档不同，Cookbooks 提供"拿来即用"的实践配方——每个示例都是一个完整的端到端解决方案，你可以直接复制、修改、集成到自己的项目中。

如果把 SDK 文档比作"食材清单和烹饪原理"，那么 Cookbooks 就是"已经写好的菜谱"——精确的步骤、可运行的代码、经过验证的最佳实践。

## Cookbooks 是什么

Claude Cookbooks 的核心价值：

| 特性 | 说明 |
|------|------|
| **可复制的代码片段** | 每个示例都是独立可运行的，无需复杂配置即可上手 |
| **实践导向** | 聚焦真实场景，而非 API 参数罗列 |
| **模式提炼** | 展示解决一类问题的通用模式，而非单一用例 |
| **最佳实践** | 官方推荐的提示词、错误处理、性能优化方案 |
| **Jupyter + Python 双格式** | 既可以交互式运行 Notebook，也可以直接使用 `.py` 脚本 |

## 前置条件

在使用 Cookbooks 之前，你需要：

1. **Anthropic API Key**：在 [console.anthropic.com](https://console.anthropic.com) 注册并获取 API Key
2. **Python 3.10+**：Cookbooks 使用现代 Python 语法和类型注解
3. **Python 基础**：了解基本的 Python 语法、函数、字典操作即可
4. **uv 包管理器**（推荐）：官方使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理，比 pip 快 10-100 倍

## 快速开始

```bash
# 1. 克隆官方 cookbooks 仓库
git clone https://github.com/anthropics/anthropic-cookbook.git
cd anthropic-cookbook

# 2. 使用 uv 同步依赖（推荐）
uv sync

# 或者使用 pip
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 ANTHROPIC_API_KEY

# 4. 运行示例（以文本分类为例）
cd skills/classification
jupyter notebook classification.ipynb
# 或者直接运行 Python 脚本
python classification.py
```

### 最小可运行示例

如果你不想克隆整个仓库，这里是一个最小的"Hello Cookbook"示例：

```python
from anthropic import Anthropic
from dotenv import load_dotenv
import os

load_dotenv()
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def classify_text(text: str, categories: list[str]) -> str:
    """最简单的文本分类 Cookbook 模式"""
    prompt = f"""请将以下文本分类到给定类别中。只返回类别名称，不要其他解释。

文本：{text}
可选类别：{', '.join(categories)}"""

    response = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()

# 使用
result = classify_text("我的订单什么时候发货？", ["咨询", "投诉", "建议", "其他"])
print(f"分类结果：{result}")
```

## 六大能力域地图

Cookbooks 按能力域分为六大类，对应不同的应用场景和技术难度：

```
┌─────────────────────────────────────────────────────────────────┐
│                    Claude Cookbooks 能力域                      │
├─────────────────┬─────────────────┬─────────────────────────────┤
│  核心能力        │  工具使用        │  第三方集成                 │
│  Capabilities   │  Tool Use       │  Third-Party Integrations   │
│                 │                 │                             │
│  • 分类         │  • 客服 Agent   │  • Pinecone 向量数据库      │
│  • RAG 检索     │  • 计算器工具   │  • Wikipedia 搜索           │
│  • 摘要         │  • SQL 查询     │  • Voyage AI Embeddings     │
│  • Text-to-SQL  │                 │  • Web 页面读取             │
│  • 知识图谱     │                 │                             │
│  • 上下文嵌入   │                 │                             │
│  • 内容审核     │                 │                             │
├─────────────────┴─────────────────┼─────────────────────────────┤
│  多模态能力        Multimodal      │  高级技巧  Advanced          │
│                                   │                             │
│  • Vision 入门                    │  • Sub-agents 子 Agent      │
│  • Vision 最佳实践                │  • PDF 上传与解析           │
│  • 图表/PPT 解读                  │  • 自动化评估 Evals         │
│  • 表单/文字提取                  │  • JSON 模式                │
│  • 图片生成（Stable Diffusion）   │  • Prompt Caching 缓存      │
│                                   │  • 成本优化                 │
│                                   │  • Extended Thinking 扩展思考│
│                                   │  • Fine-tuning 微调         │
│                                   │  • 前端美学提示             │
├───────────────────────────────────┴─────────────────────────────┤
│              Claude Agent SDK 示例（企业级 Agent）               │
│                                                                 │
│  • 幕僚长 Agent (chief_of_staff)    • SRE Agent                 │
│  • 可观测性 Agent (observability)   • 漏洞检测 Agent            │
│  • 研究 Agent (research)           • Docker/K8s/Modal 部署      │
└─────────────────────────────────────────────────────────────────┘
```

### 能力域难度梯度

| 能力域 | 难度 | 学习曲线 | 建议学习顺序 |
|--------|------|----------|-------------|
| 核心能力（Capabilities） | ⭐ | 平缓 | 第 1 步 |
| 工具使用（Tool Use） | ⭐⭐ | 中等 | 第 2 步 |
| 多模态（Multimodal） | ⭐⭐ | 中等 | 第 3 步 |
| 第三方集成 | ⭐⭐⭐ | 较陡 | 按需学习 |
| 高级技巧 | ⭐⭐⭐⭐ | 陡峭 | 有基础后 |
| Agent SDK | ⭐⭐⭐⭐⭐ | 最陡 | 企业级场景 |

## 如何选择适合的 Cookbook

根据你的需求场景快速定位：

### 我想让 Claude 处理文本...
- **分类打标签** → [classification](/cookbooks/concepts/03-rag-patterns.md) 相关食谱
- **从文档中找答案** → [RAG 模式](/cookbooks/concepts/03-rag-patterns.md)
- **总结长文/会议记录** → summarization 食谱
- **自然语言查数据库** → text_to_sql 食谱
- **审核内容合规性** → content_moderation 食谱

### 我想让 Claude 调用工具/执行动作...
- **理解工具调用基础** → [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md)
- **做客服/多轮对话** → customer_service_agent 食谱
- **做数学计算** → calculator_tool 食谱
- **查数据库** → SQL queries 食谱

### 我想处理图片/PDF/多模态...
- **理解视觉能力基础** → [多模态模式](/cookbooks/concepts/02-multimodal-patterns.md)
- **识别图片内容** → Vision 入门/最佳实践
- **解读图表 PPT** → 图表解读食谱
- **提取表单文字** → OCR/表单提取食谱
- **处理 PDF** → PDF 上传解析食谱
- **生成图片** → Stable Diffusion 集成食谱

### 我想做生产级优化...
- **减少 Token 成本** → [高级技巧 - 成本优化](/cookbooks/concepts/04-advanced-techniques.md)
- **加快响应速度** → Prompt Caching
- **复杂推理任务** → Extended Thinking
- **保证输出格式** → JSON 模式
- **自动评估效果** → Evals 框架
- **多模型协作** → Sub-agents
- **微调模型** → Fine-tuning on Bedrock

### 我想构建企业级 Agent...
- **理解 Agent 架构** → [高级技巧 - Sub-agents](/cookbooks/concepts/04-advanced-techniques.md)
- **任务编排 Agent** → chief_of_staff_agent
- **运维监控 Agent** → observability_agent / site_reliability_agent
- **安全扫描 Agent** → vulnerability_detection_agent
- **深度研究 Agent** → research_agent
- **部署上线** → hosting (Docker/K8s/Modal)

## 与 Python SDK Wiki 的关系

本 Cookbook Wiki 与 [Python SDK Wiki](/python-sdk/index.md) 是互补关系，定位不同：

| 维度 | Python SDK Wiki | Claude Cookbooks Wiki |
|------|----------------|----------------------|
| **定位** | API 参考与概念解释 | 实践配方与完整示例 |
| **内容形式** | 结构化概念文档 + API 参考 | 可运行代码 + 模式总结 |
| **回答的问题** | "这个参数是什么意思？" | "这个场景怎么做？" |
| **阅读方式** | 从头到尾系统学习 | 按需查阅，复制即用 |
| **代码量** | 片段化示例 | 完整可运行项目 |
| **适合阶段** | 入门打基础 | 上手做项目 |

### 阅读路径建议

```
Python SDK Wiki（打基础）
    ↓
    ├─ 00-overview → 理解 SDK 架构
    ├─ 02-messages-basics → 掌握消息 API
    ├─ 04-tool-use → 理解工具调用原理
    └─ 05-vision-files → 理解多模态基础
            ↓
    Claude Cookbooks Wiki（做项目）
            ↓
    ├─ 选择对应能力域的 concept 文档
    ├─ 在 recipe-index 找到具体示例
    └─ 复制代码 → 修改适配 → 集成上线
```

简单来说：**SDK Wiki 教你"Claude 能做什么"，Cookbooks 教你"用 Claude 做成这件事的最佳方式"**。

## 相关概念

- [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md) — 深入理解 Function Calling 的各种实践模式
- [多模态模式](/cookbooks/concepts/02-multimodal-patterns.md) — Vision、PDF、图片处理的实践方案
- [RAG 与知识检索模式](/cookbooks/concepts/03-rag-patterns.md) — 检索增强生成的完整实践
- [高级技巧](/cookbooks/concepts/04-advanced-techniques.md) — 缓存、扩展思考、子 Agent 等进阶能力
- [食谱完整索引](/cookbooks/references/recipe-index.md) — 按能力域分类的所有 Cookbook 速查表
- [Python SDK - 工具调用概念](/python-sdk/concepts/04-tool-use.md) — 工具调用的底层 API 原理
