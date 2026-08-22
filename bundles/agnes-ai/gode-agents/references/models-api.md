---
type: Reference
title: Models API 参考
description: codified-smolagents 模型层API参考，包含Model基类、ChatMessage消息结构、MessageRole枚举及各模型实现类
tags: [Model, LLM, ChatMessage, TransformersModel, HfApiModel, LiteLLMModel, OpenAIServerModel, API参考]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-22T22:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-22T22:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: models-source
    resource: ../../../../../../external/libs/models/AgnesAI/GodeAgents/Multi-Agent-Task/src/codified-smolagents/models.py
    title: codified-smolagents/models.py
---

# Models API 参考

本文件记录 `models.py` 模块中的模型抽象层和实现，基于源码零推测事实 F-061 ~ F-081。

## 概述

模型层提供了统一的语言模型调用接口，支持多种后端：本地Transformers模型、Hugging Face Inference API、LiteLLM（支持数百个LLM提供商）、OpenAI兼容API、Azure OpenAI、Amazon Bedrock、vLLM本地推理和MLX（Apple Silicon）。所有模型类继承自 `Model` 基类，统一输入输出为 `ChatMessage` 数据类。

> 事实溯源：F-063、F-067~F-078

## 枚举与数据类

### MessageRole

```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool-call"
    TOOL_RESPONSE = "tool-response"

    @classmethod
    def roles(cls) -> list[str]
```

消息角色枚举，定义5种角色：用户（user）、助手（assistant）、系统（system）、工具调用（tool-call）、工具响应（tool-response）。`roles()` 类方法返回所有角色值的列表。

> 事实溯源：F-061

### ChatMessageToolCallDefinition

```python
@dataclass
class ChatMessageToolCallDefinition:
    arguments: Any
    name: str
    description: Optional[str] = None
```

工具调用的函数定义数据类，包含参数、函数名和可选描述。

### ChatMessageToolCall

```python
@dataclass
class ChatMessageToolCall:
    function: ChatMessageToolCallDefinition
    id: str
    type: str
```

工具调用数据类，包含函数定义、调用ID和类型（通常为"function"）。

### ChatMessage

```python
@dataclass
class ChatMessage:
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ChatMessageToolCall]] = None
    raw: Optional[Any] = None
```

聊天消息数据类，是模型输入输出的统一格式。

**字段：**
- `role` (`str`): 消息角色（使用MessageRole值）
- `content` (`Optional[str]`): 消息文本内容
- `tool_calls` (`Optional[List[ChatMessageToolCall]]`): 工具调用列表
- `raw` (`Optional[Any]`): 原始API响应（不参与序列化）

**方法：**
- `model_dump_json() -> str`: 序列化为JSON字符串
- `from_dict(data: dict, raw: Any = None) -> ChatMessage`: 从字典反序列化
- `dict() -> str`: 序列化为JSON字符串
- `from_hf_api(message, raw) -> ChatMessage`: 从HF API响应创建（已废弃）

> 事实溯源：F-062

## Model 基类

```python
class Model
```

所有模型的抽象基类，定义统一的调用接口和通用功能。

> 事实溯源：F-063

### 构造函数

```python
def __init__(
    self,
    flatten_messages_as_text: bool = False,
    tool_name_key: str = "name",
    tool_arguments_key: str = "arguments",
    **kwargs,
)
```

**参数：**
- `flatten_messages_as_text` (`bool`, 默认`False`): 是否将消息扁平化为纯文本
- `tool_name_key` (`str`, 默认`"name"`): 工具名称在工具调用JSON中的键名
- `tool_arguments_key` (`str`, 默认`"arguments"`): 工具参数在工具调用JSON中的键名
- `**kwargs`: 传递给具体实现的额外参数

初始化属性：`last_input_token_count`、`last_output_token_count`（初始None）。

> 事实溯源：F-064

### 核心方法

#### __call__

```python
def __call__(
    self,
    messages: List[Dict[str, str]],
    stop_sequences: Optional[List[str]] = None,
    grammar: Optional[str] = None,
    tools_to_call_from: Optional[List[Tool]] = None,
    **kwargs,
) -> ChatMessage
```

模型调用的抽象方法，子类必须实现。接收消息列表，返回 `ChatMessage`。

**参数：**
- `messages` (`List[Dict[str, str]]`): 消息列表，每个字典包含 `role` 和 `content`
- `stop_sequences` (`Optional[List[str]]`): 停止序列列表
- `grammar` (`Optional[str]`): 输出语法约束
- `tools_to_call_from` (`Optional[List[Tool]]`): 可调用的工具列表
- `**kwargs`: 额外参数

> 事实溯源：F-063

#### _prepare_completion_kwargs

```python
def _prepare_completion_kwargs(
    self,
    messages: List[Dict[str, str]],
    stop_sequences: Optional[List[str]] = None,
    grammar: Optional[str] = None,
    tools_to_call_from: Optional[List[Tool]] = None,
    custom_role_conversions: dict[str, str] | None = None,
    convert_images_to_image_urls: bool = False,
    **kwargs,
) -> Dict
```

