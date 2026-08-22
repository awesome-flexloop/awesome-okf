# langchain-core 事实清单

> 源码根：`d:/spaces/SpecWeave/external/libs/ai/langchain-ai/langchain/libs/core/langchain_core/`
> 版本：`version.py` 第1行 `VERSION = "1.6.1"`。
> 事实编号 F-lc-xxx，零推测；每条含文件相对路径与行号。

## 项目元信息

F-lc-001: 文件 `version.py` 第1行，常量 `VERSION = "1.6.1"`。

F-lc-002: 文件 `load/serializable.py` 第106行，类 `Serializable(BaseModel, ABC)`。第138-149行类方法 `is_lc_serializable(cls) -> bool` 默认返回 `False`。第151-175行类方法 `get_lc_namespace(cls) -> list[str]` 默认返回 `cls.__module__.split(".")`。第177-183行属性 `lc_secrets` 默认返回 `{}`。第185-193行属性 `lc_attributes` 默认返回 `{}`。第195-213行类方法 `lc_id(cls) -> list[str]` 返回 `[*cls.get_lc_namespace(), original_name]`，其中 `original_name` 取自 `cls.__pydantic_generic_metadata__["origin"].__name__` 或 `cls.__name__`。第215-217行 `model_config = ConfigDict(extra="ignore")`。第227行方法 `to_json(self) -> SerializedConstructor | SerializedNotImplemented`。

F-lc-003: 文件 `load/serializable.py` 第21-50行定义 TypedDict：`BaseSerialized`（含 `lc` 字段，值为 `1`）、`SerializedConstructor(BaseSerialized)`（含 `type: Literal["constructor"]`、`id: list[str]`、`kwargs: dict`）、`SerializedSecret(BaseSerialized)`（含 `type: Literal["secret"]`）、`SerializedNotImplemented(BaseSerialized)`（含 `type: Literal["not_implemented"]`）。

## Runnable 协议（runnables/base.py）

F-lc-004: 文件 `runnables/base.py` 第133行，抽象基类 `Runnable(ABC, Generic[Input, Output])`。第130行模块常量 `_RUNNABLE_GENERIC_NUM_ARGS = 2`。

F-lc-005: 文件 `runnables/base.py` 第270行，方法 `get_name(self, suffix: str | None = None, *, name: str | None = None) -> str`。第308-309行属性 `InputType`，第343-344行属性 `OutputType`。第374-375行属性 `input_schema`（返回 `TypeBaseModel`），第379行方法 `get_input_schema(self, config: RunnableConfig | None = None) -> TypeBaseModel`，第420行方法 `get_input_jsonschema`。第450-451行属性 `output_schema`，第458行方法 `get_output_schema`，第499行方法 `get_output_jsonschema`。第529-530行属性 `config_specs`，第534行方法 `config_schema(self, *, include: Sequence[str] | None = None) -> type[BaseModel]`，第577行方法 `get_config_jsonschema`。第593行方法 `get_graph(self, config: RunnableConfig | None = None) -> Graph`。第614行方法 `get_prompts`。

F-lc-006: 文件 `runnables/base.py` 第628-724行，运算符重载 `__or__`/`__ror__`（多个 overload）支持将 `Runnable`、字典、可调用对象通过 `|` 组合。第724行方法 `pipe(self, *others: Any) -> Runnable[Any, Other]`。第773行方法 `pick(self, keys: str | list[str]) -> RunnableSerializable[Any, Any]`。第836行方法 `assign(self, **kwargs: Runnable[Input, Any] | Callable[[Input], Any] | Any) -> RunnableSerializable[Input, dict[str, Any]]`。

F-lc-007: 文件 `runnables/base.py` 第885-890行抽象方法 `invoke(self, input: Input, config: RunnableConfig | None = None, **kwargs: Any) -> Output`。第907-928行 `async def ainvoke(...)` 默认实现 `return await run_in_executor(config, self.invoke, input, config, **kwargs)`。

F-lc-008: 文件 `runnables/base.py` 第930-978行方法 `batch(self, inputs: list[Input], config: RunnableConfig | list[RunnableConfig] | None = None, *, return_exceptions: bool = False, **kwargs: Any | None) -> list[Output]`，默认实现通过 `get_executor_for_config` 在线程池中并行调用 `invoke`；当 `len(inputs) == 1` 时不使用线程池。第982-1001行 `batch_as_completed` 含多个 overload。

F-lc-009: 文件 `runnables/base.py` 第1193-1212行方法 `stream(self, input: Input, config: RunnableConfig | None = None, **kwargs: Any | None) -> Iterator[Output]`，默认实现 `yield self.invoke(input, config, **kwargs)`。第1214-1233行 `async def astream(...)` 默认 `yield await self.ainvoke(...)`。

F-lc-010: 文件 `runnables/base.py` 第1237-1250行 `astream_log` overload（`diff: Literal[True] = True` 返回 `AsyncIterator[RunLogPatch]`）；第1253-1267行 overload（`diff: Literal[False]` 返回 `AsyncIterator[RunLog]`）。第1343-1368行 `astream_events` 多个 overload，支持 `version: Literal["v1", "v2"]`。第1674-1699行同步 `stream_events` 多个 overload。

