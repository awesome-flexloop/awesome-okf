---
type: Concept
title: "MAI-UI Navigation Agent：继承式多步导航与上下文工程"
description: "MAIUINaivigationAgent 继承 BaseAgent：3 个模块级解析函数、坐标 2/4 值格式、mcp_tools 模板切换、history_responses 再合成、图像滑窗与全文本回放，及 10 个消息契约测试。"
tags: [MAI-UI, NavigationAgent, 上下文工程, 轨迹回放, history_n]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mai-ui-facts
    resource: /references/facts.md
    title: MAI-UI 源码事实台账
  - id: mai-ui-sources
    resource: /references/source-registry.md
    title: MAI-UI 信源登记
---

`MAIUINaivigationAgent` 是 MAI-UI 的多步任务执行者，`class MAIUINaivigationAgent(BaseAgent)` 继承 [/concepts/02-base-agent-traj-memory.md](/concepts/02-base-agent-traj-memory.md) 的抽象契约（F-026）。类名拼写 "Naivigation" 在 README、源码、notebook 标题（"# Run Naivagation"，F-050）中一贯如此，是检索代码的关键签名；类 docstring 写的是 "MAIMobileAgent"，与类名不一致属代码现状（F-026）。本篇核心是它的上下文工程：**文本全量回放、图像滑动窗口、回放文本再合成**。

## 构造与配置

```python
def __init__(self, llm_base_url: str, model_name: str,
             runtime_conf: Optional[Dict[str, Any]] = None,
             mcp_tools: Optional[List[Dict[str, Any]]] = None)
```

先 `super().__init__()`（初始化 traj_memory），`self.mcp_tools = mcp_tools or []`；default_conf 为 `{"history_n": 3, "temperature": 0.0, "top_k": -1, "top_p": 1.0, "max_tokens": 2048}`（F-026）。`history_n: 3` 意味着模型最多看到"最近 2 张历史截图 + 当前截图"的图像窗口。

## 三个模块级解析函数（F-024）

| 函数 | 签名 | 职责 |
|---|---|---|
| `mask_image_urls_for_logging` | `(messages) -> List[Dict]` | 深拷贝消息并把 image_url 替换为 "[IMAGE_DATA]"，用于日志脱敏 |
| `parse_tagged_text` | `(text) -> Dict` | 正则提取 `<thinking>` 与 `<tool_call>`（tool_call 须为合法 JSON）；兼容 thinking 模型把 `</think>` 替换为 `</thinking>` 并补前置 `<thinking>` |
| `parse_action_to_structure_output` | `(text) -> Dict` | 返回 `{"thinking", "action_json"}` |

坐标解析支持两种格式（F-025）：`coordinate`/`start_coordinate`/`end_coordinate` 长度为 2 时（x,y）直接用，长度为 4 时（x1,y1,x2,y2）取中点；均除以模块常量 `SCALE_FACTOR = 999` 归一化（F-023）；长度既非 2 也非 4 时 raise ValueError。

## system_prompt：按 mcp_tools 切换模板

`@property def system_prompt`：若 `self.mcp_tools` 非空，把每个 tool dict 以 `json.dumps(tool, ensure_ascii=False)` 逐行 join 后传入 `MAI_MOBILE_SYS_PROMPT_ASK_USER_MCP.render(tools=mcp_tools_str)`（动作空间扩到 12 种，含 ask_user/double_click，F-014）；否则返回 `MAI_MOBILE_SYS_PROMPT`（10 种动作，F-014）。模板机制见 [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)（F-027）。

## 上下文工程三原则

**原则一：回放文本"再合成"而非照抄原始输出。** 基类的 `history_responses` property 返回各 step.prediction（F-010），本类将其覆写（F-028）：遍历 traj_memory.steps、跳过无 structured_action 的 step，把 action_json 的 normalized 坐标**乘以 SCALE_FACTOR 取 int 还原**，组装 `{"name": "mobile_use", "arguments": action_json}`（`json.dumps(..., separators=(",", ":"))` 紧凑格式），输出：

```
<thinking>
{thinking}
</thinking>
<tool_call>
{tool_call_json}
</tool_call>
```

即回放的 assistant 文本是从结构化 action_json 反归一化坐标后重新拼装的规范化版本，原始 `prediction` 字段虽被保存（F-033）但回放时不使用。配套三个 mem2 方法（F-029）：`mem2response(step)`（按上述格式化单步，无 structured_action 时 raise ValueError）、`mem2ask_user_response(step)`（返回 step.ask_user_response）、`mem2mcp_response(step)`（返回 step.mcp_response）。

**原则二：图像滑动窗口。** `_prepare_images(self, screenshot_bytes) -> List[Image.Image]` 取 `min(len(history_images), history_n - 1)` 张最近历史截图，追加当前截图，逐张转 PIL、非 RGB 转 RGB；兼容 bytes/PIL 输入，其他类型 raise TypeError（F-030）。

