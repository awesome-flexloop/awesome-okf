---
type: example
title: "其余三个基准：GameWorld、AI GameStore 与 BabyVision"
description: "三个非 ARC 基准的环境准备、单次运行与批量运行方式，含各自的协议常量、规模口径与必须注意的参数差异。"
tags: [vista, gameworld, aigamestore, babyvision, run]
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

# 其余三个基准

> 假设已完成 [00 环境准备与授权配置](00-setup-and-auth.md)。
> 三个基准共用同一套 VISTA 工具，但**环境准备方式、动作语义、评分口径完全不同** [F-095]。

## 0. 三个基准的差异速查

| | ARC-AGI-3 | GameWorld | AI GameStore | BabyVision |
|---|---|---|---|---|
| 交互性 | 交互式 | 交互式（浏览器） | 交互式（浏览器） | **静态一问一答** |
| 后端限制 | codex 或 claude | **仅 codex** | **仅 codex** | **仅 codex** |
| 协议常量 | — | `gameworld-computer-use` | `aigamestore-segmented-input` | `babyvision-mllm-one-question-final-answer` |
| 规模 | 25 局 | 34 游戏 / 170 任务 | 10 游戏 | 388 题（论文用 39） |
| 动作 | 8 个（RESET/ACTION1-7） | computer-use 动作 | 分段按键 | 无 |
| 人类参考 | 动作基线 | 两名 CS 研究生，100 动作/任务 | 106 人中位数 | 16 人加权 92.3% [F-137] |

"仅 codex"是源码层面的硬约束：CLI 对非 `arc3` profile 会直接 `parser.error` [F-092]。

---

## 1. GameWorld

### 环境准备

```bash
./scripts/env_setup/gameworld.sh
export GAMEWORLD_ROOT="$PWD/local/GameWorld"
export GAMES_ROOT="$PWD/local/GameWorld-Games"
```

脚本把上游仓库固定到不可变 revision：`GAMEWORLD_REVISION = f2883c34e377c8b73fdb503a4a8e87be12310df7`、`GAMES_REVISION = a23b4370c3f99df6fa4ee01ea0299fdab9668b86` [F-113]。

### 单个任务

```bash
.venv/bin/vista --profile gameworld --backend codex run \
  --gameworld-root "$GAMEWORLD_ROOT" --games-root "$GAMES_ROOT" \
  --game 01_2048 --task 01_01 \
  --model gpt-5.6-sol --effort max \
  --output runs/gameworld-single
```

| 参数 | 说明 | F |
|------|------|---|
| `--gameworld-root` / `--games-root` | 两个上游根目录 | [F-113] |
| `--game` / `--task` | 游戏 ID 与任务 ID | [F-116] |
| `--output` | 输出目录 | [F-115] |

### 全部 170 个任务

```bash
./scripts/run_gameworld_batch.sh --backend codex \
  --model gpt-5.6-sol --effort max -j 2
```

**每任务 100 步预算**（`PRIMARY_STEPS = 100`），与论文的人类预算口径一致 [F-116]。这一条在读分数时很关键：成功率的分母因此是 170 项任务，不是动作数 [F-056]。

> 人类参考由**两名计算机科学研究生**产生，各自尝试全部 170 项任务，预算与智能体相同（每任务 100 动作），其中一名此前无相关经验 [F-081]。因此"人类 55.3%"是个位数样本的参考值，引用时不宜当作"人类平均水平"。

---

## 2. AI GameStore

### 环境准备

```bash
./scripts/env_setup/aigamestore.sh
export AIGAMESTORE_GAMES_ROOT="$PWD/local/aigamestore/games"
```

### 单个游戏

```bash
.venv/bin/vista --profile aigamestore --backend codex run \
  --games-root "$AIGAMESTORE_GAMES_ROOT" --game 1 \
  --model gpt-5.6-sol --effort max \
  --output runs/aigamestore-single
```

### 全部 10 个游戏

```bash
./scripts/run_aigamestore_batch.sh --backend codex \
  --model gpt-5.6-sol --effort max -j 2
```

