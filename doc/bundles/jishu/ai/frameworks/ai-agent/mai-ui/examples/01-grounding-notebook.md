---
type: Example
title: "Grounding Notebook 复现：单图定位到红圈可视化"
description: "按 cookbook/grounding.ipynb 六步复现 MAIGroundingAgent：加载示例图、建 Agent、predict 单图、extract_click_coordinates 换算绝对坐标、draw_clicks_on_image 画红圈。"
tags: [MAI-UI, cookbook, grounding, 可视化, 示例]
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

`cookbook/grounding.ipynb` 是仓库内最小、最快的"跑一遍"素材：单图、单轮、无基类依赖，只需一个已启动的 vLLM 服务（[/concepts/01-quickstart-installation.md](/concepts/01-quickstart-installation.md)）和仓库自带的示例图。notebook 共 6 个 cell，完整流程为"加载示例图 → 建 Agent → predict → 坐标换算 → 可视化"（F-049）。

## 前置条件

- vLLM 服务已按 `--served-model-name MAI-UI-8B --port 8000` 启动（F-004），服务地址 `http://localhost:8000/v1`。
- 工作目录能相对访问 `../src` 与 `../resources/example_img/`（notebook 的路径约定，F-049）。

## Cell 1：导入（sys.path 注入）

```python
import sys
sys.path.insert(0, "../src")

from mai_grounding_agent import MAIGroundingAgent
from utils import draw_clicks_on_image, extract_click_coordinates
```

导入 `MAIGroundingAgent` 与两个 utils 工具函数 `draw_clicks_on_image`、`extract_click_coordinates`（F-049、F-012）。

## Cell 2：加载示例图

```python
from PIL import Image
test_image = Image.open("../resources/example_img/figure1.png")
```

示例图来自仓库 `resources/example_img/` 的 figure1.png（F-006、F-049）。

## Cell 3：指令与 Agent 构造

```python
instruction = "click the email icon"

agent = MAIGroundingAgent(
    llm_base_url="http://localhost:8000/v1",
    model_name="MAI-UI-8B",
    runtime_conf={"history_n": 3, "temperature": 0.0, "top_k": -1,
                  "top_p": 1.0, "max_tokens": 2048},
)
```

instruction 为 "click the email icon"；runtime_conf 与 README 示例一致（F-049、F-005）。grounding 的 default_conf 本不含 `history_n`，传入后被字典合并保留但不参与逻辑（F-019）。

## Cell 4：predict（第二参数直接传 PIL 图）

```python
prediction, action = agent.predict(instruction, test_image)
```

`predict(instruction, image)` 的第二参数直接接受 PIL Image（或 bytes），返回 `(prediction_text, {"thinking", "coordinate"})`，coordinate 为除以 999 归一化后的 [x_norm, y_norm]（F-020、F-017、F-018）。

## Cell 5：归一化坐标 → 绝对像素坐标

```python
click_coords = extract_click_coordinates(action)
# 归一化坐标乘图像宽高得绝对坐标
abs_x = click_coords[0] * test_image.width
abs_y = click_coords[1] * test_image.height
```

`extract_click_coordinates(action)` 读取 `action['coordinate']` 返回 `Optional[Tuple[float, float]]`（F-012）；notebook 将归一化坐标乘图像宽高得到绝对坐标（F-049）。

## Cell 6：可视化红圈

```python
result_image = draw_clicks_on_image("../resources/example_img/figure1.png",
                                    (abs_x, abs_y))
display(result_image)
```

`draw_clicks_on_image(image_path, click_coords, output_path=None)` 在图上画半径 20 的红色圆并返回 PIL Image（F-012）；notebook 调用后 display 展示（F-049）。

## 常见问题

| 现象 | 检查点 |
|---|---|
| 返回 `("llm client error", {"thinking": None, "coordinate": None})` | vLLM 服务是否已启动、model_name 是否与 `--served-model-name` 一致（F-020、F-004） |
| 坐标落点系统性偏移 | 确认除数口径：src 归一化用 999（F-017），第三方环境若按 1000 约定须自行换算（[/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)） |
| 想换指令复测 | grounding 无状态，改 instruction 直接重跑 Cell 4 即可，无需 reset |

## 相关概念

- [/concepts/03-grounding-agent.md](/concepts/03-grounding-agent.md)：predict 内部行为（重试、seed=42、消息结构）
- [/concepts/02-base-agent-traj-memory.md](/concepts/02-base-agent-traj-memory.md)：utils 5 函数的完整清单（F-012）
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：grounding 输出协议与坐标口径对照表
- [/examples/02-navigation-trajectory-notebook.md](/examples/02-navigation-trajectory-notebook.md)：多步导航版 notebook
