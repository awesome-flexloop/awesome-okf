---
title: libs/code/README.md
type: reference
bundle: /datawhale/deepagents
source_path: libs/code/README.md
source_url: https://github.com/datawhalechina/deepagents/blob/main/libs/code/README.md
---

# libs/code/README.md 引用

Deep Agents Code（dcode）终端编码 Agent 的产品文档。

## 核心内容

- **定位**：预构建终端编码 Agent，类似 Claude Code 或 Cursor，由任何支持工具调用的 LLM 驱动
- **安装**：`curl -LsSf https://langch.in/dcode | bash`，支持 DEEPAGENTS_CODE_EXTRAS 选择额外提供商
- **功能特性**：交互式 TUI、会话恢复、Web 搜索、远程沙箱（LangSmith/AgentCore/Daytona/Modal/Runloop）、持久化记忆、自定义技能、Headless 模式、人在回路
- **安全模型**：默认信任运行目录，审批门控工具调用但项目工件在审批前已读取；不可信仓库应使用远程沙箱；详见 THREAT_MODEL.md
- **资源链接**：文档、Changelog、源码、SDK、LangChain Academy

## 相关概念

- [Code终端编码Agent](/datawhale/deepagents/concepts/code-module)
