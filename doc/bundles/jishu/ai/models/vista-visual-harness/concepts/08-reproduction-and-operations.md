---
type: concept
title: "复现与运维：跑通 VISTA 需要的全部前置"
description: "VISTA 的环境前置、授权配置、四个 profile 的运行方式、批量与竞争模式、版本锚点，以及运行时会遇到的失败模式与恢复策略。"
tags: [vista, reproduction, operations, docker, cli, arcmax]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
  - id: article-source
    resource: /references/article-source.md
  - id: vista-commit
    url: "https://github.com/joshhhhhan/VISTA/tree/c97c354f0a8948256545a3e8850a1848f8e5b8c1"
---

# 08 · 复现与运维

> 本篇给出的是**可执行路径**，逐条对应 README 与源码；命令原文来自仓库固定 commit `c97c354f` [F-086]。
> **前置提醒**：本束不提供任何私有集或半私有集相关路径——那部分环境不在任何公开仓库中，需平台授权 [F-130]。

## 一、环境前置（硬性要求）

| 项 | 要求 | F |
|----|------|---|
| 操作系统 | Linux x86_64 | [F-075] |
| Python | **3.12**（`requires-python = ">=3.12,<3.13"`） | [F-090] |
| 容器 | Docker Engine | [F-075] |
| Agent CLI（二选一） | Codex CLI **0.145.0** 或 Claude Code **2.1.220** | [F-075][F-110] |
| 批量运行 | 另需 `tmux` | [F-075] |
| 授权 | ARC Prize 平台账号 + API Key（online/competition 模式必需） | [F-094] |

> **为什么版本被钉得这么死**：源码把 CLI 版本写进了常量——`PINNED_CLAUDE_VERSION = '2.1.220'`、`PINNED_CODEX_CLI_VERSION = 'codex-cli 0.145.0'`，并按版本号计算默认安装路径（`DEFAULT_PINNED_CLAUDE_BIN` / `DEFAULT_PINNED_CODEX_BIN`）[F-132]。连 `arc-agi` / `arcengine` 也钉到 `0.9.9` / `0.9.3` [F-091]。这不是洁癖：Agent CLI 的工具协议与压缩行为会随版本变动，直接影响分数可比性。

## 二、安装（README 原文）

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e .
cp .env.example .env
chmod 600 .env
```

`.env` 需要写入 [F-094]：

```dotenv
ARC_API_KEY=your-key
ARC_BASE_URL=https://three.arcprize.org
CLAUDE_CODE_OAUTH_TOKEN=your-token   # 仅 Claude Code 运行需要
```

非 offline 模式下缺少 `ARC_API_KEY` 会在启动阶段直接报错终止 [F-094]。

### CLI 工具安装

```bash
# Codex CLI
npm install --prefix ~/.local/share/arc3-codex/0.145.0 \
  --omit=dev --no-audit --no-fund @openai/codex@0.145.0
~/.local/share/arc3-codex/0.145.0/node_modules/.bin/codex login

# Claude Code
curl -fsSL https://claude.ai/install.sh | bash -s 2.1.220
~/.local/share/claude/versions/2.1.220 setup-token
```

### Docker 镜像

```bash
docker build -t arc3-codex-player:0.1 -f Dockerfile.codex-player .
docker build -t arc3-claude-player:0.1 -f Dockerfile.claude-player .
```

镜像名与源码常量一致（`PLAYER_IMAGE = 'arc3-codex-player:0.1'` / `'arc3-claude-player:0.1'`）[F-132]。

## 三、统一 CLI 入口

```bash
.venv/bin/vista --profile <arc3|gameworld|aigamestore|babyvision> --backend <codex|claude> ...
```

| 参数 | 约束 | F |
|------|------|---|
| `--profile` | 必填，四选一 | [F-092] |
| `--backend` | 必填，`codex` 或 `claude` | [F-092] |
| profile ≠ arc3 时 | **强制 `--backend codex`** | [F-092] |
| `--operation-mode` | 批量协调器三态 `offline`/`online`/`competition`（默认 competition）；单局 harness 仅 `online`/`offline`（默认 online） | [F-093] |

四个控制台入口中，`vista` 是统一入口，其余三个是各基准的独立 CLI：`vista-gameworld`、`vista-aigamestore`、`vista-babyvision` [F-090]。

## 四、ARC-AGI-3

### 单局

```bash
# Codex
.venv/bin/vista --profile arc3 --backend codex \
  --game-id s5i5 --operation-mode online \
  --model gpt-5.6-sol --effort max

