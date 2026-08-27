---
type: reference
title: "食谱完整索引"
description: "Claude Cookbooks 按能力域分类的完整食谱索引，包含核心能力、工具使用、多模态、高级技巧、Agent SDK、第三方集成六大类所有 recipe 的源路径、核心技术和一句话说明。"
tags: [reference, index, recipes, cookbook, catalog]
generated: { by: "process:content-structuring", at: "2026-08-27" }
status: stable
stale_after: 2027-08-27
---

# 食谱完整索引

本文档是 Claude Cookbooks 所有可用 recipe（食谱/示例）的完整索引，按能力域分类整理。每个 recipe 对应官方仓库中的一个 Jupyter Notebook 或 Python 脚本，可以直接复制运行。

> 官方仓库地址：`https://github.com/anthropics/anthropic-cookbook`
>
> 源路径是相对于仓库根目录的路径。

---

## 一、核心能力（Capabilities）

这类 Cookbook 展示 Claude 的基础 NLP 能力，不依赖外部工具，是最容易上手的入门示例。

| 名称 | 源路径 | 核心技术 | 一句话说明 |
|------|--------|---------|-----------|
| 文本分类 | `skills/classification/` | 提示工程、Few-shot | 将文本分类到预定义类别，支持情感分析、意图识别、主题分类等场景 |
| 检索增强生成（RAG） | `skills/retrieval_augmented_generation/` | Embeddings、向量检索、上下文注入 | 基于私有文档问答的基础 RAG 实现，从文档切分到答案生成完整流程 |
| 文本摘要 | `skills/summarization/` | Map-Reduce、分块摘要、自定义风格 | 长文档/文章/书籍的摘要生成，支持不同长度和风格的摘要 |
| Text-to-SQL | `skills/text_to_sql/` | Schema 注入、SQL 生成、错误自修正 | 自然语言转 SQL 查询，支持多表 JOIN、聚合查询等复杂场景 |
| 知识图谱 | `skills/knowledge_graph/` | 实体关系抽取、图谱构建、图查询 | 从非结构化文本中抽取实体和关系，构建知识图谱并基于图谱问答 |
| 上下文嵌入 | `skills/contextual-embeddings/` | Anthropic Embeddings、上下文增强检索 | 用 Claude 为每个 chunk 生成上下文说明，大幅提升 RAG 检索准确率 |
| 内容审核 | `skills/content_moderation/` | 安全分类器、多层审核、自定义规则 | 输入输出内容审核，检测有害、违规、不当内容并标记分类 |

---

## 二、工具使用与集成（Tool Use and Integration）

这类 Cookbook 展示 Function Calling（工具调用）的各种实践模式。

| 名称 | 源路径 | 核心技术 | 一句话说明 |
|------|--------|---------|-----------|
| 客服 Agent | `tool_use/customer_service_agent/` | 多轮工具调用、缺失参数追问、状态管理 | 完整的电商客服 Agent 实现：查订单、退款、转人工多轮对话 |
| 计算器工具 | `tool_use/calculator_tool/` | 确定性函数、安全表达式求值、精确计算 | 为 Claude 添加精确数学计算能力，解决大模型计算不准的问题 |
| SQL 查询工具 | `tool_use/sql_queries/` | Text-to-SQL + 执行工具、错误处理、结果格式化 | 自然语言提问 → 生成 SQL → 执行查询 → 自然语言回答的完整闭环 |

---

## 三、多模态能力（Multimodal Capabilities）

这类 Cookbook 展示 Claude Vision（视觉）能力的各种应用。

| 名称 | 源路径 | 核心技术 | 一句话说明 |
|------|--------|---------|-----------|
| Vision 入门 | `multimodal/vision_getting_started/` | 图片输入（base64/URL）、基础图片理解 | Vision 能力快速上手：图片编码、发送请求、解析响应的基础流程 |
| Vision 最佳实践 | `multimodal/vision_best_practices/` | 图片预处理、分辨率优化、提示词技巧 | Vision 使用的经验总结：图片大小、格式、裁剪、提示词写法等最佳实践 |
| 图表与 PPT 解读 | `multimodal/reading_charts_graphs/` | 图表理解、数据提取、洞察生成 | 看懂柱状图、折线图、饼图等数据可视化，提取数据点和洞察 |
| 表单与文字提取（OCR）| `multimodal/ocr_text_extraction/` | 文字识别、结构化提取、JSON 输出 | 从图片中提取印刷/手写文字、表单字段、票据信息，支持结构化 JSON |
| PDF 上传与解析 | `multimodal/pdf_with_vision/` | PDF 转图片、逐页理解、长文档处理 | PDF 文档的视觉理解：逐页转图片后用 Vision 分析，支持扫描版 PDF |
| 图片生成（Stable Diffusion）| `multimodal/image_generation/` | 提示词生成、SD API 集成、多轮优化 | 用 Claude 生成高质量 Stable Diffusion 提示词，调用 SD API 生成图片 |
| 前端美学提示 | `multimodal/frontend_aesthetics/` | UI 截图分析、设计建议、CSS 生成 | 分析 UI 截图给出美学改进建议，甚至生成改进后的 CSS |

