---
type: Reference
title: LangGraphJS 源码事实清单
description: 从 langgraphjs 源码中提取的编号事实，用于验证概念文档准确性
tags: [facts, source-verification, langgraphjs]
generated:
  by: reference_agent/trae-solo
  at: 2026-08-23T00:00:00Z
status: stable
sources:
  - id: langgraphjs-source
    resource: https://github.com/langchain-ai/langgraphjs
    title: LangGraphJS GitHub Repository
    author: team:langchain-ai
---

# LangGraphJS 源码事实清单

本文件记录从 `libs/langgraph-core/src/` 与 `libs/checkpoint/src/` 中提取的编号事实，每条事实标注源码位置，供 V 阶段验证使用。

## 1. 包结构与分层

- **F1.1** 仓库采用 pnpm monorepo，核心包位于 `libs/langgraph-core/`，checkpoint 抽象位于 `libs/checkpoint/`，后端实现包括 `checkpoint-postgres`、`checkpoint-sqlite`、`checkpoint-redis`、`checkpoint-mongodb`。（`libs/` 目录结构）
- **F1.2** 系统分为四层：Channels 层（状态管理原语）、Checkpointer 层（持久化）、Pregel 层（消息传递执行引擎）、Graph 层（高层工作流 API）。（CLAUDE.md "Library Architecture"）
- **F1.3** 主入口 `src/index.ts` 初始化 `AsyncLocalStorage` 单例后重新导出 `web.ts`；`web.ts` 是面向用户的公共 API 桶文件。（`src/index.ts:1-8`、`src/web.ts:1-189`）

## 2. Graph 层核心类

- **F2.1** `StateGraph` 是用户构建有状态工作流的主类，继承自 `Graph`，泛型参数包括状态通道、输入/输出类型。（`graph/state.ts:107+`，从导入与类定义推断）
- **F2.2** `Graph` 基类提供 `addNode`、`addEdge`、`addConditionalEdges`、`compile` 方法；编译产物为 `CompiledGraph`，后者继承 `Pregel`。（`graph/graph.ts:22-30` 导入 `Pregel`；`pregel/index.ts:399` JSDoc 明确说明）
- **F2.3** `Branch` 类实现条件边，持有 `path`（Runnable）与可选 `ends`（pathMap）；`run` 方法注册 writer，`_route` 执行路由并返回目标节点名或 `Send` 数组。（`graph/graph.ts:128-200`）
- **F2.4** 两个保留节点名常量：`START = "__start__"`、`END = "__end__"`。（`constants.ts:8-10`）
- **F2.5** `MessageGraph` 继承 `StateGraph<BaseMessage[], BaseMessage[], Messages>`，内置 `__root__` 通道使用 `messagesStateReducer`，默认值为空数组。（`graph/message.ts:13-28`）

## 3. Annotation 与状态定义

- **F3.1** `Annotation` 是一个函数对象，调用签名：无参数返回 `LastValue<T>` 通道；传入 `SingleReducer` 返回 `BinaryOperatorAggregate` 通道；`Annotation.Root(sd)` 创建 `AnnotationRoot` 实例。（`graph/annotation.ts:158-172`）
- **F3.2** `AnnotationRoot<SD>` 类携带 `lc_graph_name = "AnnotationRoot"` 标记，声明 `State`、`Update`、`Node` 三个类型插槽，`spec` 属性保存原始状态定义。（`graph/annotation.ts:62-85`）
- **F3.3** `SingleReducer<V, U>` 类型支持三种形式：`{ reducer, default? }`、已废弃的 `{ value, default? }`、`null`。（`graph/annotation.ts:7-19`）
- **F3.4** `getChannel` 工厂函数根据 reducer 配置返回 `BinaryOperatorAggregate`（有 reducer）或 `LastValue`（无 reducer）。（`graph/annotation.ts:174-195`）
- **F3.5** `StateType<SD>` 将每个 `StateDefinition` 键映射为通道的 `ValueType`；`UpdateType<SD>` 映射为可选的 `UpdateType`；`NodeType<SD>` 是接收 `StateType` 返回 `UpdateType | Partial<StateType>` 的 `RunnableLike`。（`graph/annotation.ts:37-48`）

