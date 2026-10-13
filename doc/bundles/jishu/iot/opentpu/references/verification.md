---
okf_version: "0.2"
type: Reference
title: "openTPU 教程束 V 阶段验证报告"
description: "束内文档的独立验证记录：符号 Grep 核验、计数断言复核、链接与 toctree 门禁、frontmatter 检查与 blocked 项"
tags: [openTPU, 验证报告, V阶段, 计数断言, 门禁]
generated:
  by: "source-code-to-okf-wiki/V"
  at: "2026-10-13T18:10:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-source-map
    resource: /references/source-code-map.md
    title: "openTPU 源码地图与信源固定"
  - id: opentpu-pinned
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e"
---

# openTPU 教程束 V 阶段验证报告

> 固定信源 `ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`（工作树 clean）。V 由**独立上下文子代理**执行（非 R/E 作者），手段刻意区别于 R 阶段：R 用 git grep 计数取证，V 用 `git ls-tree`+PowerShell 分组正则+Python AST/literal_eval 独立复算；链接用独立 Python 枚举器机械扫描。本报告 2026-10-13 18:10(+08:00) 回填。

## 1. 验证范围与方法

- **对象**：束内 29 个 Markdown——17 concepts + 3 examples + 4 references + 4 index + log.md；独立链接枚举器（剔除代码围栏）解析 **572 条** Markdown 链接：356 条 pinned blob、26 条其他 GitHub（tree 23/commit 1/仓库根 2）、124 条束内 `/`-根链接、66 条相对族（plain 63 + 合法跨束 `../` 3）。计数取 G4 修复后快照（C 阶段 2026-10-13 复扫）。
- **基线**：源码树 `external/dao/openTPU` HEAD=ffe997e，全程只读；未运行仿真、未构建位流、未使用板卡。
- **G 门**：G1 结构/frontmatter；G2 零虚构符号；G3 计数独立复核（C01-C32）；G4 链接与门禁；G5 Sphinx dummy。
- **分级**：P0=虚构/方向性错误（0）；P1=死链/错文件名（修复 6 处）；P2=事实归属/锚点错误（修复 4 处）；P3=锚点边界/措辞（修复 3 处，余观察项记录）。

## 2. 符号 Grep 核验（零虚构 API）

