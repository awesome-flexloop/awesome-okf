---
okf_version: "0.2"
type: bundle
title: "MobileWorld：移动 GUI 智能体评测框架源码精读"
description: "MobileWorld 评测框架源码精读教程——DinD 单容器 Android 评测环境、BaseAgent 契约与九项注册表、任务快照+冻结时钟确定性复现、eval-server 大规模编排与 MCP 工具注入，80 条编号事实全溯源"
tags: [MobileWorld, GUI智能体, 评测框架, Android模拟器, Docker, MCP, 源码精读, 阿里通义, Benchmark]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-29T14:00:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-08-29T14:00:00+08:00" }
status: stable
stale_after: 2026-12-31
sources:
  - id: mobile-world-facts
    resource: /references/facts.md
    title: MobileWorld 源码事实台账
  - id: mobile-world-sources
    resource: /references/source-registry.md
    title: MobileWorld 信源登记
---

# MobileWorld：移动 GUI 智能体评测框架源码精读

MobileWorld（PyPI 包 `mobile-world`，Tongyi-MAI 团队出品）是开源的移动 GUI 智能体评测框架：把 DinD 容器里的 Android 模拟器（Pixel_8_API_34_x86_64 AVD）、FastAPI 控制服务、任务体系与判分逻辑压缩进单个 Docker 镜像，以 `mobile-world`/`mw` 双 CLI 驱动从环境启动到大规模评测的全流程（F-001、F-002、F-067）。初版 2025-12-23 发布（arXiv 2512.19432，F-078），已沉淀出官方榜单与社区轨迹提交机制（F-079）。

本知识包基于**源码直读的 80 条编号事实**（F-001~F-080，零推测）构建：8 篇概念文档沿四层架构（agents/core/runtime/tasks）递进精读，3 篇示例覆盖官方评测脚本、AVD 快照定制与真机/提交流程。每处引用均标注 F-xxx，可在 [references/facts.md](references/facts.md) 检索核对。

## 知识结构总览

```
mobile-world/
├── concepts/                        # 概念文档（8 篇，按学习路径递进）
│   ├── 00-project-overview.md       # 包定义、双 CLI、依赖、版本时间线
│   ├── 01-quickstart-installation.md# .env 六变量、env run、WSL/KVM 前置
│   ├── 02-architecture-layers.md    # 四层地图、CLI 八子命令、FastAPI 19 端点、runner 主循环
│   ├── 03-agent-registry.md         # BaseAgent 契约、九项注册表、文件路径后门
│   ├── 04-tasks-registry.md         # 快照+冻结时钟+后台清理的确定性复现
│   ├── 05-runtime-controller.md     # JSONAction 通用语言、AndroidController 35 方法
│   ├── 06-eval-server-mcp.md        # SQLite WAL 队列 + tmux 编排 40 容器、MCP 工具注入
│   └── 07-docker-environment.md     # DinD 镜像、entrypoint 十步、AVD 快照定制
├── examples/                        # 实战示例（3 篇）
│   ├── 01-run-built-in-eval-scripts.md      # 四个官方评测脚本的两段式模板
│   ├── 02-customize-avd-snapshot.md         # AVD 快照定制八步
│   └── 03-real-device-and-leaderboard-submit.md # 真机评测与榜单提交
├── references/                      # 信源登记（2 篇）
│   ├── facts.md                     # F-001~F-080 事实台账（唯一事实来源）
│   └── source-registry.md           # 九组信源文件清单与覆盖范围
├── index.md                         # 本文件
└── log.md                           # 生成日志
```

## 分层导航

### 概念层（concepts/）

| 文档 | 核心内容 |
|------|---------|
| [项目概述](concepts/00-project-overview.md) | 包定义与双 CLI 入口（F-001/F-002）、40 项依赖与 optional-groups（F-003）、3 个 submodule 应用资源（F-006）、CHANGELOG 时间线（F-078）与 Pages 站点/轨迹提交机制（F-079） |
| [快速开始](concepts/01-quickstart-installation.md) | .env 六变量（F-005）与 env check 校验（F-025）、env run 四组起始端口（F-024）、Windows/WSL/KVM 前置（F-080） |
| [分层架构](concepts/02-architecture-layers.md) | CLI 8 子命令（F-018）与 eval 参数/报告（F-019~F-022）、FastAPI 19 端点（F-033）与 /health 自愈（F-032）、/step 动作分发表（F-034）、runner 主循环与 joblib 并发（F-038） |
| [Agent 注册表](concepts/03-agent-registry.md) | BaseAgent 契约与 token 记账（F-007/F-009）、模型怪癖分支（F-008）、九项注册表（F-011）、create_agent 双路径与文件后门（F-012/F-013）、UIINS 子代理（F-014） |
| [任务体系](concepts/04-tasks-registry.md) | BaseTask 与冻结时钟（F-060）、initialize_task 流程（F-061）、用户代理注入（F-062/F-064）、TaskRegistry 扫描（F-063）、10 场景任务目录（F-066） |
| [运行时层](concepts/05-runtime-controller.md) | AndroidEnvClient 生命周期（F-046/F-047）、AndroidController 32 方法（F-050）与 ask_user 模拟（F-051）、JSONAction 19 动作常量与校验器（F-054）、APP_DICT（F-055）、TrajLogger（F-057）、app_helpers 七模块（F-059） |
| [eval-server 与 MCP](concepts/06-eval-server-mcp.md) | SQLite WAL jobs 表（F-041）、FastHTML 路由（F-042）、40 容器/tmux/5 秒轮询 worker（F-043）、MCP_CONFIG 五服务（F-052/F-076）、SyncMCPClient 串行化（F-053）、按 tag/apps 过滤注入（F-048） |
| [Docker 环境](concepts/07-docker-environment.md) | DinD 镜像分层（F-067）、entrypoint 十步序列（F-068）、start_emulator.sh（F-069）、proxy_chain 旁路代理（F-070）、镜像版本史与 iptables 排坑（F-071）、AVD 快照定制八步（F-073）、dev 模式（F-077） |

