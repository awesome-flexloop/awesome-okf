---
okf_version: "0.2"
type: Concept
title: "自治 harness 可靠性工程：故障方向、误删事故与遥测重建"
description: "130-170h 无人值守必然遇故障：HWE Bench 的原则是让每个已知故障只制造假失败、不制造假通过——seatbelt 误删事故、大声崩政策与 git 遥测重建"
tags: [HWE Bench, harness工程, 故障方向, 遥测, 隔离]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T17:00:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-14T19:30:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-facts
    resource: /references/facts.md
    title: "HWE Bench 事实登记表 F-001~F-126"
  - id: hwe-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb"
---

## 问题尺度：故障不是例外，是必然事件

V1 方法学预估的运行尺度（作者报告）是：xhigh premium 模型每 rep 约 **4-5h** wall，11 模型 × 3 rep 加对照串行约 **130-170h**（F-091）。单个 rep 就是 45 个候选各跑一遍 lint→synth→formal→cosim→3-seed FPGA 的长任务（F-080）。在这种尺度下无人值守地跑，环境性故障（沙箱权限、PID 回收、解析器漂移、进程残留）必然发生——可靠性因此不是「让故障不出现」，而是设计故障发生后的**错误方向**与**现场留存**。

## 核心原则：错误方向的非对称

作者在事故日记中把原则讲得很直白：**"This can only produce false failures, never false passes."**（F-126）。两类错误的代价不对称：

- **假失败（false failure）**：一个本来有效的设计/rep 没拿到分——代价是数据点缺失，可隔离、可重跑；
- **假通过（false pass）**：一个无效结果被计分——代价是污染排行榜且几乎不可追溯。

工程目标因此是：**所有已知故障模式只产生假失败（不计分），绝不产生假通过（错计分）**。一次 harness 删掉自己工作目录的事故，正是被当作「系统按正确方向失败」的正面案例记录的（F-126）。

## seatbelt EPERM 事故全链

