# LangGraph 事实清单

## 项目元信息

F-001: 包 `langgraph` 的版本通过 `importlib.metadata.version(__package__)` 动态获取（`langgraph/version.py` 第7-11行），无硬编码版本号。`__all__ = ("__version__",)`。

F-002: 仓库为 monorepo，`libs/langgraph` 是核心框架库，`libs/checkpoint` 提供检查点基类接口（`AGENTS.md`）。依赖关系：checkpoint ← checkpoint-postgres / checkpoint-sqlite / prebuilt / langgraph；prebuilt → langgraph。

F-003: 公共 API 入口 `langgraph/graph/__init__.py` 导出 `END`、`START`、`StateGraph`、`add_messages`、`MessagesState`、`MessageGraph`。`__all__` 包含这6个名称。

## 常量（langgraph/constants.py）

F-004: `START = sys.intern("__start__")`，图的第一个虚拟节点；`END = sys.intern("__end__")`，图的最后一个虚拟节点（`constants.py` 第28-31行）。

F-005: `TAG_HIDDEN = sys.intern("langsmith:hidden")`，用于在 tracing/streaming 中隐藏节点/边；`TAG_NOSTREAM = sys.intern("nostream")`，禁用聊天模型流式输出（`constants.py` 第24-27行）。

F-006: 模块级 `__getattr__` 对 `Send`、`Interrupt` 发出弃用警告并重定向到 `langgraph.types`；其他私有常量重定向到 `langgraph._internal._constants`（`constants.py` 第34-62行）。

## 内部常量（langgraph/_internal/_constants.py）

F-007: 保留写入键包括：`INPUT="__input__"`、`INTERRUPT="__interrupt__"`、`RESUME="__resume__"`、`ERROR="__error__"`、`ERROR_SOURCE_NODE="__error_source_node__"`、`NO_WRITES="__no_writes__"`、`TASKS="__pregel_tasks"`、`RETURN="__return__"`、`PREVIOUS="__previous__"`（第7-26行）。

F-008: 配置键包括：`CONFIG_KEY_SEND="__pregel_send"`、`CONFIG_KEY_READ="__pregel_read"`、`CONFIG_KEY_CHECKPOINTER="__pregel_checkpointer"`、`CONFIG_KEY_STREAM="__pregel_stream"`、`CONFIG_KEY_THREAD_ID="thread_id"`、`CONFIG_KEY_CHECKPOINT_ID="checkpoint_id"`、`CONFIG_KEY_CHECKPOINT_NS="checkpoint_ns"`、`CONFIG_KEY_CHECKPOINT_MAP="checkpoint_map"`、`CONFIG_KEY_RUNTIME="__pregel_runtime"`（第33-71行）。

F-009: 命名空间分隔符 `NS_SEP = sys.intern("|")`，任务 ID 分隔符 `NS_END = sys.intern(":")`；`NULL_TASK_ID = "00000000-0000-0000-0000-000000000000"`；`OVERWRITE = "__overwrite__"`（第87-96行）。

F-010: `CONF = cast(Literal["configurable"], sys.intern("configurable"))`，RunnableConfig 中 configurable 字典的键名（第91行）。

F-011: `RESERVED` 集合包含所有保留的标签、写入键和配置键，用于在通道更新时跳过这些特殊键（第110-139行）。

## StateGraph 类（langgraph/graph/state.py）

F-012: `StateGraph(Generic[StateT, ContextT, InputT, OutputT])` 是构建器类，`__all__ = ("StateGraph", "CompiledStateGraph")`（第94行）。节点签名为 `State -> Partial<State>`，状态键可用 `Annotated[type, reducer]` 标注聚合函数，reducer 签名为 `(Value, Value) -> Value`（第131-139行）。

F-013: `StateGraph.__init__(self, state_schema, context_schema=None, *, input_schema=None, output_schema=None, **kwargs)` 初始化 `nodes={}`、`edges=set()`、`branches=defaultdict(dict)`、`schemas={}`、`channels={}`、`managed={}`、`compiled=False`、`waiting_edges=set()`。`input_schema` 默认为 `state_schema`，`output_schema` 默认为 `state_schema`（第216-270行）。

F-014: `set_node_defaults(*, retry_policy=None, cache_policy=None, error_handler=None, timeout=None)` 设置编译时应用于所有节点的默认策略，每节点值优先。`retry_policy` 和 `timeout` 也应用于错误处理器节点；`cache_policy` 和 `error_handler` 不应用于错误处理器节点（第272-335行）。

