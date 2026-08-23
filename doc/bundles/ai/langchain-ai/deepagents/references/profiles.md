---
type: reference
scope: deepagents
name: profiles
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents Harness Profile 与 Provider Profile 机制——模型特化的正交调优
---

# Profile 机制参考

Profile 系统允许 Deep Agents 根据模型提供者或具体模型规格调整运行时行为，而无需修改核心组装逻辑。Profile 分为两类，分别在不同阶段介入。

## 两类 Profile 的正交关系

| Profile 类型 | 介入阶段 | 控制内容 | 注册函数 |
|---|---|---|---|
| `ProviderProfile` | 模型构造阶段 | 模型初始化参数、API 配置 | `register_provider_profile()` |
| `HarnessProfile` | 模型构造之后 | 提示组装、工具可见性、中间件、子代理行为 | `register_harness_profile()` |

两者正交：Provider Profile 决定"如何创建模型"，Harness Profile 决定"创建后如何调优 harness"。

## Harness Profile

**模块路径**：`deepagents.profiles.harness.harness_profiles`

Harness Profile 声明 `create_deep_agent` 应为给定模型塑造的运行时行为。用户可通过 `register_harness_profile()` 注册自定义 profile，Deep Agents 为多个前沿模型规格内置了 profile。

### 可配置项

- `base_system_prompt`：基础系统提示（位于 `USER` 之后）
- `system_prompt_suffix`：系统提示后缀（位于最后）
- `excluded_tools`：从最终工具集中排除的工具名集合
- `excluded_middleware`：从中间件栈中排除的中间件（类或字符串名）
- `extra_middleware`：额外中间件（工厂函数形式，延迟实例化）
- `tool_description_overrides`：工具描述覆盖（如 `task` 工具描述）
- `general_purpose_subagent`：通用子代理配置（`GeneralPurposeSubagentProfile`）

### GeneralPurposeSubagentProfile

```python
@dataclass(frozen=True)
class GeneralPurposeSubagentProfile:
    enabled: bool | None = None
    description: str | None = None
    system_prompt: str | None = None
```

- `enabled`：三态开关。`None` 继承/默认开启，`True` 强制包含，`False` 禁用
- `description`：覆盖通用子代理的描述
- `system_prompt`：覆盖通用子代理的系统提示

禁用通用子代理且不传入同步子代理时，`task` 工具不会暴露。异步子代理不受影响。

### 内置 Harness Profiles

源码位于 `deepagents/profiles/harness/` 目录：

| 文件 | 目标模型 |
|---|---|
| `_anthropic_sonnet_4_6.py` | Anthropic Claude Sonnet 4.6 |
| `_anthropic_opus_4_7.py` | Anthropic Claude Opus 4.7 |
| `_anthropic_haiku_4_5.py` | Anthropic Claude Haiku 4.5 |
| `_nvidia_nemotron_3_ultra.py` | NVIDIA Nemotron 3 Ultra |
| `_openai_codex.py` | OpenAI Codex |

### 排除中间件的安全约束

`excluded_middleware` 不能排除 `_REQUIRED_MIDDLEWARE` 中的脚手架：

- `FilesystemMiddleware`（类名和字符串名均受保护）
- `SubAgentMiddleware`（类名和字符串名均受保护）

违反时引发 `ValueError`，错误消息建议使用 `excluded_tools` 控制工具可见性。

排除验证还检查：
- 不允许使用下划线前缀的私有名称
- 不允许名称碰撞到多个不同的中间件类
- 每个排除项必须在组装后的栈中匹配到至少一个中间件（主代理或通用子代理栈）

### Profile 解析

`_harness_profile_for_model(model, model_spec)` 根据已解析的模型实例和原始模型规格字符串自动确定适用的 profile。该函数在主代理和每个子代理的模型解析时分别调用。

## Provider Profile

**模块路径**：`deepagents.profiles.provider.provider_profiles`

Provider Profile 控制模型构造阶段的行为，通过 `register_provider_profile()` 注册。主要处理不同 LLM 提供者的初始化差异。

源码位于 `deepagents/profiles/provider/` 目录：

| 文件 | 提供者 |
|---|---|
| `_openai.py` | OpenAI（包括 Responses API 配置） |
| `_anthropic.py` | Anthropic |
| `_nvidia.py` | NVIDIA |
| `_openrouter.py` | OpenRouter |

## 相关概念

- [核心 API](/ai/langchain-ai/deepagents/references/api) — `create_deep_agent()` 如何使用 profile
- [中间件栈](/ai/langchain-ai/deepagents/references/middleware-stack) — profile 如何影响中间件排序和排除
