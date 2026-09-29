---
type: spec
scope: langchainjs
name: facts
version: "0.1.0"
source: https://github.com/langchain-ai/langchainjs
description: LangChain.js 源码事实验证清单——从 langchain-core 与 langchain agents 核心模块提取的可验证事实
---

# LangChain.js 事实清单

## 项目元信息

F-001: 仓库为 monorepo，使用 pnpm workspaces (v10.14.0) 与 Turborepo 管理。核心包 `@langchain/core` 位于 `libs/langchain-core/`，主包 `langchain` 位于 `libs/langchain/`。TypeScript target 为 ES2022，模块为 ESNext with bundler resolution，strict 模式启用。

F-002: 支持的运行环境包括 Node.js (20.x, 22.x, 24.x)、Cloudflare Workers、Vercel/Next.js (Browser/Serverless/Edge)、Supabase Edge Functions、Browser、Deno、Bun。

F-003: 代码规范要求：本地导入必须包含 `.js` 扩展名（ESM）；使用命名导出而非默认导出；Zod 同时支持 v3 和 v4（`import { z } from "zod/v3"` 或 `"zod/v4"`）。

## Runnable 核心抽象（langchain-core/src/runnables/）

F-004: 文件 `runnables/types.ts` 第23-63行，`RunnableInterface<RunInput, RunOutput, CallOptions>` 接口继承 `SerializableInterface`，声明五个核心方法：`invoke(input, options?): Promise<RunOutput>`、`batch(inputs, options?, batchOptions?)`（三个重载，支持 `returnExceptions`）、`stream(input, options?): Promise<IterableReadableStreamInterface<RunOutput>>`、`transform(generator, options): AsyncGenerator<RunOutput>`、`getName(suffix?): string`。

F-005: 文件 `runnables/types.ts` 第80-109行，`RunnableConfig<ConfigurableFieldType>` 接口继承 `BaseCallbackConfig`，包含字段：`configurable?`、`recursionLimit?`（默认25）、`maxConcurrency?`、`timeout?`（毫秒）、`signal?: AbortSignal`。

F-006: 文件 `runnables/base.ts` 第124-133行，抽象类 `Runnable<RunInput, RunOutput, CallOptions>` 继承 `Serializable` 并实现 `RunnableInterface`。受保护属性 `lc_runnable = true`，可选属性 `name?: string`。

F-007: 文件 `runnables/base.ts` 第145-148行，`Runnable` 声明抽象方法 `abstract invoke(input: RunInput, options?: Partial<CallOptions>): Promise<RunOutput>`，所有子类必须实现。

F-008: 文件 `runnables/base.ts` 第156-168行，`withRetry(fields?)` 方法返回 `RunnableRetry` 实例，接受 `stopAfterAttempt` 和 `onFailedAttempt` 参数。

F-009: 文件 `runnables/base.ts` 第175-184行，`withConfig(config)` 方法返回新的 `RunnableBinding` 实例，将配置绑定到 Runnable。

F-010: 文件 `runnables/base.ts` 第192-205行，`withFallbacks(fields)` 方法接受 `{ fallbacks: Runnable[] }` 或 `Runnable[]`，返回 `RunnableWithFallbacks` 实例。

F-011: 文件 `runnables/base.ts` 第615-623行，`pipe<NewRunOutput>(coerceable: RunnableLike<RunOutput, NewRunOutput>): Runnable<RunInput, Exclude<NewRunOutput, Error>>` 方法创建新的 `RunnableSequence`，将当前 Runnable 作为 `first`，coerceable 通过 `_coerceToRunnable` 转换后作为 `last`。

F-012: 文件 `runnables/base.ts` 第628-631行，`pick(keys: string | string[]): Runnable` 方法通过 `this.pipe(new RunnablePick(keys))` 实现。

F-013: 文件 `runnables/base.ts` 第636-646行，`assign(mapping)` 方法通过 `this.pipe(new RunnableAssign(new RunnableMap({ steps: mapping })))` 实现。

F-014: 文件 `runnables/base.ts` 第243-289行，`batch` 默认实现使用 `AsyncCaller` 控制并发，对每个 input 调用 `this.invoke`，支持 `returnExceptions` 选项将错误作为返回值而非抛出。

F-015: 文件 `runnables/base.ts` 第297-302行，`_streamIterator` 默认实现为 `async *` 生成器，直接 `yield this.invoke(input, options)`；子类应覆盖以支持真正的流式输出。

