---
type: Reference
title: 配置系统参考
description: Jupyter AI 命令行参数、配置文件格式、Jupyternaut 设置与模型参数配置
tags: [configuration, cli, config-file, model-parameters, jupyternaut]
sources:
  - id: jupyternaut-docs
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/jupyternaut/index.md
    title: jupyternaut/index.md
  - id: magic-commands
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/magic_commands/index.md
    title: magic_commands/index.md
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 配置系统参考

本页提供 Jupyter AI 的完整配置参考，包括命令行参数、配置文件和 Jupyternaut 设置。

## 命令行配置（--AiExtension.*）

通过 `jupyter lab` 启动时的 `--AiExtension` 参数配置：

### 模型与 API Key

| 参数 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `--AiExtension.initial_language_model` | string | 默认语言模型 ID | `--AiExtension.initial_language_model=bedrock/anthropic.claude-3-5-haiku-20241022-v1:0` |
| `--AiExtension.default_api_keys` | dict | 默认 API Key 字典 | `--AiExtension.default_api_keys={'OPENAI_API_KEY': 'sk-abcd'}` |

### 提供者过滤

| 参数 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `--AiExtension.blocked_providers` | string（可重复） | 黑名单提供者 | `--AiExtension.blocked_providers=openai` |
| `--AiExtension.allowed_providers` | string（可重复） | 白名单提供者 | `--AiExtension.allowed_providers=openai` |

黑名单优先级高于白名单。可重复指定多个值：

```bash
jupyter lab --AiExtension.blocked_providers=openai --AiExtension.blocked_providers=ai21
```

### 聊天记忆

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `--AiExtension.default_max_chat_history` | int | 2 | 对话历史轮数（k=2 表示 4 条消息：2问2答） |

```bash
jupyter lab --AiExtension.default_max_chat_history=4
```

### 模型参数

| 参数 | 类型 | 说明 |
|---|---|---|
| `--AiExtension.model_parameters <model_id>='<json>'` | dict | 为指定模型设置参数，解包后传给 Provider 类 |

示例：

```bash
jupyter lab --AiExtension.model_parameters bedrock/anthropic.claude-3-5-haiku-20241022-v1:0='{"model_kwargs":{"maxTokens":200}}'

# 多模型参数
jupyter lab \
  --AiExtension.model_parameters bedrock/anthropic.claude-3-5-haiku-20241022-v1:0='{"model_kwargs":{"maxTokens":200}}' \
  --AiExtension.model_parameters openai/gpt-4.1='{"max_tokens":1024,"temperature":0.9}'
```

## 配置文件方式

模型参数可通过 JSON 配置文件设置，文件名为 `jupyter_jupyter_ai_config.json`：

```json
{
  "AiExtension": {
    "model_parameters": {
      "bedrock/anthropic.claude-3-5-haiku-20241022-v1:0": {
        "model_kwargs": {
          "maxTokens": 200
        }
      }
    }
  }
}
```

加载方式：
- `jupyter lab --config <config-file-path>`
- 放入 Jupyter 配置搜索路径（通过 `jupyter --paths` 查看 `config` 目录）

## Jupyternaut 设置（UI 配置）

### 模型选择

通过 Settings → Jupyternaut Settings 选择：
- 从预设列表选择模型
- 添加自定义模型（Custom models），自定义模型显示在模型选择器顶部
- 支持模型参数配置（+ Add Parameter）

### API Key 配置

每个 Provider 的 API Key 在 Jupyternaut Settings 中设置，Key 名称遵循 LiteLLM 文档。

### 支持的 Provider 类型

| Provider | 认证方式 | 备注 |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | 直接选择 openai/ 前缀 |
| OpenRouter | OpenRouter API Key | 支持 Deepseek/Qwen/Mistral 等，选择 openrouter/ 前缀 |
| Amazon Bedrock | boto3 凭证 | 支持跨区推理、自定义模型、精调模型 |
| Ollama | 本地服务（默认 127.0.0.1:11434） | 通过 `api_base` 参数配置远程地址 |
| vLLM | 自建 vLLM 服务 | 需要启动 vLLM API server |
| NVIDIA | `NVIDIA_API_KEY` | NGC 服务 |
| Hugging Face Hub | API Token | 文本生成图像需安装 pillow |

### Jupyternaut 可选功能

| Extra | 功能 | 无此 extra 时 |
|---|---|---|
| `persistence` | SQLite 持久化对话记忆（服务重启后保留） | 对话记忆仅在服务进程生命周期内保留 |
| `all` | 所有可选运行时功能 | — |

安装：
```bash
pip install 'jupyter-ai-jupyternaut[persistence]'
```

## Magic Commands 配置

### 默认模型

```python
%config AiMagics.initial_language_model = "anthropic:claude-v1.2"
```

全局配置（ipython_config.py）：
```python
c.AiMagics.initial_language_model = "anthropic:claude-v1.2"
```

### 上下文窗口

```python
%config AiMagics.max_history = 4
```

全局配置：
```python
c.AiMagics.max_history = 4
```

### 别名配置

```python
c.AiMagics.aliases = {
  "my_custom_alias": "my_provider:my_model"
}
```

## 相关概念

- [配置系统](../concepts/11-configuration-system.md)
- [Magic Commands](../concepts/10-magic-commands.md)
- [Magic Commands 使用示例](../examples/magic-commands-usage.md)
