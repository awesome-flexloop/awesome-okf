---
type: reference
scope: deepagents
name: api
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents 核心 API 参考——create_deep_agent、DeepAgentState 及公共导出
---

# 核心 API 参考

## `create_deep_agent()`

**模块路径**：`deepagents.graph.create_deep_agent`

`create_deep_agent()` 是 Deep Agents 的唯一组装入口。它不引入新的运行时，而是解析模型和后端、组装中间件栈、构建子代理、组合系统提示，最终委托给 `langchain.agents.create_agent()` 生成标准的 `CompiledStateGraph`。

### 函数签名

```python
def create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: Sequence[SubAgent | CompiledSubAgent | AsyncSubAgent] | None = None,
    skills: list[str] | None = None,
    memory: list[str] | None = None,
    permissions: list[FilesystemPermission] | None = None,
    backend: BackendProtocol | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    response_format: ResponseFormat | type | dict[str, Any] | None = None,
    state_schema: type[DeepAgentState] | None = None,
    context_schema: type | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
) -> CompiledStateGraph
```

### 参数说明

| 参数 | 类型 | 说明 |
|---|---|---|
| `model` | `str \| BaseChatModel \| None` | 模型，支持 `provider:model` 字符串（如 `"openai:gpt-5.5"`）或预初始化的 `BaseChatModel` 实例。`None` 已弃用 |
| `tools` | `Sequence` | 额外工具，与内置工具集合并（加法式，不移除内置工具） |
| `system_prompt` | `str \| SystemMessage` | 调用者编写的系统指令，位于最终提示的 `USER` 部分 |
| `middleware` | `Sequence[AgentMiddleware]` | 自定义中间件，插入在基础栈之后、尾部栈之前 |
| `subagents` | `Sequence` | 子代理规格，支持 `SubAgent`、`CompiledSubAgent`、`AsyncSubAgent` |
| `skills` | `list[str]` | 技能源路径列表（POSIX 格式，相对于后端根目录） |
| `memory` | `list[str]` | 内存文件路径列表（AGENTS.md 文件） |
| `permissions` | `list[FilesystemPermission]` | 文件系统权限规则，首匹配优先 |
| `backend` | `BackendProtocol` | 文件存储和执行后端，默认 `StateBackend()` |
| `interrupt_on` | `dict` | 工具名到中断配置的映射，用于人工审批 |
| `response_format` | `ResponseFormat` | 结构化输出格式 |
| `state_schema` | `type[DeepAgentState]` | 自定义状态模式，必须是 `DeepAgentState` 的子类 |
| `checkpointer` | `Checkpointer` | 持久化代理状态的检查点器 |
| `store` | `BaseStore` | 持久化存储（`StoreBackend` 时必需） |

### 默认内置工具

- `ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`：文件操作
- `execute`：运行 shell 命令（仅沙箱后端可用）
- `task`：调用子代理

### 返回值

返回配置好的 `CompiledStateGraph`，通过 `.with_config()` 设置了 `recursion_limit: 9999` 和元数据 `ls_integration: "deepagents"`。

### 构造流程

1. 解析模型（`resolve_model`）并确定适用的 harness profile
2. 验证 profile 的 `excluded_middleware` 不包含必需脚手架
3. 处理调用者提供的子代理（区分异步/编译/声明式三种形态）
4. 自动添加默认 `general-purpose` 子代理（除非 profile 禁用）
5. 组装主代理中间件栈
6. 应用 profile 排除和自定义中间件合并
7. 组合最终系统提示（`USER` → `BASE` → `SUFFIX`）
8. 委托给 `langchain.agents.create_agent()`

## `DeepAgentState`

**模块路径**：`deepagents.graph.DeepAgentState`

```python
class DeepAgentState(AgentState):
    messages: Required[Annotated[list[AnyMessage], DeltaChannel(_messages_delta_reducer, snapshot_frequency=50)]]
```

继承自 LangChain 的 `AgentState`，核心差异是 `messages` 字段使用 `DeltaChannel` 减速器，将长线程的检查点增长从 O(N²) 降至 O(N)。每50条消息生成一次快照，中间以增量存储。

自定义状态模式必须继承 `DeepAgentState` 以保留 `DeltaChannel` 减速器：

```python
from deepagents.graph import DeepAgentState

class MyState(DeepAgentState):
    page_url: str
    file_urls: list[str]

agent = create_deepagent(model=..., state_schema=MyState)
```

## 公共导出（`deepagents/__init__.py`）

| 符号 | 类型 | 来源模块 |
|---|---|---|
| `create_deep_agent` | 函数 | `deepagents.graph` |
| `DeepAgentState` | 类 | `deepagents.graph` |
| `SubAgent` | TypedDict | `deepagents.middleware.subagents` |
| `CompiledSubAgent` | TypedDict | `deepagents.middleware.subagents` |
| `SubAgentMiddleware` | 类 | `deepagents.middleware.subagents` |
| `AsyncSubAgent` | TypedDict | `deepagents.middleware.async_subagents` |
| `AsyncSubAgentMiddleware` | 类 | `deepagents.middleware.async_subagents` |
| `FilesystemMiddleware` | 类 | `deepagents.middleware.filesystem` |
| `FilesystemPermission` | 类 | `deepagents.middleware.filesystem` |
| `FsToolName` | 类型 | `deepagents.middleware.filesystem` |
| `MemoryMiddleware` | 类 | `deepagents.middleware.memory` |
| `RubricMiddleware` | 类 | `deepagents.middleware.rubric` |
| `HarnessProfile` | 类 | `deepagents.profiles.harness` |
| `HarnessProfileConfig` | 类 | `deepagents.profiles.harness` |
| `GeneralPurposeSubagentProfile` | dataclass | `deepagents.profiles.harness` |
| `register_harness_profile` | 函数 | `deepagents.profiles.harness` |
| `ProviderProfile` | 类 | `deepagents.profiles.provider` |
| `register_provider_profile` | 函数 | `deepagents.profiles.provider` |
| `__version__` | 字符串 | `deepagents._version`（当前 `0.7.8`） |

## 版本信息

- **SDK 版本**：`0.7.8`
- **Python 要求**：`>=3.11,<4.0`
- **核心依赖**：`langchain>=1.3.16`、`langchain-core>=1.6.0`、`langchain-anthropic>=1.6.1`、`langsmith>=0.11.1`、`wcmatch>=11.0`
- **许可证**：MIT

## 相关概念

- [中间件栈](/langchain-ai/deepagents/references/middleware-stack) — 了解中间件排序和自定义规则
- [后端系统](/langchain-ai/deepagents/references/backends) — 了解可插拔存储后端
- [规划与子代理](/langchain-ai/deepagents/concepts/planning-subagents) — 了解子代理架构
