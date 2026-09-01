---
type: Facts
title: GodeAgents (codified-smolagents) 源码事实清单
---

# GodeAgents (codified-smolagents) 源码事实清单

> R阶段产出：从 `d:\spaces\SpecWeave\external\libs\models\AgnesAI\GodeAgents\Multi-Agent-Task\src\codified-smolagents\` 采集的零推测事实，编号 F-001 ~ F-195。

## 模块 1: `__init__.py`

- **F-001**: 文件 `__init__.py` 第17行定义 `__version__ = "1.14.0.dev0"`。
- **F-002**: 文件 `__init__.py` 通过 `from .agent_types import *` 导入 `agent_types` 模块全部公开符号。
- **F-003**: 文件 `__init__.py` 通过 `from .agents import *` 导入 `agents` 模块全部公开符号，第20行注释标注 `# noqa: I001` 以忽略因 `cli.py` 导致的循环依赖警告。
- **F-004**: 文件 `__init__.py` 依次从 `.default_tools`、`.gradio_ui`、`.local_python_executor`、`.memory`、`.models`、`.monitoring`、`.remote_executors`、`.tools`、`.utils`、`.cli` 模块执行 `import *` 导入。
- **F-005**: 文件 `__init__.py` 从 `.models` 显式导入 `Model`、`TransformersModel`、`HfApiModel`、`LiteLLMModel`、`OpenAIServerModel`、`AzureOpenAIServerModel`、`AmazonBedrockServerModel` 七个类。

## 模块 2: `agents.py`