F-015: `add_node(node, action=None, *, defer=False, metadata=None, input_schema=None, retry_policy=None, cache_policy=None, error_handler=None, destinations=None, timeout=None, trace_policy=None, **kwargs)` 添加节点。节点名不能为 `END` 或 `START`，不能包含 `NS_SEP` 或 `NS_END` 字符。若提供 `error_handler`，自动创建名为 `__error_handler__{node}` 的处理器节点（第667-926行）。

F-016: `add_edge(start_key, end_key)` 支持单个起点或起点列表。单起点直接加入 `self.edges`；多起点加入 `self.waiting_edges`（集合元素为 `(tuple(starts), end)`）。`END` 不能作为起点，`START` 不能作为终点（第928-980行）。

F-017: `add_conditional_edges(source, path, path_map=None)` 将 `path` 强制转换为 Runnable，创建 `BranchSpec.from_path(path, path_map, True)` 并存入 `self.branches[source][name]`（第982-1030行）。

F-018: `add_sequence(nodes)` 按顺序添加节点并在相邻节点间添加边，空序列抛出 ValueError，重复节点名抛出 ValueError（第1032-1077行）。

F-019: `set_entry_point(key)` 等价于 `add_edge(START, key)`；`set_finish_point(key)` 等价于 `add_edge(key, END)`；`set_conditional_entry_point(path, path_map=None)` 等价于 `add_conditional_edges(START, path, path_map)`（第1079-1114行）。

F-020: `validate(interrupt=None)` 验证所有边的源节点和目标节点存在，必须有从 START 出发的入口边，设置 `self.compiled = True`（第1129-1175行）。

F-021: `compile(checkpointer=None, *, cache=None, store=None, interrupt_before=None, interrupt_after=None, debug=False, name=None, transformers=None)` 方法：调用 `ensure_valid_checkpointer` 验证 checkpointer；当 `_serde.STRICT_MSGPACK_ENABLED` 时构建 serde 允许列表；调用 `self.validate()`；确定 `output_channels` 和 `stream_channels`；应用 `_node_defaults` 到各节点 spec；创建 `CompiledStateGraph` 实例；附加 START 节点和所有用户节点；附加边、等待边和分支；返回 `compiled.validate()`（第1177-1401行）。

F-022: `CompiledStateGraph(Pregel[StateT, ContextT, InputT, OutputT], Generic[...])` 继承自 Pregel，包含 `builder`、`schema_to_mapper`、`_output_mapper`、`_state_mapper` 属性（第1404-1422行）。

F-023: `CompiledStateGraph.attach_node(key, node)` 为每个节点创建 `PregelNode`，触发通道为 `branch:to:{key}`，写入器包含 `ChannelWriteTupleEntry`（状态更新映射器 `_get_updates` 和控制分支映射器 `_control_branch`）。START 节点的触发通道为 `START`，使用 `EphemeralValue` 通道（第1444-1549行）。

F-024: `CompiledStateGraph.attach_edge(starts, end)` 单起点时为起点节点的 writers 追加 `ChannelWriteEntry(branch:to:{end}, None)`；多起点时创建 `NamedBarrierValue` 或 `NamedBarrierValueAfterFinish` 通道（通道名 `join:{'+'.join(starts)}:{end}`），将通道加入终点节点的 triggers 并为每个起点添加 writer（第1551-1575行）。

F-025: `CompiledStateGraph.attach_branch(start, name, branch, *, with_reader=True)` 创建 `ChannelRead.do_read` 读取器（带 mapper），将分支的 runnable 追加到起点节点的 writers（第1577-1624行）。

F-026: `CompiledStateGraph._migrate_checkpoint(checkpoint)` 支持从旧版检查点格式迁移：将 `start:node` 迁移为 `branch:to:node`，将 `branch:source:condition:node` 迁移为 `branch:to:node`，将裸节点名迁移为 `branch:to:node`（第1626-1729行）。

F-027: `_pick_mapper(state_keys, schema)` 当 `state_keys == ["__root__"]` 返回 None；当 schema 是 Pydantic BaseModel 子类或 dataclass 时返回 `partial(_coerce_state, schema)`；否则返回 None（第1732-1739行）。