F-016: 文件 `runnables/base.ts` 第310-323行，`stream` 方法使用 `AsyncGeneratorWithSetup` 包装 `_streamIterator`，缓冲第一个 chunk 以允许初始错误立即浮现，返回 `IterableReadableStream`。

F-017: 文件 `runnables/base.ts` 第1302行，`RunnableBinding` 类导出，用于将配置和 kwargs 绑定到 Runnable。

F-018: 文件 `runnables/base.ts` 第1727行，`RunnableRetry` 类导出，使用 `pRetry` 库实现重试逻辑。

F-019: 文件 `runnables/base.ts` 第1925行，`RunnableSequence` 类导出，包含 `first`、`middle`、`last` 三个 Runnable 组件。第2186-2208行重写 `pipe` 方法，支持序列合并优化（当 coerceable 也是 RunnableSequence 时合并 middle 数组）。

F-020: 文件 `runnables/base.ts` 第2261行，`RunnableMap` 类导出，并行执行多个 Runnable 并将结果组装为对象。第2852行 `RunnableParallel` 是 `RunnableMap` 的别名子类。

F-021: 文件 `runnables/base.ts` 第2536行，`RunnableLambda` 类导出，将普通函数包装为 Runnable。

F-022: 文件 `runnables/base.ts` 第2922行，`RunnableWithFallbacks` 类导出，实现主 Runnable 失败时回退到备用 Runnable。

F-023: 文件 `runnables/config.ts` 第5行，`DEFAULT_RECURSION_LIMIT = 25`。

F-024: 文件 `runnables/config.ts` 第49-148行，`mergeConfigs(...configs)` 函数合并多个 RunnableConfig：metadata 浅合并、tags 去重合并、configurable 浅合并、timeout 取最小值、signal 使用 `AbortSignal.any` 合并、callbacks 支持数组/管理器的六种组合。

F-025: 文件 `runnables/config.ts` 第153-200行，`ensureConfig(config?)` 函数确保配置对象包含 `tags: []`、`metadata: {}`、`recursionLimit: 25`，从 `AsyncLocalStorageProviderSingleton` 继承隐式配置（但排除 runId/runName），当 `configurable.model` 为字符串时自动设置 `metadata.model`。

## Graph 数据结构（langchain-core/src/runnables/graph.ts）

F-026: 文件 `runnables/graph.ts` 第53-61行，`Graph` 类包含 `nodes: Record<string, Node>` 和 `edges: Edge[]`。

F-027: 文件 `runnables/graph.ts` 第94-112行，`addNode(data, id?, metadata?)` 方法：id 未提供时使用 `uuidv4()` 生成；若 id 已存在则抛出错误。返回 `Node` 对象。

F-028: 文件 `runnables/graph.ts` 第124-144行，`addEdge(source, target, data?, conditional?)` 方法：验证 source 和 target 节点存在后创建 Edge 对象。

F-029: 文件 `runnables/graph.ts` 第158-188行，`extend(graph, prefix?)` 方法将另一个 Graph 的所有节点和边合并进来，支持前缀重命名；若所有节点 id 都是 UUID 则不使用前缀。返回 `[firstNode, lastNode]` 元组。

F-030: 文件 `runnables/graph.ts` 第65-92行，`toJSON()` 方法将图序列化为 JSON 格式，UUID 节点 id 替换为数字索引以保证稳定性，节点数据区分为 `"runnable"` 类型（含 lc_id 和 name）和 `"schema"` 类型（含 JSON Schema）。

F-031: 文件 `runnables/types.ts` 第65-78行，`Edge` 接口包含 `source: string`、`target: string`、`data?: string`、`conditional?: boolean`。`Node` 接口包含 `id: string`、`name: string`、`data: RunnableIOSchema | RunnableInterface`、`metadata?`。

## Message 系统（langchain-core/src/messages/）

F-032: 文件 `messages/base.ts` 第52行，`MessageContent` 类型定义为 `string | Array<ContentBlock>`，支持纯文本或多模态内容块数组。

F-033: 文件 `messages/base.ts` 第69-88行，`BaseMessageFields` 接口包含 `content?`、`contentBlocks?`、`additional_kwargs?`（已废弃，含 `function_call` 和 `tool_calls`）、`response_metadata?`、`id?`、`name?`。

