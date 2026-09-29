# 概念文档（Concepts）

本目录包含 MobileWorld 评测框架源码精读的 8 篇概念文档，按"项目概述→部署→架构→三大子系统（agents/tasks/runtime）→高级编排→容器环境"递进排列。

## 学习路径

| 序号 | 文档 | 核心问题 |
|------|------|---------|
| 00 | [项目概述](00-project-overview.md) | MobileWorld 是什么？CLI 入口与依赖怎么组织？版本如何演进？ |
| 01 | [快速开始](01-quickstart-installation.md) | .env 怎么配？第一个容器怎么起？Windows 宿主要什么前置？ |
| 02 | [分层架构](02-architecture-layers.md) | 四层怎么分工？CLI 八子命令与 FastAPI 19 端点长什么样？runner 主循环怎么跑？ |
| 03 | [Agent 注册表](03-agent-registry.md) | 接一个新模型最少要实现什么？九项注册表与文件后门怎么用？ |
| 04 | [任务体系](04-tasks-registry.md) | 任务如何做到确定性复现？快照/冻结时钟/后台清理缺一不可？ |
| 05 | [运行时层](05-runtime-controller.md) | JSONAction 为什么是通用语言？AndroidController 有哪些能力？ |
| 06 | [eval-server 与 MCP](06-eval-server-mcp.md) | 40 容器怎么编排？MCP 工具按什么规则注入？ |
| 07 | [Docker 环境](07-docker-environment.md) | DinD 单容器全栈怎么构建与启动？AVD 快照怎么定制？ |

### 路径建议

```
入门：00 → 01（部署环境，卡壳时跳 07 排查）
核心：02（分层地图）→ 05（JSONAction 是通用语言）→ 03（Agent 接入）→ 04（任务体系）
高级：06（大规模编排与 MCP）→ 07（DinD 环境深度定制，配 examples/02）
```

依赖关系：05 的 JSONAction 是 03 的 predict 返回类型与 02 的 /step 分发共同语言；04 依赖 05 的 controller；06 依赖 02 的 runner。

```{toctree}
:hidden:
:maxdepth: 7

00-project-overview
01-quickstart-installation
02-architecture-layers
03-agent-registry
04-tasks-registry
05-runtime-controller
06-eval-server-mcp
07-docker-environment
```
