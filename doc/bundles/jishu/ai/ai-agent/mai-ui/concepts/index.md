# 概念文档（Concepts）

本目录包含 MAI-UI 源码精读教程的 7 篇概念文档，按"项目定位 → 部署上手 → 数据结构 → 双 Agent 实现 → Prompt 与动作空间 → 评估管线"的知识依赖顺序排列。

## 学习路径

| 序号 | 文档 | 核心问题 |
|------|------|---------|
| 00 | [项目概述](00-project-overview.md) | MAI-UI 是什么？仓库里有什么、没什么？与 Qwen-UI-Agent 什么关系？ |
| 01 | [快速开始](01-quickstart-installation.md) | 怎么部署 vLLM 服务？怎么初始化两个 Agent？两套依赖环境怎么区分？ |
| 02 | [轨迹记忆与 BaseAgent](02-base-agent-traj-memory.md) | TrajStep/TrajMemory 长什么样？BaseAgent 契约是什么？ |
| 03 | [Grounding Agent](03-grounding-agent.md) | 无基类定位代理怎么设计？999 归一化与解析容错怎么做？ |
| 04 | [Navigation Agent](04-navigation-agent.md) | 多步导航的上下文工程三原则是什么？轨迹怎么回放？ |
| 05 | [Prompt 与动作空间](05-prompt-action-space.md) | 4 个模板怎么切换？10/12 种动作怎么定义？999/1000 双口径差在哪？ |
| 06 | [评估管线](06-evaluation-pipeline.md) | 6 基准怎么统一？双通道怎么跑？五视图指标怎么聚合？ |

### 路径建议

```
入门：00 → 01（配 examples/01）
核心：05（动作空间与输出协议，读 03/04 的前提）→ 02（BaseAgent 契约）→ 03 → 04（配 examples/02）
高级：06（评估管线，依赖 01 的 vLLM 部署）
说明：03 可在 01 后提前阅读（grounding 无基类依赖，是最低成本的成功路径）
```

每篇文档结尾均附"相关概念"章节，可按需跳读；所有事实引用（F-xxx）以 [/references/facts.md](/references/facts.md) 为唯一裁决依据。

```{toctree}
:hidden:
:maxdepth: 2

00-project-overview
01-quickstart-installation
02-base-agent-traj-memory
03-grounding-agent
04-navigation-agent
05-prompt-action-space
06-evaluation-pipeline
```
