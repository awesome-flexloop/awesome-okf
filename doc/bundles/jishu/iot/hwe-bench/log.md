# 生成日志（Log）

> 本日志记录 HWE Bench（auto-arch-tournament）源码教程束的生成过程、计数台账与勘误决策，供后续维护者审计复核。方法论链路：**source-code-to-okf-wiki（G0 信源固定 → R → I → E → V → C）**，Spec Mode 规格在 `.trae/specs/hwe-bench-okf-wiki/`（spec.md/tasks.md 已批准）。CMD-LOG session：`sc-20261014-auto-arch-tournament`。

## 2026-10-14：初始版本（G0 → R → I → E，V/C 待回填）

### G0：信源固定（先于一切读取）

- **对象**：本地镜像 `external/dao/auto-arch-tournament`（remote github.com/FeSens/auto-arch-tournament，Apache-2.0；vendored formal/riscv-formal 为 ISC）。
- **固定提交**：`4a137bb1378834ca3664a1c971684777eb5f364a`（2026-10-05 19:24:11 +0200，"site: V2 results page (v2.html), V2 nav entry, and a notice on the V1 leaderboard that V2 supersedes its timer-based numbers"），工作树 clean。
- **纪律**：源码树只读——不改不推不跑构建；pinned 链接统一 `https://github.com/FeSens/auto-arch-tournament/blob|tree/4a137bb.../`（40 字符）。
- **环境限制**：verilator/sby/bitwuzla/nextpnr 在 Windows 本机不可用（部分路径依赖 fcntl）；EDA/仿真/位流按 blocked 记录，性能数字一律「作者报告」。
- **分组裁决**：入 `jishu/iot/`，与 opentpu 并列「开源源码精读」硬件双束；束名 hwe-bench（品牌 hwebench.com）。

### R 阶段：事实采集

- **全树走读**：README、CLAUDE.md（10 不变量）、BENCH_METHODOLOGY.md、Makefile、tools/（orchestrator/tournament/worktree/sandbox/accept_rule/agents/eval/bench/site）、formal/（checks.cfg 三配置、run_all.sh）、test/cosim/ 三件套、fpga/（core_bench 夹具、synth/nextpnr 脚本）、bench/（programs/holdout/reference-cores/LEADERBOARD/results.jsonl）、cores/（baseline/bench/v1 + v1 experiments/log.jsonl）、site/v2.html、research/（lessons、diary 5 篇、E3 prereg、review_log）、.design/branding。
- **C01-C20 计数台账**：以 source-code-map.md 为准（orchestrator 838 行、runner 1278 行、tournament 600、sandbox 340、log.jsonl 74 行/603,222 字节、LEADERBOARD 16 模型行、results.jsonl 41 行等）。
- **关键机械复算**：log.jsonl 用 Python json 全量解析两次独立复算——73 假设结局 9 improvement/51 regression/9 broken/4 placement_failed；类别 structural 25/micro_opt 24/predictor 24；9 真实胜场（不含 L1 基线哨兵）与最差回归 r24s2 −73.25% 均由脚本得出，不采信博客叙述表。
- **事实登记**：F-001~F-126 共 126 条，十组 A-J（10/12/12/10/13/9/13/12/15/20），编号先于概念页冻结。

### I 阶段：洞察冻结（先于正文）

6 个四元组洞察（references/insights.md，陈述/证据/反常识/行动，每条证据 ≥3 个 F）：I-1 验证器才是沉淀工件；I-2 接受规则塑造搜索空间形状；I-3 防作弊是基准工程本体；I-4 formal 分层声明与空过分类；I-5 测量口径即结论对象；I-6 harness 故障方向非对称（只许假失败）。纪律：E 阶段只消费洞察不新造。

### E 阶段：信源先行 + 五批并行生成

