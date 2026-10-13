# 生成日志（Log）

> 本日志记录 openTPU 源码教程束的生成过程、计数台账与勘误决策，供后续维护者审计复核。方法论链路：**source-code-to-okf-wiki v1.5.0（G0 信源固定 → R → I → E → V → C）**，Spec Mode 规格在 `.trae/specs/opentpu-okf-wiki/`（spec.md/tasks.md 已批准）。CMD-LOG session：`sc-20261013-opentpu-okf`。

## 2026-10-13：初始版本（G0 → R → I → E → V）

### G0：信源固定（先于一切读取）

- **对象**：本地镜像 `external/dao/openTPU`（remote `git@github.com:FeSens/openTPU.git`，Apache-2.0）。
- **固定提交**：`ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`（2026-10-12 19:10 -0300，docs-only），工作树 clean。
- **废弃基线**：v0.5 标签 `730ca28` 落后 1499 commits 不可用；上游概念页基线 `8eaa4806` 落后 232 commits。
- **纪律**：源码树只读——勿改勿切勿跑构建；pinned 链接统一 `https://github.com/FeSens/openTPU/blob|tree/ffe997e.../`。
- **环境限制**：rtlsim/Verilator 依赖 fcntl，Windows 本机不可运行；仿真/位流构建按 blocked 记录，不谎报执行。

### R 阶段：事实采集（R-0 ~ R-3）

- **R-0/R-1 全树走读**：README、docs/ 36 个 md、opentpu/ Python 包、rtl/ SystemVerilog、tools/、host/、kernels/、llm/、targets/、asic/、tests/。
- **R-2 计数台账 C01-C32**：所有数量事实只信脚本计数（git grep / 文件解析），原始匹配数与去重数双列；RTL 42 个 .sv/.svh（生产 34、rtl/exp 8）、Verilator 源 20、tests 78（RTL10/board12/serve 口径 7/模型 15 等）、docs 36 md、kernels 8 py、llm 15 py、targets 4 TOML、CLI 11、README 结果表 18 行/10 模型、KL 表 11 行、板卡 0 ulp 6 runs/103-128 步/build 1025907f。
- **R-3 二十条对账**（reconciliation-draft.md R3-01~R3-20）：对同组概念页 embedded-weekly-03（F-053~F-072）在固定提交上逐条复核，三大关键勘误——ISA **17 条**指令（编码表 16 行 + STREAM 0x13 独立专节）、VOP **20 个**功能码（码 7 跳用）、生产配置 **S=1 D=128 MCOLS=4 ACT_ROWS=16 LANES=8 WIN=16**（design_config 的 S=2/MCOLS=8 与 09-23 稿 WIN=32 仅作旧设计点对照）。
- **事实登记**：F-001~F-123 共 123 条，十组 A-J，工作底稿 facts-draft.md 先行，发布版入 references/facts.md。

### I 阶段：洞察冻结（先于正文）

- 5 个四元组洞察（references/insights.md）：I-1 契约对拍（四行表与 top-1≥80%/KL≤3×floor 判据）、I-2 限制即隐式行为（WIN=16 顺序窗口、replay 透明）、I-3 修复配反例（recip(1)=0.99999994、负零 mutant、WAITW port-A flush）、I-4 量化即 ISA 一等公民（QACT/QST opcode、CSCALE/RSCALE 折叠）、I-5 归属与口径分离（不收 HN/star；perf.py 与 decode_profile.py 两套计时口径不可混）。
- 纪律：E 阶段只消费洞察不新造。

### E 阶段：信源先行 + 五批并行生成

生成顺序与批次（references 先于全部概念页；每批独立上下文、先读简报 concept-gen-brief.md 与 facts.md，只读核实源码）：

| 批次 | 时间（+08:00） | 文件 |
|------|---------------|------|
| E-0 | 15:40 | references 四件套（source-code-map → facts → insights → verification 骨架，V 阶段再回填） |
| E-1 | 16:00 | concepts 00-03 |
| E-2 | 16:20 | concepts 04-07 |
| E-3 | 16:40 | concepts 08-11 |
| E-4 | 17:00 | concepts 12-16 |
| E-5 | 17:20 | examples 00-02 |
| 收尾 | 17:40 | 4 个 index + 本日志 |

共 29 个 Markdown 文件：17 concepts + 3 examples + 4 references + 4 index + log。子目录 index 按已批准 tasks 规定**无 frontmatter**（表格 + toctree；门禁不强制 frontmatter，与参照束历史形态不同但全束自洽）。

### E 阶段勘误记录（3 条，均回写发布版与工作底稿）

1. **F-026 锚点勘误**：BAR 的 `bar()` 定义在 isa.py **L133**；R 阶段误记 L167（该处实为 f2i）。facts.md 已改锚点并留痕。
2. **F-062 计数勘误**：isasim `_vop` 的 ops 字典实为 **14** 个条目（ADD/SUB/RSUB/MUL/MAX/MIN 六个算术 + COPY/EXP2/RECIP/RSQRT/ABS/FILL/EXP2SUB/LOG2 八个），非 13；OUTER（码 6）、ARGMAX、三个归约在字典外。锚点 isasim.py L649-L656。concept 07 据源码逐名列算子、不写可疑计数。
3. **F-117 PPA 归属勘误（重要）**：读 docs/asic.md L62-L71 原表确认——419/339MHz、0.79W、0 DRC、die 7.02mm² 属 **nangate45-small 列（已布线签收）**，native ORFS（f395e4b6）复跑 422/341MHz 在工具噪声内，报告在 results/small/；**板卡架构大核（nangate45）仅到 CTS、未布线**，178/156MHz（clock skew 2.7ns），3.34W 是 400MHz 假设下 vectorless 功耗，die 30.6mm²。R 阶段误把 419/339 归大核、误记结果目录 cand2_3p3ns/（该目录在 ffe997e 不存在）。facts.md F-117 已重写，source-code-map C28 同步，concept 15 按原表正确归属撰写。

