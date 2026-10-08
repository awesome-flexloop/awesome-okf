---
type: Concept
title: AgentType 多模态类型系统
description: AgentText/AgentImage/AgentAudio多模态类型、输入输出类型自动转换
tags: [多模态, AgentType, 图片, 音频, 类型系统]
generated: { by: "agent:source-code-to-okf-wiki", at: "2026-08-22T12:30:00+08:00" }
status: stable
stale_after: 2027-08-22
sources:
  - id: F-097
    resource: /references/utils-api.md
    title: Utils API 参考
  - id: F-103
    resource: /references/memory-api.md
    title: Memory API 参考
---

# AgentType 多模态类型系统

## 概述

AgentType 是 GodeAgents 框架中统一表示 Agent 输入输出数据的多模态类型系统。框架定义了 `AgentType` 基类，并派生出 `AgentText`（文本）、`AgentImage`（图片）、`AgentAudio`（音频）三个具体子类，使 Agent 能够以统一的方式处理文本、图像和音频数据。配合 `handle_agent_input_types()` 和 `handle_agent_output_types()` 两个转换函数，框架在工具调用前后自动完成多模态数据与原始类型之间的转换，开发者无需手动处理文件路径、字节流或张量格式的差异。

> 事实溯源：F-097~F-104

## 核心概念

### AgentType 基类设计

`AgentType` 是所有多模态类型的抽象基类，采用值封装模式：构造时接收原始值并存储为 `self._value`，通过 `to_raw()` 获取原始值，`to_string()` 则由子类实现具体的字符串/路径表示。

| 方法 | 说明 |
|------|------|
| `__init__(value)` | 接收原始值，存储为 `self._value` |
| `to_raw()` | 返回原始值（未经包装的 Python 对象） |
| `to_string()` | 返回字符串表示，基类中抛 `NotImplementedError` |

这种设计使得所有 Agent 输入输出都可以被统一处理，同时保留原始数据的完整性。

> 事实溯源：F-097~F-099

### AgentText：文本类型

`AgentText` 继承自 `AgentType`，用于包装字符串值。其 `to_string()` 方法直接返回内部存储的字符串值。这是最常用的类型，所有纯文本的工具输入输出都通过 `AgentText` 传递。

> 事实溯源：F-100

### AgentImage：图片类型

`AgentImage` 同时继承自 `AgentType` 和 `PIL.Image.Image`，是最复杂的多模态类型，支持多种输入格式：

| 输入格式 | 说明 |
|----------|------|
| `PIL.Image.Image` | 直接接收 PIL 图像对象 |
| `bytes` | 图像字节数据（自动解码） |
| `str`（路径） | 图像文件路径（自动加载） |
| `torch.Tensor` | PyTorch 张量格式的图像数据 |

`AgentImage` 提供以下核心方法：
- `to_string()`：返回图片文件路径（若内存中的图像则先保存为临时文件再返回路径）
- `save_to_file(path)`：将图像保存到指定文件路径
- `to_raw()`：返回原始图像数据（PIL Image 对象）

> 事实溯源：F-101

### AgentAudio：音频类型

`AgentAudio` 继承自 `AgentType`，用于包装音频数据，支持：
- 音频文件路径（`str`）
- 音频原始数据（字节流或 numpy 数组）

核心方法：
- `to_string()`：返回音频文件路径（内存中数据先保存为临时文件）
- `save_to_file(path)`：将音频保存到指定文件路径

> 事实溯源：F-102

### 输入输出类型自动转换

框架通过两个核心函数实现多模态类型的自动转换：

**`handle_agent_input_types(tool_name, arguments, state)`**

在工具调用前，自动检测 `arguments` 中的 `AgentImage` 和 `AgentAudio` 实例，将它们转换为文件路径字符串，使工具函数可以直接使用路径访问多媒体文件，无需关心原始数据格式。

**`handle_agent_output_types(output, observations_images=None)`**

在工具执行后，将原始输出值包装为对应的 `AgentType` 子类实例：
- 字符串 → `AgentText`
- PIL Image / 字节 / 路径 / 张量 → `AgentImage`
- 音频相关数据 → `AgentAudio`

这两个函数构成了多模态工具调用的"类型桥梁"。

> 事实溯源：F-103~F-104

