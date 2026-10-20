---
type: example
title: "ARC-AGI-3：单局、全部 25 局与竞争模式"
description: "ARC-AGI-3 的单局运行、25 局批量运行与竞争模式编排，含默认参数、并发设置、运行产物与失败排查。"
tags: [vista, arc-agi-3, run, batch, competition]
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

# ARC-AGI-3：单局、全部 25 局与竞争模式

> 假设已完成 [00 环境准备与授权配置](00-setup-and-auth.md)。
> 命令原文来自仓库固定 commit `c97c354f` 的 README 与 `scripts/` [F-086]。

## 1. 单局运行

### Codex（GPT-5.6 Sol，max effort）

```bash
.venv/bin/vista --profile arc3 --backend codex \
  --game-id s5i5 \
  --operation-mode online \
  --model gpt-5.6-sol \
  --effort max
```

### Claude（Opus 5.0，xhigh effort）

```bash
.venv/bin/vista --profile arc3 --backend claude \
  --game-id s5i5 \
  --operation-mode online \
  --model opus \
  --effort xhigh
```

### 参数说明

| 参数 | 取值 | 默认 | F |
|------|------|------|---|
| `--profile` | `arc3` | 无（必填） | [F-092] |
| `--backend` | `codex` / `claude` | 无（必填） | [F-092] |
| `--game-id` | 25 个公开局 ID 之一 | — | [F-112] |
| `--operation-mode` | `online` / `offline` | `online` | [F-093] |
| `--model` | `gpt-5.6-sol` / `opus` / 完整模型 ID | Codex: `gpt-5.6-sol`；Claude: `opus` | [F-110] |
| `--effort` | Codex: minimal…ultra；Claude: low…max | Codex: `max`；Claude: `xhigh` | [F-110] |

> **默认参数与论文表 1 完全对应**：Opus 5.0 用 **xhigh**、GPT-5.6 Sol 用 **max** [F-110][F-077]。若你改了 `--effort`，分数就不再与论文可比。

### 25 个公开局 ID

`bp35`、`sk48`、`lf52`、`wa30`、`sp80`、`re86`、`su15`、`vc33`、`ka59`、`dc22`、`ls20`、`tn36`、`g50t`、`sc25`、`tu93`、`s5i5`、`cn04`、`tr87`、`ar25`、`m0r0`、`r11l`、`lp85`、`ft09`、`cd82`、`sb26` [F-112]。

> `ar25` 值得注意：它正是论文逐局表中动作数最多的那一局（256 动作）[F-112][F-138]。

### offline 模式

需要本地游戏文件时用 `--operation-mode offline`，并通过 `ENVIRONMENTS_DIR` 指向本地环境目录 [F-093]。offline 模式**不需要** `ARC_API_KEY` [F-094]。

## 2. 全部 25 局

```bash
./scripts/run_batch.sh --runtime codex --mode online \
  --model gpt-5.6-sol --effort max -j 2

./scripts/run_batch.sh --runtime claude --mode online \
  --model opus --effort xhigh -j 2
```

| 参数 | 说明 | F |
|------|------|---|
| `--runtime` | `codex` / `claude` | [F-110] |
| `--mode` | `offline` / `online` / `competition` | [F-093] |
| `-j` | 并发数，默认 **2** | [F-110] |
| `--model` / `--effort` | 同单局 | [F-110][F-133] |

批量运行**需要 `tmux`** [F-075]。

> **论文成绩的复现要点**：论文的 25 局跑分是"同一模型 + 同一 effort + 完整 25 局"的口径。少跑几局或降低 effort 得到的分数无法与之比较；多次运行的波动应按附录 B.1 的口径报告（ARC ±0.17）[F-067]。

## 3. 竞争模式

`--operation-mode competition` 启用完整编排：账号调度、凭证池、限流感知与运行时预检。

```bash
# 基础竞争运行
./scripts/run_batch.sh --runtime claude --mode competition \
  --model opus --effort xhigh -j 2
```

竞争模式需要额外准备 [F-113][F-119]：