### 实战层（examples/）

| 文档 | 核心内容 |
|------|---------|
| [运行官方评测脚本](examples/01-run-built-in-eval-scripts.md) | `sudo mw env run --count 5` + `sudo mw eval` 公共模式与四脚本差异（agentic/claude/gemini/qwen3vl，F-072） |
| [定制 AVD 快照](examples/02-customize-avd-snapshot.md) | dev 容器内改快照 → 定冻结日期 → snapshot save → docker cp → buildx 重建镜像八步（F-073） |
| [真机评测与 leaderboard 提交](examples/03-real-device-and-leaderboard-submit.md) | USB 真机 + 各模型坐标约定表（F-074）、bundle_trajs.py 打包 → leaderboard.json 条目 → issue 提交（F-075） |

### 信源层（references/）

| 文档 | 核心内容 |
|------|---------|
| [MobileWorld 源码事实台账](references/facts.md) | F-001~F-080 全部 80 条编号事实 + 模块覆盖核对表 |
| [MobileWorld 信源登记](references/source-registry.md) | 根配置/agents/core/runtime/tasks/docker/docs/scripts 九组信源的相对路径与覆盖事实范围 |

## 学习路径

```
入门：00 → 01（部署环境，卡壳时跳 07 排查）
核心：02（分层地图）→ 05（JSONAction 是通用语言）→ 03（Agent 接入）→ 04（任务体系）
高级：06（大规模编排与 MCP）→ 07（DinD 环境深度定制，配 examples/02）
依赖：05 的 JSONAction 是 03 的 predict 返回类型与 02 的 /step 分发共同语言；
     04 依赖 05 的 controller；06 依赖 02 的 runner
```

## 跨束互链

本束与同目录的三个知识包构成 Tongyi-MAI 生态的互补视角：

- **[MAI-UI：模型与 Agent 实现](../mai-ui/index.md)**——MAI-UI 是 MobileWorld 排行榜上的模型提交方（CHANGELOG 记录 MAI-UI 41.7%，F-078），且其导航 Agent 以注册名 `mai_ui_agent` 直接进入本框架的 `AGENT_CONFIGS` 九项注册表（F-011），无需任何改造即成为内置 agent——这是两束最强的代码级耦合点。注意坐标口径差异：MAI-UI 源码用 SCALE_FACTOR=999，本框架评估口径默认 1000（F-019）。
- **[Qwen-UI-Agent：技术评测](../qwen-ui-agent/index.md)**——Qwen-UI-Agent 在 MobileWorld 上 82.1%（GUI-Only）的成绩即在本框架取得；本束提供该分数的环境侧解读（快照/冻结时钟/`score > 0.99` 判分阈值，F-021）。
- **[MobilePA-Bench：规划基准](../mobilepa-bench/index.md)**——同属 MAI Team 生态的结构化工具规划基准，与本框架是互补层级而非竞品：MobileWorld 考"端到端在真实 GUI 里做对"（环境实测得分），MobilePA-Bench 考"规划器对结构化工具的调度与状态推理"（托管私有评测），两套分数不可互相替代。

## 信任与生命周期说明

- **事实基础**：80 条编号事实（F-001~F-080）全部采集自本地检出仓库 `external/libs/tools/Tongyi-MAI/MobileWorld`（2026-08-29 源码直读，零推测），采集边界与未逐字读取项见 [references/source-registry.md](references/source-registry.md) 的采集边界说明。
- **引用纪律**：束内每个事实引用均标注 F-xxx 且可回查 [references/facts.md](references/facts.md)；CLI 子命令/类名/签名/环境变量名与事实清单逐字一致。
- **status: stable**——包版本 0.1.0 的源码事实稳定；CHANGELOG 显示项目活跃迭代中（最近条目 2026-04-29，F-078）。
- **stale_after: 2026-12-31**——注册表内容、脚本参数、镜像版本可能随版本演进变化，过期后建议重新核对。
- **方法论链路**：R（事实采集）→ I（架构洞察与知识地图）→ E（信源先行成文）→ V（自检），执行记录见 [log.md](log.md)。

---

**本知识包共收录 13 个内容文档（8 概念 + 3 示例 + 2 信源），外加 3 个子目录索引、根索引与生成日志，合计 18 个文件。**

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
