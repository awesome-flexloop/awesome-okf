---
type: bundle
okf_version: "0.2"
scope: openwork
name: openwork
version: "0.1.0"
source: https://github.com/langchain-ai/openwork
description: openwork——LangChain 开发的桌面 AI 代理界面，基于 deepagentsjs 和 LangGraph，提供文件系统操作、shell 命令执行、子代理委派和 HITL 审批能力
---

# openwork

**openwork** 是 LangChain 团队开发的 Electron 桌面应用，为 [deepagentsjs](https://github.com/langchain-ai/deepagentsjs) 深度代理框架提供图形化交互界面。用户可通过聊天驱动 AI 代理在本地工作区执行编码、研究、文件编辑和 shell 命令，所有命令执行前需人工审批。

- **版本**：0.1.0
- **作者**：LangChain
- **许可证**：MIT
- **运行时**：Electron 43 + Node.js >= 18
- **核心依赖**：deepagents ^1.5.1、LangGraph ^1.0.15、React 19

## 核心特性

- **多模型支持**：Anthropic Claude（4.5/4.1 系列）、OpenAI GPT（5.x/o-series/4.x）、Google Gemini（3/2.5 系列），共 20+ 模型
- **文件系统操作**：ls、read_file、write_file、edit_file、glob、grep，带语法高亮的文件查看器
- **Shell 执行**：在工作区目录执行命令，2 分钟超时，输出限制 100KB，所有命令需 HITL 审批
- **任务规划**：内置 Todo 列表管理，支持子代理委派与并行任务
- **对话持久化**：每线程独立 SQLite 检查点，支持中断恢复和历史回溯
- **工作区监听**：递归文件监听，500ms 防抖，自动刷新文件树

## 快速开始

```bash
# 直接运行
npx openwork

# 全局安装
npm install -g openwork
openwork
```

## 文档导航

### 核心概念

- [总览](/ai/langchain-ai/openwork/concepts/overview) — openwork 是什么、解决什么问题、核心机制与架构

### 参考资料

- [信源登记](/ai/langchain-ai/openwork/references/source-registry) — 源码文件清单、版本与溯源映射

### 规格文档

- [事实清单](/ai/langchain-ai/openwork/spec/facts) — 从源码提取的 26 条可验证事实
- [深度洞察](/ai/langchain-ai/openwork/spec/insights) — 架构设计决策与安全模型分析

## 目录结构

```
openwork/
├── spec/
│   ├── facts.md           # 源码事实验证清单（26 条）
│   └── insights.md        # 设计决策与深度洞察
├── concepts/              # 核心概念（1 篇）
│   └── overview.md
├── references/            # 信源登记（1 篇）
│   └── source-registry.md
├── log.md                 # 更新历史
└── index.md               # 本文件
```
