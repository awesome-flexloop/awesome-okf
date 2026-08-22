---
type: Concept
title: 配置系统
description: Jupyter AI 的配置选项、Traitlets 配置方式、命令行参数、配置文件和各扩展的配置项
tags: [configuration, traitlets, config-file, command-line, settings, ai-extension]
sources:
  - id: config-overview
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/config/index.md
    title: config/index.md
  - id: ai-config
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/config/ai.md
    title: config/ai.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 配置系统

Jupyter AI 使用 Jupyter 标准的 Traitlets 配置系统。配置可以通过命令行参数、Jupyter 配置文件或 Notebook 中的 `%config` magic 命令设置。

## 配置方式

### 1. 命令行参数

启动 JupyterLab 时通过 `--AiExtension.<option>=<value>` 传递：

```bash
jupyter lab --AiExtension.default_max_chat_history=4
```

### 2. Jupyter 配置文件

编辑 Jupyter 配置文件（通常在 `~/.jupyter/jupyter_server_config.py` 或 `~/.jupyter/jupyter_notebook_config.py`）：

```python
c = get_config()

# Jupyter AI 配置
c.AiExtension.default_max_chat_history = 4
c.AiExtension.default_language_model = "openai:gpt-4"
```

### 3. Notebook 内 %config

在 Notebook 中临时设置（重启后失效）：

```python
%config AiExtension.default_max_chat_history = 4
```

### 4. 查看所有配置项

```bash
jupyter lab --show-config | grep -i ai
```

或在 Notebook 中：

```python
%config AiExtension
```

## 主要配置项

### AiExtension 配置

`AiExtension` 是 Jupyter AI 主扩展的配置类：

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `default_language_model` | str | `"openai:gpt-3.5-turbo"` | Jupyternaut 默认使用的语言模型（LiteLLM 格式） |
| `default_max_chat_history` | int | `2` | 默认保留的对话轮数（每轮=1问1答） |
| `model_providers` | dict | `{}` | 自定义模型提供商配置 |
| `api_keys` | dict | `{}` | API Key 配置（建议用环境变量代替） |
| `allowed_personas` | list | `[]` | 允许使用的 Persona ID 列表（空列表=全部允许） |
| `blocked_personas` | list | `[]` | 禁止使用的 Persona ID 列表 |
| `default_persona` | str | `None` | 默认选中的 Persona |

### AiMagics 配置（Magic Commands）

```python
c.AiMagics.default_language_model = "openai:gpt-4"
c.AiMagics.max_history = 2  # Magic 命令保留的对话轮数
```

### MCP 配置

MCP 服务器配置不通过 Traitlets，而是通过 JSON 文件配置，详见 [自定义 MCP 服务器](08-custom-mcp-servers.md)。

## API Key 配置

### 方式 1：环境变量（推荐）

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# AWS Bedrock
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

### 方式 2：配置文件

```python
c.AiExtension.api_keys = {
    "OPENAI_API_KEY": "sk-...",
    "ANTHROPIC_API_KEY": "sk-ant-...",
}
```

> ⚠️ **安全提示**：不要将 API Key 硬编码在 Notebook 或配置文件中提交到版本控制。优先使用环境变量。

## 模型提供商配置

### LiteLLM 提供商

Jupyternaut 通过 LiteLLM 支持 1000+ 模型。模型 ID 格式为 `<provider>:<model>`：

| Provider | 模型 ID 格式 | 环境变量 |
|---|---|---|
| OpenAI | `openai:gpt-4` | `OPENAI_API_KEY` |
| Anthropic | `anthropic:claude-sonnet-4` | `ANTHROPIC_API_KEY` |
| AWS Bedrock | `bedrock:anthropic.claude-sonnet` | `AWS_ACCESS_KEY_ID` 等 |
| Ollama（本地） | `ollama:llama3` | 无需 Key（本地运行） |
| vLLM（自托管） | `openai:<custom>` | 按部署配置 |
| OpenRouter | `openrouter/<model>` | `OPENROUTER_API_KEY` |

### 自定义模型提供商

可以通过 `model_providers` 配置添加自定义 LiteLLM 兼容的提供商：

```python
c.AiExtension.model_providers = {
    "my-custom-provider": {
        "api_base": "https://my-llm-server.example.com/v1",
        "api_key": "...",
    }
}
```

## 配置文件位置

| 文件 | 用途 |
|---|---|
| `~/.jupyter/jupyter_server_config.py` | Jupyter Server 全局配置 |
| `~/.jupyter/jupyter_notebook_config.py` | Jupyter Notebook 配置（兼容） |
| `.jupyter/mcp_settings.json` | 自定义 MCP 服务器配置 |
| 环境变量 | API Key 和敏感配置 |

## 相关概念

- [安装与配置](01-installation-and-setup.md)
- [自定义 MCP 服务器](08-custom-mcp-servers.md)
- [AI Persona 系统](05-ai-personas.md)
- [Magic Commands](10-magic-commands.md)
- [配置参考](../references/config-reference.md)
- [MCP 配置参考](../references/mcp-config-reference.md)