F-126 记载了完整事故链（[diary 2026-09-25 L72-L88](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/diary/2026-09-25.md#L72-L88)）：

1. `formal/run_all.sh` 在 `kill -0 <pid>` 失败时回收 `riscv-formal/cores/<core>-<pid>` 工作目录；
2. 每克隆的 `formal/riscv-formal` 副本对 Claude seatbelt 沙箱**可写**；
3. 在 seatbelt 沙箱内，对任何**外部 PID** 执行 `kill -0` 一律返回 **EPERM**（实测探针确认）；
4. 于是 round 8 slot 2 实现代理的 formal 自检（02:04:50Z）把 **harness 自己的活工作目录（PID 91122）** 误删，02:04:51Z 起每个 `make .../status` 全失败；
5. 前兆信号是 round 8 slot 1 报 `make_failed_during_execution / no_checks_generated`，但该 formal 运行自己的 per-check 日志全是 pass——空过计数与现场日志的矛盾暴露了目录被破坏。

处置与修复：commit `d3c9cd7` 把克隆内 formal/riscv-formal（含解析后路径）对 agent 设为 **denyWrite**（探针验证 `rm` 被拒）；commit `7a7d593` 进一步把临时根下的游离文件设为拒读。现场完整保留在 `aborted1-formal-reaper/`（journal round 0-7、日志、NOTES.md），其中 **best 601.32（round 6，n=1，partial）显式不计分、不写入 results.jsonl**（F-126）。由于 round 1-7 无 formal 失败，没有任何已记账 outcome 被改变——错误方向被实测确认为单向。

## 同类设计：大声崩溃，而不是替零

同一原则贯穿评测代码的多个故障点：

- **LUT4/DFF 解析失败永不替 0**：设了 LUT 目标时 0 LUT4 是最佳面积分，日志格式漂移若被静默替成 0，会让每个假设都「获胜」——那就是假通过。代码选择大声失败（`fpga_report_unparsed`），失败只丢这一个候选（F-075）。
- **formal 计数 TOTAL=0 强制 FAIL**：PASS+FAIL=0 时记 `no_checks_generated` 并判失败，防止 genchecks 崩溃只产出一个空过任务被当成全过（F-053）；若输出里确有 SBY DONE/engine status 痕迹，再改判 `make_failed_during_execution`，区分「没生成」与「跑到一半死掉」（F-056）。

崩溃是假失败，替零/空过是假通过——非对称性比故障频率更重要。Fmax 取最后一条布线后输出、3 seed 至少 2 个成功才计分等同源设计见 [07-fpga-fitness](/concepts/07-fpga-fitness.md)。

## 编排方自身也是故障源：heredoc 落主树事故

故障不只来自 agent 或环境，也来自编排方自己。gemini 破损槽 1 的一次 heredoc 重定向落到 orchestrator **主树**（bash 工具继承主树 cwd），alu.sv/ex_stage.sv 两个游离文件阻塞了 slot0 一个干净的 **+28.5%** 胜场合并；修复方式是合并前 `git checkout HEAD -- cores/<target>/` 清主树（F-037，[worktree.py L155-L174](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/worktree.py#L155-L174)）。隔离边界必须同时覆盖 agent 的 cwd 与 harness 自己的文件描述符；信任边界的整体设计见 [03-worktree-sandbox](/concepts/03-worktree-sandbox.md)。

## 预防设施

方法学与运维教训沉淀了一组事前防线（F-019、F-029、F-034）：

- **成本硬上限** $200/rep（`DEFAULT_MAX_COST_USD`），与实现代理 1800s、假设代理 1200s 的 watchdog 一起防止失控燃烧预算或挂死（F-019、F-029、F-028）；
- **parser burn-in**：机械式 prompt 解析共用一个加固 parser，每个 prompt-parsing agent 以 **N≥2 轮** burn-in，集成测试用真实 round-2 prompt 构造（F-034）；
- **独立运行环境**：每个克隆独立 `CODEX_HOME`（关闭记忆）、无 login shell、首 rep 实时监看 shell 命令（F-034）；
- formal 全机锁（`/tmp/auto-arch-tournament.formal.lock`）避免 `--parallel` rep 各自 `make -j` 把慢检查拖过 45 分钟超时（BENCH 可靠性节，作者报告）。

## 可重建性：从 git 状态复原 log.jsonl

长任务产物必须可由底层状态独立复原。runner 的做法（F-116）：

- **telemetry 重建**：每次 `append_log` 立即以 `log: <hyp-id> <outcome>` 提交，runner 遍历 `git log --all --reflog` 独立重建 log.jsonl，不依赖磁盘上那份文件（runner.py L146-L222）；
- **orphan fixture + tag 成对重建**：夹具以无父根提交与 tag 成对构造（build_fixture L124-L179），克隆后主动 `git tag -d`，防止同名 branch/tag 歧义让 checkout 静默回退 HEAD、孤儿化此前全部日志（F-116）；
- **random 种子按 100+rep**（runner.py L797），让对照变异可按 rep 逐粒复现（V1 的播种污染是反面教材，K-6）。

## 隔离强化：剥离成果与每 run 一个 OS 账号

为防训练泄漏与跨会话污染，runner 克隆时**剥离成果与研究目录、删 tag、造无父根根提交并 gc**（runner.py L267-L398，F-116）。V2 进一步把读权限从「按 CLI 不一」改为**每个并发 run 一个 OS 账号、隐藏程序对任何 CLI 都不可读**（F-124）；首 rep 监看、剥离成果等运维规则也由 scribe 沉淀进 lessons 体系（F-034，见 [12-scribe-lessons](/concepts/12-scribe-lessons.md)）。

## 遥测样本与证据边界

作者报告的 Opus rep1 遥测：**522,817,399 tokens in / 1,904,689 out**（覆盖全部代理，implementer 与 scribe transcript 均归档），api_equivalent 估算 **$123.62**、OAuth 实付 **$0.00**（F-126，[diary 2026-09-26 L46](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/research/diary/2026-09-26.md#L46)）。这解释了排行榜上 $0.00 的计费口径。

边界：本节所有事故链、时间戳、PID、commit hash 与 token 数都来自**作者运维日记**（research/diary/）与代码常量的静态取证，属于运维证据而非可复现实验；aborted1 之类的隔离产物本身不计入任何数据结论（F-115、F-126）。

## 相关概念

- [隔离与信任边界：git worktree、路径白名单与契约指纹](/concepts/03-worktree-sandbox.md)
- [经验积累：append-only LESSONS.md、scribe 角色与 lessons 消融](/concepts/12-scribe-lessons.md)
- [V1 排行榜：16 模型、失败模式谱与两个对照的崩溃](/concepts/14-v1-leaderboard.md)
- [HWE Bench 事实登记表 F-001~F-126](/references/facts.md)