F-lc-011: 文件 `runnables/base.py` 第1760行方法 `transform(self, input: Iterator[Input], config: RunnableConfig | None = None, **kwargs: Any | None) -> Iterator[Output]`。第1851行方法 `bind(self, **kwargs: Any) -> Runnable[Input, Output]`。第1885行方法 `with_config(self, config: RunnableConfig | None = None, **kwargs: Any) -> Runnable[Input, Output]`。第1910行 `with_listeners`，第1982行 `with_alisteners`。第2079行 `with_types(self, *, input_type: type | None = None, output_type: type | None = None) -> Runnable[Input, Output]`。第2101行 `with_retry(...)`。第2165行 `map(self) -> Runnable[Sequence[Input], list[Output]]`。第2188行 `with_fallbacks(self, handlers, *, exception_key=...) -> RunnableWithFallbacksT[Input, Output]`。

F-lc-012: 文件 `runnables/base.py` 第2707-2824行，`@beta_decorator.beta(...)` 装饰的方法 `as_tool(self, args_schema: type[BaseModel] | None = None, *, name: str | None = None, description: str | None = None, arg_types: dict[str, type] | None = None) -> BaseTool`，内部调用 `convert_runnable_to_tool(self, args_schema=args_schema, name=name, description=description, arg_types=arg_types)`（第2816-2824行，从 `langchain_core.tools` 延迟导入）。

F-lc-013: 文件 `runnables/base.py` 第2827行，类 `RunnableSerializable(Serializable, Runnable[Input, Output])`。第2843行方法 `to_json(self)`。第2855行 `configurable_fields(self, **kwargs: Any) -> RunnableSerializable[Input, Output]`。第2913行 `configurable_alternatives(self, which: ConfigurableField, *, default_key: str = "default", **kwargs: Runnable | Callable[..., Runnable]) -> RunnableSerializable[Input, Output]`。

F-lc-014: 文件 `runnables/base.py` 第3075行，类 `RunnableSequence(RunnableSerializable[Input, Output])`。第3169行 `__init__(self, *steps: Runnable[Any, Any] | Callable[[Any], Any] | Mapping[str, Any | Runnable[Any, Any] | Callable[[Any], Any]], name: str | None = None, first: RunnableLike | None = None, last: RunnableLike | None = None, middle: Sequence[RunnableLike] = ())`。第3220-3221行属性 `steps` 返回 `list[Runnable[Any, Any]]`。第3230-3231行 `is_lc_serializable` 返回 `True`。第3292行 `get_graph`。第3430行 `invoke`，第3506行 `batch`，第3764行 `_transform`，第3813行 `transform`，第3827行 `stream`。

F-lc-015: 文件 `runnables/base.py` 第3864行，类 `RunnableParallel(RunnableSerializable[Input, dict[str, Any]])`。第3950行 `__init__(self, _steps_: Mapping[str, Runnable | Callable | Any] | None = None, **kwargs: Runnable | Callable | Any)`。第3977-3978行 `is_lc_serializable` 返回 `True`。第4092行 `get_graph`。第4139行 `invoke`，第4253行 `_transform`，第4300行 `transform`，第4311行 `stream`。

F-lc-016: 文件 `runnables/base.py` 第4399行，类 `RunnableGenerator(Runnable[Input, Output])`。第4631行 `transform`，第4649行 `stream`，第4658行 `invoke`，第4667行 `atransform`，第4682行 `astream`。

F-lc-017: 文件 `runnables/base.py` 第4703行，类 `RunnableLambda(Runnable[Input, Output])`。第4959-4961行属性 `InputType`，第5017-5019行属性 `OutputType`。第5069行属性 `deps` 返回 `list[Runnable[Any, Any]]`。第5156行 `_invoke`，第5302行 `invoke`，第5357行 `_transform`，第5420行 `transform`，第5441行 `stream`。

F-lc-018: 文件 `runnables/base.py` 第5577行，类 `RunnableEachBase(RunnableSerializable[Sequence[Input], list[Output]])`。第5734行，类 `RunnableEach(RunnableEachBase[Input, Output])`。

F-lc-019: 文件 `runnables/base.py` 第5851行，类 `RunnableBindingBase(RunnableSerializable[Input, Output])`。第5898行 `__init__(self, *, bound: Runnable[Input, Output], kwargs: Mapping[str, Any] | None = None, config: RunnableConfig | None = None, **other_kwargs: Any)`。第5948-5950行属性 `InputType`，第5957-5959行属性 `OutputType`。

## Runnable 配置（runnables/config.py）

F-lc-020: 文件 `runnables/config.py` 第57行，`class RunnableConfig(TypedDict, total=False)`，字段：第80行 `tags: list[str]`、第86行 `metadata: dict[str, Any]`、第92行 `callbacks: Callbacks`、第98行 `run_name: str`、第103行 `max_concurrency: int | None`、第109行 `recursion_limit: int`、第115行 `configurable: dict[str, Any]`、第124行 `run_id: uuid.UUID | None`。第131-140行 `CONFIG_KEYS` 列表含这8个键。第171行 `DEFAULT_RECURSION_LIMIT = 25`。第174行 `var_child_runnable_config: ContextVar[RunnableConfig | None] = ContextVar("child_runnable_config", default=None)`。

F-lc-021: 文件 `runnables/config.py` 第255行函数 `ensure_config(config: RunnableConfig | None = None) -> RunnableConfig`；第311行 `get_config_list(config, length: int) -> list[RunnableConfig]`；第357行 `patch_config(config, *, callbacks=None, copy_local_ts=False, deep_check_ctx=True, **kwargs) -> RunnableConfig`；第431行 `merge_configs(*configs: RunnableConfig | None) -> RunnableConfig`。

## Messages（messages/）

