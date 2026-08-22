---
type: Example
title: 创建自定义 Persona
description: 从零开发一个自定义 AI Persona 并注册到 Jupyter AI 的完整示例
tags: [example, persona, extension, development, plugin]
sources:
  - id: personas-group
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/personas_group.md
    title: personas_group.md
  - id: entry-points
    resource: external/libs/jupyter/jupyter-ai/docs/source/developers/entry_points_api/index.md
    title: entry_points_api/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 创建自定义 Persona

本示例演示如何开发一个自定义 AI Persona（AI 角色），并通过 Python entry points 注册到 Jupyter AI 中。我们将创建一个"代码审查助手"Persona，它专门帮助用户审查和改进代码。

## 前提条件

- Python >= 3.9
- Jupyter AI 已安装（`pip install jupyter-ai`）
- `jupyter_ai_persona_manager` 包已安装（jupyter-ai 的依赖，通常已自动安装）
- 基本的 Python 包开发知识

## 项目结构

创建以下项目结构：

```
code-review-persona/
├── pyproject.toml
└── code_review_persona/
    ├── __init__.py
    └── persona.py
```

## 步骤 1：实现 Persona 类

创建 `code_review_persona/persona.py`：

```python
"""代码审查助手 Persona"""
from jupyter_ai_persona_manager import BasePersona
from jupyter_ai_persona_manager.api import PersonaDefaults
from jupyterlab_chat.models import Message, NewMessage


class CodeReviewPersona(BasePersona):
    """一个专门用于代码审查的 AI Persona。

    接收用户代码，提供审查意见和改进建议。
    本示例使用简单的规则引擎，实际应用中可接入 LLM。
    """

    @property
    def defaults(self) -> PersonaDefaults:
        """返回 Persona 的默认配置"""
        return PersonaDefaults(
            name="CodeReviewer",
            avatar_path="/api/ai/static/jupyternaut.svg",  # 可替换为自定义头像
            description="代码审查助手，帮你发现代码问题并提供改进建议",
            system_prompt=(
                "你是一个专业的代码审查助手。你的职责是：\n"
                "1. 检查代码中的潜在 bug 和安全问题\n"
                "2. 建议代码风格和可读性改进\n"
                "3. 推荐性能优化方案\n"
                "4. 给出具体的改进代码示例\n"
            ),
        )

    async def process_message(self, message: Message) -> None:
        """处理用户消息，生成审查回复"""
        code = message.body.strip()

        # 简单的代码审查逻辑（实际应用中调用 LLM）
        issues = []
        suggestions = []

        # 检查常见问题
        if "print(" in code and "logging" not in code:
            issues.append("- 考虑使用 logging 模块替代 print，便于日志管理")

        if "except:" in code or "except Exception:" in code:
            issues.append("- 避免裸 except 或捕获过宽的 Exception，应捕获具体异常类型")

        if "TODO" in code or "FIXME" in code:
            issues.append("- 代码中包含 TODO/FIXME 标记，请确保这些问题已被跟踪")

        if "==" is not None and "is None" not in code and "= None" in code:
            suggestions.append("- 判断是否为 None 应使用 'is None' 而非 '== None'")

        if len(code.split("\n")) > 50:
            suggestions.append("- 函数/代码块超过50行，建议拆分为更小的函数")

        # 构建回复
        if not issues and not suggestions:
            reply = "✅ 代码看起来不错！没有发现明显问题。"
        else:
            reply = "## 代码审查结果\n\n"
            if issues:
                reply += "### ⚠️ 需要注意的问题\n" + "\n".join(issues) + "\n\n"
            if suggestions:
                reply += "### 💡 改进建议\n" + "\n".join(suggestions) + "\n\n"
            reply += "请根据以上建议改进代码，如有疑问可以继续提问。"

        # 发送回复
        self.send_message(NewMessage(body=reply, sender=self.id))
```

## 步骤 2：创建包入口

创建 `code_review_persona/__init__.py`：

