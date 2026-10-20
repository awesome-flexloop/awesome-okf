---
type: concept
title: "九个工具与三层记忆的实现细节"
description: "inspect / read_pixels / history / play 四个视觉工具与四个笔记工具的参数边界、帧档案落盘、量化符号表、双笔记职责划分与压缩交接的强制次序。"
tags: [vista, tools, inspect, read-pixels, memory, implementation]
generated: { by: "opencode/minimax-m3.1-flash-free", at: "2026-10-20" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-20" }
status: stable
stale_after: 2027-04-20
sources:
  - id: source-code-map
    resource: /references/source-code-map.md
  - id: article-source
    resource: /references/article-source.md
  - id: vista-commit
    url: "https://github.com/joshhhhhan/VISTA/tree/c97c354f0a8948256545a3e8850a1848f8e5b8c1"
---

# 07 · 工具与记忆的实现细节

> 本篇是 [01 三组件机制](01-visual-harness-components.md) 与 [02 记忆与上下文](02-memory-and-context.md) 的**源码层对应**。论文给出机制，源码给出参数边界——两者在每一节末互相指向。

## 一、九个工具的参数边界

工具白名单为 `{"save_compact_checkpoint","inspect","read_pixels","history","play"}`，其余工具名不被派发 [F-107]。

### `inspect`：取回历史帧与区域

| 参数 | 必填 | 约束 | F |
|------|------|------|---|
| `question` | ✅ | 字符串，长度 1–1024 | [F-096] |
| `views` | ✅ | 数组，1–16 项 | [F-096] |
| `views[].label` | ✅ | 字符串，1–128 字符 | [F-096] |
| `views[].turn` | ✅ | 整数 0–999999 | [F-096] |
| `views[].frame` | — | 整数 0–999999；**省略则取该回合的末帧** | [F-096] |
| `views[].region` | — | `{x, y, width, height}`，坐标上限 `display_size-1` | [F-096] |

工具描述对行为的界定很精确 [F-096][F-097]：

> "Each view selects an archived turn; omit frame to use that turn's final frame. Omit region to see the full visual, or select a rectangular region in the same standard {display_size}x{display_size} coordinates used by ACTION6. A selected region is **cropped exactly** from that visual and **enlarged proportionally to fit within {display_size}x{display_size} without smoothing."

三个要点：

1. **每次调用可取多帧**，按请求顺序返回；`question` 与 label 留在调用里 [F-096]。
2. **坐标系与 ACTION6 共用**——模型用同一套坐标既能点击格子，也能裁剪检视 [F-097]。
3. **"without smoothing"** = 最近邻放大，不插值 [F-097][F-105]。

> **一条旧解读被源码升级为事实**：本束此前把"为什么用最近邻而非插值"标为**解读（假设）**（理由是模型不该看到插值出来的颜色）。源码的工具描述与 `render_frame_image` 都明确写了最近邻且**不插值** [F-097][F-105]，因此"避免引入新颜色值"这一效果现在是**源码可见的行为**，而非推断。

### `read_pixels`：精确颜色采样

| 参数 | 必填 | 约束 | F |
|------|------|------|---|
| `question` | ✅ | 字符串，1–1024 字符 | [F-098] |
| `views` | ✅ | 数组，1–**64** 项 | [F-098] |
| `views[].label` / `turn` | ✅ | 同 inspect | [F-098] |
| `views[].region` | ✅ | 必填（与 inspect 不同） | [F-098] |
| `views[].rows` / `columns` | ✅ | 各 1–`display_size` | [F-098] |

行为 [F-098][F-099]：

1. 把 region **等分为 `rows × columns` 格**，**取每格中心像素**采样；
2. 输出"一个 RGB 符号调色板 + 每采样行一条紧凑行字符串"，按请求顺序排列；
3. 单次调用总采样点上限 **4096**；
4. 颜色先经 `quantize_rgb(color, bits)` 量化——默认 `pixel_readout_color_bits = 4`，即**每通道 16 级**；
5. 调色板作用域默认 `pixel_readout_palette_scope = "call"`，**每次调用重建**；符号表 `PIXEL_READOUT_SYMBOLS` 长 64，超出即报 "The pixel readout color limit has been reached."（源码原文含句首 The 与句末句号）

> **口径提醒**：工具名叫 `read_pixels`、论文说"exact pixel readout"，但实现是**量化后的精确**（4 位/通道），不是原始 8 位通道值 [F-099]。对 16 色调色板的 ARC-AGI-3 画面这没有损失；对连续自然风格图像，量化会把 JPEG 噪声折叠掉——这正是 `quantize_rgb` 文档字符串所说的意图 [F-099]。

### `history`：回看动作与环境结果

论文把它列为第三个视觉工具。**源码里有两套语义不同的实现，引用时必须区分** [F-135]：

| 实现 | 使用范围 | 参数 | 返回 |
|------|---------|------|------|
| `TaskContext._history_reply`（`core/support.py:664`） | GameWorld / AI GameStore / BabyVision 等通用任务 | `start` / `end` / `limit` | `{"events": [...], "truncated": bool}` |
| `GameController._history`（`arc3/claude/controller.py:576`） | ARC-AGI-3 | `view`（**必填**，`attempts` 或 `events`）+ `start_turn` / `end_turn` / `limit` | `attempts` 汇总，或按回合的精确动作/结果记录 |

> **`attempts`/`events` 视图选择器只有 ARC-AGI-3 有；`start`/`end` 区间参数只有通用实现有**（ARC-AGI-3 用的是 `start_turn`/`end_turn`）[F-135]。把两套实现合并成一句描述是错的——本束早期版本正是这么写的，已按 E-15 更正。

> **与 `inspect` 的分工**：`inspect` 回看的是**画面**，`history` 回看的是**事件流**。论文附录 A.2 把 `history` 描述为"无损保存并允许主动回看任意历史帧"，源码里它更偏向动作/事件序列——引用时宜按源码口径。

### `play`：一次调用一个动作

`play` 的行为约束写得很死 [F-100]：

> "Execute **exactly one** game action. **Each executed play call counts as one game action.** The result contains the resulting final visual, **the number of archived frames for the action**, and the actions available afterward. The player observes this result before another action can execute."

三个工程细节：

- **串行**：观察结果之后才能执行下一次动作 [F-100]；
- **结果自带帧数**：模型能直接知道"刚才这个动作归档了几帧"（对应动作过程中的动画中间帧）[F-100][F-051]；
- **结果自带可用动作集**：模型不必记住动作表 [F-100]。

### 四个笔记工具

`read_guide` / `write_guide` / `read_working` / `write_working`——`GUIDE.md` 与 `WORKING.md` 是**通过工具**读写的，不是文件系统旁路 [F-095][F-131]。

## 二、帧档案：索引即文件名

| 场景 | 落盘路径 | F |
|------|---------|---|
| 通用任务上下文 | `visuals/turn_%06d_frame_0<ext>`，落盘后 `chmod 0o400`（只读） | [F-102] |
| ARC-AGI-3 harness | `screenshots/turn_%03d_frame_%02d.png` | [F-102] |

帧的获取靠 glob 模式解析文件名：`turn_{turn:03d}_frame_*.png`，帧号取文件名末段 [F-102]。

> **论文说法的实现形式**：论文 §3.1 说每帧"按回合号与帧号索引"、且"独立于模型当前上下文保留" [F-051]——源码把它变成**一个目录加一个文件名约定**，不需要数据库，也不需要额外的索引文件。落盘后 `chmod 0o400` 保证档案不被 Agent 意外改写 [F-102]。

## 三、双笔记：职责划分写进了工具描述

`save_compact_checkpoint` 的描述原文 [F-121]：

> "replacement GUIDE.md **only when the durable game model materially changed**; continuation state that cannot be recovered from GUIDE.md and the current ..."

即：

| 文件 | 何时写 | 内容 | F |
|------|-------|------|---|
| `GUIDE.md` | **持久模型实质变化时**才整体替换 | 跨关卡可复用的游戏理解 | [F-121] |
| `WORKING.md` | 随时 | 无法从 GUIDE.md 与当前画面恢复的交接状态 | [F-121] |

两份文件的权限都是 0600，`GUIDE.md` 的初始内容是 `"No reliable model yet.\n"` [F-103]。

### 压缩交接的强制次序

压缩边界之后，`core/dispatcher.py` 要求**先调用 `save_compact_checkpoint`，再调用其他工具**（"Save the compact checkpoint before using another tool."），否则拒绝 [F-122]。

配套的磁盘标记把交接过程显式化 [F-103]：

| 标记文件 | 作用 |
|---------|------|
| `compact_checkpoint.requested` | 请求保存检查点 |
| `compact_checkpoint.ready` | 检查点就绪 |
| `compact_restore.pending` | 待恢复 |
| `compact_guide.snapshot` | GUIDE.md 快照 |
| `retry_boundary.pending` | 重试边界 |
| `compact_recovery.jsonl` | 恢复过程日志 |

## 四、核心提示词：三句话就是全部方法契约

`src/vista/core/prompts/claude.md` 全文只有三句 [F-118]：

> 1. "Build and use a **compact, revisable model** of the game and its current state. Update it as new evidence changes what is supported."
> 2. "Before each registered game action, **briefly state what you expect to see**. Afterward, briefly state **all visible changes, expected or not**."
> 3. "Keep **concise, durable, revisable** game understanding in `GUIDE.md`; use `WORKING.md` as a **scratchpad** when useful."

这三句与论文机制的对应关系非常直接：

| 提示词 | 对应机制 | 论文位置 | 源码位置 |
|--------|---------|---------|---------|
| 第 1 句 | 跨关卡模型 + 当前状态的双层记忆 | §3.2 GUIDE.md/WORKING.md | `core/prompts/claude.md:3` |
| 第 2 句 | **预测—执行—对比**闭环 | §3 执行流程 | `core/prompts/claude.md:5` |
| 第 3 句 | 结论沉淀与临时草稿的分工 | §3.2 双笔记 | `core/prompts/claude.md:7` |

> **解读（假设）**：整个 VISTA 方法在"给模型说什么"这个层面，被压缩成了三句话；其余全部复杂度——帧档案、坐标空间、量化符号表、压缩交接、凭证隔离——都由 Harness 承担。这是"**harness 决定能力上限**"这一命题最直白的工程证据：模型侧只需要被提醒去预测与记录，其余不必教。

## 五、ARC-AGI-3 的调色板

`arc3/palette.py` 定义 16 色调色板：`FALLBACK_COLOR_MAP` 把索引 0–15 映射为白、五级灰阶、黑、品红、粉、红、青、浅蓝、黄、橙、深红、绿、紫；`COLOR_MAP` **优先取 ARC SDK 的 `SDK_COLOR_MAP`**，缺失时才回落 [F-106]。

`validate_palette_indices` 会对越界颜色索引抛错 [F-140]。这套调色板正是 `read_pixels` 的 4 位/通道量化能无损表达 16 色的原因 [F-099][F-106]。

## 六、下一步

- 把这些跑起来需要什么 → [08 复现与运维](08-reproduction-and-operations.md)
- 这些实现与论文每一节的对应关系 → [09 论文与源码映射](09-paper-source-mapping.md)

## 相关

- [01 三组件机制](01-visual-harness-components.md) · [02 记忆与上下文](02-memory-and-context.md)
- [源码快照登记](/references/source-code-map.md) · [事实登记](/references/article-source.md)
