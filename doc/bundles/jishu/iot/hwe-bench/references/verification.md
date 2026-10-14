---
okf_version: "0.2"
type: Reference
title: "HWE Bench 教程束 V 阶段验证报告"
description: "束内文档的独立验证记录：G1 结构/frontmatter、G2 符号抽核、G3 计数复核（C01-C20）、G4 链接与 toctree 门禁、G5 Sphinx dummy，含 P0-P3 分级与 blocked 项"
tags: [HWE Bench, 验证报告, V阶段, 计数断言, 门禁]
generated:
  by: "source-code-to-okf-wiki/V"
  at: "2026-10-14T19:30:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-14T19:30:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: hwe-source-map
    resource: /references/source-code-map.md
    title: "HWE Bench 源码地图与信源固定"
  - id: hwe-pinned
    resource: "https://github.com/FeSens/auto-arch-tournament/tree/4a137bb1378834ca3664a1c971684777eb5f364a"
    title: "HWE Bench 固定提交 4a137bb"
---

# HWE Bench 教程束 V 阶段验证报告

> 固定信源 `4a137bb1378834ca3664a1c971684777eb5f364a`（V 开跑前复确工作树 clean）。V 由**独立上下文子代理**执行（非 R/E 作者），手段刻意区别于 R/E：E 作者 Read/grep 取证，V 用自写 Python 枚举器、json 全量解析与行号回扫独立复算，不采信束内台账自报值。本报告 2026-10-14 19:30(+08:00) 回填。

## 1. 验证范围与方法

- **对象**：束内 29 个 Markdown——17 concepts + 3 examples + 4 个 references 内容文件（source-code-map/facts/insights/verification）+ 根 index + 3 个子目录 index + log.md。
- **链接总体**：独立链接枚举器（剔除代码围栏，严格排除方括号嵌套）解析 **600 条** Markdown 链接：353 条 pinned blob、9 条 pinned tree、2 条仓库根 URL（无 hash 的 repo 首页链接，合法）、236 条束内链接（169 条 `/`-根绝对、39 条同目录/子 index bare filename、3 条 `../`——concepts/index 到 references/facts 两条与根 index 跨束到 `../opentpu/index.md` 一条、25 条根表相对路径）；纯片段链接不计。
- **基线**：上游 `https://github.com/FeSens/auto-arch-tournament` 固定提交 4a137bb；本地镜像 `external/dao/auto-arch-tournament` 仅作只读取证参照；未运行 EDA/仿真/位流，未接触板卡。
- **G 门**：G1 结构/frontmatter；G2 零虚构符号（每页 ≥1 条 pinned，抽核命中率 ≥98%、P0=0）；G3 计数独立复核（C01-C20 + F/I/K + log.jsonl 复算）；G4 链接与门禁；G5 Sphinx dummy 非严格+严格。
- **分级结果**：**P0=0**；P1 修复 1 处；P2 修复 2 处；P3 修复 3 类（06 锚点、examples×3 双 H2、vex 文件数），残余观察项 1（C05「+1」措辞，见 §6）。

## 2. 符号 Grep 核验（零虚构 API）

- concepts+examples 共 **191 条 pinned GitHub 链接**，逐页分布 concept 00-16 = 1/5/2/9/13/10/25/18/7/5/5/11/15/7/6/6/3、examples = 7/12/24；机械检查三要素（镜像文件存在、hash 恰为 40 字符且=pin、#L 锚点不越界）**100% 通过**。
- 正文反引号符号页级回扫 **85 个**（const 43、CLI 26、hex 16）；36 条页级未命中项经全仓独立解析**全部在镜像找到真实出处**（跨页符号、git 内建 flag、品牌色等），无虚构。
- **14 组高风险数字/符号逐一命中实位**：五 CRC `0xe9f5/0xe714/0x1fd7/0x8e3a/0xfcaf` 在 fpga.py L38-L43；`SEEDS=[1,2,3]` fpga.py L30、`MIN_SUCCESSFUL_SEEDS=2` L56；`EXPECTED_MIN_CHECKS=50` formal.py L42；`DEFAULT_MAX_COST_USD=200.0` runner.py L71；hyp id 正则 `\bhyp-\d{8}-\d{3}-r\d+s\d+\b` _hyp_parse.py L19；五类 category enum 在 schemas/hypothesis.schema.json L8；fitness 公式 `fmax_median * cm['iter_per_cycle'] * 1_000_000` 在 **fpga.py L274**；run_all.sh PREUNSAT/rc=16 在 L169/L183/L187；checks.cfg L1-L4（isa rv32im/nret 2/solver bitwuzla，67 行，ALTOPS L45）；v0_expected.json geomean=7212.331561429864；LEADERBOARD.md 主榜 16 行 L15-L30、Opus 983.2 L15；V2 页面真实路径 **site/v2.html**（1.32x/CI 1.18-1.47/p=0.0005 在 L44/L224，V0 309 在 L76-77/L215，7,024 在 L80/L157/L291）。
- 验证中发现并已修复的问题（均回写 [facts.md](facts.md) 与 [source-code-map.md](source-code-map.md)，留「V 阶段勘误」痕）：