# Claude
.venv/bin/vista --profile arc3 --backend claude \
  --game-id s5i5 --operation-mode online \
  --model opus --effort xhigh
```

### 全部 25 局

```bash
./scripts/run_batch.sh --runtime codex --mode online \
  --model gpt-5.6-sol --effort max -j 2
./scripts/run_batch.sh --runtime claude --mode online \
  --model opus --effort xhigh -j 2
```

25 个公开局的 ID 列表由 `STANDARD_GAME_ORDER` 固定 [F-112]。批量默认并发：Codex 2、Claude 2、Claude 每账号 2 个 worker，调度轮询 5 秒 [F-133]。

### 竞争模式（`--operation-mode competition`）

这是源码里最"重"的一层能力，需要显式配置：

| 能力 | 实现 | F |
|------|------|---|
| 账号调度 | `ClaudeAccountSchedule` / `claude_account_schedule` / `pop_claude_scheduled_game` / `claude_worker_slots`；`.env` 支持 `CLAUDE_CODE_OAUTH_TOKEN_2/_3` | [F-094][F-134] |
| 凭证池 | `ClaudeCredentialPool` / `ClaudeCredentialLease`；5xx 退避 10/30/60/120 秒；容量重试 10/20/40 秒 | [F-119][F-134] |
| 限流感知 | `ClaudeRateLimitEvent` / `rate_limit_event_from_message`；默认排空利用率 0.9、轮询 5 秒 | [F-134] |
| 环境工厂 | `CompetitionEnvironmentFactory` / `CompetitionConfig` / `CompetitionGameResult` / `RuntimeProbeController` | [F-134] |

> **只有 arc3 支持 competition 模式**（`CompetitionConfig.operation_mode` 默认 `competition`，但 preflight 时会降级为 `online`）[F-093]。

## 五、其余三个基准

### GameWorld

```bash
./scripts/env_setup/gameworld.sh
export GAMEWORLD_ROOT="$PWD/local/GameWorld"
export GAMES_ROOT="$PWD/local/GameWorld-Games"

.venv/bin/vista --profile gameworld --backend codex run \
  --gameworld-root "$GAMEWORLD_ROOT" --games-root "$GAMES_ROOT" \
  --game 01_2048 --task 01_01 --model gpt-5.6-sol --effort max \
  --output runs/gameworld-single

./scripts/run_gameworld_batch.sh --backend codex \
  --model gpt-5.6-sol --effort max -j 2
```

每任务 100 步预算（`PRIMARY_STEPS = 100`），与论文的人类预算口径一致 [F-116]。

### AI GameStore

```bash
./scripts/env_setup/aigamestore.sh
export AIGAMESTORE_GAMES_ROOT="$PWD/local/aigamestore/games"

.venv/bin/vista --profile aigamestore --backend codex run \
  --games-root "$AIGAMESTORE_GAMES_ROOT" --game 1 \
  --model gpt-5.6-sol --effort max --output runs/aigamestore-single

./scripts/run_aigamestore_batch.sh --backend codex \
  --model gpt-5.6-sol --effort max -j 2
```

10 个公开游戏；每次决策输出 5 段 × 0.2 秒，最多 120 次决策 [F-115]。

### BabyVision

```bash
./scripts/env_setup/babyvision.sh
export BABYVISION_ROOT="$PWD/local/BabyVision"

.venv/bin/vista --profile babyvision --backend codex run \
  --task-id 666 --model gpt-5.6-sol --effort max \
  --output runs/babyvision-single

# 论文使用的 39 道 Maze + Connect the Lines 题
./scripts/run_babyvision_batch.sh --backend codex \
  --model gpt-5.6-sol --effort max -j 2 \
  --subtypes 'Maze|Connect the lines'
