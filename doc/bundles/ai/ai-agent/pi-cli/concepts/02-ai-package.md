---
type: Concept
title: "AI 包（packages/ai）"
description: "@earendil-works/pi-ai 是统一多提供商 LLM API，核心为 Provider/Models 抽象、createModels/createProvider 工厂、OAuth 认证、10 种 API 类型、40 个 provider，以及成本计算和图片生成。"
tags: [pi-cli, ai, llm, provider, models, oauth, sdk]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-verification", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: 源码信源
---

# AI 包（packages/ai）

`@earendil-works/pi-ai` 是 Pi 的统一多提供商 LLM API 层。它将不同厂商的聊天补全、响应 API、流式传输差异抽象为一致的 `Provider`/`Models` 接口，支持 OpenAI、Anthropic、Google、Bedrock、DeepSeek、xAI、Groq、Mistral、Moonshot、Kimi、小米等 40 个已知 provider。

## 入口设计：无副作用核心

`src/index.ts` 是核心无副作用入口，刻意**不导出** provider factories、OAuth 实现或全局 API 注册表：

```ts
// Core only, side-effect free: no generated catalogs, no provider factories,
// no api-registry, no OAuth implementations, no compat. Provider factories
// live under "@earendil-works/pi-ai/providers/*", API implementations under
// "@earendil-works/pi-ai/api/*", the old global API under
// "@earendil-works/pi-ai/compat".
export type { Static, TSchema } from "typebox";
export { Type } from "typebox";
export * from "./auth/context.ts";
export * from "./auth/credential-store.ts";
export * from "./models.ts";
export * from "./models-store.ts";
export * from "./types.ts";
export * from "./utils/event-stream.ts";
export { contentText } from "./utils/text.ts";
export { uuidv7 } from "./utils/uuid.ts";
// ... 其余为类型和工具导出
```

新代码应使用 `createModels()` + provider factories 模式。

## models.ts：Provider 与 Models 抽象

`Provider<TApi>` 是运行时具体单元，拥有认证、模型列表和流式行为：

```ts
export interface Provider<TApi extends Api = Api> {
  readonly id: string;
  readonly name: string;
  readonly baseUrl?: string;
  readonly headers?: ProviderHeaders;
  readonly auth: ProviderAuth;

  getModels(): readonly Model<TApi>[];
  refreshModels?(context: RefreshModelsContext): Promise<void>;
  filterModels?(
    models: readonly Model<TApi>[],
    credential: Credential | undefined,
  ): readonly Model<TApi>[];

  stream<T extends TApi>(
    model: Model<T>,
    context: Context,
    options?: ApiStreamOptions<T>,
  ): AssistantMessageEventStream;
  streamSimple(
    model: Model<TApi>,
    context: Context,
    options?: SimpleStreamOptions,
  ): AssistantMessageEventStream;
  fetchDeferred?(...): AssistantMessageEventStream;
  cancelDeferred?(...): Promise<void>;
}
```

`Models` 是编排集合，负责解析认证、刷新动态模型目录、将请求委派给拥有该模型的 provider：

```ts
export interface Models {
  getProviders(): readonly Provider[];
  getProvider(id: string): Provider | undefined;
  getModels(provider?: string): readonly Model<Api>[];
  getModel(provider: string, id: string): Model<Api> | undefined;
  refresh(options?: ModelsRefreshOptions): Promise<ModelsRefreshResult>;
  checkAuth(providerId: string, options?: AuthOperationOptions): Promise<AuthCheck | undefined>;
  getAvailable(providerId?: string, options?: AuthOperationOptions): Promise<readonly Model<Api>[]>;
  getAuth(providerId: string, overrides?: AuthResolutionOverrides): Promise<AuthResult | undefined>;
  login(providerId: string, type: AuthType, interaction: AuthInteraction): Promise<Credential>;
  logout(providerId: string, options?: AuthOperationOptions): Promise<void>;
  stream<TApi extends Api>(...): AssistantMessageEventStream;
  complete<TApi extends Api>(...): Promise<AssistantMessage>;
  streamSimple(...): AssistantMessageEventStream;
  completeSimple(...): Promise<AssistantMessage>;
}
```

