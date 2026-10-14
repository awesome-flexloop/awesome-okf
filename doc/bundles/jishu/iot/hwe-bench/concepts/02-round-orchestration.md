---
okf_version: "0.2"
type: Concept
title: "一轮编排：N 槽锦标赛、四个角色与门的短路顺序"
description: "一轮编排是 K 槽锦标赛：角色并行扇出跑七门、协调线程串行收束，严格大于冠军才 ff-only 合并；N/K 旋钮存在三套口径"
tags: [HWE Bench, 轮次编排, 锦标赛, 角色分工]
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

## 硬编码编排："The LLM never touches this file"

orchestrator.py 共 838 行，文件头逐字是 `"""Hardcoded AutoResearch loop. The LLM never touches this file."""`（F-011）。循环编排代码对 LLM 不可触碰，这是「模型不能给自己改考官」原则的第一行；运行时再由路径沙箱把它强制执行（见[概念 03](/concepts/03-worktree-sandbox.md)）。

## 一轮三步

README 对一轮的对外说明是三步（F-018）：

1. 每个槽各自生成假设、完成实现并跑完全部门；
2. 只有 fitness **严格高于**现任冠军的槽才进入候选；
3. 候选中最高 fitness 的槽合并入主干，commit message 由假设 ID 关联（F-018）。

单槽全链路实现在 tournament.py L268-L419（F-014，亲验）：Phase 1 假设生成 → Phase 1b schema 校验 → Phase 2 建 worktree 与实现 → 沙箱与契约检查 → Phase 3 lint/synth/build → Phase 3.5 RVFI 毫秒级预检 → Phase 4 formal → Phase 5 cosim → Phase 6 FPGA，评测结束后还做一次契约复查（F-014）。建 worktree、ff-only 合并与销毁的细节见[概念 03](/concepts/03-worktree-sandbox.md)。

## K 槽并行：ThreadPool 扇出，协调线程串行收束

一轮的并行结构是典型的「扇出-收束」（F-014，亲验）：

```text
  编排器主线程（收束后唯一改主仓 git 状态的线程）
   |
   +-- ThreadPool(max_workers=K) -- slot 0: 假设 -> 实现 -> 门 1..7
   |                              |- slot 1: 假设 -> 实现 -> 门 1..7
   |                              |- slot 2: 假设 -> 实现 -> 门 1..7
   |
   |  as_completed 实时收结果；按 slot 排序稳定日志顺序
   v
  pick_winner（委托 accept_rule：严格 > 冠军；tie-break = fitness, -lut4, -slot）
   v
  串行收束：winner -> ff-only 合并；其余候选 -> destroy worktree；逐行 append_log
```

fan-out 与收束位于 [tournament.py L513-L594](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/tournament.py#L513-L594)：线程池提交 K 个 `run_slot`，收束段注释明确声明协调线程是此后唯一改动主仓 git 状态的线程（L563-L564 亲验）。三个配套机制同样在该文件（F-014，均亲验）：

- **类别轮转**：槽号对五类取模，确定性地保持一轮内的想法多样性（L56-L71）；
- **ID 预分配**：一轮的 `hyp-YYYYMMDD-NNN-rRsS` 在开跑前发完，修并发抢号（L74-L93，与[概念 01](/concepts/01-hypothesis-schema.md)的 ID 账本呼应）；
- **phase_gate 信号量**：formal 与 fpga 两门容量各为 1，formal 另加整机 fcntl 锁，避免并发 SMT 任务互相抢占 CPU、把慢任务推过 formal 门超时（L138-L211）。

## 四个执行角色与两个无 LLM 对照

- **hypothesis 角色**（567 行）：产出 YAML、白名单回滚、1200s 超时、失败重试一次（F-028，细节见[概念 01](/concepts/01-hypothesis-schema.md)）；
- **implement 角色**（225 行）：唯一可写 `rtl/` 与 `test/test_*.py` 的角色，`CLAUDE_TIMEOUT_SEC = 600*3` 即 1800s（F-029；K-5 记录同行注释误写 "10 min watchdog"）；
- **scribe 角色**（231 行）：只能 append-only 写 LESSONS.md，240s 超时，经验只追加不改写历史（F-030，深度见[概念 12](/concepts/12-scribe-lessons.md)）；
- **static 对照**（152 行）：无 LLM 的空操作桩，YAML id 为 `static-control-noop`，不改 RTL（F-031）；
- **random 对照**（290 行）：op_swap / ternary_swap / lit_perturb 三类随机单行变异，确定性种子，MAX_DRAWS=20（F-032）。

runtime 的 provider 合法集为 codex/claude/opencode/static/random（F-033）。所以「四个角色」更准确地说是三个 LLM 角色加两个对照桩，硬编码编排器本身不在角色之列。

## 七门顺序与短路

七门顺序固定：verilator lint→yosys 综合→bench make→cosim build→riscv-formal→Verilator/Python ISS cosim→3-seed FPGA 加 CoreMark；第一步失败即短路，结局写成 `broken: <step>`（F-001）。formal 与 fpga 两门另受上节 phase_gate 的容量约束。各门内部机制见概念 04-07。

## 三结果类

方法学把一轮产物分为三类（F-082）：**improvement**（fitness 严格超冠军，合并）、**regression**（门全过但 fitness 不高于冠军，丢弃 worktree）、**broken**（某门失败）。运行日志中还可见第四种工程态 `placement_failed`：3 个种子中布局成功者不足 2 即不给分，v1 的 4 例全部是 structural 类存储结构尝试（F-099、F-103）。接受规则与平局处理的完整口径见[概念 09](/concepts/09-accept-rule-outcomes.md)。

## 旋钮口径：N/K 的三套场景

同一对旋钮 N（轮数）/K（槽数）存在三套默认值，勘误台账 K-3 裁决如下：

- **orchestrator CLI**：`--iterations` 默认 1、`--tournament-size` 默认 3；另有 `--from-hypothesis` 可跳过 LLM 假设步（F-012）；
- **Makefile 交互 loop**：`N ?= 10`、`K ?= 1`，K=1 即顺序执行（F-013；[Makefile L27-L28](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/Makefile#L27-L28) 亲验）；
- **bench 基准**：runner CLI 默认 `--n 15 --k 3`（F-020），预注册规模为 N=15×K=3=45 候选/rep（F-081）；方法学示例命令两处写 `--n 10` 属文档笔误（K-3）。

Makefile 的 N/K 是交互式 `make loop` 的旋钮，不是基准配置；两者不可混用（K-3）。基准场景的完整方法学见[概念 13](/concepts/13-v1-bench-methodology.md)。

## 相关概念

- [假设即数据：JSON Schema、五类 hypothesis 与 ID 账本](/concepts/01-hypothesis-schema.md)
- [隔离与信任边界：git worktree、路径白名单与契约指纹](/concepts/03-worktree-sandbox.md)
- [接受规则：严格大于、三结果类与搜索的单调形状](/concepts/09-accept-rule-outcomes.md)
- [V1 基准方法学：预注册配置、45 候选/rep 与统计口径](/concepts/13-v1-bench-methodology.md)
