---
type: reference
scope: deepagents
name: middleware-stack
version: "0.7.8"
source: https://github.com/langchain-ai/deepagents
description: deepagents 中间件栈排序、自定义合并规则与必需脚手架约束
---

# 中间件栈参考

Deep Agents 的所有核心能力都通过 `AgentMiddleware` 实现。中间件通过 `wrap_model_call()` 钩子在每次 LLM 请求发送前拦截调用，能够动态过滤工具、注入系统提示、变换消息和维护跨轮状态。

## 默认中间件顺序

主代理的中间件栈分为三段（源码：`graph.py:817-893`）：

### 基础栈（Scaffolding）

按添加顺序：

1. **`SkillsMiddleware`**（仅当 `skills` 参数提供时）— 加载技能索引并注入系统提示
2. **`FilesystemMiddleware`** — 提供文件工具（`ls`/`read_file`/`write_file`/`edit_file`/`glob`/`grep`/`execute`），强制执行权限规则
3. **`SubAgentMiddleware`**（仅当有内联子代理时）— 提供 `task` 工具，管理子代理调用
4. **`SummarizationMiddleware`** — 自动压缩对话，卸载旧消息到后端
5. **`PatchToolCallsMiddleware`** — 修补工具调用
6. **`AsyncSubAgentMiddleware`**（仅当有异步子代理时）— 提供异步任务工具（启动/检查/更新/取消/列出）

### 用户中间件插入点

调用者通过 `middleware=` 参数传入的中间件在此处插入。插入规则由 `_apply_custom_middleware()` 控制：

- 如果中间件的 `.name` 与基础栈中的同名，**原地替换**，保留栈顺序
- 否则插入到最后一个核心中间件之后、尾部栈之前

### 尾部栈（Tail）

7. Harness profile 的 `extra_middleware`
8. **`_ToolExclusionMiddleware`**（仅当 profile 有 `excluded_tools` 时）— 从最终工具集中排除指定工具
9. **PromptCaching 中间件**（无条件添加）— Anthropic/Bedrock/Fireworks 的提示缓存，对非目标模型无操作
10. **`MemoryMiddleware`**（仅当 `memory` 参数提供时）— 加载 AGENTS.md 文件并注入系统提示
11. **`HumanInTheLoopMiddleware`**（仅当 `interrupt_on` 或 interrupt 模式权限存在时）— 暂停执行等待人工审批

## 必需脚手架

`_REQUIRED_MIDDLEWARE` 元组定义了两个不可通过 `HarnessProfile.excluded_middleware` 排除的中间件：

| 中间件 | 不可排除原因 |
|---|---|
| `FilesystemMiddleware` | 支撑所有内置文件工具，并强制执行 `permissions` 权限规则（安全保证） |
| `SubAgentMiddleware` | 支撑 `task` 工具处理器 |

尝试排除这些中间件会引发 `ValueError`，错误消息提示使用 `excluded_tools` 控制工具可见性或调整 profile 设置。

排除验证有三重保障：
1. `_validate_excluded_middleware_config()` — 构造时验证 profile 配置
2. `_apply_excluded_middleware()` — 组装时过滤中间件，记录匹配项
3. `_verify_excluded_middleware_coverage()` — 最终验证每个排除项在主代理或通用子代理栈中至少匹配一个中间件

匹配不到任何中间件的排除项会引发 `ValueError`，防止拼写错误或过时配置静默降级。

## 子代理中间件栈

声明式 `SubAgent` 规格在编译时获得独立的中间件栈：

```
FilesystemMiddleware
→ SummarizationMiddleware
→ PatchToolCallsMiddleware
→ SkillsMiddleware（如子代理指定 skills）
→ Profile extra_middleware
→ PromptCaching 中间件
→ 用户自定义中间件
→ _ToolExclusionMiddleware（如 profile 有 excluded_tools）
```

子代理默认继承父代理的 `tools` 和 `permissions`，但可以通过自身的 `tools`、`permissions`、`middleware` 字段覆盖。`interrupt_on` 也默认继承，但子代理自身的配置会完全替换（非合并）。

`CompiledSubAgent` 的预编译 runnable 不继承父代理的中间件、状态模式或 `interrupt_on`——这些需在编译 runnable 时自行配置。

## 中间件与普通工具的区别

| 维度 | 中间件 | 普通工具（`tools=`） |
|---|---|---|
| 调用时机 | 每次 LLM 请求前（`wrap_model_call`） | 仅当 LLM 选择使用该工具时 |
| 能修改工具列表 | 是 | 否 |
| 能修改系统提示 | 是 | 否 |
| 能变换消息历史 | 是 | 否 |
| 跨轮状态 | 支持（`state_schema`） | 无状态 |
| 适用场景 | 需要拦截/变换/状态的能力 | 自包含的无状态函数 |

## 相关 API

- `create_deep_agent()` — 中间件栈的组装入口
- 后端系统 — 中间件依赖的后端抽象
- Profile 机制 — 控制中间件排除和额外中间件
