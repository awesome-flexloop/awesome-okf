---
okf_version: "0.2"
type: Reference
title: "openTPU 源码地图与信源固定（ffe997e）"
description: "openTPU 固定提交 ffe997e 的仓库模块地图、规模计数台账、官方阅读路径，以及与 8eaa4806 概念页基线的 20 条对账"
tags: [openTPU, 源码地图, 信源固定, 模块索引, 基线对账]
generated:
  by: "source-code-to-okf-wiki/E"
  at: "2026-10-13T15:10:00+08:00"
verified:
  by: "process:source-code-to-okf-wiki-v"
  at: "2026-10-13T18:10:00+08:00"
status: draft
stale_after: 2027-04-30
sources:
  - id: opentpu-pinned-tree
    resource: "https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e"
    title: "openTPU 固定提交 ffe997e 仓库树"
  - id: opentpu-readme-pinned
    resource: "https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/README.md"
    title: "openTPU README，固定提交 ffe997e"
---

# openTPU 源码地图与信源固定（ffe997e）

本文件是束内一切源码引用的**信源锚点**：固定提交、模块职责、规模计数与阅读路径。束内概念页的全部数字与符号都可回溯到这里登记的路径与行段。

## 信源固定记录（G0）

| 项 | 值 |
|---|---|
| 仓库 | [FeSens/openTPU](https://github.com/FeSens/openTPU)（remote `git@github.com:FeSens/openTPU.git`） |
| 固定提交 | [`ffe997e9a8b8607b07b3d1bb3c1132db0faf044e`](https://github.com/FeSens/openTPU/commit/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e)（2026-10-12 19:10 -0300，docs-only 提交） |
| 工作树状态 | 取证时工作树 clean，HEAD == ffe997e（2026-10-13 两次 `git rev-parse HEAD` 一致） |
| 最新 release tag | v0.5 = `730ca28`（2026-09-25），落后 HEAD **1499 个提交**，不含 stream engine、当前结果表与多 target，不可用 |
| 概念页旧基线 | `8eaa4806`（2026-10-08），落后 HEAD **232 个提交** |
| 选型裁决 | 引用集合（stream engine/10 模型结果表/4 个 target/NanGate45）与版本变更集合交集非空，tag 不满足「引用集合 ∩ 版本变更 = ∅」，故固定全 hash 而非 tag |
| 引用形式 | 束内所有源码链接为 pinned 形式 `https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/<path>#Lxx-Lyy` |
| 取证方式 | 静态阅读 + 对固定 blob 的 `git grep/git ls-tree` 脚本计数；**未运行测试、未构建位流、未使用 FPGA** |
| 许可 | Apache License 2.0 |

## 顶层模块地图

```text
openTPU/
├── opentpu/            # Python 侧：ISA 定义、fp32 模型、内核语言、编译器、位精确模拟器、量化
├── rtl/                # SystemVerilog RTL（42 个 .sv/.svh；生产相关 34，实验 8）
├── sim/                # Verilator/技术单元 testbench（18 个 .sv/.v）
├── boards/             # FPGA 板工程（ypcb-00338、bcu1525）
├── asic/               # NanGate45 + OpenROAD-flow-scripts 流程
├── targets/            # 4 个构建目标描述（TOML）
├── kernels→opentpu/kernels/   # ol 内核库（attention/mlp/lib/layouts/mailbox/gather/deltanet）
├── host/               # 板卡主机运行时（29 个文件 + litedram/litedram4/pcie 子目录）
├── serve/              # OpenAI 风格服务（api/batching/scheduler/kvio/store）
├── tools/              # validate.py、qual/、scoreboard.py、asic/ 等验证与建模工具
├── tests/              # 78 个 test_*.py
├── docs/               # 36 篇 Markdown 文档
└── llm→opentpu/llm/    # 模型适配（5 模型族 + MoE/MTP + 8 基础设施）
```

### Python 核心（`opentpu/`）

| 文件 | 职责 | 关键锚点 |
|---|---|---|
| [isa.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isa.py) | 17 opcode 编码/解码、MM/QACT/QST/VOP/DSTEP/STREAM 构造器、StreamDesc 描述符、硬件可接受子集裁决 | OPNAMES L8-L17；VOP 码 L39-L46；Instr L73-L90；StreamDesc L245-L317（V 阶段勘误：R 阶段误记 L206-L271） |
| [fp32.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/fp32.py) | 位精确 fp32 模型（add/sub/mul/exp2/log2/recip/rsqrt/quantize），与 RTL 逐位一致 | canonical NaN L8；RED_PARTIALS=64；exp2 系数 L18-L21 |
| [language.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/language.py) | ol 内核语言：`__all__` 38 名（36 原语/类 + 常量 LOG2E/LN2），load/store/dot/quantize/range/state_step/kv_append… | `__all__` L29-L34；dot L105-L117；state_step L240-L326（模块函数，非 `__all__`） |
| [compiler.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/compiler.py) | 布局即 API、仿射循环寻址、寄存器分配、算子融合与 Builder（1929 行） | Builder L712-L1868；jit L1928；arg_reg L111 |
| [isasim.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py) | 位精确 ISA 模拟器（RTL 的 golden）：Config/Slice/Machine | Config L18-L130；design_config/board_config L39-L72；Machine L721+ |
| [quant.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/quant.py) | int8/int4/FP4/NVFP4 量化与反量化、MX 块尺度、pack4（863 行） | NSUB=4 L267；quantize_mxu L510；import_nvfp4 L817 |
| [target.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/target.py) | targets/*.toml 单加载器：Target/load/current/rtl_params/sources/build_config | Target L87；current L181；arch_hash |
| [rtlsim.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/rtlsim.py) | Verilator 构建/运行（RTL_SOURCES 20 文件；依赖 fcntl，仅 Unix/WSL） | RTL_SOURCES L1-L40 |
| [lens.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/lens.py) | profiler：.otpuprof（gzip JSON），kind=rtl/isa/board | 头注释 L1-L12 |
| 其他 | hwtrace/imgcache/profile/progcache/qcache/reference/simtmp.py | 观测、缓存与参考工具 |

### RTL（`rtl/`，42 个 .sv/.svh）

| 子目录（数量） | 文件 |
|---|---|
| top/（4） | [otpu_top.sv](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl/top/otpu_top.sv)（多 slice 顶）、otpu_slice.sv（单 slice）、otpu_coll.sv（GATHER/BAR 集合单元）、otpu_pkg.sv（参数包） |
| seq/（1） | otpu_seq.sv：按程序序派发，WIN 参数默认 16 的指令足迹窗口 |
| dma/（1） | otpu_dma.sv |
| mxu/（1） | otpu_mxu.sv：四列脉动阵列、DSP48 cascade 链、48-bit 精确累加、列尾第 9 颗 DSP、E lane epilogue |
| vpu/（7） | otpu_vpu/otpu_fp（位精确 fp）/otpu_fpipe/otpu_quant/otpu_se_comp/otpu_se_tail/otpu_vtree.sv |
| mem/（4） | otpu_tmem/otpu_actram/otpu_dram/otpu_native_dram.sv（64B beat、部分写合并、通道交织） |
| shell/（6） | otpu_board/otpu_ctrl/otpu_mem_ch/otpu_axi_split2/otpu_afifo/otpu_trace.sv |
| tech/（5） | generic、xilinx7（DSP48E1）、xilinxus（DSP48E2）、asic（1R1W macro） |
| boards/（4） | ypcb-00338：otpu_fpga_top_ld（LiteDRAM 版）、otpu_native_sys；bcu1525：fpga_top_bcu、bcu_sys |
| asic/（1） | otpu_asic_top.sv：单 slice + collective，存储端口在边界 |
| exp/（8，实验性） | mx_mxu/（6，MCOLS=8/E 分析）、vpu_pump/（2）——不计入生产 34 文件 |

### 内核、模型、主机与工具

- **kernels 8 文件**：[attention.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels/attention.py)（attention_decode/attention_layer + Bucket/Blocks/TileSeq）、mlp.py（swiglu_down/mlp）、lib.py（rmsnorm/silu/rope 等 8 个）、layouts.py、mailbox.py（wait_served/post）、gather.py（onehot/gather_row/gather_record）、deltanet.py（gated_deltanet_step）、__init__.py。
- **llm 15 文件**：模型适配 qwen3/qwen35/gemma4/lfm2/llama（5）；moe/mtp（2）；__init__/batch/formats/generate/prefill/rtl_backend/snapshot/tiled（8）。
- **host 29+ 文件**：board/offload/chat/chat_tui/smi/diag/selftest/checks/opchecks/ddrcal/selfcal/memcal/streamed/hwlens 等，含 litedram/litedram4/pcie 子目录。
- **serve 5 文件**：api.py、batching.py、scheduler.py、kvio.py、store.py。
- **tools**：[validate.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/tools/validate.py)（1005 行）、scoreboard.py（四负载 what-if 模型）、qual/（perf.py、waitw.py）、asic/（flow.py、paths.py）、decode_profile.py。
- **tests 78 个 test_*.py**：文件名粗分 RTL 相关 10、board/host 12、serve 7、模型 15，其余为 ISA/编译器/fp/quant/kernel 纯 Python 层。
- **docs 36 篇 .md**：含 isa/compiler/quant/formats/stream/scoreboard/offload/board/host/targets/bcu1525/asic/lens/observability/benchmarks/serve/status/tourney 与模型文档。
- **CLI 11 入口**：otpu-chat、otpu-serve、otpu-smi、otpu-lens、otpu-selftest、otpu-diag、otpu-lock、otpu-setup、otpu-i2c、otpu-memcal、otpu-ddr4（pyproject.toml `[project.scripts]`）。

## 4 个构建目标（targets/*.toml）

| target | kind | 关键架构 | 平台 |
|---|---|---|---|
| [ypcb-00338](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/ypcb-00338.toml) | fpga | S=1 D=128 **MCOLS=4** ACT_BLOCKS=128 **ACT_ROWS=16** LANES=8 IMEM=32K DRAM=4GiB；PAIR/DSTEP/STREAM=true；uarch MXU_IMPL=2（systolic）MXU_CL=16 MXU_E=4 **WIN=16** FIFO_DEPTH=1024 TRACE_DEPTH=16384 | Kintex-7 xc7k480tffg1156-2，133.33MHz，DDR3-1066 LiteDRAM（hostcal），2×2GiB，64B beat，PCIe Gen2 x8 |
| [bcu1525](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/bcu1525.toml) | fpga | S=2（4 通道）D=128 MCOLS=4；开发构建 100MHz | VU9P xcvu9p，4×DDR4 RDIMM（16GiB/条），XDMA Gen3 x16；**bring-up 计划，尚未建成** |
| [nangate45](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/nangate45.toml) | asic | 同板卡架构 S=1 D=128 MCOLS=4；TMEM_IMPL=1（banked 1R1W）；TRACE=0；400MHz 目标 | FreePDK45（不可制造，PPA 参考） |
| [nangate45-small](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/targets/nangate45-small.toml) | asic | D=32 MCOLS=2 LANES=4 TMEM=16K IMEM=8K DRAM=256MiB；可选特性全关 | 同上，shuttle 尺寸小核 |

## 规模计数台账（对 ffe997e 脚本计数；口径与 V 阶段复核见 [verification.md](verification.md)）

| # | 断言 | 计数值与口径 |
|---|---|---|
| C01 | ISA 指令数 | **17 opcode**（isa.py OPNAMES 字典键）；0x00-0x07 八控制、0x10-0x13 四访存/状态、0x20-0x22 三矩阵/量化、0x30 VOP、0x40 GATHER |
| C02 | docs/isa.md 编码表 | **16 表格行**；0x13 STREAM 在独立章节（isa.md 编码表 L160-L177，STREAM L386-L414） |
| C03 | VOP 功能码 | **20 个已定义功能码**：0-6、8-15、16-20（**码 7 跳用**）；码槽位 0-20 共 21 个 |
| C04 | LOOP 嵌套深度 | 4 |
| C05 | 通用寄存器 | 16（R0 读为 0；R8-R15=ARG0-ARG7） |
| C06 | 指令编码长度 | 8×32-bit 字（w0 操作码/寄存器/flags，w1..w7 立即数） |
| C07 | RTL 文件 | 42 个 .sv/.svh（mxu1/vpu7/dma1/mem4/seq1/top4/shell6/tech5/asic1/boards4/exp8） |
| C08 | 其中实验目录 | 8（rtl/exp：mx_mxu 6 + vpu_pump 2）；生产相关 34 |
| C09 | Verilator 源 | 20（rtlsim.py RTL_SOURCES，generic tech） |
| C10 | 测试文件 | 78 个 test_*.py（RTL 相关 10 / board·host 12 / serve 7 / 模型 15 / 其余 Python 层） |
| C11 | 文档 | 36 篇 .md（递归） |
| C12 | kernels | 8 个 .py（含 __init__） |
| C13 | llm | 15 个 .py（5 模型族 + 2 MoE/MTP + 8 基础设施） |
| C14 | targets | 4 个 TOML |
| C15 | README 结果表 | 18 配置行、10 个模型（README L30-L47；L24 自称 "ten modern models"） |
| C16 | validate KL 表 | 11 行（README L252-L262） |
| C17 | 板卡 0 ulp 对拍 | 6 runs（3 模型×int8/4bit-int8head），每 run 103-128 步，build 1025907f，2026-10-07 |
| C18 | CLI 入口 | 11 |
| C19 | seq 窗口 | WIN=16（4 个 target 一致；otpu_seq.sv 参数默认 16） |
| C20 | MM 累加上界 | 精确整数累加，|acc| < 2^47（48-bit） |
| C21 | 量化子块 | 每 D 块 4 个 D/4 子块（NSUB=4） |
| C22 | 4-bit 权重位宽声称 | 4.25 bits/weight（FP4 + 两级块尺度，作者报告） |
| C23 | MX shift window | W=16（int8）/11（int4、fp4）/13（nvfp4） |
| C24 | 三组参数点 | 代码默认（S=1 D=32 MCOLS=8 ACT_BLOCKS=64，测试用）；design_config()（S=2 D=128 MCOLS=8 LANES=16，旧设计点）；生产 target（S=1 D=128 **MCOLS=4** ACT_ROWS=16） |
| C25 | 板卡时钟/带宽 | 133.33MHz，DDR3-1066，峰值 17.1GB/s，4GiB，64B beat，PCIe Gen2 x8 |
| C26 | DRAM 利用率（作者报告） | 82%-94%（build B 91-94%；旧镜像 82-87%） |
| C27 | 收敛余量 | 生产镜像 WNS +0.032 ns，WHS +0.016 ns |
| C28 | ASIC PPA（作者报告；E 阶段据 asic.md 原表勘误归属） | 小核（nangate45-small，已布线签收）reg-reg 419MHz/含端口 339MHz/0.79W/0 DRC，native 复跑 422/341MHz；大核（板卡架构）仅到 CTS 未布线，178/156MHz，400MHz 假设 vectorless 3.34W |
| C29 | MoE offload（作者报告） | LFM2.5-8B-A1B 10.6tok/s·98.5%命中·5.2MB/token；Qwen3.5-35B-A3B 3.95tok/s·62%·153MB/token·1.41GB/s |
| C30 | otpu-serve（作者报告） | Qwen3-0.6B 4 客户端 78 tok/s，单客户端 25 tok/s |
| C31 | validate 模型 | Qwen3-0.6B、LFM2.5-230M、Qwen3.5-0.8B、Gemma4 E2B（base+instruct）；MoE 不支持 |
| C32 | fp32 近似误差（作者契约值） | exp2 1.26/1.61 ulp、recip 1.16 ulp、rsqrt 1.03 ulp、log2 2.3 ulp |

## 官方阅读路径（README L311-L322）

1. [docs/isa.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/isa.md)——编译器/模拟器/RTL 的逐位契约；
2. [opentpu/kernels/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/kernels) + [docs/compiler.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/compiler.md)——内核语言与编译；
3. [opentpu/isasim.py](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/opentpu/isasim.py)——"the simulator, which is the spec"；
4. [rtl/](https://github.com/FeSens/openTPU/tree/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/rtl)，起点 rtl/top/otpu_top.sv；
5. 模型文档（docs/lfm2.md、qwen35.md、llama.md、gemma4.md、benchmarks.md）；
6. [docs/board.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/board.md)——板卡构建与镜像；
7. [docs/targets.md](https://github.com/FeSens/openTPU/blob/ffe997e9a8b8607b07b3d1bb3c1132db0faf044e/docs/targets.md)——多目标体系（旧基线时代的第 7 步尚未存在）。

## 附录：与概念页基线（8eaa4806）的 20 条对账

对账对象：[embedded-weekly-03/concepts/00](../../embedded-weekly-03/concepts/00-ai-designed-chip.md) 的 F-053~F-072。判定档：仍成立 / 扩展 / 变更 / 无法静态确认。

| # | 概念页事实 | 判定 | ffe997e 证据 |
|---|---|---|---|
| R3-01（F-053） | 执行链六层 | 仍成立（扩展） | README 六层链图保留，补 "same bits, checked by the tests" 与 stream engine |
| R3-02（F-054） | 指令固定 8×32-bit 字 | 仍成立 | isa.py L1；isa.md L154-L158 |
| R3-03（F-055） | ol.load→LD、quantize→QACT、dot→MM | 仍成立（扩展） | 新增 state_step→STREAM/DSTEP、kv_append、all_gather→GATHER 等映射 |
| R3-04（F-056） | 五单元；int8 激活/int8·4 位权重/fp32 向量 | 扩展 | 权重显式四 WF（int8/int4/FP4/NVFP4）；新增 stream engine 与 collective 单元 |
| R3-05（F-057） | 无 cache、无隐藏调度、搬运显式 | 仍成立 | README L144-L148；WIN=16 是顺序足迹窗口非乱序重排 |
| R3-06（F-058） | HF/ISA/RTL·FPGA 三参照 | 仍成立（扩展） | validate 四行表（含 W+A~ ulp floor 自对照） |
| R3-07（F-059） | fp32/W+A/设备区分；--against | 仍成立 | validate.py 参数与 README 验证节 |
| R3-08（F-060） | top-1≥80%、KL≤3×floor | 仍成立 | README L231-L234（--min-top1/--kl-ratio 可调） |
| R3-09（F-061） | RNE+FTZ、零符号、非完整 IEEE754 | 仍成立 | 232 commits 后系数/魔数零漂移（3F800000…37B3C7D6、0x7EF311C3、0x5F3759DF） |
| R3-10（F-062） | 8eaa4806 联动修复+反例 | 仍成立（强化） | 修复均在；新增 WAITW port-A flush 等后续案例 |
| R3-11（F-063） | 6 runs/103-128 步/0 ulp | 仍成立 | README L304-L309（build 1025907f，2026-10-07） |
| R3-12（F-064） | 博主 `116 passed, 1 deselected` | **无法静态确认** | 外部第三方历史观测；测试已增至 78 文件，口径不可比；本束不引为事实 |
| R3-13（F-065） | Verilator 5；validate 不支持 MoE；E2B 16GB | 仍成立（扩展） | README L210-L211；MoE 改走 chat/offload 路径对拍 |
| R3-14（F-066） | 板卡规格 133.33MHz/17.1GB/s/4GiB | 仍成立 | targets/ypcb-00338.toml；README L54-L57 |
| R3-15（F-067） | 512+64、device/wall、主机 argmax 在环 | 仍成立（扩展） | 另增第二口径 decode_profile.py：96 token、卡自选取、logits 流式 |
| R3-16（F-068） | 7 个性能数字 | **数字逐字仍成立；范围扩展** | README L30-L47 七数一致；表扩为 18 行/10 模型并增 Prefill、DRAM 列 |
| R3-17（F-069） | 4 位权重减流量/提速/质量代价 | 扩展 | 明示 4.25 bits/weight、LM head 保 int8、+40%~45%（作者报告） |
| R3-18（F-070） | 35B-A3B 3.95/153MB/1.41GB/s | 仍成立（扩展） | README L103-L108；新增 8B-A1B 配套数据 |
| R3-19（F-071） | Lens 与阅读路径 | 仍成立（扩展） | 阅读路径现 7 步（末增 targets.md）；新增 serve/scoreboard |
| R3-20（F-072） | HN/star 与 AI 归属 | **无法静态确认** | 源码外时点观测，本束不收录；保留「自述 AI 开发 ≠ 逐行可证」方法论 |

### 基线后 232 commits 的新增项（旧概念页未覆盖）

STREAM 0x13 与 stream engine（CAPS bit26）；多 target 体系（4 TOML + target.py）；NanGate45 ASIC 流程与 PPA；四列脉动 MXU + LiteDRAM 生产镜像（替代两列 se-cand3 120.755MHz）；WIN=16 生产点（旧 09-23 设计稿为 WIN=32/S=2/MCOLS=8）；otpu-serve 卡上批量；MoE 专家流 offload；scoreboard 四负载模型；NVFP4/MXFP4/混合格式；HALT CHAIN 常驻 decode 程序；CAPS 能力位（bit6 DSTEP / bit25 参数 / bit26 STREAM / bit31 WAITW）。

## 相关概念

- [事实登记表 F-001~F-123](facts.md)
- [架构洞察四元组](insights.md)
- [V 阶段验证报告](verification.md)