F-028: `_control_branch(value)` 处理节点返回的 `Send` 和 `Command` 对象：`Send` 写入 `TASKS` 通道；`Command(goto=...)` 转换为 `branch:to:{target}` 写入；`Command(graph=Command.PARENT)` 抛出 `ParentCommand`（第1749-1775行）。

## MessageGraph 与消息处理（langgraph/graph/message.py）

F-029: `add_messages(left, right, *, format=None)` 合并两个消息列表，按 ID 去重/覆盖。为缺失 ID 的消息生成 `uuid4()`。`RemoveMessage` 可删除消息；`REMOVE_ALL_MESSAGES = "__remove_all__"` 清空列表。`format="langchain-openai"` 将消息转换为 OpenAI 格式。通过 `@_add_messages_wrapper` 装饰，支持无参数调用返回 partial（第60-244行）。

F-030: `MessageGraph(StateGraph)` 已弃用（v1.0.0，将在 v2.0.0 移除），其 `__init__` 调用 `super().__init__(Annotated[list[AnyMessage], add_messages])`（第312-369行）。

F-031: `MessagesState(TypedDict)` 定义 `messages: Annotated[list[AnyMessage], add_messages]`（第372-373行）。

F-032: `_messages_delta_reducer(state, writes)` 是用于 `DeltaChannel` 的批量 reducer，单次处理所有写入，按 ID 去重和 tombstone，要求批处理不变性 `reducer(reducer(state, xs), ys) == reducer(state, xs + ys)`（第247-309行）。

F-033: `push_message(message, *, state_key="messages")` 手动向 `messages` / `messages-tuple` 流模式写入消息，需要消息 ID，通过 `StreamMessagesHandler` 发射并通过 `CONFIG_KEY_SEND` 写入状态通道（第392-436行）。

## Channels 基类（langgraph/channels/base.py）

F-034: `BaseChannel(Generic[Value, Update, Checkpoint], ABC)` 是所有通道的基类，`__slots__ = ("key", "typ")`。抽象方法包括 `ValueType`（属性）、`UpdateType`（属性）、`from_checkpoint(checkpoint)`、`get()`、`update(values)`。具体方法包括 `copy()`、`checkpoint()`、`is_available()`、`consume()`、`finish()`（第19-121行）。

F-035: `checkpoint()` 默认返回 `self.get()`，空通道返回 `MISSING`；`consume()` 和 `finish()` 默认返回 False（第49-121行）。

## LastValue 通道（langgraph/channels/last_value.py）

F-036: `LastValue(Generic[Value], BaseChannel[Value, Value, Value])` 存储最后接收到的值，每步最多接收一个值。`update(values)` 当 `len(values) != 1` 时抛出 `InvalidUpdateError`（错误码 `INVALID_CONCURRENT_GRAPH_UPDATE`），否则取 `values[-1]`。`__eq__` 仅检查类型（第20-78行）。

F-037: `LastValueAfterFinish(Generic[Value], BaseChannel[Value, Value, tuple[Value, bool]])` 存储值但仅在 `finish()` 后可用，`consume()` 时清空值。用于 `defer=True` 的延迟节点（第81-151行）。

## Topic 通道（langgraph/channels/topic.py）

F-038: `Topic(Generic[Value], BaseChannel[Sequence[Value], Value | list[Value], list[Value]])` 是可配置的 PubSub 主题。构造参数 `accumulate: bool = False`，非累积模式每步清空值。`update(values)` 通过 `_flatten` 展平嵌套列表并 extend 到 `self.values`。`get()` 返回 `list(self.values)`，空时抛出 `EmptyChannelError`（第23-93行）。

## EphemeralValue 通道（langgraph/channels/ephemeral_value.py）

F-039: `EphemeralValue(Generic[Value], BaseChannel[Value, Value, Value])` 存储前一步接收到的值，之后清空。构造参数 `guard: bool = True`，`guard=True` 时每步最多接收一个值，否则取最后一个。无更新时（空序列）将值设为 `MISSING`（第15-79行）。

## NamedBarrierValue 通道（langgraph/channels/named_barrier_value.py）

F-040: `NamedBarrierValue(Generic[Value], BaseChannel[Value, Value, set[Value]])` 等待所有命名值到达后才使值可用。构造参数 `names: set[Value]`。`update(values)` 将值加入 `seen` 集合，值不在 `names` 中时抛出 `InvalidUpdateError`。`is_available()` 返回 `seen == names`。`consume()` 在全部到达后清空 `seen`（第13-81行）。