---

## 四、高级技巧（Advanced Techniques）

这类 Cookbook 展示提升系统效果、降低成本、处理复杂任务的进阶技术。

| 名称 | 源路径 | 核心技术 | 一句话说明 |
|------|--------|---------|-----------|
| Sub-agents 子 Agent | `advanced_techniques/sub_agents/` | 多模型协作、路由分发、Haiku+Opus 配合 | 主 Agent 路由 + 子 Agent 执行的架构，Haiku 做路由/Opus 做推理，降本增效 |
| PDF 处理（高级） | `advanced_techniques/pdf/` | PDF 解析、混合处理（文字层+视觉）、RAG 集成 | 生产级 PDF 处理方案：优先提取文字层，扫描页用 Vision，结合 RAG 问答 |
| 自动化评估（Evals）| `advanced_techniques/evals/` | LLM-as-Judge、测试集、质量指标 | 用 Claude 评估 Claude 的自动化测试框架，评估回答质量防止回归 |
| JSON 模式 | `advanced_techniques/json_mode/` | response_format、JSON Schema、结构化输出 | 强制 Claude 返回有效 JSON，用于数据提取、分类、函数参数生成 |
| 内容审核过滤 | `advanced_techniques/content_moderation/` | 多层审核、敏感词检测、安全策略 | 生产级输入输出内容审核管线，多层级安全检测 |
| Prompt Caching | `advanced_techniques/prompt_caching/` | 缓存断点标记、前缀缓存、成本监控 | 利用提示缓存降低最多 90% 成本，加快响应速度 |
| 成本优化 | `advanced_techniques/cost_optimization/` | 模型选择、提示词优化、缓存策略综合 | 全方位成本优化指南：模型路由、max_tokens、缓存、批量请求等 |
| Extended Thinking | `advanced_techniques/extended_thinking/` | 思考预算配置、推理过程可见、复杂任务 | 开启扩展思考提升复杂推理任务准确率，数学/逻辑/代码场景效果显著 |
| Fine-tuning（Bedrock）| `advanced_techniques/fine_tuning/` | AWS Bedrock、训练数据准备、微调流程 | 在 AWS Bedrock 上微调 Claude 模型的完整流程（注意：大多数场景不需要微调） |
| 流式处理进阶 | `advanced_techniques/streaming/` | SSE 流式、增量输出、思考过程流式 | 流式响应的高级用法，包括工具调用流式、思考过程流式输出 |

---

## 五、Claude Agent SDK 示例

这类 Cookbook 展示基于 Claude Agent SDK 构建的企业级专用 Agent，以及部署方案。

| 名称 | 源路径 | 核心技术 | 一句话说明 |
|------|--------|---------|-----------|
| 幕僚长 Agent（Chief of Staff）| `agent_sdk/chief_of_staff_agent/` | 任务编排、日程管理、多 Agent 协作 | 类似行政幕僚的综合助手 Agent：日程安排、邮件处理、任务优先级排序 |
| 可观测性 Agent（Observability）| `agent_sdk/observability_agent/` | 日志分析、指标监控、异常检测 | 运维可观测性 Agent：分析日志、检测异常、定位问题根因 |
| SRE Agent（站点可靠性）| `agent_sdk/site_reliability_agent/` | 故障排查、Runbook 执行、自动化修复 | 站点可靠性工程 Agent：自动响应告警、执行排查步骤、甚至自动修复 |
| 漏洞检测 Agent | `agent_sdk/vulnerability_detection_agent/` | 代码扫描、漏洞分析、安全建议 | 安全 Agent：扫描代码库检测安全漏洞，给出修复建议和优先级 |
| 研究 Agent（Research）| `agent_sdk/research_agent/` | 深度搜索、多源信息整合、报告生成 | 深度研究 Agent：自动搜索多源信息、交叉验证、生成完整研究报告 |
| Agent 部署方案（Hosting）| `agent_sdk/hosting/` | Docker、Kubernetes、Modal 部署 | Agent 服务化部署方案：容器化、K8s 编排、Serverless（Modal）部署指南 |

---

## 六、第三方集成（Third-Party Integrations）