F-lc-022: 文件 `messages/base.py` 第47行，类 `TextAccessor(str)`。第64行 `__new__(cls, value: str) -> Self`。第68-90行 `__call__(self) -> str`，调用时发出 `warn_deprecated(since="1.0.0", removal="2.0.0")` 弃用警告，提示使用 `.text` 属性而非 `.text()` 方法。

F-lc-023: 文件 `messages/base.py` 第93行，类 `BaseMessage(Serializable)`。第103行字段 `content: str | list[str | dict[Any, Any]]`。第106行 `additional_kwargs: dict[Any, Any] = Field(default_factory=dict)`。第114行 `response_metadata: dict[Any, Any] = Field(default_factory=dict)`。第117行字段 `type: str`。第125行 `name: str | None = None`。第135行 `id: str | None = Field(default=None, coerce_numbers_to_str=True)`。第142-144行 `model_config = ConfigDict(extra="allow")`。第181-188行 `is_lc_serializable` 返回 `True`。第190-197行 `get_lc_namespace` 返回 `["langchain", "schema", "messages"]`。第199-200行属性 `content_blocks` 返回 `list[types.ContentBlock]`。第262-263行属性 `text` 返回 `TextAccessor`。第294行 `__add__(self, other: Any) -> ChatPromptTemplate`。第309行 `pretty_repr(self, html: bool = False) -> str`，第344行 `pretty_print(self) -> None`。

F-lc-024: 文件 `messages/base.py` 第409行，类 `BaseMessageChunk(BaseMessage)`。第412行 `__add__(self, other: Any) -> BaseMessageChunk`（抽象）。

F-lc-025: 文件 `messages/human.py` 第9行类 `HumanMessage(BaseMessage)`，`type` 为 `"human"`；第63行类 `HumanMessageChunk(HumanMessage, BaseMessageChunk)`。

F-lc-026: 文件 `messages/system.py` 第9行类 `SystemMessage(BaseMessage)`，`type` 为 `"system"`；第63行类 `SystemMessageChunk(SystemMessage, BaseMessageChunk)`。

F-lc-027: 文件 `messages/ai.py` 第38行 `class InputTokenDetails(TypedDict, total=False)`；第74行 `class OutputTokenDetails(TypedDict, total=False)`；第104行 `class UsageMetadata(TypedDict)`，字段第138行 `input_tokens: int`、第141行 `output_tokens: int`、第144行 `total_tokens: int`、第147行 `input_token_details: NotRequired[InputTokenDetails]`、第153行 `output_token_details: NotRequired[OutputTokenDetails]`。

F-lc-028: 文件 `messages/ai.py` 第160行，类 `AIMessage(BaseMessage)`。第170行 `tool_calls: list[ToolCall] = Field(default_factory=list)`。第173行 `invalid_tool_calls: list[InvalidToolCall] = Field(default_factory=list)`。第176行 `usage_metadata: UsageMetadata | None = None`。第182行 `type: Literal["ai"] = "ai"`。第230-240行属性 `lc_attributes` 返回 `{"tool_calls": self.tool_calls, "invalid_tool_calls": self.invalid_tool_calls}`。第418行类 `AIMessageChunk(AIMessage, BaseMessageChunk)`。第509行方法 `init_tool_calls(self) -> Self`，第604行 `init_server_tool_calls(self) -> Self`。第633-642行 `__add__` 多个 overload。

F-lc-029: 文件 `messages/tool.py` 第16行，类 `ToolOutputMixin`（无方法体，文档说明工具可直接返回该 mixin 实例）。第26行类 `ToolMessage(BaseMessage, ToolOutputMixin)`。第67行字段 `tool_call_id: str`。第70行 `type: Literal["tool"] = "tool"`。第73行 `artifact: Any = None`。第81行 `status: Literal["success", "error"] = "success"`。第90-133行 `@model_validator(mode="before")` 类方法 `coerce_args`，将 tuple content 转 list、非 str/list content 转 str、将 UUID/int/float 类型的 `tool_call_id` 转 str。第174行类 `ToolMessageChunk(ToolMessage, BaseMessageChunk)`，第180行 `type: Literal["ToolMessageChunk"] = "ToolMessageChunk"`。

F-lc-030: 文件 `messages/tool.py` 第206行，`class ToolCall(TypedDict)`：第225行 `name: str`、第228行 `args: dict[str, Any]`、第231行 `id: str | None`、第238行 `type: NotRequired[Literal["tool_call"]]`。第242-258行工厂函数 `tool_call(*, name: str, args: dict[str, Any], id: str | None) -> ToolCall`，返回 `ToolCall(name=name, args=args, id=id, type="tool_call")`。第261行 `class ToolCallChunk(TypedDict)`。

F-lc-031: 文件 `messages/content.py` 第844-851行，类型别名 `ContentBlock = TextContentBlock | InvalidToolCall | ReasoningContentBlock | NonStandardContentBlock | DataContentBlock | ToolContentBlock`。第831-838行 `DataContentBlock = ImageContentBlock | VideoContentBlock | AudioContentBlock | PlainTextContentBlock | FileContentBlock`。第840-842行 `ToolContentBlock = ToolCall | ToolCallChunk | ServerToolCall | ServerToolCallChunk | ServerToolResult`。第855行 `KNOWN_BLOCK_TYPES` 集合含 `"text"`、`"reasoning"`、`"tool_call"`、`"invalid_tool_call"`、`"tool_call_chunk"`、`"image"`、`"audio"`、`"file"`、`"text-plain"`、`"video"` 等。

F-lc-032: 文件 `messages/utils.py` 第86行，类型别名 `AnyMessage = Annotated[...]`（消息联合类型）。

## Tools（tools/）