- **F-006**: 文件 `agents.py` 定义函数 `get_variable_names(self, template: str) -> Set[str]`，使用正则 `r"\{\{([^{}]+)\}\}"` 从 Jinja2 模板中提取变量名集合。
- **F-007**: 文件 `agents.py` 定义函数 `populate_template(template: str, variables: Dict[str, Any]) -> str`，使用 `jinja2.Template`（`StrictUndefined`）渲染模板，捕获异常后抛出 `Exception`。
- **F-008**: 文件 `agents.py` 定义 `PlanningPromptTemplate(TypedDict)`，包含6个 `str` 类型字段：`initial_facts`、`initial_plan`、`update_facts_pre_messages`、`update_facts_post_messages`、`update_plan_pre_messages`、`update_plan_post_messages`。
- **F-009**: 文件 `agents.py` 定义 `ManagedAgentPromptTemplate(TypedDict)`，包含2个 `str` 类型字段：`task`、`report`。
- **F-010**: 文件 `agents.py` 定义 `FinalAnswerPromptTemplate(TypedDict)`，包含2个 `str` 类型字段：`pre_messages`、`post_messages`。
- **F-011**: 文件 `agents.py` 定义 `PromptTemplates(TypedDict)`，包含4个字段：`system_prompt: str`、`planning: PlanningPromptTemplate`、`managed_agent: ManagedAgentPromptTemplate`、`final_answer: FinalAnswerPromptTemplate`。
- **F-012**: 文件 `agents.py` 定义常量 `EMPTY_PROMPT_TEMPLATES`，类型为 `PromptTemplates`，所有字段值为空字符串。
- **F-013**: 文件 `agents.py` 定义类 `MultiStepAgent`，无显式基类（继承 `object`）。
- **F-014**: 类 `MultiStepAgent.__init__` 接收参数：`tools: List[Tool]`、`model: Callable[[List[Dict[str, str]]], ChatMessage]`、`prompt_templates: Optional[PromptTemplates]=None`、`max_steps: int=20`、`add_base_tools: bool=False`、`verbosity_level: LogLevel=LogLevel.INFO`、`grammar: Optional[Dict[str, str]]=None`、`managed_agents: Optional[List]=None`、`step_callbacks: Optional[List[Callable]]=None`、`planning_interval: Optional[int]=None`、`name: Optional[str]=None`、`description: Optional[str]=None`、`provide_run_summary: bool=False`、`final_answer_checks: Optional[List[Callable]]=None`。
- **F-015**: `MultiStepAgent.__init__` 中实例属性包括：`self.agent_name`、`self.model`、`self.prompt_templates`、`self.max_steps`、`self.step_number = 0`、`self.grammar`、`self.planning_interval`、`self.state = {}`、`self.name`、`self.description`、`self.provide_run_summary`、`self.final_answer_checks`、`self.managed_agents`（dict）、`self.tools`（dict，key为tool.name）、`self.system_prompt`、`self.memory = AgentMemory(self.system_prompt)`、`self.logger = AgentLogger(level=verbosity_level)`、`self.monitor = Monitor(self.model, self.logger)`、`self.step_callbacks`。
- **F-016**: `MultiStepAgent._validate_name(self, name: str|None) -> str|None` 方法：若 `name` 非 `None` 且 `is_valid_name(name)` 返回 `False`，则抛出 `ValueError`。
- **F-017**: `MultiStepAgent._setup_managed_agents(self, managed_agents)` 方法：当 `managed_agents` 非空时，断言每个 agent 同时具有 `name` 和 `description` 属性，然后构建 `{agent.name: agent}` 字典赋值给 `self.managed_agents`。
- **F-018**: `MultiStepAgent._setup_tools(self, tools, add_base_tools)` 方法：断言 `tools` 中所有元素均为 `Tool` 实例；构建 `{tool.name: tool}` 字典；当 `add_base_tools=True` 时，将 `TOOL_MAPPING` 中除 `python_interpreter`（仅 `ToolCallingAgent` 保留）外的所有工具实例加入；最后 `self.tools.setdefault("final_answer", FinalAnswerTool())` 确保 `final_answer` 工具存在。
- **F-019**: `MultiStepAgent._validate_tools_and_managed_agents(self, tools, managed_agents)` 方法：收集所有 tool 名称、managed_agent 名称以及 `self.name`，检测重复名称并抛出 `ValueError`。
- **F-020**: `MultiStepAgent.run(self, task: str, stream: bool=False, reset: bool=False, images: Optional[List[PIL.Image.Image]]=None, additional_args: Optional[Dict]=None, max_steps: Optional[int]=None)` 方法：当 `stream=True` 时返回 `self._run(...)` 生成器；否则使用 `deque(..., maxlen=1)[0].final_answer` 返回最终答案。
- **F-021**: `MultiStepAgent._run(self, task: str, max_steps: int, images: List[PIL.Image.Image]|None=None) -> Generator[ActionStep|AgentType, None, None]` 方法：循环执行步骤直到 `final_answer` 非 `None` 或 `step_number > max_steps`；在步骤1和每隔 `planning_interval` 步时创建 `PlanningStep`；最后 yield `FinalAnswerStep`。
- **F-022**: `MultiStepAgent.step(self, memory_step: ActionStep) -> Union[None, Any]` 方法体为 `pass`，由子类实现。
- **F-023**: `MultiStepAgent.write_memory_to_messages(self, summary_mode: Optional[bool]=False) -> List[Dict[str, str]]` 方法：将 `self.memory.system_prompt` 和 `self.memory.steps` 依次调用 `to_messages(summary_mode=summary_mode)` 并扩展到消息列表中返回。
- **F-024**: `MultiStepAgent.extract_action(self, model_output: str, split_token: str) -> Tuple[str, str]` 方法：按 `split_token` 分割模型输出，取倒数第二个元素作为 `rationale`，最后一个元素作为 `action`，均 strip 后返回；分割失败时抛出 `AgentParsingError`。
- **F-025**: `MultiStepAgent.provide_final_answer(self, task: str, images: Optional[list]) -> str` 方法：构造含 `final_answer.pre_messages` 和 `final_answer.post_messages` 的消息列表，调用 `self.model(messages)` 获取最终回答内容。
- **F-026**: `MultiStepAgent.__call__(self, task: str, **kwargs)` 方法：使用 `populate_template` 渲染 `managed_agent.task` 模板后调用 `self.run()`，再渲染 `managed_agent.report` 模板返回结果；若 `provide_run_summary=True` 则追加 `write_memory_to_messages(summary_mode=True)` 摘要。
- **F-027**: `MultiStepAgent.save(self, output_dir: str|Path, relative_path: Optional[str]=None)` 方法：将 agent 保存到输出目录，包括递归保存 managed_agents、将每个 tool 保存为 `tools/{tool_name}.py`、将 prompt_templates 序列化为 `prompts.yaml`、将 `to_dict()` 序列化为 `agent.json`、生成 `requirements.txt`、使用 Jinja2 模板生成 `app.py`。
- **F-028**: `MultiStepAgent.to_dict(self) -> dict[str, Any]` 方法：返回包含 `tools`、`model`、`managed_agents`、`prompt_templates`、`max_steps`、`verbosity_level`、`grammar`、`planning_interval`、`name`、`description`、`requirements` 的字典。
- **F-029**: `MultiStepAgent.from_hub(cls, repo_id: str, token: Optional[str]=None, trust_remote_code: bool=False, **kwargs)` 类方法：要求 `trust_remote_code=True`，使用 `snapshot_download` 下载 Hub 上的 Space 仓库，然后调用 `cls.from_folder()` 加载。
- **F-030**: `MultiStepAgent.from_folder(cls, folder: Union[str, Path], **kwargs)` 类方法：从本地文件夹加载 agent，读取 `agent.json`，递归加载 managed_agents、tools（`Tool.from_code`）、model（动态导入），返回 `cls(**args)`。
- **F-031**: `MultiStepAgent.push_to_hub(self, repo_id: str, commit_message="Upload agent", private=None, token=None, create_pr=False) -> str` 方法：使用 `huggingface_hub.create_repo` 创建 Space 仓库，调用 `self.save()` 输出到临时目录，再用 `upload_folder` 上传。
- **F-032**: 文件 `agents.py` 定义类 `ToolCallingAgent(MultiStepAgent)`，继承 `MultiStepAgent`。
- **F-033**: `ToolCallingAgent.__init__` 接收参数：`tools: List[Tool]`、`model: Callable`、`prompt_templates: Optional[PromptTemplates]=None`、`planning_interval: Optional[int]=None`、`**kwargs`。
- **F-034**: `ToolCallingAgent.__init__` 在 `prompt_templates` 为 `None` 时，从 `smolagents.prompts.toolcalling_agent.yaml` 读取默认 YAML 模板。
- **F-035**: `ToolCallingAgent.initialize_system_prompt(self) -> str` 方法：使用 `populate_template` 渲染 `self.prompt_templates["system_prompt"]`，传入变量 `tools` 和 `managed_agents`。
- **F-036**: `ToolCallingAgent.step(self, memory_step: ActionStep) -> Union[None, Any]` 方法：调用 `self.model(memory_messages, tools_to_call_from=list(self.tools.values()), stop_sequences=["Observation:", "Calling tools:"])` 获取模型响应；从 `model_message.tool_calls[0]` 提取 `tool_name`、`tool_call_id`、`tool_arguments`；若工具为 `final_answer` 则返回最终答案，否则调用 `self.execute_tool_call()` 并返回 `None`。
- **F-037**: `ToolCallingAgent._substitute_state_variables(self, arguments: Union[Dict[str, str], str]) -> Union[Dict[str, Any], str]` 方法：将参数中值为字符串且在 `self.state` 中存在的键替换为 `self.state[value]`。
- **F-038**: `ToolCallingAgent.execute_tool_call(self, tool_name: str, arguments: Union[Dict[str, str], str]) -> Any` 方法：在 `{**self.tools, **self.managed_agents}` 中查找工具；替换状态变量后调用工具；`TypeError` 抛出 `AgentToolCallError`，其他异常抛出 `AgentToolExecutionError`。
- **F-039**: 文件 `agents.py` 定义类 `CodeAgent(MultiStepAgent)`，继承 `MultiStepAgent`。
- **F-040**: `CodeAgent.__init__` 接收参数：`tools: List[Tool]`、`model: Callable`、`prompt_templates: Optional[PromptTemplates]=None`、`grammar: Optional[Dict[str, str]]=None`、`additional_authorized_imports: Optional[List[str]]=None`、`planning_interval: Optional[int]=None`、`executor_type: str|None="local"`、`executor_kwargs: Optional[Dict[str, Any]]=None`、`max_print_outputs_length: Optional[int]=None`、`**kwargs`。
- **F-041**: `CodeAgent.__init__` 设置 `self.authorized_imports = sorted(set(BASE_BUILTIN_MODULES) | set(self.additional_authorized_imports))`；当 `"*"` 在 `additional_authorized_imports` 中时输出警告日志。
- **F-042**: `CodeAgent.__init__` 在 `prompt_templates` 为 `None` 时，从 `smolagents.prompts.code_agent.yaml` 读取默认 YAML 模板。
- **F-043**: `CodeAgent.create_python_executor(self) -> PythonExecutor` 方法：根据 `self.executor_type` 创建执行器：`"e2b"` 返回 `E2BExecutor`、`"docker"` 返回 `DockerExecutor`、`"local"` 返回 `LocalPythonExecutor`；其他值抛出 `ValueError`。
- **F-044**: `CodeAgent.initialize_system_prompt(self) -> str` 方法：使用 `populate_template` 渲染 system_prompt，传入变量 `tools`、`managed_agents`、`authorized_imports`。
- **F-045**: `CodeAgent.step(self, memory_step: ActionStep) -> Union[None, Any]` 方法：调用 `self.model(self.input_messages, stop_sequences=["<end_code>", "Observation:", "Calling tools:"])` 获取模型输出；使用 `parse_code_blobs(model_output)` 和 `fix_final_answer_code()` 解析代码；调用 `self.python_executor(code_action)` 执行代码，返回 `(output, execution_logs, is_final_answer)` 三元组。
- **F-046**: `CodeAgent.to_dict(self) -> dict[str, Any]` 方法：在父类 `to_dict()` 结果基础上追加 `authorized_imports`、`executor_type`、`executor_kwargs`、`max_print_outputs_length` 四个字段。