| # | 级别 | 位置 | 问题 | 裁决/处理 |
|---|------|------|------|-----------|
| 1 | P1 | references/source-code-map.md | 整个文件缺 YAML frontmatter（四篇 references 中唯一缺失） | 按 opentpu 同构补全（type: Reference、generated.by /E、verified.by=process:source-code-to-okf-wiki-v、sources 双 pin、stale_after 2027-04-30） |
| 2 | P2 | references/facts.md F-115 + source-code-map C07 | results.jsonl 笼统称「27 字段；仅末两行带 provenance」，未反映键集异构 | Python 实测 37 行公共 27 字段、键并集 34：L38/L39 多 `quota_pause_sec/resumed_at`，L40/L41 多 `fixture_commit/fixture_ref/runner_commit/runner_dirty`，L41 再带 `api_equivalent_cost_usd`；provenance 字段名实为 fixture_*/runner_*。两处已改写留痕 |
| 3 | P2 | source-code-map.md C06 | 台账只报「41 个 repN 目录」，未解释 summary 42 份/agent.log 43 份的差异 | 实测 bench/ 另有两个非 repN 运行目录：aborted1-formal-reaper（有 agent.log/run_summary/log.jsonl 无 summary.json）、startup-attempt1（有 agent.log/summary.json 无另两件），份数口径已在台账写清 |
| 4 | P3 | concepts/06-cosim-iss.md L54 | 「访存窗口 [0x0,0x100000)+UART [0x10000000,0x10000200)」整句只挂 main.cpp L135-L141，但 0x10000200 上界在该文件无出处 | 补 main.cpp L24-L27（MEM_SIZE=1u<<20）与 CLAUDE.md L17（不变量 #6）双锚点，原 L135-L141/L267-L283 保留 |
| 5 | P3 | examples 00/01/02 尾部 | 各有「## 相关概念」与「## 相关示例」两个相邻 H2，不符收尾纪律 | 合并为单个「## 相关概念与示例」，bullet 全保留 |
| 6 | P3 | source-code-map.md §3.6 | vexriscv「39 个 .scala」漏数 | 实测 demo_scala 顶层 39 + demo_scla/smp/ 子目录 4 = 全树 43；改为分层口径留痕 |

## 3. 计数断言复核（C01-C20 + F/I/K）

C01-C20 由 V 子代理用 Python/枚举器独立复算，**台账=实测全部一致**（C06/C07/§3.6 三处经上面勘误后一致）。要点：

| 项 | 台账=实测 | 项 | 台账=实测 |
|---|---|---|---|
| C01 编排层行数 | orchestrator 838/tournament 600/worktree 194/sandbox 340/accept_rule 109/plot 143 | C11 73 假设分布 | improvement 9/regression 51/broken 9/placement_failed 4 |
| C02 tools/agents | 12 .py（567/225/231/152/290/494/41） | C12 类别 | structural 25/micro_opt 24/predictor 24 |
| C03 tools/eval | 15 .py（246/179/311/255/67/104） | C13 rtl 集合 | baseline 13/bench 13/v1 16 个 .sv |
| C04 bench/site | 20 .py/site 8；runner 1278/report 635/build_fixture 190/telemetry 421 | C14 研究产物 | diary 5 篇、runs 5 个 EXP 目录 |
| C05 花名册 | 16 个 models*.yaml、39 个 name 条目（+1 见 §6） | C15 formal 检查 | 53/95+/~105 三口径文本俱在 |
| C06 bench 运行目录 | 41 repN+2 非 repN；summary/run_summary/log.jsonl 各 42、agent.log 43 | C16 site/ | 5 html+CNAME+css 4 |
| C07 results.jsonl | 41 行=37 done+4 failed；公共 27 键/并集 34 | C17 胜场 | 10 条 improvement 行含 L1 哨兵，真实架构胜场 9 |
| C08 leaderboard.csv | 17 行（表头+16 模型） | C18 V2 | 6 系统×6 runs=36 scored；12 Holm 对 9 分离 |
| C09 holdout | 22 文件 | C19 random 对照 | 3×45=135（LEADERBOARD L28、v2.html L364-L365） |
| C10 experiments/log.jsonl | 74 行、603,222 字节；73 真假设+1 哨兵 | C20 setup.sh | 非 Darwin 退出，仅 macOS |

参照核文件数：ibex 30 .sv + ibex_core.f、neorv32 56 .vhd、picorv32 1 .v、vexriscv 43 .scala；21 个硬件相关文件行数与束锚点全部一致。

- **log.jsonl 字段**：键并集 26，键数分布 {25:60, 22:1, 13:8, 14:4, 10:1} 与 E 期 F-097 勘误记录完全一致。9 个真胜：首胜 r1s2 Backward-Branch L4 313.10/+4.01，末胜 r20s2 Banked Replay L61 577.76/+9.15；最差回归 r24s2 L73 −73.25/154.53。
- **F 台账**：F-001~F-126 unique 126、无缺号，十组 10/12/12/10/13/9/13/12/15/20 全对；**K-1~K-6** 齐。
- **I 台账**：I-1~I-6 齐（H2 节），每条「证据」bullet 含 F 编号数 5/5/8/5/7/5，全部 ≥3。

