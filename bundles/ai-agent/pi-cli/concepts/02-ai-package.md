---
type: Concept
title: AI 包详解
description: @earendil-works/pi-ai 是统一多提供商 LLM API，包含模型管理、OAuth 认证、CLI 工具、兼容层、图片生成和完整类型系统。
tags: [pi-cli, ai, llm, provider, models, oauth, compat]
generated: 2026-08-23
verified: 2026-08-23
status: stable
stale_after: 2026-11-23
sources:
  - packages/ai/src/index.ts:1-47
  - packages/ai/src/models.ts:97-223
  - packages/ai/src/types.ts:17-850
  - packages/ai/src/cli.ts:1-119
  - packages/ai/src/oauth.ts:1-10
  - packages/ai/src/compat.ts:1-298
  - packages/ai/src/images.ts:1-21
---

# AI 包详解

`@earendil-works/pi-ai` 是 pi 项目的 LLM 统一抽象层。它定义了 provider/model 接口、认证机制、流式请求协议，并内置了10种 API 实现和40个已知提供商。

## 模块结构

### 核心入口 (`src/index.ts`)

核心入口是无副作用的，仅重新导出类型和纯函数。它不包含 provider factories、OAuth 实现或生成目录。子路径导出包括：
- `@earendil-works/pi-ai/providers/*`：provider 工厂
- `@earendil-works/pi-ai/api/*`：API 实现
- `@earendil-works/pi-ai/compat`：旧版全局 API 兼容层
- `@earendil-works/pi-ai/oauth`：OAuth 类型导出

### 模型管理 (`src/models.ts`)

模型系统由两个核心接口构成：

- **`Provider<TApi>`**：运行时具体单元，拥有 `id`、`name`、`auth`、`getModels()`、`refreshModels()`、`stream()`、`streamSimple()` 方法。
- **`Models`**：provider 集合的运行时编排器，提供认证解析、模型目录刷新、请求委派。

关键工厂函数：
- `createModels(options?)`：返回 `MutableModels` 实例，默认使用内存凭证存储和内存模型存储。
- `createProvider(input)`：从部件构建 provider，支持静态基线模型 + 动态覆盖模型，支持单 API 实现或按 `model.api` 分派的多 API map。

辅助函数：
- `calculateCost(model, usage)`：根据费率计算 token 成本，支持分层定价和 Anthropic 1小时缓存写入的2倍费率。
- `getSupportedThinkingLevels(model)` / `clampThinkingLevel(model, level)`：查询和约束模型支持的思考级别。
- `hasApi(model, api)`：运行时类型守卫，窄化 `Model<TApi>` 类型。
- `modelsAreEqual(a, b)`：按 id 和 provider 比较模型。

### 类型系统 (`src/types.ts`)

定义了完整的类型体系：

- **API 类型**（10种已知）：`anthropic-messages`、`openai-completions`、`openai-responses`、`openai-codex-responses`、`azure-openai-responses`、`google-generative-ai`、`google-vertex`、`mistral-conversations`、`bedrock-converse-stream`、`pi-messages`。
- **Provider ID**（40个已知）：包括 `anthropic`、`openai`、`google`、`amazon-bedrock`、`deepseek`、`xai`、`groq`、`openrouter`、`mistral`、`moonshotai`、`kimi-coding`、`qwen-token-plan`、`xiaomi` 等。
- **`Model<TApi>`**：模型元数据，包含 id、name、api、provider、baseUrl、reasoning、input 类型、cost 费率、contextWindow、maxTokens、samplingParams、compat 配置。
- **消息类型**：`UserMessage`、`AssistantMessage`、`ToolResultMessage`，content 可为 TextContent、ThinkingContent、ToolCall、ImageContent。
- **Compat 接口**：为 OpenAI Completions、OpenAI Responses、Anthropic Messages、Bedrock 分别定义了细粒度兼容选项（如 thinkingFormat、cacheControlFormat、supportsStrictMode 等）。

### CLI 工具 (`src/cli.ts`)

pi-ai 包附带一个简单的 CLI（`#!/usr/bin/env node`），支持：
- `npx @earendil-works/pi-ai list`：列出所有支持 OAuth 的 provider
- `npx @earendil-works/pi-ai login [provider]`：执行 OAuth 登录流程

凭证保存到当前工作目录的 `auth.json` 文件。CLI 仅筛选具有 `auth.oauth` 定义的 provider。

### OAuth (`src/oauth.ts`)

该文件是纯类型导出入口，重新导出7个 OAuth 相关类型：`OAuthAuthInfo`、`OAuthCredentials`、`OAuthDeviceCodeInfo`、`OAuthLoginCallbacks`、`OAuthPrompt`、`OAuthSelectOption`、`OAuthSelectPrompt`。具体 OAuth 实现位于 `src/auth/` 和 `src/providers/` 目录中。

### 兼容层 (`src/compat.ts`)

compat 模块是临时的旧版 API 垫片，保留：
- 全局 `stream()` / `complete()` / `streamSimple()` / `completeSimple()` 函数
- api-registry（`registerApiProvider()`、`getApiProvider()`、`unregisterApiProviders()`）
- 废弃的静态目录读取函数（`getModel`、`getModels`、`getProviders`）
- 环境变量 API key 自动注入（`withEnvApiKey()`）
- Faux provider 注册（用于测试）

模块加载时自动调用 `registerBuiltInApiProviders()` 注册全部10个内置 API。文件头注释明确声明该模块将在 coding-agent ModelManager 迁移完成后删除。

### 图片生成 (`src/images.ts`)

图片生成模块导出 `generateImages()` 函数。它首先导入 `providers/images/register-builtins.ts` 注册内置图片 provider，然后通过 `getImagesApiProvider()` 解析对应 API 的实现并调用 `generateImages()`。已知图片 API 类型为 `openrouter-images`，已知图片 provider 为 `openrouter`。

## 相关概念

- [项目简介](/concepts/00-introduction.md)
- [Monorepo 架构](/concepts/01-monorepo-architecture.md)
- [TUI 终端 UI 系统](/concepts/03-tui-system.md)
- [内置 Prompt 模板](/concepts/04-builtin-prompts.md)