F-lc-033: 文件 `tools/base.py` 第89行异常类 `SchemaAnnotationError(TypeError)`。第371行异常类 `ToolException(Exception)`。第253行内部类 `_SchemaConfig`。

F-lc-034: 文件 `tools/base.py` 第433行，抽象基类 `BaseTool(RunnableSerializable[str | dict[str, Any] | ToolCall, Any])`。第474行字段 `name: str`。第477行 `description: str`。第483-485行 `args_schema: Annotated[ArgsSchema | None, SkipValidation()] = Field(default=None, description="The tool schema.")`。第495行 `return_direct: bool = False`。第502行 `verbose: bool = False`。第505行 `callbacks: Callbacks = Field(default=None, exclude=True)`。第508行 `tags: list[str] | None = None`。第518行 `metadata: dict[str, Any] | None = None`。第527-529行 `handle_tool_error: bool | str | Callable[[ToolException], ToolExceptionHandlerOutput] | None = False`。第542-544行 `handle_validation_error: bool | str | Callable[[ValidationError | ValidationErrorV1], str] | None = False`。第547行 `response_format: Literal["content", "content_and_artifact"] = "content"`。第555行 `extras: dict[str, Any] | None = None`。第593-595行 `model_config = ConfigDict(arbitrary_types_allowed=True)`。

F-lc-035: 文件 `tools/base.py` 第597-598行属性 `is_single_input -> bool`。第607-608行属性 `args -> dict[str, Any]`。第676-677行属性 `tool_call_schema -> ArgsSchema`。第741行方法 `get_input_schema(self, config: RunnableConfig | None = None) -> TypeBaseModel`。第757行方法 `invoke(self, input: Union[str, dict], config: RunnableConfig | None = None, **kwargs: Any) -> Any`。第778行方法 `_parse_input(self, input: Union[str, dict, ToolCall], *, suppress_args_stripping: bool = False) -> Tuple[dict[str, Any], dict[str, Any]]`。第908-909行抽象方法 `_run(self, *args: Any, **kwargs: Any) -> Any`。第1009行方法 `run(self, *args: Any, **kwargs: Any) -> Any`。

F-lc-036: 文件 `tools/base.py` 第1726行类 `InjectedToolArg`（标记注入参数）；第1756行类 `InjectedToolCallId(InjectedToolArg)`；第1734行类 `_DirectlyInjectedToolArg`。

F-lc-037: 文件 `tools/base.py` 第1935行抽象基类 `BaseToolkit(BaseModel, ABC)`。第1942-1943行抽象方法 `get_tools(self) -> list[BaseTool]`。

F-lc-038: 文件 `tools/structured.py` 第40行类 `StructuredTool(BaseTool)`。第43行 `description: str = ""`。第45-47行 `args_schema: Annotated[ArgsSchema, SkipValidation()] = Field(..., description="The tool schema.")`（必填）。第50行 `func: Callable[..., Any] | None = None`。第53行 `coroutine: Callable[..., Awaitable[Any]] | None = None`。第74-99行方法 `_run(self, *args, config: RunnableConfig, run_manager: CallbackManagerForToolRun | None = None, **kwargs) -> Any`，调用 `self.func(*args, **kwargs)`，若函数签名含 `callbacks` 则注入 `run_manager.get_child()`，若含 config 参数则注入 config。第132-133行类方法 `from_function(...)`。

F-lc-039: 文件 `tools/convert.py` 第77-89行函数 `tool(name_or_callable: str | Callable[..., Any] | None = None, runnable: Runnable[Any, Any] | None = None, *args, description: str | None = None, return_direct: bool = False, args_schema: ArgsSchema | None = None, infer_schema: bool = True, response_format: Literal["content", "content_and_artifact"] = "content", parse_docstring: bool = False, error_on_invalid_docstring: bool = True, extras: dict[str, Any] | None = None) -> BaseTool | Callable[...]`。第18-74行含4个 overload（无参装饰器、name+runnable、直接传 callable、name 作为装饰器工厂）。

F-lc-040: 文件 `tools/__init__.py` 第42-62行 `__all__` 导出：`BaseTool`、`StructuredTool`、`Tool`、`BaseToolkit`、`ToolException`、`SchemaAnnotationError`、`InjectedToolArg`、`InjectedToolCallId`、`tool`、`convert_runnable_to_tool`、`create_retriever_tool`、`render_text_description`、`render_text_description_and_args`、`ToolsRenderer`、`RetrieverInput`、`ArgsSchema`、`FILTERED_ARGS`、`create_schema_from_function`、`_get_runnable_config_param`。使用第64-84行 `_dynamic_imports` 懒加载。

## Prompts（prompts/）

F-lc-041: 文件 `prompts/base.py` 第38-40行抽象基类 `BasePromptTemplate(RunnableSerializable[dict[str, Any], PromptValue], ABC, Generic[FormatOutputType])`。第43行字段 `input_variables: list[str]`。第48行 `optional_variables: list[str] = Field(default=[])`。第55行 `input_types: dict[str, Any] = Field(default_factory=dict, exclude=True)`。第64行 `output_parser: BaseOutputParser | None = None`。第67行 `partial_variables: Mapping[str, Any] = Field(default_factory=dict)`。第74行 `metadata: dict[str, Any] | None = None`。第77行 `tags: list[str] | None = None`。第80-106行 `@model_validator(mode="after")` 方法 `validate_variable_names`，禁止 `input_variables` 或 `partial_variables` 含 `"stop"`，禁止两者重叠。第108-115行 `get_lc_namespace` 返回 `["langchain", "schema", "prompt_template"]`。第117-120行 `is_lc_serializable` 返回 `True`。第133-137行属性 `OutputType` 返回 `StringPromptValue | ChatPromptValueConcrete`。

