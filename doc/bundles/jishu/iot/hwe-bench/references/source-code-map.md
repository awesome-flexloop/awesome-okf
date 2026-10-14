---
okf_version: "0.2"
type: Reference
title: "HWE Bench 源码地图与信源固定（4a137bb）"
description: "固定提交 4a137bb 的 G0 信源固定记录、仓库模块地图、C01-C20 规模计数台账与官方阅读路径，束内一切源码引用的信源锚点"
tags: [HWE Bench, auto-arch-tournament, 源码地图, 信源固定, 模块索引, 计数台账, C系列]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-14T14:30:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-14T19:30:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-pinned-tree
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb 仓库树"
  - id: hwe-readme-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/README.md"
    title: "HWE Bench README，固定提交 4a137bb"
---

# 源码地图与信源固定

> G0 阶段先于一切读取完成。本包所有事实只来自本地镜像 `external/dao/auto-arch-tournament` 的一个固定提交；源码树全程只读，未运行任何 EDA/仿真。

## 1. G0 固定记录

| 项 | 值 |
|---|---|
| 仓库 | [FeSens/auto-arch-tournament](https://github.com/FeSens/auto-arch-tournament)（品牌名 **HWE Bench**，站点 hwebench.com） |
| 许可证 | Apache-2.0（[CITATION.cff](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CITATION.cff#L1-L39)） |
| 固定提交 | `4a137bb1378834ca3664a1c971684777eb5f364a` |
| 提交时间/主题 | 2026-10-05 19:24:11 +0200，"site: V2 results page (v2.html), V2 nav entry, and a notice on the V1 leaderboard that V2 supersedes its timer-based numbers" |
| 工作树状态 | clean（`git status --short` 无输出） |
| pinned 链接形式 | `https://github.com/FeSens/auto-arch-tournament/blob|tree/4a137bb1378834ca3664a1c971684777eb5f364a/<path>#Lxx-Lyy` |
| 论文题名 | "HWE Bench: An Unbounded Benchmark for LLM Hardware Development on RISC-V"（作者 Felipe Sens Bonetto，v1，2026-05-15） |

## 2. 仓库一句话地图

auto-arch-tournament 是一个**指向 SystemVerilog RV32IM CPU 的自主研究循环**：LLM coding agent 每轮提出微架构假设、在隔离 git worktree 内实现，依次通过 verilator lint→yosys 综合→程序构建→cosim 构建→RVFI 契约预检→riscv-formal 形式验证→Verilator/Python ISS 协同仿真→3 种子 FPGA 布局布线与 CoreMark 测量，只有 fitness **严格超过**现任冠军的候选才被合并（[README.md#L3-L13](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/README.md#L3-L13)）。

```text
auto-arch-tournament/
├── tools/                  # LLM 不可触碰的编排与评测代码（沙箱指纹覆盖）
│   ├── orchestrator.py     # 硬编码循环主体（838 行）
│   ├── tournament.py       # N 槽并行轮次、门顺序、winner 挑选（600 行）
│   ├── worktree.py         # git worktree 生命周期（194 行）
│   ├── sandbox.py          # 白名单 + 契约/EDA 指纹 + gitignore 清洗（340 行）
│   ├── accept_rule.py      # 严格接受 / 两阶段 Pareto（109 行）
│   ├── plot.py             # progress.png 绘图（143 行）
│   ├── agents/             # hypothesis/implement/scribe 三角色 + static/random 对照
│   ├── eval/               # formal/cosim/fpga/holdout/rvfi_lint 评测门
│   ├── bench/              # HWE Bench 批量 runner/report/fixture/模型花名册
│   └── site/               # GitHub Pages 静态站生成器
├── formal/                 # riscv-formal wrapper（nret=2 / nret=1 两套）+ 三份 checks cfg
├── fpga/                   # Gowin Tang Nano 20K 综合脚本、core_bench 顶层、约束
├── test/cosim/             # Verilator C++ 仿真器 + Python RV32IM ISS + 对拍器
├── schemas/                # hypothesis / eval_result 两份 JSON Schema
├── bench/                  # CoreMark 程序、holdout 五内核、16 模型组运行产物、排行榜
├── cores/                  # baseline / v1 / bench + ibex/neorv32/picorv32/vexriscv 参考核
├── research/               # 研究日记 5 篇、E1/E3 实验、lessons、评审与修订计划
├── docs/                   # 博客、bench-protocol-v1、bootstrap 记录、superpowers 设计
├── site/                   # hwebench.com 站点（index/v2/models/data/methodology）
├── CLAUDE.md               # 10 条硬不变量 + don't-touch 清单（164 行）
├── BENCH_METHODOLOGY.md    # HWE Bench V1 预注册方法学（251 行）
├── Makefile / setup.sh     # macOS 工具链自举（.toolchain/）
└── .design/branding/       # HWE Bench 品牌战略（BRIEF/IDENTITY/STYLE）
```

## 3. 模块地图（行号为 pinned 提交实测）

### 3.1 编排层

| 文件 | 行数 | 职责 |
|---|---|---|
| [tools/orchestrator.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/orchestrator.py#L1-L2) | 838 | 文件头逐字 `"""Hardcoded AutoResearch loop. The LLM never touches this file."""`；fork-on-create、baseline retest、emit_verilog 四步、append_log+scribe、reaper 安装、main() L710-L838 |
| [tools/tournament.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/tournament.py#L268-L405) | 600 | 单 slot 全链路 L268-L419；ThreadPool fan-out 与串行收束 L513-L594；类别轮转 L56-L71；ID 预分配 L74-L93；pick_winner L96-L135；phase_gate 信号量 L138-L211 |
| [tools/worktree.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/worktree.py#L13-L22) | 194 | worktree 根/分支命名 L13-L41；创建（prune+删分支+add）L62-L82；pyc assume-unchanged 与 riscv-formal symlink L84-L113；accept L133-L182；容错 destroy L184-L194 |
| [tools/sandbox.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/sandbox.py#L45-L66) | 340 | CONTRACT_PATHS L45-L66；EVAL_TOOLS 指纹 L71-L79；gitignore 清洗 L81-L126；SHA-256 指纹 L217-L228；riscv-formal 指纹 L246-L285；eval 副本切换 L316-L334 |
| [tools/accept_rule.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/accept_rule.py#L84-L86) | 109 | 无 target 严格 `>` L84-L86；饱和缺口 L12-L41；两阶段 Pareto L56-L66、L88-L108 |
| [tools/plot.py](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/tools/plot.py#L11-L15) | 143 | improvement/regression/broken 三色、LUT4 归一化点面积、VexRiscv 370 参考线 |

### 3.2 agent 角色层（tools/agents/）

| 文件 | 行数 | 职责 |
|---|---|---|
| _runtime.py | 494 | provider 合法集 codex/claude/opencode/static/random；三种 CLI 命令拼装 L265-L362；streaming 执行+watchdog L448-L494 |
| hypothesis.py | 567 | 假设生成、白名单回滚、1200s 超时、YAML 容错规范化 L345-L405、失败重试一次 L480-L499 |
| implement.py | 225 | 唯一可写 rtl/ 与 test/test_*.py；`CLAUDE_TIMEOUT_SEC=600*3`=1800s（L11 注释误写 "10 min"） |
| scribe.py | 231 | 仅可写 LESSONS.md 且 append-only L133-L231；240s 超时 |
| static_agent.py | 152 | 无 LLM 空操作对照（桩 YAML "static-control-noop"，不改 RTL） |
| random_agent.py | 290 | 随机变异对照：op_swap/ternary_swap/lit_perturb，确定性种子，MAX_DRAWS=20 |
| _hyp_parse.py | 41 | marker rfind + 正则 `\bhyp-\d{8}-\d{3}-r\d+s\d+\b` 解析 ID |

### 3.3 评测层（tools/eval/）

| 文件 | 行数 | 职责 |
|---|---|---|
| formal.py | 246 | nret 路由 L20-L85；EXPECTED_MIN_CHECKS=50 L38-L62；工作目录 PID 回收 L88-L131；45 分钟超时 L163-L195；no_checks 再分类 L199-L229 |
| cosim.py | 179 | 普通 ELF 全 RVFI trace 对拍 + coremark.elf CRC 门两段短路 L140-L171；CoreMark sim timeout 600s |
| fpga.py | 311 | SEEDS=[1,2,3] L30；五 CRC 常量 L33-L44；stall flags L45-L56；CoreMark JSON 判定 L106-L176；CRC UART 校验 L182-L207；3 seed 合成 L246-L303 |
| holdout.py | 255 | E3 五内核留存基准；HOLDOUT_KERNELS L31；geomean 仅对 validated 核 L222-L250 |
| rvfi_lint.py | 67 | ch0 不得被裸常量 tie 死的毫秒级预检 L19-L67 |
| _subprocess.py | 104 | start_new_session+psutil 递归杀 L22-L77；SIGTERM 树收割 reaper L80-L104 |

### 3.4 Bench 层（tools/bench/，20 个 .py=10 模块+10 测试）

| 模块 | 行数 | 关键点 |
|---|---|---|
| runner.py | 1278 | CLI 默认 reps=3/n=15/k=3/max-cost=200 L1137-L1149；provenance L231-L244；clone 剥离+删 tag+无父根提交+gc L267-L398；random 种子 100+rep L797；repo.bundle L1085-L1093 |
| report.py | 635 | 总体 pstdev L143-L145；纯 Python Wilcoxon（n<5 不报 p）L235-L282；配对 L285-L319；CSV 18 列 L572-L580 |
| build_fixture.py | 190 | orphan fixture 提交与 tag 成对重建 L124-L179 |
| telemetry.py | 421 | 从 git 全引用+reflog 重建 log.jsonl L146-L222 |
| transfer.py | — | E3：从 bundle 克隆 champion + 主仓注入 holdout 打分 |
| gc.py / preflight.py / croissant.py / transcript.py | — | 垃圾回收/飞行前检查/数据格式/会话记录 |

### 3.5 硬件契约与程序

- `formal/`：[wrapper.sv](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/formal/wrapper.sv#L55-L100)（102 行，NRET=2 双通道路由切片）、wrapper_si.sv（72 行，单发射整宽连接）、checks.cfg（67 行，ALTOPS）、checks_si.cfg（40 行，nret=1）、checks-deep.cfg（66 行，nret=1 无 ALTOPS）、run_all.sh（220 行，PREUNSAT-as-pass 计数 L176-L203）。
- `fpga/`：core_bench.sv（150 行，LFSR 指令流+反常量折叠+XOR 防 DCE）、core_bench_si.sv（93 行）、scripts/synth.tcl（44 行，synth_gowin）、scripts/nextpnr_run.sh（31 行，GW2A-LV18QN88C8/I7）、constraints/Tang_Nano_20K.cst（4 行）。
- `test/cosim/`：main.cpp（285 行，xorshift7 约 22% 停顿、OOB、MMIO 计时括号、JSON 退休流）、reference.py（318 行，RV32IM ISS，9 类陷阱纪律）、run_cosim.py（112 行，15 字段对拍+ALIGNED_MEM 归一）、build.sh（60 行，-DNRET 宏）。
- `bench/programs/`：Makefile（44 行，COREMARK_SIZE=2000/-O3）、coremark/baremetal/core_portme.{c,h}、crt0.S（9 行）、link.ld（11 行）、selftest.S（157 行）。
- `schemas/`：hypothesis.schema.json 与 eval_result.schema.json（各 35/33 行）。

### 3.6 cores/ 七个核目录

| 核 | 性质 | RTL 规模 |
|---|---|---|
| baseline | 通用种子核，5 级按序 RV32IM、前递/冒险、无预测无 cache | rtl/ 13 个 .sv（12 module + core_pkg） |
| v1 | 历史自主进化冠军核（73 假设运行产物） | rtl/ 16 个 .sv（新增 div_unit/store_slot/00_core_pkg_first） |
| bench | 冻结基准夹具核（bench-fixture-v1），nret:1 | 13 个 .sv，与 baseline 仅 core.sv 不同（12 文件哈希一致） |
| ibex | lowRISC vendored（eede2fb…，Apache-2.0），synth_only | 30 .sv + ibex_core.f |
| neorv32 | stnolting vendored（a0c202…，BSD-3），VHDL | 56 .vhd（需 ghdl 插件） |
| picorv32 | YosysHQ vendored（87c89a…，ISC） | 1 个 picorv32.v |
| vexriscv | SpinalHDL vendored（680756…，MIT），citation_only | rtl/demo_scala 39 个 + demo_scala/smp 4 个 = 全树 43 个 .scala 文档（V 阶段勘误：E 台账仅计顶层 39，漏 smp/ 子目录 4 个），无预生成 Verilog |

## 4. 计数台账（C 系列）

> 全部由 R 阶段子代理用 git/Shell/PowerShell/Python json 机械计数，非人工目测。

| 编号 | 计数 | 口径与取证 |
|---|---|---|
| C01 | tools/orchestrator.py 838 行、tournament.py 600、worktree.py 194、sandbox.py 340、accept_rule.py 109、plot.py 143 | PowerShell ReadAllLines |
| C02 | tools/agents 12 个 .py（3 角色 567/225/231 + 2 对照 152/290 + runtime 494 + parse 41 + 2 个 __init__） | 同上 |
| C03 | tools/eval 15 个 .py（6 模块 246/179/311/255/67/104 + 7 测试 + __init__ 等） | 同上 |
| C04 | tools/bench 20 个 .py（10 模块+10 测试）；tools/site 8 个 .py | 同上 |
| C05 | 模型花名册 16 个 models*.yaml/lite.yaml，共 39+1 个模型条目 | 逐文件枚举 |
| C06 | bench/ 下 16 个模型目录（另 holdout/programs 为数据目录）、41 个 repN 目录 + 2 个非 repN 运行目录（V 阶段勘误：E 稿只报 repN 数，未交代另两个）——claude-opus-5_5_xhigh/aborted1-formal-reaper 有 agent.log/run_summary.json/log.jsonl 而无 summary.json，gpt-6-astra_max/startup-attempt1 有 agent.log/summary.json 而无 run_summary.json/log.jsonl；故 summary/run_summary/log.jsonl 各 42 份、agent.log 43 份；repo.bundle 0 份 | 目录清点 |
| C07 | bench/results.jsonl 41 行 = 37 done + 4 failed；37 行公共 27 字段（V 阶段勘误：E 台账"27 字段"为公共口径，键并集实为 34——L38/L39 另带 quota_pause_sec/resumed_at 2 键，L40/L41 另带 fixture_commit/fixture_ref/runner_commit/runner_dirty 4 个 provenance 键，L41 再带 api_equivalent_cost_usd）；仅末两行（L40/L41）有 provenance | Python json 解析 |
| C08 | bench/leaderboard.csv 17 行（表头+16 模型） | 行数计数 |
| C09 | bench/holdout 22 个文件（5 内核+support+Makefile+v0_expected.json+VENDOR.md） | 目录清点 |
| C10 | cores/v1/experiments/log.jsonl 74 行、603,222 字节；73 个真假设+1 行基线哨兵 | Python json 全量解析 |
| C11 | 73 假设结果分布：improvement 9、regression 51、broken 9、placement_failed 4（不含基线行） | 同上 |
| C12 | 73 假设类别：structural 25、micro_opt 24、predictor 24（v1 运行未用 memory/extension） | 同上 |
| C13 | baseline/bench rtl 各 13 个 .sv；v1 rtl 16 个 .sv | Get-ChildItem |
| C14 | research/diary 5 篇（2026-07-15、07-16、09-23、09-25、09-26）；research/runs 5 个 EXP 目录 | 目录清点 |
| C15 | formal checks 三口径并存：formal.py docstring "53 total against the V0 baseline"；run_all.sh "95+ checks"；README "~105 checks at NRET=2" | 三处行号见 F-057 |
| C16 | site/ 5 个 html（index/v2/models/data/methodology）+ CNAME=hwebench.com + css 4 个 | 目录清点 |
| C17 | v1 十连胜（含基线哨兵 10 条 improvement 行）：真实架构胜场 9 个，九胜场逐条明细（槽位/标题/fitness/增幅/日志行）见 F-100；log.jsonl 不记录实现提交 hash，hash 仅能经 git log --all 与日志时间戳/标题对拍复原 | git log --all 与日志行对拍 |
| C18 | V2 页数据：6 agent 系统×6 runs=36 scored runs；12 个 Holm 附加对中 9 对分离 | v2.html 静态文本 |
| C19 | V1 random 对照 3 rep×45=135 假设全部首败 formal（旧口径，V2 披露播种有 bug） | LEADERBOARD L28 + v2.html L364-L365 |
| C20 | setup.sh 仅 macOS（非 Darwin 退出）；.toolchain 自装 verilator/OSS CAD Suite(~1GB)/xPack riscv gcc | setup.sh L1-L20 |

## 5. 建议阅读路径

1. 先读 [README.md](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/README.md#L1-L47) 与 [CLAUDE.md](https://github.com/FeSens/auto-arch-tournament/blob/4a137bb1378834ca3664a1c971684777eb5f364a/CLAUDE.md#L9-L21) 建立循环与硬不变量全景；
2. 跟本束概念 00→03 理解"假设-实现-评测-接受"一轮；
3. 概念 04→08 走一遍验证器（形式→协同→FPGA→CoreMark）；
4. 概念 10→11 读 CPU 本身与 73 假设进化史；
5. 概念 13→15 进入基准方法学与 V1/V2 数据；
6. 要溯源任何数字时回到 [事实登记表](facts.md) 的 F 编号。
