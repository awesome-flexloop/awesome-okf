---
type: Example
title: "运行官方评测脚本：四个 run_*.sh 的公共模式与差异"
description: "以 scripts/ 下四个官方评测脚本为模板，解读 sudo mw env run --count 5 与 sudo mw eval 的公共模式、四脚本（agentic/claude/gemini/qwen3vl）差异及关键参数含义"
tags: [MobileWorld, 评测脚本, CLI, planner_executor, general_e2e]
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

# 运行官方评测脚本：四个 run_*.sh 的公共模式与差异

仓库 `scripts/` 目录提供了 4 个官方评测脚本：`run_agentic.sh`、`run_claude_e2e.sh`、`run_gemini_e2e.sh`、`run_qwen3vl.sh`（F-072）。它们是"启动容器集群 → 全量评测"的官方标准两段式模板，覆盖了 planner_executor 与 general_e2e 两类 Agent 路线。本篇解读其公共模式、差异点与参数含义，读者换模型跑分时改占位符即可复用。

## 公共模式：两段式

每个脚本的第一行均为（F-072）：

```bash
sudo mw env run --count 5 --launch-interval 20
```

随后统一执行（F-072）：

```bash
sudo mw eval --agent_type <X> --task ALL --max_round 50 --step_wait_time 3 \
    --enable_mcp --enable_user_interaction
```

公共参数解读（F-019、F-020）：

| 参数 | 含义 |
|---|---|
| `--count 5` | 启动 5 个容器并行（`env run`，各端口组从起始值递增分配，F-024） |
| `--launch-interval 20` | 每个容器间隔 20 秒启动 |
| `--task ALL` | 全量任务；报告以 `score > 0.99` 判过，写 `eval_report_{timestamp}.json`（F-022） |
| `--max_round 50` | 最大步数（`--max-round` 的下划线别名，F-019） |
| `--step_wait_time 3` | 每步等待 3 秒（默认 1.0，F-019） |
| `--enable_mcp` | 启用 MCP 工具（任务集合按 `"agent-mcp"` tag 过滤，F-047） |
| `--enable_user_interaction` | 启用用户交互任务（按 `"agent-user-interaction"` tag 过滤，F-047） |

`eval` 的日志默认写 `./traj_logs`（`log_file_root = args.log_file_root or args.output or "./traj_logs"`），`api_key` 缺省取环境变量 `API_KEY`（F-020）。

## 四脚本差异对照

（F-072）

| 脚本 | `--agent_type` | 模型/占位符 | 特殊点 |
|---|---|---|---|
| `run_agentic.sh` | `planner_executor` | executor 模型与 planner 模型分别传占位符 | 加 `--executor_agent_class uiins`（planner/executor 分工，executor 用 grounding 子代理 F-014） |
| `run_claude_e2e.sh` | `general_e2e` | `--model_name claude-sonnet-4-5-20250929` | 设 `HISTORY_N_IMAGES=3`；注释说明 general_e2e 按名称含 "claude" 部分匹配触发图像缩放（对应 F-008 的 claude 分支） |
| `run_gemini_e2e.sh` | `general_e2e` | `--model_name gemini-3-pro-preview` | 设 `HISTORY_N_IMAGES=3` |
| `run_qwen3vl.sh` | `qwen3vl` | `--model_name Qwen3-VL-235B-A22B` | 加 `--log_file_root traj_logs/qwen3_vl_logs` 单独存放日志 |

两条 Agent 路线的含义（F-011 注册表）：

- **planner_executor**：规划与执行分离，执行端固定接 `uiins` grounding 子代理（F-014、F-017）。
- **general_e2e**：单 Agent 端到端，模型怪癖由 BaseAgent 的分支表收敛（F-008）。

## 换模型跑分的改编要点

1. **agent_type 二选一**：有独立 grounding/规划需求用 `planner_executor` + `--executor_agent_class uiins`；端到端模型用 `general_e2e`（F-072）。
2. **模型名影响分支**：名称含 "claude"/"gpt"/"o1"/"kimi-k" 会触发 `openai_chat_completions_create` 的不同参数改写（F-008），命名时注意。
3. **图像窗口**：`HISTORY_N_IMAGES=3` 环境变量控制历史图像张数（F-072）。
4. **密钥**：`.env` 的 `API_KEY` 供 agent 模型、`DASHSCOPE_API_KEY`/`MODELSCOPE_API_KEY` 供 MCP（F-005），`--enable_mcp` 开着就必须配 MCP 密钥（F-025）。
5. **容器规模**：5 容器只是脚本默认；更大规模用 eval-server 编排（F-029、F-043）。
6. **自动发现**：`run_agent_with_evaluation` 在 aw_urls 为空时 `discover_backends` 自动发现 `env run` 启动的容器（F-037），因此两段式脚本无需手工传 `--aw-host`。

## 运行结果查看

评测完成后：`mw logs results` 打印结果表（F-028）；`--pass-k` 场景下报告写 `pass_k_report_{YYYYmmdd_HHMMSS}.json`（F-021）；轨迹在 `./traj_logs` 下（F-020），可视化用 `mw logs view`（默认端口 8760，F-028、F-044）。

## 相关概念

- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——eval 子命令参数体系与报告格式
- [/concepts/03-agent-registry.md](/concepts/03-agent-registry.md)——planner_executor/general_e2e/uiins 的注册与怪癖分支
- [/concepts/06-eval-server-mcp.md](/concepts/06-eval-server-mcp.md)——5 容器不够时的大规模编排
