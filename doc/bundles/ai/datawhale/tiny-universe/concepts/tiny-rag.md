---
title: TinyRAG 检索增强生成
type: concept
bundle: /datawhale/tiny-universe
related:
  - /datawhale/tiny-universe/concepts/white-box-philosophy
  - /datawhale/tiny-universe/concepts/tiny-agent
  - /datawhale/tiny-universe/concepts/tiny-llm
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# TinyRAG 检索增强生成

## 定位

TinyRAG 是 tiny-universe 主体部分的第五个模块，**抛弃高度封装的 RAG 框架，从零手搓一个检索增强生成（Retrieval-Augmented Generation）系统**。项目配有讲解视频与 GPU 镜像，是 tiny-universe 中关注度较高的模块之一。

## 解决的问题

LLM 存在固有缺陷：产生"幻觉"、依赖的信息可能过时、处理特定知识时效率不高、缺乏专业领域深度洞察、推理能力有限。RAG 通过在生成答案前先从文档库检索相关信息，引导生成过程，从而：

- 提升内容准确性与相关性
- 缓解幻觉问题
- 提高知识更新速度
- 增强内容生成的可追溯性

TinyRAG 进一步指出：其他 RAG 项目虽基于封装框架提供完整服务、易于使用，却隐藏了底层原理，难以自由魔改升级。TinyRAG 的目标是让学习者理解 RAG 的每一个环节。

## 核心技术点

### 文档检索流程

TinyRAG 手工实现从文档到答案的完整管道：

1. **文档加载与切分**：将原始文档切分为适合检索的片段
2. **向量化**：将文本片段编码为向量表示
3. **向量检索**：根据用户查询从向量库中召回相关片段
4. **提示词拼装**：将检索结果作为上下文拼入 prompt
5. **答案生成**：LLM 基于检索上下文生成答案

### 白盒实现

不使用 LangChain、LlamaIndex 等 RAG 框架，各环节代码独立可见，学习者可以：

- 替换不同的切分策略
- 更换嵌入模型
- 修改检索算法（如从向量检索改为混合检索）
- 自定义 prompt 模板

## 在项目中的位置

TinyRAG 位于"增强系统层"，上承模型基础（TinyTransformer、TinyLLM），下接智能体（TinyAgent）。TinyGraphRAG 是 TinyRAG 的进阶变体，将图结构引入检索过程。

项目 README 中配有 RAG 流程图（`./content/TinyRAG/images/RAG.png`）。

## 镜像与视频

- GPU 镜像：`https://www.codewithgpu.com/i/datawhalechina/tiny-universe/tiny-universe-tiny-rag`
- 讲解视频：腾讯会议录播（链接见 README）

## 延伸

- 图结构进阶：TinyGraphRAG（主体模块第 8 项）
- 工具调用延伸：[TinyAgent](/ai/datawhale/tiny-universe/concepts/tiny-agent)
- 方法论根源：[白盒构建理念](/ai/datawhale/tiny-universe/concepts/white-box-philosophy)