| 批次 | 时间（+08:00） | 文件 |
|------|---------------|------|
| E-0 | 15:00-15:40 | references：source-code-map（R 期先行）→ facts → insights → verification 骨架（V 期回填）→ references/index |
| E-1 | 16:00 | concepts 00-03 |
| E-2 | 16:20 | concepts 04-07 |
| E-3 | 16:40 | concepts 08-12 |
| E-4 | 17:00 | concepts 13-16 |
| E-5 | 17:40 | examples 00-02 |
| 收尾 | 18:00 | 4 个 index + 本日志 |

共 29 个 Markdown：17 concepts + 3 examples + 5 references（含 index）+ 3 个子目录 index + 根 index + log。三个子目录 index **无 frontmatter**（表格 + hidden toctree，与 opentpu 束形态一致）。

### E 阶段勘误与复核记录

1. **K-1~K-6 口径台账**（facts.md 独立勘误段，AC-2）：V1/V2 不可比；博客 10/50 vs 日志 9/51（基线哨兵归属）；N/K 三套口径（Makefile 10/1、bench 预注册 15/3、示例命令 --n 10）；formal 检查数 53/95+/~105 三口径；文档漂移四处（fpga.py:247 引位、help $30、"10 min" 注释、--n 10）；random 135 播种污染（3 draws×45 → V2 135 独立抽取）。
2. **F-097 字段数勘误**：初稿误记「每行 23 字段」；Python 解析实测键集异构——并集 26 字段，60 个全门行 25（缺 skip_implementation）、L1 哨兵 22、8 个 cosim/沙箱 broken 行 13、4 placement 行 14、r6s2 schema 行 10。facts.md 与 concept 11 已同步改写并留痕。
3. **F-039 指纹精度勘误**：E 期子代理亲验 sandbox.py L288-L301——EVAL_TOOLS 指纹是 PATH 解析路径+size+mtime_ns，**不是 SHA-256**；SHA-256 仅用于契约文件（L217-L243）与 riscv-formal 脏路径（L246-L285）。facts.md 已收紧措辞。
4. **F-126 锚点拆分**：seatbelt EPERM 事故在 research/diary/2026-09-25.md L72-L88，遥测 $123.62/522,817,399 在 2026-09-26.md L46；初稿两锚点混挂，已校正为双锚点。
5. **两个易混基线**（concept 10 重点防混）：v1 log L1 历史基线 301.04/135.21/9880/ff 1858（2026-04-28）；baseline/core.yaml current 282.82/127.03/9563/ff 1866（2026-07-16 retest）；V1 排行榜对照 282.8 为后者。

### E 阶段机械检查（收尾时）

- 全束文件清单 29 个齐备；17 concept 行数 75-99、3 example 行数 114-157，均在区间；4 批执笔子代理各自跑过 H1/禁用链接/hash 长度/frontmatter 机械 QA。
- 子代理新增 pinned 锚点（tournament/worktree/sandbox/cosim/fpga/holdout/scribe/rtl 文件名等细粒度行段）均经本地镜像逐行亲验；rtl 文件集合经 LS + Get-FileHash 比对（bench 与 baseline 12 文件哈希一致仅 core.sv 不同）。
- frontmatter verified.at 在 E 阶段统一占位，V 阶段以精确时间戳批量回填（见上节）。

### V 阶段：独立验证（2026-10-14 19:30 +08:00 回填）

