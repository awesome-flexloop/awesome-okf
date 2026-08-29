---
type: Concept
title: "MAI-UI Grounding Agent：无基类的单元素定位代理"
description: "MAIGroundingAgent 不继承 BaseAgent，无状态单轮定位：SCALE_FACTOR=999 归一化、正则解析 grounding_think/answer 标签、predict 直传 PIL 图、3 次重试与 seed=42。"
tags: [MAI-UI, GroundingAgent, 元素定位, 坐标归一化, 无状态Agent]
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

`MAIGroundingAgent` 是 MAI-UI 双 Agent 中的"定位器"：给定一句指令（如 "click the email icon"）和一张截图，返回目标元素的坐标。它最特殊的的设计决策是**不继承 BaseAgent**——`class MAIGroundingAgent:` 无基类（F-019），因为定位是单轮无状态任务，没有轨迹可记，强行继承只会产生空实现。这与 [/concepts/02-base-agent-traj-memory.md](/concepts/02-base-agent-traj-memory.md) 中继承式导航 Agent 形成有意对照。

## 构造：default_conf 与 OpenAI 客户端

```python
class MAIGroundingAgent:
    def __init__(self, llm_base_url: str, model_name: str,
                 runtime_conf: Optional[Dict[str, Any]] = None):
```

- default_conf 为 `{"temperature": 0.0, "top_k": -1, "top_p": 1.0, "max_tokens": 2048}`，与传入 runtime_conf 按 `{**default_conf, **(runtime_conf or {})}` 合并（F-019）。注意 grounding 的 default_conf **不含** `history_n`——没有历史，自然没有窗口。
- 构造 `OpenAI(base_url=..., api_key="empty")` 客户端（F-019）。api_key 用字面量 "empty"，因为 vLLM 服务不校验密钥（F-004）。

## 输出协议与解析：grounding_think / answer

grounding 专用 prompt（`MAI_MOBILE_SYS_PROMPT_GROUNDING`）要求模型输出 `<grounding_think>...</grounding_think>` 与 `<answer>{"coordinate": [x,y]}</answer>`（F-015）。

解析函数 `parse_grounding_response(text: str) -> Dict[str, Any]`（F-018）：

```python
# 正则提取
<grounding_think>(.*?)</grounding_think>   # → thinking
<answer>(.*?)</answer>                     # → JSON，取 coordinate 字段
# 坐标非 2 个值时 raise ValueError
# 返回 {"thinking": ..., "coordinate": [x_norm, y_norm]}
```

归一化除数是模块级常量 `SCALE_FACTOR = 999`——answer 中的坐标除以 999 归一化到 [0,1]（F-017）。这个 999 不是笔误，与导航 Agent 的常量一致（F-023），但与评估管线的 1000 口径并存（见 [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md) 的坐标口径对照表）。

## predict：签名、容错与采样参数

```python
def predict(self, instruction: str, image: Union[Image.Image, bytes],
            **kwargs: Any) -> Tuple[str, Dict[str, Any]]
```

行为要点（F-020）：

1. 第二参数直接接受 PIL Image 或 bytes；bytes 输入经 `Image.open(BytesIO(image))` 转 PIL，非 RGB 模式转 RGB。
2. 返回 `(prediction_text, {"thinking", "coordinate"})`。
3. LLM 调用失败重试 3 次，仍失败返回 `("llm client error", {"thinking": None, "coordinate": None})`。

采样参数固定确定性（F-021）：

```python
self.llm.chat.completions.create(
    model=..., messages=..., max_tokens=..., temperature=..., top_p=...,
    frequency_penalty=0.0, presence_penalty=0.0,
    extra_body={"repetition_penalty": 1.0, "top_k": self.top_k},
    seed=42,
)
```

`top_k` 走 extra_body（OpenAI 协议无此参数，vLLM 扩展），`seed=42` 保证同图同指令结果可复现。

## 消息结构：system + 单条 user

`_build_messages(self, instruction: str, image: Image.Image) -> list` 生成且仅生成 2 条消息（F-022）：

1. **system**：`MAI_MOBILE_SYS_PROMPT_GROUNDING`（`system_prompt` 是 @property，直接返回该模板，F-022）；
2. **user**：`instruction + "\n"` 文本 + base64 PNG 的 image_url。

**无历史图像逻辑**——每次调用都是独立的一问一答（F-022）。这与导航 Agent 的"文本全量回放 + 图像滑窗"（F-031）形成架构层面的鲜明对比。

## 选型指引

| 场景 | 用谁 | 理由 |
|---|---|---|
| 单元素定位（图标/按钮/控件） | `MAIGroundingAgent` | 无状态、单图、seed 固定，最低成本路径 |
| 多步任务（打开 App、连续操作） | `MAIUINaivigationAgent` | 需要 TrajMemory 轨迹积累（[/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)） |

自定义无多轮需求的 Agent 可效仿"不继承"这一设计；复现示例直接看 [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md)。

## 相关概念

- [/concepts/02-base-agent-traj-memory.md](/concepts/02-base-agent-traj-memory.md)：它选择不继承的基类长什么样
- [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)：predict 签名对照（F-020 vs F-032）
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：grounding prompt 与坐标口径对照表
- [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md)：cookbook 复现步骤
- [Qwen-UI-Agent 技术评测束](../qwen-ui-agent/index.md)：grounding 失误问题的博客级讨论线索（见该束评测视角）
