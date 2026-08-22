---
type: concept
scope: awesome-deepseek-agent
name: overview
description: awesome-deepseek-agent 总览——DeepSeek 模型接入工具精选指南合集
---

# awesome-deepseek-agent 总览

## 什么是 awesome-deepseek-agent

**awesome-deepseek-agent** 是 DeepSeek 官方维护的精选资源列表（Awesome List），收录了将 DeepSeek 大语言模型（特别是 DeepSeek-V4-Pro 和 DeepSeek-V4-Flash）集成到主流 AI Agent 和编程助手工具的完整指南。

- **GitHub 仓库**：https://github.com/deepseek-ai/awesome-deepseek-agent
- **定位**：不是代码库或 SDK，而是一个文档型资源合集
- **内容**：每份指南包含安装、配置、首次运行的完整步骤
- **语言**：中英文双语指南
- **目标**：让用户几分钟内在喜爱的工具中用上 DeepSeek 模型

## 收录范围

该列表覆盖 4 大类共 22 个工具/平台：

1. **IDE 插件**（3 个）：直接集成在代码编辑器中的 AI 编程助手
2. **终端 CLI 工具**（12 个）：在命令行中运行的 AI 编程 Agent
3. **桌面/聊天客户端**（2 个）：图形界面的 AI 对话客户端
4. **AI Agent 框架与平台**（5 个）：可扩展的 Agent 框架和平台

## 适用模型

- **DeepSeek-V4-Pro**：高性能版本，适合复杂推理、深度思考任务
- **DeepSeek-V4-Flash**：快速版本，适合代码补全、日常对话等低延迟场景

## 前置条件

使用任何工具接入 DeepSeek 模型需要：

1. **API Key**：从 [DeepSeek 开放平台](https://platform.deepseek.com/) 获取
2. **API 端点**：使用 DeepSeek 的 OpenAI 兼容 API（`https://api.deepseek.com`）
3. **网络连接**：能够访问 DeepSeek API 服务

## 与其他 DeepSeek 项目的关系

awesome-deepseek-agent 是 DeepSeek 生态的**应用层**资源，帮助终端用户将 DeepSeek 模型接入日常工具。它本身不包含模型代码或推理代码，仅提供配置指南。

- 模型本身（DeepSeek-V3/V4/R1 等）发布在 DeepSeek 主仓库
- 推理和部署框架（如 vLLM 集成、SGLang 等）在各自独立的仓库
- awesome-deepseek-agent 专注于**第三方工具的接入文档**