F-041: `NamedBarrierValueAfterFinish` 类似但额外要求 `finish()` 被调用后才可用，用于 `defer=True` 节点的多起点 join（第84-166行）。

## BinaryOperatorAggregate 通道（langgraph/channels/binop.py）

F-042: `BinaryOperatorAggregate(Generic[Value], BaseChannel[Value, Value, Value])` 通过二元运算符聚合值。构造参数 `typ` 和 `operator: Callable[[Value, Value], Value]`。初始化时尝试 `typ()` 创建空值，失败则设为 `MISSING`。`update(values)` 依次应用 operator，支持 `Overwrite` 值绕过 reducer 直接设置值（每步最多一个 Overwrite）（第65-155行）。

F-043: `_get_overwrite(value)` 识别三种 Overwrite 形式：`Overwrite` 实例、`{"__overwrite__": value}` 字典、`{"value": ..., "type": "__overwrite__"}` JSON 反序列化形式（第31-51行）。

F-044: `_operators_equal(a, b)` 比较两个 reducer 是否相等，lambda 函数因名称均为 `<lambda>` 而视为相等（第54-62行）。

## DeltaChannel（langgraph/channels/delta.py）

F-045: `DeltaChannel(Generic[Value], BaseChannel[Any, Any, Any])` 是 beta 功能，在检查点 blob 中仅存储哨兵值，通过重放祖先写入重建状态。reducer 签名为 `(state, list[writes]) -> new_state`，必须确定性和批处理不变性。构造参数 `reducer`、`typ=None`、`snapshot_frequency=1000`（第25-93行）。

F-046: `DeltaChannel.checkpoint()` 始终返回 `MISSING`；快照决策在 `create_checkpoint` 中根据通道版本号进行，写入 `_DeltaSnapshot(value)` 到 `channel_values`。非快照步骤通道不出现在 `channel_values` 中，重建时遍历祖先写入（第193-202行）。

F-047: `replay_writes(writes)` 从旧到新应用祖先写入，若存在 Overwrite 则以最后一个 Overwrite 为新基础，仅应用其后的写入（第139-157行）。

## Pregel 执行引擎（langgraph/pregel/main.py）

F-048: `Pregel(PregelProtocol[StateT, ContextT, InputT, OutputT], Generic[...])` 结合 actors 和 channels，按 BSP（Bulk Synchronous Parallel）模型组织执行。每步三阶段：Plan（确定执行哪些 actors）、Execution（并行执行）、Update（用写入更新通道）。重复直到无 actors 被选中或达到最大步数（第450-477行）。

F-049: `NodeBuilder` 提供流式 API 构建 PregelNode：`subscribe_only(channel)`、`subscribe_to(*channels, read=True)`、`read_from(*channels)`、`do(node)`、`write_to(*channels, **kwargs)`、`meta(*tags, **metadata)`、`add_retry_policies(*policies)`、`add_cache_policy(policy)`、`set_timeout(timeout)`、`build()`（第205-375行）。

F-050: Pregel 文档中列出的内建通道：`LastValue`（默认，存储最后值）、`Topic`（PubSub）、`Context`（上下文管理器值）、`BinaryOperatorAggregate`（二元运算符聚合）（第496-512行）。

## PregelLoop（langgraph/pregel/_loop.py）

F-051: `PregelLoop` 是同步和异步循环的基类，属性包括 `config`、`store`、`stream`、`step`、`stop`、`input`、`cache`、`checkpointer`、`nodes`、`specs`、`input_keys`、`output_keys`、`stream_keys`、`is_replaying`、`is_nested`、`interrupt_after`、`interrupt_before`、`durability`、`submit`、`channels`、`checkpoint`、`tasks`、`status` 等（第158-269行）。

F-052: `status` 字段类型为 `Literal["input", "pending", "done", "draining", "interrupt_before", "interrupt_after", "out_of_steps"]`（第256-264行）。

F-053: `DuplexStream(*streams)` 创建组合流，根据 `value[1]`（模式名）分发到匹配的流（第149-155行）。

F-054: `AsyncPregelLoop` 和 `SyncPregelLoop` 是具体实现，分别从 `pregel.main` 导入（第141-144行）。

## 算法函数（langgraph/pregel/_algo.py）