F-lc-042: 文件 `prompts/base.py` 第210行方法 `invoke(self, input: dict, config: RunnableConfig | None = None, **kwargs: Any) -> PromptValue`。第267-268行抽象方法 `format_prompt(self, **kwargs: Any) -> PromptValue`。第289行方法 `partial(self, **kwargs: Any) -> Self`。第316-317行抽象方法 `format(self, **kwargs: Any) -> FormatOutputType`。第387行方法 `save(self, file_path: Path | str) -> None`。

F-lc-043: 文件 `prompts/string.py` 第328行抽象类 `StringPromptTemplate(BasePromptTemplate[str], ABC)`。第340行方法 `format_prompt(self, **kwargs) -> PromptValue`（返回 `StringPromptValue`）。第363-364行抽象方法 `format(self, **kwargs: Any) -> str`。

F-lc-044: 文件 `prompts/prompt.py` 第24行类 `PromptTemplate(StringPromptTemplate)`。第77行字段 `template: str`。第80行 `template_format: PromptTemplateFormat = "f-string"`（可选 `"f-string"`、`"mustache"`、`"jinja2"`）。第86行 `validate_template: bool = False`。第90-91行 `@model_validator(mode="before")` 类方法 `pre_init_validation`。第186-187行属性 `_prompt_type` 返回 `"prompt"`。第191行方法 `format(self, **kwargs: Any) -> str`。第203-204行类方法 `from_examples`，第235-236行 `from_file`，第256-257行 `from_template`。第67-75行 `get_lc_namespace` 返回 `["langchain", "prompts", "prompt"]`。

F-lc-045: 文件 `prompts/chat.py` 第53行类 `MessagesPlaceholder(BaseMessagePromptTemplate)`；第354行类 `ChatMessagePromptTemplate`；第668行 `HumanMessagePromptTemplate`、第677行 `AIMessagePromptTemplate`、第686行 `SystemMessagePromptTemplate`；第794行类 `ChatPromptTemplate(BaseChatPromptTemplate)`。

## Language Models（language_models/）

F-lc-046: 文件 `language_models/base.py` 第140行类型别名 `LanguageModelInput = PromptValue | str | Sequence[MessageLikeRepresentation]`。第143行 `LanguageModelOutput = BaseMessage | str`。第146行 `LanguageModelLike = Runnable[LanguageModelInput, LanguageModelOutput]`。第149行 `LanguageModelOutputVar = TypeVar("LanguageModelOutputVar", AIMessage, str)`。

F-lc-047: 文件 `language_models/base.py` 第181-183行抽象基类 `BaseLanguageModel(RunnableSerializable[LanguageModelInput, LanguageModelOutputVar], ABC)`。第190行字段 `cache: BaseCache | bool | None = Field(default=None, exclude=True)`。第201行 `verbose: bool = Field(default_factory=_get_verbosity, exclude=True, repr=False)`。第204行 `callbacks: Callbacks = Field(default=None, exclude=True)`。第207行 `tags: list[str] | None = Field(default=None, exclude=True)`。第210行 `metadata: dict[str, Any] | None = Field(default=None, exclude=True)`。第213行 `custom_get_token_ids: Callable[[str], list[int]] | None = Field(default=None, exclude=True)`。第218-220行 `model_config = ConfigDict(arbitrary_types_allowed=True)`。第222行 `model_post_init` 钩子，第253行 `_add_version(self, pkg: str, version: str) -> None` 向 `metadata["lc_versions"]` 累积包版本。

F-lc-048: 文件 `language_models/base.py` 第317-318行抽象方法 `generate_prompt(self, prompts: list[PromptValue], stop: list[str] | None = None, callbacks: Callbacks = None, **kwargs: Any) -> LLMResult`。第405行方法 `with_structured_output(self, schema: dict | type, *, include_raw: bool = False, **kwargs: Any) -> Runnable`。第434行 `get_token_ids(self, text: str) -> list[int]`，第448行 `get_num_tokens(self, text: str) -> int`，第465行 `get_num_tokens_from_messages(self, messages: list[BaseMessage]) -> int`。

F-lc-049: 文件 `language_models/chat_models.py` 第284行抽象基类 `BaseChatModel(BaseLanguageModel[AIMessage], ABC)`。第334行字段 `rate_limiter: BaseRateLimiter | None = Field(default=None, exclude=True)`。第337行 `disable_streaming: bool | Literal["tool_calling"] = False`。第355行 `output_version: str | None = Field(default_factory=from_env("LC_OUTPUT_VERSION", default=None))`。第455-457行属性 `OutputType` 返回 `AIMessage`。第475行方法 `invoke(self, input: LanguageModelInput, config: RunnableConfig | None = None, *, stop: list[str] | None = None, **kwargs: Any) -> AIMessage`。第727行 `stream`，第1287行 `stream_events`，第1361行 `astream_events`。第1592行 `generate`，第1869行 `generate_prompt`。第2208-2209行抽象方法 `_generate(self, messages: list[BaseMessage], stop: list[str] | None = None, run_manager: CallbackManagerForLLMRun | None = None, **kwargs: Any) -> ChatResult`。第2255行 `_stream`。第2329-2331行抽象属性 `_llm_type -> str`。第2355行 `bind(self, **kwargs: Any) -> _ChatModelBinding`。第2366-2383行方法 `bind_tools(self, tools: Sequence[dict | type | Callable | BaseTool], *, tool_choice: str | None = None, **kwargs: Any) -> Runnable[LanguageModelInput, AIMessage]`，基类抛出 `NotImplementedError`。第2385-2391行 `with_structured_output(self, schema: dict | type, *, include_raw: bool = False, **kwargs: Any) -> Runnable[LanguageModelInput, dict | BaseModel]`。