`MutableModels` 扩展 `Models`，增加 `setProvider()`、`deleteProvider()`、`clearProviders()`。

### 工厂函数

`createModels()` 返回 `MutableModels` 实例，默认使用内存凭证存储和内存模型存储：

```ts
export function createModels(options?: CreateModelsOptions): MutableModels {
  return new ModelsImpl(options);
}

export interface CreateModelsOptions {
  credentials?: CredentialStore;
  modelsStore?: ModelsStore;
  authContext?: AuthContext;
}
```

`createProvider()` 从部件构建 provider，支持静态基线模型列表与动态模型覆盖，以及单个 `api` 实现或按 `model.api` 分派的 map：

```ts
export function createProvider<TApi extends Api = Api>(
  input: CreateProviderOptions<TApi>,
): Provider<TApi>;

export interface CreateProviderOptions<TApi extends Api = Api> {
  id: string;
  name?: string;
  baseUrl?: string;
  headers?: ProviderHeaders;
  auth: ProviderAuth;
  models: readonly Model<TApi>[];
  fetchModels?: (context: RefreshModelsContext) => Promise<readonly Model<TApi>[]>;
  filterModels?: (... ) => readonly Model<TApi>[];
  api: ProviderStreams | Partial<Record<TApi, ProviderStreams>>;
}
```

动态 provider 的模型列表在首次 `refreshModels()` 前为空，`getModels()` 返回同步的"最后已知"快照。

## types.ts：核心类型定义

### 10 种已知 API 类型

```ts
export type KnownApi =
  | "openai-completions"
  | "mistral-conversations"
  | "openai-responses"
  | "azure-openai-responses"
  | "openai-codex-responses"
  | "anthropic-messages"
  | "bedrock-converse-stream"
  | "google-generative-ai"
  | "google-vertex"
  | "pi-messages";
```

### 40 个已知 Provider ID

包括 `amazon-bedrock`、`anthropic`、`google`、`openai`、`deepseek`、`github-copilot`、`xai`、`groq`、`openrouter`、`mistral`、`moonshotai`、`kimi-coding`、`qwen-token-plan`、`xiaomi` 等。

### Model 接口

```ts
export interface Model<TApi extends Api> {
  id: string;
  name: string;
  api: TApi;
  provider: ProviderId;
  baseUrl: string;
  reasoning: boolean;
  thinkingLevelMap?: ThinkingLevelMap;
  input: ("text" | "image")[];
  cost: ModelCost;
  contextWindow: number;
  maxTokens: number;
  samplingParams?: Record<string, unknown>;
  headers?: Record<string, string>;
  compat?: TApi extends "openai-completions" ? OpenAICompletionsCompat
    : TApi extends "openai-responses" | ... ? OpenAIResponsesCompat
    : TApi extends "anthropic-messages" ? AnthropicMessagesCompat
    : ...;
}
```

### 7 种停止原因

```ts
type StopReason = "pending" | "stop" | "length" | "toolUse" | "error" | "aborted" | "deferred";
```

### 成本计算

`calculateCost()` 根据模型费率和使用量计算成本，支持分层定价，Anthropic 1 小时缓存写入按基础输入费率 2 倍计费：

```ts
export function calculateCost<TApi extends Api>(
  model: Model<TApi>,
  usage: Usage,
): Usage["cost"] {
  const inputTokens = usage.input + usage.cacheRead + usage.cacheWrite;
  let rates: ModelCostRates = model.cost;
  for (const tier of model.cost.tiers ?? []) {
    if (inputTokens > tier.inputTokensAbove && tier.inputTokensAbove > matchedThreshold) {
      rates = tier;
    }
  }
  const longWrite = usage.cacheWrite1h ?? 0;
  const shortWrite = usage.cacheWrite - longWrite;
  usage.cost.cacheWrite =
    (rates.cacheWrite * shortWrite + rates.input * 2 * longWrite) / 1000000;
  // ...
}
```

