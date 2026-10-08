---
type: Concept
title: "MAI-UI 轨迹记忆与 BaseAgent 抽象契约"
description: "解读 unified_memory.py 的 TrajStep/TrajMemory 数据结构、base.py 的 BaseAgent 抽象类（predict 契约、6 个只读 property、轨迹管理方法）与 utils.py 的 5 个工具函数。"
tags: [MAI-UI, TrajMemory, BaseAgent, 轨迹记忆, 数据结构]
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

MAI-UI 的导航 Agent 之所以能做多步任务，靠的是一套统一的轨迹记忆结构：`src/unified_memory.py` 定义了 `TrajStep` 与 `TrajMemory` 两个 dataclass（文件 docstring 为 "Unified memory structures for trajectory tracking"，F-007、F-008），`src/base.py` 的 `BaseAgent(ABC)` 则把它们变成所有多步 Agent 的契约（docstring "Base agent class for mobile GUI automation agents"，F-009）。本篇讲解这三个抽象层，它们是理解 [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md) 的前提。

## TrajStep：单步轨迹的完整快照

`@dataclass class TrajStep`（F-007）的字段分两组：

**必填字段（9 个）**：

| 字段 | 类型 | 含义 |
|---|---|---|
| `screenshot` | `Image.Image` | 当前步截图（PIL 对象） |
| `accessibility_tree` | `Optional[Dict[str, Any]]` | 无障碍树（可空） |
| `prediction` | `str` | 模型原始输出文本 |
| `action` | `Dict[str, Any]` | 解析出的动作 JSON |
| `conclusion` | `str` | 结论 |
| `thought` | `str` | 思考文本 |
| `step_index` | `int` | 步序号 |
| `agent_type` | `str` | Agent 类型标识 |
| `model_name` | `str` | 模型名 |

**默认字段（4 个，均 `= None`）**：`screenshot_bytes`（截图 bytes 副本）、`structured_action`（结构化动作，navigation Agent 写入 `{"action_json": ...}`）、`ask_user_response`、`mcp_response`（F-007）。

注意 `ask_user_response`/`mcp_response` 两个字段由外部 runtime 回填而非 Agent 自身的 predict 写入（F-033）——在评测环境 MobileWorld 的 runner 主循环中，这两个观测键由外部宿主注入（见 [MobileWorld 束的 runtime 章节](../../mobile-world/index.md)）。

## TrajMemory：任务级容器

`TrajMemory(task_goal: str, task_id: str, steps: List[TrajStep] = field(default_factory=list))`——任务目标、任务 ID 与步列表三件套（F-008）。

## BaseAgent：predict 契约与 6 个只读 property

`class BaseAgent(ABC)` 的 `__init__` 初始化 `self.traj_memory = TrajMemory(task_goal="", task_id="", steps=[])`（F-009）。抽象方法签名：

```python
def predict(self, instruction: str, obs: Dict[str, Any], **kwargs: Any) -> Tuple[str, Dict[str, Any]]
```

即所有子类必须实现"指令 + 观测字典 → (原始输出文本, 动作字典)"的契约（F-009）。

BaseAgent 提供 6 个只读 property，从 `traj_memory.steps` 派生数据（F-010）：

| property | 返回类型 | 内容 |
|---|---|---|
| `thoughts` | `List[str]` | 各 step.thought |
| `actions` | `List[Dict[str, Any]]` | 各 step.action |
| `conclusions` | `List[str]` | 各 step.conclusion |
| `observations` | `List[Dict[str, Any]]` | 每项为 `{"screenshot": step.screenshot_bytes, "accessibility_tree": step.accessibility_tree}` |
| `history_images` | `List[bytes]` | 各 step.screenshot_bytes |
| `history_responses` | `List[str]` | 各 step.prediction |

以及 3 个轨迹管理方法（F-011）：

```python
def reset(self) -> None: ...            # 重建空 TrajMemory
def load_traj(self, traj_memory: TrajMemory) -> None: ...  # 直接替换 self.traj_memory
def save_traj(self) -> Dict[str, Any]: ...  # 导出 task_goal/task_id/steps
```

`save_traj` 返回的每个 step 是 9 字段 dict：screenshot_bytes、accessibility_tree、prediction、action、conclusion、thought、step_index、agent_type、model_name（F-011）。

## utils：5 个图像/坐标工具函数

`src/utils.py` 提供（F-012）：

```python
safe_pil_to_bytes(image: Union[Image.Image, bytes]) -> bytes      # PIL 转 PNG bytes
pil_to_base64(image: Image.Image) -> str                          # PNG base64 字符串
save_screenshot(screenshot: Image.Image, path: str) -> None       # 保存截图
extract_click_coordinates(action: Dict[str, Any]) -> Optional[Tuple[float, float]]
    # 读 action['coordinate']，grounding notebook 用它换算绝对坐标
draw_clicks_on_image(image_path: str, click_coords: Tuple[float, float],
                     output_path: Optional[str] = None) -> Image.Image
    # 在图上画半径 20 的红色圆
```

这 5 个函数是 cookbook 两个 notebook 的可视化基础（F-049、F-050），也是自定义集成时最常复用的部分。

## 设计要点：memory 与 agent 分层

这套结构把"记什么"（TrajStep 字段）与"怎么用"（BaseAgent property 派生 + 子类覆写）分开：navigation Agent 覆写 `history_responses` property，把回放文本从原始 `prediction` 换成坐标反归一化后的规范化文本（见 [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)）——基类只提供数据视图，子类决定视图语义。

## 相关概念

- [/concepts/03-grounding-agent.md](/concepts/03-grounding-agent.md)：刻意不继承 BaseAgent 的对照设计
- [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)：BaseAgent 契约的具体实现者
- [/concepts/05-prompt-action-space.md](/concepts/05-prompt-action-space.md)：TrajStep.action 字段的动作 JSON 从哪来
- [/examples/02-navigation-trajectory-notebook.md](/examples/02-navigation-trajectory-notebook.md)：轨迹累积的最小可运行示例
- [MobileWorld 评测环境束](../../mobile-world/index.md)：`mai_ui_agent` 的注册与观测回填（ask_user_response/mcp_response 的外部宿主）