F-lc-050: 文件 `language_models/chat_models.py` 第2568行类 `_ChatModelBinding(RunnableBinding[LanguageModelInput, AIMessage])`。第2657行类 `SimpleChatModel(BaseChatModel)`，第2666行 `_generate`，第2678-2679行抽象方法 `_call(self, messages: list[BaseMessage], stop: list[str] | None = None, run_manager: CallbackManagerForLLMRun | None = None, **kwargs: Any) -> str`。

## Callbacks（callbacks/）

F-lc-051: 文件 `callbacks/base.py` 第24行 `class RetrieverManagerMixin`：第27行 `on_retriever_error`、第44行 `on_retriever_end`。第62行 `class LLMManagerMixin`：第65行 `on_llm_new_token`、第90行 `on_llm_end`、第109行 `on_llm_error`、第128行 `on_stream_event`。第169行 `class ChainManagerMixin`：第172行 `on_chain_end`、第189行 `on_chain_error`、第206行 `on_agent_action`、第223行 `on_agent_finish`。第241行 `class ToolManagerMixin`：第244行 `on_tool_end`、第261行 `on_tool_error`。第279行 `class CallbackManagerMixin`：第282行 `on_llm_start`、第311行 `on_chat_model_start`、第363行 `on_retriever_start`、第386行 `on_chain_start`、第409行 `on_tool_start`。第435行 `class RunManagerMixin`：第438行 `on_text`、第455行 `on_retry`、第472行 `on_custom_event`。

F-lc-052: 文件 `callbacks/base.py` 第496-503行 `class BaseCallbackHandler(LLMManagerMixin, ChainManagerMixin, ToolManagerMixin, RetrieverManagerMixin, CallbackManagerMixin, RunManagerMixin)`。第506行字段 `raise_error: bool = False`。第509行 `run_inline: bool = False`。第512-545行属性：`ignore_llm`、`ignore_retry`、`ignore_chain`、`ignore_agent`、`ignore_retriever`、`ignore_chat_model`、`ignore_custom_event`，均默认返回 `False`。

F-lc-053: 文件 `callbacks/base.py` 第548行类 `AsyncCallbackHandler(BaseCallbackHandler)`，定义了 `on_llm_start`（第551行，参数含 `serialized`、`prompts: list[str]`、`run_id: UUID`、`parent_run_id`、`tags`、`metadata`）、`on_chat_model_start`（第580行，参数 `messages: list[list[BaseMessage]]`）、`on_llm_new_token`（第632行）、`on_llm_end`（第655行，参数 `response: LLMResult`）、`on_llm_error`、`on_stream_event`、`on_chain_start`、`on_chain_end`、`on_chain_error`、`on_tool_start`、`on_tool_end`、`on_tool_error`、`on_text`、`on_retry`、`on_agent_action`、`on_agent_finish`、`on_retriever_start`、`on_retriever_end`、`on_retriever_error`、`on_custom_event`（第980行）的 async 版本。

F-lc-054: 文件 `callbacks/base.py` 第1004行类 `BaseCallbackManager(CallbackManagerMixin)`。第1007行 `__init__(self, handlers: list[BaseCallbackHandler] | None = None, inheritable_handlers: list[BaseCallbackHandler] | None = None, parent_run_id: UUID | None = None, *, tags: list[str] | None = None, inheritable_tags: list[str] | None = None, metadata: dict[str, Any] | None = None, inheritable_metadata: dict[str, Any] | None = None)`。第1039行 `copy(self) -> Self`，第1051行 `merge(self, other: BaseCallbackManager) -> Self`，第1107行属性 `is_async -> bool`，第1111行 `add_handler`，第1127行 `remove_handler`，第1138行 `set_handlers`，第1154行 `set_handler`，第1167行 `add_tags`，第1197行 `add_metadata`。

F-lc-055: 文件 `callbacks/manager.py` 第490行类 `BaseRunManager(RunManagerMixin)`；第546行 `RunManager`；第599行 `ParentRunManager(RunManager)`；第621行 `AsyncRunManager(BaseRunManager, ABC)`；第683行 `AsyncParentRunManager(AsyncRunManager)`。第705行 `CallbackManagerForLLMRun(RunManager, LLMManagerMixin)`；第806行 `AsyncCallbackManagerForLLMRun`；第928行 `CallbackManagerForChainRun(ParentRunManager, ChainManagerMixin)`；第1018行 `AsyncCallbackManagerForChainRun`；第1127行 `CallbackManagerForToolRun(ParentRunManager, ToolManagerMixin)`；第1181行 `AsyncCallbackManagerForToolRun`；第1248行 `CallbackManagerForRetrieverRun(ParentRunManager, RetrieverManagerMixin)`；第1302行 `AsyncCallbackManagerForRetrieverRun`。第1377行 `CallbackManager(BaseCallbackManager)`；第1859行 `AsyncCallbackManager`。

## Output Parsers（output_parsers/）

F-lc-056: 文件 `output_parsers/base.py` 第34行抽象类 `BaseLLMOutputParser(ABC, Generic[T])`。第37-38行抽象方法 `parse_result(self, result: list[Generation], *, partial: bool = False) -> T`。