```python
from .persona import CodeReviewPersona

__all__ = ["CodeReviewPersona"]
```

## 步骤 3：配置 pyproject.toml

创建 `pyproject.toml`，关键是声明 entry point：

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "code-review-persona"
version = "0.1.0"
description = "A code review AI persona for Jupyter AI"
requires-python = ">=3.9"
dependencies = [
    "jupyter_ai_persona_manager>=0.1.2,<0.2.0",
    "jupyterlab_chat>=0.23.2,<0.24.0",
]

# 关键：注册 Persona 到 Jupyter AI
[project.entry-points."jupyter_ai.personas"]
code_reviewer = "code_review_persona:CodeReviewPersona"
```

## 步骤 4：安装开发版本

```bash
pip install -e .
```

## 步骤 5：测试 Persona

1. **重启 JupyterLab**（entry points 需要重启才能加载）
2. 打开聊天面板，创建新聊天
3. 在 Persona 选择器中找到 **CodeReviewer**
4. 发送一段代码测试：

```python
def process_data(data):
    try:
        result = data == None
        print(result)
        # TODO: add error handling
        return result
    except:
        return None
```

CodeReviewer 应该返回审查意见，指出 print、裸 except、== None、TODO 等问题。

## 进阶：接入 LLM

上面的示例使用简单规则引擎。实际使用中，可以接入 LLM 提供更智能的审查。以下是使用 LangChain + LiteLLM 的示例：

```python
from langchain_core.messages import HumanMessage, SystemMessage
from jupyter_ai_litellm import LiteLLMProvider

class LLMReviewPersona(BasePersona):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = LiteLLMProvider(model="openai:gpt-4")

    @property
    def defaults(self):
        return PersonaDefaults(
            name="LLMReviewer",
            avatar_path="/api/ai/static/jupyternaut.svg",
            description="基于 LLM 的代码审查助手",
            system_prompt="你是资深代码审查专家，请仔细审查用户提供的代码..."
        )

    async def process_message(self, message: Message):
        messages = [
            SystemMessage(content=self.defaults.system_prompt),
            HumanMessage(content=message.body)
        ]

        # 流式回复
        async def stream():
            async for chunk in self.llm.astream(messages):
                yield chunk.content

        await self.stream_message(stream())
```

记得在 `pyproject.toml` 中添加 `jupyter_ai_litellm` 依赖，并设置对应的 API Key 环境变量。

## 进阶：支持 MCP 工具调用

如果 Persona 需要使用 MCP 工具（如读取 Notebook 文件），可以在 process_message 中通过 `self` 访问工具调用接口。参考 jupyter-ai-jupyternaut 的实现。

## 打包发布

开发完成后：

1. 构建包：
   ```bash
   pip install build
   python -m build
   ```

2. 上传到 PyPI（或私有包索引）：
   ```bash
   pip install twine
   twine upload dist/*
   ```

3. 用户安装后即可在 Jupyter AI 中使用：
   ```bash
   pip install code-review-persona
   ```

## 常见问题

### Persona 不出现
- 确认包已正确安装（`pip list | grep code-review`）
- 确认 entry point 名称正确（`jupyter_ai.personas` group）
- **重启 JupyterLab**——entry points 在启动时加载
- 检查 JupyterLab 终端是否有导入错误

### 回复不显示
- 确认 `sender=self.id` 已设置
- 确认使用了 `self.send_message()` 或 `self.stream_message()`
- 检查 process_message 是否是 async 函数

### 头像不显示
- `avatar_path` 是相对于 Jupyter Server 的 URL 路径
- 可以使用 Jupyter AI 内置头像路径 `/api/ai/static/jupyternaut.svg`
- 自定义头像需要通过 Jupyter Server 静态文件服务提供

## 相关概念

- [AI Persona 系统](../concepts/05-ai-personas.md)
- [Entry Points API](../concepts/09-entry-points-api.md)
- [Persona API 参考](../references/persona-api.md)