F-034: 文件 `messages/base.ts` 第110-162行，`mergeContent(firstContent, secondContent): MessageContent` 函数处理字符串与数组的合并：字符串+字符串直接拼接；字符串+数组转为 text block 后追加；数组+数组调用 `_mergeLists` 或展开合并。

F-035: 文件 `messages/human.ts` 第18-42行，`HumanMessage` 类继承 `BaseMessage`，`readonly type = "human"`。提供静态 `isInstance(obj)` 类型守卫和 `Symbol.hasInstance` 支持。对应的 Chunk 类为 `HumanMessageChunk`。

F-036: 文件 `messages/system.ts` 第18-77行，`SystemMessage` 类继承 `BaseMessage`，`readonly type = "system"`。`concat(chunk)` 方法支持字符串或 SystemMessage 参数，合并 content、additional_kwargs、response_metadata。

F-037: 文件 `messages/ai.ts` 第46-66行，`AIMessage` 类继承 `BaseMessage`，`readonly type = "ai"`。包含 `tool_calls?`（默认 `[]`）、`invalid_tool_calls?`（默认 `[]`）、`usage_metadata?` 字段。`lc_aliases` 覆盖确保 `tool_calls`、`invalid_tool_calls`、`usage_metadata` 在序列化时保持 snake_case。

F-038: 文件 `messages/ai.ts` 第81-113行，AIMessage 构造函数处理向后兼容：若 `additional_kwargs.tool_calls` 存在但 `tool_calls` 未设置，调用 `defaultToolCallParser` 解析并发出弃用警告。支持 `response_metadata.output_version === "v1"` 时将 content 转换为 contentBlocks。

F-039: 文件 `messages/tool.ts` 第53-118行，`ToolMessage` 类继承 `BaseMessage`，实现 `DirectToolOutput` 接口（`lc_direct_tool_output = true`）。`readonly type = "tool"`。必填字段 `tool_call_id: string`，可选 `status?: "success" | "error"`、`artifact?`、`metadata?`。构造函数支持 `(fields, tool_call_id, name?)` 三参数或单 fields 对象两种签名。

F-040: 文件 `messages/tool.ts` 第37-48行，`DirectToolOutput` 接口标记对象为 `readonly lc_direct_tool_output: true`，`isDirectToolOutput(x)` 类型守卫检查该标记。工具返回 DirectToolOutput 时不自动包装为 ToolMessage。

F-041: 文件 `messages/tool.ts` 第228-232行，`ToolCall<TName, TArgs>` 接口包含 `readonly type?: "tool_call"`、`id?`、`name: TName`、`args: TArgs`。

F-042: 文件 `messages/tool.ts` 第293-301行，`ToolCallChunk` 接口包含 `readonly type?: "tool_call_chunk"`、`id?: string`、`name?: string`、`args?: string`，用于流式传输中的增量工具调用。

F-043: 文件 `messages/tool.ts` 第13-28行，`ToolMessageFields` 接口包含 `artifact?`、`tool_call_id: string`、`status?: "success" | "error"`、`metadata?`。

## Tool 系统（langchain-core/src/tools/）

F-044: 文件 `tools/types.ts` 第30行，`ResponseFormat` 类型为 `"content" | "content_and_artifact" | string`。默认值为 `"content"`。

F-045: 文件 `tools/types.ts` 第86-118行，`ToolParams` 接口继承 `BaseLangChainParams`，包含 `responseFormat?`、`defaultConfig?`、`verboseParsingErrors?`（默认 false）、`metadata?`、`extras?`（provider 特定额外字段）。

F-046: 文件 `tools/types.ts` 第120-128行，`ToolRunnableConfig` 类型扩展 `RunnableConfig`，增加 `toolCall?: ToolCall` 和 `context?: ContextSchema`。

F-047: 文件 `tools/types.ts` 第81行，`ToolInputSchemaBase` 类型为 `InteropZodType | JSONSchema`，支持 Zod schema 或 JSON Schema。

F-048: 文件 `tools/index.ts` 第95-107行，抽象类 `StructuredTool<SchemaT, SchemaOutputT, SchemaInputT, ToolOutputT, ToolEventT>` 继承 `BaseLangChain` 并实现 `StructuredToolInterface`。抽象属性：`name: string`、`description: string`、`schema: SchemaT`。实例属性：`extras?`、`returnDirect = false`、`verboseParsingErrors = false`、`responseFormat? = "content"`、`defaultConfig?`。

