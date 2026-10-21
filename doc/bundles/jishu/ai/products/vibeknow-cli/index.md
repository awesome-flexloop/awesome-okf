---
okf_version: "0.2"
type: bundle
title: "VibeKnow CLI——把文档变成视频的终端工具"
description: "VibeKnow CLI 源码级教程（v0.9.2 @ 93a26eca）——八档退出码契约、付费动作授权门、stdout/stderr/磁盘三通道输出、运行账本与异步语义、preset 白名单、字幕样式读-改-写、预览产物去重落盘与 Agent 运行契约"
tags: [vibeknow, cli, ai视频, 文档转视频, agent, 退出码, 授权门, go]
generated:
  by: trae-seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: "2027-04-21"
sources:
  - id: vksrc
    resource: https://github.com/vibeknow/cli
    title: "VibeKnow CLI 源码仓库 v0.9.2 @ 93a26eca"
  - id: facts
    resource: /references/source-facts.md
    title: "VibeKnow CLI 编号事实清单 F-001~F-104"
---

# VibeKnow CLI——把文档变成视频的终端工具

> **类型**：源码级 CLI 教程（以 v0.9.2 固定 commit 为唯一一手信源）
> **信源**：`github.com/vibeknow/cli`，tag `v0.9.2`，commit `93a26eca3383d480148c5cfd8da7995ee3352187`（2026-09-09），18 个 tag，工作树干净
> **方法论**：七概念场景 4 知识沉淀链路 R→I→E→V→C；事实登记 104 条（F-001~F-104）

## 本文概要

VibeKnow CLI 是把文档、URL、文件变成视频的 Go 终端工具。它最值得读的地方不是功能清单，而是**它几乎每一处约束都在为「被 Agent 驱动」而设计**：

- **退出码是契约本体**——0/1/2/3/4/5/6/7/8 八档各有可判定语义，其中 6 是「投递状态三态」（submitted / not_submitted / indeterminate），8 是「需要用户决策的计费动作阻断」
- **付费动作拆成两段**——「展示条款」与「授予同意」分离，同意凭据是载荷的 HMAC 哈希（`act_` 前缀），非交互环境下 CLI 拒绝替用户决定
- **三条通道各司其职**——stdout 是答案、stderr 是过程（`vk_event=` 前缀）、磁盘是记忆（`jobs.jsonl` 账本）
- **preset 只描述长相与声音**——14 个允许键、9 个拒绝键（授权类与单次调用类一律拒收），命令行永远赢
- **预览产物按内容哈希去重**——`resource_ready` 事件给本地产物路径，签名 URL 绝不进事件

## 文档结构

### concepts/ — 概念解析

