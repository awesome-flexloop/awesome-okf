---
title: 第十四章 自动化深度研究智能体
type: reference
bundle: /datawhale/hello-agents
chapter: 14
part: 第四部分：综合案例进阶
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter14/第十四章%20自动化深度研究智能体.md
---

# 第十四章 自动化深度研究智能体

## 章节概要

构建知识密集型应用——自动化深度研究助手，将1-2小时的研究工作压缩到5-10分钟，展示上下文工程工具（NoteTool）和多Agent协作在研究场景的应用。

## 三大核心能力
1. **问题剖析**：将开放主题拆解为可检索的查询语句
2. **多轮信息采集**：结合不同搜索API持续挖掘资料，去重整合
3. **反思与总结**：识别知识空白，决定是否继续检索，生成结构化总结

## 核心价值
- **节省时间**：1-2小时研究压缩到5-10分钟
- **提高质量**：系统化流程避免遗漏
- **可追溯**：记录所有搜索结果和来源
- **可扩展**：轻松添加新搜索引擎和数据源

## 技术架构
四层架构：
```
前端层（Vue3+TypeScript）：全屏模态UI、Markdown可视化
    ↓ SSE流式
后端层（FastAPI）：/research/stream API
    ↓
智能体层（HelloAgents）：3 Agent + 2工具
    ↓
外部服务层：搜索引擎 + LLM提供商
```

### Agent架构
- **TODO Planner**：研究规划，将主题分解为3个子任务
- **Task Summarizer**：总结每个子任务的搜索结果
- **Report Writer**：整合所有总结生成最终报告

### 核心工具
- **SearchTool**：多搜索引擎信息检索
- **NoteTool**：结构化笔记，持久化记录研究发现（第九章上下文工程工具）

### 研究流程
1. 用户输入研究主题
2. Planner分解为3个子任务
3. 逐个执行：搜索 → 总结 → 笔记记录
4. Report Writer整合所有笔记
5. SSE流式推送进度和结果

## 关键技术点
- **SSE（Server-Sent Events）**：实时推送研究进度和日志
- **信息去重整合**：多轮搜索结果的智能合并
- **知识空白识别**：反思机制决定是否需要继续检索
- **结构化报告生成**：带引用来源的Markdown报告

## 教学价值
- NoteTool在真实场景中的应用
- 多Agent协作处理知识密集型任务
- 流式输出提升用户体验
- 研究范式的工程化落地