F-049: 文件 `tools/index.ts` 第132-134行，`StructuredTool.lc_namespace` 返回 `["langchain", "tools"]`。

F-050: 文件 `tools/index.ts` 第163-167行，`StructuredTool` 声明抽象方法 `protected abstract _call(arg: SchemaOutputT, runManager?: CallbackManagerForToolRun, parentConfig?: ToolRunnableConfig): Promise<ToolOutputT> | AsyncGenerator<ToolEventT, ToolOutputT>`，支持同步返回或异步生成器（用于流式工具事件）。

F-051: 文件 `tools/index.ts` 第175-209行，`StructuredTool.invoke(input, config?)` 方法：若 input 是 ToolCall 则提取 `args` 并将 toolCall 注入 config；调用 `this.call(toolInput, enrichedConfig)`。返回类型由条件类型 `ToolReturnType<TInput, TConfig, TOutput>` 决定——ToolCall 输入返回 ToolMessage，普通输入返回原始输出。

F-052: 文件 `tools/index.ts` 第222-350行，`StructuredTool.call(arg, configArg?, tags?)` 方法（已废弃，推荐 invoke）：(1) 从 ToolCall 提取 args；(2) 使用 Zod `interopParseAsync` 或 `@cfworker/json-schema` 的 `validate` 校验输入，失败抛出 `ToolInputParsingException`；(3) 通过 CallbackManager 触发 `handleToolStart`；(4) 调用 `_call`，支持 AsyncGenerator 结果通过 `consumeAsyncGenerator` 消费并触发 `handleToolEvent`；(5) 根据 responseFormat 处理 content/artifact；(6) 调用 `_formatToolOutput` 将结果包装为 ToolMessage。

F-053: 文件 `tools/index.ts` 第356-407行，抽象类 `Tool<ToolOutputT, ToolEventT>` 继承 `StructuredTool<StringInputToolSchema, ...>`。`schema = z.object({ input: z.string().optional() }).transform((obj) => obj.input)`。重写 `call` 方法处理字符串输入自动包装为 `{ input: arg }`。

F-054: 文件 `tools/index.ts` 第412-461行，`DynamicTool` 类继承 `Tool`，包含 `name: string`、`description: string`、`func` 属性。`_call` 直接调用 `this.func(input, runManager, parentConfig)`。

F-055: 文件 `tools/index.ts` 第478-564行，`DynamicStructuredTool` 类继承 `StructuredTool`，包含 `name`、`description`、`func`、`schema` 属性。支持 Zod 或 JSON Schema。

F-056: 文件 `tools/index.ts` 第571-577行，抽象类 `BaseToolkit` 声明 `abstract tools: StructuredToolInterface[]`，提供 `getTools()` 方法返回 tools 数组。

F-057: 文件 `tools/index.ts` 第642-1025行，`tool(func, fields)` 工厂函数具有多个重载：支持 ZodString（返回 DynamicTool）、ZodObject v3/v4（返回 DynamicStructuredTool）、JSONSchema（返回 DynamicStructuredTool）、带 ToolRuntime 参数的函数签名。当 schema 未提供、为简单字符串 schema 或仅验证字符串的 JSON Schema 时创建 DynamicTool，否则创建 DynamicStructuredTool。函数内部通过 `AsyncLocalStorageProviderSingleton.runWithConfig` 在正确的异步上下文中执行用户函数，并处理 AbortSignal。

F-058: 文件 `tools/index.ts` 第1031-1065行，`_formatToolOutput(params)` 函数：当存在 toolCallId 且 content 不是 DirectToolOutput 时，创建 ToolMessage（status: "success"）；若 content 不是字符串或内容块数组则 JSON.stringify；无 toolCallId 时直接返回 content。

F-059: 文件 `tools/index.ts` 第1075-1079行，导出类型 `ServerTool = Record<string, unknown>` 和 `ClientTool = StructuredToolInterface | DynamicTool | RunnableToolLike`。

## Prompt 模板（langchain-core/src/prompts/）

F-060: 文件 `prompts/base.ts` 第24-42行，`BasePromptTemplateInput` 接口包含 `inputVariables: string[]`、`outputParser?: BaseOutputParser`、`partialVariables?: PartialValues`。