F-lc-057: 文件 `output_parsers/base.py` 第74行类 `BaseGenerationOutputParser(BaseLLMOutputParser[T], RunnableSerializable[Generation, T])`。第81行属性 `InputType`，第87行属性 `OutputType`，第94行方法 `invoke(self, input: Generation, config: RunnableConfig | None = None, **kwargs: Any) -> T`。

F-lc-058: 文件 `output_parsers/base.py` 第140-142行抽象类 `BaseOutputParser(BaseLLMOutputParser[T], RunnableSerializable[LanguageModelOutput, T])`。第177行属性 `InputType` 返回 `str | AnyMessage`。第183行属性 `OutputType` 返回 `type[T]`（从 Pydantic 泛型元数据推断）。第204-224行方法 `invoke(self, input: str | BaseMessage, config: RunnableConfig | None = None, **kwargs: Any) -> T`，当 input 为 `BaseMessage` 时包装为 `[ChatGeneration(message=...)]`，否则包装为 `[Generation(text=...)]`，调用 `parse_result`，`run_type="parser"`。第250行 `parse_result(self, result: list[Generation], *, partial: bool = False) -> T`（取第一个 Generation 调用 `parse`）。第270-271行抽象方法 `parse(self, text: str) -> T`。第315行 `parse_with_prompt(self, completion: str, prompt: PromptValue) -> T`。第334行 `get_format_instructions(self) -> str`（返回空字符串）。第338-339行属性 `_type` 抛出 `NotImplementedError`。

## Documents（documents/）

F-lc-059: 文件 `documents/base.py` 第34行类 `BaseMedia(Serializable)`。第59行类 `Blob(BaseMedia)`，第136-137行属性 `source -> str | None`，第150-151行类方法 `check_blob_is_valid`，第158行 `as_string(self) -> str`，第176行 `as_bytes(self) -> bytes`，第195行 `as_bytes_io(self) -> Generator[BytesIO | BufferedReader, None, None]`，第213-214行类方法 `from_path`，第250-251行 `from_data`。

F-lc-060: 文件 `documents/base.py` 第288行类 `Document(BaseMedia)`。第306行字段 `page_content: str`。第309行 `type: Literal["Document"] = "Document"`。第311行 `__init__(self, page_content: str, **kwargs: Any)`。第317-320行 `is_lc_serializable` 返回 `True`。第322-329行 `get_lc_namespace` 返回 `["langchain", "schema", "document"]`。第331行 `__str__(self) -> str`，当有 metadata 时返回 `page_content='...' metadata={...}`，否则返回 `page_content='...'`。`Document` 继承 `BaseMedia`（进而继承 `Serializable`），含 `metadata`、`id` 字段。

## VectorStores（vectorstores/）

F-lc-061: 文件 `vectorstores/base.py` 第43行抽象类 `VectorStore(ABC)`。第46行方法 `add_texts(self, texts: Iterable[str], metadatas: list[dict] | None = None, *, ids: list[str] | None = None, **kwargs: Any) -> list[str]`，默认委托给 `add_documents`。第99-100行属性 `embeddings -> Embeddings | None` 默认返回 `None`。第108行 `delete(self, ids: list[str] | None = None, **kwargs: Any) -> bool | None` 抛 `NotImplementedError`。第122行 `get_by_ids(self, ids: Sequence[str], /) -> list[Document]`。第148行 `async aget_by_ids`。第185行 `async aadd_texts`。第234行 `add_documents(self, documents: list[Document], **kwargs: Any) -> list[str]`。第265行 `async aadd_documents`。第293行 `search(self, query: str, search_type: str, **kwargs: Any) -> list[Document]`，支持 `"similarity"`、`"mmr"`、`"similarity_score_threshold"`。第360-363行抽象方法 `similarity_search(self, query: str, k: int = 4, **kwargs: Any) -> list[Document]`。第375-388行静态方法 `_euclidean_relevance_score_fn(distance: float) -> float` 返回 `1.0 - distance / math.sqrt(2)`。第390-393行 `_cosine_relevance_score_fn(distance)` 返回 `1.0 - distance`。第395-401行 `_max_inner_product_relevance_score_fn(distance)`。第417行 `similarity_search_with_score`，第506行 `similarity_search_with_relevance_scores`，第659行 `max_marginal_relevance_search`。第786-787行类方法 `from_documents`，第846-848行抽象类方法 `from_texts`。第905行方法 `as_retriever(self, **kwargs: Any) -> VectorStoreRetriever`，第960-961行返回 `VectorStoreRetriever(vectorstore=self, tags=tags, **kwargs)`。

F-lc-062: 文件 `vectorstores/base.py` 第964行类 `VectorStoreRetriever(BaseRetriever)`。第987-988行类方法 `validate_search_type`（验证 search_type 只能是 `"similarity"`、`"mmr"`、`"similarity_score_threshold"`）。第1040行 `_get_relevant_documents`，第1061行 `_aget_relevant_documents`，第1087行 `add_documents`。

## Retrievers（retrievers.py）

F-lc-063: 文件 `retrievers.py` 第39行 `class LangSmithRetrieverParams(TypedDict, total=False)`。第55行抽象基类 `BaseRetriever(RunnableSerializable[RetrieverInput, RetrieverOutput], ABC)`。第125行字段 `tags: list[str] | None = None`。第135行 `metadata: dict[str, Any] | None = None`。第146行 `__init_subclass__` 通过检查 `_get_relevant_documents` 签名判断 `_new_arg_supported` 和 `_expects_other_args`，若子类未实现 async 版本则自动包装 `run_in_executor`。第167行 `_get_ls_params(self, **_kwargs: Any) -> LangSmithRetrieverParams`（从类名推导 retriever 名称）。第179-181行方法 `invoke(self, input: str, config: RunnableConfig | None = None, **kwargs: Any) -> list[Document]`。第237行 `async ainvoke`。第297-298行抽象方法 `_get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]`。第311行 `async _aget_relevant_documents`（默认抛 `NotImplementedError`）。

