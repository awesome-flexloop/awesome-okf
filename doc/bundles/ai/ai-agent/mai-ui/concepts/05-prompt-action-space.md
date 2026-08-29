---
type: Concept
title: "MAI-UI Prompt 与动作空间：模板、动作集与坐标口径"
description: "prompt.py 的 4 个模板（含 Jinja2 MCP 版）、导航 10/12 种动作定义、thinking/tool_call 与 grounding 输出协议、21/14 两套 App 列表及 999/1000 双坐标口径对照表。"
tags: [MAI-UI, Prompt, 动作空间, 坐标归一化, mobile_use]
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

`src/prompt.py`（148 行）是 MAI-UI 的"行为说明书"：4 个 prompt 模板（F-013）定义了模型能做什么（动作空间，F-014）、必须怎么回答（输出协议，F-015）、在哪个 App 宇宙里工作（App 列表，F-016）。读 03/04 两篇 Agent 实现前先读本篇，能省一半力气。

## 4 个 prompt 模板（F-013）

| 模板 | 类型 | 用途 |
|---|---|---|
| `MAI_MOBILE_SYS_PROMPT` | str | 导航默认版（thinking + tool_call） |
| `MAI_MOBILE_SYS_PROMPT_NO_THINKING` | str | 导航无思考版（仅 tool_call） |
| `MAI_MOBILE_SYS_PROMPT_ASK_USER_MCP` | jinja2.Template | 导航 + ask_user/MCP 版，带 `{{ tools }}` 占位与 `{% if tools -%}` 条件块 |
| `MAI_MOBILE_SYS_PROMPT_GROUNDING` | str | grounding 定位专用 |

模板切换由导航 Agent 的 `system_prompt` property 按需完成（F-027）。

## 动作空间：10 种与 12 种（F-014）

`MAI_MOBILE_SYS_PROMPT` 定义 10 种动作：

| 动作 | 参数 |
|---|---|
| `click` | coordinate |
| `long_press` | coordinate |
| `type` | text |
| `swipe` | direction: up/down/left/right + 可选 coordinate |
| `open` | text: app_name |
| `drag` | start_coordinate + end_coordinate |
| `system_button` | button: back/home/menu/enter |
| `wait` | — |
| `terminate` | status: success/fail |
| `answer` | text |

`MAI_MOBILE_SYS_PROMPT_ASK_USER_MCP` 版本额外含 `ask_user`（text）与 `double_click`（coordinate），共 12 种（F-014）。

## 输出协议：XML 标签包 JSON（F-015）

```text
<thinking>...</thinking>
<tool_call>{"name": "mobile_use", "arguments": <args-json-object>}</tool_call>
```

- NO_THINKING 版本仅要求 `<tool_call>`（F-015）；
- grounding 版本要求 `<grounding_think>...</grounding_think>` 与 `<answer>{"coordinate": [x,y]}</answer>`（F-015）。

解析侧与协议一一对应：导航用 `parse_tagged_text`/`parse_action_to_structure_output`（F-024），grounding 用 `parse_grounding_response`（F-018）。

## 两套 App 列表（F-016）

- `MAI_MOBILE_SYS_PROMPT` / NO_THINKING 列出 **21 个 App**：Camera、Chrome、Clock、Contacts、Dialer、Files、Settings、Markor、Tasks、Simple Draw Pro、Simple Gallery Pro、Simple SMS Messenger、Audio Recorder、Pro Expense、Broccoli APP、OSMand、VLC、Joplin、Retro Music、OpenTracks、Simple Calendar Pro；
- `ASK_USER_MCP` 模板列出 **14 个 App**：Contacts、Settings、Clock、Maps、Chrome、Calendar、files、Gallery、Taodian、Mattermost、Mastodon、Mail、SMS、Camera。

两套列表的差异反映了两种运行环境：21 App 版对应 AndroidWorld 系应用生态，14 App 版对应含 Mattermost/Mastodon/Taodian（淘店）等的评测容器生态（见 [MobileWorld 束](../mobile-world/index.md) 的应用资源）。

## 坐标口径对照表（重要）

同一仓库内并存两套归一化除数，复现分数或接入第三方环境时必须显式核对：

| 位置 | 除数 | 出处 |
|---|---|---|
| `src/mai_grounding_agent.py` 模块常量 `SCALE_FACTOR` | **999** | F-017（`parse_grounding_response` 坐标除以 999 归一化到 [0,1]） |
| `src/mai_naivigation_agent.py` 模块常量 `SCALE_FACTOR` | **999**（归一化除，反归一化乘） | F-023、F-025、F-028 |
| 评估批量推理 `batch_ground_only_positive` | **1000**（point 归一化固定除以 1000） | F-036 |
| 评估单样本 `ground_only_positive` | **resize 后宽度**（`point_x / resized_width`） | F-036 |
| eval_server.py | **1000.0**（`related / 1000.0` 再乘原图宽高） | F-040 |

999 与 1000 极易被当成笔误，但 src 两个文件一致用 999、评估端一致用 1000，是两套约定并存而非错误；把 Agent 接入第三方环境时，分数异常先查归一化口径再查模型。

## 与 MobileWorld 的动作衔接

本篇的 10/12 种动作（F-014）与 MobileWorld 服务端 `JSONAction` 的动作常量存在映射关系（如 `open` → OPEN_APP），详见 [MobileWorld 束的动作分发](../mobile-world/index.md)。

## 相关概念

- [/concepts/03-grounding-agent.md](/concepts/03-grounding-agent.md)：GROUNDING 模板的使用者
- [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)：三个导航模板的切换逻辑与解析函数
- [/concepts/06-evaluation-pipeline.md](/concepts/06-evaluation-pipeline.md)：评估端 1000 口径的完整上下文
- [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md)：answer 坐标如何换算回绝对像素
- [MobileWorld 评测环境束](../mobile-world/index.md)：动作常量映射与 App 生态对齐
