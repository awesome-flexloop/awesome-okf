---
type: concept
title: "论文与源码的逐条映射：三组件、六步消融与两处口径差"
description: "VISTA 论文的每一节在源码中的落点——三组件、六步消融、算法 1、指标公式与提示词附录如何一一对应，以及源码揭示的三处论文未述细节与两处口径差异。"
tags: [vista, paper, source-code, mapping, consistency, errata]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-01-20
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
  - id: paper-reading-map
    resource: /references/paper-reading-map.md
  - id: article-source
    resource: /references/article-source.md
  - id: paper
    url: "https://arxiv.org/abs/2610.02200"
---

# 09 · 论文与源码的逐条映射

> 本篇做一件此前没做的事：**把论文的每一节与源码的每一处对应起来**，并指出两者口径不同的地方。核心问题是"论文说的"和"代码做的"是否一致——答案是：**机制层面高度一致，但有三处论文未述的工程细节、两处口径差异**。

## 一、三组件 → 源码落点

| 论文 §3.1 组件 | 源码实现 | 关键证据 | F |
|----------------|---------|---------|---|
| **visual observations**（视觉观测） | ARC 控制器每回合把观测渲染为帧并交给模型 | `render_observation_frames` → `save_frame_png`；`GRID_SIZE=64`、`RENDER_SCALE=8` | [F-105][F-123] |
| **lossless visual memory**（无损视觉记忆） | `visuals/` 帧档案，按回合号 + 帧号命名，落盘后只读 | `visuals/turn_%06d_frame_0<ext>`、`chmod 0o400` | [F-102][F-123] |
| **visual inspection**（视觉检查） | 三个工具：`inspect`（取帧/裁剪/放大）、`read_pixels`（颜色采样）、`history`（事件回看） | `build_inspect_tool` / `build_read_pixels_tool` / `HISTORY_TOOL` | [F-123] |
| （论文未列为组件） | `play` 动作工具 | `build_play_tool` | [F-100] |
| （论文未列为组件） | 四个笔记工具 `read_guide`/`write_guide`/`read_working`/`write_working` | `core/tools.py:31,211,273,290` | [F-095] |
| （论文未列为组件） | `save_compact_checkpoint` | `core/tools.py:237` | [F-121] |

> **一处口径差**：论文把"视觉检查"归为**一个**组件，源码把它拆成**三个工具**；而论文未列为组件的 `play` 与四个笔记工具，在源码里与视觉工具**同级**。因此"三组件"是**论文的概念划分**，不是源码的模块划分 [F-095][F-123]。

## 二、六步消融 → 源码配置

论文 §4.3 的六步消融在源码中各有明确落点 [F-125]：

| 消融步 | 论文得分 | 源码落点 | F |
|--------|---------|---------|---|
| 官方实现（文本网格） | 13.33 | 非本仓库路径；对照的是 ARC 官方实现 | [F-065] |
| (i) 图像观测 | 47.32 | `render_frame_image`（最近邻放大，512×512 PNG） | [F-105][F-125] |
| (ii) 动作/时间上限 | 51.66 | `DEFAULT_MAX_STEPS = 2000` | [F-111][F-125] |
| (iii) 连续对话 | 65.82 | `run_task_with_native_context`（Claude）/ `run_task_with_compact_checkpoints`（Codex） | [F-108][F-125] |
| (iv) 双笔记 | 70.05 | 四个 read/write 工具 + `GUIDE.md`/`WORKING.md` | [F-095][F-125] |
| (v) 无损记忆 + 视觉检查 | 94.10 | `visuals/` 档案 + `inspect`/`read_pixels` | [F-102][F-125] |
| (vi) 精确像素读出 | 99.00 | `read_pixels`（4 位/通道量化 + 64 符号表） | [F-099][F-125] |

> **最大跃升归属再次确认**：70.05 → 94.10（+24.05）正是 (v)——**无损视觉记忆 + 视觉检查**这两项 VISTA 自有组件 [F-125]。此前容易被误读为"第一步的图像观测贡献最大"，但论文自己在 (i) 注明该配置的低动作数部分源于"run 在通关前触及动作/时间上限" [F-065]。

## 三、附录算法 → 源码签名

| 论文附录 | 源码 | 差异 | F |
|---------|------|------|---|
| A.4 算法 1：`inspect(question, views) -> images`，`view = {label, turn, frame=final, region=full}`，`region = {x,y,w,h}` | `core/tools.py:62-127` 的 JSON Schema | **字段逐一对应**；源码额外给出上限（label 128 字符、question 1024 字符、views 16 项、turn/frame ≤ 999999） | [F-096][F-124] |
| A.2：GUIDE.md 跨关卡跨会话 / WORKING.md 当前关卡临时状态；WORKING.md 随关卡推进清空 | `core/support.py:116-125` 的两个路径；`save_compact_checkpoint` 描述中的"仅在持久模型实质变化时替换 GUIDE.md" | 源码把"何时替换"写成了**工具契约** | [F-103][F-121] |
| A.3：指标公式 | `aigamestore/environment.py:305` `normalized_score(raw_score, human_median)` | 归一化公式在源码中直接可读 | [F-115] |
| A.5：提示词 | `core/prompts/claude.md` + `arc3/{claude,codex}/prompt.md` | 核心提示词只有三句 | [F-118] |
| A.6：人类参考 | `gameworld/upstream.py:17` `PRIMARY_STEPS = 100`；`babyvision/scoring.py` 的 judge 与归一化匹配 | 人类预算口径在源码常量中固化 | [F-116] |