## Tracers（tracers/）

F-lc-064: 文件 `tracers/base.py` 第33行抽象类 `BaseTracer(_TracerCore, BaseCallbackHandler, ABC)`。第37行 `_persist_run(self, run: Run) -> None`，第40行 `_start_trace(self, run: Run) -> None`，第45行 `_end_trace(self, run: Run) -> None`。回调方法：第61行 `on_chat_model_start`、第108行 `on_llm_start`、第150行 `on_llm_new_token`、第185行 `on_retry`、第208行 `on_llm_end(self, response: LLMResult, *, run_id: UUID, **kwargs) -> Run`、第234行 `on_llm_error`、第261行 `on_chain_start`、第306行 `on_chain_end`、第335行 `on_chain_error`、第363行 `on_tool_start`、第408行 `on_tool_end(self, output: Any, *, run_id: UUID, **kwargs) -> Run`、第428行 `on_tool_error`、第453行 `on_retriever_start`、第495行 `on_retriever_error`、第521行 `on_retriever_end`。第542行 `__deepcopy__`，第546行 `__copy__`。

F-lc-065: 文件 `tracers/base.py` 第551行抽象类 `AsyncBaseTracer(_TracerCore, AsyncCallbackHandler, ABC)`。第556行 `async _persist_run`，第560行 `async _start_trace`，第571行 `async _end_trace`。含全部 async 回调（`on_llm_start` 第622行、`on_chat_model_start` 第592行、`on_llm_end` 第677行等）及内部钩子 `_on_run_create`（第904行）、`_on_run_update`（第907行）、`_on_llm_start`、`_on_llm_end`、`_on_chain_start`、`_on_tool_start`、`_on_retriever_start` 等。

## Embeddings（embeddings/）

F-lc-066: 文件 `embeddings/embeddings.py` 第8行抽象类 `Embeddings(ABC)`。第36-37行抽象方法 `embed_documents(self, texts: list[str]) -> list[list[float]]`。第47-48行抽象方法 `embed_query(self, text: str) -> list[float]`。第58-67行 `async aembed_documents(self, texts: list[str]) -> list[list[float]]` 默认 `run_in_executor(None, self.embed_documents, texts)`。第69-78行 `async aembed_query(self, text: str) -> list[float]` 默认 `run_in_executor(None, self.embed_query, text)`。

## Outputs（outputs/）

F-lc-067: 文件 `outputs/generation.py` 第11行类 `Generation(Serializable)`。第25行字段 `text: str`。第28行 `generation_info: dict[str, Any] | None = None`。第34行 `type: Literal["Generation"] = "Generation"`。第40-43行 `is_lc_serializable` 返回 `True`。第45-52行 `get_lc_namespace` 返回 `["langchain", "schema", "output"]`。第55行类 `GenerationChunk(Generation)`，第58行 `__add__(self, other: GenerationChunk) -> GenerationChunk` 拼接 text 并合并 `generation_info`。

F-lc-068: 文件 `outputs/chat_generation.py` 第17行类 `ChatGeneration(Generation)`。第31行 `text: str = ""`。第37行字段 `message: BaseMessage`。第41行 `type: Literal["ChatGeneration"] = "ChatGeneration"`。第44-84行 `@model_validator(mode="after")` 方法 `set_text`，从 `message.content`/`message.text` 设置 `text`。第87行类 `ChatGenerationChunk(ChatGeneration)`，第93行 `message: BaseMessageChunk`，第97行 `type: Literal["ChatGenerationChunk"] = "ChatGenerationChunk"`，第100-137行 `__add__` 支持单个或列表拼接。第140-156行函数 `merge_chat_generation_chunks(chunks: list[ChatGenerationChunk]) -> ChatGenerationChunk | None`。

## Prompt Values（prompt_values.py）

F-lc-069: 文件 `prompt_values.py` 第24行抽象类 `PromptValue(Serializable, ABC)`。第45-46行抽象方法 `to_string(self) -> str`。第49-50行抽象方法 `to_messages(self) -> list[BaseMessage]`。第54行类 `StringPromptValue(PromptValue)`，第71行 `to_string` 返回 `self.text`，第75行 `to_messages` 返回 `[HumanMessage(content=self.text)]`。第80行类 `ChatPromptValue(PromptValue)`，第89行 `to_string`，第93行 `to_messages`。第152行类 `ChatPromptValueConcrete(ChatPromptValue)`。

## Runnable Passthrough（runnables/passthrough.py）

F-lc-070: 文件 `runnables/passthrough.py` 中定义 `RunnablePassthrough` 和 `RunnableAssign`（由 `runnables/__init__.py` 第48-49行、第113-114行导出，映射到 `"passthrough"` 模块）。

## 公共导出

F-lc-071: 文件 `runnables/__init__.py` 第28-33行导出 `RunnableBinding`、`RunnableGenerator`、`RunnableLambda`、`RunnableParallel`、`RunnableSequence`；第48-49行导出 `RunnableAssign`、`RunnablePassthrough`。使用懒加载（第98-114行 `_dynamic_imports`）。
