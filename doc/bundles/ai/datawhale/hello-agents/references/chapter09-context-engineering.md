---
title: 第九章 上下文工程
type: reference
bundle: /datawhale/hello-agents
chapter: 9
part: 第三部分：高级知识扩展
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter9/第九章%20上下文工程.md
---

# 第九章 上下文工程

## 章节概要

本章系统讲解上下文工程（Context Engineering）——从提示工程演进而来的工程方法，关注如何在每次模型调用前策划和维护最优的token集合。

## 核心知识点

### 上下文工程 vs 提示工程
- **提示工程**：如何编写与组织LLM指令以获得更优结果（主要是系统提示）
- **上下文工程**：在推理阶段如何策划与维护"最优的信息集合"，包含系统指令、工具、MCP、外部数据、消息历史等所有进入上下文窗口的信息

### 上下文腐蚀（Context Rot）
- 随上下文窗口tokens增加，模型准确回忆信息的能力反而下降
- Transformer的n²级注意力关系被"拉薄"
- 训练数据中短序列更常见，长序列经验不足
- 位置编码插值牺牲部分精度
- **核心结论**：上下文是有限资源，边际收益递减

### 有效上下文"解剖学"
1. **系统提示**：
   - 避免过度硬编码（脆弱if-else）或过于空泛
   - 分区组织：background_information、instructions、工具指引、输出描述
   - 追求"最小必要信息集"

2. **工具**：
   - 职责单一、低重叠、语义清晰、错误鲁棒
   - 警惕"臃肿工具集"
   - 最小可行工具集（MVTS）

3. **示例（Few-shot）**：
   - 多样且典型的示例
   - 好示例胜过千言万语

### JIT上下文与智能体式搜索
- 从"推理前一次性检索"到"及时（Just-in-time）上下文"
- 维护轻量化引用（文件路径、URL等），运行时动态加载
- **渐进式披露**：每步交互产生新上下文指导下一步
- 元数据隐含语义（目录层级、命名、时间戳）
- 混合策略：前置高价值上下文 + 按需自主探索

### 长时程任务三手段

**1. 压缩整合（Compaction）**
- 接近上限时高保真总结，用摘要重启上下文
- 保留架构决策、未解决缺陷、实现细节
- 先优化召回，再优化精确度

**2. 结构化笔记（Structured Note-taking）**
- Agent将关键信息写入上下文外持久化存储
- 维护TODO、NOTES.md、结论/依赖/阻塞索引
- 跨数十次工具调用保持进度

**3. 子代理架构（Sub-agent Architectures）**
- 主代理：高层规划与综合
- 子代理：干净上下文窗口中深挖，仅回传1,000-2,000 tokens摘要
- 关注点分离，适合并行探索

**选型经验**：
- 压缩整合 → 长对话连续性
- 结构化笔记 → 里程碑迭代式任务
- 子代理 → 复杂研究并行探索

### ContextBuilder：GSSC流水线
- **Gather（获取）**：从多来源收集候选信息
- **Select（选择）**：基于"相关性+新近性"评分筛选
- **Structure（结构化）**：固定骨架模板
  - `[Role & Policies]` → `[Task]` → `[State]` → `[Evidence]` → `[Context]` → `[Output]`
- **Compress（压缩）**：token预算兜底

**设计原则**：统一入口、稳定形态、预算守护、最小规则

### 配套工具
- **NoteTool**：结构化笔记持久化
- **TerminalTool**：文件系统操作和即时上下文检索

## 相关概念
- [上下文工程](/ai/datawhale/hello-agents/concepts/context-engineering)
- [记忆系统](/ai/datawhale/hello-agents/concepts/memory-systems)