- 抽样核验约 **120 个符号**（类名/函数名/指令助记符/opcode/CLI/文件名，覆盖 isa.py、fp32.py、isasim.py、quant.py、language.py、compiler.py、target.py、validate.py、host/{offload,regs,checks}.py、kernels/* 与 RTL 关键模块），**全部在 ffe997e 真实存在，P0=0**。
- 关键锚点逐一 Read 原文核对：StreamDesc 位置、Slice._mm L458-L532、_vop L595-L660、fp_mul_s2 L163-L181、kernels/mlp.py `swiglu_down`、mailbox.py `wait_served/post`、qwen3.compile_decode L605 等。
- **未发现编造数字**：README、docs/isa.md、docs/board.md、docs/asic.md、pyproject、4 个 target TOML 中被引数值均复现；性能/PPA 数字正文逐处保留「作者报告」标签。
- 验证中发现并已修复的归属/计数类问题（均回写 [facts.md](facts.md) 与 [source-code-map.md](source-code-map.md)，留「V 阶段勘误」痕）：

| # | 阶段 | 问题 | 裁决依据 |
|---|------|------|---------|
| 1 | E | F-026 BAR 锚点误记 isa.py L167 | bar() 实在 L133；L167 是 f2i |
| 2 | E | F-062 ops 字典误记 13 个 | isasim.py L649-L656 实列 14 条 |
| 3 | E | F-117 PPA 归属颠倒 | asic.md L62-L71 原表：419/339/0.79W 属 small；大核 178/156MHz 仅 CTS |
| 4 | V | F-065 `__all__` 误记 36 且混入 5 个非导出名 | language.py L29-L34 AST 实测 38 名（36 原语/类+LOG2E/LN2） |
| 5 | V | StreamDesc 锚点误记 L206-L271 | isa.py 实在 L245-L317 |
| 6 | V | target 表 kind 误写 fpla | ypcb/bcu 两 TOML 均为 `kind = "fpga"` |

## 3. 计数断言复核（C01-C32）

**32/32 全部独立复算一致**（独立工具：`git ls-tree -r --name-only HEAD` + PowerShell 正则 + Python AST）。要点：

| 项 | 台账=实测 | 项 | 台账=实测 |
|---|---|---|---|
| C01 opcode | 17（码 7 跳用） | C18 CLI | 11（pyproject L14-L24） |
| C02 编码表行 | 16（+STREAM 专节=17） | C19 WIN | 16（4 TOML+otpu_seq） |
| C03 VOP 功能码 | 20（0-6/8-15/16-20） | C21 NSUB | 4（quant.py L267） |
| C07 RTL .sv/.svh | 42（生产 34+exp 8） | C23 MX_W | 16/11/11/13 |
| C09 RTL_SOURCES | 20（rtlsim.py AST） | C25 板卡 | 133.33MHz/DDR3-1066/4GiB/xc7k480t |
| C10 tests | 78（rtl10/板12/serve 口径 7/模型15） | C27 时序 | WNS+0.032/WHS+0.016 |
| C11 docs | 36 md | C28 ASIC PPA | small 419/339/0.79W；大核 178/156/3.34W |
| C12/C13/C14 | kernels 8/llm 15/targets 4 | C29 MoE | 10.6 tok/s·98.5%；3.95·62% |
| C15/C16 | 结果表 18 行/10 模型；KL 表 11 行 | C30 serve | 78 tok/s 4 客/25 单客 |
| C17 板卡 0 ulp | 6 runs/103-128 步/build 1025907f | C32 ulp | 1.26/1.61/1.16/1.03/2.3 |

行数独立值：compiler.py 1929、validate.py 1005、fp32.py 316、mailbox.py 37，与束锚点一致。F-001~F-123 无缺号；insights I-1~I-5 齐。口径备注：F-100「serve 7」= 6 个 test_serve_* + test_chatkv 的 7 项口径，concept 16 已如实表述。

## 4. 链接与 toctree 门禁

- **修复前**：356 条 pinned blob 中 1 条 hash 损坏（concept 06，43 字符死链）；4 条 concepts 相对路径断链（05/16，`references/…` 应为 `/references/…`）；1 条错误文件名裸链（13 引用不存在的 examples/03，实为 02）；2 条裸全角括号路径不可点击。
- **修复后复扫**（独立枚举器）：非 40 长度 hash 变体 0；全部本地链接（`/`-根+相对+同目录）目标存在；0 file:///、0 external/dao、0 .tmp/.spec 真实引用。
- **门禁输出（cwd=projects/awesome-okf-xs，Python 3.13/sphinx 8.2.3 环境）**：
  - `python scripts/check-bundles-index.py` → **rc=0**：「9 域 / 61 组 / 628 束，五面一致」（总索引随本束入库同步至地面真值；既有漂移 ai 234→238、relationships 8→9 一并校正，改动前后数值均有脚本输出佐证）。
  - `python scripts/check-toctrees.py doc/bundles/jishu/iot/opentpu` → **rc=0**：「全部 index.md 引用有效，所有内容文档均可达」。
  - 全树 check-toctrees 有 81 条红名，**0 条属本束**——全部为他束已提交未挂父 toctree 的既有漂移（telecom-*、deepseek-harness、wifit3、tauri 等），按「谁添加谁对账」不在本任务范围。
- **G5 Sphinx dummy**：`sphinx-build -b dummy doc <tmp>` 非严格模式 **rc=0**（全文档无 error 级问题，本束全部参与构建）；严格 `-W --keep-going` 模式 rc=1，30 条警告中 **0 条来自 opentpu**（均为他束 toc.not_included 与 myst-tutorial 演示性 undefined label）。

## 5. Frontmatter 与结构检查

- 24 个内容文件（17 Concept + 3 Example + 4 Reference）frontmatter 机械解析：okf_version 0.2、type、title、description（长度区间内）、generated.by、verified.at、status:draft、stale_after:2027-04-30 全部完整；本报告回填后束内无待回填时间戳残留（审计底稿保留在 .trae/specs/ 过程目录）。
- 4 个 index + log：根 index 带 type:bundle frontmatter 且 toctree 收 concepts/examples/references 三 index + log；三个子目录 index 按已批准 tasks 无 frontmatter，toctree stem 与同目录文件集合差集为空（17/3/4）。
- 标题纪律：concepts 04-07 frontmatter 后误重复的 4 个 H1 已删除；全束正文仅用 `##`，每篇以「## 相关概念/示例」收尾。

## 6. Blocked / 残余不确定性

1. **仿真/位流未执行**：rtlsim/Verilator 路径依赖 fcntl，Windows 本机不可运行；本束为静态源码走读，未跑 pytest/validate、未构建 FPGA 位流、未接触板卡——所有「板卡/仿真结果」均为作者报告口径并逐处标注。
2. **他束门禁漂移**：全树 toctrees 81 条、Sphinx 严格模式 30 条警告均来自其他已提交束，本任务未修改他束文件，仅在总索引计数面对齐地面真值。
3. **锚点相关性抽样**：356 条 blob 链接的文件存在性与行号边界已 100% 机械通过，锚点内文字相关性为抽样核对（已抽均吻合）；docs/stream.md、scoreboard.md、offload.md 等未逐行打开。
4. **上游自述不一致观察**（非束错误）：ypcb toml 注释写 LiteDRAM hostcal="host calibrates"，README 另有自校准表述；束仅如实转录 toml 键与 12s hostcal 事实，不替上游裁决。
5. **F-027「TMEM 顶部 64 字」** 等少量实现措辞回溯至 isa.md 原文即止，未做 RTL 信号级追踪。

## 相关概念

- [位精确验证体系](/concepts/16-verification-system.md)
- [源码地图与基线对账](source-code-map.md)
- [事实登记表](facts.md)
- [架构洞察四元组](insights.md)