这类 Cookbook 展示 Claude 与流行第三方服务的集成方案。

| 名称 | 源路径 | 核心技术 | 一句话说明 |
|------|--------|---------|-----------|
| Pinecone 向量数据库 RAG | `third_party/pinecone/` | Pinecone Vector DB、向量检索、RAG 集成 | 与 Pinecone 托管向量数据库集成的生产级 RAG 方案 |
| Wikipedia 搜索集成 | `third_party/wikipedia/` | Wikipedia API、实时检索、知识增强 | 让 Claude 搜索 Wikipedia 获取最新百科知识作为回答依据 |
| Voyage AI Embeddings | `third_party/voyage_ai/` | Voyage 嵌入模型、高质量向量、检索优化 | 使用 Voyage AI 的嵌入模型替代默认嵌入，提升 RAG 检索质量 |
| Web 页面读取 | `third_party/web_fetching/` | 网页抓取、BeautifulSoup/Trafilatura、内容提取 | 读取并解析网页内容，让 Claude 能基于最新网页信息回答问题 |
| Chroma 本地向量库 | `third_party/chroma/` | Chroma DB、本地向量存储、轻量 RAG | 使用开源 Chroma 向量数据库的本地 RAG 方案，适合开发和小规模场景 |
| LangChain 集成 | `third_party/langchain/` | LangChain 框架、Chain、Agent 编排 | Claude 与 LangChain 框架的集成示例，使用 LangChain 的工具和链 |
| LlamaIndex 集成 | `third_party/llamaindex/` | LlamaIndex、数据连接、索引框架 | Claude 与 LlamaIndex 数据框架集成，构建 RAG 应用 |

---

## 按难度等级索引

### ⭐ 入门级（无需外部依赖，5 分钟跑通）

- `skills/classification/` — 文本分类
- `skills/summarization/` — 文本摘要
- `multimodal/vision_getting_started/` — Vision 入门
- `advanced_techniques/json_mode/` — JSON 模式
- `tool_use/calculator_tool/` — 计算器工具

### ⭐⭐ 进阶级（需要少量依赖，理解核心概念）

- `skills/retrieval_augmented_generation/` — 基础 RAG
- `skills/text_to_sql/` — Text-to-SQL
- `tool_use/customer_service_agent/` — 客服 Agent
- `tool_use/sql_queries/` — SQL 查询工具
- `multimodal/ocr_text_extraction/` — OCR 文字提取
- `multimodal/reading_charts_graphs/` — 图表解读
- `advanced_techniques/prompt_caching/` — 提示缓存
- `advanced_techniques/extended_thinking/` — 扩展思考
- `third_party/wikipedia/` — Wikipedia 集成

### ⭐⭐⭐ 高级（需要外部服务或完整系统设计）

- `skills/contextual-embeddings/` — 上下文嵌入
- `skills/knowledge_graph/` — 知识图谱
- `skills/content_moderation/` — 内容审核
- `multimodal/pdf_with_vision/` — PDF 处理
- `multimodal/image_generation/` — 图片生成
- `advanced_techniques/sub_agents/` — 子 Agent
- `advanced_techniques/evals/` — 自动化评估
- `advanced_techniques/cost_optimization/` — 成本优化
- `third_party/pinecone/` — Pinecone 集成
- `third_party/voyage_ai/` — Voyage 嵌入
- `third_party/web_fetching/` — Web 读取

### ⭐⭐⭐⭐ 专家级（企业级/生产级方案）

- `advanced_techniques/pdf/` — 高级 PDF 处理
- `advanced_techniques/fine_tuning/` — 微调
- `agent_sdk/chief_of_staff_agent/` — 幕僚长 Agent
- `agent_sdk/site_reliability_agent/` — SRE Agent
- `agent_sdk/research_agent/` — 研究 Agent
- `agent_sdk/vulnerability_detection_agent/` — 漏洞检测 Agent
- `agent_sdk/hosting/` — 生产部署

---

## 相关概念

- [Cookbook 导览](/cookbooks/concepts/00-overview.md) — 如何选择适合你的 Cookbook
- [工具调用模式](/cookbooks/concepts/01-tool-use-patterns.md) — Tool Use 分类下所有 recipe 的模式总结
- [多模态模式](/cookbooks/concepts/02-multimodal-patterns.md) — Multimodal 分类下 recipe 的模式总结
- [RAG 与知识检索模式](/cookbooks/concepts/03-rag-patterns.md) — RAG/Embeddings/向量数据库相关 recipe 的模式总结
- [高级技巧](/cookbooks/concepts/04-advanced-techniques.md) — Advanced Techniques 分类下所有 recipe 的模式总结