F-055: `should_interrupt(checkpoint, interrupt_nodes, tasks)` 检查是否应中断：自上次中断以来有任何通道更新，且任何触发节点在 `interrupt_nodes` 列表中（或 `"*"` 匹配所有非隐藏节点）（第155-185行）。

F-056: `local_read(scratchpad, channels, managed, task, select, fresh=False)` 注入到 `CONFIG_KEY_READ` 的函数，读取当前状态。`fresh=True` 时复制通道并仅应用该任务的写入，实现条件边读取节点局部写入后的状态（第188-224行）。

F-057: `increment(current, channel)` 是默认通道版本函数，`current + 1 if current is not None else 1`（第227-229行）。

F-058: `apply_writes(checkpoint, channels, tasks, get_next_version, trigger_to_nodes)` 按路径排序任务，更新 `versions_seen`，消费触发的通道（调用 `consume()`），按通道分组写入并调用 `channel.update(vals)`，对未更新通道调用 `update(EMPTY_SEQ)`，当无更新通道触发节点时调用所有通道的 `finish()`。返回更新的通道集合（第232-345行）。

F-059: `prepare_next_tasks(checkpoint, pending_writes, processes, channels, managed, config, step, stop, *, for_execution, ...)` 根据通道版本和 `versions_seen` 确定哪些节点应在下一步执行，创建 `PregelExecutableTask` 或 `PregelTask`（第348-399行）。

F-060: `PregelTaskWrites(NamedTuple)` 包含 `path`、`name`、`writes`、`triggers`，用于非任务来源的写入（图输入、update_state 等）（第110-117行）。

F-061: `Call` 类封装函数调用：`func`、`input`（args/kwargs 元组）、`retry_policy`、`cache_policy`、`callbacks`、`timeout`（第120-152行）。

## 执行器（langgraph/pregel/_executor.py）

F-062: `BackgroundExecutor(AbstractContextManager)` 使用线程池在后台运行同步任务，退出时取消标记 `__cancel_on_exit__=True` 的任务、等待所有任务完成、重新抛出标记 `__reraise_on_exit__=True` 的第一个异常。`submit` 支持 `__name__`、`__cancel_on_exit__`、`__reraise_on_exit__`、`__next_tick__` 参数（第40-120行）。

F-063: `AsyncBackgroundExecutor(AbstractAsyncContextManager)` 使用 asyncio 事件循环运行异步任务，支持 `max_concurrency` 信号量限流。`GraphBubbleUp` 异常被视为中断信号而非错误，不在退出时重新抛出（第122-211行）。

F-064: `Submit` 是 Protocol，定义 `__call__(fn, *args, __name__=None, __cancel_on_exit__=False, __reraise_on_exit__=True, __next_tick__=False, **kwargs) -> Future`（第27-37行）。

## PregelNode（langgraph/pregel/_read.py）

F-065: `PregelNode` 是 Pregel 图中的节点容器，属性包括 `channels`（str 或 list[str]）、`triggers`（list[str]）、`mapper`、`writers`（list[Runnable]）、`bound`（Runnable）、`retry_policy`、`cache_policy`、`timeout`、`tags`、`metadata`、`trace_policy`、`is_error_handler`、`error_handler_node`、`subgraphs`（第97-150行）。

F-066: `ChannelRead(RunnableCallable)` 实现从 `CONFIG_KEY_READ` 读取状态的逻辑，静态方法 `do_read(config, *, select, fresh=False, mapper=None)`（第25-91行）。

F-067: `DEFAULT_BOUND = RunnableCallable(lambda input: input)` 是默认的恒等绑定 runnable（第94行）。

## ChannelWrite（langgraph/pregel/_write.py）

F-068: `ChannelWriteEntry(NamedTuple)` 包含 `channel: str`、`value: Any = PASSTHROUGH`、`skip_none: bool = False`、`mapper: Callable | None = None`（第26-34行）。

F-069: `ChannelWriteTupleEntry(NamedTuple)` 包含 `mapper: Callable`、`value: Any = PASSTHROUGH`、`static: Sequence[tuple[str, Any, str | None]] | None = None`（第37-43行）。

F-070: `ChannelWrite(RunnableCallable)` 将写入通过 `CONFIG_KEY_SEND` 发送，静态方法 `do_write(config, writes, allow_passthrough=True)` 验证并组装写入。`SKIP_WRITE = object()`、`PASSTHROUGH = object()` 是哨兵值（第46-134行）。

