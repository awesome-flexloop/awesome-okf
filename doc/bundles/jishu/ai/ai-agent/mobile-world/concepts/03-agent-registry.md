---
type: Concept
title: "Agent 注册表：一个抽象方法、九项固定注册表与文件路径后门"
description: "BaseAgent 抽象契约与 token 记账、openai_chat_completions_create 模型怪癖分支、AGENT_CONFIGS 九项注册表、create_agent 双路径与 load_agent_from_file、UIINS grounding 子代理与统一测试脚本"
tags: [MobileWorld, Agent, BaseAgent, 注册表, MCP]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
  - id: mobile-world-sources
    resource: /references/source-registry.md
    title: MobileWorld 信源登记
---

# Agent 注册表：一个抽象方法、九项固定注册表与文件路径后门

接入新 Agent 只需实现一个抽象方法 `predict(observation) -> tuple[str, JSONAction]`；扩展走"9 项固定注册表 + .py 文件路径动态加载"双通道；各家模型 API 的怪癖集中收敛在 BaseAgent 的一个方法里。这是 MobileWorld Agent 接入面的三个核心设计。

## BaseAgent 抽象契约

`class BaseAgent(ABC)`（`agents/base.py`，F-007）：

- `__init__(self, *args, **kwargs)` 初始化 `_total_completion_tokens/_total_prompt_tokens/_total_cached_tokens = 0`
- `initialize(self, instruction: str) -> bool` 与 `initialize_hook(self, instruction: str) -> None`
- 抽象方法 `predict(self, observation: dict[str, Any]) -> tuple[str, JSONAction]`——返回动作语言是 runtime 层的 JSONAction（见 `/concepts/05-runtime-controller.md`）
- `done() -> None`、`reset() -> None`
- `build_openai_client(self, base_url: str, api_key: str) -> None`：OpenAI 客户端 `timeout=120.0`，api_key 为空时用 `"empty"`

### token 用量统计

`get_total_token_usage() -> dict[str, int]` 返回键 `completion_tokens/prompt_tokens/cached_tokens/total_tokens`（total 为 completion+prompt）；`reset_token_usage()` 归零三个计数器；流式请求经 `_wrap_stream_with_usage_logging` 在流结束时取最后一个带 usage 的 chunk 记账（F-009）——即使流式响应也会进入统一记账。

### 模型怪癖分支

`openai_chat_completions_create(self, model: str, messages: list[dict], retry_times: int = 3, stream: bool = False, **kwargs: Any) -> str | None` 按模型名分支处理（F-008）：

| 模型名含 | 处理 |
|---|---|
| `"claude"` | 强制 `kwargs["max_tokens"] = 64000` 并删除 `temperature` |
| `"gpt"`/`"o1"` | 将 `max_tokens` 换成 `max_completion_tokens` |
| `"kimi-k"` | 加 `extra_body={"enable_thinking": True}`，且把 `reasoning_content` 包成 `<think>...</think>` 前缀 |

重试失败 `time.sleep(1)`。模型兼容性排查先查这张分支表，而不是翻各个子类。

## MCPAgent 子类

`class MCPAgent(BaseAgent)`：`__init__(self, tools: list[dict], *args, **kwargs)` 保存 `self.tools`；提供 `reset_tools(self, tools: list[dict]) -> None`；`predict` 仍为抽象方法（F-010）。需要 MCP 工具的 Agent 继承它，工具由环境客户端注入（见 `/concepts/06-eval-server-mcp.md`）。

## AGENT_CONFIGS 九项注册表

`agents/registry.py` 的模块级字典 `AGENT_CONFIGS` 固定 9 项映射（注册名 → 类）（F-011）：

| 注册名 | 类 |
|---|---|
| `qwen3vl` | Qwen3VLAgentMCP |
| `planner_executor` | PlannerExecutorAgentMCP |
| `mai_ui_agent` | MAIUINaivigationAgent |
| `general_e2e` | GeneralE2EAgentMCP |
| `seed_agent` | SeedAgent |
| `gelab_agent` | GelabAgent |
| `ui_venus_agent` | VenusNaviAgent |
| `gui_owl_1_5` | GUIOWL15AgentMCP |
| `memgui` | MemGUIAgent |

注意 `mai_ui_agent`——MAI-UI 的导航 Agent `MAIUINaivigationAgent` 无需任何改造即成为 9 个内置 agent 之一（[../mai-ui/index.md](../../mai-ui/index.md)）。

## create_agent 双路径与文件后门

工厂签名（F-012）：

```python
def create_agent(agent_type: str, model_name: str, llm_base_url: str,
                 api_key: str = "empty", **kwargs)
```

双路径判定：若 `agent_type.endswith(".py") or os.path.exists(agent_type)` 走文件加载路径 `load_agent_from_file`，以 `model_name/llm_base_url/api_key` 实例化；否则查 `AGENT_CONFIGS`，以 `model_name/llm_base_url/tools=kwargs["env"].tools/api_key` 实例化；未知类型抛 `ValueError(f"Unsupported agent type: {agent_type}")`。

