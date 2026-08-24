---
type: Concept
title: 安装与配置
description: Jupyter AI 的安装方式、Agent 安装、ACP 适配器配置和首次启动
tags: [installation, setup, pip, conda, agent, acp, getting-started]
sources:
  - id: getting-started
    resource: external/libs/jupyter/jupyter-ai/docs/source/getting-started.md
    title: getting-started.md
  - id: pyproject
    resource: external/libs/jupyter/jupyter-ai/pyproject.toml
    title: pyproject.toml
  - id: troubleshooting
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/troubleshooting.md
    title: troubleshooting.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 安装与配置

Jupyter AI 支持多种包管理器安装，默认不包含任何 AI Agent，需要按需安装至少一个 Agent 才能开始使用。

## 安装 Jupyter AI

### 使用 pip

```bash
pip install jupyter-ai
```

### 使用 uv（推荐）

```bash
uv pip install jupyter-ai
```

### 使用 conda/mamba/micromamba

```bash
conda install -c conda-forge jupyter-ai
# 或
mamba install -c conda-forge jupyter-ai
# 或
micromamba install -c conda-forge jupyter-ai
```

### 使用 pixi

```bash
pixi add jupyter-ai
```

## 安装 AI Agent

Jupyter AI **默认不内置任何 Agent**，必须单独安装至少一个。

### 安装 Agent CLI

按 Agent 官方文档安装对应 CLI：

| Agent | 安装参考 |
|---|---|
| Claude Code | https://docs.anthropic.com/en/docs/claude-code/quickstart |
| Codex CLI | https://developers.openai.com/codex/cli |
| GitHub Copilot CLI | https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli |
| Goose | https://block.github.io/goose/docs/getting-started/installation |
| Kilo CLI | https://kilo.ai/cli |
| Kiro CLI | https://kiro.dev/docs/cli/installation/ |
| Mistral Vibe | `pip install mistral-vibe` 或 `uv tool install mistral-vibe` |
| OpenCode | https://opencode.ai/docs/#install |

### 安装 ACP 适配器

部分 Agent 需要额外安装 ACP 适配器才能在 Jupyter AI 中使用：

| Agent | ACP 适配器安装 |
|---|---|
| Claude Code | `npm install -g @agentclientprotocol/claude-agent-acp` |
| Codex | `npm install -g @zed-industries/codex-acp` |
| Mistral Vibe | Python 包自带，无需额外适配器 |

> **Conda 环境提示**：如果使用 Conda 环境管理器，建议在环境内安装 ACP 适配器。npm 类适配器需要先安装 nodejs：
> ```bash
> conda install nodejs
> npm install -g <npm-package-name>
> ```

### 安装 Jupyternaut（内置 Persona）

Jupyternaut 是 Jupyter AI 提供的默认 AI Persona，通过 LiteLLM 支持 1000+ 模型：

```bash
pip install 'jupyter-ai[jupyternaut]'
# 或
pip install jupyter-ai-jupyternaut
```

带持久化记忆：
```bash
pip install 'jupyter-ai-jupyternaut[persistence]'
```

### 安装 Magic Commands（可选）

```bash
pip install jupyter-ai-magic-commands
```

## 启动 JupyterLab

安装完成后，正常启动 JupyterLab：

```bash
jupyter lab
```

Jupyter AI 会自动检测环境中可用的 Agent。

## Agent 认证

部分 Agent 需要先登录认证才能使用：[^troubleshooting]

| Agent | 登录命令 |
|---|---|
| Claude | `claude login` |
| Codex | `codex` |
| GitHub Copilot | `copilot login`（或设置 `COPILOT_GITHUB_TOKEN`/`GH_TOKEN`/`GITHUB_TOKEN`） |
| Goose | `goose configure` |
| Kilo | `kilo auth login` |
| Kiro | `kiro-cli login` |
| Mistral Vibe | `vibe --setup`（或设置 `MISTRAL_API_KEY`） |
| OpenCode | `opencode auth login` |

如果 Agent 不回复，通常是因为未登录。通过 Agent 的 CLI 登录后重启 JupyterLab。

## 首次使用

1. 启动 JupyterLab 后，点击启动页面（Launcher）中的 **Chat** 卡片，或点击左侧边栏的聊天图标
2. 点击 **+ New Chat** 创建新聊天，输入聊天名称
3. 通过输入工具栏中的 Persona 选择器选择 AI Persona
4. 输入提示并发送消息

## 安装可选功能

### Magic Commands

```bash
pip install jupyter-ai-magic-commands
```

在 Notebook 中加载：
```python
%load_ext jupyter_ai_magic_commands
```

### Jupyternaut 持久化记忆

```bash
pip install 'jupyter-ai-jupyternaut[persistence]'
```

启用后，对话历史通过 SQLite 持久化，服务重启后仍可恢复。

## 升级建议

Jupyter AI 发展迅速，建议频繁升级以获取最新功能。优先使用环境管理器而非直接 pip：

```bash
micromamba update -c conda-forge jupyter-ai
# 或
uv pip install -U jupyter-ai
```

> **注意**：`.chat` 文件不保证前向兼容。跨版本升级后，旧聊天文件可能无法正常工作。

## 相关概念

- [Jupyter AI 简介](00-introduction.md)
- [聊天界面](02-chat-interface.md)
- [AI Persona 系统](05-ai-personas.md)
- [配置系统](11-configuration-system.md)
- [首次聊天示例](../examples/first-chat.md)

[^troubleshooting]: troubleshooting.md
