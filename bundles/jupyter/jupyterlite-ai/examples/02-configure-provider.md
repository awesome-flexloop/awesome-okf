---
type: Example
title: "配置 AI 模型提供商"
description: "详细指南：配置 OpenAI/Anthropic/Google/Mistral 及兼容 OpenAI 的第三方服务"
tags: [jupyterlite-ai, provider, configuration, api-key, settings]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
  - id: providers
    resource: /references/built-in-providers.md
    title: 内置 AI Provider 配置参考
---

# 配置 AI 模型提供商

JupyterLite AI 支持多家 AI 模型提供商，本指南详细说明每种提供商的配置方法。

## 支持的内置提供商

| 提供商 | 标识 | 默认模型 | 内置工具支持 | 获取 API Key |
|--------|------|----------|-------------|-------------|
| OpenAI | `openai` | `gpt-4o-mini` | web_search, web_fetch | https://platform.openai.com |
| Anthropic | `anthropic` | `claude-3-5-sonnet-latest` | web_search, web_fetch | https://console.anthropic.com |
| Google | `google` | `gemini-2.5-flash` | 无内置工具 | https://aistudio.google.com |
| Mistral | `mistral` | `mistral-large-latest` | 无内置工具 | https://console.mistral.ai |
| Generic (OpenAI兼容) | `none` | 需手动指定 | 无内置工具 | 取决于服务 |

## 配置方式

### 方式一：通过 GUI 设置面板（推荐）

1. 点击聊天面板顶部的**齿轮图标**打开设置
2. 选择 **Provider**（提供商）
3. 输入 **API Key**
4. 选择或输入 **Model**（模型名称）
5. 点击 **Save**

### 方式二：通过 JupyterLab 设置编辑

1. 菜单栏 → **Settings** → **Settings Editor**
2. 搜索 **AI Chat** 或 **JupyterLite AI**
3. 配置以下字段：

```json
{
  "provider": "openai",
  "model": "gpt-4o",
  "apiKey": "sk-..."
}
```

### 方式三：Generic OpenAI-Compatible（通用兼容模式）

适用于 Ollama、vLLM、LM Studio、Azure OpenAI、本地模型等任何兼容 OpenAI API 格式的服务：

1. Provider 选择 **Generic OpenAI-Compatible**
2. 填写 **Base URL**：API 端点地址
3. 填写 **API Key**（如服务需要）
4. 填写 **Model**：模型名称

#### Ollama 本地模型配置示例

| 字段 | 值 |
|------|-----|
| Provider | Generic OpenAI-Compatible |
| Base URL | `http://localhost:11434/v1` |
| API Key | `ollama`（任意非空字符串） |
| Model | `llama3` |

确保 Ollama 已启动并允许跨域请求：

```bash
# 启动 Ollama
ollama serve

# 设置跨域环境变量（Linux/Mac）
OLLAMA_ORIGINS=* ollama serve
```

#### Azure OpenAI 配置示例

| 字段 | 值 |
|------|-----|
| Provider | Generic OpenAI-Compatible |
| Base URL | `https://YOUR_RESOURCE.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT` |
| API Key | 你的 Azure API Key |
| Model | 部署名称（如 `gpt-4o`） |

## 提供商能力详解

### 内置 Web 工具支持

OpenAI 和 Anthropic 提供商内置了 `web_search` 和 `web_fetch` 工具，AI 可以自主决定是否使用：

- **web_search**：搜索网络获取最新信息
- **web_fetch**：获取指定 URL 的网页内容

Google 和 Mistral 提供商不挂载内置 web 工具，但可以使用 Jupyter 相关工具（执行命令、浏览器获取、Notebook 操作等）。

### 模型选择建议

| 使用场景 | 推荐模型 | 提供商 |
|----------|---------|--------|
| 快速测试/低成本 | `gpt-4o-mini` | OpenAI |
| 平衡性能与成本 | `claude-3-5-sonnet-latest` | Anthropic |
| 代码生成 | `gpt-4o` / `claude-3-5-sonnet-latest` | OpenAI/Anthropic |
| 免费额度 | `gemini-2.5-flash` | Google |
| 本地部署 | `llama3` (via Ollama) | Generic |

## 切换提供商

你可以随时在设置中切换提供商：

1. 打开设置面板
2. 选择新的 Provider
3. 更新 API Key 和 Model
4. 点击 Save

切换后，当前对话上下文会保留，但后续消息将使用新配置的模型。

## 配置多提供商（高级）

当前版本一次只能激活一个提供商。如需在多个提供商间切换，可：
- 使用设置面板快速切换
- 通过 JupyterLab 命令面板搜索 "AI Settings"

## 故障排查

**问题：API 调用失败，返回 401**
→ 检查 API Key 是否正确、是否过期、是否有足够配额。

**问题：Generic 模式下连接失败**
→ 检查 Base URL 是否正确、服务是否启动、是否存在 CORS 问题（浏览器控制台查看 Network 错误）。

**问题：模型名称无效**
→ 不同提供商的模型名称格式不同，请参照提供商文档确认准确名称。