## 四、源码揭示的三处论文未述细节

### 4.1 像素读出是**量化**的，不是原始 8 位

论文说 "exact pixel readout"、§4.3 称 (vi) 为 "exact pixel readout (which provides numerical RGB values for selected pixels)" [F-065]；源码实现的 `quantize_rgb(color, bits)` 默认 **4 位/通道**（每通道 16 级），并用 64 符号的调色板编码 [F-099]。

对 16 色调色板的 ARC-AGI-3 无损；连续自然风格图像上会把噪声折叠掉——这正是 `quantize_rgb` 文档字符串所述意图 [F-099]。

> **引用口径**：说"精确像素读出"时，应补一句"实现为 4 位/通道量化"。本束把该细节记为 **E-12**。

### 4.2 `history` 返回的是**动作与事件流**，不只是帧

论文附录 A.2 把 `history` 描述为"无损保存并允许主动回看任意历史帧"；源码里 ARC-AGI-3 的 `_history` 接受**必填**的 `view`（`attempts`/`events`）与 `start_turn`/`end_turn`/`limit`；通用任务实现则用 `start`/`end`/`limit` 并返回 `{"events", "truncated"}`——**两套实现不可混谈** [F-135]。

> **引用口径**：论文与源码在此处的粒度不同，宜按"动作/事件回看"表述。本束记为 **E-13**。

### 4.3 压缩策略**按后端分叉**，且 `save_compact_checkpoint` 触发机制不同

论文 §3.2 只说"上下文接近上限时模型整理交接摘要" [F-031]；源码则明确分叉：Claude 走**原生压缩**（窗口 1,000,000、90% 触发），Codex 走**注入式交接**（压缩边界强制先调 `save_compact_checkpoint`，否则拒绝其他工具）[F-108][F-122]。

> 这是源码最重要的增量：论文描述的是**统一机制**，实现是**双机制**。记为 **E-14**。

## 五、两处口径差异

### 5.1 上下文窗口：论文 200K vs 源码 272,000

论文 §4.3 称消融默认 "GPT-5.6 Sol, max effort, **200K context**" [F-065]；源码 `DEFAULT_MODEL_CONTEXT_WINDOW = 272000`（回落 128,000），适用 `gpt-5.4/5.5/5.6-` 前缀 [F-109]。

两者不是同一口径：**200K 是论文实验时设定的有效上下文**，**272,000 是源码认为的模型上下文窗口**（压缩预算由它减去硬预留 32,000 与回合余量 40,000 推导）[F-109]。引用时须注明来源，本束记为 **E-11** [F-127]。

### 5.2 动作空间：ARC 论文的口径此前被本束遗漏

ARC-AGI-3 技术报告 §2.3.2 原文 [F-126]：

> "Each environment offers a different action space, which is a subset of: Five key actions, plus an Undo action (reverting to the previous state); One action to select (e.g. click on) a cell from the 64x64 grid by specifying its coordinates."

即**除五个关键动作与 Undo 外，还有一类坐标选择动作**。本束先前的 F-084 只写了"5 个关键动作 + Undo"，遗漏了坐标动作类；源码侧的 `ACTION6` 正是这一类（鼠标点击，与 `inspect` 共用坐标系）[F-101][F-126]。已按 F-126 更正，记为 **E-10**。

## 六、论文与源码一致性的整体判断

| 维度 | 判断 | 依据 |
|------|------|------|
| 三组件机制 | **一致** | 三个组件在源码各有明确实现，且论文的"帧按回合+帧号索引"被实现为文件名约定 [F-123][F-102] |
| 工具语义 | **一致且更细** | 源码给出论文未写的参数上限与量化细节 [F-096][F-099][F-124] |
| 消融阶梯 | **一致** | 六步消融的每一项都有对应配置 [F-125] |
| 默认模型与强度 | **逐格吻合** | 源码默认 `gpt-5.6-sol`/`max` 与 `opus`/`xhigh` 与论文表 1 完全一致 [F-110][F-077] |
| 回合上限 | **一致** | `DEFAULT_MAX_STEPS = 2000` 对应论文的 "2,000 total actions" [F-111][F-079] |
| 上下文口径 | **不一致（需注明来源）** | 论文 200K vs 源码 272,000 [F-127] |
| 压缩机制 | **源码更细** | 论文统一叙述，源码双机制分叉 [F-108][F-128] |
| 实验覆盖面 | **源码小于论文** | 无私有集适配；BabyVision 默认 48 题多于论文 39 题 [F-130] |

> **解读（假设）**：整体上，源码是论文的**忠实实现**而非另一套系统——默认模型、强度、回合上限、消融配置逐项吻合。差异集中在**论文未展开的工程细节**（参数上限、量化、压缩分叉）与**两处需要注明来源的口径**。这意味着：**读论文理解机制，读源码理解可复现性**，两者不能互相替代。

## 七、下一步

- 论文体系与其余基准的关系 → [10 论文谱系与口径边界](10-paper-lineage.md)
- 核验与勘误全表 → [references/verification.md](/references/verification.md)

## 相关

- [06 源码架构总览](06-source-architecture.md) · [07 工具与记忆实现](07-tooling-and-memory-implementation.md) · [08 复现与运维](08-reproduction-and-operations.md)
- [源码快照登记](/references/source-code-map.md) · [论文谱系](/references/paper-reading-map.md)
