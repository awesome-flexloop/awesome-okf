# GodeAgents (codified-smolagents) 架构洞察

> I阶段产出：基于F-001~F-161事实清单提炼的5个核心洞察四元组与知识地图。

## 洞察 I-01：双智能体范式——ToolCalling vs CodeAct

**陈述**：GodeAgents 在统一的 `MultiStepAgent` 基类下实现了两种本质不同的推理范式：`ToolCallingAgent` 使用 JSON 格式的 function calling，`CodeAgent` 使用 Python 代码块（CodeAct）作为行动语言。两者共享 `run()` 循环、记忆系统、规划机制，但 `step()` 方法的实现完全不同。

**证据**：
- F-032/F-036：ToolCallingAgent.step() 调用 model 时传入 `tools_to_call_from`，从 `model_message.tool_calls[0]` 解析工具调用
- F-039/F-045：CodeAgent.step() 调用 model 时不传 tools_to_call_from，而是从模型输出中解析 ````py` 代码块，通过 `python_executor` 执行
- F-018：`_setup_tools` 中 `python_interpreter` 仅对 ToolCallingAgent 保留，CodeAgent 通过内置的 `PythonInterpreterTool` 获得代码执行能力
- F-034/F-042：两者使用不同的默认 YAML 提示模板（toolcalling_agent.yaml vs code_agent.yaml）

**反常识**：CodeAgent 不是 ToolCallingAgent 的超集——CodeAgent 的工具通过在 Python 执行环境中注入工具函数来调用（F-116），而非通过 LLM 的 function calling API。这意味着 CodeAgent 可以在一个代码块中组合多个工具调用、使用变量传递中间结果、编写循环和条件判断，表达能力远超单步 JSON tool calls。

**行动**：文档需分别阐述两种智能体类型的适用场景，并明确其 step() 方法的差异。初学者应先理解 MultiStepAgent 的统一 run 循环，再分别学习两种 step 实现。

---

## 洞察 I-02：记忆即步骤序列——MemoryStep 状态机

**陈述**：AgentMemory 不是键值存储或向量数据库，而是一个严格时序的 MemoryStep 列表，每个步骤是一个不可变的数据类实例。系统运行过程表现为 MemoryStep 子类的有序序列：SystemPromptStep → TaskStep → [PlanningStep → ActionStep*] → FinalAnswerStep。

**证据**：
- F-084/F-092：MemoryStep 是基类，AgentMemory.steps 是 List[Union[TaskStep, ActionStep, PlanningStep]]
- F-087/F-088：ActionStep 包含完整的单步信息（模型输入输出、工具调用、观察结果、错误、耗时）
- F-089/F-090：PlanningStep 包含规划输出，to_messages 返回 assistant+user 双消息（防模型续写计划）
- F-021：_run() 方法在第1步和每隔 planning_interval 步时插入 PlanningStep
- F-023：write_memory_to_messages 将所有 steps 序列化平铺为消息列表发送给模型

**反常识**：记忆系统没有"检索"或"压缩"机制（无 RAG/向量检索/摘要截断），而是通过 `summary_mode=True` 时 PlanningStep 返回空消息（F-090）实现轻量级"遗忘"——规划步骤在摘要模式下不输出。完整上下文始终在 steps 列表中，由 LLM 上下文窗口限制自然截断。

**行动**：概念文档需以步骤序列为主线讲解记忆系统，重点说明 ActionStep 的字段含义和 to_messages 的消息序列格式。

---

## 洞察 I-03：沙箱代码执行——AST 级安全解释器

**陈述**：CodeAgent 的代码执行不使用 `eval()/exec()` 在全局命名空间中直接运行，而是通过 `LocalPythonExecutor` 实现了一个基于 AST 遍历的受限 Python 解释器。该解释器逐节点解析 Python AST，在白名单命名空间中求值，禁止危险模块导入和危险函数调用。

**证据**：
- F-114：run_code_raise_errors 使用 ast.parse 解析代码，通过 _check_imports AST访问器验证 import 安全性
- F-106/F-107：DANGEROUS_MODULES（os/subprocess/sys/shutil等）和 DANGEROUS_FUNCTIONS（eval/exec/compile/globals等）被显式禁止
- F-108：BASE_PYTHON_TOOLS 提供安全的内置函数子集，print 被替换为 custom_print（返回 None）
- F-105/F-119：MAX_OPERATIONS=10000000 和 MAX_WHILE_ITERATIONS=1000000 防止无限循环
- F-115：final_answer() 在执行器中通过抛出 FinalAnswerException 实现提前返回
- F-116：工具通过 send_tools 以函数形式注入执行器命名空间

**反常识**：`fix_final_answer_code()` 函数（F-118）专门处理 LLM 将 `final_answer` 当作变量赋值的错误模式——将 `final_answer = ...` 替换为 `final_answer_variable = ...`，防止覆盖 final_answer() 函数。这是一个针对 LLM 特有错误模式的防御性编程。

**行动**：概念文档需单独讲解 PythonExecutor 的安全机制，列出禁止的模块和函数，并解释 final_answer 的异常实现机制。

---

## 洞察 I-04：模型抽象层——统一接口多后端

**陈述**：Model 基类定义了统一的 `__call__(messages, stop_sequences, grammar, tools_to_call_from) -> ChatMessage` 接口，在此之上实现了 7+ 种模型后端（本地 Transformers、vLLM、MLX，远程 HF API、LiteLLM、OpenAI 兼容、Azure OpenAI、Amazon Bedrock），新增后端只需继承 Model 并实现 __call__ 和 create_client。

**证据**：
- F-063/F-064：Model 基类定义 __call__ 抽象方法和 token 计数属性
- F-065：_prepare_completion_kwargs 统一处理消息清理、工具Schema转换、参数优先级
- F-067~F-078：7+ 个子类分别实现不同推理后端
- F-079/F-080：get_tool_json_schema 和 get_clean_message_list 是模型层共享的消息处理工具
- F-081：get_tool_call_from_text 统一从文本解析工具调用，兼容不原生支持 function calling 的模型

**反常识**：ApiModel.postprocess_message（F-060之后）会在API返回的tool_calls为空时，尝试从content文本中解析JSON格式的工具调用——这意味着即使模型/API不原生支持function calling，也能通过文本解析实现工具调用能力。这是 VLLMModel 和 MLXModel 等本地模型的统一处理方式。

**行动**：概念文档以 Model 基类为核心，对比各后端的初始化参数差异，重点讲解 _prepare_completion_kwargs 的参数优先级逻辑。

---

## 洞察 I-05：工具系统——装饰器即定义，Schema 自动生成

**陈述**：工具系统的核心设计是 `@tool` 装饰器+类型注解+Google风格docstring=完整工具定义。装饰器自动从函数签名生成JSON Schema（inputs定义），从docstring生成描述，Tool基类统一处理参数校验、序列化、输入输出类型转换。

**证据**：
- F-047~F-051：Tool基类定义 name/description/inputs/output_type 四要素和 forward/__call__ 方法
- F-056：@tool 装饰器将普通函数转为Tool实例
- F-141：get_json_schema 从类型注解+Google docstring生成JSON Schema
- F-142：_BASE_TYPE_MAPPING 映射Python类型到JSON Schema类型，额外处理PIL.Image和torch.Tensor
- F-104：handle_agent_output_types 自动将工具输出转换为AgentType子类（图片→AgentImage等）
- F-052/F-054：Tool支持to_dict()序列化和from_code()动态加载

**反常识**：Tool.__init__ 通过 `self.__dict__.update(kwargs)` 接收任意关键字参数设置为实例属性（F-049），而非定义显式的 __init__ 参数列表。这使得Tool子类可以灵活添加自定义属性，但也意味着IDE无法提供自动补全。

**行动**：概念文档以 @tool 装饰器为入口点讲解工具开发，强调类型注解和docstring的格式要求，示例展示自定义工具的完整流程。

---

## 知识地图（学习路径设计）

### 文档分组

| 分组 | 文档数 | 覆盖事实 | 学习目标 |
|------|--------|---------|---------|
| **入门** | 3 | F-001,F-013,F-032,F-039,F-192~F-195 | 了解框架是什么、如何安装、第一个Agent |
| **核心架构** | 4 | F-013~F-031 | 理解MultiStepAgent的run循环、记忆、规划 |
| **智能体类型** | 2 | F-032~F-046 | 掌握ToolCallingAgent和CodeAgent的差异 |
| **工具系统** | 2 | F-047~F-060,F-120~F-125,F-139~F-142 | 掌握内置工具和自定义工具开发 |
| **模型层** | 1 | F-061~F-081 | 理解Model抽象和多后端 |
| **执行与安全** | 2 | F-105~F-119,F-148~F-150 | 理解代码执行沙箱和远程执行 |
| **基础设施** | 1 | F-082~F-096,F-126~F-138 | 记忆、日志、工具函数 |

### 概念文档列表（15篇）

| 编号 | 文件名 | 标题 | 覆盖事实 |
|------|--------|------|---------|
| 00 | 00-introduction.md | 简介：编码式多智能体推理 | F-001,F-192~F-195 |
| 01 | 01-getting-started.md | 快速开始 | F-143~F-145 |
| 02 | 02-architecture-overview.md | 架构总览 | F-002~F-005,F-156~F-161 |
| 03 | 03-multi-step-agent.md | MultiStepAgent 核心循环 | F-013~F-031 |
| 04 | 04-memory-system.md | 记忆系统：步骤序列 | F-082~F-096 |
| 05 | 05-tool-calling-agent.md | ToolCallingAgent：函数调用范式 | F-032~F-038 |
| 06 | 06-code-agent.md | CodeAgent：代码执行范式 | F-039~F-046,F-105~F-119 |
| 07 | 07-tool-system.md | 工具系统：@tool装饰器与Tool基类 | F-047~F-060,F-139~F-142 |
| 08 | 08-builtin-tools.md | 内置工具详解 | F-120~F-125 |
| 09 | 09-model-layer.md | 模型抽象层与多后端 | F-061~F-081 |
| 10 | 10-agent-types.md | AgentType 多模态类型系统 | F-097~F-104 |
| 11 | 11-python-executor.md | Python 执行器与安全沙箱 | F-105~F-119 |
| 12 | 12-prompt-templates.md | 提示词模板系统 | F-006~F-012,F-153~F-155 |
| 13 | 13-monitoring-logging.md | 监控与日志 | F-126~F-128 |
| 14 | 14-advanced-features.md | 高级特性：Managed Agents、远程执行、UI | F-017,F-146~F-152 |

### 示例文档列表（7篇）

| 编号 | 文件名 | 标题 |
|------|--------|------|
| 01 | 01-first-agent.md | 创建第一个 ToolCallingAgent |
| 02 | 02-code-agent-basic.md | 创建 CodeAgent 执行 Python 代码 |
| 03 | 03-custom-tool.md | 使用 @tool 装饰器创建自定义工具 |
| 04 | 04-web-search-agent.md | 构建网页搜索 Agent |
| 05 | 05-different-models.md | 使用不同模型后端 |
| 06 | 06-vision-browser.md | 视觉网页浏览器 Agent |
| 07 | 07-planning-interval.md | 使用规划间隔实现 Plan-and-Execute |

### 信源参考列表（7篇）

| 文件名 | 内容 |
|--------|------|
| agents-api.md | MultiStepAgent/ToolCallingAgent/CodeAgent 完整 API |
| tools-api.md | Tool基类/@tool/ToolCollection/内置工具 API |
| models-api.md | Model基类及所有子类 API |
| memory-api.md | AgentMemory/MemoryStep子类/ToolCall API |
| executor-api.md | PythonExecutor/LocalPythonExecutor/远程执行器 API |
| utils-api.md | 工具函数、异常类、AgentLogger API |
| prompts-reference.md | YAML 提示模板结构与变量参考 |