## 配置（langgraph/_internal/_config.py）

F-071: `DEFAULT_RECURSION_LIMIT = int(getenv("LANGGRAPH_DEFAULT_RECURSION_LIMIT", "10007"))`（第32行）。

F-072: `DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT = int(getenv("LANGGRAPH_DELTA_MAX_SUPERSTEPS_SINCE_SNAPSHOT", "5000"))`（第33-35行）。

F-073: `recast_checkpoint_ns(ns)` 从检查点命名空间中移除任务 ID，用 `NS_SEP` 连接各部分中 `NS_END` 之前的内容，跳过纯数字部分（第38-49行）。

F-074: `patch_configurable(config, patch)` 在 config 的 `configurable` 字典中合并补丁（第52-60行）。

## 运行时配置（langgraph/config.py）

F-075: `get_config()` 从 `var_child_runnable_config` contextvar 获取当前 RunnableConfig，在 runnable 上下文外调用抛出 RuntimeError。Python < 3.11 在 async 上下文中使用会抛出 RuntimeError（第17-29行）。

F-076: `get_store()` 返回 `get_config()[CONF][CONFIG_KEY_RUNTIME].store`，需要在编译时提供 store（第32-123行）。

F-077: `get_stream_writer()` 返回 `runtime.stream_writer`，用于在节点内发射自定义流数据（第126-196行）。

## Runtime（langgraph/runtime.py）

F-078: `ExecutionInfo` 是 frozen dataclass（slots=True），包含 `checkpoint_id`、`checkpoint_ns`、`task_id`、`thread_id=None`、`run_id=None`、`node_attempt=1`、`node_first_attempt_time=None`，提供 `patch(**overrides)` 方法（第26-57行）。

F-079: `ServerInfo` 是 frozen dataclass，包含 `assistant_id`、`graph_id`、`user: BaseUser | None = None`（第60-76行）。

F-080: `RunControl` 提供协作式排空控制，`request_drain(reason="shutdown")` 设置排空原因，`drain_requested` 属性检查是否请求排空。线程安全（单属性写）（第79-104行）。

F-081: `Runtime(Generic[ContextT])` 是 dataclass（kw_only, slots, frozen），捆绑运行时上下文和工具：`context`、`store`、`stream_writer`、`previous`、`execution_info`、`server_info`、`control`。v0.6.0 新增（第124-150行）。

## 类型定义（langgraph/types.py）

F-082: `Durability = Literal["sync", "async", "exit"]`：sync 同步持久化、async 异步持久化、exit 仅退出时持久化（第89-95行）。

F-083: `All = Literal["*"]` 特殊值表示在所有节点中断（第97行）。

F-084: `Checkpointer = None | bool | BaseCheckpointSaver`：True 启用持久化、False 禁用、None 继承父图（第100-106行）。

F-085: `StreamMode = Literal["values", "updates", "checkpoints", "tasks", "debug", "messages", "custom"]`（第122-136行）。

F-086: `StreamWriter = Callable[[Any], None]` 接受单参数写入输出流（第138-141行）。

F-087: `RetryPolicy(NamedTuple)` 字段：`initial_interval=0.5`、`backoff_factor=2.0`、`max_interval=128.0`、`max_attempts=3`、`jitter=True`、`retry_on=default_retry_on`（第418-437行）。

F-088: `TimeoutPolicy` 是 frozen dataclass（kw_only, slots），字段：`run_timeout`（硬墙钟上限）、`idle_timeout`（无进度最大时间）、`refresh_on: Literal["auto", "heartbeat"] = "auto"`。提供 `coerce(value)` 类方法标准化输入（第451-514行）。

F-089: `CachePolicy(Generic[KeyFuncT])` 是 frozen dataclass，字段：`key_func=default_cache_key`、`ttl=None`（第520-529行）。

F-090: `TracePolicy` 是 frozen dataclass，字段：`process_inputs`、`process_outputs`，用于转换 trace 记录的输入/输出。`omit_payload(_value)` 返回空字典（第532-567行）。

F-091: `Interrupt` 是 final dataclass（slots），字段 `value: Any`、`id: str`。`from_ns(value, ns)` 类方法用 `xxh3_128_hexdigest` 从命名空间生成确定性 ID（第573-628行）。

