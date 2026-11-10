---
type: Concept
title: "模型接入：litellm 全家桶与 toolcall/textbased 双通道"
description: "十类模型实现的注册表、litellm/openrouter/portkey/requesty 四家通道、原生 tool calling 与文本解析的差异、成本追踪、缓存控制与重试"
tags: [litellm, OpenRouter, Portkey, Requesty, tool calling, 成本, 重试]
generated: { by: "seven-concepts-cmd/E", at: "2026-11-10T16:59:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T17:05:00+08:00" }
status: stable
stale_after: 2027-03-31
sources:
  - id: repo-mini-swe-agent
    resource: /references/repo-source.md
    title: "仓库事实清单（F-035 ~ F-090）"
  - id: official-models
    resource: https://mini-swe-agent.com/latest/models/quickstart/
    title: "官方文档：Language models"
---

# 模型接入：litellm 全家桶与 toolcall/textbased 双通道

> mini 不绑定任何模型厂商。它把“模型”抽象成一个 `Model` Protocol，具体实现由注册表选择（F-058）。这既是它“任何模型都能跑”的来源，也是配置容易踩坑的地方。

## 1. 十类模型实现

`models/__init__.py` 的 `_MODEL_CLASS_MAPPING` 注册了 10 个类（F-058）：

| 短名 | 类 | 通道 | 说明 |
|---|---|---|---|
| `litellm` | `LitellmModel` | 原生 tool call | 默认；覆盖最多厂商 |
| `litellm_textbased` | `LitellmTextbasedModel` | 文本三反引号 | v1 兼容 |
| `litellm_response` | `LitellmResponseModel` | Responses API | OpenAI `/response` 端点 |
| `openrouter` | `OpenRouterModel` | 原生 tool call | OpenRouter 路由 |
| `openrouter_textbased` | `OpenRouterTextbasedModel` | 文本 | OpenRouter 兼容 |
| `openrouter_response` | `OpenRouterResponseModel` | Responses API | OpenRouter 响应端点 |
| `portkey` | `PortkeyModel` | 原生 tool call | Portkey 网关 |
| `portkey_response` | `PortkeyResponseAPIModel` | Responses API | Portkey 响应端点 |
| `requesty` | `RequestyModel` | 原生 tool call | Requesty 网关 |
| `deterministic` | `DeterministicModel` | 测试用 | 固定输出，便于单测 |

不指定 `model_class` 时默认 `LitellmModel`（F-059）。模型名建议带 provider 前缀，例如 `anthropic/claude-sonnet-4-5-20250929`（F-080）。

## 2. 两条动作通道

### 2.1 原生 tool calling（v2 默认）

```python
BASH_TOOL = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Execute a bash command",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}
```

`litellm.completion(..., tools=[BASH_TOOL])`（F-060）。模型返回 `tool_calls`，`parse_toolcall_actions` 校验：

1. 必须至少有一个 tool call。
2. `function.name` 必须是 `bash`。
3. `arguments` 必须能 JSON 解析，且含 `command`。
4. 任一不满足 → `FormatError`，把错误模板作为 user 消息追加。

### 2.2 文本解析（v1 兼容）

模型输出一个三反引号代码块，`parse_regex_actions` 用正则提取，要求**恰好一个**动作（F-061、F-062）。默认标记为 ` ```mswea_bash_command `，可通过 `action_regex` 配置。

| 维度 | tool calling | textbased |
|---|---|---|
| 模型要求 | 支持 tools 的 API | 任何文本模型 |
| 解析失败面 | JSON/参数校验 | 正则匹配数量 |
| 多动作 | 可一次返回多个 tool_calls | 强制恰好一个 |
| 兼容性 | v2 默认 | v1/旧模型 |
| 官方态度 | 推荐 | 保留兼容 |

> **README 滞后**：README 与 FAQ 仍写“不需要 tool-calling”（F-078），但 v2 默认已经切到 tool calling。判断当前行为要看 `config/mini.yaml` 与 `litellm_model.py`，不要只看 README 的一句话。

## 3. 成本追踪

`LitellmModelConfig` 提供 `cost_tracking`（`default` / `ignore_errors`），并通过 `GLOBAL_MODEL_STATS` 做全局成本/调用次数限制（F-059）：

1. 每次 `query()` 后从响应计算 cost，累加到 `Agent.cost`。
2. `GlobalModelStats` 用线程锁累计全局成本，支持 `MSWEA_GLOBAL_COST_LIMIT` 与 `MSWEA_GLOBAL_CALL_LIMIT`。
3. 超限抛 `RuntimeError`，在批处理中可快速失败。

这意味着：**成本是循环的退出条件之一**，不是事后报表。默认 `cost_limit=3.0` 美元（F-048），跑 SWE-bench 时要按模型单价调整。

## 4. 缓存、重试与多模态

| 能力 | 实现 | 说明 |
|---|---|---|
| Anthropic prompt caching | 名称含 anthropic/sonnet/opus/claude 时默认 `set_cache_control="default_end"`（F-059） | 降低长系统提示的重复成本 |
| 重试 | `tenacity` + `models/utils/retry.py` | 对限流/瞬时错误退避重试 |
| 中止异常 | `UnsupportedParamsError`、`NotFoundError`、`PermissionDeniedError`、`ContextWindowExceededError`、`AuthenticationError`、`KeyboardInterrupt` | 不重试，直接失败 |
| 多模态 | `expand_multimodal_content` + `multimodal_regex` | v2 支持图片等内容 |
| 本地模型 | `litellm_model_registry` 可注册自定义模型元数据 | 便于成本计算 |

依赖层面，`pyproject.toml` 显式排除 litellm 1.82.7/1.82.8（安全原因）与 openai 1.100.0/1.100.1（issue #446）（F-081）。安装时不要强行降级到这些版本。

## 5. 选模型的实际建议

1. **先看工具调用支持**：v2 默认走 tool calling；不支持的老模型改用 `litellm_textbased`。
2. **再看上下文窗口**：线性历史不做压缩，长任务需要大窗口（F-011）。
3. **最后看单价**：`cost_limit=3.0` 是默认值，强模型跑复杂 Issue 很容易触顶。
4. **批量评测固定模型快照**：74% 是 Gemini 3 Pro 的单点成绩（F-070、F-088），换模型/换日期不能直接复用。

## 6. 一段最小接线

```python
from minisweagent.agents.default import DefaultAgent
from minisweagent.models import get_model
from minisweagent.environments.local import LocalEnvironment

agent = DefaultAgent(
    get_model(input_model_name="anthropic/claude-sonnet-4-5-20250929"),
    LocalEnvironment(),
)
result = agent.run("修复登录页对特殊字符用户名的处理")
print(result["exit_status"], result["submission"])
```

这段代码来自官方 Python bindings（F-067），不是博客里的 `MiniSWEAgent` 伪代码（E-3）。
