---
type: Example
title: "编码 Agent 接入：Claude Code 与 OpenCode"
description: "把 Claude Code 与 OpenCode 指到 HF 路由的两套官方配置路径，含 hf-claude 扩展、模型槽位映射、subagent 模型与组织计费。"
tags: [Claude Code, OpenCode, 编码 Agent, hf-claude, 环境变量, 组织计费]
sources:
  - id: hf-ip-claude-code
    resource: https://huggingface.co/docs/inference-providers/integrations/claude-code
    title: "Claude Code 接入官方指南"
  - id: hf-ip-opencode
    resource: https://huggingface.co/docs/inference-providers/integrations/opencode
    title: "OpenCode 接入官方指南"
  - id: hf-announcement
    resource: https://huggingface.co/blog/openrouter
    title: "Hugging Face × OpenRouter 官方合作公告（2026-11-16）"
---

# 编码 Agent 接入：Claude Code 与 OpenCode

公告列出五份接入指南：Claude Code、Codex、OpenCode、Pi、Hermes Agent（F-019），并提供了一个可把整套配置复制成 prompt 交给 Agent 的交互式 setup Space。本页展开其中两份最常被用到的；其余三份结构相近，按同一模式回官方文档即可。

> 前置：Claude Code / OpenCode 已安装；HF token 带 `inference.serverless.write`（"Make calls to Inference Providers"）权限（F-010、F-020）。

## Claude Code · 路径 A：`hf-claude` 扩展（官方推荐）

```bash
export HF_TOKEN="hf_..."
hf extensions install hf-claude
hf claude
```

扩展会弹出交互式选择器让你挑模型、可选挑供应商，然后用正确的环境变量启动 Claude Code；额外参数可透传（`hf claude --help`）（F-020）。

组织计费两种方式：

```bash
hf claude --bill-to your-org-name
# 或
export HF_BILL_TO="your-org-name"
hf claude
```

## Claude Code · 路径 B：手动环境变量

官方指南原文（F-020）：

```bash
export ANTHROPIC_BASE_URL="https://router.huggingface.co"
export ANTHROPIC_AUTH_TOKEN="${HF_TOKEN}"
export ANTHROPIC_API_KEY="${HF_TOKEN}"
export ANTHROPIC_DEFAULT_FABLE_MODEL="zai-org/GLM-5.3"
export ANTHROPIC_DEFAULT_OPUS_MODEL="zai-org/GLM-5.3"
export ANTHROPIC_DEFAULT_SONNET_MODEL="zai-org/GLM-5.3"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="zai-org/GLM-5.3"
export CLAUDE_CODE_SUBAGENT_MODEL="zai-org/GLM-5.3"
claude
```

三个要点：

1. `ANTHROPIC_BASE_URL` **不带 `/v1`**（Claude Code 自己拼 `/v1/messages`）；
2. 五个 `ANTHROPIC_DEFAULT_*_MODEL` 对应 Claude Code 内部的模型槽位（从最强到最快），可以分别指定不同模型，例如官方举例 `zai-org/GLM-5.3` 给 Opus、`google/gemma-4-31B-it:deepinfra` 给 Sonnet、`deepseek-ai/DeepSeek-V4.1-Flash:novita` 给 Haiku；`CLAUDE_CODE_SUBAGENT_MODEL` 控制子代理；
3. 带 `:novita` 这类后缀是**确定性 pin**（官方称 deterministic routing），不带后缀则走默认路由并自动故障转移（F-014、F-017、F-020）。

手动模式下记到组织账单：

```bash
export ANTHROPIC_CUSTOM_HEADERS="X-HF-Bill-To: your-org-name"
claude
```

## OpenCode

官方指南称 OpenCode **原生支持** Hugging Face Inference Providers（F-021），配置走交互式登录：

```bash
opencode auth login          # 在 provider 列表里选 Hugging Face
# 提示输入 API key 时填 hf_...
```

进入 TUI 后用 `/models` 选模型，之后可随时切换。组织计费写进 `~/.config/opencode/opencode.json`（官方原文）：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "huggingface": {
      "options": {
        "headers": {
          "X-HF-Bill-To": "your-org-name"
        }
      }
    }
  }
}
```

官方还给了 GitHub Actions 场景的自动 PR 审查指南，可回 `integrations` 目录查阅。

## 接入时最容易错的四处

| 现象 | 先查什么 |
|---|---|
| 404 / 路径像 `/v1/v1/messages` | `ANTHROPIC_BASE_URL` 多写了 `/v1`（F-020） |
| 401 / 权限不足 | token 是否 fine-grained 且勾了 "Make calls to Inference Providers"（F-010） |
| 模型不存在或全部下线 | 用 `hf models ls --warm` 核对模型 id 与命名空间（F-018、C-04） |
| 组织额度没生效 | 是否显式传了 `--bill-to` / `HF_BILL_TO` / `X-HF-Bill-To`（F-011、F-029） |

## 迁移提醒

这两份配置本身不因路由切换改变（公告称 "Your code stays the same"）。但如果你此前在 Agent 里配过**供应商自己的 API key**，语言模型侧现在会失效（F-005）；请把配置统一改成 `HF_TOKEN`，并检查账单归属是否已从供应商迁到 HF / 组织。
