---
type: Example
title: "真机评测与 leaderboard 提交"
description: "按 docs/real-devices.md 用 USB 真机跑 mw test 评测（含各模型坐标约定表）与按 docs/submit.md 三步提交 leaderboard（bundle_trajs.py 打包 → leaderboard.json 条目 → issue 提交）"
tags: [MobileWorld, 真机评测, ADB, leaderboard, 社区提交]
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

# 真机评测与 leaderboard 提交

除模拟器容器外，MobileWorld 支持 USB 物理手机真机评测（2026-03-20 起支持，F-078），并提供了把轨迹打包提交到官方 leaderboard 的社区通道（F-075、F-079）。本篇覆盖这两个文档化的可复现流程。

## 第一部分：真机评测

### 前置条件

（F-074）

- USB 物理手机 + ADB
- ADBKeyboard.apk 可选（未装时 MobileWorld 自动安装）
- 服务启动：`uv run mobile-world server`

### 运行任务

docs/real-devices.md 的示例命令（F-074）：

```bash
uv run mw test "set an alarm at 8:00 am" --agent-type general_e2e \
    --model_name anthropic/claude-sonnet-4-5 \
    --llm_base_url https://openrouter.ai/api/v1 \
    --aw-host http://127.0.0.1:6800 --api_key ...
```

`test` 子命令接收位置参数 `goal`；不指定 `--device` 时运行 `adb devices` 自动发现——0 台抛 `ValueError("No Android devices found")`，多台抛 `ValueError("Multiple Android devices found, please specify the device ID")`；`aw_url = args.aw_host.split(",")[0]`（F-030）。任务由交互式运行器 `run_user_task` 执行（F-030、F-040）。

### 各模型坐标约定表

不同模型输出的坐标口径不同，接入时必须核对（F-074）：

| 模型 | 坐标约定 |
|---|---|
| Claude Opus 4.7 | 绝对像素坐标 |
| Gemini 3 Pro / Qwen-3.5 / Seed-2.0-Pro | 相对坐标 0–1000 |
| Kimi K2.6 / K2.5 | 相对坐标 0–1 |
| Claude Sonnet 4.5 | 需图像缩放至 1280×720 |

Seed-2.0-Pro 使用 `seed_agent`（F-074）。CLI 的 `--scale-factor` 默认 1000（F-019），与相对 0–1000 口径对应；跨框架复用坐标代码时注意 MAI-UI 源码侧的 SCALE_FACTOR=999 与本框架评估口径 1000 不同（[../mai-ui/index.md](../../mai-ui/index.md)）。

## 第二部分：leaderboard 提交

官方 site/ 目录（leaderboard.json、bundle_trajs.py、trajs/*.json.gz 轨迹包）配合 deploy-pages.yml 工作流构成榜单与社区提交机制（F-079）。docs/submit.md 的三步流程（F-075）：

### 第 1 步：打包轨迹

```bash
uv run python site/bundle_trajs.py traj_logs/your_run -o site/trajs/your-model.json.gz \
    [--with-screenshots --video-base-url ...]
```

把评测日志目录（`./traj_logs` 下的运行目录，F-020）打包为 `.json.gz` 轨迹包。

### 第 2 步：新增 leaderboard 条目

按 `site/leaderboard.json` 既有条目格式新增对象，字段包括（F-075）：

```text
model / organization / date / link / category / model_type / max_steps /
runs / gui_only / user_int / mcp / agent_type / num_images_in_history / notes / traj_file
```

其中 `category` 必须为 `Agentic/General/Specialized` 之一（F-075）。

### 第 3 步：提交

经 GitHub issue 或 Contact 提交 `.json.gz` 与 entry（F-075）。

## 提交前自查

- [ ] 评测用了官方脚本模板的两段式（`env run` + `eval`，见 `/examples/01-run-built-in-eval-scripts.md`）或等效参数（F-072）
- [ ] 用户交互任务注明用户代理模型配置（`USER_AGENT_MODEL` 等，F-005、F-062）
- [ ] 轨迹包由 `site/bundle_trajs.py` 生成且可通过 `--with-screenshots` 附截图（F-075）
- [ ] leaderboard 条目字段齐全、`category` 合法（F-075）

## 相关概念

- [/examples/01-run-built-in-eval-scripts.md](/examples/01-run-built-in-eval-scripts.md)——全量评测的官方脚本模板
- [/concepts/02-architecture-layers.md](/concepts/02-architecture-layers.md)——test 子命令与轨迹日志体系
- [/concepts/00-project-overview.md](/concepts/00-project-overview.md)——site/ 提交机制与版本时间线（Seed-2.0-Pro 真机支持始于 2026-03-20，F-078）
- [../qwen-ui-agent/index.md](../../qwen-ui-agent/index.md)——Qwen-UI-Agent 在 MobileWorld 上 82.1% 的成绩与真机子集