## 4. Channels 通道体系

- **F4.1** `BaseChannel<ValueType, UpdateType, CheckpointType>` 是抽象基类，声明 `lc_graph_name`、`lg_is_channel = true`，核心抽象方法：`fromCheckpoint`、`update(values)`、`get()`、`checkpoint()`；生命周期方法 `consume()`、`finish()` 默认 no-op。（`channels/base.ts:30-138`）
- **F4.2** `LastValue<Value>` 通道每步最多接收一个值，多值写入抛 `InvalidUpdateError`（code `INVALID_CONCURRENT_GRAPH_UPDATE`）；内部用 `[Value] | []` 元组区分「未写入」与「写入 undefined」。（`channels/last_value.ts:12-67`）
- **F4.3** `BinaryOperatorAggregate<V, U>` 通道持有 `operator: BinaryOperator<V, U>`，将新值与当前值归约；支持 `OverwriteValue` 绕过 reducer，同一步多个 Overwrite 抛错；`equals` 比较 operator 引用。（`channels/binop.ts:27-127`）
- **F4.4** `Topic<Value>` 是可配置 PubSub 通道，选项 `unique`（引用去重）、`accumulate`（跨步累积，默认每步清空）；checkpoint 格式在 `unique: true` 时为 `[seen, values]`，否则为扁平 `values` 数组。（`channels/topic.ts:27-136`）
- **F4.5** `LastValueAfterFinish<Value>` 通道在 `finish()` 被调用后才可读，`consume()` 后清空；用于「图结束时才暴露」的值。（`channels/last_value.ts:73-138`）
- **F4.6** `emptyChannels(channels, checkpoint)` 从 checkpoint 恢复每个通道：调用 `fromCheckpoint(channel_value)`，返回新通道实例集合。（`channels/base.ts:158-172`）
- **F4.7** `isBaseChannel(obj)` 通过 `lg_is_channel === true` 结构判定，避免 instanceof 跨版本问题。（`channels/base.ts:25-27`）

## 5. Pregel 执行引擎

- **F5.1** `Pregel` 类继承 `PartialRunnable<Runnable>`，是 LangGraph 的核心运行时，灵感来自 Google Pregel；不直接实例化，由 `StateGraph.compile()` 或 `entrypoint()` 返回。（`pregel/index.ts:385-466`）
- **F5.2** Pregel 执行模型基于「超步（superstep）」：节点在超步内并行执行，通过通道消息传递，`DEFAULT_LOOP_LIMIT = 25` 作为递归限制默认值。（`pregel/loop.ts:113`；`constants.ts:94 RECURSION_LIMIT_DEFAULT = 25`）
- **F5.3** `Channel` 工具类提供静态方法 `subscribeTo(channel(s), options?)` 创建 `PregelNode`（订阅通道作为触发器），`writeTo(channels, writes?)` 创建 `ChannelWrite`。（`pregel/index.ts:196-347`）
- **F5.4** `shouldInterrupt(checkpoint, interruptNodes, tasks)` 判定是否在断点处中断：检查通道版本是否自上次 seen 以来更新，且触发节点在中断名单内。（`pregel/algo.ts:127-163`）
- **F5.5** `_localRead` 支持节点在执行期间读取通道「新鲜值」（包含本步已写入但尚未 apply 的值），用于节点内状态查询。（`pregel/algo.ts:165-200+`）
- **F5.6** `PregelLoop` 类封装单次图运行的主循环，持有 checkpoint、channels、step、stop、nodes、stream 等状态；`PregelLoopInitializeParams` 包含 checkpointer、interruptAfter/Before、durability、debug 等。（`pregel/loop.ts:136-187`）
- **F5.7** `Durability` 类型取值：`"exit"` | `"async"` | `"sync"`，控制 checkpoint 持久化时机。（`pregel/types.ts:35`）
- **F5.8** `PregelRunner` 负责任务实际执行（在 `runner.ts` 中），与 `PregelLoop` 协作。（`pregel/index.ts:88` 导入）