**原则三：文本全量回放 + 图像只挂窗口内。** `_build_messages(self, instruction, images)` 的结构（F-031）：

```
system
→ user(instruction)
→ 对每个历史 step：
    [可选 user 图像消息]（仅当 history_idx >= len(steps) - (history_n - 1)，
     start_image_idx = max(0, len(steps) - (history_n - 1))）
    + assistant(mem2response(step))
    + [ask_user_response 存在时追加 user 文本]
    + [mcp_response 存在时追加 user 文本]
→ user(当前图像)
```

无历史时退化为 system → user(instruction) → user(当前图像) 三条消息（F-031）。反直觉之处：图像远贵于文本，模型可从先前 assistant 回复文本（含动作与思考）推断早期画面，所以图像滑窗、文本长存——长任务的 token 开销主要来自全量文本回放。

## predict 生命周期

```python
def predict(self, instruction: str, obs: Dict[str, Any], **kwargs: Any) -> Tuple[str, Dict[str, Any]]
```

1. obs 读取 `obs["screenshot"]`（PIL 或 bytes）与 `obs.get("accessibility_tree")`；docstring 还声明可选 `ask_user_response`/`mcp_response` 键，但代码实际仅使用 screenshot 与 accessibility_tree（F-032）。
2. 首次调用时 `if not self.traj_memory.task_goal: self.traj_memory.task_goal = instruction`（F-032）。
3. 成功后构造 TrajStep 并追加：`TrajStep(screenshot=..., accessibility_tree=..., prediction=prediction, action=action_json, conclusion="", thought=thinking, step_index=len(self.traj_memory.steps), agent_type="MAIMobileAgent", model_name=self.model_name, screenshot_bytes=..., structured_action={"action_json": action_json})`，返回 `(prediction, action_json)`（F-033）。
4. **回填边界**：`ask_user_response`/`mcp_response` 字段不被 predict 写入（保持默认 None，由外部赋值）（F-033）——评测环境 MobileWorld 的 runner 就是那个外部宿主（见 [MobileWorld 束](../../mobile-world/index.md)）。
5. LLM 调用 3 次重试失败返回 `("llm client error", {"action": None})`（F-033）。

`reset` 被覆写为 `def reset(self, runtime_logger: Any = None) -> None`，调用 `super().reset()`；runtime_logger 未使用，docstring 注明 "unused, kept for API compatibility"（F-034）——这是为评测框架签名预留的兼容参数。

## 10 个消息契约测试

`tests/test_mai_navigation_agent.py`（docstring "Unit tests for MAIUINaivigationAgent._build_messages functionality"，F-051）覆盖 10 个用例（F-051）：

- test_build_messages_no_history（断言 3 条消息）
- test_build_messages_with_single_history（5 条消息：system/user/历史图/assistant/当前图）
- test_build_messages_with_multiple_history（3 history 时 image_count==3）
- test_build_messages_with_5_history_steps（5 assistant + 3 image——直观验证滑窗）
- test_build_messages_with_5_steps_ask_user_and_mcp（验证 ask_user_response 与 mcp_response 进入消息、MCP 工具名进入 system prompt）
- test_build_messages_with_ask_user_response、test_build_messages_with_mcp_response、test_build_messages_system_prompt、test_build_messages_with_mcp_tools、test_build_messages_image_encoding（base64 前缀 `data:image/png;base64,` 校验）

测试机制：fixture 用 `with patch('mai_naivigation_agent.OpenAI')` 构造 agent（llm_base_url="http://test.com"、model_name="test-model"、runtime_conf={"history_n": 3}），用 `mask_image_urls_for_logging` 屏蔽图像后把消息 dump 为 `tests/output_messages/<test_name>.json` 基线文件（8 个）（F-052）。这组"mock OpenAI + JSON 基线"测试是不用 LLM 就能复现消息格式的现成素材。

想修改回放格式，只需改 `history_responses`/`mem2response` 一处（F-028、F-029），不要篡改 `prediction` 字段；改动后跑上述 10 个用例即可验证消息契约。

## 相关概念

- [/concepts/02-base-agent-traj-memory.md](/concepts/02-base-agent-traj-memory.md)：继承的基类与 TrajStep 字段
- [/concepts/03-grounding-agent.md](/concepts/03-grounding-agent.md)：predict 签名对照（F-032 vs F-020）
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：system prompt 两模板与坐标口径
- [/examples/02-navigation-trajectory-notebook.md](/examples/02-navigation-trajectory-notebook.md)：5 图循环的最小复现
- [MobileWorld 评测环境束](../../mobile-world/index.md)：`mai_ui_agent` 注册名与 ask_user_response/mcp_response 回填宿主
