---
okf_version: "0.2"
type: bundle
title: "MAI-UI 源码精读教程：GUI Agent 基础模型家族"
description: "通义 Tongyi-MAI 的 MAI-UI GUI Agent 基础模型家族（2B/8B/32B/235B-A22B）源码精读：vLLM 部署、grounding/navigation 双 Agent、轨迹记忆与上下文工程、999/1000 双坐标口径、评估管线双通道，54 条事实源码级可溯源。"
tags: [MAI-UI, GUI智能体, 基础模型, Tongyi-MAI, 源码精读, vLLM, Grounding, Navigation, ScreenSpot-Pro]
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

# MAI-UI 源码精读教程

MAI-UI 是通义 Tongyi-MAI 团队的 GUI Agent（图形界面智能体）基础模型家族，提供 2B/8B/32B/235B-A22B 四个尺寸，其中 2B/8B 权重已在 HuggingFace 发布，技术报告为 arXiv:2512.22047（F-001）。仓库的 `src/` 是纯 OpenAI 兼容 API 客户端外壳（根依赖仅 Jinja2/numpy/openai/Pillow 四包，F-003），模型运行时外置到 vLLM（F-004）——本教程从这一"推理外壳与模型底座解耦"的关键事实出发，覆盖双 Agent（无基类定位 + 继承式导航）、轨迹记忆、上下文工程、prompt 与动作空间、坐标双口径、评估管线六个知识块。

全部内容基于 R 阶段对源码逐行精读采集的 54 条编号事实（F-001~F-054）生成，每个事实引用均可在 [references/facts.md](references/facts.md) 中核验；博客站（MAI-UI-blog）内容仅引用其 HTML 页面事实，两篇 Notion 重定向 stub 博客正文零引用（F-036、F-037）。

## 📚 知识结构总览

```
mai-ui/
├── concepts/                          # 概念文档（7 篇）
│   ├── 00-project-overview.md         # 仓库定位、目录地图、版本谱系、博客站概览
│   ├── 01-quickstart-installation.md  # vLLM 部署、双 Agent 初始化、两套依赖环境
│   ├── 02-base-agent-traj-memory.md   # TrajStep/TrajMemory、BaseAgent 契约、utils 工具
│   ├── 03-grounding-agent.md          # 无基类定位代理：999 归一化、解析、seed=42
│   ├── 04-navigation-agent.md         # 继承式导航：上下文工程三原则、10 个契约测试
│   ├── 05-prompt-action-space.md      # 4 模板、10/12 动作、输出协议、999/1000 对照表
│   └── 06-evaluation-pipeline.md      # 双通道评估、判分、五视图聚合、6 基准统一格式
├── examples/                          # 实战示例（2 篇）
│   ├── 01-grounding-notebook.md       # cookbook/grounding.ipynb 六步复现
│   └── 02-navigation-trajectory-notebook.md  # run_agent.ipynb 5 图轨迹累积
├── references/                        # 信源层（2 篇 + 索引）
│   ├── facts.md                       # F-001~F-054 事实台账（唯一裁决依据）
│   └── source-registry.md             # 信源文件逐项登记
├── index.md                           # 本文件
└── log.md                             # 生成日志（R→I→E 链路）
```

## 🧭 分层导航

| 层 | 入口 | 内容 |
|---|---|---|
| 概念层 | [concepts/](concepts/index.md) | 7 篇，按"入门（00/01）→ 核心（05→02→03/04）→ 高级（06）"学习路径排列 |
| 实战层 | [examples/](examples/index.md) | 2 篇，仓库自带 cookbook notebook 的逐步复现 |
| 信源层 | [references/](references/index.md) | 事实台账（54 条）与信源登记，所有 F-xxx 引用的裁决依据 |

### 概念层明细