## API 要点

### AgentType 类层次

```python
class AgentType:
    """多模态类型基类"""
    def __init__(self, value):
        self._value = value

    def to_raw(self):
        """返回原始值"""
        return self._value

    def to_string(self):
        """返回字符串表示，子类必须实现"""
        raise NotImplementedError


class AgentText(AgentType):
    """文本类型"""
    def to_string(self) -> str:
        return str(self._value)


class AgentImage(AgentType, PIL.Image.Image):
    """图片类型，同时继承AgentType和PIL.Image.Image"""
    def __init__(self, value):
        # value 可以是 PIL.Image / bytes / 文件路径str / torch.Tensor
        ...

    def to_string(self) -> str:
        """返回图片文件路径"""
        ...

    def save_to_file(self, path: str):
        """保存图片到文件"""
        ...

    def to_raw(self):
        """返回原始图像数据"""
        ...


class AgentAudio(AgentType):
    """音频类型"""
    def __init__(self, value):
        # value 可以是音频文件路径或音频数据
        ...

    def to_string(self) -> str:
        """返回音频文件路径"""
        ...

    def save_to_file(self, path: str):
        """保存音频到文件"""
        ...
```

> 事实溯源：F-097~F-102

### 类型转换函数

```python
def handle_agent_input_types(
    tool_name: str,
    arguments: dict,
    state: dict,
) -> dict:
    """
    处理工具输入中的多模态类型。
    将 AgentImage/AgentAudio 转换为文件路径字符串。
    返回转换后的 arguments 字典。
    """
    ...

def handle_agent_output_types(
    output: Any,
    observations_images: Optional[list] = None,
) -> AgentType:
    """
    将工具输出转换为 AgentType 子类实例。
    - str → AgentText
    - PIL.Image/bytes/path/tensor → AgentImage
    - 音频数据 → AgentAudio
    """
    ...
```

> 事实溯源：F-103~F-104

## 代码示例

### 基本类型操作

```python
from codified_smolagents import AgentText, AgentImage, AgentAudio

# AgentText：文本包装
text = AgentText("Hello, World!")
print(text.to_string())   # "Hello, World!"
print(text.to_raw())      # "Hello, World!"（原始值）

# AgentImage：从文件路径创建
img = AgentImage("path/to/image.png")
print(img.to_string())    # 返回图片文件路径
img.save_to_file("output/copy.png")  # 保存到新路径
raw_img = img.to_raw()    # 获取PIL Image对象

# AgentImage：从PIL Image创建
from PIL import Image
pil_img = Image.new("RGB", (100, 100), color="red")
img2 = AgentImage(pil_img)
path = img2.to_string()   # 内存中的图像先保存为临时文件，返回路径

# AgentImage：从字节创建
with open("photo.jpg", "rb") as f:
    img_bytes = f.read()
img3 = AgentImage(img_bytes)

# AgentAudio：从文件路径创建
audio = AgentAudio("path/to/audio.wav")
print(audio.to_string())  # 返回音频文件路径
audio.save_to_file("output/copy.wav")
```

### 多模态工具调用中的自动转换

```python
from codified_smolagents import tool, handle_agent_input_types, handle_agent_output_types

# 定义一个接受图片路径的工具（框架自动将AgentImage转为路径）
@tool
def describe_image(image_path: str) -> str:
    """描述图片内容。

    Args:
        image_path: 图片文件的路径

    Returns:
        图片描述文本
    """
    from PIL import Image
    img = Image.open(image_path)
    return f"图片尺寸: {img.size}, 模式: {img.mode}"

# 手动演示输入转换
arguments = {"image_path": AgentImage("test.jpg")}
state = {}
converted = handle_agent_input_types("describe_image", arguments, state)
# converted["image_path"] 现在是文件路径字符串，而非AgentImage对象
print(converted["image_path"])  # "test.jpg"

# 手动演示输出转换
output = "这是一张风景照片"
result = handle_agent_output_types(output)
# result 是 AgentText 实例
print(type(result))        # <class 'AgentText'>
print(result.to_string())  # "这是一张风景照片"
```

### 在自定义Tool中处理多模态输出