F-061: 文件 `prompts/base.ts` 第48-93行，抽象类 `BasePromptTemplate<RunInput, RunOutput, PartialVariableName>` 继承 `Runnable<RunInput, RunOutput>`。设置 `lc_serializable = true`，`lc_namespace = ["langchain_core", "prompts", this._getPromptType()]`。`lc_attributes` 将 partialVariables 设为 undefined（Python 不支持）。构造函数禁止 inputVariables 包含 `"stop"`。

F-062: 文件 `prompts/base.ts` 第95-97行，声明抽象方法 `abstract partial(values: PartialValues): Promise<BasePromptTemplate>`。

F-063: 文件 `prompts/base.ts` 第133-147行，`invoke(input, options?)` 方法通过 `_callWithConfig` 调用 `this.formatPromptValue(input)`，设置 `runType: "prompt"`，合并 metadata 和 tags。

F-064: 文件 `prompts/prompt.ts` 第110-118行，`PromptTemplate` 类继承 `BaseStringPromptTemplate`，实现 `PromptTemplateInput`。`static lc_name()` 返回 `"PromptTemplate"`。属性 `template: MessageContent`、`templateFormat: TemplateFormat = "f-string"`、`validateTemplate = true`、`additionalContentFields?`。

F-065: 文件 `prompts/prompt.ts` 第136-150行，构造函数中若 templateFormat 为 `"mustache"` 且 validateTemplate 未定义则设为 false；validateTemplate 为 true 时 mustache 模板抛出错误。

F-066: 文件 `prompts/chat.ts` 第50-87行，抽象类 `BaseMessagePromptTemplate<RunInput, RunOutput>` 继承 `Runnable<RunInput, RunOutput>`。声明 `abstract inputVariables` 和 `abstract formatMessages(values): Promise<RunOutput>`。`invoke` 通过 `_callWithConfig` 调用 formatMessages，runType 为 `"prompt"`。

F-067: 文件 `prompts/chat.ts` 第101-134行，`MessagesPlaceholder<RunInput>` 类继承 `BaseMessagePromptTemplate`，包含 `variableName: string` 和 `optional: boolean`（默认 false）。`inputVariables` 返回 `[this.variableName]`。formatMessages 从 values 中取出消息数组，optional 为 true 且无值时返回空数组，否则无值时抛出 InputFormatError。

F-068: 文件 `prompts/chat.ts` 第298行、707行、724行、751行分别导出 `ChatMessagePromptTemplate`、`HumanMessagePromptTemplate`、`AIMessagePromptTemplate`、`SystemMessagePromptTemplate`，各自通过静态 `_messageClass()` 返回对应消息类。

F-069: 文件 `prompts/chat.ts` 第924行，`ChatPromptTemplate` 类导出，用于组合多个消息模板为聊天提示。

## Document（langchain-core/src/documents/document.ts）

F-070: 文件 `documents/document.ts` 第1-16行，`DocumentInput<Metadata>` 接口包含 `pageContent: string`、`metadata?: Metadata`、`id?: string`。

F-071: 文件 `documents/document.ts` 第38-64行，`Document<Metadata>` 类实现 `DocumentInput` 和 `DocumentInterface`。属性 `pageContent: string`（构造时调用 `.toString()`，默认空字符串）、`metadata: Metadata`（默认 `{}`）、`id?: string`（建议 UUID 但不强制）。

## Serializable 序列化（langchain-core/src/load/serializable.ts）

F-072: 文件 `load/serializable.ts` 第4-24行，定义三种序列化类型：`SerializedConstructor`（含 `kwargs: SerializedFields`）、`SerializedSecret`（密钥占位）、`SerializedNotImplemented`。所有类型都包含 `lc: number`、`type: T`、`id: string[]`。

F-073: 文件 `load/serializable.ts` 第97-106行，抽象类 `Serializable` 实现 `SerializableInterface`。`lc_serializable = false`（默认不可序列化），`lc_kwargs: SerializedFields`，声明 `abstract lc_namespace: string[]`。

F-074: 文件 `load/serializable.ts` 第114-126行，静态方法 `static lc_name(): string` 默认返回 `this.name`（类名），子类可覆盖以在压缩环境中保持名称。`get lc_id(): string[]` 返回 `[...lc_namespace, get_lc_unique_name(constructor)]`。