## 6. Checkpoint 持久化

- **F6.1** `Checkpoint` 接口字段：`v`（格式版本，当前为 4）、`id`（uuid6）、`ts`（ISO 时间戳）、`channel_values`、`channel_versions`、`versions_seen`。（`checkpoint/src/base.ts:18-46`）
- **F6.2** `BaseCheckpointSaver<V>` 抽象类声明抽象方法：`getTuple(config)`、`list(config, options?)`、`put(config, checkpoint, metadata, newVersions)`、`putWrites(config, writes, taskId)`、`deleteThread(threadId)`。（`checkpoint/src/base.ts:113-162`）
- **F6.3** `CheckpointTuple` 包含 `config`、`checkpoint`、可选 `metadata`、`parentConfig`、`pendingWrites`，构成 checkpoint 链表节点。（`checkpoint/src/base.ts:98-104`）
- **F6.4** `emptyCheckpoint()` 返回 `v:4`、`id: uuid6(0)`、空映射的初始 checkpoint。（`checkpoint/src/base.ts:75-84`）
- **F6.5** `MemorySaver` 是内存 saver 实现，用三级键 `threadId → checkpointNs → checkpointId` 存储；`storage` 与 `writes` 使用 `Object.create(null)` 防原型污染，`assertSafeStorageKey` 拦截 `__proto__`/`constructor`/`prototype` 键（CWE-1321 防护）。（`checkpoint/src/memory.ts:28-118`）
- **F6.6** `getDeltaChannelHistory` 沿 `parentConfig` 链向上走，为每个 `DeltaChannel` 收集 pending writes 直到最近快照作为 seed，用于增量通道状态重建。（`checkpoint/src/base.ts:193-200+`）
- **F6.7** `JsonPlusSerializer` 是默认序列化器，支持比 JSON 更丰富的类型。（`checkpoint/src/base.ts:11` 导入；`serde/jsonplus.ts`）

## 7. Stream 流式系统

- **F7.1** `StreamMode` 类型包含 8 种：`"values"` | `"updates"` | `"debug"` | `"messages"` | `"checkpoints"` | `"tasks"` | `"custom"` | `"tools"`。（`pregel/types.ts:25-33`）
- **F7.2** 默认流模式为 `"updates"`（`DefaultStreamMode = "updates"`）。（`pregel/types.ts:106`）
- **F7.3** `IterableReadableWritableStream` 是内部双工流，`createDuplexStream` 创建；`StreamChunkMeta` 携带命名空间等元数据。（`pregel/stream.ts`，从 `loop.ts:105-108` 导入推断）
- **F7.4** 支持 SSE 编码：当 `encoding: "text/event-stream"` 时输出 `Uint8Array`，`protocolEventsToEventStream` 将 `ProtocolEvent` 转为 `event: xxx\ndata: {...}\n\n` 格式。（`pregel/index.ts:159-187`）
- **F7.5** `StreamMessagesHandler` 回调处理器实现消息 token 级流，`pushMessage` 函数可在节点执行中手动推送消息。（`pregel/messages.ts`；`graph/message.ts:42-98`）
- **F7.6** 新版流系统位于 `stream/` 目录，提供 `GraphRunStream`、`createGraphRunStream`、`StreamTransformer` 协议及内置 transformer（`createMessagesTransformer`、`createValuesTransformer`、`createLifecycleTransformer`、`createSubgraphDiscoveryTransformer`）。（`web.ts:52-95`）
- **F7.7** `STREAM_EVENTS_V3_MODES` 常量标识 v3 协议事件模式集合。（`web.ts:58`、`pregel/index.ts:99`）

