---
type: Example
title: "快速开始：安装与首次对话"
description: "从零开始安装 JupyterLite AI 扩展并完成第一次 AI 对话"
tags: [jupyterlite-ai, quick-start, installation, getting-started]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-04-21T00:00:00+08:00" }
status: stable
stale_after: 2026-10-21
sources:
  - id: source
    resource: /references/source-code.md
    title: 源码结构与核心文件索引
---

# 快速开始：安装与首次对话

本教程将引导你完成 JupyterLite AI 扩展的安装、配置，并完成第一次 AI 对话。

## 1. 安装扩展

### 方式一：pip 安装（JupyterLab/Notebook 环境）

```bash
# 安装核心扩展
pip install jupyterlite-ai

# 验证安装
jupyter labextension list
# 应看到 @jupyterlite/ai 已启用
```

### 方式二：JupyterLite 部署（纯浏览器环境）

```bash
# 安装 JupyterLite 和 AI 扩展
pip install jupyterlite jupyterlite-ai

# 构建 JupyterLite 站点
jupyter lite build

# 启动本地服务器预览
jupyter lite serve
```

访问 `http://localhost:8000` 即可使用。

### 方式三：conda/mamba 安装

```bash
conda install -c conda-forge jupyterlite-ai
```

## 2. 启动 JupyterLab

安装完成后启动 JupyterLab：

```bash
jupyter lab
```

或启动 Notebook 7：

```bash
jupyter notebook
```

## 3. 打开 AI 聊天面板

1. JupyterLab 启动后，在左侧边栏找到 **AI Chat** 图标（机器人形状）
2. 点击图标打开聊天面板
3. 首次打开时，会提示你配置 AI 提供商

## 4. 配置第一个 AI 提供商

点击聊天面板顶部的**设置按钮**（齿轮图标），进入设置面板：

1. 在 **Provider** 下拉菜单中选择你有 API Key 的提供商：
   - **OpenAI**：需要 OpenAI API Key
   - **Anthropic**：需要 Anthropic API Key
   - **Google**：需要 Google AI API Key
   - **Mistral**：需要 Mistral API Key
   - **Generic OpenAI-Compatible**：使用兼容 OpenAI API 格式的服务（如本地模型、Ollama、vLLM 等）

2. 在 **API Key** 字段中输入你的密钥
3. 在 **Model** 字段中选择或输入模型名称（如 `gpt-4o`、`claude-3-5-sonnet-latest`）
4. 点击 **Save** 保存

> 💡 API Key 会安全存储在 Jupyter Secrets Manager 中，不会明文保存到配置文件。

## 5. 开始第一次对话

配置完成后，回到聊天面板：

1. 在底部输入框中输入：`你好，请介绍一下你自己`
2. 按 Enter 或点击发送按钮
3. AI 将开始流式回复

你可以尝试：

```
你好！请帮我写一个 Python 函数来计算斐波那契数列。
```

```
我现在的 Notebook 里有什么内容？请查看并总结。
```

## 6. 验证功能正常

如果一切正常，你应该看到：
- ✅ AI 回复正常流式显示
- ✅ 可以在 Notebook 中创建新单元格
- ✅ 设置面板中配置信息已保存

## 常见问题

**Q: 提示"Provider not configured"？**
→ 确保已在设置面板中选择了提供商并输入了有效的 API Key。

**Q: API Key 存储在哪里？**
→ 存储在 `jupyter-secrets-manager` 管理的安全存储中，以占位符 `[JUPYTER_SENTINEL_SECRET_REPLACEMENT]` 替代明文。

**Q: 可以在离线环境使用吗？**
→ 可以，但需要使用 Generic OpenAI-Compatible 配置指向本地模型服务（如 Ollama），且需要 JupyterLite 环境或本地部署的 JupyterLab。

**Q: 支持中文吗？**
→ 支持，AI 的回复语言取决于模型本身和你的提问语言。
