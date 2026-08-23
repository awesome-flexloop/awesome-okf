---
type: Example
title: "JupyterLite 部署配置"
description: "在纯浏览器环境（JupyterLite）中部署和配置 AI 扩展"
tags: [jupyterlite-ai, jupyterlite, deployment, wasm, browser]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
---

# JupyterLite 部署配置

JupyterLite AI 最独特的特性是支持纯浏览器环境运行——无需后端服务器，AI 推理和 Notebook 执行都在浏览器中通过 WebAssembly 完成。本指南介绍 JupyterLite 环境的部署与配置。

## JupyterLite vs JupyterLab

| 特性 | JupyterLab | JupyterLite |
|------|-----------|-------------|
| 执行环境 | Python 内核（服务器端） | Pyodide（浏览器 WASM） |
| 需要服务器 | ✅ 是 | ❌ 静态文件即可 |
| AI 推理 | API 调用（服务端或客户端） | API 调用（客户端直接调用） |
| 文件系统 | 服务器文件系统 | 浏览器 IndexedDB |
| MCP 服务器 | stdio/HTTP 均支持 | 仅 HTTP/SSE |
| 部署复杂度 | 需要 Python 环境 | 静态托管（GitHub Pages 等） |

## 快速部署

### 1. 安装依赖

```bash
pip install jupyterlite jupyterlite-ai
```

### 2. 构建静态站点

```bash
jupyter lite build
```

构建产物位于 `_output/` 目录。

### 3. 本地预览

```bash
jupyter lite serve
```

访问 `http://localhost:8000`。

### 4. 部署到静态托管

**GitHub Pages**：
```bash
# 将 _output 目录推送到 gh-pages 分支
git subtree push --prefix _output origin gh-pages
```

**任意静态文件服务器**（Nginx、Apache、Vercel、Netlify 等）：
直接将 `_output/` 目录作为静态文件托管。

## 预配置 AI 设置

部署时可以预设 AI 配置，让用户开箱即用。

### 配置默认提供商和模型

在构建前创建覆盖配置：

```python
# jupyter_lite_config.json（或 jupyter_lite_config.py）
c = get_config()

# AI 扩展设置
c.AISettings.provider = "openai"
c.AISettings.model = "gpt-4o-mini"
```

或在 `overrides.json` 中设置：

```json
{
  "@jupyterlite/ai:plugin": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  }
}
```

> ⚠️ 注意：API Key 不应硬编码在配置中，应由用户在浏览器中输入（存储在本地 IndexedDB）。

### 配置 MCP 服务器

在 JupyterLite 环境中，MCP 服务器必须使用 HTTP/SSE 模式：

```json
{
  "@jupyterlite/ai:plugin": {
    "mcpServers": {
      "my-tools": {
        "url": "https://my-mcp-server.example.com/sse"
      }
    }
  }
}
```

## 浏览器环境注意事项

### 1. CORS 限制

浏览器环境中，API 调用受同源策略限制：
- AI 提供商 API（OpenAI、Anthropic 等）通常已配置 CORS 头，可直接调用
- 自托管模型服务（如 Ollama）需配置 CORS：`OLLAMA_ORIGINS=*`
- MCP 服务器需配置 CORS 允许你的 JupyterLite 域名

### 2. API Key 安全

- API Key 存储在浏览器的 IndexedDB 中
- 仅在用户浏览器本地存储，不上传到任何服务器
- 用户清除浏览器数据会导致配置丢失
- 建议提醒用户妥善保管自己的 API Key

### 3. 网络限制

JupyterLite 环境中：
- 可以直接访问配置了 CORS 的外部 API
- `browser_fetch` 工具受 CORS 限制
- 无法启动本地进程（stdio MCP 不可用）

### 4. 内核限制

JupyterLite 使用 Pyodide（WASM 编译的 Python）：
- 不是所有 Python 包都可用
- 纯 Python 包支持较好
- 含 C 扩展的包需要 Pyodide 版本支持
- 文件操作是虚拟的（IndexedDB 后端）

## 推荐配置

### 用于演示/教学

```json
{
  "@jupyterlite/ai:plugin": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "sendLogs": false
  }
}
```

- 使用低成本模型（gpt-4o-mini）
- 用户首次打开时输入自己的 API Key

### 用于开发测试

搭配本地 Ollama 使用：

1. 启动 Ollama：`OLLAMA_ORIGINS=* ollama serve`
2. 拉取模型：`ollama pull llama3`
3. JupyterLite AI 设置中：
   - Provider: Generic OpenAI-Compatible
   - Base URL: `http://localhost:11434/v1`
   - API Key: `ollama`
   - Model: `llama3`

## 离线使用

JupyterLite 本身支持离线使用（静态文件），但 AI 功能需要访问模型 API。要完全离线使用：
1. 部署本地模型服务（Ollama、LM Studio、vLLM）
2. 配置 CORS 允许 JupyterLite 域名
3. 使用 Generic OpenAI-Compatible 连接本地服务