## 模块 3: `tools.py`

- **F-047**: 文件 `tools.py` 定义 `Tool` 基类，要求子类定义类属性 `name: str`、`description: str`、`inputs: Dict[str, Dict]`、`output_type: str`，以及实例方法 `forward(self, *args, **kwargs)`。
- **F-048**: `Tool` 类包含类属性 `skip_forward_signature_validation = False`、`is_initialized = False`。
- **F-049**: `Tool.__init__(self, **kwargs)` 方法：将 `kwargs` 通过 `self.__dict__.update(kwargs)` 设置为实例属性；调用 `self.validate_arguments()`；设置 `self.is_initialized = True`。
- **F-050**: `Tool.forward(self, *args, **kwargs)` 方法抛出 `NotImplementedError`。
- **F-051**: `Tool.__call__(self, *args, sanitize_inputs_outputs: bool=False, **kwargs)` 方法：调用 `self.forward()`；若 `sanitize_inputs_outputs=True` 则对结果调用 `handle_agent_output_types()`。
- **F-052**: `Tool.to_dict(self) -> Dict` 方法：返回包含 `name`、`description`、`inputs`、`output_type`、`requirements` 的字典。
- **F-053**: `Tool.save(self, output_dir, tool_file_name=None, make_gradio_app=True)` 方法：将工具代码保存到 `output_dir` 下的 `.py` 文件，可选生成 Gradio app。
- **F-054**: `Tool.from_code(cls, tool_code: str) -> Tool` 类方法：动态执行代码字符串，提取其中 `Tool` 子类实例。
- **F-055**: `Tool.from_space(cls, space_id: str, name: str|None=None, description: str|None=None, api_name: str|None=None) -> SpaceToolWrapper` 类方法：从 Hugging Face Space 创建工具包装器。
- **F-056**: `@tool` 装饰器将普通 Python 函数转换为 `Tool` 子类实例，通过函数名、docstring、类型注解自动生成工具定义。
- **F-057**: 文件 `tools.py` 定义 `ToolCollection` 类，用于加载和管理一组工具，提供 `__iter__`、`__getitem__`、`__len__` 等集合方法。
- **F-058**: 文件 `tools.py` 定义 `PipelineTool(Tool)` 子类，用于包装 Transformer pipeline 模型。
- **F-059**: 文件 `tools.py` 定义 `SpaceToolWrapper(Tool)` 子类，包装 Hugging Face Space 推理端点作为工具。
- **F-060**: 函数 `get_tools_definition_code(tools: Dict[str, Tool]) -> str` 接收工具字典，返回工具定义的 Python 代码字符串。