- **执行**：fresh-context 独立子代理（非 R/E 作者），自写枚举器/解析脚本独立复算；镜像 HEAD 复确 4a137bb、工作树 clean。详见 [verification.md](references/verification.md)。
- **G1**：29 文件结构/toctree 全通过；修复 P1×1（source-code-map.md 补 frontmatter）、P3×3 文件（examples 三篇尾部双 H2 合并）。
- **G2**：concepts+examples 191 条 pinned 链接 100% 机械通过（文件存在+40 字符 pin+锚点不越界），正文反引号符号 85 条（const 43/cli 26/hex 16）全仓回扫 0 虚构，14 组高风险数值全部命中；P0=0。修复 P3×1（concept 06 的 0x10000200 窗口补 CLAUDE.md L17 锚点）。
- **G3**：C01-C20 全量独立复算一致；F-001~F-126 无缺号、I-1~I-6 每条证据 5/5/8/5/7/5 个 F、K-1~K-6 齐；log.jsonl 74 行字段并集 26（60×25、L1=22、8×13、4×14、1×10）、9 真胜（首 r1s2 L4、末 r20s2 L61 577.76/+9.15）、最差回归 r24s2 L73 −73.25。修复 P2×2（C06 补两个非 repN 运行目录成因；F-115/C07 results.jsonl 字段口径收紧为公共 27/并集 34 异构）、P3×1（vexriscv .scala 39→43，补 smp/ 4 个）；C05「39+1」中 +1 无上游出处，记为残余措辞观察项。
- **G4**：独立链接枚举器（剔除围栏）扫全束 600 条 Markdown 链接——353 pinned blob+9 pinned tree 全通过（0 越界/0 错 hash），236 条束内链接（169 `/`-根、39 bare、3 `../`、25 根表相对）全可达，2 条仓库根 URL 合法；0 file:///、0 external/dao 真实引用、0 `.tmp/.spec`。`check-bundles-index.py` rc=0 五面一致（首跑 9 域/61 组/629 束，窗口内本束三级注册并入后复跑为 630）；`check-toctrees.py` 束内与全树均 rc=0。
- **G5**：Sphinx 8.2.3 dummy 非严格构建 rc=0；严格 `-W --keep-going` 的警告中 **0 条来自本束**（均为他束既有警告，未修改他束）。
- **回填**：references/verification.md 骨架改写为完整 V 报告；22 个内容文件 frontmatter 的 E 阶段占位时间戳以精确串替换为 `2026-10-14T19:30:00+08:00`，替换后束内占位串机械 grep 残留 0。

### C 阶段：fresh-context 独立评审（2026-10-14 20:00 +08:00 回填）

- **执行**：又一 fresh-context 子代理（未参与 R/E/V，不采信 V 结论），自写枚举器/解析脚本（Temp 下独立脚本，未调用 V 脚本）；镜像 HEAD 复确 `4a137bb1378834ca3664a1c971684777eb5f364a`、工作树 clean。报告见 `.trae/specs/hwe-bench-okf-wiki/review.md`。
- **独立复算**：600 链接全机扫（blob 353/tree 9/内部 236/仓库根 2）0 违例；log.jsonl 74 行独立 Python 复算得 9/51/9/4、类别 25/24/24、九真胜与 r24s2 −73.25 全命中；F-001~F-126 无缺号重号、C01-C20 齐、I-1~I-6 证据均 ≥3 F；20 篇正文逐篇 ≥3 条主张回镜像/回 F 编号抽核，命中率 100%（~90 条高风险主张直读镜像 ~30 个文件逐行对拍，含五 CRC、fitness 实居 L274、$30 help、seatbelt PID 91122、$123.62 遥测、13/13/16 RTL 集与 12 文件哈希一致等）。
- **门禁**：`check-bundles-index.py` rc=0（最终复跑 9 域/61 组/632 束五面一致；窗口内并行注册曾瞬时 631→632 漂移，收敛后复跑通过）、`check-toctrees.py` 本束 rc=0、Sphinx dummy rc=0（最终复跑 279 他束警告，本束 0）、严格 `-W --keep-going` 中本束警告 0。
- **修复 P2×2**（C 段发现并修复，修后枚举器复跑 0 违例）：source-code-map.md C15「三处行号见 F-058」误引——三口径事实编号为 **F-057**（F-058 是 cosim 三件套）；C17「实现提交 hash 全表见 F-121」误引——F-121 是 V2 random 135 独立抽取，且 log.jsonl 根本不记录实现提交 hash，改为「九胜场逐条明细见 F-100」并注明 hash 仅能经 git log 对拍复原。
- **P0=0、P1=0**；P3 观察项维持 V 段登记（C05「39+1」无上游出处，C 段独立清点 16 个花名册文件恰 39 个 `- name:` 条目，与 V 一致）。
- **裁决**：AC-1~AC-6 全过，Result=pass。**不 commit**：awesome-okf-xs 为 git submodule，提交留待用户显式指令。
