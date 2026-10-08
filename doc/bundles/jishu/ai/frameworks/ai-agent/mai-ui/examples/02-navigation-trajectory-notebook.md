---
type: Example
title: "Run Agent Notebook 复现：5 张连续截图的轨迹累积"
description: "按 cookbook/run_agent.ipynb 复现 MAIUINaivigationAgent 多步导航：加载 figure1~5 五张连续截图，同一实例循环 predict，观察 TrajMemory 轨迹累积与结果可视化。"
tags: [MAI-UI, cookbook, navigation, 轨迹累积, 示例]
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

`cookbook/run_agent.ipynb` 演示 MAIUINaivigationAgent 的多步工作方式：对 5 张连续截图循环调用同一 Agent 实例，让 TrajMemory 轨迹逐步累积。notebook 标题为 "# Run Naivagation"（notebook 内即此拼写，F-050）——该拼写是检索代码的关键签名（F-005、F-026）。与 [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md) 的关键区别：obs 是字典而非裸图，且 Agent 实例跨步复用。

## 前置条件

- vLLM 服务已启动（`--served-model-name MAI-UI-8B --port 8000`，F-004）。
- `resources/example_img/` 下的 figure1.png 至 figure5.png 共 5 张示例图在位（F-006、F-050）。

## 步骤 1：加载 5 张连续截图

```python
from PIL import Image

test_images = [Image.open(f"../resources/example_img/figure{i}.png")
               for i in range(1, 6)]
```

加载 `../resources/example_img/figure1.png` 至 `figure5.png` 共 5 张图（F-050）。这 5 张图模拟一个任务执行过程中的连续屏幕状态序列。

## 步骤 2：构造导航 Agent

```python
agent = MAIUINaivigationAgent(
    llm_base_url="http://localhost:8000/v1",
    model_name="MAI-UI-8B",
    runtime_conf={"history_n": 3, "temperature": 0.0, "top_k": -1,
                  "top_p": 1.0, "max_tokens": 2048},
)
```

runtime_conf 与 README 示例一致（F-005、F-049）。`history_n: 3` 决定从第 4 步起模型最多看到"最近 2 张历史截图 + 当前截图"（F-026、F-030、F-031）。

## 步骤 3：循环 predict，轨迹累积

```python
instruction = "open the settings and turn on the wifi"
results = []

for test_image in test_images:
    obs = {"screenshot": test_image}
    prediction, action = agent.predict(instruction, obs)
    results.append((prediction, action))
```

要点（F-050）：

1. instruction 为 "open the settings and turn on the wifi"；
2. 每轮构造 `obs = {"screenshot": test_image}`，调用 `agent.predict(instruction, obs)`——obs 是字典（F-032 的签名），与 grounding 直传 PIL 图不同（F-020）；
3. **同一 agent 实例连续调用**：每次 predict 成功后 TrajStep 追加进 `traj_memory.steps`（F-033），首次调用还会把 instruction 写入 `task_goal`（F-032）——这就是"轨迹累积"的机制；
4. 结果收集到 results 列表（F-050）。

从第 2 步起，`_build_messages` 开始回放历史：全部 assistant 文本（坐标反归一化再合成的规范化 `<thinking>/<tool_call>`，F-028）+ 最近 `history_n - 1 = 2` 张历史截图（F-031）。

## 步骤 4：结果可视化

```python
from utils import draw_clicks_on_image, extract_click_coordinates

for test_image, (prediction, action) in zip(test_images, results):
    click_coords = extract_click_coordinates(action)
    # ...归一化坐标乘图像宽高得绝对坐标后画红圈
    result_image = draw_clicks_on_image(image_path, (abs_x, abs_y))
    display(result_image)
```

notebook 对每个结果做与 grounding notebook 相同的坐标可视化（F-050）：`extract_click_coordinates` 取归一化坐标、乘图像宽高换算绝对坐标、`draw_clicks_on_image` 画红圈（F-012、F-049）。

## 观察点：轨迹如何改变行为

- 对比第 1 步与第 5 步的请求消息数：第 1 步是 system → user(instruction) → user(当前图) 三条（F-031 无历史分支）；第 5 步含 4 条 assistant 回放 + 3 张图（当前 + 2 历史），可用 tests 的 `test_build_messages_with_5_history_steps`（5 assistant + 3 image）断言对照（F-051）。
- 查看轨迹内容：`agent.save_traj()` 导出每个 step 的 9 字段 dict（F-011）；`agent.thoughts`/`agent.actions` 派生思考与动作列表（F-010）。
- 本示例不涉及 ask_user/MCP：未传 `mcp_tools`，system prompt 用默认 10 动作模板（F-014、F-027）；ask_user_response/mcp_response 字段保持 None（F-033）。

## 常见问题

| 现象 | 检查点 |
|---|---|
| 每步结果像"独立重答" | 确认是同一 agent 实例循环调用——新建实例会清空 traj_memory（F-026、F-033） |
| 想从头重跑任务 | 调用 `agent.reset()`（或 `agent.reset(runtime_logger)`，参数仅为兼容保留）（F-011、F-034） |
| 多步后 token 增长明显 | 预期行为：文本全量回放是长任务开销主项，`history_n` 只控制图像窗口（F-028、F-031） |

## 相关概念

- [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)：本示例背后全部机制（回放/滑窗/生命周期）
- [/concepts/02-base-agent-traj-memory.md](/concepts/02-base-agent-traj-memory.md)：TrajStep/TrajMemory 与 save_traj
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：动作空间与输出协议
- [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md)：单图定位版 notebook
- [MobileWorld 评测环境束](../../mobile-world/index.md)：把这套循环接入真实 Android 容器的下一步