| 项 | 值 | F |
|----|-----|---|
| 公开游戏 | `PUBLIC_GAMES = range(1, 11)` | [F-115] |
| 输入协议 | 分段输入：每次决策 **5 段 × 0.2 秒** | [F-115] |
| 决策上限 | `MAX_DECISIONS = 120` | [F-115] |
| 动作集 | **11** 个按键（UP/DOWN/LEFT/RIGHT/SPACE/Z/SHIFT/W/A/S/D）+ 11 个 HOLD 变体 + `NOOP`，共 23 个模型可选动作 | [F-136] |
| 评分 | 逐游戏按**人类中位数**归一化，再取**几何平均** | [F-057] |

> **"综合得分 140.3"是几何平均，不是总分** [F-057]。含义是"平均比人类中位数高 40.3%"。附录 B.1 给出的三次运行原始聚合值是 119.99 / 148.58 / 140.06——**波动约 ±14** [F-085]，所以单次运行的 140.3 应视为特定聚合协议下的代表值。

---

## 3. BabyVision

### 环境准备

```bash
./scripts/env_setup/babyvision.sh
export BABYVISION_ROOT="$PWD/local/BabyVision"
```

数据集固定在 revision `7f92fd4b1dc1c68b7b936a9bc09c68b4a944a55a` [F-113]。额外依赖 `regex>=2024.11`（官方答案抽取依赖其递归分组）[F-091]。

### 单题

```bash
.venv/bin/vista --profile babyvision --backend codex run \
  --task-id 666 \
  --model gpt-5.6-sol --effort max \
  --output runs/babyvision-single
```

### 论文使用的 39 题（重要）

```bash
./scripts/run_babyvision_batch.sh --backend codex \
  --model gpt-5.6-sol --effort max -j 2 \
  --subtypes 'Maze|Connect the lines'
```

> **务必带 `--subtypes`**：源码默认任务集是 `tracking48`——48 题，含 `Maze`、`Connect the lines`、**`Lines Observation`** 三个子类 [F-114]。而论文评估的是 39 题（20 Maze + 19 Connect the lines）[F-058]。不带该参数跑出来的是**另一组题**，与论文数字不可比 [F-130]。

| 项 | 值 | F |
|----|-----|---|
| 题集定义 | `TASK_SETS = {'full', 'visual-tracking', 'tracking48'}` | [F-114] |
| 默认 | `tracking48`（48 题、三子类） | [F-114] |
| 论文口径 | 39 题（Maze + Connect the lines） | [F-058] |
| 答案类型 | `blank` 与 `choice` | [F-139] |
| 评测 | 末次 boxed 答案 + 归一化精确匹配；官方 LLM judge 为独立标注步骤 | [F-139] |

> **这个基准没有游戏、没有环境动作**——源码的共享指令原文是 "there is no game, no environment action, and nothing to explore beyond it" [F-114]。因此 BabyVision 验证的是"**视觉检查**组件在无交互场景同样有效"，而不是交互式 Harness 的能力 [F-058]。

---

## 4. 三个基准的结果该怎么读

| 基准 | 主指标 | 人类参考 | 波动 | F |
|------|-------|---------|------|---|
| GameWorld | 成功率（170 项任务） | 55.3%（新手，2 名研究生） | ±2.37% | [F-056][F-081][F-137][F-067] |
| GameWorld | 进度（次指标） | 64.1% | ±2.14% | [F-085][F-067] |
| AI GameStore | 几何平均分 | 100（归一化） | 原始聚合 ±14 | [F-057][F-085] |
| BabyVision | 准确率（39 题） | 92.3%（16 人加权） | ±3.00% | [F-058][F-081][F-137][F-067] |

> **把三行并排看会得出一个容易被"满分 100"掩盖的结论**：在 BabyVision 这类**没有跨多关聚合、基线也不是 upper median** 的任务上，同一套 harness 仍**落后人类 29 个百分点**（63.2% vs 92.3%）[F-081]。原因在指标口径，不在方法本身——详见 [04 跨基准验证](../concepts/04-cross-benchmark-validation.md)。

---

## 5. 下一步

- 结果口径与 RHAE 定义 → [03 ARC-AGI-3 结果与计分口径](../concepts/03-arc-agi3-results.md)
- 完整局限与行动建议 → [05 局限与实践](../concepts/05-limitations-and-practice.md)

## 相关

- [00 环境准备与授权配置](00-setup-and-auth.md) · [01 ARC-AGI-3 单局与批量](01-arc3-single-and-batch.md)
- [08 复现与运维](../concepts/08-reproduction-and-operations.md) · [源码快照登记](/references/source-code-map.md)
