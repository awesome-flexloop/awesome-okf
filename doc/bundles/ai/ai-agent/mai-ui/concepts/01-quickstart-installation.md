---
type: Concept
title: "MAI-UI 快速开始：vLLM 部署与双 Agent 初始化"
description: "部署 MAI-UI 的完整前置链路：先起 vLLM 0.11.0 模型服务，再安装根 4 包依赖，最后用 runtime_conf 初始化 MAIGroundingAgent 与 MAIUINaivigationAgent。"
tags: [MAI-UI, vLLM, 快速开始, 安装部署, OpenAI兼容API]
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

MAI-UI 的"安装"分两层：模型服务层（vLLM）与 Agent 使用层（根仓库 4 包依赖）。README 安装章节指定 `pip install vllm==0.11.0`（注明需 transformers>=4.57.0），并强调 "Must use VLLM=0.11.0"（F-004）。第一步必须是部署 vLLM 服务而非安装仓库依赖——`src/` 里没有任何模型运行时代码，两个 Agent 都只是 OpenAI 兼容 API 的客户端（F-003）。

## 第一步：部署 vLLM 模型服务

README 指定的服务启动命令与地址（F-004）：

```bash
pip install vllm==0.11.0
# 需 transformers>=4.57.0
python -m vllm.entrypoints.openai.api_server --served-model-name MAI-UI-8B --port 8000
```

服务地址为 `http://localhost:8000/v1`（F-004）。`--served-model-name MAI-UI-8B` 决定了后续 Agent 初始化时 `model_name` 参数必须填 `"MAI-UI-8B"`——两侧字符串一致，请求才能路由到已加载的模型。

## 第二步：安装根仓库依赖

```bash
pip install -r requirements.txt
```

根 `requirements.txt` 仅 4 个包（F-003）：

| 包 | 版本 |
|---|---|
| Jinja2 | 3.1.6 |
| numpy | 2.3.5 |
| openai | 2.13.0 |
| Pillow | 12.0.0 |

无 torch / transformers——这 4 包只支撑 Agent 客户端（Jinja2 渲染 MCP prompt 模板、Pillow 处理截图、openai 发请求、numpy 做坐标数值处理）。

⚠️ **两套环境不可混装**：仓库实际存在两份 requirements——根目录 4 包版（跑 Agent，F-003）与 `evaluation/grounding/requirements.txt` 的 11 包评估版（跑评测，锁定 `vllm==0.11.0`、`transformers==4.57.0`、`torch==2.8.0` 等，其中 openai==2.2.0、Pillow==10.4.0、numpy==1.26.4 与根版本不一致）（F-045）。日常使用 Agent 只装根依赖；复现评估管线时按评估 requirements 单独建环境（见 [/concepts/06-evaluation-pipeline.md](/concepts/06-evaluation-pipeline.md)）。

## 第三步：初始化两个 Agent

README Quick Start 给出的初始化方式（F-005）：

```python
from mai_grounding_agent import MAIGroundingAgent
from mai_naivigation_agent import MAIUINaivigationAgent

common_conf = {
    "history_n": 3,
    "temperature": 0.0,
    "top_k": -1,
    "top_p": 1.0,
    "max_tokens": 2048,
}

grounding_agent = MAIGroundingAgent(
    llm_base_url="http://localhost:8000/v1",
    model_name="MAI-UI-8B",
    runtime_conf=common_conf,
)

navigation_agent = MAIUINaivigationAgent(
    llm_base_url="http://localhost:8000/v1",
    model_name="MAI-UI-8B",
    runtime_conf=common_conf,
)
```

两个要点：

1. **类名拼写 `Naivigation`** 在 README、源码、notebook 中一贯如此，是检索代码时的关键签名而非笔误（F-005，另见 [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)）。
2. `runtime_conf` 会与类内 default_conf 字典合并（`{**default_conf, **(runtime_conf or {})}`）。grounding 的 default_conf 不含 `history_n`（F-019），navigation 的 default_conf 含 `history_n: 3`（F-026）——`history_n` 只对 navigation 生效，控制图像滑动窗口大小。

## 最小验证路径

依赖就绪后，最快的成功路径是跑 grounding notebook（无基类依赖、单轮调用）：加载仓库自带示例图 → `agent.predict(instruction, pil_image)` → 坐标可视化，完整步骤见 [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md)。多步导航的 5 图循环示例见 [/examples/02-navigation-trajectory-notebook.md](/examples/02-navigation-trajectory-notebook.md)。

## 相关概念

- [/concepts/00-project-overview.md](/concepts/00-project-overview.md)：仓库定位与目录地图
- [/concepts/03-grounding-agent.md](/concepts/03-grounding-agent.md)：MAIGroundingAgent 的构造参数与 predict 行为
- [/concepts/04-navigation-agent.md](/concepts/04-navigation-agent.md)：MAIUINaivigationAgent 的 runtime_conf 与 history_n 语义
- [/concepts/06-evaluation-pipeline.md](/concepts/06-evaluation-pipeline.md)：评估侧独立环境（F-045）的完整说明
- [/examples/01-grounding-notebook.md](/examples/01-grounding-notebook.md)：最小复现示例
- [MobileWorld 评测环境束](../mobile-world/index.md)：把 MAI-UI Agent 跑在真实 Android 容器环境中的下一站