## 4. 链接与 toctree 门禁

- **独立枚举器复扫**（29 文件，600 链接，V 回填定稿后复跑 0 problems）：非 40 长度 hash 变体 0；hash≠pin 0；blob 文件缺失 0；#L 锚点越界 0；tree 目录缺失 0；束内链接目标缺失 0；file:/// 0；指向 external/dao 或 .tmp/.spec 的真实链接 0（log/source-code-map 中 backtick 内 `external/dao/...` 为镜像位置的散文说明，与 opentpu 束同形态，非链接）；concepts/examples 20 个内容页 0 条 `](../`。
- **门禁输出（cwd=projects/awesome-okf-xs，sphinx 8.2.3）**：
  - `python scripts/check-bundles-index.py` → **rc=0**（首跑）：「9 域 / 61 组 / **629** 束，五面一致」；回填后复跑仍 **rc=0**，总束数 **630**——验证窗口内本束三级注册（bundles 总索引 iot 行 9、jishu/index.md iot 行、jishu/iot/index.md 表行+toctree `hwe-bench/index`）由并行流程并入，非本 V 代理手工编辑，两次输出均留档。
  - `python scripts/check-toctrees.py doc/bundles/jishu/iot/hwe-bench` → **rc=0**：「全部 index.md 引用有效，所有内容文档均可达」。
  - `python scripts/check-toctrees.py doc`（全树）→ **rc=0**，无任何红名；本束 toctree 集合 concepts 17/examples 3/references 4，根 index 收三子 index+log，差集为空。
- **G5 Sphinx dummy**（回填前后各跑一遍，共四跑；复跑后本报告仅做数字/措辞订正，无新增标题、表格、指令或链接）：
  - `python -m sphinx -b dummy doc <tmp>` → 两次均 **rc=0**「build succeeded」（首轮 306 warnings、定稿复跑 298）；hwe-bench 来源警告 **0**。
  - `python -m sphinx -W --keep-going -b dummy doc <tmp2>` → 两次均 rc=1（-W 预期）「warnings treated as errors」（首轮 295、定稿复跑 305）；hwe-bench 来源警告/错误 **0**。警告总数两轮波动来自验证窗口内其他束并发增改（如 first-principles 的 docutils ERROR、embedded-weekly-03 的 Malformed YAML 等），均属他束，按纪律未修改。

## 5. Frontmatter 与结构检查

- 24 个内容文件（17 Concept + 3 Example + 4 Reference）frontmatter 机械解析：okf_version 0.2、type、title、description、generated.by、verified.by、status:draft、stale_after:2027-04-30、sources 全部完整；verified.at 已由 E 阶段占位统一回填为 `2026-10-14T19:30:00+08:00`，回填后束内占位串机械 grep 残留 0。
- 根 index 带 type:bundle frontmatter，toctree 收 concepts/examples/references 三 index + log；三个子目录 index 无 frontmatter（与 opentpu 束形态一致），toctree stem 与同目录文件集合差集为空（17/3/4）。
- 标题纪律：concepts/examples 正文无 H1，以「## 相关概念与示例」收尾（examples 三篇的双 H2 已在 V 阶段合并）；references 四篇正文 H1 与 opentpu 同构，属允许形态。

## 6. Blocked / 残余不确定性

1. **EDA/仿真/位流未执行**：Windows 本机无 verilator/sby/bitwuzla/nextpnr（部分路径依赖 fcntl）；本束为静态源码走读，所有 Fmax/iter/s/费用/频率数字均为「作者报告」口径，束内逐处标注，未独立复现。
2. **V2 数据仅转录**：site/v2.html 数字来自 v2 页面静态文本，36 runs/1.32x/CI/p 值未重新统计；按 K-1，V1/V2 数字不互相比较。
3. **锚点相关性为抽样核对**：362 条 pinned 链接的文件存在性与行号边界 100% 机械通过；锚点文字相关性对 14 组高风险与全部页级 miss 逐条核对吻合，其余为抽样。
4. **C05「39+1」残余措辞**：16 个花名册文件内 `- name:` 条目机械清点为 39；台账「+1」在上游无对应文本/代码出处（runner 无 human/reference 特殊注入），无法证实亦无法证伪，保留 E 原文并在此声明——读者引用模型总数时应以 39 个 YAML 条目为准。
5. **上游自述笔误（非束错误）**：implement.py L11 `CLAUDE_TIMEOUT_SEC=600*3`（30 min）同行注释误写 "10 min"，束内 F-029/K-5 已正确记录，不替上游改源码。

## 相关概念与示例

- [FPGA 评测与 fitness 公式](/concepts/07-fpga-fitness.md)
- [V2 holdout 与 Holm 校正](/concepts/15-v2-holdout.md)
- [源码地图与基线对账](source-code-map.md)
- [事实登记表](facts.md)
- [架构洞察四元组](insights.md)
