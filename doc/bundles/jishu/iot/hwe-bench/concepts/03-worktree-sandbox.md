---
okf_version: "0.2"
type: Concept
title: "隔离与信任边界：git worktree、路径白名单与契约指纹"
description: "信任边界由两层 worktree、CONTRACT_PATHS 白名单与契约/EDA 双指纹构成：agent 只能改 RTL，评测前拦篡改，但不防测量契约漏洞"
tags: [HWE Bench, worktree, 路径沙箱, 契约指纹]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T16:00:00+08:00"
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

## 可写面：两个前缀加一个不变量

agent 的可写面极小且显式：只有 `cores/<TARGET>/rtl/**`（可新增、删除、改名、从零重写任何 SystemVerilog）与 `cores/<TARGET>/test/test_*.py`（cocotb 测试）；顶层唯一不变量是 core.sv 的 I/O 契约——clock/reset、imem/dmem 与 NRET=2 RVFI（F-021）。触碰 `formal/`、`tools/`、`fpga/`、`test/cosim/main.cpp`、CRC 表或任何兄弟核目录，会在**任何评测运行之前**被路径沙箱拒绝。原话是："The agent doesn't get to soften its own grader."（F-022）

## 两层 worktree：外层 loop 隔离，内层按槽隔离

隔离分两层，初读代码时容易混为一层：

```text
  make loop               .worktrees/<TARGET>/            分支 core-<TARGET>
  （自举 re-exec，防多个 TARGET 并行时撞 git index）
        |
  每槽 create_worktree    cores/<TARGET>/worktrees/       分支 <TARGET>-<hyp-id>
                          <hyp-id>/
```