F-075: 文件 `load/serializable.ts` 第133-163行，提供四个可选 getter：`lc_secrets`（密钥路径到密钥 ID 的映射，序列化时替换为 secret 占位）、`lc_attributes`（额外构造参数）、`lc_aliases`（构造参数别名，用于匹配 Python 命名）、`lc_serializable_keys`（手动指定应序列化的键白名单）。

F-076: 文件 `load/serializable.ts` 第177行起，`toJSON(): Serialized` 方法：若 `lc_serializable` 为 false 返回 `toJSONNotImplemented`；否则遍历 lc_kwargs，从实例读取当前值，沿原型链收集 secrets/attributes/aliases，通过 `replaceSecrets` 替换敏感字段，返回 SerializedConstructor。

## Callbacks 系统（langchain-core/src/callbacks/）

F-077: 文件 `callbacks/base.ts` 第29-37行，`BaseCallbackHandlerInput` 接口包含 `ignoreLLM?`、`ignoreChain?`、`ignoreAgent?`、`ignoreRetriever?`、`ignoreCustomEvent?`、`_awaitHandler?`、`raiseError?` 布尔选项。

F-078: 文件 `callbacks/base.ts` 第58行起，`BaseCallbackHandlerMethodsClass` 定义所有可选回调方法：`handleLLMStart`、`handleLLMNewToken`、`handleChatModelStreamEvent`、`handleLLMError`、`handleLLMEnd`、`handleChatModelStart`、`handleChainStart`、`handleChainError`、`handleChainEnd`、`handleToolStart`、`handleToolEnd`、`handleToolError`、`handleAgentAction`、`handleAgentEnd`、`handleRetrieverStart`、`handleRetrieverEnd`、`handleRetrieverError`、`handleCustomEvent` 等，均返回 `Promise<any> | any`。

F-079: 文件 `callbacks/manager.ts` 第779行，`CallbackManager` 类导出，管理 handlers、tags、metadata，提供 `configure` 静态方法和 `handleChainStart`/`handleLLMStart`/`handleToolStart`/`handleRetrieverStart` 等方法创建子管理器。

F-080: 文件 `callbacks/manager.ts` 分别在第298行、373行、517行、664行导出 `CallbackManagerForRetrieverRun`、`CallbackManagerForLLMRun`、`CallbackManagerForChainRun`、`CallbackManagerForToolRun`，这些是单次运行范围内的回调管理器，提供 `getChild()` 方法创建子运行管理器。

## Output Parsers（langchain-core/src/output_parsers/base.ts）

F-081: 文件 `output_parsers/base.ts` 第19-22行，抽象类 `BaseLLMOutputParser<T>` 继承 `Runnable<string | BaseMessage, T>`。声明 `abstract parseResult(generations: Generation[] | ChatGeneration[], callbacks?): Promise<T>`。

F-082: 文件 `output_parsers/base.ts` 第72-99行，`invoke(input, options?)` 方法：若 input 为字符串，包装为 `[{ text: input }]`；若为 BaseMessage，包装为 `[{ message: input, text: contentToString }]`，然后调用 `parseResult`，runType 为 `"parser"`。

F-083: 文件 `output_parsers/base.ts` 第105-150行，抽象类 `BaseOutputParser<T>` 继承 `BaseLLMOutputParser<T>`。`parseResult` 默认取 `generations[0].text` 调用 `this.parse`。声明 `abstract parse(text: string, callbacks?): Promise<T>` 和 `abstract getFormatInstructions(options?): string`。提供 `_type()` 方法默认抛出未实现错误。

F-084: 文件 `output_parsers/base.ts` 第170-197行，`OutputParserException` 类继承 Error，包含 `llmOutput?`、`observation?`、`sendToLLM: boolean`（默认 false）。当 sendToLLM 为 true 时必须提供 observation 和 llmOutput。通过 `addLangChainErrorFields` 设置错误码为 `"OUTPUT_PARSING_FAILURE"`。

## Agents 类型（langchain-core/src/agents.ts）

F-085: 文件 `agents.ts` 第1-6行，`AgentAction` 类型包含 `tool: string`、`toolInput: string | Record<string, any>`、`log: string`。

F-086: 文件 `agents.ts` 第8-12行，`AgentFinish` 类型包含 `returnValues: Record<string, any>`、`log: string`。

F-087: 文件 `agents.ts` 第14-17行，`AgentStep` 类型包含 `action: AgentAction`、`observation: string`。