F-092: `PregelTask(NamedTuple)` 包含 `id`、`name`、`path`、`error=None`、`interrupts=()`、`state=None`、`result=None`（第637-646行）。

F-093: `PregelExecutableTask` 是 dataclass（frozen, slots），字段：`name`、`input`、`proc`、`writes: deque`、`config`、`triggers`、`retry_policy`、`cache_key`、`id`、`path`、`writers=()`、`subgraphs=()`、`timeout=None`（第666-680行）。

F-094: `StateSnapshot(NamedTuple)` 包含 `values`、`next`、`config`、`metadata`、`created_at`、`parent_config`、`tasks`、`interrupts`（第683-701行）。

F-095: `Send` 类使用 `__slots__ = ("node", "arg", "timeout")`，构造签名 `Send(node, arg, *, timeout=None)`，实现 `__hash__`、`__eq__`、`__repr__`。用于条件边中动态调用节点并传入自定义状态（map-reduce 模式）（第704-792行）。

F-096: `Command(Generic[N], ToolOutputMixin)` 是 frozen dataclass（kw_only, slots），字段：`graph: str | None = None`、`update: Any | None = None`、`resume: dict | Any | None = None`、`goto: Send | Sequence[Send | N] | N = ()`。类常量 `PARENT = "__parent__"`。`_update_as_tuples()` 方法将 update 转换为 `(key, value)` 元组序列（第798-848行）。

F-097: `interrupt(value)` 函数通过 `CONFIG_KEY_SEND` 和 scratchpad 实现可恢复中断：首次调用抛出 `GraphInterrupt`，恢复时返回 resume 值。需要 checkpointer（第851-974行）。

F-098: `Overwrite` 是 dataclass（slots），包装值绕过 reducer 直接写入 `BinaryOperatorAggregate` 通道，同一步多个 Overwrite 抛出 `InvalidUpdateError`（第977-997行）。

## 错误体系（langgraph/errors.py）

F-099: `ErrorCode(Enum)` 包含 `GRAPH_RECURSION_LIMIT`、`INVALID_CONCURRENT_GRAPH_UPDATE`、`INVALID_GRAPH_NODE_RETURN_VALUE`、`MULTIPLE_SUBGRAPHS`、`INVALID_CHAT_HISTORY`（第34-39行）。

F-100: `create_error_message(*, message, error_code)` 附加故障排除 URL `https://docs.langchain.com/oss/python/langgraph/errors/{error_code.value}`（第42-47行）。

F-101: `GraphBubbleUp(Exception)` 是中断信号基类；`GraphDrained(GraphBubbleUp)` 表示协作排空（reason 默认 "shutdown"）；`GraphInterrupt(GraphBubbleUp)` 表示子图中断，对根图抑制；`ParentCommand(GraphBubbleUp)` 携带 Command 到父图（第50-133行）。

F-102: `GraphRecursionError(RecursionError)` 在达到最大步数时抛出，防止无限循环（第67-87行）。

F-103: `InvalidUpdateError(Exception)` 在通道更新无效时抛出（第90-99行）。

F-104: `NodeError` 是 frozen dataclass（slots），包含 `node: str` 和 `error: BaseException`，传递给节点级错误处理器（第148-165行）。

F-105: `NodeCancelledError(Exception)` 在节点自身抛出 `asyncio.CancelledError` 时使用，使其流经正常错误路径而非静默成功（第168-187行）。

F-106: `NodeTimeoutError(Exception)` 在节点调用超时（idle 或 run）时抛出，不继承内置 `TimeoutError`，字段包括 `node`、`timeout`、`run_timeout`、`idle_timeout`、`elapsed`、`kind`（第190-241行）。

## Checkpoint 基础（checkpoint/base/__init__.py）

F-107: `PendingWrite = tuple[str, str, Any]`，即 `(task_id, channel, value)`（第31行）。

F-108: `CheckpointMetadata(TypedDict, total=False)` 包含 `source: Literal["input", "loop", "update", "fork"]`、`step: int`、`parents: dict[str, str]`、`run_id: str`、`counters_since_delta_snapshot: dict[str, tuple[int, int]]`（第38-86行）。

F-109: `ChannelVersions = dict[str, str | int | float]`（第89行）。