## 模块 4: `models.py`

- **F-061**: 文件 `models.py` 定义 `MessageRole` 枚举，包含值 `USER`、`ASSISTANT`、`SYSTEM`、`TOOL_CALL`、`TOOL_RESPONSE`。
- **F-062**: 文件 `models.py` 定义 `ChatMessage` 数据类，包含字段：`role: str`、`content: Optional[str]=None`、`tool_calls: Optional[List[ChatMessageToolCall]]=None`、`raw: Optional[Any]=None`。
- **F-063**: 文件 `models.py` 定义 `Model` 基类，包含抽象方法 `__call__(self, messages, stop_sequences=None, grammar=None, tools_to_call_from=None, **kwargs) -> ChatMessage`。
- **F-064**: `Model` 基类包含属性 `last_input_token_count`、`last_output_token_count`、`flatten_messages_as_text`、`tool_name_key`、`tool_arguments_key`。
- **F-065**: `Model._prepare_completion_kwargs` 方法处理消息清理、工具JSON schema生成、参数优先级。
- **F-066**: `Model.get_token_counts(self) -> Dict[str, int]` 返回 token 计数字典。
- **F-067**: 文件 `models.py` 定义 `TransformersModel(Model)` 子类，构造参数包含 `model_id`、`device_map`、`torch_dtype`、`trust_remote_code`、`kwargs`。
- **F-068**: `TransformersModel` 先尝试 `AutoModelForImageTextToText`，失败后回退到 `AutoModelForCausalLM`。
- **F-069**: 文件 `models.py` 定义 `HfApiModel(ApiModel)` 子类，默认 `model_id="Qwen/Qwen2.5-Coder-32B-Instruct"`，使用 `huggingface_hub.InferenceClient`。
- **F-070**: `HfApiModel` 的 `create_client` 返回 `InferenceClient(**self.client_kwargs)`。
- **F-071**: 文件 `models.py` 定义 `LiteLLMModel(ApiModel)` 子类，默认 `model_id="anthropic/claude-3-5-sonnet-20240620"`，使用 `litellm.completion()`。
- **F-072**: `LiteLLMModel` 对于模型ID以 `ollama`/`groq`/`cerebras` 开头时自动设置 `flatten_messages_as_text=True`。
- **F-073**: 文件 `models.py` 定义 `OpenAIServerModel(ApiModel)` 子类，使用 `openai.OpenAI` 客户端。
- **F-074**: `OpenAIServerModel.__call__` 调用 `self.client.chat.completions.create(**completion_kwargs)`。
- **F-075**: 文件 `models.py` 定义 `AzureOpenAIServerModel(OpenAIServerModel)` 子类，额外接受 `api_version`、`azure_endpoint` 参数。
- **F-076**: 文件 `models.py` 定义 `AmazonBedrockServerModel(ApiModel)` 子类，使用 `boto3` 客户端。
- **F-077**: 文件 `models.py` 定义 `VLLMModel(Model)` 子类，使用 vLLM 进行本地快速推理。
- **F-078**: 文件 `models.py` 定义 `MLXModel(Model)` 子类，使用 MLX 在 Apple Silicon 上推理。
- **F-079**: 函数 `get_tool_json_schema(tool: Tool) -> Dict` 将 Tool 转换为 OpenAI function calling 格式的 JSON Schema。
- **F-080**: 函数 `get_clean_message_list` 处理消息列表，合并连续同角色消息，转换图片格式。
- **F-081**: 函数 `get_tool_call_from_text` 从文本中解析工具调用，返回 `ChatMessageToolCall`。