| 文档 | 主题 |
|------|------|
| [00-cli-overview.md](concepts/00-cli-overview.md) | 定位、19 个顶层命令的命令树全貌、四后端服务划分、配置目录解析与构建产物、首次使用前的 6 步准备 |
| [01-exit-code-contract.md](concepts/01-exit-code-contract.md) | 八档退出码速查、命令行层面收敛、4 与 5 的分界、exit 6 三态判定、阻塞式与单次读取式的分界规则 |
| [02-paid-action-gate.md](concepts/02-paid-action-gate.md) | `cmdutil.Gate` 四级解析、action_id 的 HMAC 派生、两个授权边界类型、exit 8 的三种输出形态、无人值守三场景处置 |
| [03-output-and-events.md](concepts/03-output-and-events.md) | text/json/ndjson 与优先级、刻意不做管道自动切、`vk_event=` 事件通道开启规则、advisory 语义、统一快照结构 |
| [04-run-ledger-and-async.md](concepts/04-run-ledger-and-async.md) | `jobs.jsonl` 六状态与 best-effort 写入、三级目标解析、`--async` 的 60 秒脱离上限、导出幂等与 exit 6/7 触发点 |
| [05-create-parameter-space.md](concepts/05-create-parameter-space.md) | `--mode` 四档与 `--engine` 两档的正交组合、引擎×类型拒绝矩阵、`--pages`/`--aspect`/`--language`/`--images` 取值域、`--from` 四种来源、完整校验顺序 |
| [06-preset-contract.md](concepts/06-preset-contract.md) | 14 允许键 / 9 拒绝键、pflag `Changed` 实现命令行优先、`schema_version=1` 与 `KnownFields(true)`、搜索目录与「无 `vk preset list`」现状 |
| [07-subtitle-style-and-work-edit.md](concepts/07-subtitle-style-and-work-edit.md) | work 级旗标集合、字幕样式 10 旗标的读-改-写、preset 先落单旗标后落、`strokeWidth=0` 与未设置的区分、`export_invalidated` 提示链 |
| [08-preview-artifacts.md](concepts/08-preview-artifacts.md) | `--preview-dir` 落盘契约、两类资产、`resource_ready` 字段、按内容 sha256 去重、临时文件+rename 原子写入、文件名 slug 消毒 |
| [09-cleanup-safety-contract.md](concepts/09-cleanup-safety-contract.md) | `kb prune` 强制筛选与默认 dry-run、分页常量、`jobs prune` 裸调用被拒、账本「缺失≠不存在」、prune 的三档退出码 |
| [10-ai-skill-contract.md](concepts/10-ai-skill-contract.md) | 三个 Skill 的结构与 frontmatter、Run Contract 的硬约束、outline→tts→render→publish 四阶段、事件与授权决策的消费方式 |

### examples/ — 实操示例

| 文档 | 主题 |
|------|------|
| [00-first-video.md](examples/00-first-video.md) | 认证四形态 → 素材三路 → 同步渲染与 `--preview-dir` → 导出授权门 → 下载，含常见卡点对照表 |
| [01-agent-safe-automation.md](examples/01-agent-safe-automation.md) | 六条铁律速查、分步等待脚本、stdout/stderr 分离、事件游标与 offset 记录、exit 8/6/7 分支处置、只读命令清单 |
| [02-style-reuse-and-maintenance.md](examples/02-style-reuse-and-maintenance.md) | preset 固化外观、`video set` 免费改动与重新导出、`video edit` 单镜头改稿（计费）、知识库与账本清理范式 |

### references/ — 信源登记

| 文档 | 说明 |
|------|------|
| [source-code-map.md](references/source-code-map.md) | 目录构成、命令文件归属、27 个 internal 包与四个服务客户端的对应、配置目录解析顺序 |
| [exit-code-contract.md](references/exit-code-contract.md) | 八档退出码全表与后端码映射、5 个失败类型常量、9 条命令行解析失败前缀、exit 6 三态表 |
| [flag-inventory.md](references/flag-inventory.md) | 104 处旗标注册调用的逐文件分布、72 个全局去重旗标名、`vk create` 23 个自有旗标、`cmd/video` 44 个旗标对 |
| [backend-endpoints.md](references/backend-endpoints.md) | 四个服务客户端的 39 个去重端点、HTTP 方法与用途、引擎↔端点对应、端点提取口径 |
| [source-facts.md](references/source-facts.md) | F-001~F-104 完整清单（每条带仓库内相对路径与行号），含四轮计数勘误的审计轨迹 |

## 已知边界

- **未实机执行**：本文全部内容来自 v0.9.2 源码与仓库自带 `AGENTS.md` / `skills/` 文档的静态阅读，**未连接后端实测**；涉及计费、后端状态、渲染效果的部分请以自己的账号验证为准
- **固定信源**：以 tag `v0.9.2` / commit `93a26eca` 为准；该仓库仍在演进，后续版本的退出码、旗标与端点可能变化，`stale_after` 设为 2027-04-21
- **数量口径**：旗标数 104/103/72、端点数 39、internal 代码行数 6803 均标注了统计口径与提取方式，不同口径不可混用
- **文档索引不含 `docs/`**：CLI 仓库自带的 `AGENTS.md` 与 `skills/` 是本教程的一手信源，但其自身不覆盖全部命令的细节，本教程以源码为准

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