## Embeddings（langchain-core/src/embeddings.ts）

F-088: 文件 `embeddings.ts` 第9-26行，`EmbeddingsInterface<TOutput = number[]>` 接口声明 `embedDocuments(documents: string[]): Promise<TOutput[]>` 和 `embedQuery(document: string): Promise<TOutput>`。

F-089: 文件 `embeddings.ts` 第32-61行，抽象类 `Embeddings<TOutput = number[]>` 实现 `EmbeddingsInterface`。构造函数创建 `AsyncCaller` 实例（用于并发控制和重试）。声明两个抽象方法 `embedDocuments` 和 `embedQuery`。

## ReactAgent（langchain/src/agents/ReactAgent.ts）

F-090: 文件 `agents/ReactAgent.ts` 第164-173行，`ReactAgent<Types>` 类是生产就绪的 ReAct（Reasoning + Acting）代理。泛型参数 `Types extends AgentTypeConfig` 封装 Response、State、Context、Middleware、Tools、StreamTransformers 六个类型参数。类声明 `declare readonly "~agentTypes": Types` 作为类型推断的幻影属性。

F-091: 文件 `agents/ReactAgent.ts` 第181-187行，私有字段 `#graph: CompiledStateGraph`、`#toolBehaviorVersion: "v1" | "v2" = "v2"`、`#agentNode: AgentNode`、`#defaultConfig: RunnableConfig`。

F-092: 文件 `agents/ReactAgent.ts` 第189-256行，构造函数接受 `options: CreateAgentParams` 和可选 `defaultConfig`。验证 `options.model` 必填，调用 `validateLLMHasNoBoundTools` 确保模型未预绑定工具。合并 options.tools 和 middleware.tools。创建 AgentState（通过 `createAgentState`），初始化 `StateGraph`（传入 state/input/output/context schema）。

F-093: 文件 `agents/ReactAgent.ts` 第304-377行，构造函数遍历 middleware 数组，为每个 middleware 的 `beforeAgent`/`beforeModel`/`afterModel`/`afterAgent` hook 创建对应节点（BeforeAgentNode/BeforeModelNode/AfterModelNode/AfterAgentNode），节点命名为 `${m.name}.before_agent` 等格式。middleware 名称不可重复。`wrapModelCall` hook 的 middleware 被收集到 `wrapModelCallHookMiddleware` 数组。

F-094: 文件 `agents/ReactAgent.ts` 第382-402行，添加 AGENT_NODE_NAME 节点（AgentNode 实例）；当存在客户端工具或 `wrapToolCall` middleware 时创建 TOOLS_NODE_NAME 节点（ToolNode 实例），传入 `wrapToolCall` 包装函数。

F-095: 文件 `agents/ReactAgent.ts` 第94-97行，`BaseGraphDestination` 类型为 `typeof TOOLS_NODE_NAME | typeof AGENT_NODE_NAME | typeof END`，是图中唯一可跳转的目标节点。

F-096: 文件 `agents/ReactAgent.ts` 第407-426行，确定入口节点优先级：beforeAgent 节点 → beforeModel 节点 → AGENT_NODE_NAME。循环入口节点（工具执行后返回点）为 beforeModel 节点或 AGENT_NODE_NAME。退出节点为最后一个 afterAgent 节点或 END。

## createAgent 工厂（langchain/src/agents/index.ts）

F-097: 文件 `agents/index.ts` 第672-702行，`createAgent(params)` 函数实现为 `return new ReactAgent(params)`。具有13个重载签名，支持 responseFormat 为 InteropZodType、InteropZodType[]、JsonSchemaFormat、JsonSchemaFormat[]、SerializableSchema、SerializableSchema[]、ToolStrategy、ProviderStrategy、undefined 等多种形式。

F-098: 文件 `agents/index.ts` 第704-730行，重新导出：`./types.js`、`./errors.js`、`./nodes/types.js`、`JumpToTarget`、`Runtime`、`toolStrategy`/`providerStrategy`/`ToolStrategy`/`ProviderStrategy`、`createMiddleware`、`MIDDLEWARE_BRAND`、middleware 类型、`FakeToolCallingModel`、`ReactAgent` 类型、transformers（`createToolCallTransformer`、`createSubagentTransformer`）。

## Agent State Annotation（langchain/src/agents/annotation.ts）