### E 阶段机械检查（收尾时）

- 全束文件清单：17+3+4 内容文件齐备；文件名/序号与简报清单一一对应。
- 禁用形式扫描（concepts+examples 正文 20 篇）：0 个 `](../`、0 个 file:///、0 个 external/dao、0 个 .tmp/.spec；GitHub 链接全部 pinned ffe997e。该结论口径仅覆盖 17 concepts + 3 examples：index 中的 `../embedded-weekly-03/…` 是合法跨束对账链接；references 内 2 处 `](../` 残留在 V 阶段修复（见下）。
- 标题纪律：concepts 04-07 frontmatter 后曾各重复一个 H1（与「正文只用 ##」冲突），已删除；examples/01 围栏内 shell 注释的 `#` 非 Markdown 标题。
- 每篇结尾含「## 相关概念/示例」且束内导航为 `/` 根链接（references 同目录互链沿用 bare filename，与既有 references 一致）；frontmatter verified.at 当时统一占位，V 阶段已回填 2026-10-13T18:10+08:00。
- 轻微口径备注：F-100「serve 7」实测为 6 个 test_serve_* + test_chatkv 共 7 项口径，concept 16 已如实表述，V 阶段复核确认。

### V 阶段：独立验证（18:10 完成，详见 references/verification.md）

- 由 fresh-context 独立子代理执行，手段与 R 互换（git ls-tree+PowerShell 分组正则+Python AST/literal_eval）：G1 结构、G2 约 120 符号零虚构（**P0=0**）、G3 **C01-C32 计数 32/32**、G4 链接枚举+门禁、G5 Sphinx dummy。
- **G4 修复 6 处链接**：concept 06 一条损坏 hash（43 字符）；concept 05/16 共 4 条 `(references/…)` 改 `/references/…`；concept 13 引用不存在的 examples/03 裸链改指 02；另 2 条裸全角括号路径改正式链接。修复后复扫：0 错 hash、0 断链、0 file:///、0 external/dao、0 .tmp/.spec；跨束 `../../embedded-weekly-03/…` 为合法对账链接予以保留。references 内 2 处 `](../`（facts L27、verification 相关概念）V 期改 `/`-根链接。
- **事实勘误 3 条（V 期）**：F-065 `__all__` AST 实测 **38 名**（36 原语/类+LOG2E/LN2；E 稿混入的 release/deltanet_step/state_step/has_dstep/has_stream 五名不在 __all__，删除）；StreamDesc 锚点 isa.py **L245-L317**（误记 L206-L271），连带 F-029 state/gdn/stream_hw_cfg 锚点校正；source-code-map target 表两处 `fpla` 改 `fpga`（两板卡 TOML 实证，nangate 两 target 才是 asic）。工作底稿 facts-draft.md 同步留痕。
- **门禁实测（cwd=projects/awesome-okf-xs）**：check-bundles-index.py rc=0（9 域/61 组/628 束五面一致）；check-toctrees.py 对本束定向 rc=0（全树 81 条红名 0 属本束，皆他束已提交漂移）；`sphinx-build -b dummy doc` rc=0（非严格），严格 -W 模式 30 警告 0 条来自 opentpu。
- **blocked**：rtlsim/Verilator 依赖 fcntl 无法在 Windows 运行；未跑 pytest/validate、未构建位流、未用板卡，板卡/PPA/性能数字均为「作者报告」口径；他束 toctree/Sphinx 漂移不在本任务修改范围。
- 24 个内容文件 verified.at 统一回填 `2026-10-13T18:10:00+08:00`；references/verification.md 同日回填 G1-G5 证据。

### C 阶段：fresh-context 独立评审（18:40 PASS-WITH-NITS，修复后 PASS）

- 独立子代理只读评审（自核 HEAD/clean、自写枚举器、复跑两门禁）：**P0=0、P1=0**；50 项行级对拍全部命中；572 条链接 0 断链 0 错 hash；编号 F-001~F-123/C01-C32/I-1~I-5 齐；两门禁 rc=0。
- 发现 6 条（1 P2 审计计数陈旧 + 5 P3 簿记/措辞），全部修复：verification §1 链接计数回填 572（356/26/124/66）；本日志「25」改 29；concept 14 kind 补 `sim`（target.py L44，附现状说明）；example 01「20 个 .sv」归属改清晰（tech/generic 实仅 2）；concept 13 `LINE=64` 改为 64 fp32 字/256 字节、beat 口径；concept 13 第八个基础设施文件补名 `__init__.py`。
- 评审记录：`.trae/specs/opentpu-okf-wiki/review.md`。**C 门通过，束可交付；不 commit**（submodule，提交待用户显式指令）。