## 模块 5: `memory.py`

- **F-082**: 文件 `memory.py` 定义 `ToolCall` 数据类，包含字段：`name: str`、`arguments: Any`、`id: str`；`dict()` 方法返回 OpenAI 格式的 function call 字典。
- **F-083**: 文件 `memory.py` 定义 `Message(TypedDict)`，包含 `role: MessageRole` 和 `content: str | list[dict]`。
- **F-084**: 文件 `memory.py` 定义 `MemoryStep` 基类，包含 `dict()` 和 `to_messages()` 方法。
- **F-085**: 文件 `memory.py` 定义 `SystemPromptStep(MemoryStep)` 子类，字段 `system_prompt: str`；`to_messages` 返回 system 角色消息。
- **F-086**: 文件 `memory.py` 定义 `TaskStep(MemoryStep)` 子类，字段 `task: str`、`task_images: list|None=None`；`to_messages` 返回 user 角色消息。
- **F-087**: 文件 `memory.py` 定义 `ActionStep(MemoryStep)` 子类，包含字段：`model_input_messages`、`tool_calls`、`start_time`、`end_time`、`step_number`、`error`、`duration`、`model_output_message`、`model_output`、`observations`、`observations_images`、`action_output`。
- **F-088**: `ActionStep.to_messages` 方法按顺序输出：模型输出（assistant）→工具调用（tool-call）→观察图片（user）→观察文本（tool-response）→错误信息（tool-response）。
- **F-089**: 文件 `memory.py` 定义 `PlanningStep(MemoryStep)` 子类，字段：`model_input_messages`、`model_output_message`、`plan: str`。
- **F-090**: `PlanningStep.to_messages` 返回 plan 内容（assistant）+ "Now proceed"（user）两条消息。
- **F-091**: 文件 `memory.py` 定义 `FinalAnswerStep(MemoryStep)` 子类，字段 `final_answer: Any`。
- **F-092**: 文件 `memory.py` 定义 `AgentMemory` 类，属性 `system_prompt: SystemPromptStep`、`steps: List[MemoryStep]`。
- **F-093**: `AgentMemory.reset(self)` 清空 `self.steps`。
- **F-094**: `AgentMemory.get_succinct_steps(self)` 返回不含 `model_input_messages` 的精简步骤列表。
- **F-095**: `AgentMemory.get_full_steps(self)` 返回完整步骤列表。
- **F-096**: `AgentMemory.replay(self, logger, detailed=False)` 使用 logger 格式化输出每一步信息。