```python
from codified_smolagents import Tool, AgentImage, AgentText
from PIL import Image

class GenerateImageTool(Tool):
    name = "generate_image"
    description = "根据文本描述生成图片"
    inputs = {
        "prompt": {
            "type": "string",
            "description": "图片描述文本",
        },
        "width": {
            "type": "integer",
            "description": "图片宽度（像素）",
            "nullable": True,
        },
    }
    output_type = "image"

    def forward(self, prompt: str, width: int = 512) -> AgentImage:
        # 模拟生成图片（实际中调用图像生成API）
        img = Image.new("RGB", (width, width), color="blue")
        # 返回AgentImage，框架会自动处理
        return AgentImage(img)

class AnalyzeTextTool(Tool):
    name = "analyze_text"
    description = "分析文本并返回结果"
    inputs = {
        "text": {
            "type": "string",
            "description": "要分析的文本",
        }
    }
    output_type = "string"

    def forward(self, text: str) -> AgentText:
        word_count = len(text.split())
        result = f"文本包含 {word_count} 个单词"
        return AgentText(result)

# 使用工具
gen_tool = GenerateImageTool()
result = gen_tool(prompt="一片宁静的湖面", width=256)
# result 是 AgentImage 实例
print(type(result))        # AgentImage
print(result.to_string())  # 临时文件路径
```

### 多模态Agent工作流

```python
from codified_smolagents import CodeAgent, HfApiModel, AgentImage
from PIL import Image

# 创建支持多模态的Agent
model = HfApiModel()
agent = CodeAgent(
    tools=[],  # 可添加支持图片的工具
    model=model,
    additional_authorized_imports=['PIL', 'io', 'base64'],
    max_steps=5,
)

# Agent可以接收图片输入
# 图片通过AgentImage包装后作为任务输入
img = Image.open("input_photo.jpg")
task = AgentImage(img)
# 在多模态场景中，Agent能够理解和处理图片内容

# 当Agent返回图片时，输出为AgentImage
# result = agent.run(task)
# if isinstance(result, AgentImage):
#     result.save_to_file("output_result.png")
```

> 事实溯源：F-097~F-104

## 注意事项

### to_string() 可能触发临时文件创建

`AgentImage.to_string()` 和 `AgentAudio.to_string()` 对于内存中的数据（非路径输入）会先将数据保存为临时文件再返回路径。频繁调用可能产生大量临时文件，建议在批量处理时注意临时文件清理。

### AgentImage 的多重继承

`AgentImage` 同时继承 `AgentType` 和 `PIL.Image.Image`，这意味着它可以直接当作 PIL Image 使用（调用 PIL 的方法如 `.resize()`、`.crop()` 等），同时具备 `to_string()`、`save_to_file()`、`to_raw()` 等多模态类型接口。使用时注意这一特性，避免与 PIL 方法名冲突。

### 输入转换是原地修改 arguments

`handle_agent_input_types()` 会直接修改传入的 `arguments` 字典中的值（将 AgentType 实例替换为路径字符串），不是返回新的深拷贝。如果需要保留原始参数，应在调用前自行复制。

### observations_images 参数

`handle_agent_output_types()` 的 `observations_images` 参数用于附加图像观察结果列表。当工具执行产生附带的图像输出时，可以通过此参数传递，框架会将它们一并纳入输出处理。

### 张量输入需确保 torch 可用

`AgentImage` 支持 `torch.Tensor` 输入格式，但需要运行环境安装了 PyTorch。如果未安装 torch 而传入张量，将抛出运行时错误。

### to_raw() 返回类型取决于输入

`AgentImage.to_raw()` 返回的原始值类型取决于构造时传入的数据类型（PIL Image / bytes / 路径字符串 / Tensor），不一定总是 PIL Image 对象。需要特定类型时应自行转换。

## 相关链接

- [工具系统：@tool装饰器与Tool基类](07-tool-system.md) — Tool.__call__中sanitize_inputs_outputs触发类型转换
- [CodeAgent：代码执行范式](06-code-agent.md) — 代码执行中多模态数据如何传递
- [记忆系统：步骤序列](04-memory-system.md) — AgentType在记忆步骤中的存储
- [Python 执行器与安全沙箱](11-python-executor.md) — 执行器中对象的序列化与传递
- [Utils API 参考](../references/utils-api.md) — AgentType及转换函数完整API