### 思考级别

```ts
type ModelThinkingLevel = "off" | "minimal" | "low" | "medium" | "high" | "xhigh" | "max";

export function getSupportedThinkingLevels<TApi extends Api>(
  model: Model<TApi>,
): ModelThinkingLevel[];
export function clampThinkingLevel<TApi extends Api>(
  model: Model<TApi>,
  level: ModelThinkingLevel,
): ModelThinkingLevel;
```

## oauth.ts：类型仅导出入口

`src/oauth.ts` 是纯类型重新导出，不包含运行时 OAuth 实现：

```ts
export type {
  OAuthAuthInfo,
  OAuthCredentials,
  OAuthDeviceCodeInfo,
  OAuthLoginCallbacks,
  OAuthPrompt,
  OAuthSelectOption,
  OAuthSelectPrompt,
} from "./compat/extension-oauth-types.ts";
```

实际的 OAuth 流程实现在 `src/auth/oauth/` 目录下，按 provider 拆分（`anthropic.ts`、`openai-codex.ts`、`github-copilot.ts`、`kimi-coding.ts`、`xai.ts`、`device-code.ts`、`pkce.ts` 等）。

## cli.ts：pi-ai 命令行工具

`src/cli.ts` 是带 shebang 的可执行脚本，支持两个命令：

```bash
npx @earendil-works/pi-ai login [provider]   # OAuth 登录
npx @earendil-works/pi-ai list                # 列出可用 OAuth provider
```

凭证保存到当前工作目录的 `auth.json` 文件。登录流程通过 `provider.auth.oauth.login()` 执行，支持 `auth_url` 和 `device_code` 两种通知类型：

```ts
const credential = await provider.auth.oauth.login({
  signal: new AbortController().signal,
  prompt: (authPrompt) => answerPrompt(rl, authPrompt),
  notify: (event) => {
    switch (event.type) {
      case "auth_url":
        console.log(`\nOpen this URL in your browser:\n${event.url}`);
        break;
      case "device_code":
        console.log(`\nOpen this URL in your browser:\n${event.verificationUri}`);
        console.log(`Enter code: ${event.userCode}`);
        break;
      // ...
    }
  },
});
```

## compat.ts：正在消亡的全局 API 垫片

`src/compat.ts` 保留旧版全局 `stream()`/`complete()` API、api-registry、环境变量 API key 注入和图片生成，模块加载时自动注册 10 个内置 API 实现。文件头明确声明：

> This module is deleted with the coding-agent ModelManager migration.

新代码**不应**导入 compat，应使用 `createModels()` + provider factories。

## images.ts：图片生成

```ts
export async function generateImages<TApi extends ImagesApi>(
  model: ImagesModel<TApi>,
  context: ImagesContext,
  options?: ProviderImagesOptions,
): Promise<AssistantImages> {
  const provider = resolveImagesApiProvider(model.api);
  return provider.generateImages(model, context, options);
}
```

已知图片 API 类型为 `openrouter-images`，已知图片 provider 为 `openrouter`。

## hasApi 类型守卫

动态查询的模型类型为 `Model<Api>`，使用 `hasApi()` 进行类型收窄：

```ts
const model = models.getModel("anthropic", "claude-opus-4-7");
if (model && hasApi(model, "anthropic-messages")) {
  // model 类型为 Model<"anthropic-messages">，stream options 完整类型化
}
```

## 相关概念

- [Monorepo 架构](01-monorepo-architecture.md)
- [TUI 系统](03-tui-system.md)
- [基础使用示例](../examples/01-basic-usage.md)