## 模块 6: `agent_types.py`

- **F-097**: 文件 `agent_types.py` 定义 `AgentType` 基类，构造函数接收 `value`，存储为 `self._value`。
- **F-098**: `AgentType.to_raw(self)` 返回原始值（如 PIL.Image.Image）。
- **F-099**: `AgentType.to_string(self)` 方法抛出 `NotImplementedError`（子类实现）。
- **F-100**: 文件 `agent_types.py` 定义 `AgentText(AgentType)` 子类，`to_string()` 返回字符串值。
- **F-101**: 文件 `agent_types.py` 定义 `AgentImage(AgentType, PIL.Image.Image)` 子类，支持 PIL 图像、字节、路径、张量输入；`to_string()` 返回图片文件路径；包含 `save_to_file` 和 `to_raw` 方法。
- **F-102**: 文件 `agent_types.py` 定义 `AgentAudio(AgentType)` 子类，支持音频路径和音频数据；`to_string()` 返回音频文件路径；包含 `save_to_file` 方法。
- **F-103**: 函数 `handle_agent_input_types(tool_name, arguments, state)` 处理工具输入中的 AgentImage/AgentAudio，转换为文件路径。
- **F-104**: 函数 `handle_agent_output_types(output, observations_images=None)` 将输出转换为 AgentType 子类实例。

## 模块 7: `local_python_executor.py`

- **F-105**: 文件 `local_python_executor.py` 定义常量 `BASE_BUILTIN_MODULES`（Python 标准库模块名集合）、`DEFAULT_MAX_LEN_OUTPUT=50000`、`MAX_OPERATIONS=10000000`、`MAX_WHILE_ITERATIONS=1000000`。
- **F-106**: 定义 `DANGEROUS_MODULES = ["builtins","io","multiprocessing","os","pathlib","pty","shutil","socket","subprocess","sys"]`。
- **F-107**: 定义 `DANGEROUS_FUNCTIONS = ["builtins.compile","builtins.eval","builtins.exec","builtins.globals","builtins.locals","builtins.__import__","os.popen","os.system","posix.system"]`。
- **F-108**: 定义 `BASE_PYTHON_TOOLS` 字典，包含安全的内置函数（print→custom_print、isinstance、range、类型转换、数学函数、len/sum/max/min、enumerate/zip/sorted等）。
- **F-109**: 定义异常类 `InterpreterError(ValueError)` 和 `FinalAnswerException(Exception)`。
- **F-110**: 定义 `PythonExecutor` 抽象基类，包含 `final_answer_pattern`、`state`、`additional_imports`、`logger`、`installed_packages` 属性；抽象方法 `run_code_raise_errors`。
- **F-111**: `PythonExecutor.__call__` 检测代码是否匹配 `final_answer_pattern`，返回 `(output, execution_logs, is_final_answer)` 三元组。
- **F-112**: 文件定义 `LocalPythonExecutor(PythonExecutor)` 子类。
- **F-113**: `LocalPythonExecutor.__init__` 初始化 state 字典（含自定义 final_answer 函数、安全 builtins、authorized_imports）。
- **F-114**: `LocalPythonExecutor.run_code_raise_errors` 使用 `ast.parse` 解析代码，`_check_imports` AST访问器验证import安全性，`compile`+`exec` 在受限命名空间中执行。
- **F-115**: `LocalPythonExecutor` 的 state 中注入的 `final_answer` 函数抛出 `FinalAnswerException(final_answer)`。
- **F-116**: `LocalPythonExecutor.send_tools` 通过 `get_tools_definition_code` 生成工具代码并在命名空间中执行，注入工具实例。
- **F-117**: `LocalPythonExecutor.send_variables` 将 variables dict 更新到 `self.state`。
- **F-118**: 函数 `fix_final_answer_code(code: str) -> str` 修复 LLM 对 `final_answer` 变量的赋值问题，将直接赋值替换为 `final_answer_variable`。
- **F-119**: `evaluate_ast` 函数是核心 AST 求值器，通过 `@safer_eval` 装饰器添加返回值安全检查，支持大部分 Python 语法节点。