准备模型调用参数，处理消息清理、工具JSON Schema生成、参数优先级（显式kwargs > 特定参数 > self.kwargs默认值）。

**参数优先级：** 1. 显式传入kwargs > 2. 特定参数（stop_sequences等） > 3. self.kwargs默认值

> 事实溯源：F-065

#### get_token_counts

```python
def get_token_counts(self) -> Dict[str, int]
```

返回token计数字典：`{"input_token_count": ..., "output_token_count": ...}`。

> 事实溯源：F-066

#### to_dict

```python
def to_dict(self) -> Dict
```

将模型序列化为JSON兼容字典。出于安全考虑，`token` 和 `api_key` 属性不会被导出。

#### from_dict

```python
@classmethod
def from_dict(cls, model_dictionary: Dict[str, Any]) -> "Model"
```

从字典反序列化模型实例。

## 本地模型类

### TransformersModel

```python
class TransformersModel(Model)
```

使用 Hugging Face Transformers 库本地加载模型。支持自回归语言模型（AutoModelForCausalLM）和视觉语言模型（AutoModelForImageTextToText），后者加载失败时自动回退到前者。

**构造参数：**
- `model_id` (`Optional[str]`): Hugging Face模型ID，默认 `"HuggingFaceTB/SmolLM2-1.7B-Instruct"`（v2.0.0后将为必需参数）
- `device_map` (`Optional[str]`): 设备映射，默认自动检测（CUDA可用时用cuda，否则cpu）
- `torch_dtype` (`Optional[str]`): PyTorch数据类型
- `trust_remote_code` (`bool`, 默认`False`): 是否信任远程代码
- `**kwargs`: 传递给model.generate()的参数，默认max_new_tokens=5000

需要安装 `smolagents[transformers]`。

> 事实溯源：F-067、F-068

### VLLMModel

```python
class VLLMModel(Model)
```

使用 vLLM 进行本地快速推理，支持高吞吐量推理。构造参数为 `model_id` 和 `model_kwargs`。需要安装 `smolagents[vllm]`。

> 事实溯源：F-077

### MLXModel

```python
class MLXModel(Model)
```

使用 MLX 在 Apple Silicon 上推理。默认 `flatten_messages_as_text=True`（不支持视觉模型）。构造参数为 `model_id`、`tool_name_key`、`tool_arguments_key`、`trust_remote_code`。需要安装 `smolagents[mlx-lm]`。

> 事实溯源：F-078

## API模型类

### ApiModel

```python
class ApiModel(Model)
```

API模型基类，为基于外部API的模型提供通用功能。管理model_id、自定义角色映射和API客户端连接。

**构造参数：**
- `model_id` (`str`): API使用的模型标识符
- `custom_role_conversions` (`dict[str, str] | None`): 角色名称映射
- `client` (`Any | None`): 预配置的API客户端实例

**方法：**
- `create_client()`: 创建API客户端（子类必须实现）
- `postprocess_message(message, tools_to_call_from) -> ChatMessage`: 后处理API响应，尝试解析工具调用

> 事实溯源：models.py中ApiModel定义

### HfApiModel

```python
class HfApiModel(ApiModel)
```

使用 Hugging Face Inference API 的模型类。

**构造参数：**
- `model_id` (`str`, 默认 `"Qwen/Qwen2.5-Coder-32B-Instruct"`): 模型ID或推理端点URL
- `provider` (`Optional[str]`): 推理提供商（"replicate"、"together"、"fal-ai"、"sambanova"、"hf-inference"）
- `token` (`Optional[str]`): HF API令牌，默认从环境变量 `HF_TOKEN` 获取
- `timeout` (`Optional[int]`, 默认120): 请求超时秒数
- `client_kwargs` (`dict[str, Any] | None`): 传递给InferenceClient的额外参数
- `custom_role_conversions` (`dict[str, str] | None`): 自定义角色映射

使用 `huggingface_hub.InferenceClient`，调用 `client.chat_completion()` 完成推理。

> 事实溯源：F-069、F-070

### LiteLLMModel

```python
class LiteLLMModel(ApiModel)
```

使用 LiteLLM SDK 访问数百个LLM提供商（OpenAI、Anthropic、Azure、Bedrock、Ollama、Groq等）。

**构造参数：**
- `model_id` (`Optional[str]`, 默认 `"anthropic/claude-3-5-sonnet-20240620"`): 模型标识符
- `api_base` (`Optional[str]`): API基础URL
- `api_key` (`Optional[str]`): API密钥
- `custom_role_conversions` (`dict[str, str] | None`): 自定义角色映射
- `flatten_messages_as_text` (`bool | None`): 是否扁平化消息，模型ID以ollama/groq/cerebras开头时自动设为True

需要安装 `smolagents[litellm]`。

> 事实溯源：F-071、F-072

### OpenAIServerModel