```

> **务必带上 `--subtypes`**：源码默认任务集是 `tracking48`（48 题、含 Lines Observation），而论文评估的是 39 题（Maze + Connect the lines）[F-114][F-130]。不带该参数跑出来的是另一组题。

## 六、运行时目录与产物

单局运行会在工作目录下产出 [F-103]：

```
visuals/                          # 帧档案（0700），turn_%06d_frame_0<ext>，落盘后 0400
screenshots/                      # ARC-AGI-3 的逐帧截图
GUIDE.md                          # 跨关卡结论（0600）
WORKING.md                        # 当前关卡状态（0600）
working_memory_provenance.json    # 工作笔记溯源
compact_recovery.jsonl            # 压缩恢复日志
compact_checkpoint.requested / .ready
compact_restore.pending
compact_guide.snapshot
retry_boundary.pending
```

评测产物会带官方记分卡链接（`open_evaluation_scorecard` / `finalize_scorecard`），这也是论文成绩可被第三方核对的原因之一 [F-076]。

## 七、失败模式与恢复策略

| 失败类型 | 表现 | 源码处理 | F |
|---------|------|---------|---|
| 压缩连续无动作 | 压缩后模型不做动作 | 上限 3 次后判为基础设施终止 | [F-119] |
| 运行期异常 | 环境/运行时错误 | 每步最多 8 次运行期恢复 | [F-119] |
| 决策租约失效 | CLI 侧超时 | 每步最多 5 次决策租约恢复 | [F-119] |
| 服务端 5xx | Provider 过载 | 退避 10/30/60/120 秒 | [F-119] |
| 容量不足 | 并发受限 | 退避 10/20/40 秒 | [F-119] |
| 环境超时 | 连接/读取慢 | 连接 10 秒、读取 120 秒、重连 3 次 | [F-120] |
| 动作重放风险 | 重复提交动作 | HTTP 层强制新连接、**绝不重放已提交动作** | [F-120] |
| 凭证泄漏 | 子进程拿到密钥 | MCP 子进程禁止携带三类凭证 | [F-117] |

五类"基础设施性终止原因"被显式枚举（`compact_recovery_failed`、`controller_error`、`environment_response_missing`、`retry_boundary_interrupt_failed`、`visual_transport_failed`），便于把"环境故障"与"模型能力不足"在统计上分开 [F-119]。

> **解读（假设）**：把基础设施终止单列一类，是为了让"分数不达标"能被正确归因——若把环境崩溃算作模型失败，评测结论会系统性偏悲观。这也是为什么 RHAE 的分母（动作数）与分子（效率）都需要动作不重放作为前提。

## 八、版本锚点总表

复现同一组数字，需要同时对齐以下坐标 [F-086][F-091][F-113]：

| 层 | 锚点 |
|----|------|
| VISTA 源码 | `c97c354f0a8948256545a3e8850a1848f8e5b8c1` |
| VISTA 发布版（`RELEASE_REVISION`） | `900aa3380e4f1120436d83b2ce1115a38ac29bf9` |
| BabyVision 数据集 | `7f92fd4b1dc1c68b7b936a9bc09c68b4a944a55a` |
| GameWorld / 游戏集 | `f2883c34e377c8b73fdb503a4a8e87be12310df7` / `a23b4370c3f99df6fa4ee01ea0299fdab9668b86` |
| ARC SDK | `arc-agi==0.9.9`、`arcengine==0.9.3` |
| Python | 3.12 |
| Agent CLI | Codex 0.145.0 / Claude Code 2.1.220 |

## 九、下一步

- 可直接照做的步骤 → [examples 目录](/examples/index.md)
- 论文每一节的源码落点 → [09 论文与源码映射](09-paper-source-mapping.md)

## 相关

- [06 源码架构总览](06-source-architecture.md) · [07 工具与记忆实现](07-tooling-and-memory-implementation.md)
- [源码快照登记](/references/source-code-map.md) · [事实登记](/references/article-source.md)