## 模块 8: `default_tools.py`

- **F-120**: 文件 `default_tools.py` 定义 `PythonInterpreterTool(Tool)` 类，`name="python_interpreter"`，`inputs={"code": {"type": "string"}}`，`forward` 调用 `self.python_executor(code_action)`。
- **F-121**: 文件定义 `FinalAnswerTool(Tool)` 类，`name="final_answer"`，`inputs={"answer": {"type": "any"}}`，`forward` 直接返回 `answer`。
- **F-122**: 文件定义 `DuckDuckGoSearchTool(Tool)` 类，`name="web_search"`，使用 `duckduckgo_search.DDGS` 搜索。
- **F-123**: 文件定义 `VisitWebpageTool(Tool)` 类，`name="visit_webpage"`，使用 `requests`+`markdownify` 获取网页内容。
- **F-124**: 文件定义 `WikipediaSearchTool(Tool)` 类，`name="search_wikipedia"`，使用 `wikipedia` 库搜索。
- **F-125**: 文件定义 `TOOL_MAPPING` 字典：`{"python_interpreter": PythonInterpreterTool, "web_search": DuckDuckGoSearchTool, "visit_webpage": VisitWebpageTool, "search_wikipedia": WikipediaSearchTool, "final_answer": FinalAnswerTool}`。

## 模块 9: `monitoring.py`

- **F-126**: 文件 `monitoring.py` 定义 `LogLevel` 枚举：`OFF=0`、`ERROR=1`、`INFO=2`、`DEBUG=3`。
- **F-127**: 定义 `AgentLogger` 类，内部使用 `rich.console.Console`，提供 `log`、`log_rule`、`log_task`、`log_markdown`、`log_code`、`log_error`、`visualize_agent_tree` 方法。
- **F-128**: 定义 `Monitor` 类，包含 `update_metrics(self, step_log, agent)` 方法更新 token 计数；`__del__` 输出总token使用量。

## 模块 10: `utils.py`