外层由 Makefile 创建：`.worktrees/<TARGET>/` 位于分支 `core-<TARGET>`，make 在其中 re-exec 自身，使两个针对不同 TARGET 的 `make loop` 互不踩 git index（F-013；[Makefile L151-L170](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/Makefile#L151-L170) 亲验）。槽内 worktree 由 worktree.py（194 行）管理：根目录是 `cores/<target>/worktrees/<hypothesis_id>`，分支带 target 前缀 `<target>-<hypothesis_id>`，以防两个 TARGET 并跑时同名假设分支在共享 git refs 上相撞（F-035，[worktree.py L13-L41](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/worktree.py#L13-L41)）。

槽内生命周期如下（F-035/F-036，均亲验）：创建时先 `git worktree prune`、`git branch -D` 旧分支再 `worktree add`，扛住上一轮崩溃留下的残 ref（[L62-L82](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/worktree.py#L62-L82)）；对夹具分支遗留的已跟踪 `.pyc` 做 `update-index --assume-unchanged`，防止 Python 重写字节码被沙箱误报越权（L96-L105）；共享的 formal/riscv-formal 以 symlink 挂入，免去每轮重复克隆整个形式框架（L107-L112，F-036）。

接受路径同样严格收窄（L116-L153 亲验）：提交时暂存范围精确限定为 `cores/<target>/` 前缀与 `test/test_*.py` glob，`git add -A` 只在该前缀内生效，提交用 `--allow-empty`；随后清主树、checkout 目标分支、`git merge --ff-only`（只准快进），最后 destroy worktree（F-038，L155-L182）。destroy 本身容错，remove/branch -D/rmtree 全部 check=False 或 ignore_errors，失败不抛死（[L184-L194](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/worktree.py#L184-L194)）。

## heredoc 泄漏事故：故障也来自编排方自己

worktree.py 的注释留存了一次实测泄漏（F-037）：gemini 的破损槽 1 用 heredoc 重定向写 RTL，但 agent 的 bash 工具继承编排器主树的 cwd，`alu.sv`/`ex_stage.sv` 因此落进主树而非槽 worktree；主树脏文件使随后的 ff-only 合并因 "local changes would be overwritten" 失败，同轮槽 0 一个干净的 **+28.5%** 胜场被连带阻塞。修复是在合并前对主树执行 `git checkout HEAD -- cores/<target>/`——契约是「编排器主检出里永远不该有脏的 cores/<target>/，有即是泄漏」（F-037，[worktree.py L155-L174](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/worktree.py#L155-L174)）。

## 沙箱三件套：白名单、双指纹、清洗与 eval 副本

**白名单**：sandbox.py（340 行）的 CONTRACT_PATHS 列出 tools/、schemas/、formal 六件、bench/programs、bench/holdout、fpga/、test/cosim 与 CLAUDE.md/ARCHITECTURE.md/README.md/setup.sh/Makefile（F-039，L45-L66 亲验）；EVAL_TOOLS 另列 yosys、nextpnr-himbaechel、verilator、sby、yosys-smtbmc、bitwuzla、riscv32-unknown-elf-gcc 七个评测必经的外部二进制（L71-L79 亲验）。

**双指纹**：agent 运行前对主树契约文件、共享 riscv-formal 检出与 PATH 上的 EDA 工具取快照，评测结束后再取一次比对（F-040；取快照点与评测后复查分别在 [tournament.py L327-L334](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/tournament.py#L327-L334) 与 [L407-L415](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/tournament.py#L407-L415)，亲验）。指纹口径在代码里分层：契约文件按内容算 SHA-256（[sandbox.py L217-L243](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/sandbox.py#L217-L243)），riscv-formal 记 HEAD 加脏路径哈希（L246-L285），EDA 二进制记解析路径加 size/mtime 而非全量哈希（L288-L301，亲验）。任何不一致一律判 `broken: sandbox_violation`（F-041）。

**清洗与 eval 副本**：worktree 内 gitignored 文件在构建前全删，评测只消费它自己产出的工件，防止预埋的更新 coremark.elf 之类被构建捡到（F-040，清洗逻辑见 sandbox.py L81-L126，F-041）；agent 跑完之后、formal 开跑之前，worktree 的 riscv-formal symlink 被切到 harness 专用副本，与 agent 自检用的检出物理隔离（[sandbox.py L316-L334](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/sandbox.py#L316-L334)，亲验）。

## CLAUDE.md：10 条不可削弱的不变量

CLAUDE.md 是一份 164 行的「不可削弱不变量 + don't-touch」清单（F-042）。开篇即要求 "Do not weaken these checks to make a hypothesis pass."：10 条硬不变量每条都在表格右栏注明由哪个检查强制，且每条都来自上一代 Chisel 实现的真实 bug（F-042，L1-L21 亲验）。举三例（亲验）：

- 不变量 #1：NRET=2 双通道退休纪律（ch0 承载较老指令、ch1 端口必须全驱动无 X/Z），由 cocotb smoke 与 formal wrapper 强制（L11）；
- 不变量 #6：访存限定 `[0x0, 0x100000)` 加 UART/markers 窗口，越界即 `oob:true` 判失败（L17）；
- 不变量 #7：CoreMark 五 CRC 必须等于 canonical 2K 配置常量，真值源是 fpga.py 的 `COREMARK_EXPECTED`（L18）。

don't-touch 清单覆盖 tools/、schemas/、formal 六件、formal/riscv-formal/、bench/programs/、bench/holdout/、fpga 契约件、test/cosim 三契约及 CLAUDE.md/ARCHITECTURE.md/README.md/setup.sh/Makefile（F-043，L23-L45 亲验）；清单末尾说明强制执行点就在 tournament.run_slot 与 sandbox.py 的指纹机制（F-040）。

## 实测三次越权：全部在评测前拒绝

v1 运行中沙箱抓到三次真实越权：r4s0、r9s0、r24s0 三个槽都试图新增白名单之外的 `test/_helpers.py`，全部在任何评测运行之前被拒绝，计入 9 个 broken（F-044，log.jsonl L11/L26/L71）。失败实例见 [/examples/02-failure-gallery.md](/examples/02-failure-gallery.md)。

## 边界：防文件篡改，不防测量契约漏洞

沙箱回答的问题是「agent 有没有改考题」：契约文件、formal 检出、EDA 二进制都在指纹内，且整套机制 fail-closed——任何不一致一律判 `broken: sandbox_violation`（F-041），可疑候选不会被放行。它不回答「测量夹具本身有没有契约漏洞」。作者在研究日记中报告了一例后者：core_bench 把 imem/dmem Ready tie 成 1'b1，使「只在 ready 为低时作用」的停顿逻辑被常量折叠出时序网表——周期收益计入、面积时序成本为零（r9s1，fitness 695.16，作者报告，F-079）。这类缺口不在路径沙箱覆盖面内，属于 FPGA 测量契约与接受规则的边界（见[概念 07](/concepts/07-fpga-fitness.md)与[概念 16](/concepts/16-harness-reliability.md)）。

## 相关概念

- [假设即数据：JSON Schema、五类 hypothesis 与 ID 账本](/concepts/01-hypothesis-schema.md)
- [一轮编排：N 槽锦标赛、四个角色与门的短路顺序](/concepts/02-round-orchestration.md)
- [FPGA 门：3-seed 中位数、fitness 公式与反常量折叠夹具](/concepts/07-fpga-fitness.md)
- [harness 可靠性：故障方向、遥测与沙箱事故复盘](/concepts/16-harness-reliability.md)
