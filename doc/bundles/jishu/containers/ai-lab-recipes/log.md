# 变更日志

## v1.0.0 - 2026-08-26

### 新增

- 初始 OKF Bundle 版本
- **concepts/**：4篇概念文档
  - 00-introduction.md：双容器架构概览（模型服务器+AI应用）
  - 01-model-servers.md：四种模型服务器选型对比
  - 02-nlp-recipes.md：NLP配方全览（Chatbot/RAG/Agent/Codegen等）
  - 03-deployment.md：三种部署方式详解（Quadlet/Bootc/Ansible）
- **examples/**：2篇实战示例
  - 01-chatbot.md：从零开始部署Chatbot聊天机器人
  - 02-rag.md：RAG检索增强生成应用部署（ChromaDB集成）
- **references/**：1篇信源文档
  - readme-source.md：项目官方README整理
- 根文件：index.md（Bundle入口）、log.md（本文件）

### 覆盖事实

- F-001 ~ F-020：完整覆盖 facts-ai-lab-recipes.md 中所有20条编号事实
- 基于项目 README.md 和 Chatbot/RAG 官方文档补充实践细节

### 生成信息

- 生成者：trae-ai
- 生成时间：2026-08-26
- 使用工作流：source-code-to-okf-wiki R→I→E→V→C 五阶段流程
- 事实基础：20条编号事实 + README + 官方应用文档
- 代码块语言：yaml/bash/python