F-110: `Checkpoint(TypedDict)` 包含 `v: int`（当前版本1）、`id: str`（唯一且单调递增）、`ts: str`（ISO 8601）、`channel_values: dict[str, Any]`、`channel_versions: ChannelVersions`、`versions_seen: dict[str, ChannelVersions]`、`updated_channels: list[str] | None`（第92-123行）。

F-111: `CheckpointTuple(NamedTuple)` 包含 `config`、`checkpoint`、`metadata`、`parent_config=None`、`pending_writes=None`（第139-146行）。

F-112: `DeltaChannelHistory(TypedDict)` 包含 `writes: list[PendingWrite]` 和可选 `seed: Any`，用于 DeltaChannel 重建（第149-173行）。

F-113: `BaseCheckpointSaver(Generic[V])` 是检查点保存器基类，使用 `thread_id` 作为主键存储和检索检查点。需要在 config 中传 `thread_id`（第176-199行）。

F-114: `copy_checkpoint(checkpoint)` 创建检查点的浅拷贝，复制 `channel_values`、`channel_versions`、`versions_seen`、`pending_sends`、`updated_channels`（第126-136行）。

## UUID6（checkpoint/base/id.py）

F-115: `uuid6(node=None, clock_seq=None)` 生成 UUIDv6，基于 100 纳秒时间戳，当时间戳不大于上次时自动加1保证单调性。使用随机 48 位 node 和 14 位 clock_seq（第79-109行）。

F-116: `UUID(uuid.UUID)` 子类支持版本 6-8，重写 `time` 属性处理 v6/v7/v8 的时间戳解码（第15-72行）。

## 序列化（checkpoint/serde/base.py）

F-117: `SerializerProtocol(Protocol)` 是 runtime_checkable 协议，定义 `dumps_typed(obj) -> tuple[str, bytes]` 和 `loads_typed(data: tuple[str, bytes]) -> Any`（第14-26行）。

F-118: `UntypedSerializerProtocol(Protocol)` 定义 `dumps(obj) -> bytes` 和 `loads(data) -> Any`（第6-11行）。

F-119: `SerializerCompat` 将旧式无类型序列化器包装为 `SerializerProtocol`，`dumps_typed` 使用 `type(obj).__name__` 作为类型标签（第29-37行）。

F-120: `maybe_add_typed_methods(serde)` 检查 serde 是否已是 `SerializerProtocol`，否则包装为 `SerializerCompat`（第40-48行）。

F-121: `CipherProtocol(Protocol)` 定义 `encrypt(plaintext) -> tuple[str, bytes]` 和 `decrypt(ciphername, ciphertext) -> bytes`（第51-63行）。

## JsonPlusSerializer（checkpoint/serde/jsonplus.py）

F-122: `JsonPlusSerializer(SerializerProtocol)` 使用 ormsgpack 序列化，带可选回退。安全提示：不应在不可信 Python 对象上使用，`LANGGRAPH_STRICT_MSGPACK=true` 环境变量限制反序列化为内置安全类型允许列表（第82-100行）。

F-123: `LC_REVIVER = Reviver(allowed_objects="core")` 使用 langchain_core 的 Reviver 反序列化 LangChain 对象（第47行）。

## Store 基础（store/base/__init__.py）

F-124: `BaseStore` 提供长期记忆，跨线程和对话持久化，支持分层命名空间、键值存储和可选向量搜索。核心类型包括 `BaseStore`、`Item`、`Op`（Get/Put/Search/List 操作）（第1-10行）。

F-125: `Item` 类使用 `__slots__ = ("value", "key", "namespace", "created_at", "updated_at")`，`value` 为字典，`namespace` 为字符串元组（第51-100行）。

## 批量 Store（store/base/batch.py）

F-126: `AsyncBatchedBaseStore(BaseStore)` 在后台任务中高效批量操作，使用 `asyncio.Queue` 提交操作，`_check_loop` 装饰器检测在主事件循环中同步调用并抛出 `InvalidStateError`，建议使用异步接口（第58-100行）。

## _internal/_runnable.py

F-127: 该模块定义 LangGraph 自己的 `Runnable`、`RunnableLike`、`RunnableSeq`、`RunnableCallable` 类型和 `coerce_to_runnable` 函数，从 langchain_core 重新导出 Runnable 相关类（第29-67行）。

F-128: `_trace_payload(value, transform)` 在 trace 时转换值，transform 为 None 时直通；transform 抛出异常时记录未转换值（第70-85行）。