F-099: 文件 `agents/annotation.ts` 第24-31行，`createAgentState(hasStructuredResponse, stateSchema, middlewareList)` 函数创建代理状态 schema。初始化 `stateFields` 包含 `jumpTo: new UntrackedValue<JumpToTarget>()`（用于内部控制流导航，不暴露为输入/输出通道）。

F-100: 文件 `agents/annotation.ts` 第44-119行，内部 `applySchema` 函数处理两种 schema 形式：(1) `StateSchema` 实例——遍历 `.fields`，`ReducedValue` 字段提取 inputSchema/valueSchema 到输入/输出字段，下划线前缀字段为私有状态；(2) Zod v3/v4 对象——通过 `getInteropZodObjectShape` 提取 shape，Zod v4 支持 `schemaMetaRegistry` 中的 reducer 元数据，自动包装为 `ReducedValue`。

F-101: 文件 `agents/annotation.ts` 第155-168行，返回三个 `StateSchema` 实例：`state`（包含 messages: MessagesValue 和所有 stateFields）、`input`（包含 messages: MessagesValue 和非私有输入字段）、`output`（包含 messages: MessagesValue 和非私有输出字段，有 structuredResponse 时追加 `UntrackedValue`）。

## Middleware 系统（langchain/src/agents/middleware/）

F-102: 文件 `agents/middleware/types.ts` 第65-96行，`MiddlewareTypeConfig<TSchema, TContextSchema, TFullContext, TTools, TStreamTransformers>` 接口作为类型袋，封装 Schema、ContextSchema、FullContext、Tools、StreamTransformers 五个类型参数。

F-103: 文件 `agents/middleware/types.ts` 第135-139行，`MiddlewareResult<TState>` 类型为 `(TState & { jumpTo?: JumpToTarget }) | void`，middleware 可返回部分状态更新和可选的 jumpTo 导航指令。

F-104: 文件 `agents/middleware.ts` 第76行起，`createMiddleware(config)` 工厂函数创建 middleware 实例，配置项包括 `name`、`stateSchema`、`contextSchema`、`wrapModelCall`、`wrapToolCall`、`beforeModel`、`afterModel`、`beforeAgent`、`afterAgent`、`tools`、`streamTransformers`。

F-105: 文件 `agents/middleware/index.ts` 导出内置 middleware：`hitl`（人类在环）、`summarizationMiddleware`（摘要）、`dynamicSystemPromptMiddleware`（动态系统提示）、`llmToolSelectorMiddleware`（LLM 工具选择）、`piiMiddleware`/`piiRedactionMiddleware`（PII 检测与脱敏）、`contextEditingMiddleware`（上下文编辑）、`toolCallLimitMiddleware`（工具调用次数限制）、`todoListMiddleware`（TODO 列表）、`modelCallLimitMiddleware`（模型调用次数限制）、`modelFallbackMiddleware`（模型回退）、`modelRetryMiddleware`（模型重试）、`toolRetryMiddleware`（工具重试）、`toolErrorMiddleware`（工具错误处理）、`toolEmulatorMiddleware`（工具模拟）、`providerToolSearchMiddleware`（provider 工具搜索），以及 provider 特定的 `openAIModerationMiddleware`、`anthropicPromptCachingMiddleware`、`bedrockPromptCachingMiddleware`。

F-106: 文件 `agents/middleware/index.ts` 第104-105行，导出类型 `AgentMiddleware` 和工具函数 `countTokensApproximately`。

## RunnableConfig 字段与回调管理器

F-107: 文件 `runnables/config.ts` 第12-31行，`_getTracingInheritableMetadataFromConfig(config)` 将 configurable 中的非 `__` 前缀、非 api_key、原始类型（string/number/boolean）且未在 metadata 中显式设置的键值对提升为 LangSmith tracing metadata。

F-108: 文件 `runnables/base.ts` 第325-357行，`_separateRunnableConfigFromCallOptions(options)` 将选项拆分为标准 RunnableConfig（callbacks/tags/metadata/runName/configurable/recursionLimit/maxConcurrency/runId/timeout/signal）和剩余的 callOptions。

F-109: 文件 `runnables/base.ts` 第359-392行，`_callWithConfig(func, input, options)` 模板方法：通过 `getCallbackManagerForConfig` 获取回调管理器，调用 `handleChainStart`，使用 `raceWithSignal` 执行 func，错误时调用 `handleChainError`，成功时调用 `handleChainEnd`。