| 项 | 配置 | 说明 |
|----|------|------|
| 多账号凭证池 | `.env` 中 `CLAUDE_CODE_OAUTH_TOKEN` / `_2` / `_3` | `ClaudeCredentialPool` 按凭证分配并发槽位 |
| 账号调度 | 源码内置 `ClaudeAccountSchedule` | 把 25 局按计划分配给不同账号，避免单账号限流 |
| 限流处理 | `ClaudeRateLimitEvent` | 识别限流事件，默认排空利用率 0.9、轮询 5 秒 [F-134] |
| 退避策略 | 5xx → 10/30/60/120 秒；容量不足 → 10/20/40 秒 | [F-119] |
| 并发 | 每账号 worker 数默认 **2**，调度轮询 5 秒 | [F-133][F-134] |
| 强制 effort | 竞争模式默认 Claude effort 为 `xhigh` | [F-110][F-133] |

> **为什么竞争模式这么重**：ARC Prize 的公开集评测对提交与并发有专门流程，源码为此实现了账号池与调度器——这是"论文数字能否被官方记分卡采纳"的操作前提 [F-076]。

## 4. 运行产物

单局运行后的工作目录 [F-103]：

```
visuals/                # 帧档案（0700）；turn_%06d_frame_0<ext>，落盘后 0400
screenshots/            # ARC-AGI-3 逐帧截图 turn_%03d_frame_%02d.png
GUIDE.md                # 跨关卡结论（0600）
WORKING.md              # 当前关卡状态（0600）
working_memory_provenance.json
compact_recovery.jsonl
compact_checkpoint.requested / .ready
compact_restore.pending / compact_guide.snapshot / retry_boundary.pending
```

**值得一读的两个文件**：

- `GUIDE.md`——模型自己沉淀的、对该游戏的理解。这是最能直接看出"视觉经验是否真的被复用"的地方 [F-103]。
- `WORKING.md`——当前关卡的临时状态，关卡推进时清空 [F-053]。

评测产物会带官方记分卡链接（`open_evaluation_scorecard` / `finalize_scorecard`），可在 ARC Prize 站点核对 [F-076]。

## 5. 失败排查

| 症状 | 原因 | 处理 | F |
|------|------|------|------|
| 启动即报缺 `ARC_API_KEY` | online/competition 模式未配置凭证 | 写入 `.env` 或 export | [F-094] |
| 报 "profile X requires --backend codex" | 非 arc3 profile 只支持 Codex | 改用 `--backend codex` | [F-092] |
| 找不到 Agent CLI | 版本号与默认安装路径不符 | 按 [00 步骤 4](00-setup-and-auth.md) 重装 | [F-110] |
| 找不到 `arc3-*-player:0.1` 镜像 | 未构建或镜像名不符 | 重新 `docker build`，名字须含 `:0.1` | [F-110] |
| 跑到一半终止，原因 `compact_recovery_failed` | 压缩连续 3 次无动作 | 属基础设施终止，非模型能力问题 | [F-119] |
| 终止原因 `environment_response_missing` | 环境未回帧 | 检查 ARC 端点可达性与凭证 | [F-119][F-120] |
| HTTP 层疑似重发动作 | 不应发生——适配器强制新连接且**从不重放已提交动作** | 若怀疑，先查 `compact_recovery.jsonl` | [F-120] |
| 上下文提前耗尽 | Claude 原生压缩 90% 触发；Codex 由 272,000 窗口推导预算 | 属正常交接，检查点会自动保存 | [F-108][F-109] |

## 6. 下一步

- 跑 GameWorld / AI GameStore / BabyVision → [02 其余三个基准](02-other-benchmarks.md)
- 这些数字该怎么读 → [03 ARC-AGI-3 结果与计分口径](../concepts/03-arc-agi3-results.md)

## 相关

- [00 环境准备与授权配置](00-setup-and-auth.md) · [08 复现与运维](../concepts/08-reproduction-and-operations.md) · [07 工具与记忆实现](../concepts/07-tooling-and-memory-implementation.md)