也就是说 `--agent-type` 参数**既接受注册名也接受 .py 文件路径**。动态加载实现（F-013）：`load_agent_from_file(file_path)` 用 `importlib.util.spec_from_file_location` 加载模块，`inspect.getmembers(module, inspect.isclass)` 收集 `issubclass(obj, BaseAgent) and obj is not BaseAgent` 的类；0 个抛 ValueError，多个取第一个并 warning。

"封闭枚举 + 文件后门"组合：注册表不是插件目录而是写死的 9 项字典，真正开放的扩展通道是文件路径分支。

## UIINSGroundingAgent：grounding 子代理

`class UIINSGroundingAgent(BaseAgent)`（`agents/grounding/uiins.py`，F-014）：

- `__init__(self, llm_base_url, model_name, runtime_conf = {"temperature": 0.0, "max_tokens": 512, "min_pixels": 3136, "max_pixels": 4096*2160}, ...)`
- `predict` 内 `smart_resize` 后 base64 编码截图；system prompt 要求输出 `<tool_call>{"name": "grounding", ...}`；`parse_coordinates_from_response` 用正则 `\[(\d+),(\d+)\]` 提取坐标
- 请求参数 `frequency_penalty=0.0, presence_penalty=0.0, extra_body={"repetition_penalty": 1.0}, seed=42`，`max_retries = 3`
- 辅助函数 `parsing_response_to_andoid_world_env_action(response, instruction)` 按指令含 "click"/"press" 映射 CLICK/LONG_PRESS

它作为 planner_executor 类 Agent 的执行子代理使用（官方脚本 run_agentic.sh 传 `--executor_agent_class uiins`，F-072）。

## 动作映射字典

`agents/utils/agent_mapping.py` 提供三张映射表，把各家模型的动作词汇对齐到 `runtime.utils.models` 的动作类型常量（F-015）：

- `QWENVL2AW_ACTION_MAP`：14 键（click/type/long_press/scroll/back/home/enter/answer/open_app/wait/terminate/swipe/ask_user/drag）
- `GUIOWL2AW_ACTION_MAP`：13 键（open→OPEN_APP、interact→ASK_USER）
- `UIINS_ACTION_MAP = {"click": CLICK, "long_press": LONG_PRESS}`

## 图像处理常量与工具

`agents/utils/helpers.py`（F-016）：`IMAGE_FACTOR = 28`、`MIN_PIXELS = 100*28*28`、`MAX_PIXELS = 16384*28*28`、`MAX_RATIO = 200`；函数 `add_period_robustly(text)`（按中英文 dominant 判定补 `。` 或 `.`）、`pil_to_base64(image)`、`pil_adaptive_resize(image, max_dimension=2576) -> tuple[Image.Image, float, float]`。

## 统一 agent 测试脚本

`python -m mobile_world.agents.utils.test_agent` 提供不跑全量评测的单 Agent 冒烟测试（F-017）：

- `get_agent_class(agent_type)` 支持 `general_e2e/planner_executor/qwen3vl/mai_ui_agent` 四种
- `test_agent(agent_type, model_name, llm_base_url, api_key, screenshot_path, instruction, output_image_path=None, runtime_conf=None, **kwargs)`
- 默认 `runtime_conf = {"history_n_images": 3, "temperature": 0.0, "max_tokens": 2048}`
- argparse 含 `--scale_factor`（默认 1000）与 planner_executor 专用 `--executor_agent_class/--executor_model_name/--executor_llm_base_url`

## 接入新 Agent 的最小清单

1. 继承 `BaseAgent`（需要 MCP 工具则继承 `MCPAgent`，F-007/F-010）
2. 实现 `predict(self, observation) -> tuple[str, JSONAction]`（F-007）
3. 必要时覆写 `build_openai_client`，或在 `openai_chat_completions_create` 分支表中补充新模型怪癖（F-007/F-008）
4. 用 `--agent-type 路径/your_agent.py` 走文件后门加载（F-012/F-013），或加入 `AGENT_CONFIGS` 注册表（F-011）
5. 用统一测试脚本先冒烟（F-017），再进 `/examples/01-run-built-in-eval-scripts.md` 的全量评测

## 相关概念

- [/concepts/05-runtime-controller.md](/concepts/05-runtime-controller.md)——predict 返回值 JSONAction 的定义与校验
- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——runner 主循环如何消费 predict
- [/concepts/06-eval-server-mcp.md](/concepts/06-eval-server-mcp.md)——MCPAgent 的 tools 从哪里来
- [../mai-ui/index.md](../../mai-ui/index.md)——`mai_ui_agent`（MAIUINaivigationAgent）的模型侧实现与上下文工程