- **F-129**: 文件 `utils.py` 定义异常类层次：`AgentError(Exception)` 为基类，子类包括 `AgentParsingError`、`AgentGenerationError`、`AgentExecutionError`、`AgentMaxStepsError`、`AgentToolCallError`、`AgentToolExecutionError`。
- **F-130**: 定义常量 `BASE_BUILTIN_MODULES`（从 `sys.stdlib_module_names` 衍生的集合）。
- **F-131**: 函数 `parse_code_blobs(text: str) -> str` 从文本中提取 ```python 代码块内容。
- **F-132**: 函数 `truncate_content(content, max_length=5000)` 截断超长内容。
- **F-133**: 函数 `make_json_serializable(obj)` 递归转换对象为JSON可序列化类型。
- **F-134**: 函数 `is_valid_name(name: str) -> bool` 检查字符串是否为有效Python标识符且非保留关键字。
- **F-135**: 函数 `make_init_file(directory)` 创建 `__init__.py`。
- **F-136**: 函数 `get_source(obj)` 获取对象源码。
- **F-137**: 函数 `_is_package_available(package_name)` 使用 `importlib.util.find_spec` 检查包可用性。
- **F-138**: 函数 `parse_json_blob(text)` 从文本中提取JSON对象。

## 模块 11: `_function_type_hints_utils.py`

- **F-139**: 文件定义 `get_imports(code: str) -> List[str]` 从代码中提取顶层 import 模块名。
- **F-140**: 定义异常 `TypeHintParsingException` 和 `DocstringParsingException`。
- **F-141**: 函数 `get_json_schema(func: Callable) -> Dict` 基于 Google 格式 docstring 和类型注解生成 JSON Schema。
- **F-142**: 常量 `_BASE_TYPE_MAPPING` 映射 Python 基础类型到 JSON Schema 类型。

## 模块 12: `cli.py`

- **F-143**: 函数 `parse_arguments()` 使用 argparse 定义命令行参数：`prompt`、`--model-type`（默认 `"HfApiModel"`）、`--model-id`（默认 `"Qwen/Qwen2.5-Coder-32B-Instruct"`）、`--imports`、`--tools`（默认 `["web_search"]`）、`--verbosity-level`、`--api-base`、`--api-key`。
- **F-144**: 函数 `load_model(model_type, model_id, api_base, api_key)` 根据 model_type 创建对应模型实例。
- **F-145**: 函数 `run_smolagent(prompt, tools, model_type, model_id, ...)` 创建 `CodeAgent` 实例并调用 `agent.run(prompt)`。

## 模块 13: `gradio_ui.py`

- **F-146**: 函数 `stream_to_gradio(agent, task, ...)` 是生成器，调用 `agent.run(stream=True)` 逐步 yield `gr.ChatMessage`。
- **F-147**: 定义 `GradioUI` 类，构造接收 `agent: MultiStepAgent`；提供 `launch()` 和 `create_app()` 方法创建 Gradio 聊天界面。

## 模块 14: `remote_executors.py`

- **F-148**: 定义 `RemotePythonExecutor(PythonExecutor)` 抽象类，`send_variables` 使用 pickle+base64 序列化变量。
- **F-149**: 定义 `E2BExecutor(RemotePythonExecutor)` 类，使用 `e2b_code_interpreter.Sandbox` 执行代码。
- **F-150**: 定义 `DockerExecutor(RemotePythonExecutor)` 类，通过 Jupyter Kernel Gateway 在 Docker 容器中执行代码，使用 WebSocket 通信。

## 模块 15: `tool_validation.py`

- **F-151**: 定义 `MethodChecker(ast.NodeVisitor)` 类，检查 Tool 方法中的未定义名称。
- **F-152**: 函数 `validate_tool_attributes(cls, check_imports=True)` 使用 AST 分析验证 Tool 子类的正确性。

## 模块 16: `prompts/code_agent.yaml`

- **F-153**: `code_agent.yaml` 包含顶层键：`system_prompt`、`planning`、`managed_agent`、`final_answer`。
- **F-154**: `system_prompt` 指示 LLM 通过 ````py ... ```` 代码块执行操作，使用 `final_answer()` 返回答案，以 `<end_code>` 标记结束。

## 模块 17: `prompts/toolcalling_agent.yaml`

- **F-155**: `toolcalling_agent.yaml` 结构与 code_agent.yaml 相同，但 system_prompt 指示 LLM 使用 JSON 格式的 tool_calls 调用工具。

## 模块依赖关系

- **F-156**: `agents.py`（核心层）依赖 9 个内部模块：agent_types、default_tools、local_python_executor、memory、models、monitoring、remote_executors、tools、utils。
- **F-157**: `tools.py` 依赖 _function_type_hints_utils、agent_types、utils；被 agents.py、default_tools.py、remote_executors.py 依赖。
- **F-158**: `models.py` 相对独立，主要依赖第三方库；被 agents.py、monitoring.py、memory.py 依赖。
- **F-159**: `memory.py` 依赖 agent_types 和 models；被 agents.py、gradio_ui.py 依赖。
- **F-160**: `local_python_executor.py` 定义 PythonExecutor 基类和 LocalPythonExecutor；被 agents.py、remote_executors.py、default_tools.py 依赖。
- **F-161**: `utils.py` 是最底层工具模块，仅依赖标准库；被多个模块依赖。