```python
class OpenAIServerModel(ApiModel)
```

连接到OpenAI兼容的API服务器。

**构造参数：**
- `model_id` (`str`): 模型标识符
- `api_base` (`Optional[str]`): API基础URL
- `api_key` (`Optional[str]`): API密钥
- `organization` (`Optional[str]`): OpenAI组织ID
- `project` (`Optional[str]`): OpenAI项目ID
- `client_kwargs` (`dict[str, Any] | None`): 传递给OpenAI客户端的额外参数
- `flatten_messages_as_text` (`bool`, 默认`False`): 是否扁平化消息为文本

使用 `openai.OpenAI` 客户端，调用 `client.chat.completions.create()`。

> 事实溯源：F-073、F-074

### AzureOpenAIServerModel

```python
class AzureOpenAIServerModel(OpenAIServerModel)
```

连接到 Azure OpenAI 部署，继承自OpenAIServerModel。额外参数：
- `azure_endpoint` (`Optional[str]`): Azure端点URL（默认从 `AZURE_OPENAI_ENDPOINT` 环境变量获取）
- `api_version` (`Optional[str]`): API版本（默认从 `OPENAI_API_VERSION` 环境变量获取）

使用 `openai.AzureOpenAI` 客户端。

> 事实溯源：F-075

### AmazonBedrockServerModel

```python
class AmazonBedrockServerModel(ApiModel)
```

通过 Amazon Bedrock API 与模型交互，使用boto3客户端。支持推理配置（inferenceConfig）和护栏配置（guardrailConfig）。

**构造参数：**
- `model_id` (`str`): Bedrock模型ID（如 "us.amazon.nova-pro-v1:0"）
- `client`: 自定义boto3客户端
- `client_kwargs` (`dict[str, Any] | None`): boto3客户端配置（region_name、config、endpoint_url等）
- `custom_role_conversions` (`dict[str, str] | None`): 自定义角色映射，默认将所有角色转换为"user"
- `flatten_messages_as_text` (`bool`, 默认`False`): 是否扁平化消息为文本

> 事实溯源：F-076

## 工具函数

### get_tool_json_schema

```python
def get_tool_json_schema(tool: Tool) -> Dict
```

将Tool实例转换为OpenAI function calling格式的JSON Schema。处理"any"类型为"string"，根据nullable属性构建required列表。

**返回格式：**
```python
{
    "type": "function",
    "function": {
        "name": tool.name,
        "description": tool.description,
        "parameters": {
            "type": "object",
            "properties": { ... },
            "required": [ ... ]
        }
    }
}
```

> 事实溯源：F-079

### get_clean_message_list

```python
def get_clean_message_list(
    message_list: List[Dict[str, str]],
    role_conversions: Dict[MessageRole, MessageRole] = {},
    convert_images_to_image_urls: bool = False,
    flatten_messages_as_text: bool = False,
) -> List[Dict[str, str]]
```

清理和标准化消息列表：
1. 合并连续同角色消息
2. 应用角色转换映射
3. 处理图片编码（base64或image_url格式）
4. 扁平化多模态消息为纯文本（当flatten_messages_as_text=True时）

> 事实溯源：F-080

### get_tool_call_from_text

```python
def get_tool_call_from_text(
    text: str,
    tool_name_key: str,
    tool_arguments_key: str,
) -> ChatMessageToolCall
```

从文本中解析JSON格式的工具调用，返回 `ChatMessageToolCall`。自动生成UUID作为调用ID。

> 事实溯源：F-081

### 其他工具函数

- `parse_json_if_needed(arguments)`: 如果参数是字符串则解析为JSON字典
- `remove_stop_sequences(content, stop_sequences)`: 从内容末尾移除停止序列
- `get_dict_from_nested_dataclasses(obj, ignore_key=None)`: 将嵌套dataclass递归转换为字典

## 默认语法规则

```python
DEFAULT_JSONAGENT_REGEX_GRAMMAR = {
    "type": "regex",
    "value": 'Thought: .+?\\nAction:\\n\\{\\n\\s{4}"action":\\s"[^"\\n]+",\\n\\s{4}"action_input":\\s"[^"\\n]+"\\n\\}\\n<end_code>'
}

DEFAULT_CODEAGENT_REGEX_GRAMMAR = {
    "type": "regex",
    "value": "Thought: .+?\\nCode:\\n```(?:py|python)?\\n(?:.|\\s)+?\\n```<end_code>"
}
```

JSON Agent和Code Agent的默认正则语法约束。

## 相关概念

- [模型层概述](/concepts/model-layer.md) — Model抽象层设计和多后端支持
- [工具调用智能体](/concepts/tool-calling-agent.md) — ToolCallingAgent与模型工具调用的交互
- [代码执行智能体](/concepts/code-agent.md) — CodeAgent与模型的代码生成交互
- [智能体API参考](/references/agents-api.md) — Agent如何调用Model
- [工具API参考](/references/tools-api.md) — Tool与Model的JSON Schema转换