## 8. Command、Send 与控制流

- **F8.1** `Send<Node, Args>` 类用于条件边中动态向节点发送自定义状态（map-reduce 模式），字段 `node`、`args`、可选 `timeout`；`_isSend(x)` 类型守卫。（`constants.ts:250-286`）
- **F8.2** `Command<Resume, Update, Nodes>` 类组合状态更新与路由，字段 `update`、`resume`、`goto`（节点名/Send/数组）、`graph`；静态常量 `Command.PARENT = "__parent__"` 用于子图向父图发命令。（`constants.ts:540-640`）
- **F8.3** `Command._updateAsTuples()` 将 update 转为 `[channelKey, value]` 元组列表；对象用 `Object.entries`，已经是元组数组则原样返回，其他包装为 `["__root__", update]`。（`constants.ts:598-616`）
- **F8.4** `Overwrite<ValueType>` 类绕过 reducer 直接替换通道值，同一步多个 Overwrite 抛 `InvalidUpdateError`；`_isOverwriteValue` 与 `_getOverwriteValue` 支持类实例与线格式双检测。（`constants.ts:288-403`）
- **F8.5** `isInterrupted(values)` 检测返回值是否含 `INTERRUPT` 通道的中断数组。（`constants.ts:427-433`）
- **F8.6** `_deserializeCommandSendObjectGraph` 深度遍历重建跨 JSON 边界反序列化的 Command/Send 对象，使用 `seen` Map 处理循环引用。（`constants.ts:684-742`）

## 9. 错误体系

- **F9.1** `BaseLangGraphError` 继承 Error，可选 `lc_error_code`，自动追加 Troubleshooting URL；错误码包括 `GRAPH_RECURSION_LIMIT`、`INVALID_CONCURRENT_GRAPH_UPDATE`、`INVALID_GRAPH_NODE_RETURN_VALUE`、`MISSING_CHECKPOINTER`、`MULTIPLE_SUBGRAPHS`、`UNREACHABLE_NODE`。（`errors.ts:5-28`）
- **F9.2** `GraphBubbleUp` 是控制流异常基类（`is_bubble_up` getter），子类包括 `GraphInterrupt`、`GraphDrained`，用于非局部跳转而非真正错误。（`errors.ts:30-97`）
- **F9.3** `NodeInterrupt` 继承 `GraphInterrupt`，节点内调用 `interrupt()` 时抛出；在条件边中抛出会被检测并打印警告。（`errors.ts:100-110`；`graph/graph.ts:172-178`）
- **F9.4** `GraphDrained` 表示图因 `RunControl.requestDrain()`（如 SIGTERM）在超步边界协作停止，checkpoint 已保存可稍后恢复。（`errors.ts:58-83`）
- **F9.5** `NodeError` 携带失败节点名 `node` 与原始错误 `error`，传给节点级 errorHandler；errorHandler 在重试策略耗尽后运行。（`errors.ts:112-149`）

## 10. 节点策略与运行时控制

- **F10.1** `NodePolicyOptions` 包含 `retryPolicy`、`cachePolicy`（`CachePolicy | boolean`）、`timeout`（毫秒数或 `TimeoutPolicy`）。（`graph/state.ts:138-167`）
- **F10.2** `setNodeDefaults` 可设置图级默认策略，`compile()` 时解析；每节点值优先于默认值；`DEFAULT_ERROR_HANDLER_NODE = "__default_error_handler__"` 是图级错误处理器的保留节点名。（`graph/state.ts:114`、`183-196`）
- **F10.3** `RunControl` 类提供运行时控制能力（如 `requestDrain`），通过 `getStore`、`getWriter`、`getConfig` 等工具函数在节点内访问上下文。（`web.ts:175`、`187`；`pregel/runtime.ts`）
- **F10.4** `RetryPolicy`、`CachePolicy`、`TimeoutPolicy` 从 `pregel/utils/index.js` 导出。（`web.ts:113-117`）