| 文档 | 覆盖事实 | 一句话 |
|---|---|---|
| [项目概述](concepts/00-project-overview.md) | F-001~F-003、F-006、F-053、F-054 + 博客站 F-025~F-030、F-033~F-035 | 家族仓库里有什么、没什么；与 Qwen-UI-Agent 的前代关系 |
| [快速开始](concepts/01-quickstart-installation.md) | F-003~F-005、F-019、F-026、F-045 | 先起 vLLM 服务，再装 4 包，最后初始化双 Agent |
| [轨迹记忆与 BaseAgent](concepts/02-base-agent-traj-memory.md) | F-007~F-012 | TrajStep 字段、6 个 property、轨迹管理与工具函数 |
| [Grounding Agent](concepts/03-grounding-agent.md) | F-015、F-017~F-022 | 不继承 BaseAgent 的无状态单轮定位设计 |
| [Navigation Agent](concepts/04-navigation-agent.md) | F-014、F-023~F-034、F-051、F-052 | 文本全量回放 + 图像滑窗 + 回放文本再合成 |
| [Prompt 与动作空间](concepts/05-prompt-action-space.md) | F-013~F-016、F-027 + F-017/F-023/F-025/F-036/F-040 口径 | 4 模板、10/12 动作、999/1000 双口径对照表 |
| [评估管线](concepts/06-evaluation-pipeline.md) | F-035~F-048 | 6 基准统一格式 → 双通道 → 判分 → 五视图 → 汇总 |

### 实战层明细

| 文档 | 覆盖事实 | 一句话 |
|---|---|---|
| [Grounding Notebook 复现](examples/01-grounding-notebook.md) | F-004~F-006、F-012、F-017~F-020、F-049 | 单图定位 → 坐标换算 → 红圈可视化，最低成本成功路径 |
| [Run Agent Notebook 复现](examples/02-navigation-trajectory-notebook.md) | F-005、F-010、F-011、F-026、F-028、F-031~F-034、F-050 | 5 张连续截图循环 predict，观察轨迹累积 |

### 信源层明细

| 文档 | 内容 |
|---|---|
| [事实台账](references/facts.md) | F-001~F-054 全量编号事实 + 模块覆盖核对表 |
| [信源登记](references/source-registry.md) | 伞仓、根文件、src 6 文件、evaluation、cookbook/tests、博客站 stub 逐项登记 |

## 🔗 跨束互链

本束属于 Tongyi-MAI 三束知识体系（mai-ui 模型与 Agent 实现 / mobile-world 评测环境 / mobilepa-bench 规划基准），并与既有 qwen-ui-agent 束构成版本谱系：

- **[Qwen-UI-Agent 技术评测束](../qwen-ui-agent/index.md)**：MAI-UI 的续作项目（伞仓 README 声明 "continuation work of MAI-UI"，F-053）——该束承载后续工作的博文实测与技术评测视角，其"权重混淆勘误"由本束 F-001/F-053 提供仓库级权威细节。
- **[MobileWorld 评测环境束](../mobile-world/index.md)**：MAI-UI 导航 Agent 的评测环境——`MAIUINaivigationAgent` 以注册名 `mai_ui_agent` 直接进入其 Agent 注册表，观测回填（ask_user_response/mcp_response）与动作分发在该束的 runtime/agent 章节展开。
- **[MobilePA-Bench 规划基准束](../mobilepa-bench/index.md)**：同属 MAI Team 的结构化工具规划基准，与 MobileWorld 的"端到端 GUI 执行"构成互补层级——按被测能力层选基准，而非按分数高低。

## ✅ 信任与生命周期说明

- **方法论链路**：R（源码逐行精读，54 条零推测事实）→ I（5 个洞察四元组 + 知识地图）→ E（信源先行批量生成，index 最后写）→ V（toctree/链接/frontmatter/API 一致性自检），详见 [log.md](log.md)。
- **事实边界**：本束仅引用事实台账内条目；博客正文（两篇 Notion stub，F-036/F-037）零引用；官方 URL 仅限已登记的 arXiv/GitHub/HuggingFace 链接。
- **status**：stable——仓库结构与 API 签名均经源码级核验。
- **stale_after**：2026-12-31——模型家族快速迭代（32B/235B-A22B 权重尚未发布，F-001），后续版本可能改变目录结构与评估脚本；到期的分数与安装版本（vLLM 0.11.0，F-004/F-045）应重新核对。
- **分数引用纪律**：博客站 HTML 表与 leaderboard.json 收录范围不一致（F-039），跨束引用任何分数须注明出处文件与快照版本。

**本束共 16 个文件**：7 概念 + 2 示例 + 2 信源 + 3 索引（concepts/examples/references）+ 根索引 + 生成日志。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
