---
title: dcode 一键安装与启动
type: example
bundle: /datawhale/deepagents
sources:
  - https://github.com/datawhalechina/deepagents/blob/main/libs/code/README.md
---

# dcode 一键安装与启动

`dcode`（Deep Agents Code）是预构建的终端编码 Agent，一条命令即可安装启动。

## 安装

```bash
# 默认安装（包含 OpenAI、Anthropic、Gemini 提供商）
curl -LsSf https://langch.in/dcode | bash

# 带额外提供商
DEEPAGENTS_CODE_EXTRAS="nvidia,ollama" curl -LsSf https://langch.in/dcode | bash
```

## 启动

```bash
dcode
```

启动后进入交互式 TUI，可直接与 Agent 对话，Agent 可以读写文件、执行命令、搜索代码等。

## 常用模式

### Headless 模式（非交互）

```bash
dcode -x "Review this repository and summarize the highest-risk issues."
```

### 指定模型

```bash
dcode --model anthropic:claude-sonnet-4-5
```

### ACP 模式（编辑器集成）

```bash
dcode --acp
```

### 恢复会话

```bash
dcode -r <thread_id>
```

## 环境变量

- `ANTHROPIC_API_KEY`、`OPENAI_API_KEY`、`GOOGLE_API_KEY` 等：提供商 API 密钥
- `DEEPAGENTS_CODE_DEBUG`：启用调试日志
- `DEEPAGENTS_CODE_AUTO_UPDATE`：控制自动更新
- `DEEPAGENTS_CODE_EXTRAS`：安装时选择额外提供商

## 相关概念

- [Code终端编码Agent](/ai/datawhale/deepagents/concepts/code-module)