## 11. 函数式 API

- **F11.1** `entrypoint(options?, func)` 创建函数式工作流，返回 Pregel 实例；`task(name, func, options?)` 声明可组合的任务单元。（`web.ts:157-162`；`func/index.ts`、`func/types.ts`）
- **F11.2** `getPreviousState()` 在 entrypoint 内获取同线程上次调用状态。（`web.ts:188`）
- **F11.3** `interrupt(value)` 函数暂停执行等待人工输入；`InferInterruptInputType`、`InferInterruptResumeType` 类型推导中断输入/恢复值类型。（`web.ts:179-183`；`interrupt.ts`）
- **F11.4** `writer()` 与 `getWriter()` 支持节点内自定义流式写入，`InferWriterType` 推导写入类型。（`web.ts:184-185`）

## 12. 消息管理

- **F12.1** `messagesStateReducer`（别名 `addMessages`）是消息列表归约器；`messagesDeltaReducer` 支持增量消息更新；`REMOVE_ALL_MESSAGES` 哨兵清空消息。（`web.ts:7-10`；`graph/messages_reducer.ts`）
- **F12.2** `MessagesAnnotation` 是预构建的消息状态 Annotation，`MessagesZodState`/`MessagesZodMeta` 提供 Zod schema 集成。（`web.ts:164-168`；`graph/messages_annotation.ts`）
- **F12.3** `pushMessage(message, options?)` 在节点执行中手动推送消息到流，要求消息有 ID，默认写入 `"messages"` 状态键，`stateKey: null` 可禁止持久化。（`graph/message.ts:42-98`）
- **F12.4** `ensureMessageIds` 递归为缺失 ID 的 `BaseMessage` 分配 uuid4，确保 DeltaChannel 重放时消息身份一致。（`pregel/loop.ts:120-134`）

## 13. 状态 Schema 与互操作

- **F13.1** `state/` 目录提供新版状态 schema 系统：`StateSchema`、adapter、values（`delta`、`reduced`、`untracked`）。（`state/index.ts`、`state/schema.ts`、`state/adapter.ts`）
- **F13.2** 支持 Zod 互操作：`isInteropZodObject`、`interopParse`、`interopZodObjectPartial`、`getInteropZodObjectShape`；`graph/zod/` 提供 Zod 插件、meta 注册、schema 注册。（`graph/state.ts:10-15` 导入；`graph/zod/`）
- **F13.3** `schemaMetaRegistry` 单例管理 Zod schema 元数据。（`graph/state.ts:84`）

## 14. 其他关键常量与机制

- **F14.1** `CHECKPOINT_NAMESPACE_SEPARATOR = "|"`，`CHECKPOINT_NAMESPACE_END = ":"`，用于嵌套子图 checkpoint 命名空间。（`constants.ts:134-135`）
- **F14.2** 保留通道：`INTERRUPT = "__interrupt__"`、`RESUME = "__resume__"`、`RETURN = "__return__"`、`TASKS = "__pregel_tasks"`、`ERROR = "__error__"`、`NO_WRITES = "__no_writes__"`。（`constants.ts:84-102`）
- **F14.3** `CONFIG_KEY_*` 系列常量是注入到 `RunnableConfig.configurable` 的内部键（`__pregel_send`、`__pregel_read`、`__pregel_checkpointer` 等），全部列入 `RESERVED` 数组防止用户占用。（`constants.ts:50-132`）
- **F14.4** `NULL_TASK_ID = "00000000-0000-0000-0000-000000000000"` 是全零任务 ID 哨兵；`TASK_NAMESPACE` 是固定 UUID 命名空间用于 uuid5。（`constants.ts:104-105`）
- **F14.5** `getDeltaMaxSuperstepsSinceSnapshot()` 默认返回 5000，可通过环境变量 `LANGGRAPH_DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT` 覆盖，防止 DeltaChannel 无界祖先遍历。（`constants.ts:38-48`）
